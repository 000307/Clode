# Karviná – volby do Poslanecké sněmovny 2025 podle volebních okrsků

Mapy a data výsledků voleb do Poslanecké sněmovny **2025** ve městě **Karviná**
(obec 598917, okres Karviná) po jednotlivých **volebních okrscích** – pro
uskupení **SPOLU**, **Piráti** a **STAN**, samostatně i dohromady.
Sledovaný ukazatel je **počet hlasů** i **% platných hlasů**.

## Výsledky za celé město (52 okrsků, 23 027 platných hlasů)

| Uskupení | Hlasy | % platných |
|---|---:|---:|
| SPOLU (ODS, KDU-ČSL, TOP 09) | 2 073 | 9,00 % |
| Piráti (Česká pirátská strana) | 1 049 | 4,56 % |
| STAN (Starostové a nezávislí) | 1 239 | 5,38 % |
| **DOHROMADY** | **4 361** | **18,94 %** |

Kompletní tabulka po okrscích: [`output/karvina_okrsky_vysledky.csv`](output/karvina_okrsky_vysledky.csv).

## Grafika (`output/`)

Choropletová mapa města podle volebních okrsků – **každý okrsek je tím tmavší,
čím více hlasů uskupení získalo**. Každý okrsek je popsán *číslem / počtem
hlasů / % platných hlasů*. Protože je v centru města mnoho malých okrsků, má
každá podrobná mapa vpravo **výřez centra**.

| Soubor | Obsah |
|---|---|
| `karvina_mapa_DOHROMADY.png` | SPOLU + Piráti + STAN dohromady |
| `karvina_mapa_SPOLU.png` | SPOLU |
| `karvina_mapa_Pirati.png` | Piráti |
| `karvina_mapa_STAN.png` | STAN |
| `karvina_mapa_prehled_procenta.png` | přehled 2×2 (barva = % platných hlasů) |

## Zdroje dat (otevřená data, CC-BY 4.0)

- **Výsledky po okrscích** – Český statistický úřad / volby.cz, PS 2025
  (`pst4` = úhrny za okrsek, `pst4p` = hlasy stran za okrsek,
  `psrkl` = číselník volebních stran). <https://www.volby.cz/opendata/ps2025/ps2025_opendata.htm>
- **Hranice volebních okrsků** – ČSÚ, *„Volební okrsky pro volby do PS 2025 –
  generalizované“* (geodata.csu.gov.cz, generalizováno z RÚIAN/ČÚZK).

Čísla ballotových stran (KSTRANA) pro PS 2025: **11 = SPOLU, 16 = Piráti,
23 = STAN**. Mapy se spojují s geometrií přes číslo okrsku.

## Reprodukce

```bash
pip install pandas geopandas matplotlib shapely
python3 scripts/fetch_data.py    # stáhne zdrojová data do data/
python3 scripts/build_data.py    # -> output/karvina_okrsky_vysledky.csv
python3 scripts/build_maps.py    # -> output/*.png
```

Velké národní CSV soubory se do gitu neukládají (jsou znovu stažitelné přes
`fetch_data.py`); v repozitáři je jen karvinská geometrie
(`data/karvina_okrsky.geojson`) a odvozené výstupy.
