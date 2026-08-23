"""Diagnose per locatie: haalt de SRI het verwachte aandeel droogteweken?

Bij een correct gestandaardiseerde SRI hoort ongeveer 15,9 procent van de weken
onder SRI < -1 te liggen, want norm.cdf(-1) = 0,1587. Waar dat sterk afwijkt is
de onderkant van de afvoerverdeling samengedrukt, wat op regulering kan wijzen.
Relevant voor R4-02 en R4-05.
"""
import sys, os, json, re, ast, csv, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import xarray as xr, numpy as np
from dtf.pipeline import find_nearest_grid_point, river_runoff_time_location_mean, SRI_calculate

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-08-23_sri_diagnostic"
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))

f = open(f"{OUT}/sri_diagnostic.csv", "w", newline="")
w = csv.writer(f); w.writerow(["river","village","pct_weeks_sri_below_-1","sri_median",
                               "sri_sd","min_over_median","p5_over_median"])
for r in rivers:
    for l in r["locations"]:
        nlon, nlat = find_nearest_grid_point(data, l["longitude"], l["latitude"])
        m = river_runoff_time_location_mean(data, nlon, nlat, 0, 5479, "1W")
        q = m["dis06"].values; sri = SRI_calculate(m).values
        row = [r["river"], l["village"], round(100*float(np.nanmean(sri < -1)), 2),
               round(float(np.nanmedian(sri)), 4), round(float(np.nanstd(sri)), 4),
               round(float(np.nanmin(q)/np.nanmedian(q)), 3),
               round(float(np.nanpercentile(q, 5)/np.nanmedian(q)), 3)]
        w.writerow(row); f.flush()
        print(row, flush=True)
f.close()
print("klaar")
