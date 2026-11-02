"""Meet hoe selectief de drempels feitelijk zijn, voor T-29 punt 3.

Per locatie en periode: welk aandeel van de weken ligt boven de flooddrempel en
welk aandeel onder de droogtedrempel, bij threshold 0,5 en 1. Nodig omdat de
methodensectie moet melden wat de drempels werkelijk selecteren, nu vaststaat
dat er geen sprake is van mirroring.
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy.stats import norm
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
OUT = "results/2026-09-01_threshold_selectivity"; os.makedirs(OUT, exist_ok=True)
data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(
    open("notebooks/drought_to_flood_europe_r1_published.ipynb"))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))

f = open(f"{OUT}/selectivity.csv", "w", newline=""); w = csv.writer(f)
w.writerow(["period","river","village","threshold","pct_weeks_flood","pct_weeks_drought"])
t0=time.time(); n=0
for pname,(b,e) in (("first",(0,5479)),("second",(5480,10958))):
    for r in rivers:
        for l in r["locations"]:
            nlon,nlat = find_nearest_grid_point(data, l["longitude"], l["latitude"])
            mean_ = river_runoff_time_location_mean(data,nlon,nlat,b,e,"1W")
            raw = data.isel(valid_time=slice(b,e)).sel(longitude=nlon,latitude=nlat)
            q = transform_to_quantiles(river_runoff_time_location_maximum(
                    data,nlon,nlat,b,e,"1W"), raw).values
            sri = SRI_calculate(mean_).values
            for t in (0.5, 1.0):
                w.writerow([pname, r["river"], l["village"], t,
                            round(100*float(np.mean(q > norm.cdf(t))), 2),
                            round(100*float(np.nanmean(sri < -t)), 2)])
            f.flush(); n+=1
            print(f"[{n}/96] {pname} {r['river']} {l['village'][:18]} ({(time.time()-t0)/60:.1f}m)", flush=True)
f.close(); print("klaar")
