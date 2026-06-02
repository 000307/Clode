#!/usr/bin/env python3
"""Extract Karviná (obec/zastupitelstvo 598917) per-okrsek results for SPOLU,
Piráti, STAN from the 2022 municipal election (komunální volby, KV 2022).

Municipal elections use panachage: each voter has as many votes as there are
council seats, so "počet hlasů" is the total of candidate votes the list got;
"%" is the share of all valid (candidate) votes in the okrsek.

Lists in Karviná 2022 (POR_STR_HL -> list), from kvros.csv:
    2 = Piráti (Česká pirátská strana)
    6 = SPOLU (KDU-ČSL, ODS, TOP 09)
    7 = STAN (Starostové a nezávislí)
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

OBEC = "598917"          # Karviná (KODZASTUP == OBEC)
LISTS = {6: "SPOLU", 2: "Pirati", 7: "STAN"}

# --- council size + candidates per list (for the "přepočtený základ") ------
# Official municipal % = 100 * votes / (valid_votes * n_candidates / n_seats).
seats = 0
with open(DATA / "kvros.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["KODZASTUP"] == OBEC:
            seats += int(row["MAND_STR"])      # filled mandates == council size

ncand = {p: 0 for p in LISTS}
with open(DATA / "kvrk.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["KODZASTUP"] == OBEC:
            por = int(row["POR_STR_HL"])
            if por in LISTS:
                ncand[por] += 1

# --- valid votes (denominator) per okrsek, from kvt3.csv ---
valid, voters = {}, {}
with open(DATA / "kvt3.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["OBEC"] != OBEC:
            continue
        ok = int(row["OKRSEK"])
        valid[ok] = int(row["PL_HL_CELK"])
        voters[ok] = int(row["VOL_SEZNAM"])

# --- list votes per okrsek, from kvhl.csv ---
votes = {ok: {p: 0 for p in LISTS} for ok in valid}
with open(DATA / "kvhl.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if row["OBEC"] != OBEC:
            continue
        por = int(row["POR_STR_HL"])
        if por in LISTS:
            votes[int(row["OKRSEK"])][por] = int(row["POC_HLASU"])


def opct(votes_n, valid_n, por):
    """Official municipal vote share (přepočtený základ) for one list."""
    base = valid_n * ncand[por] / seats
    return round(100.0 * votes_n / base, 2) if base else 0.0


rows = []
for ok in sorted(valid):
    v = votes[ok]
    spolu, pir, stan = v[6], v[2], v[7]
    comb = spolu + pir + stan
    pl = valid[ok]
    sp_p, pi_p, st_p = opct(spolu, pl, 6), opct(pir, pl, 2), opct(stan, pl, 7)
    rows.append({
        "okrsek": ok, "volici": voters[ok], "platne_hlasy": pl,
        "SPOLU_hlasy": spolu, "SPOLU_pct": sp_p,
        "Pirati_hlasy": pir, "Pirati_pct": pi_p,
        "STAN_hlasy": stan, "STAN_pct": st_p,
        "DOHROMADY_hlasy": comb, "DOHROMADY_pct": round(sp_p + pi_p + st_p, 2),
    })

with open(OUT / "karvina_2022_okrsky_vysledky.csv", "w", newline="",
          encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

tot_valid = sum(valid.values())
tot = {p: sum(votes[ok][p] for ok in valid) for p in LISTS}
tot_comb = sum(tot.values())
tot_pct = {p: opct(tot[p], tot_valid, p) for p in LISTS}
print(f"Karviná – komunální volby 2022 – {len(rows)} okrsků, "
      f"platných hlasů celkem: {tot_valid} (zastupitelstvo {seats} členů)")
for p, name in LISTS.items():
    print(f"  {name:6s}: {tot[p]:6d} hlasů  ({tot_pct[p]} %)  "
          f"[{ncand[p]} kandidátů]")
print(f"  DOHROMADY: {tot_comb} hlasů ({round(sum(tot_pct.values()),2)} %)")
print(f"\nZapsáno: {OUT / 'karvina_2022_okrsky_vysledky.csv'}")
