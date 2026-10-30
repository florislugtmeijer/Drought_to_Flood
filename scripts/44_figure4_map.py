"""Figuur 4: kaart van de locaties met significante droogte-tot-flood-samenhang onder C'.

Leest results/2026-10-27_table3_eca_cprime/figure4_categories.csv (script 39):
per locatie of de Monte Carlo-p onder nul C' in periode 1, 2, beide of geen van
beide onder 0,05 ligt, en of de locatie gemarkeerd is (D-12, de vier
gereguleerde locaties waar de SRI vrijwel geen droogtes vindt). Coördinaten uit
de locatielijst van de notebook, dezelfde bron als script 27.

Opbouw als in de ingediende figuur 4 (besluit Floris 30 oktober): het open
zwarte buitensymbool is de categorie (cirkel beide periodes, vierkant alleen
periode 2, ruit alleen periode 1; nieuw: driehoek geen van beide, grijze
gestippelde cirkel test niet informatief), de gekleurde binnenstip is de rivier
(tab20 over de rivieren in alfabetische volgorde, zoals in de ingediende figuur),
het cijfer is de positie op de rivier (1 stroomop, 2 midden, 3 stroomaf). Drie
legenda's: rivier, categorie, cijfer. Anders dan in R1 staan alle 48 locaties
op de kaart, niet alleen de significante, en staat er geen titel in de figuur
(de uitleg hoort in het bijschrift). Kaartlaag: Natural Earth 50m via cartopy.

Uitvoer in results/2026-10-28_figure4_map/: fig04_map.png (300 dpi), fig04_map.pdf,
caption_en.md, README.md, manifest.yaml.

Draaien vanuit de repo-root:
  uv run --frozen python scripts/44_figure4_map.py
"""
import os, re, ast, json, hashlib, platform
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
import cartopy.crs as ccrs, cartopy.feature as cf

CAT = "results/2026-10-27_table3_eca_cprime/figure4_categories.csv"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-10-28_figure4_map"
EXTENT = (-10.5, 44.5, 35.5, 58.5)
INK, INK2, GREY = "#0b0b0b", "#52514e", "#8a8984"
# buitensymbool en legendatekst per categorie
OUTER = {"both": ("o", "Both periods"),
         "first only": ("D", "Period 1 only"),
         "second only": ("s", "Period 2 only"),
         "none": ("^", "Neither period")}
POS = {"First location": "1", "Second location": "2", "Third location": "3"}
PLACE = {"Rhone": "Rhône"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    cat = pd.read_csv(CAT)
    src = "\n".join("".join(c["source"]) for c in json.load(open(NB))["cells"])
    rivers = ast.literal_eval(re.search(r'rivers\s*=\s*(\[.*?\n\])', src, re.S).group(1))
    info = {(r["river"], l["village"]): (l["latitude"], l["longitude"], l["river_location"])
            for r in rivers for l in r["locations"]}
    cat["lat"] = [info[(r, v)][0] for r, v in zip(cat.river, cat.village)]
    cat["lon"] = [info[(r, v)][1] for r, v in zip(cat.river, cat.village)]
    cat["pos"] = [POS[info[(r, v)][2]] for r, v in zip(cat.river, cat.village)]
    assert len(cat) == 48 and cat.lat.notna().all()

    names = sorted(cat.river.unique(), key=lambda s: PLACE.get(s, s))
    colours = dict(zip(names, plt.cm.tab20(np.linspace(0, 1, len(names)))))

    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(10.2, 3.3))
    ax = fig.add_axes([0.04, 0.08, 0.66, 0.89], projection=ccrs.PlateCarree())
    ax.set_extent(EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cf.LAND.with_scale("50m"), facecolor="#f2f2f0", zorder=0)
    ax.add_feature(cf.OCEAN.with_scale("50m"), facecolor="white", zorder=0)
    ax.add_feature(cf.COASTLINE.with_scale("50m"), lw=0.4, edgecolor=INK2, zorder=1)
    ax.add_feature(cf.BORDERS.with_scale("50m"), lw=0.3, edgecolor="#9a9994", zorder=1)
    ax.add_feature(cf.RIVERS.with_scale("50m"), lw=0.4, edgecolor="#a9c3da", zorder=1)
    gl = ax.gridlines(draw_labels=True, lw=0.3, color="#d9d8d4", xlocs=range(-10, 45, 10),
                      ylocs=range(35, 61, 5))
    gl.top_labels = gl.right_labels = False
    gl.xlabel_style = gl.ylabel_style = {"size": 7, "color": INK2}
    for s in ax.spines.values():
        s.set_linewidth(0.5); s.set_edgecolor(INK2)

    T = ccrs.PlateCarree()
    for _, r in cat.iterrows():
        if r.regulated:
            ax.scatter(r.lon, r.lat, marker="o", s=125, facecolor="white", edgecolor=GREY,
                       linewidths=1.0, linestyle=(0, (2, 1.5)), zorder=3, transform=T)
        else:
            m = OUTER[r.category][0]
            ax.scatter(r.lon, r.lat, marker=m, s=125 if m != "^" else 150, facecolor="white",
                       edgecolor=INK, linewidths=1.0, zorder=3, transform=T)
        ax.scatter(r.lon, r.lat, marker="o", s=52, facecolor=colours[r.river], edgecolor=INK,
                   linewidths=0.3, zorder=4, transform=T)
        ax.text(r.lon, r.lat, r.pos, ha="center", va="center", fontsize=4.6, fontweight="bold",
                color="white", zorder=5, transform=T,
                path_effects=[pe.withStroke(linewidth=1.0, foreground=INK)])

    kw = dict(frameon=True, framealpha=1, edgecolor="#bdbcb7", fontsize=7.5, title_fontsize=8,
              borderpad=0.6, labelspacing=0.45, handletextpad=0.6)
    h_river = [Line2D([], [], marker="o", ls="", ms=7, mfc=colours[n], mec=INK, mew=0.4,
                      label=PLACE.get(n, n)) for n in names]
    fig.legend(handles=h_river, title="River (inner dot)", loc="upper left",
               bbox_to_anchor=(0.715, 0.975), ncols=2, columnspacing=0.8, **kw)
    h_cat = [Line2D([], [], marker=m, ls="", ms=9, mfc="white", mec=INK, mew=1.1, label=lab)
             for m, lab in OUTER.values()]
    h_cat.append(Line2D([], [], marker="o", ls="", ms=9, mfc="white", mec=GREY, mew=1.1,
                        label="Test not informative"))
    fig.legend(handles=h_cat, title="Significant (outer symbol)",
               loc="upper left", bbox_to_anchor=(0.715, 0.455), **kw)
    h_pos = [Line2D([], [], ls="", label=t) for t in ("1 = upstream", "2 = midstream", "3 = downstream")]
    fig.legend(handles=h_pos, title="Location (number)", loc="upper left",
               bbox_to_anchor=(0.876, 0.455), handlelength=0, **{**kw, "handletextpad": 0})
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/fig04_map.{ext}", dpi=300 if ext == "png" else None,
                    facecolor="white")
    plt.close(fig)

    caption = ("Figure 4: Locations where droughts are followed by floods more often than expected under the "
               "stratified null (Monte Carlo p < 0.05, Table 3). Outer symbol: significant in both periods (circle), "
               "in period 1 only (diamond), in period 2 only (square), in neither period (triangle); dashed grey circle: the "
               "four locations where the SRI detects very few droughts and the test is not informative. "
               "Inner dot: river. Number: position along the river (1 upstream, 2 midstream, 3 downstream).")
    open(f"{OUT}/caption_en.md", "w").write(caption + "\n")
    counts = cat[~cat.regulated].category.value_counts().to_dict()
    open(f"{OUT}/README.md", "w").write(
        "# Figuur 4 onder C'\n\nScript: scripts/44_figure4_map.py. Bron: figure4_categories.csv (script 39).\n\n"
        f"Categorieën zonder de vier niet-toetsbare locaties: {counts}. Niet toetsbaar (grijze "
        f"gestippelde cirkel): {', '.join(cat[cat.regulated].village)}.\n\nOpbouw als de ingediende figuur: "
        "buitensymbool categorie, binnenstip rivier (tab20, alfabetisch), cijfer positie.\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/44_figure4_map.py\npython: {platform.python_version()}\n"
                 f"inputs:\n  {CAT}: {sha256(CAT)}\n  {NB}: {sha256(NB)}\n")
    print(counts)


if __name__ == "__main__":
    main()
