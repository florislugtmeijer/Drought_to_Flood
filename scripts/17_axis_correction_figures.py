"""T-11: figuren bij de as-correctie, gepubliceerde aflezing naast de gecorrigeerde.

Rekent niets opnieuw. Leest curves.csv uit
results/2026-09-02_copula_definition_variants/.

Levert:
  figures/axis_correction_overview.png        alle 16 rivieren als kleine panelen
  figures/per_river/axis_correction_<rivier>.png   per rivier een blad met alle
                                              3 locaties maal 2 periodes maal 2
                                              variabelenparen

In elk paneel staan beide aflezingen over elkaar. Gestippeld is de gepubliceerde
aflezing, waarbij de conditionele curve op de rangschaal van de post-droogte pieken
staat. Doorgetrokken is de gecorrigeerde, waarbij hij op de runoff-quantielschaal
is afgelezen. De unconditionele lijn is in beide dezelfde, want die stond al op de
runoff-quantielschaal.

Geen beschrijving in de figuren zelf, die komt als caption onder de afbeelding te
staan. Labels in het Engels, want het manuscript is dat.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with matplotlib --no-project \
      python scripts/17_axis_correction_figures.py
"""
import os, csv, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

VAR = "results/2026-09-02_copula_definition_variants"
FIG = f"{VAR}/figures"
PER = f"{FIG}/per_river"
os.makedirs(PER, exist_ok=True)
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]

GREEN, RED, ORANGE = "#2a7f3f", "#c0392b", "#e08214"
COLS = [("first", "drought_peak", "Period 1, drought peak"),
        ("first", "mean_drought_severity", "Period 1, mean severity"),
        ("second", "drought_peak", "Period 2, drought peak"),
        ("second", "mean_drought_severity", "Period 2, mean severity")]

cond, uncond = {}, {}
rivers, villages = [], collections.OrderedDict()
for r in csv.DictReader(open(f"{VAR}/curves.csv")):
    v = np.array([float(r[c]) for c in YC])
    if r["curve"] == "unconditioneel":
        uncond[(r["river"], r["village"], r["period"])] = v
        continue
    if r["variant"] != "gepubliceerd":
        continue
    cond[(r["river"], r["village"], r["period"], r["pair"], r["axis"], r["curve"])] = v
    if r["river"] not in rivers:
        rivers.append(r["river"])
    villages.setdefault(r["river"], [])
    if r["village"] not in villages[r["river"]]:
        villages[r["river"]].append(r["village"])

LEGEND = [
    Line2D([], [], color=GREEN, ls="--", lw=1.6, label="Minor drought, as published"),
    Line2D([], [], color=GREEN, ls="-", lw=2.0, label="Minor drought, corrected axis"),
    Line2D([], [], color=RED, ls="--", lw=1.6, label="Severe drought, as published"),
    Line2D([], [], color=RED, ls="-", lw=2.0, label="Severe drought, corrected axis"),
    Line2D([], [], color=ORANGE, ls="-", lw=2.0, label="Unconditional"),
]


def draw(ax, river, village, period, pair):
    u = uncond.get((river, village, period))
    if u is None:
        ax.set_axis_off(); return False
    drawn = False
    for curve, colour in (("minor", GREEN), ("major", RED)):
        kp = (river, village, period, pair, "rang", curve)
        kc = (river, village, period, pair, "ruwe", curve)
        if kp in cond:
            ax.plot(Y, cond[kp], color=colour, ls="--", lw=1.5, alpha=0.85)
            drawn = True
        if kc in cond:
            ax.plot(Y, cond[kc], color=colour, ls="-", lw=2.0)
    ax.plot(Y, u, color=ORANGE, lw=2.0)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    return drawn


# ------------------------------------------------------- blad per rivier
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
    # de legenda onder de figuur, met genoeg ruimte zodat hij de x-labels van de
    # onderste rij niet raakt
    fig.legend(handles=LEGEND, loc="upper center", ncol=5, fontsize=9.5,
               frameon=False, bbox_to_anchor=(0.5, 0.0))
    naam = river.replace("ô", "o").replace("ó", "o").replace(" ", "_").lower()
    fig.savefig(f"{PER}/axis_correction_{naam}.png", dpi=170, facecolor="white",
                bbox_inches="tight")
    plt.close(fig)
    print(f"  {river:10s} {len(vs)} locaties", flush=True)


# ------------------------------------------------------- overzicht
fig, axes = plt.subplots(4, 4, figsize=(16, 13), sharex=True, sharey=True,
                         constrained_layout=True)
for ax, river in zip(axes.ravel(), rivers):
    med = {}
    for curve in ("minor", "major"):
        for axis in ("rang", "ruwe"):
            stack = [v for k, v in cond.items()
                     if k[0] == river and k[4] == axis and k[5] == curve]
            med[(curve, axis)] = np.median(np.array(stack), axis=0)
    us = np.median(np.array([v for k, v in uncond.items() if k[0] == river]), axis=0)
    ax.plot(Y, med[("minor", "rang")], color=GREEN, ls="--", lw=1.5, alpha=0.85)
    ax.plot(Y, med[("minor", "ruwe")], color=GREEN, ls="-", lw=2.0)
    ax.plot(Y, med[("major", "rang")], color=RED, ls="--", lw=1.5, alpha=0.85)
    ax.plot(Y, med[("major", "ruwe")], color=RED, ls="-", lw=2.0)
    ax.plot(Y, us, color=ORANGE, lw=2.0)
    ax.set_title(river, fontsize=11)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3)
for ax in axes[-1, :]:
    ax.set_xlabel("Future flood quantile", fontsize=10)
for ax in axes[:, 0]:
    ax.set_ylabel("Exceedance probability", fontsize=10)
fig.legend(handles=LEGEND, loc="upper center", ncol=5, fontsize=10.5,
           frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.savefig(f"{FIG}/axis_correction_overview.png", dpi=170, facecolor="white",
            bbox_inches="tight")
plt.close(fig)

n = len(os.listdir(PER))
print(f"\ngeschreven: {FIG}/axis_correction_overview.png en {n} bladen in {PER}/",
      flush=True)
