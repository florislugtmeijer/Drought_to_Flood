"""Copulakeuze per cel met de nummer twee, en de transitiekansen bij floodniveau 0,6915.

Twee doelen, één run:

  D-16  per locatie, periode en variabelenpaar: de gekozen familie, de nummer twee
        op AIC, het AIC-verschil, en het maximale verschil tussen de transitiecurves
        van die twee. Laat zien of een instabiele familiekeuze de transitiekans
        raakt. Landt in Appendix E.

  N-1   de puntschattingen bij precies 0,6915, het floodniveau van het manuscript.
        De bootstrap van script 22 rekent op een rooster van 0,01; hier wordt
        0,6915 aan dat rooster toegevoegd.

De puntschatting is die van script 22, regel voor regel: dezelfde invoer, dezelfde
seed per locatie-periode (SeedSequence(42).spawn(96)), 100.000 trekkingen,
parametrische marginalen, aflezing op de quantielas. Op de roosterpunten moet de
uitkomst daarom exact gelijk zijn aan de puntrijen in
results/2026-09-02_copula_bootstrap/transition_ci.csv; dat wordt gecontroleerd en
weggeschreven in check.txt.

De nummer twee is de familie met de op één na laagste AIC, berekend met dezelfde
functies als bestcop (fit en neg_likelihood uit vinecopulas). Zijn curves worden
met dezelfde seed en hetzelfde aantal trekkingen bepaald.

Uitvoer in results/2026-10-22_copula_family_and_flood_level/:
  cells.csv     een regel per cel
  check.txt     de vergelijking met de bootstrap
  README.md, manifest.yaml

Draaien vanuit de repo-root:
  uv run --frozen python scripts/40_copula_family_and_flood_level.py
"""
import sys, os, json, re, ast, csv, time, hashlib, platform, warnings, multiprocessing as mp
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula, flood_peak_after_drought, mean_severity_per_week, COPS
from vinecopulas.bivariate import fit as cop_fit, neg_likelihood, copulas

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
BOOT = "results/2026-09-02_copula_bootstrap/transition_ci.csv"
OUT = "results/2026-10-22_copula_family_and_flood_level"
THRESHOLD, DT, SEED = 0.5, 4, 42
N_POINT = 100000
Q_TEXT = 0.6915
GRID = np.linspace(0, 1, 101)
Y = np.sort(np.append(GRID, Q_TEXT))
I_TEXT = int(np.where(Y == Q_TEXT)[0][0])
ON_GRID = np.array([i for i in range(len(Y)) if i != I_TEXT])
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
WORKERS = max(1, mp.cpu_count() - 2)


def aic_table(u):
    """AIC per familie, zoals bestcop hem berekent."""
    out = {}
    for c in COPS:
        try:
            par = cop_fit(c, u.copy())
            k = 2 if c == 15 else 1
            out[c] = 2 * k + 2 * neg_likelihood(par, c, u.copy())
        except Exception:
            out[c] = np.nan
    return out


def do_cell(job):
    (li, pi, river, village, rloc, lat, lon, pname, b, e, seed_state) = job
    rows, curves = [], []
    data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    nlon, nlat = find_nearest_grid_point(data, lon, lat)
    mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
    sri = SRI_calculate(mean_w)
    max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
    q = transform_to_quantiles(max_w, mean_w)
    it = Intensity_calc(sri, q, THRESHOLD)
    dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
    d2_all = flood_peak_after_drought(q, dr["end_time"].values, DT)
    sev = mean_severity_per_week(dr["max_intensity"].values, dr["duration_weeks"].values)
    var = {"drought_peak": np.asarray(dr["drought_peak"].values, float),
           "mean_drought_severity": sev}
    for pair, X in PAIRS.items():
        d1, d2 = var[pair], d2_all
        m = np.isfinite(d1) & np.isfinite(d2)
        d1, d2 = d1[m], d2[m]
        n = len(d1)
        if n < 15:
            continue
        seed = int(seed_state % (2 ** 32 - 1))
        np.random.seed(seed)
        win = fit_copula(d1, d2, X, Y, q, period_after_event=DT, n_draw=N_POINT,
                         seed=seed, axis="quantile", marginals="parametric")
        u = np.column_stack((stats.rankdata(d1) / (n + 1), stats.rankdata(d2) / (n + 1)))
        aics = aic_table(u)
        ranked = sorted((a, c) for c, a in aics.items() if np.isfinite(a))
        if ranked[0][1] != win["copula_id"]:
            raise RuntimeError(f"winnaar wijkt af van bestcop: {river} {village} {pname} {pair}")
        aic2, c2 = ranked[1]
        np.random.seed(seed)
        ru = fit_copula(d1, d2, X, Y, q, period_after_event=DT, n_draw=N_POINT,
                        seed=seed, axis="quantile", marginals="parametric", cops=[c2])
        mn, mj = win["conditional_minor"], win["conditional_major"]
        ind, unc = win["independence_reference"], win["unconditional"]
        dmin = np.abs(ru["conditional_minor"] - mn)
        dmaj = np.abs(ru["conditional_major"] - mj)
        t = I_TEXT
        rows.append({
            "river": river, "village": village, "river_location": rloc, "period": pname,
            "pair": pair, "n_events": n, "k_minor": win["k_minor"], "k_major": win["k_major"],
            "dist_drought": win["dist1"], "dist_flood": win["dist2"],
            "family": win["copula_name"], "aic": round(win["aic"], 4),
            "runner_up": copulas[c2], "aic_runner_up": round(float(aic2), 4),
            "delta_aic": round(float(aic2 - win["aic"]), 4),
            "max_abs_diff_minor": round(float(np.nanmax(dmin)), 4),
            "max_abs_diff_major": round(float(np.nanmax(dmaj)), 4),
            "diff_minor_at_q": round(float(ru["conditional_minor"][t] - mn[t]), 4),
            "diff_major_at_q": round(float(ru["conditional_major"][t] - mj[t]), 4),
            "q": Q_TEXT,
            "minor_at_q": round(float(mn[t]), 6), "major_at_q": round(float(mj[t]), 6),
            "unconditional_at_q": round(float(unc[t]), 6),
            "independence_at_q": round(float(ind[t]), 6),
            "gap_at_q": round(float(mn[t] - unc[t]), 6),
            "marginal_part_at_q": round(float(ind[t] - unc[t]), 6),
            "copula_part_at_q": round(float(mn[t] - ind[t]), 6),
            "major_minus_minor_at_q": round(float(mj[t] - mn[t]), 6),
        })
        for naam, arr in (("minor_resel", mn), ("major_resel", mj),
                          ("marginal_part", ind - unc), ("copula_part", mn - ind)):
            curves.append(((river, village, pname, pair, naam), arr[ON_GRID]))
    return rows, curves


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
            for r in rivers for l in r["locations"]]
    seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))
    jobs = []
    for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
        for li, (river, village, rloc, lat, lon) in enumerate(locs):
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            jobs.append((li, pi, river, village, rloc, lat, lon, pname, b, e, st))
    t0 = time.time(); rows, curves = [], []
    with mp.Pool(WORKERS) as pool:
        for k, (r, c) in enumerate(pool.imap_unordered(do_cell, jobs), 1):
            rows += r; curves += c
            print(f"[{k}/{len(jobs)}] {(time.time() - t0) / 60:.1f} min", flush=True)
    cells = pd.DataFrame(rows).sort_values(["period", "river", "river_location", "pair"])
    cells.to_csv(f"{OUT}/cells.csv", index=False)

    boot = pd.read_csv(BOOT)
    boot = boot[(boot.scheme == "iid") & (boot.kind == "point")]
    gcols = [f"y_{i:03d}" for i in range(101)]
    worst, compared = 0.0, 0
    for (river, village, pname, pair, naam), arr in curves:
        ref = boot[(boot.river == river) & (boot.village == village) & (boot.period == pname)
                   & (boot.pair == pair) & (boot.quantity == naam)]
        if len(ref) != 1:
            raise RuntimeError(f"geen unieke bootstraprij: {river} {village} {pname} {pair} {naam}")
        worst = max(worst, float(np.nanmax(np.abs(ref[gcols].values[0] - arr))))
        compared += 1
    with open(f"{OUT}/check.txt", "w") as f:
        f.write(f"cellen: {len(cells)}\n")
        f.write(f"vergeleken met de bootstrap, puntrijen iid: {compared} curves van 101 punten\n")
        f.write(f"grootste absolute afwijking: {worst:.2e}"
                f" (de bootstrap schrijft op zes decimalen)\n")
    with open(f"{OUT}/manifest.yaml", "w") as f:
        f.write(f"script: scripts/40_copula_family_and_flood_level.py\n"
                f"run_minutes: {(time.time() - t0) / 60:.1f}\n"
                f"python: {platform.python_version()}\n"
                f"inputs:\n  {DATA}: {sha256(DATA)}\n  {BOOT}: {sha256(BOOT)}\n"
                f"seed_scheme: \"numpy.random.SeedSequence({SEED}).spawn(96), als script 22\"\n"
                f"n_draw: {N_POINT}\nflood_level: {Q_TEXT}\n")
    print(f"klaar, grootste afwijking met de bootstrap {worst:.2e}", flush=True)


if __name__ == "__main__":
    main()
