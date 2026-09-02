"""T-11: is er echt zo weinig copula-afhankelijkheid? Vier toetsen per cel.

Vraag van Floris, 2 september: onderzoek nog een keer of de copula's echt zo
weinig betekenis hebben, en of de manier van significantie bepalen deugt. De
eerdere onderbouwing leunde op Kendall's tau als beschrijvend getal en op
bootstrap-intervallen om het copula-deel. Tau ziet alleen monotone samenhang, dus
hier vier toetsen die elk iets anders zien:

  1. Kendall's tau, met analytische p. Monotone samenhang, de klassieke toets.
  2. Spearman's rho, met analytische p. Ook monotoon, andere weging.
  3. Hoeffding's D, met permutatie-p. Ziet ook NIET-monotone samenhang, dus ook
     een verband waarbij zowel milde als zware droogtes lagere pieken geven.
  4. Een permutatietoets op de copulafit zelf. De nulhypothese is
     onafhankelijkheid: de koppeling tussen droogtezwaarte en piek wordt B keer
     verbroken door de pieken te husselen, en elke keer wordt dezelfde procedure
     gedraaid als in het artikel, dus bestcop over vijftien families. De toets
     vergelijkt de AIC van de beste fit met wat husselen oplevert. Dit is de
     eerlijkste toets op "vindt de copula iets", want de selectie over vijftien
     families zit in de nulverdeling. Zonder dat zou de AIC altijd te gunstig
     lijken, vijftien kandidaten vinden altijd wel iets.

  Daarnaast, uit dezelfde permutaties: p-waardes voor het copula-deel van het gat
  op drie floodniveaus en voor het maximum ervan over de curve. Dat koppelt de
  toets direct aan de grootheid in de figuren.

Belangrijk voordeel van permuteren boven bootstrappen voor deze vraag: husselen
laat beide marginale verdelingen exact intact en verbreekt alleen de koppeling.
De drempels en F_Y veranderen dus niet mee, en de toets isoleert precies de
afhankelijkheid. De bootstrap-intervallen beantwoorden de andere vraag, hoe groot
het effect is; deze toets beantwoordt of het bestaat.

Definities conform de besluiten van 2 september: floodvenster vier weken na
afloop (R-02), duur in weken (R-03), parametrische marginalen, as op F_Y (R-01).

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/25_dependence_tests.py
"""
import sys, os, json, re, ast, csv, time, warnings, multiprocessing as mp
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events, empirical_cdf)
from dtf.copula import (flood_peak_after_drought, mean_severity_per_week,
                        fit_best_distribution, calculate_rolling_max, _exceedance)
from vinecopulas.bivariate import bestcop, random as cop_random, copulas

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_dependence_tests"
THRESHOLD, DT, SEED = 0.5, 4, 43
B_PERM, N_DRAW = 1000, 20000
Y = np.linspace(0, 1, 101)
QI = {"q6915": 69, "q90": 90, "q95": 95}
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
WORKERS = max(1, mp.cpu_count() - 2)
EPS = 1e-6
os.makedirs(OUT, exist_ok=True)


def hoeffding_d(a, c):
    """Hoeffding's D, O(n^2). Ziet ook niet-monotone samenhang. Bij gebonden
    waardes is dit een statistiek zonder exacte nulverdeling, maar de p komt hier
    uit permutaties van dezelfde data, dus dat is geen probleem."""
    n = len(a)
    R = stats.rankdata(a); S = stats.rankdata(c)
    Q = 1 + np.sum((a[None, :] < a[:, None]) & (c[None, :] < c[:, None]), axis=1) \
        + 0.25 * np.sum((a[None, :] == a[:, None]) & (c[None, :] == c[:, None]), axis=1) - 0.25 \
        + 0.5 * np.sum((a[None, :] == a[:, None]) & (c[None, :] < c[:, None]), axis=1) \
        + 0.5 * np.sum((a[None, :] < a[:, None]) & (c[None, :] == c[:, None]), axis=1)
    D1 = np.sum((Q - 1) * (Q - 2))
    D2 = np.sum((R - 1) * (R - 2) * (S - 1) * (S - 2))
    D3 = np.sum((R - 2) * (S - 2) * (Q - 1))
    d = 30.0 * ((n - 2) * (n - 3) * D1 + D2 - 2 * (n - 2) * D3) / \
        (n * (n - 1) * (n - 2) * (n - 3) * (n - 4))
    return float(d)


def copula_part(a, c, t_min, read, n):
    """AIC van de beste familie plus het copula-deel van het gat, uit een fit op
    de rangen en een trekking. Zelfde procedure als het artikel."""
    u = np.column_stack((stats.rankdata(a) / (n + 1), stats.rankdata(c) / (n + 1)))
    fam, par, aic = bestcop(COPS, u.copy())
    draw = cop_random(fam, par, N_DRAW)
    draw = draw[np.all(np.isfinite(draw), axis=1)]
    cond = _exceedance(np.sort(draw[draw[:, 0] >= t_min, 1]), read)
    return fam, float(aic), cond - (1.0 - read)


def do_cell(job):
    (river, village, rloc, pname, b, e, lat, lon, seed_state) = job
    rows = []
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
        a0, c0 = d1[m], d2[m]
        n = len(a0)
        if n < 15:
            continue
        seed = int(seed_state % (2 ** 32 - 1))
        rng = np.random.default_rng(seed)
        np.random.seed(seed)

        # marginalen een keer, ze veranderen niet onder permutatie
        (D1, P1), _ = fit_best_distribution(a0)
        (D2, P2), _ = fit_best_distribution(c0)
        t_min = float(np.clip(D1.cdf(X[0], *P1), EPS, 1 - EPS))
        read = np.clip(D2.cdf(Y, *P2), EPS, 1 - EPS)

        tau, tau_p = stats.kendalltau(a0, c0)
        rho, rho_p = stats.spearmanr(a0, c0)
        hd_obs = hoeffding_d(a0, c0)
        fam_obs, aic_obs, cp_obs = copula_part(a0, c0, t_min, read, n)

        ge_aic = ge_hd = 0
        ge_cp = {k: 0 for k in QI}
        ge_max = 0
        cp_obs_at = {k: cp_obs[j] for k, j in QI.items()}
        max_obs = float(np.nanmax(np.abs(cp_obs)))
        for _ in range(B_PERM):
            cperm = c0[rng.permutation(n)]
            ge_hd += hoeffding_d(a0, cperm) >= hd_obs
            _, aic_p, cp_p = copula_part(a0, cperm, t_min, read, n)
            ge_aic += aic_p <= aic_obs
            for k, j in QI.items():
                ge_cp[k] += abs(cp_p[j]) >= abs(cp_obs_at[k])
            ge_max += np.nanmax(np.abs(cp_p)) >= max_obs
        pv = lambda g: (1 + g) / (B_PERM + 1)
        rows.append([river, village, rloc, pname, pair, n,
                     int(np.sum(a0 > X[0])), int(np.sum(a0 > X[1])),
                     D1.name, D2.name, copulas[fam_obs], round(aic_obs, 4),
                     round(float(tau), 4), round(float(tau_p), 5),
                     round(float(rho), 4), round(float(rho_p), 5),
                     round(hd_obs, 6), round(pv(ge_hd), 5), round(pv(ge_aic), 5)]
                    + [x for k in QI for x in
                       (round(float(cp_obs_at[k]), 4), round(pv(ge_cp[k]), 5))]
                    + [round(max_obs, 4), round(pv(ge_max), 5)])
    return rows


def main():
    data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
            for r in rivers for l in r["locations"]]
    seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))
    jobs = []
    for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
        for li, (river, village, rloc, lat, lon) in enumerate(locs):
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            jobs.append((river, village, rloc, pname, b, e, lat, lon, st))
    f = open(f"{OUT}/dependence_tests.csv", "w", newline=""); w = csv.writer(f)
    w.writerow(["river", "village", "river_location", "period", "pair", "n_events",
                "k_minor", "k_major", "dist1", "dist2", "copula_name", "aic",
                "tau", "tau_p", "rho", "rho_p", "hoeffd", "hoeffd_p", "aic_perm_p",
                "cp_q6915", "cp_q6915_p", "cp_q90", "cp_q90_p", "cp_q95", "cp_q95_p",
                "cp_maxabs", "cp_maxabs_p"])
    t0 = time.time(); done = 0
    with mp.Pool(WORKERS) as pool:
        for rows in pool.imap_unordered(do_cell, jobs):
            for r in rows: w.writerow(r)
            f.flush(); done += 1
            el = time.time() - t0
            print(f"[{done}/{len(jobs)}] {el/60:5.1f} min", flush=True)
    f.close()
    print(f"klaar in {(time.time()-t0)/60:.1f} min, uitvoer in {OUT}/", flush=True)


if __name__ == "__main__":
    main()
