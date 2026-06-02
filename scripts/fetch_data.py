#!/usr/bin/env python3
"""Download the raw source data for the Karviná / Havířov / Orlová election
maps (parliamentary PS 2025 + municipal KV 2022).

Sources (open data, CC-BY 4.0):
  * Results per polling district (okrsek): Czech Statistical Office / volby.cz
  * Polling-district polygons:             ČSÚ geodata (generalised)

Run once before build_data.py / build_maps.py. The large national CSVs are
re-fetchable and are not stored in git; only the small per-city geojson
subsets (data/<slug>_<election>.geojson) are kept.
"""
import io
import json
import urllib.request
import zipfile
from pathlib import Path

from cities import CITIES

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

PS = "https://www.volby.cz/opendata/ps2025/csv_od/"
KV = "https://www.volby.cz/opendata/kv2022/"
PS_GEO = ("https://geodata.csu.gov.cz/server/rest/services/Hosted/"
          "Volebni_okrsky_2025_gdb/FeatureServer/1/query?"
          "where=kod_obec%3D%27{code}%27"
          "&outFields=kod,cislo,kod_obec,naz_obec&outSR=4326&f=geojson")
KV_GEO_NATIONAL = KV + "geo/vol_okrsky_2022g100.geojson"


def get(url, dest):
    print("stahuji", url)
    with urllib.request.urlopen(url, timeout=180) as r:
        dest.write_bytes(r.read())


def get_zip_members(url, names):
    """Extract only the given file basenames from a zip (later wins => csv_od)."""
    print("stahuji", url)
    with urllib.request.urlopen(url, timeout=180) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
        for name in z.namelist():
            if Path(name).name in names:
                (DATA / Path(name).name).write_bytes(z.read(name))


# --- national result CSVs --------------------------------------------------
get(PS + "psrkl.csv", DATA / "psrkl.csv")                 # KSTRANA -> party
get_zip_members(PS + "pst4.zip", {"pst4.csv"})            # okrsek totals
get_zip_members(PS + "pst4p.zip", {"pst4p.csv"})          # per-party votes
get_zip_members(KV + "KV2022_data_20260328_csv.zip", {"kvt3.csv", "kvhl.csv"})
get_zip_members(KV + "KV2022reg20260328_csv.zip", {"kvros.csv", "kvrk.csv"})

# --- PS 2025 polygons: one small per-city query each -----------------------
for slug, city in CITIES.items():
    out = DATA / f"{slug}_ps2025.geojson"
    get(PS_GEO.format(code=city["code"]), out)
    n = len(json.loads(out.read_text(encoding="utf-8"))["features"])
    print(f"  {city['name']} PS2025: {n} okrsků")

# --- KV 2022 polygons: download national file once, slice per city ---------
get(KV_GEO_NATIONAL, DATA / "vol_okrsky_2022.geojson")
nat = json.loads((DATA / "vol_okrsky_2022.geojson").read_text(encoding="utf-8"))
by_obec = {}
for f in nat["features"]:
    by_obec.setdefault(str(f["properties"].get("OBEC")), []).append(f)
for slug, city in CITIES.items():
    feats = []
    for f in by_obec.get(city["code"], []):
        p = f["properties"]
        feats.append({"type": "Feature", "geometry": f["geometry"],
                      "properties": {"kod": p.get("KOD"),
                                     "cislo": int(p["CISLO"]),
                                     "kod_obec": city["code"],
                                     "naz_obec": city["name"]}})
    (DATA / f"{slug}_kv2022.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": feats},
                   ensure_ascii=False), encoding="utf-8")
    print(f"  {city['name']} KV2022: {len(feats)} okrsků")

print("hotovo.")
