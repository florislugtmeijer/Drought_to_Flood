"""T-11: figuren bij de copula-review en bij stap A.

Rekent niets opnieuw. Leest alleen de CSV's uit twee eerdere runs:
  results/2026-09-02_copula_definition_variants/  curves.csv en summary.csv
  results/2026-09-01_copula_selection/            copula_selection.csv

Vier figuren:
  1. axis_artefact_example.png     een cel, de gepubliceerde aflezing naast
                                   dezelfde curves op een gemeenschappelijke as
  2. axis_artefact_all_cells.png   hetzelfde over alle 192 cellen
  3. definition_variants_effect.png  wat R-02 en R-03 met de curves doen
  4. copula_selection_overview.png   familiekeuze, AIC-marge en k_major

Geen beschrijving in de figuren zelf, die komt als caption onder de afbeelding te
staan, zie figures/caption_en.md. Labels in het Engels, want het manuscript is dat.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with matplotlib --no-project \
      python scripts/15_copula_review_figures.py
"""
import os, csv, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VAR = "results/2026-09-02_copula_definition_variants"
SEL = "results/2026-09-01_copula_selection"
FIGV = f"{VAR}/figures"
FIGS = f"{SEL}/figures"
os.makedirs(FIGV, exist_ok=True)
os.makedirs(FIGS, exist_ok=True)
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]

GREEN, RED, ORANGE, BLUE = "#2a7f3f", "#c0392b", "#e08214", "#2c6fbb"
PAIR_LABEL = {"drought_peak": "Drought peak",
              "mean_drought_severity": "Mean drought severity"}


def load_curves():
    cond, uncond = {}, {}
    with open(f"{VAR}/curves.csv") as fh:
        for r in csv.DictReader(fh):
            v = np.array([float(r[c]) for c in YC])
            if r["curve"] == "unconditioneel":
                uncond[(r["river"], r["village"], r["period"])] = v
            else:
                cond[(r["river"], r["village"], r["period"], r["pair"],
                      r["variant"], r["axis"], r["curve"])] = v
    return cond, uncond


cond, uncond = load_curves()
summary = list(csv.DictReader(open(f"{VAR}/summary.csv")))
selection = list(csv.DictReader(open(f"{SEL}/copula_selection.csv")))
cells = sorted({(r["river"], r["village"], r["period"], r["pair"]) for r in summary})
print(f"ingelezen: {len(cond)} conditionele curves, {len(uncond)} unconditionele, "
      f"{len(cells)} cellen", flush=True)


# --------------------------------------------------------------- figuur 1
# Representatieve cel: de mediaan van het aantal punten waar de conditionele
# curve op de ruwe as onder de unconditionele ligt. Niet de gunstigste cel, niet
# de ongunstigste.
pub = [r for r in summary if r["variant"] == "gepubliceerd"
       and r["pair"] == "drought_peak"]
pub.sort(key=lambda r: int(r["n_punten_cond_onder_uncond_ruweas"]))
pick = pub[len(pub) // 2]
key = (pick["river"], pick["village"], pick["period"], "drought_peak")
print(f"figuur 1 gebruikt: {key}, ruwe-as telling "
      f"{pick['n_punten_cond_onder_uncond_ruweas']}/101", flush=True)

u = uncond[key[:3]]
fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
for ax, axis, titel in zip(
        axes, ("rang", "ruwe"),
        ("As published: conditional curves read on the event-rank scale",
         "Both curves on the same runoff-quantile scale")):
    mn = cond[key + ("gepubliceerd", axis, "minor")]
    mj = cond[key + ("gepubliceerd", axis, "major")]
    ax.plot(Y, mn, color=GREEN, lw=2, label="Conditional | minor drought")
    ax.plot(Y, mj, color=RED, lw=2, label="Conditional | severe drought")
    ax.plot(Y, u, color=ORANGE, lw=2, label="Unconditional")
    ax.fill_between(Y, mn, u, where=(mn < u), color=ORANGE, alpha=0.15,
                    interpolate=True)
    ax.set_title(titel, fontsize=11)
    ax.set_xlabel("Future flood quantile")
    ax.set_ylabel("Exceedance probability")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9, loc="upper right")
fig.savefig(f"{FIGV}/axis_artefact_example.png", dpi=200, facecolor="white")
plt.close(fig)


# --------------------------------------------------------------- figuur 2
d_rank, d_raw, n_rank, n_raw = [], [], [], []
for river, village, period, pair in cells:
    k = (river, village, period)
    if k not in uncond:
        continue
    uu = uncond[k]
    for axis, bucket, cnt in (("rang", d_rank, n_rank), ("ruwe", d_raw, n_raw)):
        ck = (river, village, period, pair, "gepubliceerd", axis, "minor")
        if ck not in cond:
            continue
        d = cond[ck] - uu
        bucket.append(d)
        cnt.append(int(np.sum(d < 0)))
d_rank, d_raw = np.array(d_rank), np.array(d_raw)
print(f"figuur 2: {len(d_rank)} cellen op de rang-as, {len(d_raw)} op de ruwe as",
      flush=True)

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
ax = axes[0]
for arr, colour, label in ((d_rank, BLUE, "Read on the event-rank scale (as published)"),
                           (d_raw, ORANGE, "Read on the runoff-quantile scale")):
    med = np.median(arr, axis=0)
    lo, hi = np.percentile(arr, 25, axis=0), np.percentile(arr, 75, axis=0)
    ax.plot(Y, med, color=colour, lw=2, label=label)
    ax.fill_between(Y, lo, hi, color=colour, alpha=0.20)
ax.axhline(0, color="black", lw=1)
ax.set_xlabel("Future flood quantile")
ax.set_ylabel("Conditional minus unconditional probability")
ax.set_xlim(0, 1); ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="lower right")
ax.set_title("Median across 192 cells, shading is the interquartile range", fontsize=11)

ax = axes[1]
bins = np.arange(-0.5, 102.5, 4)
ax.hist(n_rank, bins=bins, color=BLUE, alpha=0.75,
        label="Read on the event-rank scale (as published)")
ax.hist(n_raw, bins=bins, color=ORANGE, alpha=0.75,
        label="Read on the runoff-quantile scale")
ax.set_xlabel("Number of the 101 grid points where conditional < unconditional")
ax.set_ylabel("Number of cells")
ax.set_xlim(0, 101); ax.grid(alpha=0.3); ax.legend(fontsize=9, loc="upper center")
ax.set_title("Distribution over all 192 cells", fontsize=11)
fig.savefig(f"{FIGV}/axis_artefact_all_cells.png", dpi=200, facecolor="white")
plt.close(fig)


# --------------------------------------------------------------- figuur 3
combos = [("R02_venster", "drought_peak"), ("R02_venster", "mean_drought_severity"),
          ("R03_duur", "mean_drought_severity"), ("R02_R03", "drought_peak"),
          ("R02_R03", "mean_drought_severity")]
labels = ["R-02\nDrought peak", "R-02\nMean severity", "R-03\nMean severity",
          "R-02 + R-03\nDrought peak", "R-02 + R-03\nMean severity"]
vals = [[float(r["max_diff_minor_vs_gepubliceerd"]) for r in summary
         if r["variant"] == v and r["pair"] == p] for v, p in combos]
fam = [100.0 * sum(1 for r in summary if r["variant"] == v and r["pair"] == p
                   and r["familie_gewijzigd"] == "1")
       / max(1, sum(1 for r in summary if r["variant"] == v and r["pair"] == p))
       for v, p in combos]

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.0), constrained_layout=True)
ax = axes[0]
bp = ax.boxplot(vals, tick_labels=labels, showfliers=True, patch_artist=True,
                flierprops=dict(marker=".", markersize=4, alpha=0.5))
for patch in bp["boxes"]:
    patch.set_facecolor(BLUE); patch.set_alpha(0.55)
for med in bp["medians"]:
    med.set_color("black")
ax.set_ylabel("Largest absolute shift in the conditional curve")
ax.set_title("Effect of the two definition corrections, per cell", fontsize=11)
ax.tick_params(axis="x", labelsize=8.5); ax.grid(alpha=0.3, axis="y")

ax = axes[1]
ax.bar(range(len(fam)), fam, color=RED, alpha=0.75)
ax.set_xticks(range(len(fam))); ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Cells in which the AIC-selected family changes (%)")
ax.set_ylim(0, 100); ax.grid(alpha=0.3, axis="y")
ax.set_title("Stability of the family choice under the corrections", fontsize=11)
fig.savefig(f"{FIGV}/definition_variants_effect.png", dpi=200, facecolor="white")
plt.close(fig)


# --------------------------------------------------------------- figuur 4
fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8), constrained_layout=True)
cnt = collections.Counter(r["cop_name"] for r in selection)
names = [n for n, _ in cnt.most_common()]
ax = axes[0]
ax.barh(range(len(names)), [cnt[n] for n in names], color=BLUE, alpha=0.8)
ax.set_yticks(range(len(names))); ax.set_yticklabels(names, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("Number of cells (of 192)")
ax.set_title("Copula family selected by AIC", fontsize=11)
ax.grid(alpha=0.3, axis="x")

ax = axes[1]
da = np.array([float(r["delta_aic_next"]) for r in selection])
ax.hist(da, bins=np.arange(0, max(6.0, da.max()) + 0.25, 0.25), color=BLUE, alpha=0.8)
ax.axvline(2, color=RED, lw=2, label="Conventional threshold, $\\Delta$AIC = 2")
ax.set_xlabel("$\\Delta$AIC to the runner-up family")
ax.set_ylabel("Number of cells")
ax.set_xlim(0, 6); ax.legend(fontsize=9); ax.grid(alpha=0.3, axis="y")
ax.set_title(f"{int(np.sum(da < 2))} of {len(da)} cells below 2", fontsize=11)

ax = axes[2]
km = np.array([int(r["k_major"]) for r in selection])
ax.hist(km, bins=np.arange(-0.5, km.max() + 1.5, 1), color=BLUE, alpha=0.8)
ax.axvline(np.median(km), color=RED, lw=2, label=f"Median = {int(np.median(km))}")
ax.set_xlabel("Droughts above the severe-drought threshold, $k_{major}$")
ax.set_ylabel("Number of cells")
ax.legend(fontsize=9); ax.grid(alpha=0.3, axis="y")
ax.set_title("Support behind the severe-drought curve", fontsize=11)
fig.savefig(f"{FIGS}/copula_selection_overview.png", dpi=200, facecolor="white")
plt.close(fig)

print(f"\ngeschreven:")
for p in (f"{FIGV}/axis_artefact_example.png", f"{FIGV}/axis_artefact_all_cells.png",
          f"{FIGV}/definition_variants_effect.png",
          f"{FIGS}/copula_selection_overview.png"):
    print(f"  {p}  ({os.path.getsize(p)//1024} kB)")
