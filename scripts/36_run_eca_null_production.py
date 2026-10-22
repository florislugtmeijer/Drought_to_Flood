"""Productierun van de ECA Monte Carlo onder de nul C', met de gepubliceerde nul A ernaast.

Besluit D-21, 21 oktober 2026 (CHANGELOG-methodology.md): de drempels blijven
SRI 0,5 met floodniveau norm.cdf(0,5), de nul van de toets wordt C'. De
gepubliceerde nul A draait in dezelfde pass mee, met dezelfde events en
dezelfde telling, zodat oud en nieuw uit hetzelfde rekenwerk komen.

De nullen verschillen alleen in waar een gesimuleerde floodstart mag vallen.
Het aantal starts is steeds het waargenomen aantal, getrokken zonder
teruglegging, en de telling is die van de toets: een droogte telt als match
zodra minstens een start strikt na het droogte-einde en hoogstens W weken
erna valt.

  A   alle weken. De gepubliceerde nul. Conform monte_carlo_p_value in
      src/dtf/pipeline.py vallen de laatste W weken buiten de kandidaten.
  C'  gestratificeerd met startregel: het waargenomen aantal starts op
      droogteweken (laag 2) uniform over de droogteweken, de rest (laag 1) over
      de niet-droogteweken, en in beide lagen alleen op weken waarvan de
      voorganger in de waargenomen floodreeks geen floodweek is. C' gebruikt
      daarmee de waargenomen floodreeks en is deels circulair. Ook hier vallen
      de laatste W weken buiten de kandidaten.

Weekmaskers op het weekraster van de toets: droogteweek is SRI < -threshold,
floodweek is weekmaximum-quantiel > norm.cdf(threshold), referentie de
dagelijkse reeks van de periode.

Zelfcontroles per cel, hard: elke gesimuleerde trekking heeft het juiste
aantal starts per laag, laag 1 ligt niet op een droogteweek, en onder C' heeft
geen kandidaat een floodweek als voorganger. De eerste simulatie van elke cel
wordt element voor element gecontroleerd.

Uitvoer: results/2026-10-21_eca_null_production/production.csv, incrementeel
met hervatten (bestaande rijen worden overgeslagen). NSIM en LIMIT via de
omgeving, default NSIM=10000.

Draaien vanuit de repo-root:
  python3 scripts/36_run_eca_null_production.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy.stats import norm
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-10-21_eca_null_production"
W = 4
NSIM = int(os.environ.get("NSIM", 10000))
LIMIT = int(os.environ.get("LIMIT", 0))
THRESHOLDS = tuple(float(t) for t in os.environ.get("THRESHOLDS", "0.5").split(","))
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))

d = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"]) for r in rivers for l in r["locations"]]
if LIMIT: locs = locs[:LIMIT]
os.makedirs(OUT, exist_ok=True)
OUTCSV = f"{OUT}/production{'_smoke' if LIMIT else ''}.csv"

HEADER = ["threshold", "period", "river", "village", "n_dr", "n_fl_starts",
          "k_layer1", "k_layer2", "obs",
          "pA", "expA", "pCp", "expCp",
          "n_cand_A", "n_cand_Cp1", "n_cand_Cp2",
          "selfcheck", "seconds"]

done_keys = set()
if os.path.exists(OUTCSV):
    with open(OUTCSV) as fh:
        for row in csv.DictReader(fh):
            done_keys.add((row["threshold"], row["period"], row["river"], row["village"]))
    f = open(OUTCSV, "a", newline=""); w = csv.writer(f)
else:
    f = open(OUTCSV, "w", newline=""); w = csv.writer(f)
    w.writerow(HEADER); f.flush()


def runs_of(mask):
    m = np.asarray(mask, bool)
    if not m.any(): return []
    dif = np.diff(np.concatenate([[False], m, [False]]).astype(int))
    st_, en = np.where(dif == 1)[0], np.where(dif == -1)[0]
    return list(zip(st_.tolist(), (en - st_).tolist()))


def sim_pass(dend, cand1, cand2, k1, k2, nsim, rng, obs, isd=None, prevf=None, startrule=False):
    """p-waarde en verwachting onder een nul met kandidaatlagen cand1/cand2.
    k2 == 0 en cand2 leeg betekent ongelaagd (nul A) met cand1 als enige laag."""
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


t0 = time.time(); done = 0
total = len(THRESHOLDS) * len(PERIODS) * len(locs)
for thr in THRESHOLDS:
    for pi, (pname, (b, e)) in enumerate(PERIODS):
        for li, (river, village, lat, lon) in enumerate(locs):
            key = (str(thr), pname, river, village)
            if key in done_keys:
                done += 1; continue
            t1 = time.time()
            rng = np.random.default_rng([45, li, int(thr * 100), pi])
            nlon, nlat = find_nearest_grid_point(d, lon, lat)
            mean_ = river_runoff_time_location_mean(d, nlon, nlat, b, e, "1W")
            sri = SRI_calculate(mean_)
            raw = d.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
            wmax = river_runoff_time_location_maximum(d, nlon, nlat, b, e, "1W")
            q = transform_to_quantiles(wmax, raw)
            inten = Intensity_calc(sri, q, thr)
            fl = extract_events(inten["Flood_Intensity"], inten["SRI"], q, W)
            dr = extract_events(inten["Drought_Intensity"] * -1, inten["SRI"] * -1, q, W)
            weeks = mean_.valid_time.values.astype("datetime64[ns]"); n = len(weeks)
            isd = np.nan_to_num(sri.values < -thr).astype(bool)
            isf = (q.values > norm.cdf(thr))
            dend = np.searchsorted(weeks, np.asarray(dr["end_time"].values, dtype="datetime64[ns]"))
            fst = np.searchsorted(weeks, np.asarray(fl["start_time"].values, dtype="datetime64[ns]"))
            obs_sorted = np.sort(fst)
            obs = int(np.count_nonzero(np.searchsorted(obs_sorted, dend + W, side="right")
                                       - np.searchsorted(obs_sorted, dend, side="right")))
            # lagen van de waargenomen starts
            k2 = int(isd[fst].sum()); k1 = len(fst) - k2
            # kandidaten; de staartregel van A geldt overal: laatste W weken niet
            tail_ok = np.zeros(n, bool); tail_ok[:max(0, n - W)] = True
            prevf = np.concatenate([[False], isf[:-1]])        # week ervoor flood
            candA = np.where(tail_ok)[0]
            candB1 = np.where(~isd & tail_ok)[0]
            candB2 = np.where(isd & tail_ok)[0]
            candC1 = np.where(~isd & ~prevf & tail_ok)[0]
            candC2 = np.where(isd & ~prevf & tail_ok)[0]
            row = [thr, pname, river, village, len(dend), len(fst), k1, k2, obs]
            if len(dend) == 0 or len(fst) == 0:
                w.writerow(row + [""] * 4 + [len(candA),
                           len(candC1), len(candC2), "niet toetsbaar",
                           round(time.time() - t1, 1)]); f.flush(); done += 1
                print(f"[{done}/{total}] {thr} {pname} {river} {village[:14]} niet toetsbaar", flush=True)
                continue
            sc = []
            if k2 > len(candC2): sc.append(f"C': laag 2 past niet ({k2} > {len(candC2)})")
            if k1 > len(candC1): sc.append(f"C': laag 1 past niet ({k1} > {len(candC1)})")
            if sc:
                w.writerow(row + [""] * 4 + [len(candA),
                           len(candC1), len(candC2), "; ".join(sc),
                           round(time.time() - t1, 1)]); f.flush(); done += 1
                print(f"[{done}/{total}] {thr} {pname} {river} {village[:14]} {'; '.join(sc)}", flush=True)
                continue
            pA, eA = sim_pass(dend, candA, np.empty(0, int), len(fst), 0, NSIM, rng, obs)
            # Niet gerapporteerd, maar deze trekking moet blijven: hij verbruikt
            # hetzelfde deel van de randomstroom als in de productierun van
            # 21 oktober, zodat C' hieronder exact die getallen reproduceert.
            sim_pass(dend, candB1, candB2, k1, k2, NSIM, rng, obs, isd=isd)
            pC, eC = sim_pass(dend, candC1, candC2, k1, k2, NSIM, rng, obs,
                              isd=isd, prevf=prevf, startrule=True)
            w.writerow(row + [round(pA, 5), round(eA, 2),
                              round(pC, 5), round(eC, 2),
                              len(candA), len(candC1), len(candC2),
                              "ok", round(time.time() - t1, 1)])
            f.flush(); done += 1
            el = time.time() - t0
            print(f"[{done}/{total}] {thr} {pname} {river:8} {village[:14]:14} obs={obs:3} "
                  f"pA={pA:.4f} pC'={pC:.4f} expC'={eC:5.1f} "
                  f"({el/60:.1f}m, eta {el/max(1,done-len(done_keys))*(total-done)/60:.0f}m)", flush=True)
f.close()
print("klaar:", OUTCSV)
