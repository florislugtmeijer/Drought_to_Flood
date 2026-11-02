"""Strikte definities, diagnose: in welke toestand zit de rivier na afloop van een droogte?

De strikte variant (droogte bij SRI < -1) laat het venster na een droogte droger
uitkomen dan een willekeurig venster, terwijl dat bij 0,5 natter is. Hypothese: het
einde van een strenge droogte is het moment dat de SRI weer boven -1 komt, en dan
zit de rivier vaak nog in een milde droogte tussen -1 en -0,5. Het "venster na de
droogte" valt dan nog binnen droge omstandigheden.

Dit script meet dat direct, voor beide varianten: per droogte-event de gemiddelde
SRI over de vier weken na afloop, en het aandeel van die weken met SRI < -0,5.
Daarnaast dezelfde twee getallen over alle weken, als referentie.

Geen bestaande code aangepast. Uitvoer: post_drought_sri.csv in de map van
scripts/27, als aanvullende diagnose.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --no-project python scripts/30_strict_post_drought_state.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-04_strict_definition_points"
DT = 4
VARIANTS = {"referentie_0.5": 0.5, "strikt_1.0": 1.0}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}

data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

f = open(f"{OUT}/post_drought_sri.csv", "w", newline=""); w = csv.writer(f)
w.writerow(["variant", "threshold", "river", "village", "period", "n_events",
            "mean_sri_after_events", "share_weeks_below_m05_after_events",
            "share_weeks_below_m1_after_events",
            "mean_sri_all_weeks", "share_weeks_below_m05_all"])
t0 = time.time(); done = 0
for pname, (b, e) in PERIODS.items():
    for river, village, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mean_w)
        max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(max_w, mean_w)
        s = np.asarray(sri.values, float)
        tijd = sri["valid_time"].values
        alle_ok = np.isfinite(s)
        for vname, thr in VARIANTS.items():
            it = Intensity_calc(sri, q, thr)
            dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
            vals = []
            for end in dr["end_time"].values:
                i = int(np.searchsorted(tijd, end))
                seg = s[i + 1:i + 1 + DT]
                seg = seg[np.isfinite(seg)]
                if len(seg):
                    vals.append(seg)
            if vals:
                allv = np.concatenate(vals)
                w.writerow([vname, thr, river, village, pname, len(vals),
                            round(float(allv.mean()), 4),
                            round(float(np.mean(allv < -0.5)), 4),
                            round(float(np.mean(allv < -1.0)), 4),
                            round(float(s[alle_ok].mean()), 4),
                            round(float(np.mean(s[alle_ok] < -0.5)), 4)])
        f.flush(); done += 1
        print(f"[{done}/96] {time.time()-t0:6.1f}s", flush=True)
f.close()
print(f"klaar in {time.time()-t0:.1f}s, uitvoer in {OUT}/post_drought_sri.csv", flush=True)
