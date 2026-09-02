"""Toetst de hypothese onder het P-02 effect.

Hypothese: de samenhang tussen droogte en flood zit vooral in de middenband van
floodgroottes, niet in de extremen. Als dat klopt verklaart het waarom een
strengere flooddrempel (P-02) het signaal wegneemt: die gooit juist de
droogte-gerelateerde floods weg.

Opzet: per flood-event vaststellen of er binnen `period_after_event` weken
ervoor een droogte eindigde (de precursor-richting, gelijk aan
get_matching_pairs_eca). De toevalskans daarop is per locatie constant,
1 - (1 - dT/W)^n_droogtes, en dus vlak over alle floodgroottes. Neemt het
overschot boven toeval af met de grootte, dan is de hypothese ondersteund.

Grootte van een flood: het piekquantiel tijdens het event, en apart de
max_intensity (cumulatieve overschrijding). Binnen elke locatie omgezet naar een
percentielrang, zodat locaties vergelijkbaar zijn.

Onderzoek, geen wijziging aan de pipeline.
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-08-23_flood_magnitude_test"
DT = 4
os.makedirs(OUT, exist_ok=True)

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

f = open(f"{OUT}/floods.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["period","river","village","flood_idx","peak_quantile","max_intensity",
            "preceded_by_drought","n_droughts","n_floods","weeks","p_chance"])
t0 = time.time(); n = 0
for pname, (b, e) in (("first", (0, 5479)), ("second", (5480, 10958))):
    for river, village, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_ = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_)
        raw = data.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
        mx = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(mx, raw)                      # gepubliceerde referentie
        it = Intensity_calc(sri, q, 1)
        fl = extract_events(it["Flood_Intensity"], it["SRI"], q, DT)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
        weeks = len(it["Drought_Intensity"]["valid_time"])
        d_end = pd.to_datetime(dr["end_time"].values)
        delta = pd.Timedelta(weeks=DT)
        nd, nf = len(d_end), len(fl["start_time"].values)
        p_chance = 1 - (1 - DT/weeks) ** nd
        for i in range(nf):
            fs = pd.Timestamp(fl["start_time"].values[i])
            fe = pd.Timestamp(fl["end_time"].values[i])
            preceded = bool(np.any((d_end < fs) & (d_end >= fs - delta)))
            peak = float(q.sel(valid_time=slice(fs, fe)).max().values)
            w.writerow([pname, river, village, i, round(peak, 6),
                        round(float(fl["max_intensity"].values[i]), 6),
                        int(preceded), nd, nf, weeks, round(p_chance, 6)])
        f.flush(); n += 1
        el = time.time()-t0
        print(f"[{n}/96] {pname:6} {river:8} {village[:20]:20} floods={nf:3} "
              f"droogtes={nd:3} ({el/60:.1f}m, eta {el/n*(96-n)/60:.0f}m)", flush=True)
f.close()
print("klaar")
