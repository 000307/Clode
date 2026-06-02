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


for c in CSVS:
    get(VOLBY + c, DATA / c)
for z in ZIPS:
    get_zip_member(VOLBY + z)

# only the Karviná subset of polygons is needed
get(KARVINA_GEOJSON, DATA / "karvina_okrsky.geojson")
print("hotovo.")
