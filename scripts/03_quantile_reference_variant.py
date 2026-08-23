"""Onderzoekt P-02: wat doet het spiegelen van de flooddrempel met de resultaten?

Draait alle 48 locaties maal 2 periodes met threshold=1, één keer met de
gepubliceerde referentie (ruwe dagwaardes) en één keer met de variant
(weekmaxima tegen hun eigen verdeling).

Dit is onderzoek, geen wijziging. De default in src/dtf/pipeline.py blijft
"daily".
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import xarray as xr
from dtf.pipeline import find_nearest_grid_point, drought_flood_p_value_trigger_ECA

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-08-23_quantile_reference_variant"
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

f = open(f"{OUT}/variant_results.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["quantile_reference","period","river","village","river_location",
            "drought_count","flood_count","match_count_trigger","observed_matches_mc",
            "p_trigger","p_precursor","p_mc_trigger"])
t0 = time.time(); n = 0; total = 2*2*len(locs)
for ref in ("weekly_max",):          # daily staat al in de threshold-run
    for pname, (b, e) in (("first", (0, 5479)), ("second", (5480, 10958))):
        for river, village, rloc, lat, lon in locs:
            nlon, nlat = find_nearest_grid_point(data, lon, lat)
            n += 1
            r = drought_flood_p_value_trigger_ECA(
                data, nlon, nlat, b, e, "1W", threshold=1, period_after_event=4,
                n_simulations=10000, seed=42, quantile_reference=ref)
            w.writerow([ref, pname, river, village, rloc, r["drought_count"],
                        r["flood_count"], r["match_count_trigger"], r["observed_matches"],
                        r["p_trigger"], r["p_precursor"], r["p_mc_trigger"]])
            f.flush()
            el = time.time()-t0
            print(f"[{n}/96] {pname:6} {river:8} {village[:20]:20} "
                  f"fl={r['flood_count']:3} p_mc={r['p_mc_trigger']:.4f} "
                  f"({el/60:.1f}m, eta {el/n*(96-n)/60:.0f}m)", flush=True)
f.close()
print(f"klaar in {(time.time()-t0)/60:.1f} minuten")
