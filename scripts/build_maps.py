#!/usr/bin/env python3
"""Choropleth maps of Karviná voting districts (PS 2025) for SPOLU, Piráti,
STAN and the three combined ("DOHROMADY").

Geometry: ČSÚ "Volební okrsky pro volby do PS 2025 - generalizované"
          (geodata.csu.gov.cz), joined on okrsek number == cislo.
Results : output/karvina_okrsky_vysledky.csv (see build_data.py).

Each district is shaded darker the more votes the grouping received; every
district is labelled with both the number of votes and the percentage of
valid votes.
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

# grouping -> (vote column, pct column, colormap, czech title)
GROUPS = {
    "DOHROMADY": ("DOHROMADY_hlasy", "DOHROMADY_pct", "Purples",
                  "SPOLU + Piráti + STAN dohromady"),
    "SPOLU":     ("SPOLU_hlasy", "SPOLU_pct", "Blues",
                  "SPOLU (ODS, KDU-ČSL, TOP 09)"),
    "Pirati":    ("Pirati_hlasy", "Pirati_pct", "Greens",
                  "Piráti (Česká pirátská strana)"),
    "STAN":      ("STAN_hlasy", "STAN_pct", "Oranges",
                  "STAN (Starostové a nezávislí)"),
}

# --- load + join -----------------------------------------------------------
gdf = gpd.read_file(ROOT / "data" / "karvina_okrsky.geojson").to_crs(5514)
res = pd.read_csv(OUT / "karvina_okrsky_vysledky.csv")
gdf["cislo"] = gdf["cislo"].astype(int)
gdf = gdf.merge(res, left_on="cislo", right_on="okrsek", how="left")
assert gdf["okrsek"].notna().all(), "okrsek bez výsledku!"

STROKE = [pe.withStroke(linewidth=2.2, foreground="white")]


def draw(ax, col, pct_col, cmap, title, label_mode):
    vmax = gdf[col].max()
    norm = Normalize(vmin=0, vmax=vmax)
    gdf.plot(ax=ax, column=col, cmap=cmap, norm=norm,
             edgecolor="#444", linewidth=0.4)
    for _, r in gdf.iterrows():
        p = r.geometry.representative_point()
        if label_mode == "full":
            txt = f"{r['cislo']:.0f}\n{r[col]:.0f}\n{r[pct_col]:.1f}%"
            fs = 6.0
        else:                       # overview: just the district number
            txt = f"{r['cislo']:.0f}"
            fs = 5.5
        ax.annotate(txt, (p.x, p.y), ha="center", va="center",
                    fontsize=fs, fontweight="bold", path_effects=STROKE)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_axis_off()
    return ScalarMappable(norm=norm, cmap=cmap)


# bounding box of the dense central cluster (smallest-area third of okrsky)
gdf["_area"] = gdf.geometry.area
small = gdf.nsmallest(len(gdf) // 3, "_area")
cxmin, cymin, cxmax, cymax = small.total_bounds
mx = (cxmax - cxmin) * 0.06
my = (cymax - cymin) * 0.06
CENTER = (cxmin - mx, cxmax + mx, cymin - my, cymax + my)

# --- 1) four detailed standalone maps (number + votes + %) -----------------
for key, (col, pct_col, cmap, title) in GROUPS.items():
    fig, (ax, axz) = plt.subplots(1, 2, figsize=(20, 11),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    sm = draw(ax, col, pct_col, cmap, title + " – celé město", "full")

    # zoom of the central cluster (same choropleth, same scale)
    draw(axz, col, pct_col, cmap, title + " – detail centra", "full")
    axz.set_xlim(CENTER[0], CENTER[1])
    axz.set_ylim(CENTER[2], CENTER[3])
    # outline the zoom area on the overview map
    ax.add_patch(plt.Rectangle((CENTER[0], CENTER[2]), CENTER[1] - CENTER[0],
                               CENTER[3] - CENTER[2], fill=False,
                               edgecolor="red", linewidth=1.2, linestyle="--"))

    cb = fig.colorbar(sm, ax=[ax, axz], shrink=0.6, pad=0.01)
    cb.set_label("počet hlasů v okrsku", fontsize=9)
    tot = res[col].sum()
    totp = round(100 * tot / res["platne_hlasy"].sum(), 2)
    fig.suptitle(f"Karviná – volby do PS 2025 – {title}\n"
                 f"celkem {tot} hlasů ({totp} % platných hlasů)   |   "
                 f"popisek okrsku: číslo / počet hlasů / % platných hlasů   |   "
                 f"tmavší = více hlasů",
                 fontsize=13, fontweight="bold", y=0.97)
    fp = OUT / f"karvina_mapa_{key}.png"
    fig.savefig(fp, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("napsáno:", fp.name)

# --- 2) 2x2 overview comparing all four groupings (shaded by %) ------------
fig, axes = plt.subplots(2, 2, figsize=(16, 16))
for ax, (key, (col, pct_col, cmap, title)) in zip(axes.ravel(), GROUPS.items()):
    vmax = gdf[pct_col].max()
    norm = Normalize(vmin=0, vmax=vmax)
    gdf.plot(ax=ax, column=pct_col, cmap=cmap, norm=norm,
             edgecolor="#444", linewidth=0.4)
    for _, r in gdf.iterrows():
        p = r.geometry.representative_point()
        ax.annotate(f"{r['cislo']:.0f}", (p.x, p.y), ha="center", va="center",
                    fontsize=5, fontweight="bold", path_effects=STROKE)
    tot = res[col].sum()
    totp = round(100 * tot / res["platne_hlasy"].sum(), 2)
    ax.set_title(f"{title}\ncelkem {tot} hlasů ({totp} %)",
                 fontsize=10, fontweight="bold")
    ax.set_axis_off()
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                      shrink=0.55, pad=0.01)
    cb.set_label("% platných hlasů", fontsize=8)
fig.suptitle("Karviná – volby do Poslanecké sněmovny 2025 podle volebních okrsků\n"
             "barva = % platných hlasů pro dané uskupení (tmavší = více)",
             fontsize=14, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fp = OUT / "karvina_mapa_prehled_procenta.png"
fig.savefig(fp, dpi=150, bbox_inches="tight")
plt.close(fig)
print("napsáno:", fp.name)
