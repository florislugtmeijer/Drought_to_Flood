"""Appendix D: de copulafiguren voor alle 48 locaties, met kopjes per rivier en locatie (R1-09).

Reviewer #1: "Appendix D - The figure titles are too small and headings should be
included to better identify the different rivers and river segments." De
ingediende appendix D plakte per pagina losse afbeeldingen aan elkaar
(notebook, create_page). Dit script tekent elke cel opnieuw in de opbouw van
figuur 5 tot 9 (script 41: oppervlak links, curves met bootstrapband rechts,
periode 1 boven, periode 2 onder) en zet per locatie één liggende pagina met
twee figuren naast elkaar, drought peak links en mean severity rechts, onder
een kop met rivier, plaats en positie. Volgorde: rivieren alfabetisch, per
rivier stroomopwaarts naar stroomafwaarts.

Zelfde cijfers als script 41 en appendix E: puntschatting uit fit_copula met
dezelfde seeds als script 22, banden uit results/2026-09-02_copula_bootstrap/.
Cellen zonder bootstrap (minder dan 15 droogtes) krijgen curves zonder band,
met die melding in de paneltitel. De copula-kant staat op SRI -0,5 (besluit
Floris 30 oktober).

Uitvoer in results/2026-11-02_appendix_d/: appendix_d.pdf (48 pagina's),
per locatie een png, check.txt, README.md, manifest.yaml.

Draaien vanuit de repo-root (circa een kwartier):
  uv run --frozen python scripts/47_appendix_d_figures.py
"""
import sys, os, json, re, ast, hashlib, platform, time, warnings
sys.path.insert(0, "src"); warnings.filterwarnings("ignore")
import numpy as np, pandas as pd, xarray as xr
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from dtf.pipeline import (find_nearest_grid_point, river_runoff_time_location_mean,
    river_runoff_time_location_maximum, SRI_calculate, transform_to_quantiles,
    Intensity_calc, extract_events)
from dtf.copula import fit_copula, flood_peak_after_drought, mean_severity_per_week

DATA = "data/efas_v5_dis06_48_locations_1995_2024.nc"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
BOOT = "results/2026-09-02_copula_bootstrap/transition_ci.csv"
OUT = os.environ.get("OUT", "results/2026-11-02_appendix_d")
LIMIT = int(os.environ.get("LIMIT", 0))  # alleen de eerste n pagina's, voor een proefdraai
THRESHOLD, DT, SEED, N_POINT = 0.5, 4, 42, 100000
Y = np.linspace(0, 1, 101)
Q_TEXT = 0.6915
PAIRS = {"drought_peak": [1, 2], "mean_drought_severity": [0.5, 1]}
PERIODS = {"first": (0, 5479), "second": (5480, 10958)}
LABEL_PERIOD = {"first": "Period 1 (1995-2009)", "second": "Period 2 (2010-2024)"}
LABEL_PAIR = {"drought_peak": "Drought peak", "mean_drought_severity": "Mean severity"}
RLOC = {"First location": "upstream", "Second location": "midstream", "Third location": "downstream"}
PLACE = {"Turijn": "Turin", "Turon": "Toruń", "Warchau": "Warsaw", "Straatsburg": "Strasbourg",
         "Krementsjoek": "Kremenchuk", "Rostov - Dov": "Rostov-on-Don", "St. Maurillle": "Saint-Maurille",
         "Pora Wesfalica": "Porta Westfalica", "Krapowice": "Krapkowice", "Scinawa": "Ścinawa",
         "Kostrzyn nad Odra": "Kostrzyn nad Odrą", "Vila Velha de Rodao": "Vila Velha de Ródão",
         "Cermede / Castelmassa": "Castelmassa", "Montelimar": "Montélimar"}
MINOR, MAJOR, UNCOND = "green", "red", "orange"
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def inputs(data, lat, lon, b, e):
    nlon, nlat = find_nearest_grid_point(data, lon, lat)
    mean_w = river_runoff_time_location_mean(data, nlon, nlat, b, e, "1W")
    sri = SRI_calculate(mean_w)
    max_w = river_runoff_time_location_maximum(data, nlon, nlat, b, e, "1W")
    q = transform_to_quantiles(max_w, mean_w)
    it = Intensity_calc(sri, q, THRESHOLD)
    dr = extract_events(it["Drought_Intensity"] * -1, it["SRI"] * -1, q, DT)
    d2 = flood_peak_after_drought(q, dr["end_time"].values, DT)
    sev = mean_severity_per_week(dr["max_intensity"].values, dr["duration_weeks"].values)
    return q, d2, {"drought_peak": np.asarray(dr["drought_peak"].values, float),
                   "mean_drought_severity": sev}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def draw_pair(fig, axes, cache, pair, river, village, boot, ycols, seeds, li, locs, checks):
    """Vier panelen (2 periodes x oppervlak/curves) voor één variabelenpaar."""
    X = PAIRS[pair]
    for pi, (pname, (b, e)) in enumerate(PERIODS.items()):
        q, d2_all, var = cache[pname]
        d1, d2 = var[pair], d2_all
        m = np.isfinite(d1) & np.isfinite(d2)
        d1, d2 = d1[m], d2[m]
        st = int(seeds[pi * len(locs) + li].generate_state(1)[0])
        seed = int(st % (2 ** 32 - 1))
        np.random.seed(seed)
        res = fit_copula(d1, d2, X, Y, q, period_after_event=DT, n_draw=N_POINT, seed=seed,
                         axis="quantile", marginals="parametric", with_surface=True)
        sel = boot[(boot.river == river) & (boot.village == village)
                   & (boot.period == pname) & (boot.pair == pair)]
        has_band = len(sel) > 0
        get = lambda qty, kind: sel[(sel.quantity == qty) & (sel.kind == kind)][ycols].values[0]
        if has_band:
            dev = max(np.nanmax(np.abs(get("minor_resel", "point") - res["conditional_minor"])),
                      np.nanmax(np.abs(get("major_resel", "point") - res["conditional_major"])))
            checks.append(f"{river} {village} {pname} {pair}: puntcurve vs bootstrap {dev:.1e}")
        else:
            checks.append(f"{river} {village} {pname} {pair}: geen bootstrap ({len(d1)} droogtes)")
        vals = res["surface_drought_values"]

        ax = axes[pi, 0]
        pm = ax.pcolormesh(Y, vals, res["surface"], shading="auto", cmap="viridis",
                           vmin=0, vmax=1, rasterized=True)
        for x0, col, lab in ((X[0], "white", "minor"), (X[1], "red", "major")):
            if vals.min() <= x0 <= vals.max():
                ax.axhline(x0, color=col, lw=1.0, ls=(0, (4, 2)))
                ax.text(1.0, x0, f" {lab}", color=INK2, va="center", ha="left", fontsize=7,
                        transform=ax.get_yaxis_transform())
        ax.set_xlim(0, 1)
        ax.set_xlabel("Flood quantile q")
        ax.set_ylabel(f"Prior {LABEL_PAIR[pair].lower()} x")
        cb = fig.colorbar(pm, ax=ax, fraction=0.05, pad=0.16)
        cb.set_label("P(peak > q | drought ≥ x)", fontsize=7)
        cb.outline.set_linewidth(0.4)
        cb.ax.tick_params(labelsize=7, width=0.4)

        ax = axes[pi, 1]
        for qty, key, col, lab in (("minor_resel", "conditional_minor", MINOR, "Minor drought"),
                                   ("major_resel", "conditional_major", MAJOR, "Major drought")):
            if has_band:
                ax.fill_between(Y, get(qty, "lo"), get(qty, "hi"), color=col, alpha=0.18, lw=0)
            curve = res[key]
            if curve is not None and np.any(np.isfinite(curve)):
                ax.plot(Y, curve, color=col, lw=1.4, label=lab)
        ax.plot(Y, res["unconditional"], color=UNCOND, lw=1.4, label="Unconditional")
        ax.axvline(Q_TEXT, color="#b9b8b3", lw=0.8, zorder=0, label=f"Flood threshold, q = {Q_TEXT}")
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.grid(color=GRID, lw=0.5); ax.set_axisbelow(True)
        ax.set_xlabel("Flood quantile q")
        ax.set_ylabel("Transition probability")
        for a in axes[pi]:
            for s in ("top", "right"):
                a.spines[s].set_visible(False)
        axes[pi, 0].set_title(f"{LABEL_PERIOD[pname]}", loc="left", fontsize=8)
        extra = "" if has_band else ", no bootstrap"
        axes[pi, 1].set_title(f"{res['n_events']} droughts, {res['k_major']} major{extra}",
                              loc="left", fontsize=8)
    return axes[0, 1].get_legend_handles_labels()


def main():
    t0 = time.time()
    os.makedirs(OUT, exist_ok=True)
    data = xr.open_dataset(DATA).set_index(point=["latitude", "longitude"])
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    locs = [(r["river"], l["village"], l["latitude"], l["longitude"], l["river_location"])
            for r in rivers for l in r["locations"]]
    seeds = np.random.SeedSequence(SEED).spawn(len(locs) * len(PERIODS))
    boot = pd.read_csv(BOOT); boot = boot[boot.scheme == "iid"]
    ycols = [f"y_{i:03d}" for i in range(101)]
    checks = []
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                         "xtick.color": INK2, "ytick.color": INK2, "text.color": INK,
                         "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                         "ytick.major.width": 0.6, "pdf.fonttype": 42})
    order = sorted(range(len(locs)), key=lambda i: (locs[i][0], ["First location", "Second location", "Third location"].index(locs[i][4])))
    if LIMIT:
        order = order[:LIMIT]
    pdf = PdfPages(f"{OUT}/appendix_d.pdf")
    for page, li in enumerate(order, start=1):
        river, village, lat, lon, rloc = locs[li]
        place = PLACE.get(village, village)
        cache = {pname: inputs(data, lat, lon, b, e) for pname, (b, e) in PERIODS.items()}
        fig = plt.figure(figsize=(16.5, 7.0))
        sub = fig.subfigures(1, 2, wspace=0.04)
        for sf, pair in zip(sub, PAIRS):
            axes = sf.subplots(2, 2, gridspec_kw={"width_ratios": [1, 1], "wspace": 0.42, "hspace": 0.55})
            draw_pair(sf, axes, cache, pair, river, village, boot, ycols, seeds, li, locs, checks)
            sf.suptitle(LABEL_PAIR[pair], x=0.02, y=0.925, ha="left", fontsize=11, fontweight="bold", color=INK)
            sf.subplots_adjust(left=0.09, right=0.95, top=0.83, bottom=0.14)
        # Vaste legenda, ook als een periode geen milde of zware droogte heeft.
        from matplotlib.lines import Line2D
        proxies = [Line2D([], [], color=MINOR, lw=1.4), Line2D([], [], color=MAJOR, lw=1.4),
                   Line2D([], [], color=UNCOND, lw=1.4), Line2D([], [], color="#b9b8b3", lw=0.8)]
        fig.legend(proxies, ["Minor drought (95% bootstrap band)", "Major drought (95% bootstrap band)",
                             "Unconditional", f"Flood threshold, q = {Q_TEXT}"],
                   frameon=False, fontsize=8, loc="lower center", ncol=4,
                   handlelength=2.2, bbox_to_anchor=(0.5, 0.01))
        fig.suptitle(f"{river} — {place} ({RLOC[rloc]})   ·   Appendix D, page {page} of {len(order)}",
                     x=0.02, ha="left", fontsize=15, fontweight="bold", color=INK, y=0.985)
        pdf.savefig(fig, facecolor="white")
        fig.savefig(f"{OUT}/D{page:02d}_{river.lower()}_{re.sub(r'[^a-z]', '', village.lower())}.png",
                    dpi=150, facecolor="white")
        plt.close(fig)
        print(f"[{page}/{len(order)}] {river} {place} ({(time.time() - t0) / 60:.1f} min)", flush=True)
    pdf.close()
    open(f"{OUT}/check.txt", "w").write("\n".join(checks) + "\n")
    open(f"{OUT}/README.md", "w").write(
        "# Appendix D: copulafiguren voor alle 48 locaties\n\nScript: scripts/47_appendix_d_figures.py. "
        "Eén liggende pagina per locatie, drought peak links en mean severity rechts, elk met het "
        "oppervlak en de curves met 95%-bootstrapband voor beide periodes. Kop per pagina: rivier, plaats, "
        "positie. Copula op SRI -0,5 (besluit 30 oktober); dezelfde cijfers als figuur 5 tot 9 en appendix E. "
        "Cellen zonder bootstrap (minder dan 15 droogtes) hebben geen band, zie check.txt.\n")
    with open(f"{OUT}/manifest.yaml", "w") as f:
        f.write(f"script: scripts/47_appendix_d_figures.py\nrun_minutes: {(time.time() - t0) / 60:.1f}\n"
                f"python: {platform.python_version()}\ninputs:\n  {DATA}: {sha256(DATA)}\n  {BOOT}: {sha256(BOOT)}\n"
                f"seed_scheme: \"numpy.random.SeedSequence({SEED}).spawn(96), als script 22\"\n")


if __name__ == "__main__":
    main()
