#!/usr/bin/env python3
"""Configuration for the election-map project.

PS 2025 (parliamentary) ballot numbers (KSTRANA) are national and identical
everywhere: 11 = SPOLU, 16 = Piráti, 23 = STAN.

For the 2022 municipal election the lists are local. Each city maps a set of
"groups" to local list numbers (POR_STR_HL). Groups can be the standard
SPOLU/Pirati/STAN, but where those did not run as separable lists we map the
actual coalitions/parties that ran instead (see Nový Jičín). A city with
kv2022 = None has no municipal maps (none of the subjects ran there).
"""

PS2025_PARTIES = {11: "SPOLU", 16: "Pirati", 23: "STAN"}
DOHRO_CMAP = "Purples"

# default style/labels for the standard group keys
DEFAULT_META = {
    "SPOLU":  {"label": "SPOLU (ODS, KDU-ČSL, TOP 09)", "short": "SPOLU",
               "cmap": "Blues"},
    "Pirati": {"label": "Piráti (Česká pirátská strana)", "short": "Piráti",
               "cmap": "Greens"},
    "STAN":   {"label": "STAN (Starostové a nezávislí)", "short": "STAN",
               "cmap": "Oranges"},
}

CITIES = {
    "karvina": {
        "code": "598917", "name": "Karviná",
        "kv2022": {"SPOLU": 6, "Pirati": 2, "STAN": 7},
        "kv2022_meta": {"SPOLU": {"label": "SPOLU (KDU-ČSL, ODS, TOP 09)"}},
        "kv2022_note": "",
    },
    "havirov": {
        "code": "555088", "name": "Havířov",
        # STAN nemá vlastní kandidátku – je v koalici „SPOLU plus".
        "kv2022": {"SPOLU": 9, "Pirati": 4},
        "kv2022_meta": {"SPOLU": {
            "label": "SPOLU plus (ODS, KDU-ČSL, TOP 09, STAN)"}},
        "kv2022_note": ("STAN kandidoval v rámci koalice „SPOLU plus“ "
                        "(kand. č. 9), samostatný výsledek STAN nelze vyčíslit."),
    },
    "orlova": {
        "code": "599069", "name": "Orlová",
        # STAN v Orlové 2022 nekandidoval.
        "kv2022": {"SPOLU": 9, "Pirati": 1},
        "kv2022_meta": {"SPOLU": {"label": "SPOLU (KDU-ČSL, ODS, TOP 09)"}},
        "kv2022_note": "STAN v komunálních volbách 2022 v Orlové nekandidoval.",
    },
    "novy_jicin": {
        "code": "599191", "name": "Nový Jičín",
        # SPOLU/Piráti/STAN nekandidovaly samostatně – mapujeme reálné
        # kandidátky: koalice č.1 (Zelení+Piráti+TOP 09+STAN), ODS, KDU-ČSL.
        "kv2022": {"KOAL_ZPTS": 1, "ODS": 4, "KDU": 5},
        "kv2022_meta": {
            "KOAL_ZPTS": {"label": "Koalice Zelení + Piráti + TOP 09 + STAN "
                                   "(kand. č. 1)", "short": "Koalice č.1",
                          "cmap": "Greens"},
            "ODS": {"label": "ODS (kand. č. 4)", "short": "ODS",
                    "cmap": "Blues"},
            "KDU": {"label": "KDU-ČSL (kand. č. 5)", "short": "KDU-ČSL",
                    "cmap": "YlOrBr"},
        },
        "kv2022_note": ("V Novém Jičíně 2022 nekandidovaly SPOLU/Piráti/STAN "
                        "samostatně: Piráti a STAN byli v koalici č.1 (se "
                        "Zelenými a TOP 09); ze „SPOLU“ šly ODS (č.4) a "
                        "KDU-ČSL (č.5) samostatně, TOP 09 byla v koalici č.1."),
    },
    "sedlnice": {
        "code": "599832", "name": "Sedlnice",
        # žádné ze sledovaných uskupení v komunálu 2022 nekandidovalo
        "kv2022": None,
        "kv2022_meta": {},
        "kv2022_note": ("V komunálních volbách 2022 v Sedlnicích kandidovaly "
                        "jen ANO, sdružení „PRO SEDLNICE SPOLEČNĚ“ a Moravané "
                        "– žádné ze SPOLU/Piráti/STAN."),
    },
}


def meta_for(group, city_meta):
    """Resolve label/short/cmap for a group key, merging city overrides."""
    m = dict(DEFAULT_META.get(group, {}))
    m.update(city_meta.get(group, {}))
    m.setdefault("label", group)
    m.setdefault("short", group)
    m.setdefault("cmap", "Greys")
    return m
