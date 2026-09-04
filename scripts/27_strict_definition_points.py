"""Strikte definities: droogte bij SRI < -1, floodniveau gespiegeld naar norm.cdf(1).

Gevoeligheidsvariant op verzoek van Floris, 4 september 2026. Vraag: wat gebeurt er
met de copula-analyse als droogte en flood strikter van elkaar worden gescheiden,
dus droogtedrempel 1 in plaats van 0,5, met het floodniveau gespiegeld van 0,6915
naar 0,8413. Dit is een variant naast de gerapporteerde analyse, geen vervanging.
Bestaande code wordt niet aangepast; dit script leest src/dtf zoals het is.

Wat de drempel in de copula-kant wel en niet raakt:
  - wel: welke weken droogte zijn (Intensity_calc), dus het aantal events, de
    drought peak en de mean severity (het tekort onder -1 in plaats van -0,5)
  - niet: de floodzijde van de copula. Die is continu, het hoogste quantiel in het
    venster na de droogte. De spiegeling naar 0,8413 raakt alleen het afleesniveau
    waarop wordt gerapporteerd

Let op de drempels X voor mild en zwaar. Pagina 22 zet die op [1, 2] voor drought
peak en [0.5, 1] voor mean severity, in absolute SRI-eenheden. Met droogtedrempel 1
heeft elke droogte een piek van minstens 1, dus valt elke droogte onder "mild" en
wordt de milde curve gelijk aan de onafhankelijkheidslijn. De X-waardes zijn hier
bewust ongewijzigd gelaten, dat is een besluit voor Floris; het effect wordt gemeten.

Berekent voor beide varianten, referentie 0,5 en strikt 1,0, met dezelfde seeds:
  - per week of hij tegelijk droogte en flood is, onder de eigen gespiegelde grens
  - per cel de puntschatting: milde en zware curve, unconditioneel, onafhankelijk-
    heidslijn, en de aflezing op vier niveaus

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/27_strict_definition_points.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy.stats import norm
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula, flood_peak_after_drought, mean_severity_per_week

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-04_strict_definition_points"
DT, N_DRAW, SEED = 4, 100000, 42
VARIANTS = {"referentie_0.5": 0.5, "strikt_1.0": 1.0}
Y = np.linspace(0, 1, 101)
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
Q_READ = [0.6915, 0.8413, 0.90, 0.95]
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]
seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))

ycols = [f"y_{i:03d}" for i in range(len(Y))]
fc = open(f"{OUT}/curves.csv", "w", newline=""); wc = csv.writer(fc)
wc.writerow(["variant", "threshold", "river", "village", "period", "pair", "curve",
             "n_events"] + ycols)
fs = open(f"{OUT}/summary.csv", "w", newline=""); ws = csv.writer(fs)
head = ["variant", "threshold", "flood_mirror", "river", "village", "river_location",
        "period", "pair", "n_events", "k_minor", "k_major", "t_minor", "t_major",
        "cop_name", "dist1", "dist2"]
for q in Q_READ:
    s = f"{q:g}"
    head += [f"uncond_q{s}", f"minor_q{s}", f"major_q{s}", f"indep_q{s}",
             f"gap_q{s}", f"marginal_part_q{s}", f"copula_part_q{s}"]
ws.writerow(head)
fw = open(f"{OUT}/week_overlap.csv", "w", newline=""); ww = csv.writer(fw)
ww.writerow(["variant", "threshold", "flood_mirror", "river", "village", "period",
             "n_weeks", "drought_weeks", "flood_weeks", "both_weeks",
             "share_drought_weeks_also_flood"])

t0 = time.time(); done = 0
for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
    for li, (river, village, rloc, lat, lon) in enumerate(locs):
        seed = int(seeds[pi * len(locs) + li].generate_state(1)[0] % (2 ** 32 - 1))
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(max_w, mean_w)
        sri_vals = np.asarray(sri.values, float)
        q_vals = np.asarray(q.values, float)
        for vname, thr in VARIANTS.items():
            mirror = float(norm.cdf(thr))
            # weken die tegelijk droogte en flood zijn onder deze drempel
            dw = sri_vals < -thr
            fw_ = q_vals > mirror
            both = dw & fw_
            ww.writerow([vname, thr, round(mirror, 4), river, village, pname,
                         int(np.isfinite(sri_vals).sum()), int(dw.sum()), int(fw_.sum()),
                         int(both.sum()),
                         round(float(both.sum() / dw.sum()), 4) if dw.sum() else ""])
            it = Intensity_calc(sri, q, thr)
            dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
            d2 = flood_peak_after_drought(q, dr["end_time"].values, DT)
            sev = mean_severity_per_week(dr["max_intensity"].values,
                                         dr["duration_weeks"].values)
            var = {"drought_peak": np.asarray(dr["drought_peak"].values, float),
                   "mean_drought_severity": sev}
            for pair, X in PAIRS.items():
                try:
                    res = fit_copula(var[pair], d2, X, Y, q, period_after_event=DT,
                                     n_draw=N_DRAW, seed=seed, axis="quantile",
                                     marginals="parametric")
                except ValueError as err:
                    print(f"OVERGESLAGEN {vname} {river}/{village} {pname} {pair}: {err}",
                          flush=True)
                    continue
                for naam, key in (("minor", "conditional_minor"), ("major", "conditional_major"),
                                  ("unconditional", "unconditional"),
                                  ("independence", "independence_reference")):
                    wc.writerow([vname, thr, river, village, pname, pair, naam,
                                 res["n_events"]] + [round(float(v), 6) for v in res[key]])
                row = [vname, thr, round(mirror, 4), river, village, rloc, pname, pair,
                       res["n_events"], res["k_minor"], res["k_major"],
                       round(res["t_minor"], 6), round(res["t_major"], 6),
                       res["copula_name"], res["dist1"], res["dist2"]]
                for qq in Q_READ:
                    i = int(round(qq * 100))
                    u = float(res["unconditional"][i]); mn = float(res["conditional_minor"][i])
                    mj = float(res["conditional_major"][i])
                    ind = float(res["independence_reference"][i])
                    row += [round(u, 4), round(mn, 4), round(mj, 4), round(ind, 4),
                            round(mn - u, 4), round(ind - u, 4), round(mn - ind, 4)]
                ws.writerow(row)
        fc.flush(); fs.flush(); fw.flush()
        done += 1
        el = time.time() - t0
        print(f"[{done}/96] {pname:6} {river:8} {village[:22]:22} {el:6.1f}s "
              f"eta {el/done*(96-done):5.1f}s", flush=True)
fc.close(); fs.close(); fw.close()
print(f"klaar in {time.time()-t0:.1f}s, uitvoer in {OUT}/", flush=True)
