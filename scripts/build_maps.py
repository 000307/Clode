#!/usr/bin/env python3
"""Choropleth maps of voting districts for the tracked groupings (SPOLU /
Piráti / STAN where they ran separately, otherwise the real coalitions that
ran) for every configured city, for the 2025 parliamentary and the 2022
municipal election.

Each district is shaded darker the more votes the grouping received and is
labelled with číslo / počet hlasů / % platných hlasů. Detailed maps add a
zoom of the dense city centre.

Outputs: output/<slug>/<slug>_<election>_mapa_*.png and *_prehled.png
"""
import math
from pathlib import Path

import geopandas as gpd
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from cities import CITIES, DEFAULT_META, DOHRO_CMAP, meta_for

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
STROKE = [pe.withStroke(linewidth=2.2, foreground="white")]


def draw(ax, gdf, col, pct_col, cmap, title, fs=5.6, stats=True):
    norm = Normalize(vmin=0, vmax=max(gdf[col].max(), 1))
    gdf.plot(ax=ax, column=col, cmap=cmap, norm=norm,
             edgecolor="#444", linewidth=0.4)
    for _, r in gdf.iterrows():
        p = r.geometry.representative_point()
        txt = (f"{r['cislo']:.0f}\n{r[col]:.0f}\n{r[pct_col]:.1f}%"
               if stats else f"{r['cislo']:.0f}")
        ax.annotate(txt, (p.x, p.y), ha="center", va="center", fontsize=fs,
                    fontweight="bold", path_effects=STROKE)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_axis_off()
    return ScalarMappable(norm=norm, cmap=cmap)


def make_maps(slug, election, year_label, pct_note, geojson, csv_path,
              groups, metas, note):
    gdf = gpd.read_file(geojson).to_crs(5514)
    res = pd.read_csv(csv_path)
    gdf["cislo"] = gdf["cislo"].astype(int)
    gdf = gdf.merge(res, left_on="cislo", right_on="okrsek", how="left")
    assert gdf["okrsek"].notna().all(), f"{slug}/{election}: okrsek bez výsledku"

    city = CITIES[slug]["name"]
    dohro_title = " + ".join(metas[g]["short"] for g in groups) + " dohromady"
    titles = {g: metas[g]["label"] for g in groups}
    titles["DOHROMADY"] = dohro_title
    cmaps = {g: metas[g]["cmap"] for g in groups}
    cmaps["DOHROMADY"] = DOHRO_CMAP
    panels = ["DOHROMADY"] + groups

    gdf["_area"] = gdf.geometry.area
    sb = gdf.nsmallest(max(len(gdf) // 3, 1), "_area").total_bounds
    mx, my = (sb[2] - sb[0]) * 0.06 or 1, (sb[3] - sb[1]) * 0.06 or 1
    CEN = (sb[0] - mx, sb[2] + mx, sb[1] - my, sb[3] + my)

    outdir = OUT / slug
    outdir.mkdir(parents=True, exist_ok=True)
    single = len(gdf) == 1

    # 1) detailed standalone maps (city + centre zoom; zoom skipped if 1 okrsek)
    for g in panels:
        col, pct_col = f"{g}_hlasy", f"{g}_pct"
        if single:
            fig, ax = plt.subplots(figsize=(11, 11))
            sm = draw(ax, gdf, col, pct_col, cmaps[g], titles[g], fs=9)
        else:
            fig, (ax, axz) = plt.subplots(1, 2, figsize=(20, 11),
                                          gridspec_kw={"width_ratios": [1.15, 1]})
            sm = draw(ax, gdf, col, pct_col, cmaps[g], titles[g] + " – celé město")
            draw(axz, gdf, col, pct_col, cmaps[g], titles[g] + " – detail centra")
            axz.set_xlim(CEN[0], CEN[1])
            axz.set_ylim(CEN[2], CEN[3])
            ax.add_patch(plt.Rectangle((CEN[0], CEN[2]), CEN[1] - CEN[0],
                                       CEN[3] - CEN[2], fill=False,
                                       edgecolor="red", linewidth=1.2, ls="--"))
        cb = fig.colorbar(sm, ax=fig.axes, shrink=0.6, pad=0.01)
        cb.set_label("počet hlasů v okrsku", fontsize=9)
        tot = res[col].sum()
        totp = round(res[pct_col].mul(res["platne_hlasy"]).sum()
                     / res["platne_hlasy"].sum(), 2)
        sub = (f"celkem {tot} hlasů ({totp} %{pct_note})   |   "
               f"popisek okrsku: číslo / počet hlasů / % platných hlasů   |   "
               f"tmavší = více hlasů")
        fig.suptitle(f"{city} – {year_label} – {titles[g]}\n{sub}",
                     fontsize=13, fontweight="bold", y=0.97)
        fig.savefig(outdir / f"{slug}_{election}_mapa_{g}.png",
                    dpi=150, bbox_inches="tight")
        plt.close(fig)

    # 2) overview comparing all panels (shaded by %)
    n = len(panels)
    ncol = 2 if n == 4 else min(n, 3)
    nrow = math.ceil(n / ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(8 * ncol, 8 * nrow),
                             squeeze=False)
    flat = axes.ravel()
    fs = 4.8 if len(gdf) > 55 else (9 if single else 6)
    for ax, g in zip(flat, panels):
        col, pct_col = f"{g}_hlasy", f"{g}_pct"
        norm = Normalize(vmin=0, vmax=max(gdf[pct_col].max(), 0.1))
        gdf.plot(ax=ax, column=pct_col, cmap=cmaps[g], norm=norm,
                 edgecolor="#444", linewidth=0.4)
        for _, r in gdf.iterrows():
            p = r.geometry.representative_point()
            ax.annotate(f"{r['cislo']:.0f}", (p.x, p.y), ha="center",
                        va="center", fontsize=fs, fontweight="bold",
                        path_effects=STROKE)
        tot = res[col].sum()
        totp = round(res[pct_col].mul(res["platne_hlasy"]).sum()
                     / res["platne_hlasy"].sum(), 2)
        ax.set_title(f"{titles[g]}\ncelkem {tot} hlasů ({totp} %)",
                     fontsize=10, fontweight="bold")
        ax.set_axis_off()
        cb = fig.colorbar(ScalarMappable(norm=norm, cmap=cmaps[g]), ax=ax,
                          shrink=0.55, pad=0.01)
        cb.set_label("% platných hlasů" + pct_note, fontsize=8)
    for ax in flat[n:]:
        ax.set_axis_off()
    nt = ("\n" + note) if note else ""
    fig.suptitle(f"{city} – {year_label} podle volebních okrsků\n"
                 f"barva = % platných hlasů pro dané uskupení (tmavší = více)"
                 f"{nt}", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(outdir / f"{slug}_{election}_prehled.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"hotovo: {slug}/{election}  ({n} panelů, {len(gdf)} okrsků)")


if __name__ == "__main__":
    for slug, city in CITIES.items():
        # PS 2025 – always SPOLU / Piráti / STAN
        make_maps(slug, "ps2025", "volby do PS 2025", "",
                  DATA / f"{slug}_ps2025.geojson",
                  OUT / slug / f"{slug}_ps2025_okrsky.csv",
                  ["SPOLU", "Pirati", "STAN"],
                  {g: meta_for(g, {}) for g in DEFAULT_META}, "")

        # KV 2022 – local lists (skip if none of the subjects ran)
        if not city["kv2022"]:
            continue
        groups = list(city["kv2022"].keys())
        metas = {g: meta_for(g, city["kv2022_meta"]) for g in groups}
        make_maps(slug, "kv2022", "komunální volby 2022",
                  " – přepočtený základ",
                  DATA / f"{slug}_kv2022.geojson",
                  OUT / slug / f"{slug}_kv2022_okrsky.csv",
                  groups, metas, city["kv2022_note"])
