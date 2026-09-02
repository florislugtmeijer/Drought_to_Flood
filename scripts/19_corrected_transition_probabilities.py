"""T-11 stap C: de gecorrigeerde transitiekansen, met de drie besluiten erin.

Drie besluiten van Floris, 2 september 2026:
  R-01  de conditionele curve wordt afgelezen op F_Y(q), zodat hij dezelfde vraag
        beantwoordt als de unconditionele curve. Dit is geen methodewijziging maar
        een reparatie: pagina 21 van het manuscript geeft de formule
        P(Y > y | X >= x) = (1 - F_X(x) - F_Y(y) + C(F_X(x), F_Y(y))) / (1 - F_X(x)),
        en de bron sloeg de stap F_Y over.
  R-02  het floodvenster telt vier weken na afloop van de droogte, zoals de tekst
        op pagina 19 zegt, in plaats van vijf weekpunten inclusief de laatste
        droogteweek.
  R-03  mean_drought_severity deelt door het aantal weken, niet door einde min
        begin.

En één ding wordt beide kanten op doorgerekend, omdat het manuscript en de code
uiteenlopen:
  F_X en F_Y  "parametric" volgt pagina 21, dus uit de gefitte marginalen.
              "empirical" volgt wat de code voor de droogtezijde al deed.

Daarnaast wordt het gat tussen de conditionele en de unconditionele curve
opgesplitst, want dat is nodig om te kunnen zeggen wat de copula bijdraagt:

  gat            = conditioneel - unconditioneel
  marginaal deel = (1 - F_Y) - unconditioneel      is het venster na een droogte
                                                    natter dan een willekeurig venster
  copula deel    = conditioneel - (1 - F_Y)        hangt de piek samen met de
                                                    zwaarte van de droogte

Bij volledige onafhankelijkheid is het copula deel nul en blijft het marginale deel
over. Dat onderscheid is de kern van de vraag wat het copula-raamwerk toevoegt.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/19_corrected_transition_probabilities.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import (fit_copula, flood_peak_after_drought, mean_severity_per_week)

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_copula_corrected"
THRESHOLD, DT, N_DRAW, SEED = 0.5, 4, 100000, 42
Y = np.linspace(0, 1, 101)
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
MARGINALS = ["empirical", "parametric"]
Q_READ = [0.6915, 0.90, 0.95, 0.99]
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]
seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))

ycols = [f"y_{i:03d}" for i in range(len(Y))]
fc = open(f"{OUT}/curves.csv", "w", newline="")
wc = csv.writer(fc)
wc.writerow(["river", "village", "period", "pair", "marginals", "curve", "n_events"] + ycols)
fs = open(f"{OUT}/summary.csv", "w", newline="")
ws = csv.writer(fs)
head = ["river", "village", "river_location", "period", "pair", "marginals",
        "n_events", "k_minor", "k_major", "cop_name", "par", "aic",
        "dist1", "dist2", "n_nonfinite_draws"]
for q in Q_READ:
    s = f"{q:g}"
    head += [f"uncond_q{s}", f"minor_q{s}", f"major_q{s}", f"indep_q{s}",
             f"gap_q{s}", f"marginal_part_q{s}", f"copula_part_q{s}"]
ws.writerow(head)

sanity = {"cellen": 0, "lege_vensters": 0, "events_terug_R03": 0, "nan_trekkingen": 0}
t0 = time.time(); done = 0
for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
    for li, (river, village, rloc, lat, lon) in enumerate(locs):
        seed = int(seeds[pi * len(locs) + li].generate_state(1)[0] % (2 ** 32 - 1))
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(max_w, mean_w)          # copula-referentie, cel 25
        it = Intensity_calc(sri, q, THRESHOLD)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)

        # R-02 en R-03, de twee besluiten
        d2 = flood_peak_after_drought(q, dr["end_time"].values, DT)
        sev = mean_severity_per_week(dr["max_intensity"].values, dr["duration_weeks"].values)
        peak = np.asarray(dr["drought_peak"].values, float)
        sanity["lege_vensters"] += int(np.sum(~np.isfinite(d2)))
        sanity["events_terug_R03"] += int(np.sum(
            ~np.isfinite(np.asarray(dr["mean_drought_severity"].values, float))
            & np.isfinite(sev)))
        variabele = {"drought_peak": peak, "mean_drought_severity": sev}

        for pair, X in PAIRS.items():
            for marg in MARGINALS:
                try:
                    res = fit_copula(variabele[pair], d2, X, Y, q,
                                     period_after_event=DT, n_draw=N_DRAW, seed=seed,
                                     axis="quantile", marginals=marg)
                except ValueError as err:
                    print(f"OVERGESLAGEN {river}/{village} {pname} {pair} {marg}: {err}",
                          flush=True)
                    continue
                sanity["nan_trekkingen"] += res["n_nonfinite_draws"]
                for naam, key in (("minor", "conditional_minor"),
                                  ("major", "conditional_major"),
                                  ("unconditional", "unconditional"),
                                  ("independence", "independence_reference")):
                    wc.writerow([river, village, pname, pair, marg, naam, res["n_events"]]
                                + [round(float(v), 6) for v in res[key]])
                row = [river, village, rloc, pname, pair, marg, res["n_events"],
                       res["k_minor"], res["k_major"], res["copula_name"],
                       np.round(res["par"], 6) if np.ndim(res["par"]) == 0
                       else np.round(res["par"], 6).tolist(),
                       round(res["aic"], 4), res["dist1"], res["dist2"],
                       res["n_nonfinite_draws"]]
                for qq in Q_READ:
                    i = int(round(qq * 100))
                    u = float(res["unconditional"][i])
                    mn = float(res["conditional_minor"][i])
                    mj = float(res["conditional_major"][i])
                    ind = float(res["independence_reference"][i])
                    row += [round(u, 4), round(mn, 4), round(mj, 4), round(ind, 4),
                            round(mn - u, 4), round(ind - u, 4), round(mn - ind, 4)]
                ws.writerow(row)
                sanity["cellen"] += 1
        fc.flush(); fs.flush()
        done += 1
        el = time.time() - t0
        print(f"[{done}/96] {pname:6} {river:8} {village[:22]:22} {el:6.1f}s "
              f"eta {el/done*(96-done):5.1f}s", flush=True)
fc.close(); fs.close()
print(f"\nsanity: {sanity}", flush=True)
print(f"klaar in {time.time()-t0:.1f}s, uitvoer in {OUT}/", flush=True)
