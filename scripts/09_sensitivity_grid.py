"""Gevoeligheidsraster voor T-10 en R4-01: drie parameters, threshold 0,5 als baseline.

De reviewer noemt drie keuzes "somewhat arbitrary" en mist een gevoeligheidstest:
de SRI-drempel, het floodpercentiel en de lengte van het coincidence-venster.
Dit script varieert ze alle drie.

  threshold       0,25 / 0,5 / 0,75 / 1,0 / 1,5    droogte bij SRI < -threshold
  flood_quantile  0,60 / 0,6915 / 0,80 / 0,90 / 0,95   flood boven dit quantiel
  match_window    1 / 2 / 4 / 8 / 12 weken          coincidence-venster

De spiegeling tussen de twee drempels is losgelaten, besloten 1 september 2026.
Tot nu toe leidde de code het floodpercentiel af uit de SRI-drempel met
norm.cdf(threshold), dus één parameter bestuurde beide kanten en de as die de
reviewer vraagt bestond niet. Zie D-11 en CHANGELOG-methodology.md.

Vorm van het raster: volledig gekruist, 5 maal 5 maal 5 is 125 cellen. Eerst is
alleen het vlak bij venster 4 gedraaid plus het venster als lijn door de baseline,
samen 29 cellen. Op 1 september 2026 uitgebreid naar de volle kruising, zodat ook
de interactie tussen het venster en de twee drempels zichtbaar wordt.

Referentieconfiguratie ligt vast door T-02 en T-03, allebei besloten op
1 september 2026: quantile_reference="daily" en reference_scope="period", dus de
gepubliceerde berekening. Er is hier geen as voor.

Naast de p-waarde per locatie levert dit script de gepoolde toets uit Donges et
al. 2016 sectie 2.2, vergelijking 6. Zie de README van de resultaatmap.

Parameters staan hieronder in één blok. Ze horen in config/analysis.yaml, maar
config/ is nog leeg, zie T-42.

Draaien:
    uv run --python 3.12 --with xarray --with netCDF4 --with numpy --with pandas \
        --with scipy python scripts/09_sensitivity_grid.py

Het script hervat: een cel-periode die al af is wordt overgeslagen.
"""
import sys, os, json, re, ast, csv, time, hashlib, subprocess, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, xarray as xr
from scipy.stats import norm
from dtf.pipeline import find_nearest_grid_point, drought_flood_p_value_trigger_ECA

# --- parameters, horen in config/analysis.yaml (T-42) ---------------------
DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-09-02_sensitivity_grid_endfix"
RUN_DATE = "2026-09-02"
# Herberekening van het volledige raster na de reparatie van de einddetectie in
# extract_events, zie CHANGELOG-methodology.md 2026-09-02. Resultaten uit een
# vorige run worden nooit overschreven: de pre-fix run staat vast in
# results/2026-09-01_sensitivity_grid/ en blijft de vergelijkingsbasis.

BASE_THRESHOLD = 0.5                  # vastgelegd in T-01
BASE_FLOOD_Q = float(norm.cdf(0.5))   # 0,6914624..., NIET afgerond op 0,6915.
                                      # Dit is exact wat de gepubliceerde code
                                      # berekende, en de controlecel moet exact
                                      # reproduceren. Afronden verschuift weken
                                      # over de drempel.
BASE_WINDOW = 4                       # weken

PLANE_THRESHOLD = (0.25, BASE_THRESHOLD, 0.75, 1.0, 1.5)
PLANE_FLOOD_Q = (0.60, BASE_FLOOD_Q, 0.80, 0.90, 0.95)
WINDOWS = (1, 2, BASE_WINDOW, 8, 12)  # alle vensters, volledig gekruist

TIME_SCALE = "1W"
N_SIMULATIONS = 10000
SEED = 42                             # stam, per locatie een eigen stroom
PERIODS = (("first", (0, 5479)), ("second", (5480, 10958)))
QUANTILE_REFERENCE = "daily"          # T-02, 1 september 2026
REFERENCE_WINDOW = None               # T-03, 1 september 2026: per periode
ALPHA = 0.05
# -------------------------------------------------------------------------

# Volledig gekruist, 5 maal 5 maal 5 is 125 cellen. Uitgebreid op 1 september 2026
# nadat het vlak bij venster 4 al klaar was: die 29 cellen staan op schijf en worden
# door de hervattingslogica overgeslagen, dus alleen de 96 nieuwe draaien.
# Venster buitenom in de lus, zodat elk venster als geheel afkomt en het rapport
# tussentijds al iets kan laten zien.
CELLS = [(t, q, w) for w in WINDOWS for q in PLANE_FLOOD_Q for t in PLANE_THRESHOLD]

os.makedirs(f"{OUT}/pooled_null", exist_ok=True)
data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
locs = [(r["river"], l["village"], l["river_location"], l["latitude"], l["longitude"])
        for r in rivers for l in r["locations"]]

# Eigen seedstroom per locatie. Met één vaste seed voor alle locaties krijgen twee
# locaties met evenveel floods identieke surrogaten, want het weekrooster is binnen
# een periode overal hetzelfde. Voor de p-waarde per locatie maakt dat niets uit,
# voor de gepoolde toets wel: gecorreleerde surrogaten blazen de variantie van de
# som op en maken de toets te conservatief. De volgorde hieronder is die van de
# notebook-lijst en mag niet omgegooid worden, anders krijgt elke locatie een
# andere stroom. Zie D-04 en CHANGELOG-methodology.md.
seeds = np.random.SeedSequence(SEED).spawn(len(locs))

COLUMNS = ["threshold", "flood_quantile", "match_window", "period", "river", "village",
           "river_location", "drought_count", "flood_count", "match_count_trigger",
           "match_count_precursor", "observed_matches_mc", "p_trigger", "p_precursor",
           "p_mc_trigger", "pct_weeks_flood", "pct_weeks_drought", "n_weeks", "testable"]

CSV_PATH = f"{OUT}/grid_results.csv"
tag = lambda t, q, w, p: f"thr{t}_fq{q:.4f}_win{w}_{p}"


def done_cells():
    """Een cel-periode telt als af zodra zijn gepoolde nulverdeling op schijf staat.

    CSV-rijen en nulverdeling worden per cel-periode samen weggeschreven, dus die
    twee kunnen niet uit de pas lopen. Bij een herstart wordt een afgeronde
    cel-periode overgeslagen en een halve opnieuw gedraaid.
    """
    return {f[:-4] for f in os.listdir(f"{OUT}/pooled_null") if f.endswith(".npy")}


af = done_cells()
if af:
    print(f"hervatten: {len(af)} van de {len(CELLS)*len(PERIODS)} cel-periodes staan al op schijf")
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as fh:
        csv.writer(fh).writerow(COLUMNS)

t0 = time.time()
n = 0                                  # positie in het volledige raster
gedraaid = 0                           # runs die deze sessie echt zijn uitgevoerd
total = len(CELLS) * len(PERIODS) * len(locs)
gedaan = len(af) * len(locs)           # runs die al op schijf stonden
te_gaan = total - gedaan               # wat er deze sessie te doen is
mismatch = 0

for thr, fq, win in CELLS:
    for pname, (b, e) in PERIODS:
        naam = tag(thr, fq, win, pname)
        if naam in af:
            n += len(locs)
            continue
        rows = []
        pooled_null = np.zeros(N_SIMULATIONS, dtype=np.int64)
        for i, (river, village, rloc, lat, lon) in enumerate(locs):
            nlon, nlat = find_nearest_grid_point(data, lon, lat)
            n += 1
            r = drought_flood_p_value_trigger_ECA(
                data, nlon, nlat, b, e, TIME_SCALE, threshold=thr,
                period_after_event=win, n_simulations=N_SIMULATIONS, seed=seeds[i],
                quantile_reference=QUANTILE_REFERENCE, reference_window=REFERENCE_WINDOW,
                flood_quantile=fq)
            # Niet toetsbaar bij nul droogtes of nul floods: de p-waarde wordt dan
            # 1,0 en dat betekent niets te toetsen, niet "geen samenhang". Zie D-12.
            # In de gepoolde toets valt zo'n locatie vanzelf weg, want hij draagt
            # nul bij aan teller en noemer.
            testable = int(r["drought_count"] > 0 and r["flood_count"] > 0)
            # match_count_trigger en observed_matches tellen hetzelfde: het aantal
            # droogtes gevolgd door minstens één flood binnen het venster. Ze komen
            # uit twee verschillende stukken code, dus dit is een gratis controle.
            if r["match_count_trigger"] != r["observed_matches"]:
                mismatch += 1
                print(f"    LET OP {river}/{village}: match_count_trigger "
                      f"{r['match_count_trigger']} tegen observed_matches {r['observed_matches']}")
            pooled_null += r["mc_null_counts"]
            rows.append([thr, fq, win, pname, river, village, rloc,
                         r["drought_count"], r["flood_count"], r["match_count_trigger"],
                         r["match_count_precursor"], r["observed_matches"],
                         r["p_trigger"], r["p_precursor"], r["p_mc_trigger"],
                         round(r["pct_weeks_flood"], 2), round(r["pct_weeks_drought"], 2),
                         r["n_weeks"], testable])
            gedraaid += 1
            el = time.time() - t0
            # ETA over wat er deze sessie nog te doen is. Niet over n, want n telt de
            # overgeslagen cellen mee en die staan niet vooraan in de volgorde.
            eta = el / gedraaid * (te_gaan - gedraaid) / 60
            print(f"[{n}/{total}] thr={thr:<4} fq={fq:.4f} win={win:<2} {pname:6} "
                  f"{river:8} {village[:18]:18} dr={r['drought_count']:3} "
                  f"fl={r['flood_count']:3} p_mc={r['p_mc_trigger']:.4f} "
                  f"({el/60:.1f}m, eta {eta:.0f}m)", flush=True)

        # CSV-rijen en nulverdeling samen wegschrijven, zodat ze niet uit de pas lopen
        with open(CSV_PATH, "a", newline="") as fh:
            csv.writer(fh).writerows(rows)
        np.save(f"{OUT}/pooled_null/{naam}.npy", pooled_null)

        # gepoolde toets, Donges et al. 2016 sectie 2.2 vergelijking 6
        num = sum(r[COLUMNS.index("match_count_trigger")] for r in rows)
        den = sum(r[COLUMNS.index("drought_count")] for r in rows)
        p_pool = float(np.mean(pooled_null >= num))
        print(f"  --> gepoold {naam}: rate {num}/{den} = {num/den:.4f}, "
              f"nullijn {pooled_null.mean()/den:.4f}, p = {p_pool:.4f}", flush=True)

if mismatch:
    print(f"\nLET OP: {mismatch} runs waar match_count_trigger en observed_matches verschillen")


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
pkgs = {m: __import__(m).__version__ for m in ("numpy", "pandas", "xarray", "scipy")}

with open(f"{OUT}/manifest.yaml", "w") as mf:
    mf.write(f"""run_date: {RUN_DATE}
script: scripts/09_sensitivity_grid.py
git_commit: {commit}
git_dirty: {str(dirty).lower()}   # true betekent: niet-gecommitte wijzigingen tijdens de run
config:
  base_threshold: {BASE_THRESHOLD}
  base_flood_quantile: {BASE_FLOOD_Q!r}   # norm.cdf(0.5), niet afgerond
  base_window: {BASE_WINDOW}
  plane_threshold: {list(PLANE_THRESHOLD)}
  plane_flood_quantile: {[float(q) for q in PLANE_FLOOD_Q]}
  windows: {list(WINDOWS)}
  cells: {len(CELLS)}
  time_scale: "{TIME_SCALE}"
  n_simulations: {N_SIMULATIONS}
  seed: {SEED}          # stam voor SeedSequence, per locatie een eigen stroom
  seed_scheme: "numpy.random.SeedSequence({SEED}).spawn(48), volgorde van de notebook-lijst"
  quantile_reference: "{QUANTILE_REFERENCE}"   # T-02, 1 september 2026
  reference_window: {REFERENCE_WINDOW}         # T-03, 1 september 2026: per periode
  periods: {{first: [0, 5479], second: [5480, 10958]}}
  locations: {len(locs)}
inputs:
  {os.path.basename(DATA)}: {sha256(DATA)}
python: {sys.version.split()[0]}
packages:
""")
    for k, v in pkgs.items():
        mf.write(f"  {k}: {v}\n")
    mf.write("# uv.lock bestaat nog niet, zie T-44. Versies hierboven zijn wat deze run gebruikte.\n")

print(f"\nklaar in {(time.time()-t0)/60:.1f} minuten, {gedraaid} runs gedraaid, "
      f"{gedaan} overgeslagen, {len(CELLS)} cellen totaal")
