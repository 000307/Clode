# Karviná – výsledky voleb podle volebních okrsků

Mapy a data výsledků voleb ve městě **Karviná** (obec 598917, okres Karviná)
po jednotlivých **volebních okrscích** – pro uskupení **SPOLU**, **Piráti**
a **STAN**, samostatně i dohromady. Sledovaný ukazatel je **počet hlasů**
i **% platných hlasů**. Pokryté volby:

- **Poslanecká sněmovna 2025** (PS 2025) – 52 okrsků
- **Komunální volby 2022** (KV 2022) – 59 okrsků

## Poslanecká sněmovna 2025 – celé město (52 okrsků, 23 027 platných hlasů)

| Uskupení | Hlasy | % platných |
|---|---:|---:|
| SPOLU (ODS, KDU-ČSL, TOP 09) | 2 073 | 9,00 % |
| Piráti (Česká pirátská strana) | 1 049 | 4,56 % |
| STAN (Starostové a nezávislí) | 1 239 | 5,38 % |
| **DOHROMADY** | **4 361** | **18,94 %** |

Tabulka po okrscích: [`output/karvina_okrsky_vysledky.csv`](output/karvina_okrsky_vysledky.csv).
Mapy: `output/karvina_mapa_*.png`.

## Komunální volby 2022 – celé město (59 okrsků, 544 182 platných hlasů)

Zastupitelstvo města má 41 členů; **% je oficiální „přepočtený základ“** ČSÚ
(podíl hlasů strany na základu zohledňujícím počet kandidátů strany), proto
se Piráti (39 kandidátů místo 41) liší od prostého podílu.

| Uskupení | Hlasy | % platných |
|---|---:|---:|
| SPOLU (KDU-ČSL, ODS, TOP 09) | 32 097 | 5,89 % |
| Piráti (Česká pirátská strana) | 17 432 | 3,36 % |
| STAN (Starostové a nezávislí) | 8 985 | 1,65 % |
| **DOHROMADY** | **58 514** | **10,9 %** |

> Pozn.: komunální volby používají *panachage* – volič má až tolik hlasů, kolik
> se volí zastupitelů (41). „Počet hlasů“ strany je součet hlasů jejích
> kandidátů.

Tabulka po okrscích: [`output/karvina_2022_okrsky_vysledky.csv`](output/karvina_2022_okrsky_vysledky.csv).
Mapy: `output/karvina_2022_mapa_*.png`.

## Grafika (`output/`)

Choropletová mapa města podle volebních okrsků – **každý okrsek je tím tmavší,
čím více hlasů uskupení získalo**. Každý okrsek je popsán *číslem / počtem
hlasů / % platných hlasů*. Protože je v centru města mnoho malých okrsků, má
každá podrobná mapa vpravo **výřez centra**.

| Soubor (prefix `karvina_` / `karvina_2022_`) | Obsah |
|---|---|
| `…mapa_DOHROMADY.png` | SPOLU + Piráti + STAN dohromady |
| `…mapa_SPOLU.png` | SPOLU |
| `…mapa_Pirati.png` | Piráti |
| `…mapa_STAN.png` | STAN |
| `…mapa_prehled_procenta.png` | přehled 2×2 (barva = % platných hlasů) |

## Zdroje dat (otevřená data, CC-BY 4.0)

- **PS 2025 – výsledky po okrscích** – ČSÚ / volby.cz (`pst4` = úhrny za okrsek,
  `pst4p` = hlasy stran za okrsek, `psrkl` = číselník volebních stran).
  <https://www.volby.cz/opendata/ps2025/ps2025_opendata.htm>
  Čísla stran (KSTRANA): **11 = SPOLU, 16 = Piráti, 23 = STAN**.
- **KV 2022 – výsledky po okrscích** – ČSÚ / volby.cz (`kvt3` = úhrny za okrsek,
  `kvhl` = hlasy stran za okrsek, `kvros` = registrované kandidátky,
  `kvrk` = kandidáti). <https://www.volby.cz/opendata/kv2022/kv2022_opendata.htm>
  Čísla kandidátek v Karviné: **6 = SPOLU, 2 = Piráti, 7 = STAN**.
- **Hranice volebních okrsků** – ČSÚ, *„Volební okrsky pro volby do PS 2025 –
  generalizované“* a *„Volební okrsky 2022“* (geodata.csu.gov.cz / volby.cz,
  generalizováno z RÚIAN/ČÚZK).

## Reprodukce

```bash
pip install pandas geopandas matplotlib shapely
python3 scripts/fetch_data.py         # stáhne zdrojová data do data/
python3 scripts/build_data.py         # PS 2025 -> output/karvina_okrsky_vysledky.csv
python3 scripts/build_data_2022.py    # KV 2022 -> output/karvina_2022_okrsky_vysledky.csv
python3 scripts/build_maps.py         # PS 2025 -> output/karvina_mapa_*.png
python3 scripts/build_maps_2022.py    # KV 2022 -> output/karvina_2022_mapa_*.png
```

Velké národní soubory se do gitu neukládají (jsou znovu stažitelné přes
`fetch_data.py`); v repozitáři je jen karvinská geometrie
(`data/karvina_okrsky*.geojson`) a odvozené výstupy.
