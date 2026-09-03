"""T-11: figuren bij de betrouwbaarheidsintervallen (R4-03).

Rekent niets opnieuw, leest results/2026-09-02_copula_bootstrap/transition_ci.csv.

Drie figuren:
  ci_example.png        een cel groot, met de banden om de milde en de zware curve
                        en de verschilcurve eronder
  ci_decomposition.png  het gat opgesplitst in een marginaal deel en een copula
                        deel, met banden, over alle cellen samengevat
  ci_per_river.png      per rivier de verschilcurve met band, 16 panelen

Geen beschrijving in de figuren zelf. Labels in het Engels.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with matplotlib --no-project \
      python scripts/24_bootstrap_figures.py
"""
import csv, os, collections
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

BS = "results/2026-09-02_copula_bootstrap"
FIG = f"{BS}/figures"
os.makedirs(FIG, exist_ok=True)
Y = np.linspace(0, 1, 101)
YC = [f"y_{i:03d}" for i in range(101)]
GREEN, RED, BLUE, GREY = "#2a7f3f", "#c0392b", "#2c6fbb", "#7a7a7a"

ci = {}
for r in csv.DictReader(open(f"{BS}/transition_ci.csv")):
    if r["scheme"] != "iid":
        continue
    ci[(r["river"], r["village"], r["period"], r["pair"], r["quantity"], r["kind"])] = \
        np.array([float(r[c]) for c in YC])
cellen = sorted({k[:4] for k in ci})
rivers = []
for c in cellen:
    if c[0] not in rivers:
        rivers.append(c[0])
print(f"cellen: {len(cellen)}, rivieren: {len(rivers)}", flush=True)


def band(ax, cel, hoeveelheid, colour, label):
    p = ci.get(cel + (hoeveelheid, "point"))
    lo = ci.get(cel + (hoeveelheid, "lo"))
    hi = ci.get(cel + (hoeveelheid, "hi"))
    if p is None:
        return False
    ax.plot(Y, p, color=colour, lw=2, label=label)
    ax.fill_between(Y, lo, hi, color=colour, alpha=0.22)
    return True


# ------------------------------------------------------------------ figuur 1
voorbeeld = ("Ebro", "Haro", "second", "mean_drought_severity")
if voorbeeld not in cellen:
    voorbeeld = cellen[0]
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)
ax = axes[0]
band(ax, voorbeeld, "minor_resel", GREEN, "Conditional | minor drought")
band(ax, voorbeeld, "major_resel", RED, "Conditional | severe drought")
ax.set_xlabel("Future flood quantile"); ax.set_ylabel("Exceedance probability")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02); ax.grid(alpha=0.3); ax.legend(fontsize=9)
ax.set_title("Transition probabilities with 95% intervals", fontsize=11)
ax = axes[1]
band(ax, voorbeeld, "diff_resel", BLUE, "Severe minus minor drought")
ax.axhline(0, color="black", lw=1)
ax.set_xlabel("Future flood quantile"); ax.set_ylabel("Difference in probability")
ax.set_xlim(0, 1); ax.grid(alpha=0.3); ax.legend(fontsize=9)
ax.set_title("The difference, bootstrapped directly", fontsize=11)
fig.savefig(f"{FIG}/ci_example.png", dpi=200, facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------ figuur 2
fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), constrained_layout=True)
for ax, (h, titel, colour) in zip(axes, [
        ("marginal_part", "Marginal component: is the post-drought window wetter", GREY),
        ("copula_part", "Copula component: does drought severity matter", BLUE)]):
    stack_p = np.array([ci[c + (h, "point")] for c in cellen if c + (h, "point") in ci])
    stack_lo = np.array([ci[c + (h, "lo")] for c in cellen if c + (h, "lo") in ci])
    stack_hi = np.array([ci[c + (h, "hi")] for c in cellen if c + (h, "hi") in ci])
    ax.plot(Y, np.nanmedian(stack_p, axis=0), color=colour, lw=2, label="Median point estimate")
    ax.fill_between(Y, np.nanmedian(stack_lo, axis=0), np.nanmedian(stack_hi, axis=0),
                    color=colour, alpha=0.22, label="Median 95% interval")
    ax.fill_between(Y, np.nanpercentile(stack_p, 25, axis=0),
                    np.nanpercentile(stack_p, 75, axis=0), color=colour, alpha=0.12,
                    label="Interquartile range across cells")
    ax.axhline(0, color="black", lw=1)
    ax.set_title(titel, fontsize=11)
    ax.set_xlabel("Future flood quantile"); ax.set_ylabel("Contribution to the gap")
    ax.set_xlim(0, 1); ax.grid(alpha=0.3); ax.legend(fontsize=8.5, loc="upper right")
fig.savefig(f"{FIG}/ci_decomposition.png", dpi=200, facecolor="white")
plt.close(fig)

# ------------------------------------------------------------------ figuur 3
fig, axes = plt.subplots(4, 4, figsize=(16, 13), sharex=True, sharey=True,
                         constrained_layout=True)
for ax, riv in zip(axes.ravel(), rivers):
    sub = [c for c in cellen if c[0] == riv]
    P = np.array([ci[c + ("diff_resel", "point")] for c in sub if c + ("diff_resel", "point") in ci])
    LO = np.array([ci[c + ("diff_resel", "lo")] for c in sub if c + ("diff_resel", "lo") in ci])
    HI = np.array([ci[c + ("diff_resel", "hi")] for c in sub if c + ("diff_resel", "hi") in ci])
    if len(P):
        ax.plot(Y, np.nanmedian(P, axis=0), color=BLUE, lw=2)
        ax.fill_between(Y, np.nanmedian(LO, axis=0), np.nanmedian(HI, axis=0),
                        color=BLUE, alpha=0.22)
    ax.axhline(0, color="black", lw=1)
    ax.set_title(riv, fontsize=11); ax.set_xlim(0, 1); ax.grid(alpha=0.3)
for ax in axes[-1, :]:
    ax.set_xlabel("Future flood quantile", fontsize=10)
for ax in axes[:, 0]:
    ax.set_ylabel("Severe minus minor drought", fontsize=10)
fig.savefig(f"{FIG}/ci_per_river.png", dpi=170, facecolor="white")
plt.close(fig)
# ------------------------------------------------------------------ figuur 4
# sterkte en richting van de samenhang per cel: tau tegen de permutatie-p van de
# copulafit, met de consensuscellen benoemd
import csv as _csv
dep = list(_csv.DictReader(open("results/2026-09-02_dependence_tests/dependence_tests.csv")))
KOLS = ("tau_p", "hoeffd_p", "aic_perm_p", "cp_q6915_p")
fig, ax = plt.subplots(figsize=(9.5, 7), constrained_layout=True)
for r in dep:
    tau, p = float(r["tau"]), float(r["aic_perm_p"])
    ns = sum(1 for k in KOLS if float(r[k]) < 0.05)
    kleur = RED if (ns >= 3 and tau < 0) else (GREEN if ns >= 3 else GREY)
    ax.scatter(tau, -np.log10(max(p, 1e-4)), s=46 if ns >= 3 else 16,
               color=kleur, alpha=0.9 if ns >= 3 else 0.45, zorder=3 if ns >= 3 else 2)
    if ns >= 3:
        per = "P1" if r["period"] == "first" else "P2"
        ax.annotate(f'{r["river"]} {r["village"][:12]} {per}',
                    (tau, -np.log10(max(p, 1e-4))), fontsize=7.5,
                    xytext=(5, 3), textcoords="offset points")
ax.axhline(-np.log10(0.05), color="black", lw=1, ls="--")
ax.text(0.31, -np.log10(0.05) + 0.03, "p = 0.05", fontsize=8.5)
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("Kendall's tau between drought severity and subsequent peak")
ax.set_ylabel("$-\log_{10}$ p, permutation test on the copula fit")
ax.set_title("Strength and direction of severity dependence, all 190 cells\n"
             "large points: at least 3 of 4 tests below 0.05", fontsize=11)
ax.grid(alpha=0.3)
fig.savefig(f"{FIG}/dependence_overview.png", dpi=200, facecolor="white")
plt.close(fig)
print(f"geschreven: vier figuren in {FIG}/", flush=True)
