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


def SRI_calculate(runoff, reference=None):
    """Tweede definitie uit de bron: week 53 wordt gepoold met week 52.

    reference is de reeks waarop de gammafit per kalenderweek wordt gedaan.
    None betekent fitten op runoff zelf, en dat is de gepubliceerde berekening.
    Een aparte reference maakt een gemeenschappelijk ijkpunt over meerdere
    periodes mogelijk, de route uit D-13. Alleen de fit verschuift, de waardes
    die gestandaardiseerd worden komen in beide gevallen uit runoff.
    """
    fit_source = runoff if reference is None else reference
    grouped = fit_source["dis06"].groupby(fit_source.valid_time.dt.isocalendar().week)
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


def Intensity_calc(SRI, flood_quantiles, threshold, flood_quantile=None):
    """threshold bestuurt de droogtezijde, een droogte is SRI < -threshold.

    flood_quantile is de flooddrempel, uitgedrukt als quantiel van
    flood_quantiles. None betekent norm.cdf(threshold), en dat is de
    gepubliceerde berekening waarin de twee drempels aan elkaar vastzitten. Een
    expliciete waarde maakt ze los. Dat is nodig voor de gevoeligheidsanalyse
    die R4-01 vraagt, want die varieert de SRI-drempel en het floodpercentiel
    als twee onafhankelijke assen. Zie T-10 en D-11.

    Let op: sinds de spiegeling is losgelaten slaat threshold alleen nog op de
    droogtezijde. De naam is niet gewijzigd omdat dat de aanroepende scripts
    breekt.
    """
    threshold_floods = norm.cdf(threshold) if flood_quantile is None else flood_quantile
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


def extract_events(data_array, SRI_Values, quantiles_weekly_max, period_after_event,
                   event_peak_window=None):
    """event_peak_window is het venster waarover quantile_max_value wordt bepaald.

    None betekent gelijk aan period_after_event, en dat is de gepubliceerde
    berekening. Ze zijn losgemaakt omdat period_after_event dubbel werk deed:
    het is het matching-venster van de toets en tegelijk het venster waarover de
    piek na een event wordt gezocht. Zodra het matching-venster een as van de
    gevoeligheidsanalyse wordt, betekent één parameter anders twee dingen.

    Voor de p-waardes maakt dit niets uit, quantile_max_value zit niet in dat
    pad. Voor de copula-kant wel, zie T-11.

    Drie reparaties op 2 september 2026, goedgekeurd door Floris, zie
    CHANGES.md. Deze veranderen cijfers:

    1. end_time. De einddetectie eiste valid_time > starttijd, waardoor bij een
       event van precies een week de eigen index afviel en het einde een week te
       laat lag. Uitputtend aangetoond over alle 1024 patronen van tien weken:
       elk eenweeks event fout, elk langer event goed. Een derde van de droogtes
       duurt een week, en end_time is het matching-anker van de ECA.
    2. duration_weeks. Was de tijdspanne einde min start, dus nul voor een
       eenweeks event, en is nu een telling in weken. Zonder die omzetting zou
       de reparatie van end_time eenweekse droogtes een duur van nul geven, een
       mean_drought_severity van NaN, en daarmee zouden ze uit de copula vallen.
    3. quantile_max_value. Het venster was slice(einde, einde + peak_window],
       aan beide kanten inclusief: vijf weekwaardes waarvan de eerste de laatste
       week van de droogte zelf is. Het manuscript zegt "within four weeks after
       a drought ends" en de matching gebruikt (einde, einde + venster]. Nu doet
       dit veld hetzelfde: strikt na het einde, tot en met venster weken erna.
       Eindigt een event op de laatste week van de reeks, dan is er niets na te
       meten en is de waarde NaN. De copula filtert die er al uit.
    """
    peak_window = period_after_event if event_peak_window is None else event_peak_window
    crossing_indices = np.where(
        (data_array > 0) & (data_array.shift(valid_time=1, fill_value=0) == 0)
    )[0]
    crossing_times = data_array.valid_time.values[crossing_indices]
    start_times, end_times, max_intensities = [], [], []
    durations, drought_peak, quantile_max_value, mean_severity = [], [], [], []
    tijd_as = quantiles_weekly_max["valid_time"]
    for time in crossing_times:
        # >= en niet >: de starweek zelf mag het einde zijn, anders krijgt een
        # event van een week het einde van het eerstvolgende gat erachter
        nz = np.where(
            (data_array.shift(valid_time=-1, fill_value=0) == 0)
            & (data_array.valid_time.values >= time)
        )[0]
        nz = nz[0] if len(nz) > 0 else len(data_array.valid_time) - 1
        event = data_array.sel(
            valid_time=slice(time, data_array.coords["valid_time"].values[nz])
        )
        eind = event.valid_time.values[-1]
        start_times.append(event.valid_time.values[0])
        end_times.append(eind)
        max_intensities.append(event.max().values)
        # telling in weken, niet de tijdspanne: een event van een week duurt 1
        dur = (eind - event.valid_time.values[0]).astype(
            "timedelta64[W]") / np.timedelta64(1, "W") + 1
        durations.append(dur)
        drought_peak.append(
            SRI_Values.sel(
                valid_time=slice(event.valid_time.values[0], eind)
            ).max().values
        )
        # strikt na het einde van het event, zelfde regel als de matching
        na_event = quantiles_weekly_max.where(
            (tijd_as > eind) & (tijd_as <= eind + np.timedelta64(peak_window, "W")),
            drop=True)
        quantile_max_value.append(na_event.max().values if na_event.size else np.nan)
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


def _empty_as_datetime64(values):
    """Bij nul events levert xarray een lege float64-array, en die is niet met een
    datetime64 te vergelijken. Zonder dit valt de precursor-richting om zodra een
    locatie geen enkele droogte heeft, wat gebeurt bij een gemeenschappelijke
    referentie op de Dnieper, zie D-12 en D-13. Alleen de lege array wordt
    omgezet, een gevulde array gaat ongewijzigd door.
    """
    return values.astype("datetime64[ns]") if values.size == 0 else values


def get_matching_pairs_eca(drought_events, flood_events, time_between_events, direction):
    time_delta = np.timedelta64(time_between_events, "W")
    md, mf = [], []
    de = _empty_as_datetime64(drought_events["end_time"].values)
    ds = _empty_as_datetime64(drought_events["start_time"].values)
    fs = _empty_as_datetime64(flood_events["start_time"].values)
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
    # De trekking hieronder is onveranderd gebleven: zelfde rng, zelfde volgorde,
    # zelfde verbruik van de stroom. Alleen het tellen is anders opgeschreven.
    # Was: een Python-lus over de droogtes met een numpy-vergelijking per droogte,
    # dus circa n_simulations maal n_droughts piepkleine aanroepen. Dat was 62
    # procent van de looptijd van een run. Nu: twee searchsorted per simulatie.
    # Het aantal floods in (dt, dt+delta] is het aantal onder de bovengrens min
    # het aantal onder de ondergrens, en dat is een match zodra het groter is
    # dan nul. Bit-identiek aan de oude telling, zie de changelog.
    dt_lo = np.asarray(drought_times.values, dtype="datetime64[ns]")
    dt_hi = dt_lo + np.timedelta64(delta.value, "ns")
    for sim in range(n_simulations):
        rf = np.sort(rng.choice(candidates, size=n_floods, replace=replace))
        match_counts[sim] = np.count_nonzero(
            np.searchsorted(rf, dt_hi, side="right")
            - np.searchsorted(rf, dt_lo, side="right"))
    return float(np.mean(match_counts >= observed_matches)), observed_matches, match_counts


def drought_flood_p_value_trigger_ECA(data, lon, lat, begin, end, time_scale,
                                      threshold, period_after_event,
                                      n_simulations=10000, seed=42,
                                      quantile_reference="daily",
                                      reference_window=None,
                                      flood_quantile=None,
                                      event_peak_window=None):
    """flood_quantile is de flooddrempel als quantiel. None betekent
    norm.cdf(threshold), en dat is de gepubliceerde berekening waarin threshold
    beide drempels bestuurt. Een expliciete waarde maakt de flood- en de
    droogtezijde onafhankelijk, wat de gevoeligheidsanalyse van R4-01 vraagt.
    Zie T-10 en D-11.

    event_peak_window gaat door naar extract_events en scheidt het venster voor
    quantile_max_value van het matching-venster. None betekent gelijk aan
    period_after_event, de gepubliceerde berekening. Raakt de p-waardes niet.

    quantile_reference bepaalt waartegen het weekmaximum als quantiel wordt
    uitgedrukt. "daily" is de gepubliceerde berekening: de ruwe dagelijkse
    verdeling. "weekly_max" is de variant uit P-02, waarbij het weekmaximum
    tegen zijn eigen verdeling gaat, zodat de flooddrempel de droogtedrempel
    spiegelt. Default is en blijft "daily".

    reference_window is (begin, end) van de reeks waartegen beide drempels
    worden geijkt, dus zowel de gammafit van de SRI als de quantielreferentie
    van de flooddrempel. None betekent de periode zelf, en dat is de
    gepubliceerde berekening. Een venster over de volle reeks geeft beide
    periodes hetzelfde ijkpunt, de route uit D-13. De grenzen komen uit het
    aanroepende script, niet uit deze functie."""
    runoff_mean = river_runoff_time_location_mean(data, lon, lat, begin, end, time_scale)
    ref_begin, ref_end = (begin, end) if reference_window is None else reference_window
    same_window = (ref_begin, ref_end) == (begin, end)
    SRI_values = SRI_calculate(runoff_mean, reference=None if same_window else
        river_runoff_time_location_mean(data, lon, lat, ref_begin, ref_end, time_scale))
    runoff_slice_time_location = data.isel(valid_time=slice(ref_begin, ref_end)).sel(
        longitude=lon, latitude=lat)
    runoff_max_weekly = river_runoff_time_location_maximum(
        data, lon, lat, begin, end, time_scale)
    if quantile_reference == "daily":
        reference = runoff_slice_time_location
    elif quantile_reference == "weekly_max":
        reference = runoff_max_weekly if same_window else \
            river_runoff_time_location_maximum(data, lon, lat, ref_begin, ref_end, time_scale)
    else:
        raise ValueError("quantile_reference moet 'daily' of 'weekly_max' zijn")
    quantiles_weekly_max = transform_to_quantiles(runoff_max_weekly, reference)

    intensities = Intensity_calc(SRI_values, quantiles_weekly_max, threshold, flood_quantile)
    flood_events = extract_events(
        intensities["Flood_Intensity"], intensities["SRI"], quantiles_weekly_max,
        period_after_event, event_peak_window)
    drought_events = extract_events(
        intensities["Drought_Intensity"] * -1, intensities["SRI"] * -1,
        quantiles_weekly_max, period_after_event, event_peak_window)

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
    # selectiviteit meelopen, zelfde berekening als scripts/06_threshold_selectivity.py.
    # Nodig voor T-29 en als sanity check op het raster, en hier gratis omdat de
    # drempellogica toch al is toegepast.
    thr_floods = norm.cdf(threshold) if flood_quantile is None else flood_quantile
    pct_flood = 100 * float(np.mean(quantiles_weekly_max.values > thr_floods))
    pct_drought = 100 * float(np.nanmean(SRI_values.values < -threshold))
    return {
        # counts_mc is de volle nulverdeling, nodig om over locaties te poolen tot
        # één aggregatieve toets, zie Donges et al. 2016 sectie 2.2 en T-10
        "mc_null_counts": counts_mc,
        "p_mc_trigger": p_mc, "observed_matches": obs_mc,
        "drought_count": trig["drought_count"], "flood_count": trig["flood_count"],
        "p_trigger": trig["p_value"], "match_count_trigger": trig["drought_flood_count"],
        "p_precursor": prec["p_value"], "match_count_precursor": prec["drought_flood_count"],
        "pct_weeks_flood": pct_flood, "pct_weeks_drought": pct_drought,
        "n_weeks": timespan,
    }
