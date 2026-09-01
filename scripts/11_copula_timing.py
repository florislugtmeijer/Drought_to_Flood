"""T-11 stap 0: rekentijd meten en de vinecopulas-API vastleggen.

Onderzoek, geen wijziging. Dit script verandert niets aan bestaande code en
niets aan de gepubliceerde cijfers. Het meet hoe duur de onderdelen van de
copula-berekening zijn, zodat het budget voor de bootstrap (R4-03, T-11) op
cijfers vastgezet kan worden in plaats van op een schatting.

Meet per cel, een cel is locatie x periode x variabelenpaar:
  - bestcop over 15 families op circa 83 punten
  - random(cop, par, 100000), de trekking uit de gepubliceerde route
  - de gepubliceerde lus over 101 y-waardes
  - de analytische route via CDF, plus het verschil met de trekkingsroute
  - het Z-oppervlak van 100 bij 101, geextrapoleerd uit een paar rijen
  - een kale bootstrap-replicatie, met en zonder familie-herselectie

Meet er meteen de schaaldiagnose bij (stap 1 van het plan): de verdeling van
quantile_max_value over de droogte-events tegen de verdeling van de rollende
vierweeks maxima over alle weken.

Let op de quantielreferentie. De copula-kant in cel 25 gebruikt de wekelijkse
gemiddelden als referentie, de ECA-kant in cel 16 gebruikt de dagelijkse reeks.
Dit script volgt de copula-kant, want dat is wat T-11 moet reproduceren.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project python scripts/11_copula_timing.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events, empirical_cdf)
from vinecopulas.bivariate import bestcop, fit, random, CDF, copulas

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-01_copula_timing"
# parameters uit cel 30 en 35, daar positioneel meegegeven (zie D-14)
THRESHOLD, DT, N_DRAW = 0.5, 4, 100000
Y = np.linspace(0, 1, 101)
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
N_LOC = 3          # aantal locaties voor de meting
os.makedirs(OUT, exist_ok=True)

def calculate_rolling_max(series, period_after_event):
    """Uit cel 12. Maximum over de period_after_event elementen na i, i zelf niet mee."""
    d = series.values if isinstance(series, xr.DataArray) else series
    out = np.empty(len(d))
    for i in range(len(d)):
        s, e = i + 1, min(i + period_after_event + 1, len(d))
        out[i] = np.max(d[s:e]) if s < len(d) else np.nan
    return out

def timeit(fn, repeat):
    t0 = time.perf_counter()
    for _ in range(repeat):
        r = fn()
    return (time.perf_counter() - t0) / repeat, r

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]][:N_LOC]

f = open(f"{OUT}/timing.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["river","village","period","pair","n_events","k_minor","k_major",
            "cop_id","cop_name","par","aic","t_minor","t_major",
            "s_bestcop","s_random100k","s_loop101","s_cdf101","s_zsurface_est",
            "s_boot_reselect","s_boot_fixed","max_abs_diff_analytic_vs_draw",
            "mc_sd_expected","qmax_p25","qmax_p50","qmax_p75",
            "rollmax_p25","rollmax_p50","rollmax_p75"])

print(f"vinecopulas families: {copulas}", flush=True)
rng_note = []
t_start = time.time()
for pname, (b, e) in PERIODS.items():
    for river, village, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        # copula-referentie: wekelijkse gemiddelden, zoals cel 25. De ECA-kant
        # gebruikt hier de dagelijkse reeks, dat verschil is een aparte bevinding.
        q = transform_to_quantiles(max_w, mean_w)
        it = Intensity_calc(sri, q, THRESHOLD)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
        rollmax = calculate_rolling_max(q, DT)
        rollmax = rollmax[np.isfinite(rollmax)]

        for pair, X in PAIRS.items():
            m = np.isfinite(dr[pair]) & np.isfinite(dr["quantile_max_value"])
            ev = dr.where(m, drop=True)
            d1 = np.asarray(ev[pair].values, dtype=float)
            d2 = np.asarray(ev["quantile_max_value"].values, dtype=float)
            n = len(d1)
            if n < 10:
                print(f"OVERGESLAGEN {river}/{village} {pname} {pair}: n={n}", flush=True)
                continue
            u = np.column_stack((stats.rankdata(d1) / (n + 1), stats.rankdata(d2) / (n + 1)))

            s_best, (cop, par, aic) = timeit(lambda: bestcop(COPS, u.copy()), 10)
            s_rand, ur = timeit(lambda: random(cop, par, N_DRAW), 5)
            t_min = float(np.sum(d1 <= X[0]) / (n + 1))
            t_maj = float(np.sum(d1 <= X[1]) / (n + 1))
            k_min, k_maj = int(np.sum(d1 > X[0])), int(np.sum(d1 > X[1]))

            def published_loop():
                sel = ur[:, 0] >= t_min
                return np.array([np.sum(sel & (ur[:, 1] >= y)) / np.sum(sel) for y in Y])
            s_loop, p_draw = timeit(published_loop, 3)

            def analytic(t):
                uu = np.column_stack((np.full(len(Y), t), Y))
                return (1 - t - Y + CDF(cop, uu, par)) / (1 - t)
            s_cdf, p_ana = timeit(lambda: analytic(t_min), 10)

            # Z-oppervlak: 5 rijen meten en opschalen naar 100
            u_small = random(cop, par, 10000)
            dvals = np.linspace(d1.min(), d1.max(), 100)
            def z_rows():
                for i in range(5):
                    dp = np.sum(d1 <= dvals[i]) / (n + 1)
                    sel = u_small[:, 0] >= dp
                    for yj in Y:
                        np.sum(sel & (u_small[:, 1] >= yj)) / np.sum(sel)
            s_z5, _ = timeit(z_rows, 1)

            idx = np.random.default_rng(0).integers(0, n, n)
            a, c = d1[idx], d2[idx]
            ub = np.column_stack((stats.rankdata(a) / (n + 1), stats.rankdata(c) / (n + 1)))
            def boot_reselect():
                fam, p, _ = bestcop(COPS, ub.copy())
                tm = np.sum(a <= X[0]) / (n + 1)
                uu = np.column_stack((np.full(len(Y), tm), Y))
                return (1 - tm - Y + CDF(fam, uu, p)) / (1 - tm)
            s_br, _ = timeit(boot_reselect, 5)
            def boot_fixed():
                p = fit(cop, ub.copy())
                tm = np.sum(a <= X[0]) / (n + 1)
                uu = np.column_stack((np.full(len(Y), tm), Y))
                return (1 - tm - Y + CDF(cop, uu, p)) / (1 - tm)
            s_bf, _ = timeit(boot_fixed, 5)

            diff = float(np.max(np.abs(p_ana - p_draw)))
            n_cond = N_DRAW * (1 - t_min)
            mc_sd = float(np.max(np.sqrt(np.clip(p_ana * (1 - p_ana), 0, None) / n_cond)))

            w.writerow([river, village, pname, pair, n, k_min, k_maj, cop, copulas[cop],
                        np.round(par, 6) if np.isscalar(par) else np.round(par, 6).tolist(),
                        round(float(aic), 4), round(t_min, 6), round(t_maj, 6),
                        round(s_best, 5), round(s_rand, 5), round(s_loop, 5),
                        round(s_cdf, 6), round(s_z5 * 20, 4),
                        round(s_br, 5), round(s_bf, 5), round(diff, 6), round(mc_sd, 6),
                        *[round(float(np.percentile(d2, p)), 4) for p in (25, 50, 75)],
                        *[round(float(np.percentile(rollmax, p)), 4) for p in (25, 50, 75)]])
            f.flush()
            print(f"{river:8} {village[:16]:16} {pname:6} {pair:22} n={n:3} "
                  f"k_maj={k_maj:3} {copulas[cop]:10} bestcop={s_best*1000:6.1f}ms "
                  f"boot={s_br*1000:6.1f}ms diff={diff:.5f} (mc_sd={mc_sd:.5f})", flush=True)

# is random seedbaar
np.random.seed(1); r1 = random(2, 2.0, 5)
np.random.seed(1); r2 = random(2, 2.0, 5)
r3 = random(2, 2.0, 5)
print(f"\nrandom met np.random.seed reproduceerbaar: {np.allclose(r1, r2)}", flush=True)
print(f"random zonder herseeding verschilt: {not np.allclose(r1, r3)}", flush=True)
f.close()
print(f"\nklaar in {time.time()-t_start:.1f}s, uitvoer in {OUT}/timing.csv", flush=True)
