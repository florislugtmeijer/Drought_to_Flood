"""T-11 deel A: welke copula koos AIC per locatie en variabelenpaar (R4-03).

Levert de appendixtabel die Reviewer #4 vraagt, en meteen een controle op het
package. Tijdens stap 0 bleek dat vinecopulas voor de 90- en 270-rotaties een
CDF geeft die niet overeenkomt met zijn eigen trekking, dat `random` voor
Joe90 en Joe270 uitsluitend NaN teruggeeft, en dat een terugvindtoets voor die
families faalt. Dit script meet hoe vaak die families gekozen worden, zodat de
omvang van het probleem bekend is.

Per cel, en een cel is locatie x periode x variabelenpaar:
  - de gekozen familie, parameter en AIC, plus de nummer twee en het AIC-verschil
  - k_minor en k_major, het aantal droogtes boven X[0] en X[1]
  - Kendall tau van de data tegen Kendall tau van een trekking uit de gefitte
    copula, want die twee horen gelijk te zijn
  - het aandeel NaN in de trekking

Onderzoek, geen wijziging. Verandert niets aan bestaande code of cijfers.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project python scripts/12_copula_selection.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from vinecopulas.bivariate import bestcop, fit, random, neg_likelihood, copulas

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-01_copula_selection"
THRESHOLD, DT, N_CHECK = 0.5, 4, 20000
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
os.makedirs(OUT, exist_ok=True)

def aic_all(u):
    """AIC per familie, zoals bestcop hem berekent, maar dan de hele lijst."""
    out = []
    for cop in COPS:
        try:
            par = fit(cop, u.copy())
            k = 2 if cop == 15 else 1
            out.append((cop, par, 2 * k + 2 * neg_likelihood(par, cop, u.copy())))
        except Exception:
            out.append((cop, np.nan, np.inf))
    return sorted(out, key=lambda r: (np.inf if not np.isfinite(r[2]) else r[2]))

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

f = open(f"{OUT}/copula_selection.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["river","village","river_location","latitude","longitude","period","pair",
            "n_events","k_minor","k_major","t_minor","t_major",
            "cop_id","cop_name","par","aic","cop_id_next","cop_name_next","delta_aic_next",
            "tau_data","tau_draw","nan_frac_draw","rotated_90_270"])
t0 = time.time(); done = 0
for pname, (b, e) in PERIODS.items():
    for river, village, rloc, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mw = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mw)
        xw = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(xw, mw)          # copula-referentie, cel 25
        it = Intensity_calc(sri, q, THRESHOLD)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
        for pair, X in PAIRS.items():
            m = np.isfinite(dr[pair]) & np.isfinite(dr["quantile_max_value"])
            ev = dr.where(m, drop=True)
            d1 = np.asarray(ev[pair].values, float)
            d2 = np.asarray(ev["quantile_max_value"].values, float)
            n = len(d1)
            if n < 10:
                print(f"OVERGESLAGEN {river}/{village} {pname} {pair}: n={n}", flush=True)
                continue
            u = np.column_stack((stats.rankdata(d1) / (n + 1), stats.rankdata(d2) / (n + 1)))
            ranked = aic_all(u)
            (c1, p1, a1), (c2, p2, a2) = ranked[0], ranked[1]
            np.random.seed(42)
            s = random(c1, p1, N_CHECK)
            nanfrac = float(np.mean(~np.isfinite(s)))
            ok = np.all(np.isfinite(s), axis=1)
            tau_draw = float(stats.kendalltau(s[ok, 0], s[ok, 1])[0]) if ok.sum() > 100 else np.nan
            tau_data = float(stats.kendalltau(d1, d2)[0])
            w.writerow([river, village, rloc, lat, lon, pname, pair, n,
                        int(np.sum(d1 > X[0])), int(np.sum(d1 > X[1])),
                        round(float(np.sum(d1 <= X[0]) / (n + 1)), 6),
                        round(float(np.sum(d1 <= X[1]) / (n + 1)), 6),
                        c1, copulas[c1],
                        np.round(p1, 6) if np.ndim(p1) == 0 else np.round(p1, 6).tolist(),
                        round(float(a1), 4), c2, copulas[c2], round(float(a2 - a1), 4),
                        round(tau_data, 4), round(tau_draw, 4) if tau_draw == tau_draw else "",
                        round(nanfrac, 6), int(c1 in (3, 5, 7, 9, 12, 14))])
            f.flush()
        done += 1
        el = time.time() - t0
        print(f"[{done}/96] {pname:6} {river:8} {village[:22]:22} {el:6.1f}s "
              f"eta {el/done*(96-done):5.1f}s", flush=True)
f.close()
print(f"\nklaar in {time.time()-t0:.1f}s, uitvoer in {OUT}/copula_selection.csv", flush=True)
