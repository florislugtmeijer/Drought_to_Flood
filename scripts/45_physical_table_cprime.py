"""Tabel 4: de fysische resultaten per locatie, verwachting en toets onder C' (R1-08, T-17, O-03).

Besluit Floris 27 oktober 2026: per locatie, de twee periodes apart (Tabel 4a
periode 1, Tabel 4b periode 2). De eventgrootheden komen uit
results/2026-09-04_physical_table/per_location.csv (script 27, op de
gerepareerde definities, gecontroleerd tegen het raster); de verwachting en
de p-waarde komen uit de productierun onder C' (script 36). De oude
verwachtingskolom van script 27 (trefkans van een willekeurige week) wordt
niet meer gebruikt.

Kolommen per locatie:
  droughts        aantal droogtes
  duration        mediane duur in weken
  followed        aandeel droogtes gevolgd door een flood binnen vier weken
  expected        datzelfde aandeel verwacht onder C' (gemiddelde van de nulverdeling / aantal droogtes)
  ratio           waargenomen / verwacht
  p               Monte Carlo-p onder C', drie significante cijfers, vet onder 0,05
  lag             mediane vertraging in weken tussen droogte-einde en floodbegin
  season          seizoen waarin de meeste overgangen vallen, met het aandeel
  SRI < -1        percentage weken onder SRI -1 (15,9 bij een goed passende index)

Controle: aantallen droogtes en overgangen in beide bronnen gelijk.

Uitvoer in results/2026-10-28_physical_table_cprime/:
  table4.csv, table4a_period1.md, table4b_period2.md, caption_en.md,
  README.md, manifest.yaml

Draaien vanuit de repo-root:
  uv run --frozen python scripts/45_physical_table_cprime.py
"""
import os, hashlib, platform
import numpy as np, pandas as pd

# Hoofdanalyse sinds 30 oktober 2026 (besluit Floris): SRI -1, floodniveau 0,841.
# De versie bij -0,5 staat in results/2026-10-28_physical_table_cprime/ en wordt
# niet meer bijgewerkt. Bronnen via de omgeving voor varianten.
PHYS = os.environ.get("PHYS", "results/2026-10-30_physical_table_strict/per_location.csv")
PROD = os.environ.get("PROD", "results/2026-10-30_eca_cprime_strict/grid.csv")
OUT = os.environ.get("OUT", "results/2026-10-30_physical_table")
ALPHA = 0.05
THRESHOLD, FLOOD_Q = float(os.environ.get("THRESHOLD", 1.0)), float(os.environ.get("FLOOD_Q", 0.8413))
FQ_TXT = f"{FLOOD_Q:.4f}".rstrip("0")
PLACE = {"Turijn": "Turin", "Turon": "Toruń", "Warchau": "Warsaw", "Straatsburg": "Strasbourg",
         "Krementsjoek": "Kremenchuk", "Rostov - Dov": "Rostov-on-Don", "St. Maurillle": "Saint-Maurille",
         "Pora Wesfalica": "Porta Westfalica", "Krapowice": "Krapkowice", "Scinawa": "Ścinawa",
         "Kostrzyn nad Odra": "Kostrzyn nad Odrą", "Vila Velha de Rodao": "Vila Velha de Ródão",
         "Cermede / Castelmassa": "Castelmassa", "Montelimar": "Montélimar"}
RLOC = {"First location": "Upstream", "Second location": "Midstream", "Third location": "Downstream"}
REGULATED = {("Dnieper", "Krementsjoek"), ("Dnieper", "Dnipro"), ("Dnieper", "Cherson"),
             ("Tagus", "Vila Velha de Rodao")}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def fmt_p(p):
    s = "< 0.001" if p < 0.001 else f"{p:.3g}"
    return f"**{s}**" if p < ALPHA else s


def main():
    os.makedirs(OUT, exist_ok=True)
    ph = pd.read_csv(PHYS)
    pr = pd.read_csv(PROD)[["period", "river", "village", "n_dr", "obs", "expCp", "pCp"]]
    m = ph.merge(pr, on=["period", "river", "village"], validate="one_to_one")
    assert len(m) == 96, len(m)
    bad = m[(m.drought_count != m.n_dr) | (m.transitions != m.obs)]
    if len(bad):
        raise RuntimeError(f"events verschillen tussen script 27 en de productierun in {len(bad)} regels")
    m["expected_share_cprime"] = m.expCp / m.n_dr
    m["ratio_cprime"] = m.obs / m.expCp
    m["regulated"] = [(r, v) in REGULATED for r, v in zip(m.river, m.village)]
    m["ord"] = m.river_location.map({"First location": 0, "Second location": 1, "Third location": 2})
    m = m.sort_values(["period", "river", "ord"])
    keep = ["period", "river", "river_location", "village", "regulated", "drought_count",
            "drought_duration_median_wk", "transitions", "transition_share", "expected_share_cprime",
            "ratio_cprime", "pCp", "lag_median_wk", "transition_season_dominant",
            "transition_season_share", "pct_weeks_sri_below_minus1"]
    m[keep].to_csv(f"{OUT}/table4.csv", index=False)

    caption = (f"Table 4: Drought-to-flood transitions per location in period 1 (a, 1995–2009) and period 2 "
               f"(b, 2010–2024), at SRI < −{THRESHOLD:g} and the {FQ_TXT} discharge quantile. Droughts: number of drought "
               "events; duration: median duration in weeks; followed: share of droughts followed by a flood "
               "within four weeks; expected: the same share expected under the stratified null (Section 2.4.1); "
               "ratio: followed divided by expected; p: Monte Carlo p-value under the stratified null, bold "
               "where p < 0.05; lag: median number of weeks between the end of the drought and the start of "
               "the flood; season: season in which most transitions occur, with its share; SRI < −1: percentage "
               "of weeks below SRI −1, which is 15.9% for a well-fitted index. †: locations where the SRI "
               "detects very few droughts; the test is not informative there.")
    open(f"{OUT}/caption_en.md", "w").write(caption + "\n")
    head = ("| River | Location | Site | Droughts | Duration (wk) | Followed | Expected | Ratio | p | Lag (wk) | Season | SRI < −1 (%) |\n"
            "|---|---|---|---|---|---|---|---|---|---|---|---|")
    for per, name in (("first", "table4a_period1"), ("second", "table4b_period2")):
        lines = [caption.replace("Table 4:", f"Table 4{'a' if per == 'first' else 'b'}:", 1), "", head]
        for _, r in m[m.period == per].iterrows():
            dag = "†" if r.regulated else ""
            season = f"{r.transition_season_dominant} ({r.transition_season_share:.2f})" if isinstance(r.transition_season_dominant, str) else "–"
            lag = f"{r.lag_median_wk:.0f}" if pd.notna(r.lag_median_wk) else "–"
            lines.append("| " + " | ".join([
                r.river, RLOC[r.river_location], PLACE.get(r.village, r.village) + dag,
                f"{int(r.drought_count)}", f"{r.drought_duration_median_wk:.0f}",
                f"{r.transition_share:.2f}", f"{r.expected_share_cprime:.2f}", f"{r.ratio_cprime:.2f}",
                fmt_p(r.pCp), lag, season, f"{r.pct_weeks_sri_below_minus1:.1f}"]) + " |")
        open(f"{OUT}/{name}.md", "w").write("\n".join(lines) + "\n")

    S = []
    for per in ("first", "second"):
        x = m[(m.period == per) & ~m.regulated]
        S.append(f"- {per}, 44 vrij afstromende locaties: followed mediaan {x.transition_share.median():.2f} "
                 f"(bereik {x.transition_share.min():.2f} tot {x.transition_share.max():.2f}), expected mediaan "
                 f"{x.expected_share_cprime.median():.2f}, ratio mediaan {x.ratio_cprime.median():.2f} "
                 f"(bereik {x.ratio_cprime.min():.2f} tot {x.ratio_cprime.max():.2f}), lag mediaan "
                 f"{x.lag_median_wk.median():.0f}, duur mediaan {x.drought_duration_median_wk.median():.0f}")
        seas = m[m.period == per].transition_season_dominant.value_counts().to_dict()
        S.append(f"  seizoen met de meeste overgangen, aantal locaties: {seas}")
    reg = m[m.regulated][["period", "village", "drought_count", "transitions", "ratio_cprime", "pCp", "pct_weeks_sri_below_minus1"]]
    S.append("- gemarkeerde locaties:\n" + reg.to_string(index=False))
    open(f"{OUT}/README.md", "w").write("# Tabel 4 onder C', samenvatting\n\nScript: scripts/45_physical_table_cprime.py\n\n" + "\n".join(S) + "\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/45_physical_table_cprime.py\npython: {platform.python_version()}\n"
                 f"inputs:\n  {PHYS}: {sha256(PHYS)}\n  {PROD}: {sha256(PROD)}\n")
    print("\n".join(S))


if __name__ == "__main__":
    main()
