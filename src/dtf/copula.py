"""Copula-kant van de drought-to-flood analyse.

Port van cel 25 van notebooks/drought_to_flood_europe_r1_published.ipynb, plus
calculate_rolling_max uit cel 12. Doel is hetzelfde als bij pipeline.py: de
gepubliceerde cijfers reproduceren. Afwijkingen van de bron staan met PORT:
gemarkeerd.

Eén wijziging is geen port maar een besluit, en die staat met BESLUIT: gemarkeerd:
de as waarop de conditionele curve wordt afgelezen. Zie R-01 in de review en
CHANGELOG-methodology.md.

Let op de quantielreferentie. De copula-kant gebruikt de wekelijkse gemiddelden als
referentie voor transform_to_quantiles, de ECA-kant gebruikt de dagelijkse reeks.
Dat verschil zat al in de notebook, cel 25 tegen cel 16, en is hier bewust
overgenomen. Het staat als openstaand punt genoteerd, zie R-04. Daarom bouwt deze
module zijn invoer zelf op in plaats van via de orkestrator in pipeline.py.
"""
import numpy as np
import xarray as xr
from scipy import stats

from vinecopulas.bivariate import bestcop, random as copula_random, copulas

from .pipeline import (empirical_cdf, find_nearest_grid_point,
                       river_runoff_time_location_mean,
                       river_runoff_time_location_maximum, SRI_calculate,
                       transform_to_quantiles, Intensity_calc, extract_events)

COPS = list(range(1, 16))


def calculate_rolling_max(series, period_after_event):
    """Maximum over de period_after_event elementen na i, i zelf niet meegeteld.

    Uit cel 12, ongewijzigd. Let op dat deze functie de eigen week uitsluit en dus
    period_after_event punten telt, terwijl quantile_max_value in extract_events
    vanaf de laatste droogteweek telt en er dus een meer heeft. Dat verschil is
    R-02 en is nog niet besloten.
    """
    d = series.values if isinstance(series, xr.DataArray) else np.asarray(series)
    out = np.empty(len(d))
    for i in range(len(d)):
        start, end = i + 1, min(i + period_after_event + 1, len(d))
        out[i] = np.max(d[start:end]) if start < len(d) else np.nan
    return out


def fit_best_distribution(data):
    """Kiest een marginale verdeling op chi-kwadraat, uit tien scipy-verdelingen.

    PORT: losgekoppeld van het rekenpad. In de bron werd deze functie twee keer per
    cel aangeroepen en voedde hij prob_drought_first, prob_drought_second,
    prob_flood en prob_flood_fixed. Geen van die vier werd daarna gelezen, dus op de
    transitiekansen heeft dit geen invloed. Zie R-08. De functie blijft bestaan om
    de gekozen verdeling te kunnen rapporteren, maar fit_copula roept hem niet aan.

    PORT: de debug-prints uit de bron zijn weg.
    """
    distributions = [stats.norm, stats.lognorm, stats.weibull_min, stats.gamma,
                     stats.cauchy, stats.expon, stats.laplace, stats.uniform,
                     stats.beta, stats.pareto]
    data = np.asarray(data)
    data = data[np.isfinite(data)]
    if len(data) < 10:
        raise ValueError("Te weinig waarnemingen voor een verdelingsfit.")
    best_fit, best_chi2 = None, np.inf
    for distribution in distributions:
        try:
            params = distribution.fit(data)
            bins = np.histogram_bin_edges(data, bins="auto")
            observed, _ = np.histogram(data, bins)
            expected = len(data) * np.diff(distribution.cdf(bins, *params))
            expected[expected == 0] = 1e-8
            chi2 = np.sum((observed - expected) ** 2 / expected)
            if chi2 < best_chi2:
                best_chi2, best_fit = chi2, (distribution, params)
        except Exception:
            continue
    if best_fit is None:
        raise ValueError("Geen enkele verdeling kon gefit worden.")
    return best_fit, best_chi2


def _exceedance(sorted_values, thresholds):
    """P(U2 >= drempel) uit een gesorteerde trekking.

    PORT: vervangt de lus over 101 waardes van Y in de bron. Die telde voor elke
    drempel opnieuw de hele array door. searchsorted telt hetzelfde: het aantal
    waardes onder de drempel, dus 1 min dat aandeel is het aantal groter of gelijk.
    Zelfde definitie, orde van grootte sneller.
    """
    n = len(sorted_values)
    if n == 0:
        return np.full(len(np.atleast_1d(thresholds)), np.nan)
    return 1.0 - np.searchsorted(sorted_values, thresholds, side="left") / n


def fit_copula(data1, data2, X, Y, quantiles_weekly_max, period_after_event=4,
               n_draw=100000, seed=None, axis="quantile", with_surface=False,
               cops=None):
    """Transitiekansen uit een bivariate copula op droogte en de flood erna.

    data1 is de droogtekarakteristiek, data2 het hoogste runoff-quantiel in het
    venster na de droogte. X zijn de twee drempels voor milde en zware droogte, in
    absolute SRI-eenheden. Y is het raster waarop de curves worden afgelezen.

    BESLUIT: axis bepaalt waarop de conditionele curves worden afgelezen.

      "quantile"  Y is een runoff-quantiel. De curve wordt afgelezen op de rang die
                  daarbij hoort, y_hat(q) = sum(data2 <= q)/(n+1). Dan beantwoordt
                  hij dezelfde vraag als de unconditionele curve en mogen ze naast
                  elkaar. Dit is de gecorrigeerde aflezing en de standaard.

      "rank"      Y is een rang binnen de post-droogte pieken. Dit is de
                  gepubliceerde aflezing, en die staat op een andere schaal dan de
                  unconditionele curve. Alleen bedoeld om de gepubliceerde figuren
                  te reproduceren.

    Zie R-01 in de review. Welke van de twee je kiest verandert de curves niet, het
    verandert waar je ze afleest. De vergelijking van mild tegen zwaar staat in
    beide gevallen op de rangschaal en is dus niet van deze keuze afhankelijk.

    PORT: de figuren zijn uit deze functie gehaald, die zaten er in de bron in met
    plt.show() erbij. PORT: het Z-oppervlak is optioneel geworden, het is alleen
    nodig voor de eerste figuur en het is de traagste lus. PORT: seed toegevoegd,
    de bron seedde niet en was daarmee niet reproduceerbaar, zie R-07.
    """
    if axis not in ("quantile", "rank"):
        raise ValueError("axis moet 'quantile' of 'rank' zijn")
    cops = COPS if cops is None else cops
    d1 = np.asarray(data1, dtype=float)
    d2 = np.asarray(data2, dtype=float)
    valid = np.isfinite(d1) & np.isfinite(d2)
    d1, d2 = d1[valid], d2[valid]
    n = len(d1)
    if n < 10:
        raise ValueError(f"Te weinig droogte-events voor een copulafit: {n}")
    Y = np.asarray(Y, dtype=float)

    ranks = np.column_stack((stats.rankdata(d1) / (n + 1),
                             stats.rankdata(d2) / (n + 1)))
    cop, par, aic = bestcop(cops, ranks.copy())

    if seed is not None:
        np.random.seed(seed)
    draw = copula_random(cop, par, n_draw)
    # R-13: random levert bij de Joe-families een klein aandeel niet-eindige
    # waardes. De bron vergeleek met >= en liet die stil wegvallen. Hier worden ze
    # geteld en verwijderd, zodat teller en noemer dezelfde steekproef gebruiken.
    finite = np.all(np.isfinite(draw), axis=1)
    n_nonfinite = int(np.sum(~finite))
    draw = draw[finite]

    t_minor = float(np.sum(d1 <= X[0]) / (n + 1))
    t_major = float(np.sum(d1 <= X[1]) / (n + 1))
    sorted_minor = np.sort(draw[draw[:, 0] >= t_minor, 1])
    sorted_major = np.sort(draw[draw[:, 0] >= t_major, 1])

    if axis == "quantile":
        # de rang die hoort bij elk runoff-quantiel in Y
        read_at = np.array([np.sum(d2 <= q) / (n + 1) for q in Y])
    else:
        read_at = Y

    rolling = calculate_rolling_max(quantiles_weekly_max, period_after_event)
    rolling = rolling[np.isfinite(rolling)]

    result = {
        "copula_id": int(cop),
        "copula_name": copulas[int(cop)],
        "par": par,
        "aic": float(aic),
        "axis": axis,
        "n_events": n,
        "k_minor": int(np.sum(d1 > X[0])),
        "k_major": int(np.sum(d1 > X[1])),
        "t_minor": t_minor,
        "t_major": t_major,
        "n_nonfinite_draws": n_nonfinite,
        "read_at": read_at,
        "conditional_minor": _exceedance(sorted_minor, read_at),
        "conditional_major": _exceedance(sorted_major, read_at),
        # de unconditionele curve staat altijd op de runoff-quantielschaal, want
        # rolling bevat runoff-quantielen. Alleen bij axis="quantile" ligt hij op
        # dezelfde as als de conditionele curves.
        "unconditional": 1.0 - empirical_cdf(rolling, Y),
    }

    if with_surface:
        # PORT: de bron gebruikte hier een tweede, kleinere trekking van 10.000,
        # waardoor figuur 1 tien keer zoveel ruis had als figuur 2. Zie R-11. Hier
        # wordt dezelfde trekking gebruikt als voor de curves.
        drought_values = np.linspace(d1.min(), d1.max(), 100)
        order = np.argsort(draw[:, 0])
        u1_sorted, u2_by_u1 = draw[order, 0], draw[order, 1]
        surface = np.zeros((len(drought_values), len(Y)))
        for i, value in enumerate(drought_values):
            pseudo = np.sum(d1 <= value) / (n + 1)
            start = np.searchsorted(u1_sorted, pseudo, side="left")
            surface[i] = _exceedance(np.sort(u2_by_u1[start:]), read_at)
        result["surface"] = surface
        result["surface_drought_values"] = drought_values
    return result


def _copula_inputs(data, lon, lat, begin, end, time_scale, threshold,
                   period_after_event):
    """Bouwt de invoer voor de copula op, precies zoals cel 25 dat doet."""
    runoff_mean = river_runoff_time_location_mean(data, lon, lat, begin, end, time_scale)
    sri = SRI_calculate(runoff_mean)
    runoff_max = river_runoff_time_location_maximum(data, lon, lat, begin, end, time_scale)
    # de copula-kant gebruikt de wekelijkse gemiddelden als referentie, niet de
    # dagelijkse reeks die de ECA-kant gebruikt. Zie R-04.
    quantiles_weekly_max = transform_to_quantiles(runoff_max, runoff_mean)
    intensities = Intensity_calc(sri, quantiles_weekly_max, threshold)
    drought_events = extract_events(intensities["Drought_Intensity"] * -1,
                                    intensities["SRI"] * -1, quantiles_weekly_max,
                                    period_after_event)
    return drought_events, quantiles_weekly_max


def _copula_func(variable, data, lon, lat, begin, end, time_scale, X, Y,
                 threshold, period_after_event, **kwargs):
    drought_events, quantiles_weekly_max = _copula_inputs(
        data, lon, lat, begin, end, time_scale, threshold, period_after_event)
    return fit_copula(drought_events[variable], drought_events["quantile_max_value"],
                      X, Y, quantiles_weekly_max,
                      period_after_event=period_after_event, **kwargs)


def copula_func_drought_peak(data, lon, lat, begin, end, time_scale, X, Y,
                             threshold=0.5, period_after_event=4, **kwargs):
    """Transitiekansen met de droogtepiek als droogtekarakteristiek.

    PORT: de bron gaf X, Y, flood_score, threshold en period_after_event
    positioneel mee vanuit cel 30 en 35, wat de verwarring in D-14 heeft
    veroorzaakt. Hier zijn het benoemde parameters met de gepubliceerde waardes als
    default. PORT: flood_score is vervallen. Dat argument voedde alleen
    prob_flood_fixed, dat nergens werd gelezen, zie R-09.
    """
    return _copula_func("drought_peak", data, lon, lat, begin, end, time_scale,
                        X, Y, threshold, period_after_event, **kwargs)


def copula_func_mean_drought_severity(data, lon, lat, begin, end, time_scale, X, Y,
                                      threshold=0.5, period_after_event=4, **kwargs):
    """Transitiekansen met de gemiddelde droogte-severity als karakteristiek.

    Let op R-03: mean_drought_severity deelt in extract_events door einde min begin,
    en dat is een week te kort. Nog niet besloten, dus hier ongewijzigd overgenomen.
    """
    return _copula_func("mean_drought_severity", data, lon, lat, begin, end,
                        time_scale, X, Y, threshold, period_after_event, **kwargs)
