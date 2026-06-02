#!/usr/bin/env python3
"""Extract Karviná (obec 598917) per-okrsek results for SPOLU, Piráti, STAN
from the Czech Statistical Office open data (volby.cz, PS 2025).

Outputs: output/karvina_okrsky_vysledky.csv  – one row per voting district.

Party ballot numbers (KSTRANA) for PS 2025, from psrkl.csv:
    11 = SPOLU (ODS, KDU-ČSL, TOP 09)
    16 = Piráti (Česká pirátská strana)
    23 = STAN (STAROSTOVÉ A NEZÁVISLÍ)
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

OBEC = "598917"          # Karviná
PARTIES = {11: "SPOLU", 16: "Pirati", 23: "STAN"}

# --- valid votes (denominator) per okrsek, from pst4.csv ---
valid = {}          # okrsek -> platné hlasy celkem
voters = {}         # okrsek -> voliči v seznamu
with open(DATA / "pst4.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["OBEC"] != OBEC:
            continue
        ok = int(row["OKRSEK"])
        valid[ok] = int(row["PL_HL_CELK"])
        voters[ok] = int(row["VOL_SEZNAM"])

# --- party votes per okrsek, from pst4p.csv ---
votes = {ok: {p: 0 for p in PARTIES} for ok in valid}
with open(DATA / "pst4p.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["OBEC"] != OBEC:
            continue
        kstrana = int(row["KSTRANA"])
        if kstrana in PARTIES:
            votes[int(row["OKRSEK"])][kstrana] = int(row["POC_HLASU"])

# --- write tidy table ---
def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0

rows = []
for ok in sorted(valid):
    v = votes[ok]
    spolu, pir, stan = v[11], v[16], v[23]
    comb = spolu + pir + stan
    pl = valid[ok]
    rows.append({
        "okrsek": ok,
        "volici": voters[ok],
        "platne_hlasy": pl,
        "SPOLU_hlasy": spolu, "SPOLU_pct": pct(spolu, pl),
        "Pirati_hlasy": pir, "Pirati_pct": pct(pir, pl),
        "STAN_hlasy": stan, "STAN_pct": pct(stan, pl),
        "DOHROMADY_hlasy": comb, "DOHROMADY_pct": pct(comb, pl),
    })

fields = list(rows[0].keys())
with open(OUT / "karvina_okrsky_vysledky.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)

# --- city totals summary ---
tot_valid = sum(valid.values())
tot = {p: sum(votes[ok][p] for ok in valid) for p in PARTIES}
tot_comb = sum(tot.values())
print(f"Karviná – {len(rows)} okrsků, platných hlasů celkem: {tot_valid}")
for p, name in PARTIES.items():
    print(f"  {name:6s}: {tot[p]:6d} hlasů  ({pct(tot[p], tot_valid)} %)")
print(f"  DOHROMADY: {tot_comb} hlasů ({pct(tot_comb, tot_valid)} %)")
print(f"\nZapsáno: {OUT / 'karvina_okrsky_vysledky.csv'}")
