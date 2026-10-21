"""Sluit de seizoensverklaring uit, of bevestigt hem.

Het alternatief voor de bevinding uit script 04: als droogtes vooral in de zomer
eindigen en zomerse floods nu eenmaal kleiner zijn dan de smeltwaterpieken in het
voorjaar, ontstaat het gevonden patroon zonder causaal verband.

Twee dingen anders dan in script 04:

1. Seizoen van het flood-event wordt vastgelegd, en de groottebins worden binnen
   locatie EN seizoen bepaald. "Kleine flood" betekent dan klein voor dat
   seizoen, niet klein omdat het zomer is.

2. De toevalskans wordt seizoensspecifiek en empirisch bepaald, niet met de
   binomiale formule. Per locatie en seizoen: welk deel van ALLE weken in dat
   seizoen is voorafgegaan door een droogte-einde binnen 4 weken? Dat is de
   juiste nullijn, want die neemt de seizoensclustering van droogtes mee.

Onderzoek, geen wijziging aan de pipeline.
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-08-24_season_control"
DT = 4
SEASON = {12:"DJF",1:"DJF",2:"DJF",3:"MAM",4:"MAM",5:"MAM",
          6:"JJA",7:"JJA",8:"JJA",9:"SON",10:"SON",11:"SON"}
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

ff = open(f"{OUT}/floods.csv", "w", newline=""); wf = csv.writer(ff)
wf.writerow(["period","river","village","month","season","peak_quantile",
             "max_intensity","preceded_by_drought","null_rate_season"])
fd = open(f"{OUT}/drought_ends.csv", "w", newline=""); wd = csv.writer(fd)
wd.writerow(["period","river","village","month","season"])

t0 = time.time(); n = 0
for pname, (b, e) in (("first", (0, 5479)), ("second", (5480, 10958))):
    for river, village, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_ = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_)
        raw = data.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
        mx = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(mx, raw)
        it = Intensity_calc(sri, q, 1)
        fl = extract_events(it["Flood_Intensity"], it["SRI"], q, DT)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)

        d_end = pd.to_datetime(dr["end_time"].values)
        delta = pd.Timedelta(weeks=DT)
        for t in d_end:
            wd.writerow([pname, river, village, t.month, SEASON[t.month]])

        # seizoensspecifieke nullijn: over ALLE weken, niet alleen floodweken
        weeks = pd.to_datetime(q["valid_time"].values)
        prec_all = np.array([bool(np.any((d_end < w) & (d_end >= w - delta))) for w in weeks])
        seas_all = np.array([SEASON[w.month] for w in weeks])
        null = {s: float(prec_all[seas_all == s].mean()) for s in set(seas_all)}

        for i in range(len(fl["start_time"].values)):
            fs = pd.Timestamp(fl["start_time"].values[i])
            fe = pd.Timestamp(fl["end_time"].values[i])
            s = SEASON[fs.month]
            wf.writerow([pname, river, village, fs.month, s,
                         round(float(q.sel(valid_time=slice(fs, fe)).max().values), 6),
                         round(float(fl["max_intensity"].values[i]), 6),
                         int(bool(np.any((d_end < fs) & (d_end >= fs - delta)))),
                         round(null.get(s, float("nan")), 6)])
        ff.flush(); fd.flush(); n += 1
        el = time.time()-t0
        print(f"[{n}/96] {pname:6} {river:8} {village[:20]:20} "
              f"({el/60:.1f}m, eta {el/n*(96-n)/60:.0f}m)", flush=True)
ff.close(); fd.close()
print("klaar")
