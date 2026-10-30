"""Figuur 4: kaart van de locaties met significante droogte-tot-flood-samenhang onder C'.

Leest results/2026-10-27_table3_eca_cprime/figure4_categories.csv (script 39):
per locatie of de Monte Carlo-p onder nul C' in periode 1, 2, beide of geen van
beide onder 0,05 ligt, en of de locatie gemarkeerd is (D-12, de vier
gereguleerde locaties waar de SRI vrijwel geen droogtes vindt). Coördinaten uit
de locatielijst van de notebook, dezelfde bron als script 27.

Symbolen als in de ingediende figuur 4: cirkel beide periodes, ruit alleen
periode 1, vierkant alleen periode 2; nieuw: kruis voor geen van beide, elke
categorie in een eigen kleur (Okabe-Ito, besluit Floris 30 oktober), open
symbool voor de gemarkeerde locaties. Kaartlaag: Natural Earth 50m via cartopy.

Uitvoer in results/2026-10-28_figure4_map/: fig04_map.png (300 dpi), fig04_map.pdf,
caption_en.md, README.md, manifest.yaml.

Draaien vanuit de repo-root:
  uv run --frozen python scripts/44_figure4_map.py
"""
import os, re, ast, json, hashlib, platform
import pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs, cartopy.feature as cf

CAT = "results/2026-10-27_table3_eca_cprime/figure4_categories.csv"
NB = "notebooks/drought_to_flood_europe_r1_published.ipynb"
OUT = "results/2026-10-28_figure4_map"
EXTENT = (-11, 42, 35.5, 60.5)
INK, INK2 = "#0b0b0b", "#52514e"
# symbool, kleur, legendatekst per categorie (kleuren Okabe-Ito, kleurenblindveilig)
MARK = {"both": ("o", "#0072b2", "Both periods"), "first only": ("D", "#e69f00", "Period 1 only"),
        "second only": ("s", "#009e73", "Period 2 only"), "none": ("X", "#d55e00", "Neither period")}


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
    coords = {(r["river"], l["village"]): (l["latitude"], l["longitude"])
              for r in rivers for l in r["locations"]}
    cat["lat"] = [coords[(r, v)][0] for r, v in zip(cat.river, cat.village)]
    cat["lon"] = [coords[(r, v)][1] for r, v in zip(cat.river, cat.village)]
    assert len(cat) == 48 and cat.lat.notna().all()

    plt.rcParams.update({"font.size": 8, "pdf.fonttype": 42})
    fig = plt.figure(figsize=(7.2, 5.2))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent(EXTENT, crs=ccrs.PlateCarree())
    ax.add_feature(cf.LAND.with_scale("50m"), facecolor="#f3f2ee", zorder=0)
    ax.add_feature(cf.OCEAN.with_scale("50m"), facecolor="#e3eaf0", zorder=0)
    ax.add_feature(cf.COASTLINE.with_scale("50m"), lw=0.4, edgecolor=INK2, zorder=1)
    ax.add_feature(cf.BORDERS.with_scale("50m"), lw=0.25, edgecolor="#9a9994", zorder=1)
    ax.add_feature(cf.RIVERS.with_scale("50m"), lw=0.5, edgecolor="#7fa6c9", zorder=1)
    for s in ax.spines.values():
        s.set_linewidth(0.4); s.set_edgecolor(INK2)

    for c, (m, col, _) in MARK.items():
        for reg in (False, True):
            sub = cat[(cat.category == c) & (cat.regulated == reg)]
            if sub.empty:
                continue
            ax.scatter(sub.lon, sub.lat, marker=m, s=46 if m != "X" else 54,
                       facecolor="white" if reg else col, edgecolor=col if reg else "white",
                       linewidths=1.4 if reg else 0.5, zorder=3, transform=ccrs.PlateCarree())
    handles = [Line2D([], [], marker=m, ls="", ms=7, mfc=col, mec="white", mew=0.5, label=lab)
               for m, col, lab in MARK.values()]
    handles.append(Line2D([], [], marker="o", ls="", ms=7, mfc="white", mec=INK, mew=1.4,
                          label="Open symbol: SRI detects very few droughts"))
    ax.legend(handles=handles, loc="upper right", fontsize=7, frameon=True, framealpha=0.95,
              edgecolor="#cfcec9", borderpad=0.7)
    for ext in ("png", "pdf"):
        fig.savefig(f"{OUT}/fig04_map.{ext}", dpi=300 if ext == "png" else None,
                    bbox_inches="tight", facecolor="white")
    plt.close(fig)

    caption = ("Figure 4: Locations where droughts are followed by floods more often than expected "
               "under the stratified null (Monte Carlo p < 0.05, Table 3): in both periods (circle), "
               "in period 1 only (diamond), in period 2 only (square), in neither (cross), each category in its own colour. Open symbols: "
               "the four locations where the SRI detects very few droughts and the test is not informative.")
    open(f"{OUT}/caption_en.md", "w").write(caption + "\n")
    counts = cat.category.value_counts().to_dict()
    open(f"{OUT}/README.md", "w").write(
        "# Figuur 4 onder C'\n\nScript: scripts/44_figure4_map.py. Bron: figure4_categories.csv (script 39).\n\n"
        f"Categorieën: {counts}. Gemarkeerd (open symbool): "
        f"{', '.join(cat[cat.regulated].village)}.\n\nKaartlaag: Natural Earth 50m via cartopy "
        "(land, oceaan, kustlijn, landsgrenzen, rivieren).\n")
    with open(f"{OUT}/manifest.yaml", "w") as fh:
        fh.write(f"script: scripts/44_figure4_map.py\npython: {platform.python_version()}\n"
                 f"inputs:\n  {CAT}: {sha256(CAT)}\n  {NB}: {sha256(NB)}\n")
    print(counts)


if __name__ == "__main__":
    main()
