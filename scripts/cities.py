#!/usr/bin/env python3
"""Configuration for the Karviná / Havířov / Orlová election-map project.

For PS 2025 the ballot numbers (KSTRANA) are national and identical
everywhere: 11 = SPOLU, 16 = Piráti, 23 = STAN.

For the 2022 municipal election the lists are local, so the relevant list
numbers (POR_STR_HL) and even the *existence* of a list differ per city –
see the per-city "kv2022" maps and notes below.
"""

PS2025_PARTIES = {11: "SPOLU", 16: "Pirati", 23: "STAN"}

CITIES = {
    "karvina": {
        "code": "598917",
        "name": "Karviná",
        # group -> list number (POR_STR_HL) in the 2022 municipal election
        "kv2022": {"SPOLU": 6, "Pirati": 2, "STAN": 7},
        "kv2022_labels": {
            "SPOLU": "SPOLU (KDU-ČSL, ODS, TOP 09)",
        },
        "kv2022_note": "",
    },
    "havirov": {
        "code": "555088",
        "name": "Havířov",
        # STAN nemá vlastní kandidátku – je součástí koalice „SPOLU plus".
        "kv2022": {"SPOLU": 9, "Pirati": 4},
        "kv2022_labels": {
            "SPOLU": "SPOLU plus (ODS, KDU-ČSL, TOP 09, STAN)",
        },
        "kv2022_note": ("STAN kandidoval v rámci koalice „SPOLU plus“ "
                        "(kand. č. 9), samostatný výsledek STAN proto nelze "
                        "vyčíslit."),
    },
    "orlova": {
        "code": "599069",
        "name": "Orlová",
        # STAN v Orlové 2022 vůbec nekandidoval.
        "kv2022": {"SPOLU": 9, "Pirati": 1},
        "kv2022_labels": {
            "SPOLU": "SPOLU (KDU-ČSL, ODS, TOP 09)",
        },
        "kv2022_note": "STAN v komunálních volbách 2022 v Orlové nekandidoval.",
    },
}

# colour map + base title for each grouping
GROUP_STYLE = {
    "DOHROMADY": ("Purples", "SPOLU + Piráti + STAN dohromady"),
    "SPOLU": ("Blues", "SPOLU"),
    "Pirati": ("Greens", "Piráti (Česká pirátská strana)"),
    "STAN": ("Oranges", "STAN (Starostové a nezávislí)"),
}
