"""Tabel 3: ECA p-waardes per locatie en periode, Poisson en Monte Carlo onder C'.

Besluit Floris 27 oktober 2026 (CHANGELOG-methodology.md, 2026-10-27): Tabel 3
houdt per periode twee kolommen, de analytische p onder de Poisson-aanname en de
Monte Carlo-p, nu onder nul C' (10.000 simulaties, script 36). p-waardes op drie
significante cijfers (R4-06, besluit 5 september), onder 0,001 als "< 0.001".

Leest:
  results/2026-09-02_sensitivity_grid_endfix/grid_results.csv   analytische p
      (p_trigger) uit de baseline-cel: drempel 0,5, floodniveau norm.cdf(0,5),
      venster 4; gerepareerde einddetectie
  results/2026-10-21_eca_null_production/production.csv         Monte Carlo-p
      onder C' (pCp) en, ter controle, onder A (pA)

Controleert dat de events in beide bronnen gelijk zijn (droogtes en matches).

Uitvoer in results/2026-10-27_table3_eca_cprime/:
  table3.csv            alle velden, onafgerond
  table3.md             de tabel voor het manuscript met Engels bijschrift
  figure4_categories.csv per locatie: significant onder C' in periode 1, 2,
                        beide of geen (voor Figuur 4)
  summary.md            tellingen, per rivier, en de cellen waar Poisson en C'
                        uiteenlopen
  README.md, manifest.yaml

Draaien vanuit de repo-root:
  uv run --frozen python scripts/39_table3_eca.py
"""
import os, hashlib, platform
import numpy as np, pandas as pd

# Bronnen en drempels via de omgeving; defaults zijn de analyse van 27 oktober
# (SRI -0,5, floodniveau 0,6915). Besluit Floris 30 oktober 2026: de
# hoofdanalyse gaat naar SRI -1 met het gespiegelde floodniveau 0,841; daarvoor:
#   GRID=results/2026-10-30_eca_poisson_strict/grid_results.csv \
#   PROD=results/2026-10-30_eca_cprime_strict/grid.csv \
#   OUT=results/2026-10-30_table3_eca_strict THRESHOLD=1.0 FLOOD_Q=0.8413
GRID = os.environ.get("GRID", "results/2026-09-02_sensitivity_grid_endfix/grid_results.csv")
PROD = os.environ.get("PROD", "results/2026-10-21_eca_null_production/production.csv")
OUT = os.environ.get("OUT", "results/2026-10-27_table3_eca_cprime")
THRESHOLD, FLOOD_Q = float(os.environ.get("THRESHOLD", 0.5)), float(os.environ.get("FLOOD_Q", 0.6915))
WINDOW, ALPHA = 4, 0.05
FQ_TXT = f"{FLOOD_Q:.4f}".rstrip("0")
PLACE = {"Turijn": "Turin", "Turon": "Toruń", "Warchau": "Warsaw", "Straatsburg": "Strasbourg",
         "Krementsjoek": "Kremenchuk", "Rostov - Dov": "Rostov-on-Don", "St. Maurillle": "Saint-Maurille",
         "Pora Wesfalica": "Porta Westfalica", "Krapowice": "Krapkowice", "Scinawa": "Ścinawa",
         "Kostrzyn nad Odra": "Kostrzyn nad Odrą", "Vila Velha de Rodao": "Vila Velha de Ródão",
         "Cermede / Castelmassa": "Castelmassa", "Montelimar": "Montélimar"}
RLOC = {"First location": "Upstream", "Second location": "Midstream", "Third location": "Downstream"}
REGULATED = {("Dnieper", "Krementsjoek"), ("Dnieper", "Dnipro"), ("Dnieper", "Cherson"),
             ("Tagus", "Vila Velha de Rodao")}   # D-12: gemarkeerd als niet informatief


def fmt_p(p):
    if pd.isna(p):
        return "n/a"
    if p < 0.001:
        return "< 0.001"
    return f"{p:.3g}"


def cell(p, mark):
    s = fmt_p(p)
    if not pd.isna(p) and p < ALPHA:
        s = f"**{s}**"
    return s + ("†" if mark else "")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    g = pd.read_csv(GRID)
    b = g[(g.threshold == THRESHOLD) & np.isclose(g.flood_quantile, FLOOD_Q, atol=1e-3)
          & (g.match_window == WINDOW)]
    p = pd.read_csv(PROD)
    m = b.merge(p, on=["period", "river", "village"], validate="one_to_one")
    assert len(m) == 96, len(m)
    bad = m[(m.drought_count != m.n_dr) | (m.match_count_trigger != m.obs)]
    if len(bad):
        raise RuntimeError(f"events verschillen tussen raster en productierun in {len(bad)} cellen")
    m["regulated"] = [(r, v) in REGULATED for r, v in zip(m.river, m.village)]
    m = m.rename(columns={"p_trigger": "p_poisson", "pCp": "p_mc_cprime", "pA": "p_mc_nullA",
                          "n_dr": "droughts", "obs": "matches", "expCp": "expected_cprime",
                          "expA": "expected_nullA"})
    keep = ["river", "river_location", "village", "period", "droughts", "flood_count", "matches",
            "expected_nullA", "expected_cprime", "p_poisson", "p_mc_nullA", "p_mc_cprime", "regulated"]
    m[keep].to_csv(f"{OUT}/table3.csv", index=False)

    rivers = list(dict.fromkeys(b.sort_values(["river"]).river))
    w = m.pivot_table(index=["river", "river_location", "village", "regulated"], columns="period",
                      values=["p_poisson", "p_mc_cprime"], aggfunc="first").reset_index()
    w.columns = ["_".join(c).rstrip("_") if isinstance(c, tuple) else c for c in w.columns]
    w["ord"] = w.river_location.map({"First location": 0, "Second location": 1, "Third location": 2})
    w = w.sort_values(["river", "ord"])
    lines = ["| River | Location | Site | Poisson p, period 1 | Monte Carlo p, period 1 | Poisson p, period 2 | Monte Carlo p, period 2 |",
             "|---|---|---|---|---|---|---|"]
    for _, r in w.iterrows():
        lines.append("| " + " | ".join([
            r.river, RLOC[r.river_location], PLACE.get(r.village, r.village),
            cell(r.p_poisson_first, r.regulated), cell(r.p_mc_cprime_first, r.regulated),
            cell(r.p_poisson_second, r.regulated), cell(r.p_mc_cprime_second, r.regulated)]) + " |")
    caption = (f"Table 3: p-values of the trigger coincidence test (droughts followed by a flood within four "
               f"weeks) per location and period, at SRI < −{THRESHOLD:g} and the {FQ_TXT} discharge quantile. Poisson: "
               "analytical test under the assumption that flood onsets follow a Poisson process over all "
               "weeks. Monte Carlo: permutation test with 10,000 simulations under a null that places flood "
               "onsets only on weeks where an onset can occur (Section 2.4.1). Bold: p < 0.05. "
               "†: locations where the SRI detects very few droughts (Section 3.1); the test is not "
               "informative there. Values below 0.001 are shown as < 0.001.")
    open(f"{OUT}/table3.md", "w").write(caption + "\n\n" + "\n".join(lines) + "\n")

    # Figuur 4: categorie per locatie onder C'
    cat = []
    for _, r in w.iterrows():
        s1, s2 = r.p_mc_cprime_first < ALPHA, r.p_mc_cprime_second < ALPHA
        cat.append({"river": r.river, "village": r.village, "sig_period1": bool(s1), "sig_period2": bool(s2),
                    "category": "both" if s1 and s2 else "first only" if s1 else "second only" if s2 else "none",
                    "regulated": bool(r.regulated)})
    pd.DataFrame(cat).to_csv(f"{OUT}/figure4_categories.csv", index=False)

    # samenvatting
    S = []
    for per in ("first", "second"):
        x = m[m.period == per]
        S.append(f"- {per}: Poisson p < 0.05 in {int((x.p_poisson < ALPHA).sum())} van 48, Monte Carlo onder A "
                 f"{int((x.p_mc_nullA < ALPHA).sum())}, onder C′ {int((x.p_mc_cprime < ALPHA).sum())}")
    S.append(f"- gepoolde ratio waargenomen/verwacht: C′ {m.matches.sum() / m.expected_cprime.sum():.3f}, "
             f"A {m.matches.sum() / m.expected_nullA.sum():.3f}")
    S.append("- cellen Poisson significant maar C′ niet:")
    for _, r in m[(m.p_poisson < ALPHA) & (m.p_mc_cprime >= ALPHA)].iterrows():
        S.append(f"  - {r.river} {PLACE.get(r.village, r.village)} {r.period}: Poisson {fmt_p(r.p_poisson)}, "
                 f"C′ {fmt_p(r.p_mc_cprime)}, waargenomen {r.matches}, verwacht A {r.expected_nullA:.1f}, "
                 f"C′ {r.expected_cprime:.1f}")
    S.append(f"- cellen C′ significant maar Poisson niet: {int(((m.p_poisson >= ALPHA) & (m.p_mc_cprime < ALPHA)).sum())}")
    S.append("- per rivier, locaties significant onder C′ (periode 1, periode 2) van 3:")
    for r, grp in m.groupby("river"):
        c1 = int(((grp.period == "first") & (grp.p_mc_cprime < ALPHA)).sum())
        c2 = int(((grp.period == "second") & (grp.p_mc_cprime < ALPHA)).sum())
        S.append(f"  - {r}: {c1}, {c2}")
    cats = pd.DataFrame(cat).category.value_counts().to_dict()
    S.append(f"- Figuur 4-categorieën onder C′: {cats}")
    open(f"{OUT}/summary.md", "w").write("# Tabel 3 onder C′, samenvatting\n\n" + "\n".join(S) + "\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/39_table3_eca.py\npython: {platform.python_version()}\n"
                 f"baseline: threshold {THRESHOLD}, flood_quantile {FLOOD_Q}, window {WINDOW}\n"
                 f"inputs:\n  {GRID}: {sha256(GRID)}\n  {PROD}: {sha256(PROD)}\n")
    print("\n".join(S))


if __name__ == "__main__":
    main()
