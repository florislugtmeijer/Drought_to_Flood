"""T-17, Reviewer #1 punt R1-08: een tabel met de fysische resultaten per rivier.

De reviewer mist hydrologie tussen de statistiek. Tabel 3 geeft p-waardes per
locatie; deze tabel geeft wat er fysisch gebeurt: hoeveel droogtes, hoe lang, hoe
diep, hoe vaak er binnen vier weken een flood op volgt, hoe snel, in welk seizoen,
en of de rivier zich gedraagt als een vrij afstromende of een gereguleerde rivier.
De copula-kolommen komen uit de bootstrap en de onafhankelijkheidstoetsen van
T-11, allebei op de gerepareerde eventdefinities.

Onderzoek en rapportage, geen wijziging aan de pipeline. Alle eventgrootheden komen
uit `extract_events` op de baseline van T-01 tot T-03: drempel 0,5, floodpercentiel
norm.cdf(0,5), venster 4, quantielreferentie de dagelijkse reeks van de periode
zelf. De eventaantallen worden vergeleken met de baseline-cel van het
gevoeligheidsraster, zodat vaststaat dat dit dezelfde berekening is.

Wat "verwacht" betekent bij de overgangsratio: het aandeel van alle weken in de
periode waarna binnen (t, t+4] een flood begint. Dat is de kans dat een op een
willekeurige week geplaatst droogte-einde een flood treft, dezelfde nullijn als in
scripts/05_season_control.py. Het is een beschrijvend getal, geen toets; de toets
is de Monte Carlo p uit het raster, die hier wordt overgenomen.

Uitvoer in results/2026-09-04_physical_table/:
  per_location.csv    48 locaties maal 2 periodes, alle grootheden
  per_river.csv       16 rivieren maal 2 periodes, events gepoold over de locaties
  table_per_river.md  conceptversie van de tabel voor het manuscript, Engels
  table_per_river.tex idem, LaTeX
  sanity_check.txt    vergelijking met het raster en de standaardcontroles
  README.md, manifest.yaml

Draaien vanuit de repo-root:
    uv run --python 3.12 --with xarray --with netCDF4 --with numpy --with pandas \
        --with scipy python scripts/27_physical_results_table.py
"""
import sys, os, json, re, ast, time, hashlib, subprocess, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
from scipy.stats import norm
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)

# --- parameters, horen in config/analysis.yaml (T-42) ---------------------
DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-04_physical_table"
RUN_DATE = "2026-09-04"
GRID = "results/2026-09-02_sensitivity_grid_endfix/grid_results.csv"
BOOT = "results/2026-09-02_copula_bootstrap/transition_ci.csv"
DEP = "results/2026-09-02_dependence_tests/dependence_tests.csv"

THRESHOLD = 0.5                       # T-01
FLOOD_Q = float(norm.cdf(0.5))        # niet afgerond, zie script 09
WINDOW = 4                            # weken
TIME_SCALE = "1W"
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))
SRI_SEVERE = -1.0                     # grens voor de reguleringsindicator
EXPECTED_BELOW_SEVERE = 100 * norm.cdf(SRI_SEVERE)   # 15,87 procent bij een goede fit
COPULA_Q_INDEX = 69                   # y_069 = 0,69 op linspace(0,1,101), zoals script 25
COPULA_SCHEME = "iid"                 # blok-bootstrap staat ernaast als controle
ALPHA = 0.05
SEASON = {12: "DJF", 1: "DJF", 2: "DJF", 3: "MAM", 4: "MAM", 5: "MAM",
          6: "JJA", 7: "JJA", 8: "JJA", 9: "SON", 10: "SON", 11: "SON"}
# -------------------------------------------------------------------------

os.makedirs(OUT, exist_ok=True)
data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]
river_order = [r["river"] for r in rivers]

grid = pd.read_csv(GRID)
base = grid[(grid.threshold == THRESHOLD) & (np.isclose(grid.flood_quantile, FLOOD_Q))
            & (grid.match_window == WINDOW)].set_index(["period", "river", "village"])
assert len(base) == 2 * len(locs), f"baseline-cel in het raster onvolledig: {len(base)} rijen"

sanity = []
def note(msg):
    sanity.append(msg); print("  " + msg, flush=True)

# --- standaardcontroles op de data --------------------------------------
t_all = data.valid_time.values
if len(t_all) != len(np.unique(t_all)):
    note("LET OP: dubbele tijdstappen in de dataset")
gaps = np.unique(np.diff(t_all))
if len(gaps) != 1:
    note(f"LET OP: ongelijke stappen in de tijdas: {gaps}")
note(f"dataset: {len(t_all)} dagen, {str(t_all[0])[:10]} tot {str(t_all[-1])[:10]}")
grid_points = {}
for river, village, _, lat, lon in locs:
    nlon, nlat = find_nearest_grid_point(data, lon, lat)
    grid_points.setdefault((float(nlat), float(nlon)), []).append(f"{river}/{village}")
    if abs(nlat - lat) > 0.05 or abs(nlon - lon) > 0.05:
        note(f"LET OP: {river}/{village} ligt {abs(nlat-lat):.3f}/{abs(nlon-lon):.3f} graad van het gridpunt")
for pt, names in grid_points.items():
    if len(names) > 1:
        note(f"LET OP: zelfde gridpunt {pt} voor {names}")

# --- copula-bronnen inlezen ----------------------------------------------
boot = pd.read_csv(BOOT)
boot = boot[(boot.scheme == COPULA_SCHEME) & (boot.quantity == "diff_resel")]
ycol = f"y_{COPULA_Q_INDEX:03d}"
boot = boot.pivot_table(index=["period", "river", "village", "pair"], columns="kind",
                        values=ycol)
dep = pd.read_csv(DEP).set_index(["period", "river", "village", "pair"])

def copula_cols(period, river, village):
    out = {}
    for pair, tag in (("drought_peak", "peak"), ("mean_drought_severity", "sev")):
        key = (period, river, village, pair)
        if key in boot.index:
            r = boot.loc[key]
            out[f"cop_{tag}_diff"] = round(float(r["point"]), 4)
            out[f"cop_{tag}_lo"] = round(float(r["lo"]), 4)
            out[f"cop_{tag}_hi"] = round(float(r["hi"]), 4)
        else:
            out[f"cop_{tag}_diff"] = out[f"cop_{tag}_lo"] = out[f"cop_{tag}_hi"] = np.nan
        if key in dep.index:
            d = dep.loc[key]
            out[f"cop_{tag}_n_events"] = int(d["n_events"])
            out[f"cop_{tag}_k_major"] = int(d["k_major"])
            out[f"cop_{tag}_family"] = d["copula_name"]
            out[f"cop_{tag}_tau"] = round(float(d["tau"]), 4)
            out[f"cop_{tag}_tau_p"] = round(float(d["tau_p"]), 4)
            out[f"cop_{tag}_part_q69"] = round(float(d["cp_q6915"]), 4)
            out[f"cop_{tag}_part_q69_p"] = round(float(d["cp_q6915_p"]), 4)
        else:
            for k in ("n_events", "k_major", "family", "tau", "tau_p", "part_q69", "part_q69_p"):
                out[f"cop_{tag}_{k}"] = np.nan
    return out

# --- de lus over locaties en periodes ------------------------------------
rows, events = [], []   # events: per droogte een regel, voor de pooling per rivier
t0 = time.time(); n = 0; mismatch = 0
for pname, (b, e) in PERIODS:
    for river, village, rloc, lat, lon in locs:
        nlon, nlat = find_nearest_grid_point(data, lon, lat)
        runoff_mean = river_runoff_time_location_mean(data, nlon, nlat, b, e, TIME_SCALE)
        sri = SRI_calculate(runoff_mean)
        raw = data.isel(valid_time=slice(b, e)).sel(longitude=nlon, latitude=nlat)
        mx = river_runoff_time_location_maximum(data, nlon, nlat, b, e, TIME_SCALE)
        q = transform_to_quantiles(mx, raw)
        it = Intensity_calc(sri, q, THRESHOLD, FLOOD_Q)
        fl = extract_events(it["Flood_Intensity"], it["SRI"], q, WINDOW)
        dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, WINDOW)
        weeks = pd.to_datetime(q["valid_time"].values)
        n_weeks = len(weeks)
        sri_v = sri.values

        d_end = pd.to_datetime(dr["end_time"].values)
        f_start = pd.to_datetime(fl["start_time"].values)
        d_dur = dr["duration_weeks"].values.astype(float)
        d_peak_sri = -dr["drought_peak"].values.astype(float)   # terug naar de SRI-schaal
        f_dur = fl["duration_weeks"].values.astype(float)
        delta = pd.Timedelta(weeks=WINDOW)

        # overgangen: eerste flood die strikt na het droogte-einde en binnen het venster begint
        lags, seasons_tr = [], []
        for t in d_end:
            after = f_start[(f_start > t) & (f_start <= t + delta)]
            if len(after):
                lags.append(int(round((after.min() - t) / pd.Timedelta(weeks=1))))
                seasons_tr.append(SEASON[t.month])
        transitions = len(lags)
        # nullijn: aandeel van alle weken waarna binnen het venster een flood begint
        null_share = float(np.mean([bool(np.any((f_start > w) & (f_start <= w + delta)))
                                    for w in weeks]))
        share = transitions / len(d_end) if len(d_end) else np.nan
        seasons_end = [SEASON[t.month] for t in d_end]

        def dominant(seq):
            if not seq: return ("", np.nan)
            vc = pd.Series(seq).value_counts()
            return (vc.index[0], round(float(vc.iloc[0] / len(seq)), 3))
        dom_tr, dom_tr_share = dominant(seasons_tr)
        dom_end, dom_end_share = dominant(seasons_end)

        g = base.loc[(pname, river, village)]
        if int(g["drought_count"]) != len(d_end) or int(g["flood_count"]) != len(f_start) \
                or int(g["match_count_trigger"]) != transitions:
            mismatch += 1
            note(f"AFWIJKING van het raster bij {pname} {river}/{village}: "
                 f"droogtes {len(d_end)} tegen {int(g['drought_count'])}, floods {len(f_start)} "
                 f"tegen {int(g['flood_count'])}, overgangen {transitions} tegen {int(g['match_count_trigger'])}")
        if n_weeks not in (783, 784):
            note(f"LET OP: {pname} {river}/{village} heeft {n_weeks} weken")
        if np.isnan(sri_v).any():
            note(f"LET OP: {int(np.isnan(sri_v).sum())} NaN in de SRI van {pname} {river}/{village}")

        row = {
            "period": pname, "river": river, "village": village, "river_location": rloc,
            "n_weeks": n_weeks,
            "drought_count": len(d_end),
            "drought_duration_median_wk": float(np.median(d_dur)) if len(d_dur) else np.nan,
            "drought_duration_max_wk": float(d_dur.max()) if len(d_dur) else np.nan,
            "drought_one_week_share": round(float(np.mean(d_dur == 1)), 3) if len(d_dur) else np.nan,
            "drought_peak_sri_median": round(float(np.median(d_peak_sri)), 3) if len(d_dur) else np.nan,
            "drought_peak_sri_min": round(float(d_peak_sri.min()), 3) if len(d_dur) else np.nan,
            "pct_weeks_drought": round(100 * float(np.nanmean(sri_v < -THRESHOLD)), 2),
            "pct_weeks_sri_below_minus1": round(100 * float(np.nanmean(sri_v < SRI_SEVERE)), 2),
            "flood_count": len(f_start),
            "flood_duration_median_wk": float(np.median(f_dur)) if len(f_dur) else np.nan,
            "pct_weeks_flood": round(100 * float(np.mean(q.values > FLOOD_Q)), 2),
            "transitions": transitions,
            "transition_share": round(share, 4) if share == share else np.nan,
            "null_share": round(null_share, 4),
            "ratio_obs_exp": round(share / null_share, 3) if null_share and share == share else np.nan,
            "p_mc_trigger": float(g["p_mc_trigger"]),
            "lag_median_wk": float(np.median(lags)) if lags else np.nan,
            "lag_one_week_share": round(float(np.mean(np.array(lags) == 1)), 3) if lags else np.nan,
            "transition_season_dominant": dom_tr, "transition_season_share": dom_tr_share,
            "drought_end_season_dominant": dom_end, "drought_end_season_share": dom_end_share,
        }
        row.update(copula_cols(pname, river, village))
        rows.append(row)
        for i, t in enumerate(d_end):
            after = f_start[(f_start > t) & (f_start <= t + delta)]
            events.append({"period": pname, "river": river, "village": village,
                           "duration_wk": d_dur[i], "peak_sri": d_peak_sri[i],
                           "end_season": SEASON[t.month],
                           "lag_wk": int(round((after.min() - t) / pd.Timedelta(weeks=1))) if len(after) else np.nan})
        n += 1
        el = time.time() - t0
        if n == 1:
            print(f"eerste locatie in {el:.1f} s, schatting voor {2*len(locs)}: {el*2*len(locs)/60:.1f} min", flush=True)
        print(f"[{n}/{2*len(locs)}] {pname:6} {river:8} {village[:22]:22} "
              f"droogtes {len(d_end):3d} overgangen {transitions:3d} ({el/60:.1f} min)", flush=True)

per_loc = pd.DataFrame(rows)
per_loc.to_csv(f"{OUT}/per_location.csv", index=False)
ev = pd.DataFrame(events)
note(f"raster-vergelijking: {mismatch} van {n} locatie-periodes wijken af" if mismatch
     else f"raster-vergelijking: alle {n} locatie-periodes hebben dezelfde droogte-, flood- en overgangsaantallen als de baseline-cel")

# --- per rivier: events gepoold over de drie locaties ---------------------
riv_rows = []
for pname, _ in PERIODS:
    for river in river_order:
        L = per_loc[(per_loc.period == pname) & (per_loc.river == river)]
        E = ev[(ev.period == pname) & (ev.river == river)]
        lags = E["lag_wk"].dropna()
        tr_seasons = E.loc[E["lag_wk"].notna(), "end_season"]
        dom = tr_seasons.value_counts()
        weeks_total = L["n_weeks"].sum()
        # nullijn per rivier: gewogen met het aantal droogtes per locatie, zodat
        # observed/expected op dezelfde events slaat
        exp_tr = float((L["null_share"] * L["drought_count"]).sum())
        r = {
            "period": pname, "river": river, "n_locations": len(L),
            "drought_count": int(L["drought_count"].sum()),
            "drought_duration_median_wk": float(E["duration_wk"].median()) if len(E) else np.nan,
            "drought_one_week_share": round(float((E["duration_wk"] == 1).mean()), 3) if len(E) else np.nan,
            "drought_peak_sri_median": round(float(E["peak_sri"].median()), 3) if len(E) else np.nan,
            "drought_peak_sri_min": round(float(E["peak_sri"].min()), 3) if len(E) else np.nan,
            "pct_weeks_drought": round(float((L["pct_weeks_drought"] * L["n_weeks"]).sum() / weeks_total), 2),
            "pct_weeks_sri_below_minus1": round(float((L["pct_weeks_sri_below_minus1"] * L["n_weeks"]).sum() / weeks_total), 2),
            "pct_weeks_sri_below_minus1_range": f"{L['pct_weeks_sri_below_minus1'].min():.1f}-{L['pct_weeks_sri_below_minus1'].max():.1f}",
            "flood_count": int(L["flood_count"].sum()),
            "pct_weeks_flood": round(float((L["pct_weeks_flood"] * L["n_weeks"]).sum() / weeks_total), 2),
            "transitions": int(L["transitions"].sum()),
            "transition_share": round(float(L["transitions"].sum() / L["drought_count"].sum()), 4) if L["drought_count"].sum() else np.nan,
            "expected_transitions": round(exp_tr, 1),
            "ratio_obs_exp": round(float(L["transitions"].sum() / exp_tr), 3) if exp_tr else np.nan,
            "n_locations_significant": int((L["p_mc_trigger"] < ALPHA).sum()),
            "p_mc_range": f"{L['p_mc_trigger'].min():.3g}-{L['p_mc_trigger'].max():.3g}",
            "lag_median_wk": float(lags.median()) if len(lags) else np.nan,
            "lag_one_week_share": round(float((lags == 1).mean()), 3) if len(lags) else np.nan,
            "transition_season_dominant": dom.index[0] if len(dom) else "",
            "transition_season_share": round(float(dom.iloc[0] / len(tr_seasons)), 3) if len(dom) else np.nan,
        }
        for tag in ("peak", "sev"):
            r[f"cop_{tag}_diff_median"] = round(float(L[f"cop_{tag}_diff"].median()), 4)
            r[f"cop_{tag}_diff_range"] = f"{L[f'cop_{tag}_diff'].min():+.3f}..{L[f'cop_{tag}_diff'].max():+.3f}"
            r[f"cop_{tag}_n_ci_excl_zero"] = int(((L[f"cop_{tag}_lo"] > 0) | (L[f"cop_{tag}_hi"] < 0)).sum())
            r[f"cop_{tag}_n_part_significant"] = int((L[f"cop_{tag}_part_q69_p"] < ALPHA).sum())
            r[f"cop_{tag}_families"] = "/".join(str(x) for x in L[f"cop_{tag}_family"].fillna("-"))
        riv_rows.append(r)
per_riv = pd.DataFrame(riv_rows)
per_riv.to_csv(f"{OUT}/per_river.csv", index=False)

# --- conceptversie van de tabel, Engels, beide periodes naast elkaar -------
def fmt(x, nd=1, pct=False, sign=False):
    if x is None or (isinstance(x, float) and np.isnan(x)): return "–"
    s = f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"
    return s
def pair(col, nd=1, pct=False, sign=False):
    a = per_riv[(per_riv.period == "first") & (per_riv.river == river)].iloc[0][col]
    b = per_riv[(per_riv.period == "second") & (per_riv.river == river)].iloc[0][col]
    if isinstance(a, str): return f"{a} / {b}"
    if isinstance(a, (int, np.integer)) and nd == 0: return f"{int(a)} / {int(b)}"
    return f"{fmt(a, nd, pct, sign)} / {fmt(b, nd, pct, sign)}"

headers = ["River", "Droughts (n)", "Median duration (wk)", "One-week droughts",
           "Median peak SRI", "Weeks SRI < −1 (%)", "Floods (n)",
           "Droughts followed by flood ≤4 wk", "Obs/exp", "Sig. locations (of 3)",
           "Median lag (wk)", "Dominant season", "Δp severe−mild at q0.69"]
lines_md = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
lines_tex = []
for river in river_order:
    cells = [river,
             pair("drought_count", 0),
             pair("drought_duration_median_wk", 0),
             pair("drought_one_week_share", 2),
             pair("drought_peak_sri_median", 2),
             pair("pct_weeks_sri_below_minus1", 1),
             pair("flood_count", 0),
             pair("transition_share", 2),
             pair("ratio_obs_exp", 2),
             pair("n_locations_significant", 0),
             pair("lag_median_wk", 0),
             pair("transition_season_dominant"),
             pair("cop_peak_diff_median", 2, sign=True)]
    lines_md.append("| " + " | ".join(str(c) for c in cells) + " |")
    lines_tex.append(" & ".join(str(c).replace("−", "$-$").replace("Δ", r"$\Delta$").replace("≤", r"$\leq$")
                                for c in cells) + r" \\")

caption = ("Physical characteristics of drought-to-flood transitions per river, pooled over the "
           "three locations per river, for Period 1 (1995–2009) / Period 2 (2010–2024). Droughts are "
           f"runs of weeks with SRI < −{THRESHOLD}; floods are runs of weeks with weekly maximum runoff "
           "above the 69.1st percentile of the daily distribution of the same period. A drought is "
           f"followed by a flood if a flood starts within {WINDOW} weeks after the drought ends. "
           "Obs/exp is the observed share of droughts followed by a flood divided by the share of all "
           "weeks that are followed by a flood start within the same window. Significant locations are "
           f"those with Monte Carlo p < {ALPHA}. Median lag is the number of weeks from drought end to "
           "flood start. Dominant season is the season in which most drought ends leading to a flood "
           "fall. Weeks with SRI < −1 is compared with the 15.9% expected for a well-fitted "
           "standardised index; much lower values indicate regulated flow. Δp is the median over the "
           "three locations of the difference in the probability of a flood peak exceeding the 0.69 "
           "runoff quantile after a severe versus a mild drought (drought-peak pair, bootstrap point "
           "estimate); per-location intervals are in per_location.csv.")

with open(f"{OUT}/table_per_river.md", "w") as f:
    f.write("# Draft table for T-17 (R1-08): physical results per river\n\n")
    f.write("Generated by scripts/27_physical_results_table.py, do not edit by hand.\n\n")
    f.write("\n".join(lines_md) + "\n\n**Caption.** " + caption + "\n")
with open(f"{OUT}/table_per_river.tex", "w") as f:
    f.write("% generated by scripts/27_physical_results_table.py, do not edit by hand\n")
    f.write("\\begin{table}[htbp]\n\\centering\n\\scriptsize\n")
    f.write("\\caption{" + caption.replace("−", "$-$").replace("Δ", r"$\Delta$").replace("%", r"\%") + "}\n")
    f.write("\\begin{tabular}{l" + "r" * (len(headers) - 1) + "}\n\\toprule\n")
    f.write(" & ".join(h.replace("−", "$-$").replace("Δ", r"$\Delta$").replace("≤", r"$\leq$").replace("%", r"\%")
                       for h in headers) + " \\\\\n\\midrule\n")
    f.write("\n".join(lines_tex) + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n")

with open(f"{OUT}/sanity_check.txt", "w") as f:
    f.write("\n".join(sanity) + "\n")

# --- manifest -------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
pkgs = {m: __import__(m).__version__ for m in ("numpy", "pandas", "xarray", "scipy")}
with open(f"{OUT}/manifest.yaml", "w") as mf:
    mf.write(f"""run_date: {RUN_DATE}
script: scripts/27_physical_results_table.py
git_commit: {commit}
git_dirty: {str(dirty).lower()}   # true betekent: niet-gecommitte wijzigingen tijdens de run
config:
  threshold: {THRESHOLD}
  flood_quantile: {FLOOD_Q!r}   # norm.cdf(0.5), niet afgerond
  window: {WINDOW}
  time_scale: "{TIME_SCALE}"
  quantile_reference: "daily"   # T-02
  reference_window: None         # T-03, per periode
  periods: {{first: [0, 5479], second: [5480, 10958]}}
  locations: {len(locs)}
  sri_severe: {SRI_SEVERE}
  copula_quantile_index: {COPULA_Q_INDEX}   # y_069 op linspace(0,1,101)
  copula_scheme: "{COPULA_SCHEME}"
  alpha: {ALPHA}
inputs:
  {os.path.basename(DATA)}: {sha256(DATA)}
  {GRID}: {sha256(GRID)}
  {BOOT}: {sha256(BOOT)}
  {DEP}: {sha256(DEP)}
python: {sys.version.split()[0]}
packages:
""")
    for k, v in pkgs.items():
        mf.write(f"  {k}: {v}\n")
    mf.write("# uv.lock bestaat nog niet, zie T-44. Versies hierboven zijn wat deze run gebruikte.\n")

print(f"\nklaar in {(time.time()-t0)/60:.1f} minuten, {len(per_loc)} locatie-periodes, "
      f"{len(per_riv)} rivier-periodes, {mismatch} afwijkingen van het raster")
