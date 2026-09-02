"""T-11: figuren op de gecorrigeerde run, gepubliceerd naast gecorrigeerd.

Rekent niets opnieuw. Leest twee resultaatmappen:
  results/2026-09-02_copula_definition_variants/curves.csv   de gepubliceerde
      aflezing, dus rangschaal en de oude eventdefinities
  results/2026-09-02_copula_corrected/curves.csv             de gecorrigeerde,
      dus R-01, R-02 en R-03 en parametrische marginalen

Levert:
  figures/corrected_overview.png              alle 16 rivieren als kleine panelen
  figures/per_river/corrected_<rivier>.png    per rivier een blad

Naast de conditionele en de unconditionele curve staat ook de onafhankelijkheids-
lijn, 1 - F_Y. Dat is wat je zou zien als de zwaarte van de droogte niets uitmaakt.
De afstand tussen die lijn en de unconditionele curve is het marginale deel, de
afstand tussen de conditionele curve en die lijn is wat de copula bijdraagt.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with matplotlib --no-project \
      python scripts/21_corrected_figures.py
"""
import os, csv
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OLD = "results/2026-09-02_copula_definition_variants/curves.csv"
NEW = "results/2026-09-02_copula_corrected/curves.csv"
FIG = "results/2026-09-02_copula_corrected/figures"
PER = f"{FIG}/per_river"
MARG = "parametric"
os.makedirs(PER, exist_ok=True)
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
GREEN, RED, ORANGE, GREY = "#2a7f3f", "#c0392b", "#e08214", "#7a7a7a"
COLS = [("first", "drought_peak", "Period 1, drought peak"),
        ("first", "mean_drought_severity", "Period 1, mean severity"),
        ("second", "drought_peak", "Period 2, drought peak"),
        ("second", "mean_drought_severity", "Period 2, mean severity")]

old, new, rivers, villages = {}, {}, [], {}
for r in csv.DictReader(open(OLD)):
    if r["variant"] == "gepubliceerd" and r["axis"] == "rang":
        old[(r["river"], r["village"], r["period"], r["pair"], r["curve"])] = \
            np.array([float(r[c]) for c in YC])
for r in csv.DictReader(open(NEW)):
    if r["marginals"] != MARG:
        continue
    new[(r["river"], r["village"], r["period"], r["pair"], r["curve"])] = \
        np.array([float(r[c]) for c in YC])
    if r["river"] not in rivers:
        rivers.append(r["river"])
    villages.setdefault(r["river"], [])
    if r["village"] not in villages[r["river"]]:
        villages[r["river"]].append(r["village"])

LEGEND = [
    Line2D([], [], color=GREEN, ls="--", lw=1.5, label="Minor drought, as published"),
    Line2D([], [], color=GREEN, ls="-", lw=2.0, label="Minor drought, corrected"),
    Line2D([], [], color=RED, ls="--", lw=1.5, label="Severe drought, as published"),
    Line2D([], [], color=RED, ls="-", lw=2.0, label="Severe drought, corrected"),
    Line2D([], [], color=ORANGE, ls="-", lw=2.0, label="Unconditional"),
    Line2D([], [], color=GREY, ls=":", lw=1.8, label="No dependence, $1-F_Y$"),
]


def draw(ax, river, village, period, pair):
    k = (river, village, period, pair)
    for curve, colour in (("minor", GREEN), ("major", RED)):
        if k + (curve,) in old:
            ax.plot(Y, old[k + (curve,)], color=colour, ls="--", lw=1.4, alpha=0.8)
        if k + (curve,) in new:
            ax.plot(Y, new[k + (curve,)], color=colour, ls="-", lw=2.0)
    if k + ("independence",) in new:
        ax.plot(Y, new[k + ("independence",)], color=GREY, ls=":", lw=1.8)
    if k + ("unconditional",) in new:
        ax.plot(Y, new[k + ("unconditional",)], color=ORANGE, lw=2.0)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3)


for river in rivers:
    vs = villages[river]
    fig, axes = plt.subplots(len(vs), len(COLS), figsize=(15.5, 3.5 * len(vs) + 1.4),
                             sharex=True, sharey=True, constrained_layout=True)
    axes = np.atleast_2d(axes)
    for i, village in enumerate(vs):
        for j, (period, pair, titel) in enumerate(COLS):
            ax = axes[i, j]
            draw(ax, river, village, period, pair)
            if i == 0:
                ax.set_title(titel, fontsize=11)
            if j == 0:
                ax.set_ylabel(f"{village}\n\nExceedance probability", fontsize=9.5)
            if i == len(vs) - 1:
                ax.set_xlabel("Future flood quantile", fontsize=10)
    fig.suptitle(river, fontsize=15, fontweight="bold")
    fig.legend(handles=LEGEND, loc="upper center", ncol=6, fontsize=9,
               frameon=False, bbox_to_anchor=(0.5, 0.0))
    naam = river.replace("ô", "o").replace("ó", "o").replace(" ", "_").lower()
    fig.savefig(f"{PER}/corrected_{naam}.png", dpi=170, facecolor="white",
                bbox_inches="tight")
    plt.close(fig)
    print(f"  {river}", flush=True)

fig, axes = plt.subplots(4, 4, figsize=(16, 13), sharex=True, sharey=True,
                         constrained_layout=True)
for ax, river in zip(axes.ravel(), rivers):
    for src, style in ((old, dict(ls="--", lw=1.4, alpha=0.8)), (new, dict(ls="-", lw=2.0))):
        for curve, colour in (("minor", GREEN), ("major", RED)):
            stack = [v for k, v in src.items() if k[0] == river and k[4] == curve]
            if stack:
                ax.plot(Y, np.nanmedian(np.array(stack), axis=0), color=colour, **style)
    for curve, colour, style in (("independence", GREY, dict(ls=":", lw=1.8)),
                                 ("unconditional", ORANGE, dict(lw=2.0))):
        stack = [v for k, v in new.items() if k[0] == river and k[4] == curve]
        if stack:
            ax.plot(Y, np.nanmedian(np.array(stack), axis=0), color=colour, **style)
    ax.set_title(river, fontsize=11)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3)
for ax in axes[-1, :]:
    ax.set_xlabel("Future flood quantile", fontsize=10)
for ax in axes[:, 0]:
    ax.set_ylabel("Exceedance probability", fontsize=10)
fig.legend(handles=LEGEND, loc="upper center", ncol=6, fontsize=10,
           frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.savefig(f"{FIG}/corrected_overview.png", dpi=170, facecolor="white",
            bbox_inches="tight")
plt.close(fig)
print(f"\ngeschreven: {FIG}/corrected_overview.png en "
      f"{len([f for f in os.listdir(PER) if f.startswith('corrected_')])} bladen in {PER}/",
      flush=True)
