#!/usr/bin/env python3
"""Download the raw source data for the Karviná PS-2025 maps.

Sources (open data, CC-BY 4.0):
  * Results per polling district (okrsek): Czech Statistical Office / volby.cz
  * Polling-district polygons:             ČSÚ geodata (generalised, PS 2025)

Run once before build_data.py / build_maps.py. Re-fetchable, so the large
national CSVs are not stored in git.
"""
import io
import urllib.request
import zipfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(exist_ok=True)

VOLBY = "https://www.volby.cz/opendata/ps2025/csv_od/"
# plain CSV codebooks + per-okrsek totals
CSVS = ["psrkl.csv"]                 # KSTRANA -> party name mapping
# zipped per-okrsek CSVs
ZIPS = ["pst4.zip", "pst4p.zip"]     # pst4 = okrsek totals, pst4p = per party

GEOJSON_ZIP = ("https://geodata.csu.gov.cz/as/data/distribuce/Hosted/"
               "Volebni_okrsky_2025_gdb/FeatureServer/1/geojson.zip")
# ArcGIS REST query that returns only Karviná (obec 598917) in WGS-84
KARVINA_GEOJSON = (
    "https://geodata.csu.gov.cz/server/rest/services/Hosted/"
    "Volebni_okrsky_2025_gdb/FeatureServer/1/query?"
    "where=kod_obec%3D%27598917%27&outFields=kod,cislo,kod_obec,naz_obec"
    "&outSR=4326&f=geojson")


def get(url, dest):
    print("stahuji", url)
    with urllib.request.urlopen(url, timeout=120) as r:
        dest.write_bytes(r.read())


def get_zip_member(url):
    print("stahuji", url)
    with urllib.request.urlopen(url, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
        for name in z.namelist():
            (DATA / Path(name).name).write_bytes(z.read(name))
            print("  rozbaleno", name)


def get_zip_member_from(url, names):
    """Extract only the given file basenames from a zip (prefers csv_od/)."""
    print("stahuji", url)
    with urllib.request.urlopen(url, timeout=120) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
        for name in z.namelist():
            if Path(name).name in names:
                (DATA / Path(name).name).write_bytes(z.read(name))
                print("  rozbaleno", name)


for c in CSVS:
    get(VOLBY + c, DATA / c)
for z in ZIPS:
    get_zip_member(VOLBY + z)

# only the Karviná subset of polygons is needed
get(KARVINA_GEOJSON, DATA / "karvina_okrsky.geojson")

# ---------------------------------------------------------------------------
# Komunální volby 2022 (municipal election)
# ---------------------------------------------------------------------------
KV = "https://www.volby.cz/opendata/kv2022/"
# results: kvt3 = okrsek totals, kvhl = list votes per okrsek
get_zip_member_from(KV + "KV2022_data_20260328_csv.zip",
                    {"kvt3.csv", "kvhl.csv"})
# registration: kvros = lists per council, kvrk = candidates (for slate sizes)
get_zip_member_from(KV + "KV2022reg20260328_csv.zip",
                    {"kvros.csv", "kvrk.csv"})

# national 2022 okrsky polygons -> filter to Karviná, normalise prop names
import json  # noqa: E402
get(KV + "geo/vol_okrsky_2022g100.geojson", DATA / "vol_okrsky_2022.geojson")
d = json.loads((DATA / "vol_okrsky_2022.geojson").read_text(encoding="utf-8"))
kv = [f for f in d["features"] if str(f["properties"].get("OBEC")) == "598917"]
for f in kv:
    p = f["properties"]
    f["properties"] = {"kod": p.get("KOD"), "cislo": int(p["CISLO"]),
                       "kod_obec": "598917", "naz_obec": "Karviná"}
(DATA / "karvina_okrsky_2022.geojson").write_text(
    json.dumps({"type": "FeatureCollection", "features": kv},
               ensure_ascii=False), encoding="utf-8")
print(f"Karviná 2022: {len(kv)} okrsků -> karvina_okrsky_2022.geojson")
print("hotovo.")
