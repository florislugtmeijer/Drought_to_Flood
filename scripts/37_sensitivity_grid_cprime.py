"""Gevoeligheidsraster van de ECA onder de nul C', met B' en A als grenzen.

Vervolg op het besluit D-21 van 21 oktober 2026 en op de productierun van
scripts/36_run_eca_null_production.py (resultaat in
results/2026-10-21_eca_null_production/). Zelfde nullen, zelfde telling, zelfde
zelfcontroles als script 36, maar nu over het volle raster van R4-01: de
SRI-drempel en het floodpercentiel onafhankelijk van elkaar, venster 4 weken.
De cel (0,5, 0,6915) is de hoofdconfiguratie en moet de productierun
reproduceren op de seed na.

De flood- en droogtezijde zijn ontkoppeld zoals in de gevoeligheidsanalyse van
1 september (flood_quantile apart van threshold, zie Intensity_calc). Bij
strenge combinaties kan een laag van B' of C' te weinig kandidaatweken hebben
of kunnen er geen events zijn; die cellen worden met een melding weggeschreven
in plaats van dat de run stopt.

Uitvoer: results/2026-10-21_sensitivity_grid_cprime/grid.csv, incrementeel met
hervatten. NSIM en LIMIT via de omgeving, default NSIM=10000.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --no-project python scripts/37_sensitivity_grid_cprime.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-10-21_sensitivity_grid_cprime"
W = 4
NSIM = int(os.environ.get("NSIM", 10000))
LIMIT = int(os.environ.get("LIMIT", 0))
SRI_THRESHOLDS = (0.25, 0.5, 0.75, 1.0, 1.5)
FLOOD_QUANTILES = (0.60, 0.6915, 0.80, 0.90, 0.95)
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))

d = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"]) for r in rivers for l in r["locations"]]
if LIMIT: locs = locs[:LIMIT]
os.makedirs(OUT, exist_ok=True)
OUTCSV = f"{OUT}/grid{'_smoke' if LIMIT else ''}.csv"

HEADER = ["sri_threshold", "flood_quantile", "period", "river", "village",
          "n_dr", "n_fl_starts", "k_layer1", "k_layer2", "obs",
          "pA", "expA", "pBp", "expBp", "pCp", "expCp",
          "n_cand_A", "n_cand_Bp1", "n_cand_Bp2", "n_cand_Cp1", "n_cand_Cp2",
          "selfcheck", "seconds"]

done_keys = set()
if os.path.exists(OUTCSV):
    with open(OUTCSV) as fh:
        for row in csv.DictReader(fh):
            done_keys.add((row["sri_threshold"], row["flood_quantile"],
                           row["period"], row["river"], row["village"]))
    f = open(OUTCSV, "a", newline=""); w = csv.writer(f)
else:
    f = open(OUTCSV, "w", newline=""); w = csv.writer(f)
    w.writerow(HEADER); f.flush()


def sim_pass(dend, cand1, cand2, k1, k2, nsim, rng, obs, isd=None, prevf=None, startrule=False):
    """Identiek aan script 36: p-waarde en verwachting onder een gelaagde nul."""
    sims = np.empty(nsim, dtype=int)
    hi = dend + W
    for s in range(nsim):
        parts = []
        if k1: parts.append(rng.choice(cand1, size=k1, replace=False))
        if k2: parts.append(rng.choice(cand2, size=k2, replace=False))
        rf = np.sort(np.concatenate(parts)) if parts else np.empty(0, int)
        sims[s] = np.count_nonzero(np.searchsorted(rf, hi, side="right")
                                   - np.searchsorted(rf, dend, side="right"))
        if s == 0 and isd is not None:
            if k1 and isd[parts[0]].any():
                raise RuntimeError("zelfcontrole: laag-1-start op droogteweek")
            if k2 and not isd[parts[-1]].all():
                raise RuntimeError("zelfcontrole: laag-2-start niet op droogteweek")
            if startrule and prevf is not None and prevf[rf].any():
                raise RuntimeError("zelfcontrole: start met floodweek als voorganger")
            if len(rf) != k1 + k2 or len(np.unique(rf)) != len(rf):
                raise RuntimeError("zelfcontrole: aantal of dubbele starts")
    return float(np.mean(sims >= obs)), float(sims.mean())


t0 = time.time(); done = 0; computed = 0
total = len(SRI_THRESHOLDS) * len(FLOOD_QUANTILES) * len(PERIODS) * len(locs)
# de keten per (locatie, periode, sri) is voor elke flood_quantile gelijk tot aan
# Intensity_calc; de dure stappen (SRI, quantielen) worden daarom gecachet
chain_cache = {}
for pi, (pname, (b, e)) in enumerate(PERIODS):
    for li, (river, village, lat, lon) in enumerate(locs):
        ck = (pname, li)
        if ck not in chain_cache:
            nlon, nlat = find_nearest_grid_point(d, lon, lat)
            mean_ = river_runoff_time_location_mean(d, nlon, nlat, b, e, "1W")
            sri = SRI_calculate(mean_)
            raw = d.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
            wmax = river_runoff_time_location_maximum(d, nlon, nlat, b, e, "1W")
            q = transform_to_quantiles(wmax, raw)
            weeks = mean_.valid_time.values.astype("datetime64[ns]")
            chain_cache[ck] = (sri, q, weeks)
        sri, q, weeks = chain_cache[ck]
        n = len(weeks)
        for st in SRI_THRESHOLDS:
            for fq in FLOOD_QUANTILES:
                key = (str(st), str(fq), pname, river, village)
                if key in done_keys:
                    done += 1; continue
                t1 = time.time()
                rng = np.random.default_rng([46, li, int(st * 100), int(fq * 10000), pi])
                inten = Intensity_calc(sri, q, st, fq)
                fl = extract_events(inten["Flood_Intensity"], inten["SRI"], q, W)
                dr = extract_events(inten["Drought_Intensity"] * -1, inten["SRI"] * -1, q, W)
                isd = np.nan_to_num(sri.values < -st).astype(bool)
                isf = (q.values > fq)
                dend = np.searchsorted(weeks, np.asarray(dr["end_time"].values, dtype="datetime64[ns]"))
                fst = np.searchsorted(weeks, np.asarray(fl["start_time"].values, dtype="datetime64[ns]"))
                obs_sorted = np.sort(fst)
                obs = int(np.count_nonzero(np.searchsorted(obs_sorted, dend + W, side="right")
                                           - np.searchsorted(obs_sorted, dend, side="right")))
                k2 = int(isd[fst].sum()); k1 = len(fst) - k2
                tail_ok = np.zeros(n, bool); tail_ok[:max(0, n - W)] = True
                prevf = np.concatenate([[False], isf[:-1]])
                candA = np.where(tail_ok)[0]
                candB1 = np.where(~isd & tail_ok)[0]
                candB2 = np.where(isd & tail_ok)[0]
                candC1 = np.where(~isd & ~prevf & tail_ok)[0]
                candC2 = np.where(isd & ~prevf & tail_ok)[0]
                row = [st, fq, pname, river, village, len(dend), len(fst), k1, k2, obs]
                cands = [len(candA), len(candB1), len(candB2), len(candC1), len(candC2)]
                sc = []
                if len(dend) == 0 or len(fst) == 0:
                    sc.append("niet toetsbaar")
                if k2 > len(candB2): sc.append(f"B': laag 2 past niet ({k2} > {len(candB2)})")
                if k2 > len(candC2): sc.append(f"C': laag 2 past niet ({k2} > {len(candC2)})")
                if k1 > len(candC1): sc.append(f"C': laag 1 past niet ({k1} > {len(candC1)})")
                if len(fst) > len(candA): sc.append("A: meer starts dan kandidaten")
                if sc:
                    w.writerow(row + [""] * 6 + cands + ["; ".join(sc), round(time.time() - t1, 1)])
                    f.flush(); done += 1; continue
                pA, eA = sim_pass(dend, candA, np.empty(0, int), len(fst), 0, NSIM, rng, obs)
                pB, eB = sim_pass(dend, candB1, candB2, k1, k2, NSIM, rng, obs, isd=isd)
                pC, eC = sim_pass(dend, candC1, candC2, k1, k2, NSIM, rng, obs,
                                  isd=isd, prevf=prevf, startrule=True)
                w.writerow(row + [round(pA, 5), round(eA, 2), round(pB, 5), round(eB, 2),
                                  round(pC, 5), round(eC, 2)] + cands +
                           ["ok", round(time.time() - t1, 1)])
                f.flush(); done += 1; computed += 1
                if computed % 50 == 0 or done == total:
                    el = time.time() - t0
                    print(f"[{done}/{total}] laatst: {st} {fq} {pname} {river} {village[:14]} "
                          f"pC'={pC:.4f} ({el/60:.1f}m, eta {el/computed*(total-done)/60:.0f}m)", flush=True)
f.close()
print("klaar:", OUTCSV)
