"""T-11 stap A: de drie definitievragen uit de review doorgerekend (R4-03).

Drie bevindingen uit de review van de copula-kant bepalen wat de grootheid is
waar het betrouwbaarheidsinterval straks omheen komt. Ze worden hier naast de
gepubliceerde berekening gelegd, met volledige curves, zodat een besluit om te
corrigeren geen tweede run kost.

  R-01  de as. De conditionele curves worden afgelezen op ur[:,1], en dat is per
        constructie uniform, dus de rang van quantile_max_value binnen de events.
        De unconditionele curve staat op de ruwe quantielschaal over alle weken.
        In figuur 2 staan ze op dezelfde x-as. Variant: beide op de ruwe schaal,
        via y_hat(q) = sum(data2 <= q)/(n+1).

  R-02  het floodvenster. extract_events neemt de slice vanaf de laatste week van
        de droogte zelf, en .sel is aan beide kanten inclusief, dus vijf
        weekpunten. Variant: vanaf de week erna, vier punten. Let op dat
        calculate_rolling_max, die de unconditionele curve voedt, de eigen week
        al wel uitsluit. De twee curves zijn op dit punt dus ook onderling
        inconsistent.

  R-03  de duur. mean_drought_severity deelt door end - start, en dat is een week
        te kort. Een droogte van twee weken wordt door 1 gedeeld. Bij duur nul
        wordt het NaN en valt het event weg. Variant: delen door duur + 1 week.

Geen tweede definitie van extract_events. Beide varianten zijn af te leiden uit
wat die functie al teruggeeft: de eindtijden voor R-02, en max_intensity met
duration_weeks voor R-03. De eventdetectie zelf is in alle varianten dezelfde.

Vier eventverzamelingen: gepubliceerd, R-02, R-03, en beide. Per verzameling
opnieuw fitten, en elke curve op beide assen aflezen.

Anders dan de gepubliceerde code wordt hier wel geseed, met een eigen stroom per
cel. Dat is nodig om de varianten te kunnen vergelijken, anders zit het verschil
tussen twee varianten deels in de trekking. Zie R-07.

Onderzoek, geen wijziging. Bestaande code blijft ongemoeid, de gepubliceerde
cijfers worden niet vervangen.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with numpy --with pandas --with xarray --with scipy \
      --with netCDF4 --with vinecopulas --no-project \
      python scripts/14_copula_definition_variants.py
"""
import sys, os, json, re, ast, csv, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy import stats
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events, empirical_cdf)
from vinecopulas.bivariate import bestcop, random, copulas

DATA = os.path.expanduser("~/Downloads/8_maart_european_river_runoff_1994_2024.nc")
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_copula_definition_variants"
THRESHOLD, DT, N_DRAW, SEED = 0.5, 4, 100000, 42
Y = np.linspace(0, 1, 101)                    # zowel de rang-as als de ruwe as
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
COPS = list(range(1, 16))
Q_READ = [0.50, 0.90, 0.95, 0.99]             # ruwe quantielen om af te lezen
VARIANTS = ["gepubliceerd", "R02_venster", "R03_duur", "R02_R03"]
os.makedirs(OUT, exist_ok=True)


def calculate_rolling_max(series, period_after_event):
    """Uit cel 12, ongewijzigd. Sluit de eigen week uit, start op i+1."""
    d = series.values if isinstance(series, xr.DataArray) else series
    out = np.empty(len(d))
    for i in range(len(d)):
        s, e = i + 1, min(i + period_after_event + 1, len(d))
        out[i] = np.max(d[s:e]) if s < len(d) else np.nan
    return out


def flood_peak_excluding_drought_week(quantiles_weekly_max, end_times, weeks):
    """R-02-variant van quantile_max_value: venster vanaf de week na de droogte.

    De gepubliceerde berekening in extract_events start de slice op de laatste
    week van de droogte zelf. Hier start hij een week later, waarmee het venster
    vier weekpunten telt in plaats van vijf en geen droogteweek meer bevat.
    """
    out = np.empty(len(end_times))
    for i, t in enumerate(end_times):
        sel = quantiles_weekly_max.sel(
            valid_time=slice(t + np.timedelta64(1, "W"), t + np.timedelta64(weeks, "W")))
        out[i] = float(sel.max().values) if sel.size else np.nan
    return out


def cond_prob(u2_sorted, thresholds):
    """P(U2 >= y | U1 >= t) voor een reeks y, uit de al geselecteerde trekking.

    u2_sorted is de gesorteerde tweede kolom van de trekking, beperkt tot de
    rijen die aan de droogtevoorwaarde voldoen. Zelfde telling als de lus in
    cel 25, maar via searchsorted in plaats van 101 keer over de hele array.
    """
    n = len(u2_sorted)
    if n == 0:
        return np.full(len(thresholds), np.nan)
    return 1.0 - np.searchsorted(u2_sorted, thresholds, side="left") / n


data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]
seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))

ycols = [f"y_{i:03d}" for i in range(len(Y))]
fc = open(f"{OUT}/curves.csv", "w", newline="")
wc = csv.writer(fc)
wc.writerow(["river","village","period","pair","variant","axis","curve","n_events"] + ycols)

fs = open(f"{OUT}/summary.csv", "w", newline="")
ws = csv.writer(fs)
head = ["river","village","period","pair","variant","n_events","k_minor","k_major",
        "cop_name","par","aic","cop_name_gepubliceerd","familie_gewijzigd",
        "max_diff_minor_vs_gepubliceerd","max_diff_major_vs_gepubliceerd",
        "n_punten_cond_onder_uncond_rangas","n_punten_cond_onder_uncond_ruweas"]
for q in Q_READ:
    head += [f"uncond_q{q}", f"cond_minor_rangas_q{q}", f"cond_minor_ruweas_q{q}"]
ws.writerow(head)

sanity = {"drought_peak_R03_identiek": 0, "drought_peak_R03_afwijkend": 0,
          "lege_vensters": 0, "cellen": 0}
t0 = time.time(); done = 0
for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
    for li, (river, village, lat, lon) in enumerate(locs):
        rng_seed = seeds[pi * len(locs) + li]
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        mw = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
        sri = SRI_calculate(mw)
        xw = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
        q = transform_to_quantiles(xw, mw)          # copula-referentie, cel 25
        it = Intensity_calc(sri, q, THRESHOLD)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)

        rollmax = calculate_rolling_max(q, DT)
        rollmax = rollmax[np.isfinite(rollmax)]
        uncond = 1.0 - empirical_cdf(rollmax, Y)     # ruwe as, over alle weken

        end_times = dr["end_time"].values
        peak = np.asarray(dr["drought_peak"].values, float)
        d2_pub = np.asarray(dr["quantile_max_value"].values, float)
        d2_v2 = flood_peak_excluding_drought_week(q, end_times, DT)
        sanity["lege_vensters"] += int(np.sum(~np.isfinite(d2_v2) & np.isfinite(d2_pub)))
        sev_pub = np.asarray(dr["mean_drought_severity"].values, float)
        dur = np.asarray(dr["duration_weeks"].values, float)
        mx = np.asarray(dr["max_intensity"].values, float)
        sev_v3 = mx / (dur + 1.0)                    # R-03: een week erbij

        # per variant: welke droogtevariabele en welke floodvariabele
        var_data = {
            "gepubliceerd": (d2_pub, {"drought_peak": peak, "mean_drought_severity": sev_pub}),
            "R02_venster":  (d2_v2,  {"drought_peak": peak, "mean_drought_severity": sev_pub}),
            "R03_duur":     (d2_pub, {"drought_peak": peak, "mean_drought_severity": sev_v3}),
            "R02_R03":      (d2_v2,  {"drought_peak": peak, "mean_drought_severity": sev_v3}),
        }
        wc.writerow([river, village, pname, "", "", "ruwe", "unconditioneel", len(rollmax)]
                    + [round(float(v), 6) for v in uncond])

        ref = {}                                     # gepubliceerde curves per paar
        for variant in VARIANTS:
            d2, d1map = var_data[variant]
            for pair, X in PAIRS.items():
                d1 = d1map[pair]
                m = np.isfinite(d1) & np.isfinite(d2)
                a, c = d1[m], d2[m]
                n = len(a)
                if n < 10:
                    continue
                u = np.column_stack((stats.rankdata(a) / (n + 1), stats.rankdata(c) / (n + 1)))
                cop, par, aic = bestcop(COPS, u.copy())
                np.random.seed(rng_seed.generate_state(1)[0] % (2**32 - 1))
                ur = random(cop, par, N_DRAW)
                ur = ur[np.all(np.isfinite(ur), axis=1)]

                t_min = float(np.sum(a <= X[0]) / (n + 1))
                t_max = float(np.sum(a <= X[1]) / (n + 1))
                s_min = np.sort(ur[ur[:, 0] >= t_min, 1])
                s_max = np.sort(ur[ur[:, 0] >= t_max, 1])
                y_hat = np.array([np.sum(c <= qq) / (n + 1) for qq in Y])   # ruwe as

                curves = {
                    ("rang", "minor"): cond_prob(s_min, Y),
                    ("rang", "major"): cond_prob(s_max, Y),
                    ("ruwe", "minor"): cond_prob(s_min, y_hat),
                    ("ruwe", "major"): cond_prob(s_max, y_hat),
                }
                for (axis, curve), vals in curves.items():
                    wc.writerow([river, village, pname, pair, variant, axis, curve, n]
                                + [round(float(v), 6) for v in vals])

                if variant == "gepubliceerd":
                    ref[pair] = (curves, copulas[cop])
                    dmin = dmaj = 0.0
                    fam_changed = 0
                else:
                    ref_curves, ref_fam = ref.get(pair, (None, ""))
                    if ref_curves is None:
                        dmin = dmaj = float("nan"); fam_changed = ""
                    else:
                        dmin = float(np.nanmax(np.abs(curves[("rang", "minor")]
                                                      - ref_curves[("rang", "minor")])))
                        dmaj = float(np.nanmax(np.abs(curves[("rang", "major")]
                                                      - ref_curves[("rang", "major")])))
                        fam_changed = int(copulas[cop] != ref_fam)
                    if pair == "drought_peak" and variant == "R03_duur":
                        # R-03 raakt drought_peak niet, deze twee horen gelijk te zijn
                        key = "drought_peak_R03_identiek" if dmin == 0 and dmaj == 0 \
                              else "drought_peak_R03_afwijkend"
                        sanity[key] += 1

                below_rank = int(np.sum(curves[("rang", "minor")] < uncond))
                below_raw = int(np.sum(curves[("ruwe", "minor")] < uncond))
                row = [river, village, pname, pair, variant, n,
                       int(np.sum(a > X[0])), int(np.sum(a > X[1])),
                       copulas[cop],
                       np.round(par, 6) if np.ndim(par) == 0 else np.round(par, 6).tolist(),
                       round(float(aic), 4), ref.get(pair, (None, ""))[1], fam_changed,
                       round(dmin, 6), round(dmaj, 6), below_rank, below_raw]
                for qq in Q_READ:
                    yq = float(np.sum(c <= qq) / (n + 1))
                    row += [round(float(1.0 - empirical_cdf(rollmax, np.array([qq]))[0]), 4),
                            round(float(cond_prob(s_min, np.array([qq]))[0]), 4),
                            round(float(cond_prob(s_min, np.array([yq]))[0]), 4)]
                ws.writerow(row)
                sanity["cellen"] += 1
        fc.flush(); fs.flush()
        done += 1
        el = time.time() - t0
        print(f"[{done}/96] {pname:6} {river:8} {village[:22]:22} {el:6.1f}s "
              f"eta {el/done*(96-done):5.1f}s", flush=True)
fc.close(); fs.close()
print(f"\nsanity: {sanity}", flush=True)
print(f"klaar in {time.time()-t0:.1f}s, uitvoer in {OUT}/", flush=True)
