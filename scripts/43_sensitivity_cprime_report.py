"""Gevoeligheidsraster onder C': figuur en tabel voor de appendix (R4-01).

Besluit Floris 22 oktober 2026 (changelog, vijf presentatiebesluiten, punt 4):
in de appendix één heatmap van het raster onder de besloten nul C'. Het raster
komt uit scripts/37_sensitivity_grid_cprime.py: 5 SRI-drempels x 5
floodpercentielen, 48 locaties x 2 periodes, venster 4 weken, 10.000 simulaties
per cel.

Per rastercel en periode:
  ratio    gepoold over de 48 locaties: som van de waargenomen matches gedeeld
           door de som van de verwachte matches onder C' (de verwachting is het
           gemiddelde van de nulverdeling per locatie). Dit is een puntschatting;
           de nulverdelingen per locatie zijn niet bewaard, dus een gepoolde
           p-waarde zoals in scripts/10_sensitivity_report.py is hier niet
           beschikbaar
  n_sig    aantal locaties met p < 0,05 onder C', van het aantal toetsbare

Uitvoer in results/2026-10-27_sensitivity_cprime_report/:
  sensitivity_cprime.csv        per cel en periode: ratio, n_sig, n_testable
  sensitivity_cprime_heatmap.png / .pdf
  table_sensitivity_cprime.md   de tabel met Engels bijschrift
  caption_en.md
  README.md, manifest.yaml

Draaien vanuit de repo-root:
  uv run --frozen python scripts/43_sensitivity_cprime_report.py
"""
import os, hashlib, platform
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

GRID = "results/2026-10-21_sensitivity_grid_cprime/grid.csv"
# Extra kolom bij floodniveau 0,8413 (script 37 met FLOOD_QUANTILES=0.8413), nodig
# sinds de hoofdanalyse op 30 oktober 2026 naar SRI -1 met het gespiegelde
# floodniveau ging (besluit Floris). De omkaderde cel is nu (1,0, 0,8413).
GRID_EXTRA = "results/2026-10-30_sensitivity_grid_strict_column/grid.csv"
OUT = "results/2026-10-30_sensitivity_cprime_report"
ALPHA = 0.05
BASE = (1.0, 0.8413)
INK, INK2 = "#0b0b0b", "#52514e"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def fq(q):
    return f"{q:.4f}".rstrip("0") if abs(q - 0.6915) < 1e-6 or abs(q - 0.8413) < 1e-6 else f"{q:.2f}"


def main():
    os.makedirs(OUT, exist_ok=True)
    g = pd.concat([pd.read_csv(GRID), pd.read_csv(GRID_EXTRA)], ignore_index=True)
    assert len(g) == 2880 and not g.duplicated(["sri_threshold", "flood_quantile", "period", "river", "village"]).any()
    g["testable"] = g.selfcheck == "ok"
    rows = []
    for (st, q, per), grp in g.groupby(["sri_threshold", "flood_quantile", "period"]):
        ok = grp[grp.testable]
        rows.append({"sri_threshold": st, "flood_quantile": q, "period": per,
                     "n_testable": len(ok), "n_sig": int((ok.pCp < ALPHA).sum()),
                     "observed": int(ok.obs.sum()), "expected_cprime": float(ok.expCp.sum()),
                     "ratio": float(ok.obs.sum() / ok.expCp.sum()) if ok.expCp.sum() else np.nan,
                     "n_sig_nullA": int((ok.pA < ALPHA).sum())})
    t = pd.DataFrame(rows)
    t.to_csv(f"{OUT}/sensitivity_cprime.csv", index=False)
    THRS = sorted(t.sri_threshold.unique()); FQS = sorted(t.flood_quantile.unique())

    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK, "pdf.fonttype": 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), constrained_layout=True)
    M = {p: np.array([[t[(t.sri_threshold == s) & (t.flood_quantile == q) & (t.period == p)].ratio.iloc[0]
                       for s in THRS] for q in FQS]) for p in ("first", "second")}
    vmin, vmax = 0.6, 1.4
    for ax, p, titel in zip(axes, ("first", "second"), ("(a) Period 1, 1995–2009", "(b) Period 2, 2010–2024")):
        im = ax.imshow(M[p], cmap="RdBu_r", vmin=vmin, vmax=vmax, origin="lower", aspect="auto")
        for i, q in enumerate(FQS):
            for j, s in enumerate(THRS):
                r = t[(t.sri_threshold == s) & (t.flood_quantile == q) & (t.period == p)].iloc[0]
                kl = "white" if abs(r.ratio - 1) > 0.25 else INK
                ax.text(j, i + 0.12, f"{r.ratio:.2f}", ha="center", va="center", fontsize=7.5, color=kl)
                ax.text(j, i - 0.2, f"{r.n_sig}/{r.n_testable}", ha="center", va="center", fontsize=6, color=kl)
                if (s, round(q, 4)) == BASE:
                    ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, edgecolor=INK, lw=1.6))
        ax.set_xticks(range(len(THRS))); ax.set_xticklabels([f"{s:g}" for s in THRS])
        ax.set_yticks(range(len(FQS))); ax.set_yticklabels([fq(q) for q in FQS])
        ax.set_xlabel("Drought threshold (SRI < −x)")
        if p == "first":
            ax.set_ylabel("Flood threshold (discharge quantile)")
        ax.set_title(titel, loc="left", fontsize=8.5)
        for s_ in ("top", "right"):
            ax.spines[s_].set_visible(False)
    cb = fig.colorbar(im, ax=axes, shrink=0.9, pad=0.02)
    cb.set_label("Observed / expected coincidences, pooled over 48 locations", fontsize=7.5)
    cb.outline.set_linewidth(0.4)
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/sensitivity_cprime_heatmap.{ext}", dpi=300 if ext == "png" else None,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)

    caption = ("Figure F1: Sensitivity of the trigger coincidence test to the drought threshold (SRI, "
               "horizontal) and the flood threshold (discharge quantile, vertical), with a four-week "
               "window, in period 1 (a) and period 2 (b). Colour and the upper number: ratio of observed "
               "to expected drought-to-flood coincidences, pooled over the 48 locations, where the "
               "expectation is the mean of the Monte Carlo null distribution under the stratified null "
               "(Section 2.4.1, 10,000 simulations per location). Lower number: locations with p < 0.05 "
               "out of the locations where the test is defined. The framed cell is the configuration "
               "used in the main analysis (SRI < −1, quantile 0.841). The pooled ratio is a point "
               "estimate; no pooled significance test is reported.")
    open(f"{OUT}/caption_en.md", "w").write(caption + "\n")
    lines = [caption, "", "| Flood threshold | SRI threshold | Period 1: ratio | Period 1: p < 0.05 | Period 2: ratio | Period 2: p < 0.05 |",
             "|---|---|---|---|---|---|"]
    for q in reversed(FQS):
        for s in THRS:
            a = t[(t.sri_threshold == s) & (t.flood_quantile == q) & (t.period == "first")].iloc[0]
            b = t[(t.sri_threshold == s) & (t.flood_quantile == q) & (t.period == "second")].iloc[0]
            lines.append(f"| {fq(q)} | {s:g} | {a.ratio:.2f} | {a.n_sig}/{a.n_testable} | {b.ratio:.2f} | {b.n_sig}/{b.n_testable} |")
    open(f"{OUT}/table_sensitivity_cprime.md", "w").write("\n".join(lines).replace("Figure F1:", "Table F1:", 1) + "\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/43_sensitivity_cprime_report.py\npython: {platform.python_version()}\n"
                 f"inputs:\n  {GRID}: {sha256(GRID)}\n  {GRID_EXTRA}: {sha256(GRID_EXTRA)}\n")
    base = t[(t.sri_threshold == BASE[0]) & (np.isclose(t.flood_quantile, BASE[1], atol=1e-3))]
    print(base.to_string(index=False))
    print("cellen met n_sig >= 24 van 48 (C'):", int((t.n_sig >= 24).sum()), "van", len(t))


if __name__ == "__main__":
    main()
