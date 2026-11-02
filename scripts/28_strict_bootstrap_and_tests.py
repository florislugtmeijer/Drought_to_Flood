"""Strikte definities: bootstrap en onafhankelijkheidstoetsen bij droogtedrempel 1.

Gevoeligheidsvariant, zie scripts/27_strict_definition_points.py voor de
achtergrond. Dit script draait exact dezelfde bootstrap en dezelfde vier toetsen als
de gerapporteerde analyse, alleen met THRESHOLD 1,0 in plaats van 0,5, en met het
afleesniveau 0,8413 erbij.

Er wordt geen bestaande code aangepast. De functies do_cell uit
scripts/22_bootstrap_transition_ci.py en scripts/25_dependence_tests.py worden
geimporteerd en gedraaid met de drempelconstante overschreven. Zo blijft er een
definitie van elke functie en is de variant per constructie identiek aan de
hoofdanalyse op die ene parameter na. De pool gebruikt fork, zodat de kinderen de
overschreven constanten erven; met spawn zouden ze de module opnieuw laden en op
0,5 terugvallen.

Uitvoer, strikt gescheiden van de hoofdanalyse:
  results/2026-09-04_strict_dependence_tests/
  results/2026-09-04_strict_copula_bootstrap/

Draaien vanuit de repo-root, met threads vastgezet:
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run --python 3.12 --with numpy \
      --with pandas --with xarray --with scipy --with netCDF4 --with vinecopulas \
      --no-project python scripts/28_strict_bootstrap_and_tests.py
"""
import sys, os, json, re, ast, csv, time, importlib.util, multiprocessing as mp
sys.path.insert(0, "src")
import numpy as np

STRICT_THRESHOLD = 1.0
OUT_T = "results/2026-09-04_strict_dependence_tests"
OUT_B = "results/2026-09-04_strict_copula_bootstrap"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"


def laad(pad, naam):
    spec = importlib.util.spec_from_file_location(naam, pad)
    m = importlib.util.module_from_spec(spec)
    sys.modules[naam] = m
    spec.loader.exec_module(m)
    return m


def main():
    bs = laad("scripts/22_bootstrap_transition_ci.py", "bs22")
    dp = laad("scripts/25_dependence_tests.py", "dp25")
    # de enige inhoudelijke afwijking van de hoofdanalyse
    bs.THRESHOLD = STRICT_THRESHOLD
    dp.THRESHOLD = STRICT_THRESHOLD
    dp.QI = {"q6915": 69, "q8413": 84, "q90": 90, "q95": 95}
    os.makedirs(OUT_T, exist_ok=True); os.makedirs(OUT_B, exist_ok=True)

    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
            for r in rivers for l in r["locations"]]
    ctx = mp.get_context("fork")

    # ---------------------------------------------------------- toetsen
    seeds = np.random.SeedSequence(dp.SEED).spawn(len(locs) * len(dp.PERIODS))
    jobs = []
    for pi, (pname, (b, e)) in enumerate(dp.PERIODS.items()):
        for li, (river, village, rloc, lat, lon) in enumerate(locs):
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            jobs.append((river, village, rloc, pname, b, e, lat, lon, st))
    f = open(f"{OUT_T}/dependence_tests.csv", "w", newline=""); w = csv.writer(f)
    w.writerow(["river", "village", "river_location", "period", "pair", "n_events",
                "k_minor", "k_major", "dist1", "dist2", "copula_name", "aic",
                "tau", "tau_p", "rho", "rho_p", "hoeffd", "hoeffd_p", "aic_perm_p"]
               + [x for k in dp.QI for x in (f"cp_{k}", f"cp_{k}_p")]
               + ["cp_maxabs", "cp_maxabs_p"])
    t0 = time.time(); done = 0
    with ctx.Pool(dp.WORKERS) as pool:
        for rows in pool.imap_unordered(dp.do_cell, jobs):
            for r in rows: w.writerow(r)
            f.flush(); done += 1
            print(f"toetsen [{done}/{len(jobs)}] {(time.time()-t0)/60:5.1f} min", flush=True)
    f.close()
    print(f"toetsen klaar in {(time.time()-t0)/60:.1f} min", flush=True)

    # ---------------------------------------------------------- bootstrap
    seeds = np.random.SeedSequence(bs.SEED).spawn(len(locs) * len(bs.PERIODS))
    jobs = []
    for pi, (pname, (b, e)) in enumerate(bs.PERIODS.items()):
        for li, (river, village, rloc, lat, lon) in enumerate(locs):
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            jobs.append((li, pi, river, village, rloc, lat, lon, pname, b, e, st))
    ycols = [f"y_{i:03d}" for i in range(len(bs.Y))]
    fci = open(f"{OUT_B}/transition_ci.csv", "w", newline=""); wci = csv.writer(fci)
    wci.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                  "quantity", "kind", "n_events"] + ycols)
    fdg = open(f"{OUT_B}/bootstrap_diagnostics.csv", "w", newline=""); wdg = csv.writer(fdg)
    wdg.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                  "n_events", "k_minor", "k_major", "copula_point", "copula_modal",
                  "modal_share", "n_families_seen", "failed_replicates", "median_bias",
                  "median_width_minor", "median_width_diff", "supt_over_196",
                  "fixed_family_failures", "fixed_family_computed",
                  "lag1_spearman_drought", "lag1_spearman_flood", "block_length"])
    fsel = open(f"{OUT_B}/selection_frequency.csv", "w", newline=""); wsel = csv.writer(fsel)
    wsel.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                   "copula_name", "count", "share"])
    t0 = time.time(); done = 0
    with ctx.Pool(bs.WORKERS) as pool:
        for rows_ci, rows_diag, rows_sel in pool.imap_unordered(bs.do_cell, jobs):
            for r in rows_ci: wci.writerow(r)
            for r in rows_diag: wdg.writerow(r)
            for r in rows_sel: wsel.writerow(r)
            fci.flush(); fdg.flush(); fsel.flush(); done += 1
            print(f"bootstrap [{done}/{len(jobs)}] {(time.time()-t0)/60:5.1f} min", flush=True)
    fci.close(); fdg.close(); fsel.close()
    print(f"bootstrap klaar in {(time.time()-t0)/60:.1f} min", flush=True)
    print("klaar", flush=True)


if __name__ == "__main__":
    main()
