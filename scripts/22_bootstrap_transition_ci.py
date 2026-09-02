"""T-11, tweede helft: betrouwbaarheidsintervallen bij de transitiekansen (R4-03).

Reviewer #4 vraagt intervallen bij de transitiekansen. Die bestonden niet. Dit is
een niet-parametrische bootstrap op de droogte-events.

Opzet per cel, en een cel is locatie maal periode maal variabelenpaar:

  puntschatting   zoals results/2026-09-02_copula_corrected, dus met de vier
                  besluiten erin: F_Y toegepast (R-01), floodvenster vier weken na
                  afloop (R-02), duur gedeeld door het aantal weken (R-03), en
                  parametrische marginalen conform pagina 21

  bootstrap       B replicaties, elk een trekking met teruglegging uit de n
                  event-paren. Per replicatie opnieuw: de parameters van de
                  marginalen, de rangtransformatie, de copulaselectie, de drempels
                  en de curves

  intervallen     percentiel, 95 procent, puntsgewijs over de 101 rasterpunten

Wat er per cel uitkomt:
  - de milde en de zware curve met hun interval
  - het verschil zwaar min mild, apart gebootstrapt. Twee overlappende intervallen
    sluiten een verschil niet uit, want de curves zijn sterk gecorreleerd over de
    replicaties, dus dit moet los
  - de opsplitsing in een marginaal deel en een copula deel, allebei met interval.
    Het marginale deel is (1 - F_Y) min unconditioneel, dus of het venster na een
    droogte natter is dan een willekeurig venster. Het copula deel is conditioneel
    min (1 - F_Y), dus of de piek samenhangt met de zwaarte van de droogte

Keuzes, met de reden:
  - familie-herselectie per replicatie is de hoofdroute, want dat volgt de
    procedure die de methodensectie beschrijft. De vastgezette familie staat als
    tweede kolom, uit dezelfde replicaties, zodat parameteronzekerheid en
    selectieonzekerheid te scheiden zijn
  - de marginale verdelingsfamilie wordt eenmaal op de volle steekproef gekozen, per
    replicatie worden alleen de parameters opnieuw geschat. Volledige herselectie
    per replicatie kost 82 ms tegen 20 ms en zou de run op tien uur brengen. De
    keuze van de familie is bovendien een modelkeuze, niet een schatting
  - percentiel-intervallen, geen BCa. De biascorrectie duwt de benodigde
    percentielen ver de staart in, en met familie-herselectie is de schatter een
    argmax over vijftien families en dus niet glad, waardoor de jackknife achter BCa
    op drijfzand staat. De mediane bias wordt wel gerapporteerd
  - gemiddelde rangen bij gebonden waardes, dus rankdata default
  - replicaties worden nooit weggegooid op grond van hun uitkomst. Mislukte fits
    worden geteld en gerapporteerd
  - naast de iid-bootstrap een circulaire blokbootstrap met bloklengte n^(1/3), als
    controle op seriele afhankelijkheid tussen opeenvolgende droogtes

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/22_bootstrap_transition_ci.py
"""
import sys, os, json, re, ast, csv, time, warnings, multiprocessing as mp
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events, empirical_cdf)
from dtf.copula import (fit_copula, flood_peak_after_drought, mean_severity_per_week,
                        fit_best_distribution, calculate_rolling_max, _exceedance)
from vinecopulas.bivariate import bestcop, fit as cop_fit, random as cop_random, copulas

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_copula_bootstrap"
THRESHOLD, DT, SEED = 0.5, 4, 42
B = 2000                 # replicaties
N_POINT, N_REP = 100000, 20000   # trekkingen voor de puntschatting en per replicatie
Y = np.linspace(0, 1, 101)
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
WORKERS = max(1, mp.cpu_count() - 2)
EPS = 1e-6
os.makedirs(OUT, exist_ok=True)


def circular_blocks(rng, n, length):
    """Circulaire blokbootstrap: trek startpunten, plak blokken aan elkaar."""
    k = int(np.ceil(n / length))
    starts = rng.integers(0, n, k)
    idx = np.concatenate([(s + np.arange(length)) % n for s in starts])
    return idx[:n]


def one_replicate(d1, d2, X, D1, D2, cop_point, rng, idx, with_fixed=True):
    """Eén bootstrap-replicatie. Geeft None terug als de fit faalt."""
    a, c = d1[idx], d2[idx]
    n = len(a)
    try:
        p1, p2 = D1.fit(a), D2.fit(c)
        t_min = float(np.clip(D1.cdf(X[0], *p1), EPS, 1 - EPS))
        t_maj = float(np.clip(D1.cdf(X[1], *p1), EPS, 1 - EPS))
        read = np.clip(D2.cdf(Y, *p2), EPS, 1 - EPS)
        u = np.column_stack((stats.rankdata(a) / (n + 1), stats.rankdata(c) / (n + 1)))
        fam, par, _ = bestcop(COPS, u.copy())
    except Exception:
        return None
    out = {"family": fam}

    def curves(cop_id, p):
        """Geeft (minor, major) of None als de trekking onbruikbaar is."""
        draw = cop_random(cop_id, p, N_REP)
        draw = draw[np.all(np.isfinite(draw), axis=1)]
        if len(draw) == 0:
            return None
        return (_exceedance(np.sort(draw[draw[:, 0] >= t_min, 1]), read),
                _exceedance(np.sort(draw[draw[:, 0] >= t_maj, 1]), read))

    hoofd = curves(fam, par)
    if hoofd is None:
        return None
    out["minor_resel"], out["major_resel"] = hoofd

    # De vastgezette familie is diagnostiek, geen hoofdresultaat. Als die fit op de
    # parametergrens uitkomt geeft random uitsluitend NaN, en dat gebeurt juist bij
    # replicaties met zwakke afhankelijkheid. Die replicatie weggooien zou de
    # gerapporteerde intervallen vertekenen, dus alleen deze kolom wordt NaN.
    leeg = np.full(len(Y), np.nan)
    if with_fixed:
        try:
            vast = curves(cop_point, cop_fit(cop_point, u.copy()))
        except Exception:
            vast = None
        out["minor_fixed"], out["major_fixed"] = vast if vast else (leeg, leeg)
        out["fixed_failed"] = int(vast is None)
    else:
        out["minor_fixed"], out["major_fixed"] = leeg, leeg
        out["fixed_failed"] = 0
    out["independence"] = 1.0 - read
    return out


def do_cell(job):
    """Eén locatie-periode, beide variabelenparen, punt plus bootstrap."""
    (li, pi, river, village, rloc, lat, lon, pname, b, e, seed_state) = job
    rows_ci, rows_diag, rows_sel = [], [], []
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
    rolling = calculate_rolling_max(q, DT)
    uncond = 1.0 - empirical_cdf(rolling[np.isfinite(rolling)], Y)

    for pair, X in PAIRS.items():
        d1, d2 = var[pair], d2_all
        m = np.isfinite(d1) & np.isfinite(d2)
        d1, d2 = d1[m], d2[m]
        n = len(d1)
        if n < 15:   # onder de 15 events is een bootstrap niet zinvol
            continue
        seed = int(seed_state % (2 ** 32 - 1))
        np.random.seed(seed)
        point = fit_copula(d1, d2, X, Y, q, period_after_event=DT, n_draw=N_POINT,
                           seed=seed, axis="quantile", marginals="parametric")
        (D1, P1), _ = fit_best_distribution(d1)
        (D2, P2), _ = fit_best_distribution(d2)
        cop_point = point["copula_id"]
        lag1_a = float(stats.spearmanr(d1[:-1], d1[1:]).statistic) if n > 5 else np.nan
        lag1_b = float(stats.spearmanr(d2[:-1], d2[1:]).statistic) if n > 5 else np.nan
        L = max(1, int(round(n ** (1 / 3))))
        # De vaste-familie kolom is diagnostiek en kost ongeveer de helft van de
        # rekentijd. Hij wordt alleen berekend op de eerste locatie van elke rivier,
        # wat genoeg is om te laten zien hoeveel van de onzekerheid uit de
        # familiekeuze komt.
        with_fixed = rloc == "First location"

        for scheme in ("iid", "block"):
            rng = np.random.default_rng(seed + (0 if scheme == "iid" else 1))
            np.random.seed(seed + (0 if scheme == "iid" else 1))
            acc = {k: [] for k in ("minor_resel", "major_resel", "minor_fixed",
                                   "major_fixed", "independence")}
            fams, fails, fixed_fails = [], 0, 0
            for _ in range(B):
                idx = (rng.integers(0, n, n) if scheme == "iid"
                       else circular_blocks(rng, n, L))
                r = one_replicate(d1, d2, X, D1, D2, cop_point, rng, idx,
                                  with_fixed=with_fixed)
                if r is None:
                    fails += 1
                    continue
                fams.append(r["family"])
                fixed_fails += r.get("fixed_failed", 0)
                for k in acc:
                    acc[k].append(r[k])
            if not fams:
                continue
            A = {k: np.array(v) for k, v in acc.items()}
            A["diff_resel"] = A["major_resel"] - A["minor_resel"]
            A["marginal_part"] = A["independence"] - uncond
            A["copula_part"] = A["minor_resel"] - A["independence"]
            punt = {"minor_resel": point["conditional_minor"],
                    "major_resel": point["conditional_major"],
                    "diff_resel": point["conditional_major"] - point["conditional_minor"],
                    "independence": point["independence_reference"],
                    "marginal_part": point["independence_reference"] - uncond,
                    "copula_part": point["conditional_minor"] - point["independence_reference"],
                    "minor_fixed": point["conditional_minor"],
                    "major_fixed": point["conditional_major"]}
            for naam in ("minor_resel", "major_resel", "diff_resel", "marginal_part",
                         "copula_part", "minor_fixed", "major_fixed"):
                arr = A[naam]
                lo = np.nanpercentile(arr, 2.5, axis=0)
                hi = np.nanpercentile(arr, 97.5, axis=0)
                med = np.nanmedian(arr, axis=0)
                for soort, vals in (("point", punt[naam]), ("lo", lo), ("hi", hi),
                                    ("median", med)):
                    rows_ci.append([river, village, rloc, pname, pair, scheme, naam,
                                    soort, n] + [round(float(v), 6) for v in vals])
            # diagnostiek
            arr = A["minor_resel"]
            sd = np.nanstd(arr, axis=0, ddof=1)
            ok = sd > 1e-12
            m_b = np.nanmax(np.abs(arr[:, ok] - point["conditional_minor"][ok]) / sd[ok], axis=1)
            supt = float(np.nanpercentile(m_b, 95))
            width_min = float(np.nanmedian(np.nanpercentile(arr, 97.5, axis=0)
                                           - np.nanpercentile(arr, 2.5, axis=0)))
            width_diff = float(np.nanmedian(np.nanpercentile(A["diff_resel"], 97.5, axis=0)
                                            - np.nanpercentile(A["diff_resel"], 2.5, axis=0)))
            bias = float(np.nanmedian(np.nanmedian(arr, axis=0) - point["conditional_minor"]))
            cnt = {}
            for f in fams:
                cnt[copulas[f]] = cnt.get(copulas[f], 0) + 1
            top = max(cnt, key=cnt.get)
            rows_diag.append([river, village, rloc, pname, pair, scheme, n,
                              point["k_minor"], point["k_major"],
                              point["copula_name"], top, round(cnt[top] / len(fams), 4),
                              len(cnt), fails, round(bias, 5), round(width_min, 4),
                              round(width_diff, 4), round(supt / 1.96, 3),
                              fixed_fails, int(with_fixed),
                              round(lag1_a, 4), round(lag1_b, 4), L])
            for fam_naam, aantal in sorted(cnt.items(), key=lambda kv: -kv[1]):
                rows_sel.append([river, village, rloc, pname, pair, scheme,
                                 fam_naam, aantal, round(aantal / len(fams), 4)])
    return rows_ci, rows_diag, rows_sel


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
            jobs.append((li, pi, river, village, rloc, lat, lon, pname, b, e, st))

    # hervatten: locatie-periodes die al volledig in de diagnostiek staan worden
    # overgeslagen. Rijen van een job worden pas geschreven als de job helemaal
    # klaar is, dus aanwezigheid in de diagnostiek betekent compleet.
    klaar = set()
    diag_pad = f"{OUT}/bootstrap_diagnostics.csv"
    hervat = os.path.exists(diag_pad) and os.path.getsize(diag_pad) > 0
    if hervat:
        with open(diag_pad) as fh:
            for r in csv.DictReader(fh):
                klaar.add((r["river"], r["village"], r["period"]))
        jobs = [j for j in jobs if (j[2], j[3], j[7]) not in klaar]
        print(f"hervat: {len(klaar)} locatie-periodes staan er al, "
              f"{len(jobs)} te gaan", flush=True)
    mode = "a" if hervat else "w"
    ycols = [f"y_{i:03d}" for i in range(len(Y))]
    fci = open(f"{OUT}/transition_ci.csv", mode, newline=""); wci = csv.writer(fci)
    fdg = open(diag_pad, mode, newline=""); wdg = csv.writer(fdg)
    fsel = open(f"{OUT}/selection_frequency.csv", mode, newline=""); wsel = csv.writer(fsel)
    if not hervat:
        wci.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                      "quantity", "kind", "n_events"] + ycols)
        wdg.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                      "n_events", "k_minor", "k_major", "copula_point", "copula_modal",
                      "modal_share", "n_families_seen", "failed_replicates", "median_bias",
                      "median_width_minor", "median_width_diff", "supt_over_196",
                      "fixed_family_failures", "fixed_family_computed",
                      "lag1_spearman_drought", "lag1_spearman_flood", "block_length"])
        wsel.writerow(["river", "village", "river_location", "period", "pair", "scheme",
                       "copula_name", "count", "share"])

    t0 = time.time(); done = 0
    with mp.Pool(WORKERS) as pool:
        for rows_ci, rows_diag, rows_sel in pool.imap_unordered(do_cell, jobs):
            for r in rows_ci: wci.writerow(r)
            for r in rows_diag: wdg.writerow(r)
            for r in rows_sel: wsel.writerow(r)
            fci.flush(); fdg.flush(); fsel.flush()
            done += 1
            el = time.time() - t0
            print(f"[{done}/{len(jobs)}] {el/60:6.1f} min, eta {el/done*(len(jobs)-done)/60:6.1f} min",
                  flush=True)
    fci.close(); fdg.close(); fsel.close()
    print(f"\nklaar in {(time.time()-t0)/60:.1f} min, uitvoer in {OUT}/", flush=True)


if __name__ == "__main__":
    main()
