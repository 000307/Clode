#!/usr/bin/env python3
"""Build per-okrsek result tables for SPOLU / Piráti / STAN for every city,
for both the 2025 parliamentary (PS 2025) and the 2022 municipal (KV 2022)
elections, from the Czech Statistical Office open data (volby.cz).

Outputs: output/<slug>/<slug>_ps2025_okrsky.csv
         output/<slug>/<slug>_kv2022_okrsky.csv
"""
import csv
from collections import Counter
from pathlib import Path

from cities import CITIES, PS2025_PARTIES

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"


def pct(n, d):
    return round(100.0 * n / d, 2) if d else 0.0


def write_csv(slug, election, groups, rows):
    d = OUT / slug
    d.mkdir(parents=True, exist_ok=True)
    fp = d / f"{slug}_{election}_okrsky.csv"
    fields = ["okrsek", "volici", "platne_hlasy"]
    for g in groups:
        fields += [f"{g}_hlasy", f"{g}_pct"]
    fields += ["DOHROMADY_hlasy", "DOHROMADY_pct"]
    with open(fp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return fp


# ---------------------------------------------------------------------------
# PS 2025 – parliamentary (KSTRANA 11/16/23 everywhere; simple vote share)
# ---------------------------------------------------------------------------
def build_ps2025(slug, city):
    obec = city["code"]
    groups = ["SPOLU", "Pirati", "STAN"]
    num = {v: k for k, v in PS2025_PARTIES.items()}  # name -> KSTRANA

    valid, voters = {}, {}
    with open(DATA / "pst4.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["OBEC"] == obec:
                ok = int(r["OKRSEK"])
                valid[ok] = int(r["PL_HL_CELK"])
                voters[ok] = int(r["VOL_SEZNAM"])

    votes = {ok: {g: 0 for g in groups} for ok in valid}
    with open(DATA / "pst4p.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["OBEC"] != obec:
                continue
            ks = int(r["KSTRANA"])
            if ks in PS2025_PARTIES:
                votes[int(r["OKRSEK"])][PS2025_PARTIES[ks]] = int(r["POC_HLASU"])

    rows, tot = [], {g: 0 for g in groups}
    for ok in sorted(valid):
        pl = valid[ok]
        row = {"okrsek": ok, "volici": voters[ok], "platne_hlasy": pl}
        comb = 0
        for g in groups:
            v = votes[ok][g]
            tot[g] += v
            comb += v
            row[f"{g}_hlasy"] = v
            row[f"{g}_pct"] = pct(v, pl)
        row["DOHROMADY_hlasy"] = comb
        row["DOHROMADY_pct"] = pct(comb, pl)
        rows.append(row)

    fp = write_csv(slug, "ps2025", groups, rows)
    tv = sum(valid.values())
    summary = " | ".join(f"{g} {tot[g]} ({pct(tot[g], tv)}%)" for g in groups)
    print(f"[PS2025] {city['name']:9s} {len(rows)} okrsků, platných {tv}: {summary}")
    return groups


# ---------------------------------------------------------------------------
# KV 2022 – municipal (local lists; official "přepočtený základ" percentage)
# ---------------------------------------------------------------------------
def build_kv2022(slug, city):
    obec = city["code"]
    mapping = city["kv2022"]                 # group -> POR_STR_HL (or None)
    if not mapping:
        print(f"[KV2022] {city['name']:9s} přeskočeno – {city['kv2022_note']}")
        return []
    groups = list(mapping.keys())
    por_of = mapping
    want_por = set(mapping.values())

    # council size = number of filled mandates
    seats = 0
    with open(DATA / "kvros.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["KODZASTUP"] == obec:
                seats += int(r["MAND_STR"])

    # valid candidates per relevant list (for the přepočtený základ);
    # withdrawn/invalid candidates (PLATNOST != 'A') do not count
    ncand = Counter()
    with open(DATA / "kvrk.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r["KODZASTUP"] == obec and int(r["POR_STR_HL"]) in want_por
                    and r["PLATNOST"] == "A"):
                ncand[int(r["POR_STR_HL"])] += 1

    valid, voters = {}, {}
    with open(DATA / "kvt3.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["OBEC"] == obec:
                ok = int(r["OKRSEK"])
                valid[ok] = int(r["PL_HL_CELK"])
                voters[ok] = int(r["VOL_SEZNAM"])

    votes = {ok: {g: 0 for g in groups} for ok in valid}
    with open(DATA / "kvhl.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["OBEC"] != obec:
                continue
            por = int(r["POR_STR_HL"])
            for g in groups:
                if por_of[g] == por:
                    votes[int(r["OKRSEK"])][g] = int(r["POC_HLASU"])

    def opct(n, valid_n, g):
        base = valid_n * ncand[por_of[g]] / seats
        return round(100.0 * n / base, 2) if base else 0.0

    rows, tot = [], {g: 0 for g in groups}
    for ok in sorted(valid):
        pl = valid[ok]
        row = {"okrsek": ok, "volici": voters[ok], "platne_hlasy": pl}
        comb_v, comb_p = 0, 0.0
        for g in groups:
            v = votes[ok][g]
            p = opct(v, pl, g)
            tot[g] += v
            comb_v += v
            comb_p += p
            row[f"{g}_hlasy"] = v
            row[f"{g}_pct"] = p
        row["DOHROMADY_hlasy"] = comb_v
        row["DOHROMADY_pct"] = round(comb_p, 2)
        rows.append(row)

    fp = write_csv(slug, "kv2022", groups, rows)
    tv = sum(valid.values())
    summary = " | ".join(
        f"{g} {tot[g]} ({opct(tot[g], tv, g)}%, {ncand[por_of[g]]} kand.)"
        for g in groups)
    print(f"[KV2022] {city['name']:9s} {len(rows)} okrsků, zast. {seats} členů, "
          f"platných {tv}: {summary}")
    if city["kv2022_note"]:
        print(f"          pozn.: {city['kv2022_note']}")
    return groups


if __name__ == "__main__":
    for slug, city in CITIES.items():
        build_ps2025(slug, city)
        build_kv2022(slug, city)
