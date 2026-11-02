"""Kengetallen van de eventdefinitie voor de methodensectie, bij een opgegeven drempel.

Besluit Floris 30 oktober 2026: de hoofdanalyse van de ECA gaat naar SRI < -1 met
het gespiegelde floodniveau norm.cdf(1) = 0,841. De zinnen in 2.3 en 2.4.1 die
cijfers over de definitie dragen (selectiviteit van de drempels, overlap van
droogte- en floodweken, kans op een floodstart in een droogteweek tegen een
niet-droogteweek, aantal droogtes per cel, aandeel matches op lag 1) moeten
daarvoor opnieuw. Dit script berekent ze deterministisch uit de data, zonder
Monte Carlo, over alle 48 locaties en beide periodes.

  THRESHOLD=1.0 uv run --frozen python scripts/46_definition_stats.py
  THRESHOLD=0.5 uv run --frozen python scripts/46_definition_stats.py   (ter vergelijking)

Uitvoer in results/2026-10-30_definition_stats/: stats_thr<threshold>.csv per
locatie-periode en summary_thr<threshold>.md met de getallen voor de tekst.
"""
import sys, os, json, re, ast, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
from scipy.stats import norm
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-10-30_definition_stats"
THRESHOLD = float(os.environ.get("THRESHOLD", 1.0))
FLOOD_Q = float(norm.cdf(THRESHOLD))
W = 4
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))


def main():
    os.makedirs(OUT, exist_ok=True)
    d = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["latitude"], l["longitude"]) for r in rivers for l in r["locations"]]
    rows = []
    for pname, (b, e) in PERIODS:
        for river, village, lat, lon in locs:
            nlon, nlat = find_nearest_grid_point(d, lon, lat)
            mean_ = river_runoff_time_location_mean(d, nlon, nlat, b, e, "1W")
            sri = SRI_calculate(mean_)
            raw = d.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
            wmax = river_runoff_time_location_maximum(d, nlon, nlat, b, e, "1W")
            q = transform_to_quantiles(wmax, raw)
            weeks = mean_.valid_time.values.astype("datetime64[ns]")
            inten = Intensity_calc(sri, q, THRESHOLD, FLOOD_Q)
            fl = extract_events(inten["Flood_Intensity"], inten["SRI"], q, W)
            dr = extract_events(inten["Drought_Intensity"] * -1, inten["SRI"] * -1, q, W)
            isd = np.nan_to_num(sri.values < -THRESHOLD).astype(bool)
            isf = (q.values > FLOOD_Q)
            fst = np.searchsorted(weeks, np.asarray(fl["start_time"].values, dtype="datetime64[ns]"))
            dend = np.searchsorted(weeks, np.asarray(dr["end_time"].values, dtype="datetime64[ns]"))
            is_start = np.zeros(len(weeks), bool); is_start[fst] = True
            # matches en hun lag (eerste floodstart in (end, end+W])
            lags = []
            fs = np.sort(fst)
            for de in dend:
                i = np.searchsorted(fs, de, side="right")
                if i < len(fs) and fs[i] <= de + W:
                    lags.append(int(fs[i] - de))
            n = len(weeks); nd = int(isd.sum()); nf = int(isf.sum())
            rows.append({"period": pname, "river": river, "village": village, "n_weeks": n,
                         "n_droughts": len(dend), "n_flood_starts": len(fst),
                         "pct_weeks_drought": 100 * nd / n, "pct_weeks_flood": 100 * nf / n,
                         "pct_drought_weeks_also_flood": 100 * float((isd & isf).sum()) / max(nd, 1),
                         "p_start_given_drought_week": float(is_start[isd].mean()) if nd else np.nan,
                         "p_start_given_nondrought_week": float(is_start[~isd].mean()),
                         "p_flood_given_drought_week": float(isf[isd].mean()) if nd else np.nan,
                         "p_flood_given_nondrought_week": float(isf[~isd].mean()),
                         "matches": len(lags), "matches_lag1": int(sum(l == 1 for l in lags)),
                         "drought_duration_median": float(np.median(dr["duration_weeks"].values)) if len(dend) else np.nan,
                         "drought_one_week_share": float(np.mean(dr["duration_weeks"].values == 1)) if len(dend) else np.nan})
    t = pd.DataFrame(rows)
    tag = f"thr{THRESHOLD:g}"
    t.to_csv(f"{OUT}/stats_{tag}.csv", index=False)
    tot_d = (t.pct_weeks_drought * t.n_weeks).sum() / t.n_weeks.sum()
    tot_f = (t.pct_weeks_flood * t.n_weeks).sum() / t.n_weeks.sum()
    nd_w = (t.pct_weeks_drought / 100 * t.n_weeks)
    ov = (t.pct_drought_weeks_also_flood / 100 * nd_w).sum() / nd_w.sum() * 100
    pfd = (t.p_flood_given_drought_week * nd_w).sum() / nd_w.sum()
    nn_w = t.n_weeks - nd_w
    pfn = (t.p_flood_given_nondrought_week * nn_w).sum() / nn_w.sum()
    psd = (t.p_start_given_drought_week * nd_w).sum() / nd_w.sum()
    psn = (t.p_start_given_nondrought_week * nn_w).sum() / nn_w.sum()
    S = [f"# Kengetallen eventdefinitie, SRI < -{THRESHOLD:g}, floodniveau {FLOOD_Q:.4f}, venster {W} weken",
         "", f"- weken onder de droogtedrempel: {tot_d:.1f}% (bereik per cel {t.pct_weeks_drought.min():.1f} tot {t.pct_weeks_drought.max():.1f}); symmetrie zou {100*(1-FLOOD_Q):.1f}% geven",
         f"- weken boven de flooddrempel: {tot_f:.1f}% (bereik {t.pct_weeks_flood.min():.1f} tot {t.pct_weeks_flood.max():.1f})",
         f"- droogteweken die tegelijk floodweek zijn: {ov:.2f}% van de droogteweken",
         f"- kans dat een week een floodweek is: {pfd:.3f} in een droogteweek, {pfn:.3f} in een niet-droogteweek",
         f"- kans dat een week een floodstart is: {psd:.4f} in een droogteweek, {psn:.4f} in een niet-droogteweek",
         f"- droogtes per cel: mediaan {t.n_droughts.median():.0f} (bereik {t.n_droughts.min()} tot {t.n_droughts.max()}); floodstarts mediaan {t.n_flood_starts.median():.0f}",
         f"- duur van droogtes: mediaan van de celmedianen {t.drought_duration_median.median():.0f} weken; aandeel eenweeks mediaan {t.drought_one_week_share.median():.2f}",
         f"- matches totaal {int(t.matches.sum())}, waarvan op lag 1: {100*t.matches_lag1.sum()/max(t.matches.sum(),1):.0f}%",
         f"- cellen met minder dan 15 droogtes: {int((t.n_droughts < 15).sum())} van 96; met 0 droogtes: {int((t.n_droughts == 0).sum())}"]
    open(f"{OUT}/summary_{tag}.md", "w").write("\n".join(S) + "\n")
    print("\n".join(S))


if __name__ == "__main__":
    main()
