"""Getrouwe port van de structured Colab-versie (working_drought_to_flood_europe_(structured).py).

Doel: de gepubliceerde cijfers reproduceren. Nog geen opschoning, geen
parametrisering, geen reparaties. Afwijkingen van de bron zijn gemarkeerd met
PORT: en veranderen het gedrag niet.
"""
import numpy as np
import pandas as pd
import xarray as xr
from scipy.stats import gamma, norm, binom


def find_nearest_grid_point(ds, lon, lat):
    distances = (ds.longitude - lon) ** 2 + (ds.latitude - lat) ** 2
    nearest_idx = distances.argmin().item()
    return ds.longitude[nearest_idx].item(), ds.latitude[nearest_idx].item()


def empirical_cdf(data, x):
    data_sorted = np.sort(data)
    return np.searchsorted(data_sorted, x, side="right") / len(data_sorted)


def river_runoff_time_location_mean(data, lon, lat, begin, end, time_scale):
    s = data.isel(valid_time=slice(begin, end)).sel(longitude=lon, latitude=lat)
    return s.resample(valid_time=time_scale).mean(dim="valid_time")


def river_runoff_time_location_maximum(data, lon, lat, begin, end, time_scale):
    s = data.isel(valid_time=slice(begin, end)).sel(longitude=lon, latitude=lat)
    return s.resample(valid_time=time_scale).max(dim="valid_time", skipna=True)


def SRI_calculate(runoff):
    """Tweede definitie uit de bron: week 53 wordt gepoold met week 52."""
    grouped = runoff["dis06"].groupby(runoff.valid_time.dt.isocalendar().week)
    out = runoff["dis06"].copy()
    for k in range(len(runoff["dis06"])):
        week = int(runoff.valid_time[k].dt.isocalendar().week.item())
        if week == 53:
            w52 = np.array(grouped[52])
            w53 = np.array(grouped[53]) if 53 in grouped.groups else np.array([])
            week_data = np.concatenate([w52, w53])
        else:
            week_data = np.array(grouped[week])
        week_data = week_data[np.isfinite(week_data)]
        week_data = week_data[week_data > 0]
        if len(week_data) < 5:
            out[k] = np.nan
            continue
        shape, loc, scale = gamma.fit(week_data, floc=0)
        cdf = gamma.cdf(runoff["dis06"][k], a=shape, loc=loc, scale=scale)
        out[k] = norm.ppf(np.clip(cdf, 1e-6, 1 - 1e-6))
    return out


def transform_to_quantiles(runoff_slice_max, runoff_slice_full):
    ref = runoff_slice_full["dis06"].values.flatten()
    ref = ref[~np.isnan(ref)]
    target = runoff_slice_max["dis06"].values
    # PORT: np.vectorize vervangen door searchsorted, zelfde uitkomst maar sneller
    ref_sorted = np.sort(ref)
    q = np.searchsorted(ref_sorted, target, side="right") / len(ref_sorted)
    return xr.DataArray(
        q,
        dims=runoff_slice_max["dis06"].dims,
        coords=runoff_slice_max["dis06"].coords,
        name="quantile_dis06",
    )


def Intensity_calc(SRI, flood_quantiles, threshold):
    threshold_floods = norm.cdf(threshold)
    area = xr.DataArray(np.zeros_like(SRI), coords=SRI.coords)
    for t in range(flood_quantiles.size):
        if flood_quantiles[t] > threshold_floods:
            area[t] = flood_quantiles[t] - threshold_floods
        else:
            area[t] = 0
        if t > 0 and flood_quantiles[t] > threshold_floods and area[t - 1] > 0:
            area[t] = area[t - 1] + flood_quantiles[t] - threshold_floods
    SRI = SRI.to_dataset(name="SRI") if not hasattr(SRI, "data_vars") else SRI
    SRI["Flood_Intensity"] = area

    thr = -1 * threshold
    area = xr.DataArray(np.zeros_like(SRI["SRI"]), coords=SRI["SRI"].coords)
    sri = SRI["SRI"]
    for t in range(sri.size):
        if sri[t] < thr:
            area[t] = sri[t] - thr
        else:
            area[t] = 0
        if t > 0 and sri[t] < thr and area[t - 1] < 0:
            area[t] = area[t - 1] + sri[t] - thr
    SRI["Drought_Intensity"] = area
    return SRI


def extract_events(data_array, SRI_Values, quantiles_weekly_max, period_after_event):
    crossing_indices = np.where(
        (data_array > 0) & (data_array.shift(valid_time=1, fill_value=0) == 0)
    )[0]
    crossing_times = data_array.valid_time.values[crossing_indices]
    start_times, end_times, max_intensities = [], [], []
    durations, drought_peak, quantile_max_value, mean_severity = [], [], [], []
    for time in crossing_times:
        nz = np.where(
            (data_array.shift(valid_time=-1, fill_value=0) == 0)
            & (data_array.valid_time.values > time)
        )[0]
        nz = nz[0] if len(nz) > 0 else len(data_array.valid_time) - 1
        event = data_array.sel(
            valid_time=slice(time, data_array.coords["valid_time"].values[nz])
        )
        start_times.append(event.valid_time.values[0])
        end_times.append(event.valid_time.values[-1])
        max_intensities.append(event.max().values)
        dur = (
            event.valid_time.values[-1] - event.valid_time.values[0]
        ).astype("timedelta64[W]") / np.timedelta64(1, "W")
        durations.append(dur)
        drought_peak.append(
            SRI_Values.sel(
                valid_time=slice(event.valid_time.values[0], event.valid_time.values[-1])
            ).max().values
        )
        quantile_max_value.append(
            quantiles_weekly_max.sel(
                valid_time=slice(
                    event.valid_time.values[-1],
                    event.valid_time.values[-1] + np.timedelta64(period_after_event, "W"),
                )
            ).max().values
        )
        mean_severity.append(float(event.max().values) / float(dur) if dur else np.nan)
    return xr.Dataset(
        {
            "start_time": ("event", start_times),
            "end_time": ("event", end_times),
            "max_intensity": ("event", max_intensities),
            "duration_weeks": ("event", durations),
            "drought_peak": ("event", drought_peak),
            "quantile_max_value": ("event", quantile_max_value),
            "mean_drought_severity": ("event", mean_severity),
        },
        coords={"event": range(len(start_times))},
    )


def get_matching_pairs_eca(drought_events, flood_events, time_between_events, direction):
    time_delta = np.timedelta64(time_between_events, "W")
    md, mf = [], []
    de = drought_events["end_time"].values
    ds = drought_events["start_time"].values
    fs = flood_events["start_time"].values
    if direction == "trigger":
        for i, d_end in enumerate(de):
            valid = fs[(fs > d_end) & (fs <= d_end + time_delta)]
            if len(valid) > 0:
                md.append(ds[i]); mf.append(valid[0])
    elif direction == "precursor":
        for f_start in fs:
            valid = de[(de < f_start) & (de >= f_start - time_delta)]
            if len(valid) > 0:
                mf.append(f_start); md.append(valid[0])
    else:
        raise ValueError("Invalid direction")
    return xr.Dataset({
        "start_time_drought": (["event"], np.array(md)),
        "start_time_flood": (["event"], np.array(mf)),
    })


def eca_p_value(drought_events, flood_events, total_weeks, period_after_event, direction):
    drought_count = len(drought_events["start_time"].values)
    flood_count = len(flood_events["start_time"].values)
    pairs = get_matching_pairs_eca(drought_events, flood_events, period_after_event, direction)
    match_count = pairs.sizes["event"]
    p_single = period_after_event / total_weeks
    if direction == "trigger":
        trials, opposite_count = drought_count, flood_count
    else:
        trials, opposite_count = flood_count, drought_count
    p_at_least_one = 1 - (1 - p_single) ** opposite_count
    p_value = binom.sf(match_count - 1, trials, p_at_least_one)
    return {"p_value": p_value, "drought_count": drought_count,
            "flood_count": flood_count, "drought_flood_count": match_count}


def monte_carlo_p_value(drought_events, flood_events, period_after_event,
                        candidate_times, n_simulations, observed_matches,
                        seed=42, use_drought_end=True, replace_if_needed=True):
    rng = np.random.default_rng(seed)
    delta = pd.Timedelta(weeks=period_after_event)
    candidate_times = pd.to_datetime(candidate_times)
    time_min, time_max = candidate_times.min(), candidate_times.max() - delta
    candidates = np.array(pd.to_datetime(
        candidate_times[(candidate_times >= time_min) & (candidate_times <= time_max)]))
    n_floods = len(flood_events["start_time"].values)
    if len(candidates) == 0:
        raise ValueError("No valid candidate times")
    replace = n_floods > len(candidates) and replace_if_needed
    key = "end_time" if use_drought_end else "start_time"
    drought_times = pd.to_datetime(drought_events[key].values)
    match_counts = np.empty(n_simulations, dtype=int)
    for sim in range(n_simulations):
        rf = rng.choice(candidates, size=n_floods, replace=replace)
        match_counts[sim] = sum(
            1 for dt in drought_times if np.any((rf > dt) & (rf <= dt + delta)))
    return float(np.mean(match_counts >= observed_matches)), observed_matches, match_counts


def drought_flood_p_value_trigger_ECA(data, lon, lat, begin, end, time_scale,
                                      threshold, period_after_event,
                                      n_simulations=10000, seed=42,
                                      quantile_reference="daily"):
    """quantile_reference bepaalt waartegen het weekmaximum als quantiel wordt
    uitgedrukt. "daily" is de gepubliceerde berekening: de ruwe dagelijkse
    verdeling. "weekly_max" is de variant uit P-02, waarbij het weekmaximum
    tegen zijn eigen verdeling gaat, zodat de flooddrempel de droogtedrempel
    spiegelt. Default is en blijft "daily"."""
    runoff_mean = river_runoff_time_location_mean(data, lon, lat, begin, end, time_scale)
    SRI_values = SRI_calculate(runoff_mean)
    runoff_slice_time_location = data.isel(valid_time=slice(begin, end)).sel(
        longitude=lon, latitude=lat)
    runoff_max_weekly = river_runoff_time_location_maximum(
        data, lon, lat, begin, end, time_scale)
    if quantile_reference == "daily":
        reference = runoff_slice_time_location
    elif quantile_reference == "weekly_max":
        reference = runoff_max_weekly
    else:
        raise ValueError("quantile_reference moet 'daily' of 'weekly_max' zijn")
    quantiles_weekly_max = transform_to_quantiles(runoff_max_weekly, reference)

    intensities = Intensity_calc(SRI_values, quantiles_weekly_max, threshold)
    flood_events = extract_events(
        intensities["Flood_Intensity"], intensities["SRI"], quantiles_weekly_max, period_after_event)
    drought_events = extract_events(
        intensities["Drought_Intensity"] * -1, intensities["SRI"] * -1,
        quantiles_weekly_max, period_after_event)

    # observed matches: vanaf het EINDE van de droogte, strikt groter dan 0
    drought_df = drought_events[["end_time"]].to_dataframe().reset_index().sort_values("end_time")
    flood_df = flood_events[["start_time"]].to_dataframe().reset_index().sort_values("start_time")
    window = pd.Timedelta(weeks=period_after_event)
    observed = 0
    for _, d in drought_df.iterrows():
        for _, f in flood_df.iterrows():
            if pd.Timedelta(0) < f["start_time"] - d["end_time"] <= window:
                observed += 1
                break

    p_mc, obs_mc, counts_mc = monte_carlo_p_value(
        drought_events, flood_events, period_after_event,
        runoff_mean["valid_time"].values, n_simulations, observed, seed=seed)

    timespan = len(intensities["Drought_Intensity"]["valid_time"])
    trig = eca_p_value(drought_events, flood_events, timespan, period_after_event, "trigger")
    prec = eca_p_value(drought_events, flood_events, timespan, period_after_event, "precursor")
    return {
        "p_mc_trigger": p_mc, "observed_matches": obs_mc,
        "drought_count": trig["drought_count"], "flood_count": trig["flood_count"],
        "p_trigger": trig["p_value"], "match_count_trigger": trig["drought_flood_count"],
        "p_precursor": prec["p_value"], "match_count_precursor": prec["drought_flood_count"],
    }
