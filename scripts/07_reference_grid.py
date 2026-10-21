"""Raster voor T-02 en T-03: quantielreferentie maal referentievenster, threshold 0,5.

Twee assen, allebei over de referentieverdeling waartegen de drempels worden
geijkt:

  quantile_reference  daily | weekly_max   -> T-02, P-02, D-11 (alleen de floodzijde)
  reference_scope     period | full        -> T-03, D-13 (beide zijdes)

Waarom deze run bestaat. De bestaande variant-run
results/2026-08-23_quantile_reference_variant/ staat vast op threshold=1, en T-01
heeft de threshold op 0,5 gezet. De cijfers waarop T-02 is beslist horen dus bij
een configuratie die niet meer geldt. Dit raster draait ze opnieuw op 0,5 en
neemt T-03 mee omdat het over dezelfde referentieverdeling gaat.

Dit is onderzoek, geen wijziging. De defaults in src/dtf/pipeline.py blijven
quantile_reference="daily" en reference_window=None, dus de gepubliceerde
berekening. De cel daily+period is de controlecel: die moet exact reproduceren
wat er in results/2026-08-23_threshold_comparison/ ligt bij threshold 0,5.

Parameters staan hieronder in één blok. Ze horen in config/analysis.yaml, maar
config/ bestaat nog niet, zie T-42.
"""
import sys, os, json, re, ast, csv, time, hashlib, subprocess, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import xarray as xr
from dtf.pipeline import find_nearest_grid_point, drought_flood_p_value_trigger_ECA

# --- parameters, horen in config/analysis.yaml (T-42) ---------------------
DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-01_reference_grid"
THRESHOLD = 0.5              # vastgelegd in T-01, 1 september 2026
PERIOD_AFTER_EVENT = 4       # weken
TIME_SCALE = "1W"
N_SIMULATIONS = 10000
SEED = 42
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))
FULL_WINDOW = (0, 10958)     # de volle reeks, 1995-01-01 tot 2024-12-31.
                             # Let op: index 5479 valt buiten beide periodes maar
                             # zit hier wel in de referentie, zie de off-by-one in D-02
CELLS = (("daily", "period"), ("weekly_max", "period"),
         ("daily", "full"), ("weekly_max", "full"))
# -------------------------------------------------------------------------

os.makedirs(OUT, exist_ok=True)
data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

f = open(f"{OUT}/grid_results.csv", "w", newline="")
w = csv.writer(f)
w.writerow(["quantile_reference", "reference_scope", "period", "river", "village",
            "river_location", "drought_count", "flood_count", "match_count_trigger",
            "match_count_precursor", "observed_matches_mc", "p_trigger", "p_precursor",
            "p_mc_trigger", "pct_weeks_flood", "pct_weeks_drought", "n_weeks"])

t0 = time.time(); n = 0
total = len(CELLS) * len(PERIODS) * len(locs)
for qref, scope in CELLS:
    for pname, (b, e) in PERIODS:
        window = None if scope == "period" else FULL_WINDOW
        for river, village, rloc, lat, lon in locs:
            nlon, nlat = find_nearest_grid_point(data, lon, lat)
            n += 1
            r = drought_flood_p_value_trigger_ECA(
                data, nlon, nlat, b, e, TIME_SCALE, threshold=THRESHOLD,
                period_after_event=PERIOD_AFTER_EVENT, n_simulations=N_SIMULATIONS,
                seed=SEED, quantile_reference=qref, reference_window=window)
            w.writerow([qref, scope, pname, river, village, rloc,
                        r["drought_count"], r["flood_count"], r["match_count_trigger"],
                        r["match_count_precursor"], r["observed_matches"],
                        r["p_trigger"], r["p_precursor"], r["p_mc_trigger"],
                        round(r["pct_weeks_flood"], 2), round(r["pct_weeks_drought"], 2),
                        r["n_weeks"]])
            f.flush()
            el = time.time() - t0
            print(f"[{n}/{total}] {qref:10} {scope:6} {pname:6} {river:8} "
                  f"{village[:20]:20} dr={r['drought_count']:3} fl={r['flood_count']:3} "
                  f"p_mc={r['p_mc_trigger']:.4f} ({el/60:.1f}m, eta "
                  f"{el/n*(total-n)/60:.0f}m)", flush=True)
f.close()

# manifest, verplicht volgens de dtf-code skill
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                        text=True).stdout.strip()
dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                            text=True).stdout.strip())
pkgs = {}
for m in ("numpy", "pandas", "xarray", "scipy"):
    pkgs[m] = __import__(m).__version__

with open(f"{OUT}/manifest.yaml", "w") as mf:
    mf.write(f"""run_date: 2026-09-01
script: scripts/07_reference_grid.py
git_commit: {commit}
git_dirty: {str(dirty).lower()}   # true betekent: niet-gecommitte wijzigingen tijdens de run
config:
  threshold: {THRESHOLD}
  period_after_event: {PERIOD_AFTER_EVENT}
  time_scale: "{TIME_SCALE}"
  n_simulations: {N_SIMULATIONS}
  seed: {SEED}
  periods: {{first: [0, 5479], second: [5480, 10958]}}
  full_window: [{FULL_WINDOW[0]}, {FULL_WINDOW[1]}]
  cells: {[list(c) for c in CELLS]}
  locations: {len(locs)}
inputs:
  {os.path.basename(DATA)}: {sha256(DATA)}
python: {sys.version.split()[0]}
packages:
""")
    for k, v in pkgs.items():
        mf.write(f"  {k}: {v}\n")
    mf.write("# uv.lock bestaat nog niet, zie T-44. Versies hierboven zijn wat deze run gebruikte.\n")

print(f"klaar in {(time.time()-t0)/60:.1f} minuten, {n} runs")
