"""Draait de ECA voor alle 48 locaties, beide periodes, threshold 1 en 0,5.

threshold=1   : wat de gepubliceerde Tabel 3 heeft gemaakt (geverifieerd)
threshold=0.5 : wat de methodensectie van het manuscript beschrijft (D-01)

Schrijft incrementeel naar results/, zodat een halve run bruikbaar is.
"""
import sys, os, json, re, ast, time, warnings, csv
sys.path.insert(0, "src")
warnings.filterwarnings("ignore")
import xarray as xr
from dtf.pipeline import find_nearest_grid_point, drought_flood_p_value_trigger_ECA

NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
OUT = "results/2026-08-23_threshold_comparison"
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
THRESHOLDS = [1, 0.5]

os.makedirs(OUT, exist_ok=True)
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
path = f"{OUT}/eca_results.csv"
cols = ["threshold","period","river","village","river_location","nearest_lat","nearest_lon",
        "drought_count","flood_count","match_count_trigger","match_count_precursor",
        "observed_matches_mc","p_trigger","p_precursor","p_mc_trigger"]
f = open(path, "w", newline=""); w = csv.DictWriter(f, cols); w.writeheader()

t_start = time.time(); n = 0; total = len(THRESHOLDS)*len(PERIODS)*len(locs)
for thr in THRESHOLDS:
    for pname, (b, e) in PERIODS.items():
        for river, village, rloc, lat, lon in locs:
            nlon, nlat = find_nearest_grid_point(data, lon, lat)
            n += 1
            try:
                r = drought_flood_p_value_trigger_ECA(
                    data, nlon, nlat, b, e, "1W", threshold=thr,
                    period_after_event=4, n_simulations=10000, seed=42)
            except Exception as exc:
                print(f"[{n}/{total}] FOUT {river}/{village} thr={thr} {pname}: {exc}", flush=True)
                continue
            w.writerow({"threshold": thr, "period": pname, "river": river, "village": village,
                        "river_location": rloc, "nearest_lat": nlat, "nearest_lon": nlon,
                        "drought_count": r["drought_count"], "flood_count": r["flood_count"],
                        "match_count_trigger": r["match_count_trigger"],
                        "match_count_precursor": r["match_count_precursor"],
                        "observed_matches_mc": r["observed_matches"],
                        "p_trigger": r["p_trigger"], "p_precursor": r["p_precursor"],
                        "p_mc_trigger": r["p_mc_trigger"]})
            f.flush()
            el = time.time()-t_start
            print(f"[{n}/{total}] thr={thr} {pname:6} {river:8} {village[:20]:20} "
                  f"p_trig={r['p_trigger']:.4f} p_mc={r['p_mc_trigger']:.4f} "
                  f"({el/60:.1f}m, eta {el/n*(total-n)/60:.0f}m)", flush=True)
f.close()
print(f"\nklaar in {(time.time()-t_start)/60:.1f} minuten -> {path}")
