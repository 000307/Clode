# Výsledky voleb podle volebních okrsků – Karviná, Havířov, Orlová

Mapy a data výsledků voleb pro uskupení **SPOLU**, **Piráti** a **STAN**
(samostatně i dohromady) po jednotlivých **volebních okrscích** ve třech
městech okresu Karviná – **Karviná**, **Havířov** a **Orlová**. Sledovaný
ukazatel je **počet hlasů** i **% platných hlasů**. Pokryté volby:

- **Poslanecká sněmovna 2025** (PS 2025)
- **Komunální volby 2022** (KV 2022)

Pro každé město a volby vznikne choropletová mapa, kde je **každý okrsek tím
tmavší, čím více hlasů uskupení získalo**, s popiskem *číslo / počet hlasů /
% platných hlasů* a výřezem hustého centra.

## Poslanecká sněmovna 2025 (% z platných hlasů)

| Město | Okrsků | SPOLU | Piráti | STAN | Dohromady |
|---|--:|--:|--:|--:|--:|
| Karviná | 52 | 2 073 (9,00 %) | 1 049 (4,56 %) | 1 239 (5,38 %) | 4 361 (18,94 %) |
| Havířov | 62 | 4 618 (13,85 %) | 2 077 (6,23 %) | 2 048 (6,14 %) | 8 743 (26,22 %) |
| Orlová | 30 | 1 197 (9,00 %) | 659 (4,95 %) | 610 (4,59 %) | 2 466 (18,54 %) |

## Komunální volby 2022 (% = oficiální „přepočtený základ“ ČSÚ)

| Město | Okrsků | SPOLU | Piráti | STAN | Dohromady |
|---|--:|--:|--:|--:|--:|
| Karviná | 59 | 32 097 (5,90 %) | 17 432 (3,36 %) | 8 985 (1,65 %) | 58 514 (10,9 %) |
| Havířov | 79 | 103 177 (13,05 %) \* | 36 009 (4,56 %) | — \* | 139 186 (17,61 %) |
| Orlová | 30 | 10 948 (5,18 %) | 6 632 (3,36 %) | — \*\* | 17 580 (8,54 %) |

\* **Havířov:** STAN neměl vlastní kandidátku – kandidoval v rámci koalice
**„SPOLU plus" (ODS, KDU-ČSL, TOP 09, STAN)**, takže ho nelze vyčíslit
samostatně; číslo u „SPOLU" je celá tato koalice.
\*\* **Orlová:** STAN v komunálních volbách 2022 vůbec nekandidoval.

> **Pozor na srovnatelnost:** komunální volby používají *panachage* – volič má
> až tolik hlasů, kolik se volí zastupitelů (Karviná 41, Havířov 43, Orlová
> 31). „Počet hlasů" kandidátky je proto součet hlasů jejích kandidátů a je
> řádově vyšší než u sněmovních voleb. Procenta v komunálu jsou počítána
> oficiálním přepočteným základem (zohledňuje počet platných kandidátů
> kandidátky), takže odpovídají číslům na volby.cz.

## Struktura výstupů (`output/<město>/`)

Pro každé město (`karvina`, `havirov`, `orlova`) a každé volby
(`ps2025`, `kv2022`):

| Soubor | Obsah |
|---|---|
| `<m>_<v>_okrsky.csv` | tabulka po okrscích (hlasy i % pro všechna uskupení) |
| `<m>_<v>_mapa_DOHROMADY.png` | mapa: uskupení dohromady (město + detail centra) |
| `<m>_<v>_mapa_SPOLU.png` | mapa: SPOLU |
| `<m>_<v>_mapa_Pirati.png` | mapa: Piráti |
| `<m>_<v>_mapa_STAN.png` | mapa: STAN (jen tam, kde STAN kandidoval samostatně) |
| `<m>_<v>_prehled.png` | přehledové srovnání všech uskupení (barva = % hlasů) |

## Zdroje dat (otevřená data, CC-BY 4.0)

- **PS 2025 – výsledky po okrscích** – ČSÚ / volby.cz (`pst4`, `pst4p`,
  `psrkl`). <https://www.volby.cz/opendata/ps2025/ps2025_opendata.htm>
  Národní čísla stran (KSTRANA): **11 = SPOLU, 16 = Piráti, 23 = STAN**.
- **KV 2022 – výsledky po okrscích** – ČSÚ / volby.cz (`kvt3`, `kvhl`,
  `kvros`, `kvrk`). <https://www.volby.cz/opendata/kv2022/kv2022_opendata.htm>
  Čísla kandidátek jsou lokální – viz `scripts/cities.py`.
- **Hranice volebních okrsků** – ČSÚ, *„Volební okrsky pro volby do PS 2025 –
  generalizované“* a *„Volební okrsky 2022“* (geodata.csu.gov.cz / volby.cz,
  generalizováno z RÚIAN/ČÚZK).

## Reprodukce

```bash
pip install pandas geopandas matplotlib shapely
cd scripts
python3 fetch_data.py     # stáhne zdrojová data + výřezy geometrie do data/
python3 build_data.py     # -> output/<město>/<…>_okrsky.csv
python3 build_maps.py     # -> output/<město>/<…>.png
```

Konfigurace měst (kódy obcí, čísla komunálních kandidátek, poznámky) je
v [`scripts/cities.py`](scripts/cities.py). Velké národní soubory se do gitu
neukládají (znovu stažitelné přes `fetch_data.py`); v repu jsou jen malé
karvinská/havířovská/orlovská geometrie `data/<město>_<volby>.geojson`
a odvozené výstupy.
