"""Appendix E: de copulatabel per locatie, periode en droogtevariabele.

Antwoord op R4-03 (welke copula per cel, en intervallen bij de transitiekansen),
in de vorm van D-16: de gekozen familie, het AIC-verschil met de nummer twee en
het maximale verschil tussen hun curves, plus de transitiekansen met 95%-interval
bij het floodniveau 0,6915.

Leest:
  results/2026-10-22_copula_family_and_flood_level/cells.csv   script 40
  <BOOT>/transition_ci.csv, <BOOT>/bootstrap_diagnostics.csv   script 22, iid
  results/2026-09-02_dependence_tests/dependence_tests.csv       script 25

BOOT en COL via de omgeving. Standaard de bootstrap met 0,6915 in het rooster
(results/2026-10-22_copula_bootstrap_6915, kolom y_q6915).

Uitvoer in results/2026-10-22_appendix_e_copula_table/:
  appendix_e_copula_table.csv   alle velden, onafgerond
  appendix_e_copula_table.md    de tabel zoals hij in de appendix komt
  README.md, manifest.yaml

Draaien vanuit de repo-root:
  uv run --frozen python scripts/42_appendix_e_copula_table.py
"""
import os, hashlib, platform
import numpy as np, pandas as pd

CELLS = "results/2026-10-22_copula_family_and_flood_level/cells.csv"
BOOT = os.environ.get("BOOT", "results/2026-10-22_copula_bootstrap_6915")
COL = os.environ.get("COL", "y_q6915")
TESTS = "results/2026-09-02_dependence_tests/dependence_tests.csv"
OUT = os.environ.get("OUT", "results/2026-10-22_appendix_e_copula_table")
KEY = ["river", "village", "period", "pair"]
TOETSEN = ["tau_p", "hoeffd_p", "aic_perm_p", "cp_q6915_p"]
PLACE = {"Turijn": "Turin", "Turon": "Toruń", "Warchau": "Warsaw", "Straatsburg": "Strasbourg",
         "Krementsjoek": "Kremenchuk"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    cells = pd.read_csv(CELLS)
    ci = pd.read_csv(f"{BOOT}/transition_ci.csv")
    ci = ci[ci.scheme == "iid"]
    diag = pd.read_csv(f"{BOOT}/bootstrap_diagnostics.csv")
    diag = diag[diag.scheme == "iid"][KEY + ["modal_share"]]
    tests = pd.read_csv(TESTS)
    tests["n_tests"] = (tests[TOETSEN] < 0.05).sum(axis=1)
    tests = tests[KEY + ["n_tests", "tau"]]

    wide = ci.pivot_table(index=KEY, columns=["quantity", "kind"], values=COL, aggfunc="first")
    wide.columns = [f"{q}_{k}" for q, k in wide.columns]
    wide = wide.reset_index()
    t = cells.merge(wide, on=KEY, how="left").merge(diag, on=KEY, how="left").merge(tests, on=KEY, how="left")

    # puntschatting uit de bootstrap moet gelijk zijn aan script 40
    dev = max(np.nanmax(np.abs(t["minor_resel_point"] - t["minor_at_q"])),
              np.nanmax(np.abs(t["major_resel_point"] - t["major_at_q"])))
    t.to_csv(f"{OUT}/appendix_e_copula_table.csv", index=False)

    def f2(v): return "" if pd.isna(v) else f"{v:.2f}"
    def ci_s(p, lo, hi): return "" if pd.isna(p) else f"{p:.2f} [{lo:.2f}, {hi:.2f}]"
    order = {"first": 1, "second": 2}
    t = t.sort_values(["river", "river_location", "village", "pair", "period"],
                      key=lambda s: s.map(order) if s.name == "period" else s)
    lines = ["| River | Location | Period | Drought variable | Droughts | Major | Copula | ΔAIC to second (family) | Max. curve difference, minor / major | Selected in bootstrap | P, minor drought | P, major drought | Dependence part | Tests | Kendall's τ |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in t.iterrows():
        lines.append("| " + " | ".join([
            r.river, PLACE.get(r.village, r.village), "1" if r.period == "first" else "2",
            "drought peak" if r.pair == "drought_peak" else "mean severity",
            str(int(r.n_events)), str(int(r.k_major)), r.family,
            f"{r.delta_aic:.2f} ({r.runner_up})",
            f"{r.max_abs_diff_minor:.2f} / {r.max_abs_diff_major:.2f}",
            f"{100 * r.modal_share:.0f}%" if not pd.isna(r.modal_share) else "",
            ci_s(r.minor_resel_point, r.minor_resel_lo, r.minor_resel_hi),
            ci_s(r.major_resel_point, r.major_resel_lo, r.major_resel_hi),
            ci_s(r.copula_part_point, r.copula_part_lo, r.copula_part_hi),
            f"{int(r.n_tests)}/4" if not pd.isna(r.n_tests) else "",
            f2(r.tau)]) + " |")
    caption = ("Table E1: Copula selection and transition probabilities at the flood threshold "
               "(q = 0.6915) for each location, period and drought variable. Droughts: number of "
               "drought events; Major: events above the major-drought threshold. ΔAIC: AIC difference "
               "between the selected and the second-best copula family; maximum curve difference: the "
               "largest absolute difference between the transition curves of these two families, for "
               "the minor- and the major-drought curve. Selected in bootstrap: share of 2000 bootstrap "
               "resamples in which the most frequent family was selected. P: transition probability "
               "with 95% bootstrap interval. Dependence part: conditional probability after a minor "
               "drought minus 1 − F_Y, with 95% interval. Tests: number of the four dependence tests "
               "significant at the 5% level (Section 2.4.2).")
    open(f"{OUT}/appendix_e_copula_table.md", "w").write(caption + "\n\n" + "\n".join(lines) + "\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/42_appendix_e_copula_table.py\npython: {platform.python_version()}\n"
                 f"column: {COL}\ninputs:\n")
        for pth in (CELLS, f"{BOOT}/transition_ci.csv", f"{BOOT}/bootstrap_diagnostics.csv", TESTS):
            fh.write(f"  {pth}: {sha256(pth)}\n")
        fh.write(f"check_point_vs_script40: {dev:.1e}\n")
    print(f"{len(t)} regels, puntschatting bootstrap vs script 40: {dev:.1e}")


if __name__ == "__main__":
    main()
