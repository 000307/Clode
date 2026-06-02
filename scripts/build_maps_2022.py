#!/usr/bin/env python3
"""Choropleth maps of Karviná voting districts for the 2022 MUNICIPAL election
(komunální volby) for SPOLU, Piráti, STAN and the three combined.

Geometry: ČSÚ "Volební okrsky 2022" (vol_okrsky_2022g100), Karviná subset.
Results : output/karvina_2022_okrsky_vysledky.csv (see build_data_2022.py).

Percentages are the official municipal share (přepočtený základ). Each
district is shaded darker the more votes the grouping received and labelled
with číslo / počet hlasů / % platných hlasů.
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"

GROUPS = {
    "DOHROMADY": ("DOHROMADY_hlasy", "DOHROMADY_pct", "Purples",
                  "SPOLU + Piráti + STAN dohromady"),
    "SPOLU":     ("SPOLU_hlasy", "SPOLU_pct", "Blues",
                  "SPOLU (KDU-ČSL, ODS, TOP 09)"),
    "Pirati":    ("Pirati_hlasy", "Pirati_pct", "Greens",
                  "Piráti (Česká pirátská strana)"),
    "STAN":      ("STAN_hlasy", "STAN_pct", "Oranges",
                  "STAN (Starostové a nezávislí)"),
}

gdf = gpd.read_file(ROOT / "data" / "karvina_okrsky_2022.geojson").to_crs(5514)
res = pd.read_csv(OUT / "karvina_2022_okrsky_vysledky.csv")
gdf["cislo"] = gdf["cislo"].astype(int)
gdf = gdf.merge(res, left_on="cislo", right_on="okrsek", how="left")
assert gdf["okrsek"].notna().all(), "okrsek bez výsledku!"

STROKE = [pe.withStroke(linewidth=2.2, foreground="white")]


def draw(ax, col, pct_col, cmap, title):
    norm = Normalize(vmin=0, vmax=gdf[col].max())
    gdf.plot(ax=ax, column=col, cmap=cmap, norm=norm,
             edgecolor="#444", linewidth=0.4)
    for _, r in gdf.iterrows():
        p = r.geometry.representative_point()
        ax.annotate(f"{r['cislo']:.0f}\n{r[col]:.0f}\n{r[pct_col]:.1f}%",
                    (p.x, p.y), ha="center", va="center", fontsize=5.6,
                    fontweight="bold", path_effects=STROKE)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_axis_off()
    return ScalarMappable(norm=norm, cmap=cmap)


gdf["_area"] = gdf.geometry.area
small = gdf.nsmallest(len(gdf) // 3, "_area")
cxmin, cymin, cxmax, cymax = small.total_bounds
mx, my = (cxmax - cxmin) * 0.06, (cymax - cymin) * 0.06
CENTER = (cxmin - mx, cxmax + mx, cymin - my, cymax + my)

# --- four detailed standalone maps (number + votes + %) --------------------
for key, (col, pct_col, cmap, title) in GROUPS.items():
    fig, (ax, axz) = plt.subplots(1, 2, figsize=(20, 11),
                                  gridspec_kw={"width_ratios": [1.15, 1]})
    sm = draw(ax, col, pct_col, cmap, title + " – celé město")
    draw(axz, col, pct_col, cmap, title + " – detail centra")
    axz.set_xlim(CENTER[0], CENTER[1])
    axz.set_ylim(CENTER[2], CENTER[3])
    ax.add_patch(plt.Rectangle((CENTER[0], CENTER[2]), CENTER[1] - CENTER[0],
                               CENTER[3] - CENTER[2], fill=False,
                               edgecolor="red", linewidth=1.2, linestyle="--"))
    cb = fig.colorbar(sm, ax=[ax, axz], shrink=0.6, pad=0.01)
    cb.set_label("počet hlasů v okrsku", fontsize=9)
    tot = res[col].sum()
    totp = round(res[pct_col].mul(res["platne_hlasy"]).sum()
                 / res["platne_hlasy"].sum(), 2)
    fig.suptitle(f"Karviná – komunální volby 2022 – {title}\n"
                 f"celkem {tot} hlasů ({totp} % – přepočtený základ)   |   "
                 f"popisek okrsku: číslo / počet hlasů / % platných hlasů   |   "
                 f"tmavší = více hlasů",
                 fontsize=13, fontweight="bold", y=0.97)
    fp = OUT / f"karvina_2022_mapa_{key}.png"
    fig.savefig(fp, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("napsáno:", fp.name)

# --- 2x2 overview comparing all four groupings (shaded by %) ---------------
fig, axes = plt.subplots(2, 2, figsize=(16, 16))
for ax, (key, (col, pct_col, cmap, title)) in zip(axes.ravel(), GROUPS.items()):
    norm = Normalize(vmin=0, vmax=gdf[pct_col].max())
    gdf.plot(ax=ax, column=pct_col, cmap=cmap, norm=norm,
             edgecolor="#444", linewidth=0.4)
    for _, r in gdf.iterrows():
        p = r.geometry.representative_point()
        ax.annotate(f"{r['cislo']:.0f}", (p.x, p.y), ha="center", va="center",
                    fontsize=4.8, fontweight="bold", path_effects=STROKE)
    tot = res[col].sum()
    totp = round(res[pct_col].mul(res["platne_hlasy"]).sum()
                 / res["platne_hlasy"].sum(), 2)
    ax.set_title(f"{title}\ncelkem {tot} hlasů ({totp} %)",
                 fontsize=10, fontweight="bold")
    ax.set_axis_off()
    cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                      shrink=0.55, pad=0.01)
    cb.set_label("% platných hlasů (přepočtený základ)", fontsize=8)
fig.suptitle("Karviná – komunální volby 2022 podle volebních okrsků\n"
             "barva = % platných hlasů pro dané uskupení (tmavší = více)",
             fontsize=14, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fp = OUT / "karvina_2022_mapa_prehled_procenta.png"
fig.savefig(fp, dpi=150, bbox_inches="tight")
plt.close(fig)
print("napsáno:", fp.name)
