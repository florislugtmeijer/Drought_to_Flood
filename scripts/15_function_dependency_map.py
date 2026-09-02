"""Afhankelijkhedenkaart van de twee modellen, gelezen uit de bron.

Waarom dit script en niet een plaatje met de hand: een met de hand getekende
kaart klopt op de dag dat je hem tekent en daarna nooit meer. Dit script leest
de aanroepen en de gegevensstroom uit de broncode met `ast`, en de indeling
staat als tabel in dit bestand. Wijkt de bron af van de indeling, dan valt het
script niet stil maar meldt het het verschil en zet de onbekende functie in een
strook "niet ingedeeld", zodat de figuur nooit stilzwijgend iets weglaat.

Twee bronnen, want de twee modellen staan nu op twee plekken:
  - de ECA-kant staat in `src/dtf/pipeline.py`, overgezet en in gebruik
  - de copula-kant staat nog in `notebooks/drought_to_flood_europe_r1_published.ipynb`
Een functie die in beide staat wordt uit de port gelezen, want dat is de versie
die draait. Zie `docs/function-provenance.md`.

Twee soorten pijl, en dat onderscheid is de kern van de figuur:
  - **aanroep**, doorgetrokken: A roept B op, staat letterlijk in de body van A
  - **gegevensstroom**, gestreept: de uitvoer van A gaat als argument naar B,
    binnen dezelfde aanroeper

Dat tweede is nodig omdat de zeven functies van de gedeelde kern elkaar niet
aanroepen. Ze worden door de driver achter elkaar gezet. Een kale aanroepgraaf
laat ze dus alle zeven als losse blaadjes onder twee drivers hangen en verbergt
precies de keten die het onderzoek is.

Dit script rekent niets uit en verandert niets aan de gepubliceerde cijfers. Het
leest twee bestanden en tekent.

Draaien vanuit de repo-root:
  uv run --python 3.12 --with matplotlib --no-project \
      python scripts/15_function_dependency_map.py
"""
import ast
import hashlib
import json
import os
import platform
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
PORT = "src/dtf/pipeline.py"
OUT = "results/2026-09-02_function_dependency_map"

# ---------------------------------------------------------------------------
# Indeling. x en y zijn de plek op het doek, band bepaalt de kleur, decisions
# zijn de D- en P-nummers die deze functie raken. De statussen van die nummers
# staan in docs/open-decisions.md en docs/proposed-changes.md, niet hier: een
# status verandert en een figuur die hem meedraagt verjaart.
# ---------------------------------------------------------------------------
ECA, CORE, COP, LOOSE = "eca", "core", "copula", "loose"

LAYOUT = {
    # ECA-model
    "run_eca_period":                    (10, 88, ECA, []),
    "drought_flood_p_value_trigger_ECA": (34, 88, ECA, ["D-02", "D-08"]),
    "eca_p_value":                       (134, 95, ECA, []),
    "get_matching_pairs_eca":            (157, 95, ECA, ["D-08"]),
    "monte_carlo_p_value":               (134, 78, ECA, ["D-03", "D-04"]),
    "_empty_as_datetime64":              (157, 82, ECA, ["D-12", "D-13"]),
    "safe_format":                       (179, 95, ECA, []),
    "export_csv_and_download":           (179, 82, ECA, []),
    # gedeelde kern
    "find_nearest_grid_point":           (52, 66, CORE, ["D-09"]),
    "river_runoff_time_location_mean":   (52, 54, CORE, ["D-02"]),
    "river_runoff_time_location_maximum": (52, 42, CORE, ["D-02"]),
    "SRI_calculate":                     (78, 60, CORE, ["D-13"]),
    "transform_to_quantiles":            (78, 44, CORE, ["D-11", "D-13", "P-02"]),
    "calculate_quantile":                (78, 34, CORE, []),
    "Intensity_calc":                    (98, 52, CORE, ["D-01", "D-11", "D-14"]),
    "extract_events":                    (126, 52, CORE, []),
    # copula-model
    "export_period_pages":               (10, 18, COP, []),
    "copula_func_drought_peak":          (34, 28, COP, ["D-14"]),
    "copula_func_mean_drought_severity": (34, 8, COP, ["D-14"]),
    "fit_copula":                        (134, 18, COP, ["D-14"]),
    "fit_best_distribution":             (157, 32, COP, []),
    "calculate_rolling_max":             (157, 22, COP, []),
    "empirical_cdf":                     (157, 12, COP, []),
    "calculate_fraction":                (157, 2, COP, []),
    "save_current_page":                 (179, 30, COP, []),
    "create_page":                       (179, 20, COP, []),
    "process_img":                       (179, 10, COP, []),
    "resolve_period_label":              (179, 0, COP, []),
    # niet in een van de twee modellen
    "find_closest_index":                (34, -11, LOOSE, []),
    "plot_location_runoff":              (66, -11, LOOSE, []),
    "analyze_location_data":             (100, -11, LOOSE, []),
}

# Functies die genest in een andere functie staan. Krijgen een stippellijn naar
# hun ouder in plaats van een aanroeppijl, want ze bestaan niet zelfstandig.
NESTED = {"calculate_quantile": "transform_to_quantiles",
          "calculate_fraction": "fit_copula"}

# Waar de twee modellen inhoudelijk uit elkaar lopen. Elke regel is een
# vaststelling uit de bron, met het nummer waar de afweging staat.
DIVERGENCE = [
    ("transform_to_quantiles", 72, 20,
     "ECA ijkt op de dagelijkse reeks,\ncopula op de weekgemiddelden", "P-02"),
    ("Intensity_calc", 104, 32,
     "Flood_Intensity wordt in de copula\nberekend maar nooit gelezen", "D-14"),
]

BAND_LABEL = {
    ECA: ("ECA-model", "Tabel 3"),
    CORE: ("Gedeelde kern", "beide modellen"),
    COP: ("Copula-model", "Figuur 3, Appendix D"),
    LOOSE: ("Buiten de twee modellen", "geen gepubliceerd cijfer"),
}
BAND_Y = {ECA: (72, 101), CORE: (28, 71), COP: (-4, 37), LOOSE: (-17, -5)}

FILL = {ECA: "#dce7f2", CORE: "#e6e2d3", COP: "#e7ded9", LOOSE: "#ececec"}
LINE = {ECA: "#2f5c8a", CORE: "#7a6a3f", COP: "#8a4a3a", LOOSE: "#8c8c8c"}
BAND_BG = {ECA: "#f4f8fb", CORE: "#faf8f2", COP: "#fbf6f4", LOOSE: "#f7f7f7"}


# ---------------------------------------------------------------------------
# Bron lezen
# ---------------------------------------------------------------------------
def notebook_source():
    """Alle codecellen achter elkaar, met de cel per functie erbij.

    Cellen die niet parsen worden overgeslagen en gemeld. In deze notebook is
    dat cel 2, de pip-installregels met een uitroepteken ervoor.
    """
    nb = json.load(open(NB))
    bodies, cell_of, skipped = {}, {}, []
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        try:
            tree = ast.parse(src)
        except SyntaxError:
            skipped.append(i)
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # bij twee definities van dezelfde naam wint de laatste, want dat
                # is wat er staat na uitvoeren. Zie docs/function-provenance.md.
                bodies[node.name] = node
                cell_of.setdefault(node.name, []).append(i)
    return bodies, cell_of, skipped


def port_source():
    tree = ast.parse(open(PORT).read())
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}


def called_names(node, known):
    """Namen uit `known` die in de body van node worden aangeroepen of doorgegeven.

    Doorgegeven telt mee omdat `np.vectorize(calculate_quantile)` geen aanroep
    is maar wel een afhankelijkheid.
    """
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
            if nm in known and nm != node.name:
                out.add(nm)
        elif isinstance(n, ast.Name) and n.id in known and n.id != node.name:
            out.add(n.id)
    return out


def _names_in(expr):
    return {n.id for n in ast.walk(expr) if isinstance(n, ast.Name)}


def _producer_of(expr, known):
    """De functie uit `known` die de waarde van deze expressie maakt, als die er is."""
    for n in ast.walk(expr):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
            if nm in known:
                return nm
    return None


def dataflow_edges(node, known):
    """(A, B) als de uitvoer van A binnen deze body als argument naar B gaat.

    Twee passes over de toewijzingen, zodat aliassen meelopen: in
    `copula_func_drought_peak` is het `Intensities = Intensity_calc(...)` en
    daarna `drought_intensity = Intensities["Drought_Intensity"]`, en die
    tweede regel moet nog steeds naar Intensity_calc wijzen.
    """
    produced = {}
    for _ in range(3):
        for n in ast.walk(node):
            if not isinstance(n, ast.Assign):
                continue
            direct = _producer_of(n.value, known)
            if direct is None:
                srcs = {produced[v] for v in _names_in(n.value) if v in produced}
                direct = srcs.pop() if len(srcs) == 1 else None
            if direct is None:
                continue
            for t in n.targets:
                for nm in ast.walk(t):
                    if isinstance(nm, ast.Name):
                        produced[nm.id] = direct

    edges = set()
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        consumer = f.id if isinstance(f, ast.Name) else getattr(f, "attr", None)
        if consumer not in known:
            continue
        args = list(n.args) + [k.value for k in n.keywords]
        for a in args:
            producer = _producer_of(a, known)
            if producer is None:
                srcs = {produced[v] for v in _names_in(a) if v in produced}
                producer = srcs.pop() if len(srcs) == 1 else None
            if producer and producer != consumer:
                edges.add((producer, consumer))
    return edges


def build_graph():
    nb_bodies, cell_of, skipped = notebook_source()
    port_bodies = port_source()
    known = set(nb_bodies) | set(port_bodies)
    # de port wint waar hij bestaat, want dat is de code die draait
    bodies = {n: port_bodies.get(n, nb_bodies.get(n)) for n in known}
    ported = set(port_bodies)

    calls, flows = set(), set()
    for name, body in bodies.items():
        for c in called_names(body, known):
            calls.add((name, c))
        for a, b in dataflow_edges(body, known):
            flows.add((a, b))
    # een gegevensstroom die ook een aanroep is, is geen extra informatie
    flows -= calls
    return known, ported, cell_of, skipped, calls, flows


# ---------------------------------------------------------------------------
# Tekenen
# ---------------------------------------------------------------------------
BOX_W, BOX_H = 21.0, 7.4


def wrap(name):
    """Functienaam over maximaal drie regels, gebroken op de underscores."""
    parts = name.split("_")
    lines, cur = [], ""
    for p in parts:
        cand = f"{cur}_{p}" if cur else p
        if len(cand) > 17 and cur:
            lines.append(cur + "_")
            cur = p
        else:
            cur = cand
    lines.append(cur)
    return "\n".join(lines[:4])


def anchor(x, y, tx, ty):
    """Punt op de rand van het kader, in de richting van het doelkader."""
    hw, hh = BOX_W / 2, BOX_H / 2
    dx, dy = tx - x, ty - y
    if dx == 0 and dy == 0:
        return x, y
    sx = hw / abs(dx) if dx else float("inf")
    sy = hh / abs(dy) if dy else float("inf")
    s = min(sx, sy)
    return x + dx * s, y + dy * s


def draw(ported, cell_of, calls, flows, unplaced, path_svg, path_png,
         callouts=True):
    fig, ax = plt.subplots(figsize=(26, 13.5))
    ax.set_xlim(-6, 196)
    ax.set_ylim(-27, 108)
    ax.axis("off")

    layout = dict(LAYOUT)
    for i, name in enumerate(sorted(unplaced)):
        layout[name] = (10 + 26 * i, -22, LOOSE, [])

    # banden
    for band, (y0, y1) in BAND_Y.items():
        ax.add_patch(Rectangle((-5, y0), 200, y1 - y0, facecolor=BAND_BG[band],
                               edgecolor="none", zorder=0))
        head, sub = BAND_LABEL[band]
        ax.text(-4.2, y1 - 2.6, head, fontsize=13, fontweight="bold",
                color=LINE[band], va="top", ha="left", zorder=1)
        ax.text(-4.2, y1 - 6.4, sub, fontsize=10, color=LINE[band], va="top",
                ha="left", style="italic", zorder=1)

    # Een aanroep van een driver naar een schakel die binnen dezelfde driver al
    # gegevens van een andere schakel krijgt, voegt niets toe aan de figuur.
    # entry_calls is de eerste schakel, orchestration is de rest.
    entry_calls, orchestration = set(), set()
    for a in {x for x, _ in calls}:
        callees = {b for x, b in calls if x == a}
        if len(callees) < 3:
            continue
        for b in callees:
            fed = any((c, b) in flows for c in callees if c != b)
            (orchestration if fed else entry_calls).add((a, b))

    # pijlen eerst, kaders eroverheen
    def arrow(a, b, style, color, lw, alpha, rad, zorder):
        ax1, ay1, _, _ = layout[a]
        bx1, by1, _, _ = layout[b]
        p0 = anchor(ax1, ay1, bx1, by1)
        p1 = anchor(bx1, by1, ax1, ay1)
        ax.add_patch(FancyArrowPatch(
            p0, p1, arrowstyle="-|>", mutation_scale=11, linewidth=lw,
            linestyle=style, color=color, alpha=alpha, zorder=zorder,
            shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))

    for a, b in sorted(calls):
        if a not in layout or b not in layout:
            continue
        if NESTED.get(b) == a:
            arrow(a, b, ":", LINE[layout[a][2]], 1.0, 0.8, 0.0, 2)
        elif (a, b) in entry_calls:
            # de driver komt de keten hier binnen. Hij roept alle schakels
            # rechtstreeks aan, maar die pijlen lopen over de hele breedte en
            # zeggen niets extra: wat de een aan de ander doorgeeft staat al in
            # de gestreepte pijlen. Getekend wordt alleen de schakel die niets
            # van een andere schakel van dezelfde driver binnenkrijgt.
            arrow(a, b, "-", "#9aa0a6", 1.0, 0.6, 0.09, 1)
        elif (a, b) in orchestration:
            continue
        else:
            arrow(a, b, "-", LINE[layout[a][2]], 1.7, 0.95, 0.05, 3)
    for a, b in sorted(flows):
        if a not in layout or b not in layout:
            continue
        arrow(a, b, (0, (5, 3)), LINE[layout[a][2]], 1.7, 0.9, 0.05, 3)

    # kaders
    for name, (x, y, band, dec) in layout.items():
        is_port = name in ported
        ax.add_patch(FancyBboxPatch(
            (x - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H,
            boxstyle="round,pad=0,rounding_size=1.2",
            facecolor=FILL[band], edgecolor=LINE[band],
            linewidth=1.9 if is_port else 1.1,
            linestyle="-" if is_port else (0, (3, 2)), zorder=4))
        ax.text(x, y + (0.9 if dec else 0.0), wrap(name), fontsize=8.2,
                fontfamily="monospace", ha="center", va="center", zorder=5,
                color="#1a1a1a")
        if dec:
            ax.text(x, y - BOX_H / 2 + 1.35, "  ".join(dec), fontsize=6.8,
                    ha="center", va="center", zorder=5, color=LINE[band],
                    fontweight="bold")
        cells = cell_of.get(name)
        if cells:
            tag = "cel " + ",".join(str(c) for c in sorted(set(cells)))
            ax.text(x + BOX_W / 2 - 0.6, y + BOX_H / 2 - 1.1, tag, fontsize=6.0,
                    ha="right", va="center", color="#6b6b6b", zorder=5)

    # de plekken waar de twee modellen uit elkaar lopen
    for name, tx, ty, text, num in (DIVERGENCE if callouts else []):
        x, y, band, _ = layout[name]
        ax.annotate(
            f"{text}\n{num}", xy=(x, y - BOX_H / 2), xytext=(tx, ty),
            fontsize=7.6, color="#8a2f2f", ha="center", va="top", zorder=6,
            arrowprops=dict(arrowstyle="-", color="#8a2f2f", linewidth=0.9,
                            connectionstyle="arc3,rad=-0.2"),
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#fff", alpha=0.9,
                      edgecolor="#8a2f2f", linewidth=0.7))

    # legenda
    lx, ly = 2, 105.5
    items = [("-", 1.7, "#333", "aanroep"),
             ((0, (5, 3)), 1.7, "#333", "uitvoer wordt argument"),
             ("-", 0.8, "#9aa0a6", "driver komt de keten binnen"),
             (":", 1.0, "#333", "genest in")]
    for i, (ls, lw, col, lab) in enumerate(items):
        x0 = lx + i * 34
        ax.add_patch(FancyArrowPatch((x0, ly), (x0 + 7, ly), arrowstyle="-|>",
                                     mutation_scale=10, linewidth=lw,
                                     linestyle=ls, color=col, zorder=6))
        ax.text(x0 + 8.4, ly, lab, fontsize=8.4, va="center", ha="left",
                color="#333", zorder=6)
    ax.add_patch(FancyBboxPatch((lx + 137, ly - 2.2), 5.5, 4.4,
                                boxstyle="round,pad=0,rounding_size=1.0",
                                facecolor="#fff", edgecolor="#333", linewidth=1.9,
                                zorder=6))
    ax.text(lx + 144, ly, "in src/dtf/pipeline.py", fontsize=8.4, va="center",
            color="#333", zorder=6)
    ax.add_patch(FancyBboxPatch((lx + 176, ly - 2.2), 5.5, 4.4,
                                boxstyle="round,pad=0,rounding_size=1.0",
                                facecolor="#fff", edgecolor="#333", linewidth=1.1,
                                linestyle=(0, (3, 2)), zorder=6))
    ax.text(lx + 183, ly, "alleen in de notebook", fontsize=8.4, va="center",
            color="#333", zorder=6)

    fig.tight_layout()
    fig.savefig(path_svg, format="svg", bbox_inches="tight")
    fig.savefig(path_png, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
def main():
    for p in (NB, PORT):
        if not os.path.exists(p):
            sys.exit(f"niet gevonden: {p}, draai dit vanuit de repo-root")
    os.makedirs(OUT, exist_ok=True)

    known, ported, cell_of, skipped, calls, flows = build_graph()

    unplaced = sorted(known - set(LAYOUT))
    stale = sorted(set(LAYOUT) - known)
    if skipped:
        print(f"cellen niet geparst, geen Python: {skipped}")
    if unplaced:
        print(f"LET OP {len(unplaced)} functie(s) in de bron maar niet in de "
              f"indeling van dit script, bovenaan de figuur gezet: {unplaced}")
    if stale:
        print(f"LET OP {len(stale)} functie(s) in de indeling maar niet meer in "
              f"de bron: {stale}")

    args = (ported, cell_of, calls, flows, unplaced)
    draw(*args, f"{OUT}/function_dependency_map.svg",
         f"{OUT}/function_dependency_map.png", callouts=True)
    # kale versie zonder de tekstblokken, voor als hij het manuscript in gaat.
    # De inhoud van die blokken staat dan in caption.md.
    draw(*args, f"{OUT}/function_dependency_map_bare.svg",
         f"{OUT}/function_dependency_map_bare.png", callouts=False)

    graph = {
        "functions": {
            n: {"ported": n in ported,
                "notebook_cells": sorted(set(cell_of.get(n, []))),
                "band": LAYOUT.get(n, (0, 0, LOOSE, []))[2],
                "decisions": LAYOUT.get(n, (0, 0, LOOSE, []))[3],
                "nested_in": NESTED.get(n)}
            for n in sorted(known)},
        "calls": sorted(map(list, calls)),
        "dataflow": sorted(map(list, flows)),
        "unplaced": unplaced,
        "stale_layout_entries": stale,
    }
    with open(f"{OUT}/graph.json", "w") as f:
        json.dump(graph, f, indent=2)

    # manifest, zoals elke andere resultatenmap. Er zit hier geen data in, de
    # invoer is de code zelf, dus die twee bestanden krijgen een checksum.
    def sha256(path):
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for blk in iter(lambda: fh.read(1 << 20), b""):
                h.update(blk)
        return h.hexdigest()

    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except Exception:
        commit = "onbekend"
    with open(f"{OUT}/manifest.yaml", "w") as f:
        f.write(f"""run_date: 2026-09-02
git_commit: {commit}
script: scripts/15_function_dependency_map.py
config:
  note: geen parameters, de indeling staat als LAYOUT in het script
inputs:
  {os.path.basename(NB)}: {sha256(NB)}
  {os.path.basename(PORT)}: {sha256(PORT)}
counts:
  functions: {len(known)}
  calls: {len(calls)}
  dataflow: {len(flows)}
  in_port: {len(ported)}
  notebook_only: {len(known) - len(ported)}
python: {platform.python_version()}
packages:
  matplotlib: {matplotlib.__version__}
""")

    print(f"\n{len(known)} functies, {len(calls)} aanroepen, "
          f"{len(flows)} gegevensstromen")
    print(f"{len(ported)} in {PORT}, {len(known) - len(ported)} alleen in de notebook")
    for band in (ECA, CORE, COP, LOOSE):
        ns = [n for n, v in LAYOUT.items() if v[2] == band]
        print(f"  {BAND_LABEL[band][0]:26} {len(ns)}")
    print(f"\nuitvoer in {OUT}/")


if __name__ == "__main__":
    main()
