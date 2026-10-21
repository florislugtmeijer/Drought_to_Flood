"""D-15 / R-04: de copula-keten onder beide quantielreferenties, naast elkaar.

De ECA-kant drukt het wekelijkse afvoermaximum uit als quantiel van de dagelijkse
reeks (cel 16), de copula-kant als quantiel van de wekelijkse gemiddelden (cel 25).
`quantile_max_value` betekent daardoor niet hetzelfde in Tabel 3 als in de
transitiekansen. D-15 vraagt: gelijktrekken en herrekenen, of laten staan en in de
methodensectie benoemen. Dit script levert het beslismateriaal, het beslist niets.

Per locatie-periode-paar (192 cellen) draait de volledige copula-keten twee keer:

  weekly   referentie = wekelijkse gemiddelden, de huidige copula-kant, identiek
           aan de puntschatting in results/2026-09-02_copula_bootstrap/ (zelfde
           seedstroom, zelfde definities)
  daily    referentie = ruwe dagelijkse reeks van de periode, de ECA-kant, dus
           quantile_reference="daily" zoals de orkestrator in pipeline.py

Zelfde seed per cel voor beide varianten, zodat een verschil nooit de trekking is.
De verwachting vooraf: beide referenties zijn een monotone transformatie van
hetzelfde weekmaximum, dus de rangen en daarmee de copulafit zouden identiek
moeten zijn. Wat wel kan verschuiven: waar het manuscriptniveau 0,6915 op de
curve ligt (F_Y en de aflezing), en de unconditionele lijn. Het script toetst die
verwachting in plaats van erop te vertrouwen.

Sanity checks, hard: per cel moeten de droogte-events onder beide referenties
identiek zijn in aantal en droogtekarakteristiek, want de referentie raakt alleen
de floodzijde. Faalt dat, dan stopt de run.

Uitvoer in results/2026-09-04_copula_quantile_reference/:
  comparison.csv   een rij per cel en variant, met familie, AIC, AIC-verschil met
                   de nummer twee, marginaal voor de floodzijde, en de aflezingen
                   op 0,6915: conditioneel mild en zwaar, unconditioneel,
                   onafhankelijkheidslijn, plus het weekaandeel boven 0,6915
  cell_diffs.csv   een rij per cel: daily min weekly op de aflezingen, het
                   maximale absolute verschil over het hele curveraster, of de
                   familie gelijk koos en of de rangen exact gelijk zijn
  manifest.yaml    conform de werkafspraak

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/28_copula_quantile_reference.py [--limit N]

--limit N draait alleen de eerste N locatie-periodes, voor de rekentijdmeting.
"""
import sys, os, json, re, ast, csv, time, hashlib, warnings, subprocess
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula
from vinecopulas.bivariate import fit as cop_fit, neg_likelihood, copulas

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-04_copula_quantile_reference"
THRESHOLD, DT, N_DRAW, SEED = 0.5, 4, 100000, 42
Q_MAN = 0.6915                     # het floodniveau van het manuscript, norm.cdf(0.5)
Y_GRID = np.linspace(0, 1, 101)
Y = np.append(Y_GRID, Q_MAN)       # laatste index is de aflezing op 0,6915
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
VARIANTS = ("weekly", "daily")
os.makedirs(OUT, exist_ok=True)


def aic_all(u):
    """AIC per familie, zoals bestcop hem berekent, maar dan de hele lijst.

    Zelfde functie als in scripts/12_copula_selection.py, hier nodig voor het
    AIC-verschil met de nummer twee.
    """
    out = []
    for cop in COPS:
        try:
            par = cop_fit(cop, u.copy())
            k = 2 if cop == 15 else 1
            out.append((cop, par, 2 * k + 2 * neg_likelihood(par, cop, u.copy())))
        except Exception:
            out.append((cop, np.nan, np.inf))
    return sorted(out, key=lambda r: (np.inf if not np.isfinite(r[2]) else r[2]))


def fmt_par(p):
    return round(float(p), 6) if np.ndim(p) == 0 else np.round(np.asarray(p, float), 6).tolist()


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
            for r in rivers for l in r["locations"]]

    # dezelfde seedstroom als scripts/22_bootstrap_transition_ci.py, zodat de
    # weekly-variant bit-identiek is aan de puntschatting in de bootstrapmap
    seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))
    jobs = []
    for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
        for li, (river, village, rloc, lat, lon) in enumerate(locs):
            st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
            jobs.append((river, village, rloc, lat, lon, pname, b, e, st))
    if limit:
        jobs = jobs[:limit]

    fc = open(f"{OUT}/comparison.csv", "w", newline=""); wc = csv.writer(fc)
    wc.writerow(["river", "village", "river_location", "period", "pair", "variant",
                 "n_events", "k_minor", "k_major", "cop_id", "cop_name", "par", "aic",
                 "cop_name_next", "delta_aic_next", "dist_flood_marginal",
                 "trans_minor_at_q", "trans_major_at_q", "uncond_at_q", "indep_at_q",
                 "weekshare_above_q", "n_nonfinite_draws"])
    fd = open(f"{OUT}/cell_diffs.csv", "w", newline=""); wd = csv.writer(fd)
    wd.writerow(["river", "village", "river_location", "period", "pair", "n_events",
                 "same_family", "ranks_equal", "d_trans_minor_at_q", "d_trans_major_at_q",
                 "d_uncond_at_q", "d_indep_at_q", "max_abs_dcurve_minor",
                 "max_abs_dcurve_major", "max_abs_duncond"])

    t0 = time.time(); done = 0; skipped = []
    for (river, village, rloc, lat, lon, pname, b, e, seed_state) in jobs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        raw = data.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
        q_ref = {"weekly": transform_to_quantiles(max_w, mean_w),
                 "daily": transform_to_quantiles(max_w, raw)}
        dr = {}
        for v in VARIANTS:
            it = Intensity_calc(sri, q_ref[v], THRESHOLD)
            dr[v] = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1,
                                   q_ref[v], DT)
        # sanity, hard: de referentie raakt alleen de floodzijde, dus de
        # droogte-events moeten identiek zijn
        if len(dr["weekly"]["start_time"]) != len(dr["daily"]["start_time"]):
            raise AssertionError(f"droogte-aantallen verschillen: {river}/{village} {pname}")
        for veld in ("drought_peak", "mean_drought_severity"):
            a = np.asarray(dr["weekly"][veld].values, float)
            c = np.asarray(dr["daily"][veld].values, float)
            if not np.allclose(a, c, equal_nan=True):
                raise AssertionError(f"{veld} verschilt: {river}/{village} {pname}")

        seed = int(seed_state % (2 ** 32 - 1))
        for pair, X in PAIRS.items():
            res, rank_sets = {}, {}
            for v in VARIANTS:
                d1 = np.asarray(dr[v][pair].values, float)
                d2 = np.asarray(dr[v]["quantile_max_value"].values, float)
                m = np.isfinite(d1) & np.isfinite(d2)
                d1, d2 = d1[m], d2[m]
                if len(d1) < 10:
                    res[v] = None
                    continue
                rank_sets[v] = stats.rankdata(d2)
                np.random.seed(seed)
                r = fit_copula(d1, d2, X, Y, q_ref[v], period_after_event=DT,
                               n_draw=N_DRAW, seed=seed, axis="quantile",
                               marginals="parametric")
                u = np.column_stack((stats.rankdata(d1) / (len(d1) + 1),
                                     stats.rankdata(d2) / (len(d1) + 1)))
                ranked = aic_all(u)
                (c1, _, a1), (c2, _, a2) = ranked[0], ranked[1]
                r["cop_next"] = copulas[c2]
                r["delta_aic_next"] = float(a2 - a1)
                r["weekshare"] = float((np.asarray(q_ref[v].values, float) > Q_MAN).mean())
                res[v] = r
                wc.writerow([river, village, rloc, pname, pair, v, r["n_events"],
                             r["k_minor"], r["k_major"], r["copula_id"], r["copula_name"],
                             fmt_par(r["par"]), round(r["aic"], 4), r["cop_next"],
                             round(r["delta_aic_next"], 4), r["dist2"],
                             round(float(r["conditional_minor"][-1]), 6),
                             round(float(r["conditional_major"][-1]), 6),
                             round(float(r["unconditional"][-1]), 6),
                             round(float(r["independence_reference"][-1]), 6),
                             round(r["weekshare"], 6), r["n_nonfinite_draws"]])
            if res.get("weekly") is None or res.get("daily") is None:
                skipped.append((river, village, pname, pair))
                continue
            rw, rd = res["weekly"], res["daily"]
            wd.writerow([river, village, rloc, pname, pair, rw["n_events"],
                         int(rw["copula_id"] == rd["copula_id"]),
                         int(np.array_equal(rank_sets["weekly"], rank_sets["daily"])),
                         round(float(rd["conditional_minor"][-1] - rw["conditional_minor"][-1]), 6),
                         round(float(rd["conditional_major"][-1] - rw["conditional_major"][-1]), 6),
                         round(float(rd["unconditional"][-1] - rw["unconditional"][-1]), 6),
                         round(float(rd["independence_reference"][-1] - rw["independence_reference"][-1]), 6),
                         round(float(np.nanmax(np.abs(rd["conditional_minor"][:-1] - rw["conditional_minor"][:-1]))), 6),
                         round(float(np.nanmax(np.abs(rd["conditional_major"][:-1] - rw["conditional_major"][:-1]))), 6),
                         round(float(np.nanmax(np.abs(rd["unconditional"][:-1] - rw["unconditional"][:-1]))), 6)])
        fc.flush(); fd.flush()
        done += 1
        el = time.time() - t0
        print(f"[{done}/{len(jobs)}] {pname:6} {river:8} {village[:22]:22} "
              f"{el:6.1f}s eta {el/done*(len(jobs)-done):6.1f}s", flush=True)

    fc.close(); fd.close()
    if skipped:
        print(f"overgeslagen (n<10): {skipped}", flush=True)

    if not limit:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True).stdout.strip()
        sha = hashlib.sha256(open(DATA, "rb").read()).hexdigest()
        import importlib.metadata as im
        pkgs = {p: im.version(p) for p in
                ("numpy", "scipy", "pandas", "xarray", "netCDF4", "vinecopulas")}
        with open(f"{OUT}/manifest.yaml", "w") as mf:
            mf.write(f"""run_date: 2026-09-04
git_commit: {commit}
script: scripts/28_copula_quantile_reference.py
purpose: D-15 / R-04, beslismateriaal quantielreferentie, geen wijziging
config:
  threshold: {THRESHOLD}
  period_after_event: {DT}
  time_scale: 1W
  n_draw: {N_DRAW}
  seed: {SEED}                # SeedSequence(42).spawn(96), stroom van script 22
  q_manuscript: {Q_MAN}
  y_grid: linspace(0, 1, 101) plus {Q_MAN}
  pairs: {list(PAIRS)}
  periods: {dict(PERIODS)}
  axis: quantile
  marginals: parametric
  variants: [weekly, daily]
inputs:
  {os.path.basename(DATA)}: {sha}
python: {sys.version.split()[0]}
packages: {json.dumps(pkgs)}
""")
    print(f"\nklaar in {(time.time()-t0)/60:.1f} min, uitvoer in {OUT}/", flush=True)


if __name__ == "__main__":
    main()
