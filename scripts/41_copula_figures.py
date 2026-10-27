"""Figuren 5 tot 9: transitiekansen voor Po Piacenza, Ebro Tudela en Vistula Toruń.

Besluiten van Floris, 22 oktober 2026: Po en Ebro blijven de voorbeeldrivieren,
met bootstrapinterval en "threshold-dependent"; Vistula Toruń komt erbij als de
enige cel die bij beide droogtedrempels standhoudt (changelog 2026-10-22, punt 2).
Figuren met bootstrapband (plan, F-5). De onafhankelijkheidslijn 1 - F_Y stond
er van 22 tot 27 oktober in; op 27 oktober door Floris geschrapt, de opsplitsing
in een marginaal en een copula-deel blijft in de tekst en in appendix E staan.

Per figuur één locatie en één droogtevariabele, periode 1 boven, periode 2 onder:
  links   P(hoogste afvoer in de vier weken na de droogte > q | droogte >= x),
          over het floodquantiel q (horizontaal) en de droogtewaarde x (verticaal).
          De gestippelde lijnen markeren de milde en de zware drempel; daar wordt
          het rechterpaneel afgelezen
  rechts  de milde en de zware curve met 95%-bootstrapband, de unconditionele
          curve, plus het floodniveau 0,6915

Puntschatting en oppervlak komen uit fit_copula met dezelfde invoer en seed als
script 22; de banden uit results/2026-09-02_copula_bootstrap/transition_ci.csv
(iid). Het script controleert dat de puntcurves gelijk zijn aan de bootstrap en
dat de rij van het oppervlak bij de milde drempel gelijk is aan de milde curve.

Kleuren als in de ingediende versie: mild groen, zwaar rood, unconditioneel
oranje, oppervlak in viridis (besluit
Floris 27 oktober 2026; groen/rood is niet kleurenblindveilig, dat is een bewuste
keuze voor continuiteit met R1).

Uitvoer in results/2026-10-22_copula_figures/: fig05 tot fig09 als png (300 dpi)
en pdf, check.txt, README.md, manifest.yaml.

Draaien vanuit de repo-root:
  uv run --frozen python scripts/41_copula_figures.py
"""
import sys, os, json, re, ast, hashlib, platform, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula, flood_peak_after_drought, mean_severity_per_week

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
BOOT = "results/2026-09-02_copula_bootstrap/transition_ci.csv"
OUT = "results/2026-10-22_copula_figures"
THRESHOLD, DT, SEED, N_POINT = 0.5, 4, 42, 100000
Y = np.linspace(0, 1, 101)
Q_TEXT = 0.6915
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
LABEL_PERIOD = {"first": "Period 1 (1995-2009)", "second": "Period 2 (2010-2024)"}
LABEL_PAIR = {"drought_peak": "drought peak", "mean_drought_severity": "mean severity"}
FIGURES = [  # nummer, rivier, locatie, variabele, Engelse plaatsnaam
    (5, "Po", "Piacenza", "drought_peak", "Piacenza"),
    (6, "Ebro", "Tudela", "drought_peak", "Tudela"),
    (7, "Po", "Piacenza", "mean_drought_severity", "Piacenza"),
    (8, "Ebro", "Tudela", "mean_drought_severity", "Tudela"),
    (9, "Vistula", "Turon", "mean_drought_severity", "Toruń"),
]
# Kleuren als in de ingediende versie (notebook cel 25): groen mild, rood zwaar,
# oranje unconditioneel, oppervlak in viridis. Besluit Floris 27 oktober 2026.
MINOR, MAJOR, UNCOND = "green", "red", "orange"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def inputs(data, lat, lon, b, e):
    nlon, nlat = find_nearest_grid_point(data, lon, lat)
    mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
    sri = SRI_calculate(mean_w)
    max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
    q = transform_to_quantiles(max_w, mean_w)
    it = Intensity_calc(sri, q, THRESHOLD)
    dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
    d2 = flood_peak_after_drought(q, dr["end_time"].values, DT)
    sev = mean_severity_per_week(dr["max_intensity"].values, dr["duration_weeks"].values)
    return q, d2, {"drought_peak": np.asarray(dr["drought_peak"].values, float),
                   "mean_drought_severity": sev}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
            for r in rivers for l in r["locations"]]
    seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))
    boot = pd.read_csv(BOOT)
    boot = boot[boot.scheme == "iid"]
    ycols = [f"y_{i:03d}" for i in range(101)]
    checks = []

    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                         "ytick.major.width": 0.6, "pdf.fonttype": 42})

    for nr, river, village, pair, place in FIGURES:
        li = next(i for i, l in enumerate(locs) if l[0] == river and l[1] == village)
        lat, lon = locs[li][2], locs[li][3]
        X = PAIRS[pair]
        fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.6),
                                 gridspec_kw={"width_ratios": [1, 1], "wspace": 0.42,
                                              "hspace": 0.5})
        for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
            q, d2_all, var = inputs(data, lat, lon, b, e)
            d1, d2 = var[pair], d2_all
            m = np.isfinite(d1) & np.isfinite(d2)
            d1, d2 = d1[m], d2[m]
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            seed = int(st % (2 ** 32 - 1))
            np.random.seed(seed)
            res = fit_copula(d1, d2, X, Y, q, period_after_event=DT, n_draw=N_POINT, seed=seed,
                             axis="quantile", marginals="parametric", with_surface=True)
            sel = boot[(boot.river == river) & (boot.village == village)
                       & (boot.period == pname) & (boot.pair == pair)]
            get = lambda qty, kind: sel[(sel.quantity == qty) & (sel.kind == kind)][ycols].values[0]
            dev = max(np.nanmax(np.abs(get("minor_resel", "point") - res["conditional_minor"])),
                      np.nanmax(np.abs(get("major_resel", "point") - res["conditional_major"])))
            vals = res["surface_drought_values"]
            row = int(np.argmin(np.abs(vals - X[0])))
            # het oppervlak staat op een eigen raster van droogtewaarden; de rij die
            # het dichtst bij X[0] ligt hoort de milde curve te benaderen
            surf_dev = float(np.nanmax(np.abs(res["surface"][row] - res["conditional_minor"])))
            checks.append(f"fig{nr:02d} {river} {village} {pname} {pair}: "
                          f"puntcurve vs bootstrap {dev:.1e}; oppervlakrij op x={vals[row]:.3f} "
                          f"(X[0]={X[0]}) vs milde curve {surf_dev:.3f}")

            ax = axes[pi, 0]
            pm = ax.pcolormesh(Y, vals, res["surface"], shading="auto", cmap="viridis",
                               vmin=0, vmax=1, rasterized=True)
            for x0, col, lab in ((X[0], "white", "minor"), (X[1], "red", "major")):
                if vals.min() <= x0 <= vals.max():
                    ax.axhline(x0, color=col, lw=1.0, ls=(0, (4, 2)))
                    ax.text(1.0, x0, f" {lab}", color=INK2, va="center", ha="left", fontsize=7,
                            transform=ax.get_yaxis_transform())
            ax.set_xlim(0, 1)
            ax.set_xlabel("Flood quantile q")
            ax.set_ylabel(f"Prior {LABEL_PAIR[pair]} x")
            cb = fig.colorbar(pm, ax=ax, fraction=0.05, pad=0.16)
            cb.set_label("P(peak > q | drought ≥ x)", fontsize=7)
            cb.outline.set_linewidth(0.4)
            cb.ax.tick_params(labelsize=7, width=0.4)

            ax = axes[pi, 1]
            for qty, col, lab in (("minor_resel", MINOR, "Minor drought"),
                                  ("major_resel", MAJOR, "Major drought")):
                lo, hi = get(qty, "lo"), get(qty, "hi")
                ax.fill_between(Y, lo, hi, color=col, alpha=0.18, lw=0)
                ax.plot(Y, res["conditional_minor" if qty == "minor_resel" else "conditional_major"],
                        color=col, lw=1.4, label=lab)
            ax.plot(Y, res["unconditional"], color=UNCOND, lw=1.4, label="Unconditional")
            ax.axvline(Q_TEXT, color="#b9b8b3", lw=0.8, zorder=0,
                       label=f"Flood threshold, q = {Q_TEXT}")
            ax.set_xlim(0, 1); ax.set_ylim(0, 1)
            ax.grid(color=GRID, lw=0.5); ax.set_axisbelow(True)
            ax.set_xlabel("Flood quantile q")
            ax.set_ylabel("Transition probability")
            for a in axes[pi]:
                for s in ("top", "right"):
                    a.spines[s].set_visible(False)
            axes[pi, 0].set_title(f"({'ac'[pi]})  {LABEL_PERIOD[pname]}", loc="left", fontsize=8)
            axes[pi, 1].set_title(f"({'bd'[pi]})  {res['n_events']} droughts, "
                                  f"{res['k_major']} major", loc="left", fontsize=8)
            if pi == 0:
                handles, labels = axes[pi, 1].get_legend_handles_labels()
                fig.legend(handles, labels, frameon=False, fontsize=7, loc="lower center",
                           ncol=5, handlelength=2.2, bbox_to_anchor=(0.5, -0.02))
        fig.suptitle(f"{river}, {place}: {LABEL_PAIR[pair]}", x=0.02, ha="left",
                     fontsize=9, color=INK)
        for ext, kw in (("png", {"dpi": 300}), ("pdf", {})):
            fig.savefig(f"{OUT}/fig{nr:02d}_{river.lower()}_{village.lower()}_{pair}.{ext}",
                        bbox_inches="tight", facecolor="white", **kw)
        plt.close(fig)

    with open(f"{OUT}/check.txt", "w") as f:
        f.write("\n".join(checks) + "\n")
    with open(f"{OUT}/manifest.yaml", "w") as f:
        f.write(f"script: scripts/41_copula_figures.py\nrun_minutes: {(time.time() - t0) / 60:.1f}\n"
                f"python: {platform.python_version()}\n"
                f"inputs:\n  {DATA}: {sha256(DATA)}\n  {BOOT}: {sha256(BOOT)}\n"
                f"seed_scheme: \"numpy.random.SeedSequence({SEED}).spawn(96), als script 22\"\n")
    print("\n".join(checks))


if __name__ == "__main__":
    main()
