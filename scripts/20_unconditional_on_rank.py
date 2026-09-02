"""T-11: de omgekeerde presentatie, met de unconditionele lijn op de copula-schaal.

Twee manieren om dezelfde reparatie te tonen.

  Route A  de conditionele curve naar de runoff-quantielschaal halen, door hem af
           te lezen op F_Y(q). Dat is scripts/19 en dat is de gerapporteerde route.

  Route B  de unconditionele lijn naar de copula-schaal halen, door hem af te lezen
           op het runoff-quantiel dat bij elke rang hoort. De gepubliceerde
           conditionele curves blijven dan onaangeroerd staan en alleen de
           referentielijn verschuift.

Het gat tussen de curves is op overeenkomstige punten identiek. Dat wordt hier ook
gecontroleerd in plaats van aangenomen. Het verschil zit in het plaatje.

Marginalen parametrisch, conform pagina 21 van het manuscript en het besluit van
Floris op 2 september.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --with matplotlib --no-project \
      python scripts/20_unconditional_on_rank.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula, flood_peak_after_drought, mean_severity_per_week

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_copula_corrected"
FIG = f"{OUT}/figures"
THRESHOLD, DT, N_DRAW, SEED, MARG = 0.5, 4, 100000, 42, "parametric"
Y = np.linspace(0, 1, 101)
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
os.makedirs(FIG, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]
seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))

ycols = [f"y_{i:03d}" for i in range(len(Y))]
fh = open(f"{OUT}/curves_route_b.csv", "w", newline="")
w = csv.writer(fh)
w.writerow(["river", "village", "period", "pair", "curve", "n_events"] + ycols)

controle, voorbeeld = [], {}
t0 = time.time(); done = 0
for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
    for li, (river, village, lat, lon) in enumerate(locs):
        seed = int(seeds[pi * len(locs) + li].generate_state(1)[0] % (2 ** 32 - 1))
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(max_w, mean_w)
        it = Intensity_calc(sri, q, THRESHOLD)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
        d2 = flood_peak_after_drought(q, dr["end_time"].values, DT)
        sev = mean_severity_per_week(dr["max_intensity"].values, dr["duration_weeks"].values)
        var = {"drought_peak": np.asarray(dr["drought_peak"].values, float),
               "mean_drought_severity": sev}
        for pair, X in PAIRS.items():
            try:
                a = fit_copula(var[pair], d2, X, Y, q, period_after_event=DT,
                               n_draw=N_DRAW, seed=seed, axis="quantile", marginals=MARG)
                bb = fit_copula(var[pair], d2, X, Y, q, period_after_event=DT,
                                n_draw=N_DRAW, seed=seed, axis="rank", marginals=MARG)
            except ValueError:
                continue
            # controle: het gat is op overeenkomstige punten gelijk. Route A leest
            # bij runoff-quantiel Y[j], route B bij de rang a["read_at"][j], en dat
            # is hetzelfde punt.
            gat_a = a["conditional_minor"] - a["unconditional"]
            gat_b = np.interp(a["read_at"], Y, bb["conditional_minor"] - bb["unconditional_on_rank"])
            ok = np.isfinite(gat_a) & np.isfinite(gat_b)
            if ok.any():
                controle.append(float(np.max(np.abs(gat_a[ok] - gat_b[ok]))))
            for naam, key in (("minor", "conditional_minor"), ("major", "conditional_major"),
                              ("unconditional_on_rank", "unconditional_on_rank")):
                w.writerow([river, village, pname, pair, naam, bb["n_events"]]
                           + [round(float(v), 6) for v in bb[key]])
            if (river, village, pname, pair) == ("Ebro", "Tudela", "second", "drought_peak"):
                voorbeeld = {"a": a, "b": bb}
        fh.flush(); done += 1
        el = time.time() - t0
        print(f"[{done}/96] {pname:6} {river:8} {village[:22]:22} {el:6.1f}s "
              f"eta {el/done*(96-done):5.1f}s", flush=True)
fh.close()
c = np.array(controle)
print(f"\ncontrole, grootste verschil tussen het gat van route A en route B:")
print(f"  mediaan {np.median(c):.2e}  p90 {np.percentile(c,90):.2e}  max {c.max():.2e}  "
      f"over {len(c)} cellen", flush=True)

# figuur: dezelfde cel in drie presentaties
a, bb = voorbeeld["a"], voorbeeld["b"]
G, R, O = "#2a7f3f", "#c0392b", "#e08214"
fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.0), constrained_layout=True)
panels = [("As published", bb["conditional_minor"], bb["conditional_major"], a["unconditional"],
           "Future flood quantile"),
          ("Route A, conditional curves rescaled", a["conditional_minor"],
           a["conditional_major"], a["unconditional"], "Future flood quantile"),
          ("Route B, unconditional curve rescaled", bb["conditional_minor"],
           bb["conditional_major"], bb["unconditional_on_rank"],
           "Rank of the post-drought peak")]
for ax, (titel, mn, mj, un, xlabel) in zip(axes, panels):
    ax.plot(Y, mn, color=G, lw=2, label="Conditional | minor drought")
    ax.plot(Y, mj, color=R, lw=2, label="Conditional | severe drought")
    ax.plot(Y, un, color=O, lw=2, label="Unconditional")
    ax.set_title(titel, fontsize=11); ax.set_xlabel(xlabel)
    ax.set_ylabel("Exceedance probability")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3)
axes[0].legend(fontsize=9, loc="upper right")
fig.savefig(f"{FIG}/three_presentations.png", dpi=200, facecolor="white")
plt.close(fig)
print(f"geschreven: {OUT}/curves_route_b.csv en {FIG}/three_presentations.png", flush=True)
