"""One-off (v2): one religion, merged cultures and pops, low old-world literacy, fewer micro-states,
varied cliques, reform sets that cannot westernize at once."""
import re

# ------------------------------------------------------------------ config.py
c = open("config.py", encoding="utf-8").read()
if "STYLE = {" not in c:
    c = c.replace("WORLD_BANK = False", "WORLD_BANK = True").replace("STATE_FLAGS = False", "STATE_FLAGS = True")
    c += r'''

# ------------------------------------------------------------------ clique variety
# tag: (name, adjective, government, ruling ideology, national value)
STYLE = {
    "ZHL": ("Zhili Clique", "Zhili", "presidential_dictatorship", "reactionary", "nv_order"),
    "FTN": ("Fengtian Regency", "Fengtian", "absolute_monarchy", "reactionary", "nv_order"),
    "AHC": ("Anhui Clique", "Anhui", "presidential_dictatorship", "reactionary", "nv_order"),
    "SXI": ("Shanxi Model Province", "Shanxi", "prussian_constitutionalism", "conservative", "nv_order"),
    "GMJ": ("Guominjun", "Guominjun", "presidential_dictatorship", "reactionary", "nv_equality"),
    "SDG": ("Shandong Military Government", "Shandong", "presidential_dictatorship", "reactionary", "nv_order"),
    "HNA": ("Henan Pacification Zone", "Henan", "absolute_monarchy", "conservative", "nv_order"),
    "JSU": ("League of Five Provinces", "League", "hms_government", "conservative", "nv_liberty"),
    "ZHJ": ("Zhejiang Republic", "Zhejiang", "democracy", "liberal", "nv_liberty"),
    "FUJ": ("Fujian People's Government", "Fujian", "democracy", "liberal", "nv_equality"),
    "GDG": ("Canton Government", "Cantonese", "democracy", "liberal", "nv_liberty"),
    "GXI": ("Guangxi Clique", "Guangxi", "presidential_dictatorship", "reactionary", "nv_order"),
    "HNC": ("Hunan Federation", "Hunanese", "prussian_constitutionalism", "liberal", "nv_liberty"),
    "HBE": ("Hubei Military Government", "Hubei", "presidential_dictatorship", "reactionary", "nv_order"),
    "JXI": ("Jiangxi Garrison Command", "Jiangxi", "presidential_dictatorship", "reactionary", "nv_equality"),
    "SZC": ("Sichuan Clique", "Sichuan", "absolute_monarchy", "reactionary", "nv_order"),
    "YNN": ("Yunnan Protection Army", "Yunnan", "prussian_constitutionalism", "conservative", "nv_liberty"),
    "GZH": ("Guizhou Clique", "Guizhou", "presidential_dictatorship", "reactionary", "nv_order"),
    "XBI": ("Ma Clique", "Ma", "absolute_monarchy", "conservative", "nv_order"),
    "XIN": ("Xinjiang Governorate", "Xinjiang", "absolute_monarchy", "reactionary", "nv_order"),
    "JLN": ("Jilin Banner Lands", "Jilin", "absolute_monarchy", "conservative", "nv_order"),
    "HLJ": ("Heilongjiang Frontier", "Heilongjiang", "presidential_dictatorship", "reactionary", "nv_order"),
    "RHE": ("Rehe League", "Rehe", "absolute_monarchy", "reactionary", "nv_order"),
    "CHH": ("Chahar League", "Chahar", "absolute_monarchy", "conservative", "nv_order"),
    "SYN": ("Suiyuan Command", "Suiyuan", "presidential_dictatorship", "reactionary", "nv_order"),
    "NXA": ("Ningxia Command", "Ningxia", "absolute_monarchy", "conservative", "nv_order"),
    "QHI": ("Kokonor Command", "Kokonor", "absolute_monarchy", "conservative", "nv_order"),
    "XKG": ("Xikang Marches", "Xikang", "presidential_dictatorship", "reactionary", "nv_order"),
    "CQG": ("Chongqing Arsenal State", "Chongqing", "presidential_dictatorship", "reactionary", "nv_equality"),
    "TIB": ("Tibet", "Tibetan", "absolute_monarchy", "conservative", "nv_order"),
    "HNI": ("Hainan Garrison", "Hainan", "presidential_dictatorship", "reactionary", "nv_order"),
    "TWN": ("Republic of Formosa", "Formosan", "democracy", "liberal", "nv_liberty"),
    "SHG": ("Shanghai Free City", "Shanghai", "hms_government", "liberal", "nv_liberty"),
    "XZC": ("Xuzhou Pigtail Army", "Xuzhou", "absolute_monarchy", "reactionary", "nv_order"),
    "KSG": ("Kashgaria", "Kashgar", "absolute_monarchy", "conservative", "nv_order"),
}
# the only cultures a clique accepts besides its own (cultures matter: conquests are not automatically loyal)
ACCEPTED = {"XIN": ["uighur"], "KSG": ["uighur"], "FTN": ["manchu"], "JLN": ["manchu"], "HLJ": ["manchu"],
            "XKG": ["tibetan"], "QHI": ["tibetan"], "SYN": ["mongol"], "CHH": ["mongol"], "RHE": ["mongol"]}
PRIMARY = {"FTN": "manchu", "JLN": "manchu", "HLJ": "manchu", "GXI": "yue", "TWN": "min", "FUJ": "min", "ZHJ": "nanfaren",
           "KSG": "uighur", "SYN": "mongol", "CHH": "mongol", "XKG": "tibetan"}
ACCEPTED.update({"FTN": ["beifaren"], "JLN": ["beifaren"], "HLJ": ["beifaren"], "KSG": [], "SYN": ["beifaren"], "CHH": ["beifaren"], "XKG": ["nanfaren"]})
for _t, (_n, _a, _g, _i, _nv) in STYLE.items():
    _w = WARLORDS[_t]
    WARLORDS[_t] = (_n, _a, _w[2], PRIMARY.get(_t, _w[3]), ACCEPTED.get(_t, []), _w[5], _w[6], _w[7])

# every clique major has its own strength (a permanent country modifier)
TRAITS = {
    "ZHL": ("Beiyang Army", "The best-drilled divisions in the north.", {"land_organisation": 0.1, "land_unit_start_experience": 10}),
    "FTN": ("Mukden Arsenal", "The largest arms works in the country.", {"supply_consumption": -0.15, "factory_throughput": 0.05}),
    "AHC": ("Foreign Loans", "Friends among the foreign banks.", {"loan_interest": -0.5, "tax_efficiency": 0.03}),
    "SXI": ("Model Province", "Roads, schools and a self-sufficient economy.", {"factory_throughput": 0.1, "research_points_modifier": 0.05}),
    "GMJ": ("Christian General's Army", "Hymn-singing, well-disciplined infantry.", {"org_regain": 0.15, "land_organisation": 0.05}),
    "SDG": ("Mercenary Legions", "White Russian armoured trains and hired guns.", {"mobilisation_size": 0.02, "land_unit_start_experience": 10}),
    "HNA": ("Central Plains Granary", "The wheat fields of the Yellow River.", {"farm_rgo_eff": 0.15}),
    "JSU": ("Jiangnan Wealth", "The richest tax base in China.", {"tax_efficiency": 0.08}),
    "ZHJ": ("Ningbo Financiers", "Bankers and shipping magnates.", {"loan_interest": -0.5, "factory_throughput": 0.05}),
    "FUJ": ("Overseas Kin", "Every family has a cousin in the southern seas.", {"naval_organisation": 0.1, "tax_efficiency": 0.03}),
    "GDG": ("Revolutionary Cadres", "A party and an army with a cause.", {"land_unit_start_experience": 15, "research_points_modifier": 0.05}),
    "GXI": ("Guangxi Militia", "Every village is a company.", {"mobilisation_size": 0.03, "land_organisation": 0.05}),
    "HNC": ("Hunan Braves", "The province that has supplied China's soldiers for a century.", {"land_organisation": 0.08, "mobilisation_size": 0.01}),
    "HBE": ("Wuhan Crossroads", "Rail and river meet at the Three Towns.", {"factory_throughput": 0.08, "rgo_output": 0.03}),
    "JXI": ("Porcelain and Tungsten", "Kilns and mines pay the garrison.", {"mine_rgo_eff": 0.15}),
    "SZC": ("Land of Abundance", "Rice, salt and a population that never runs out.", {"farm_rgo_eff": 0.1, "mobilisation_size": 0.01}),
    "YNN": ("Mountain Fastness", "No army has ever marched easily into Yunnan.", {"land_organisation": 0.05, "max_attrition": -1, "mine_rgo_eff": 0.05}),
    "GZH": ("Hill Fighters", "Poor, hardy and hard to dislodge.", {"supply_consumption": -0.15, "org_regain": 0.1}),
    "XBI": ("Ma Family Cavalry", "The finest horsemen in the northwest.", {"land_unit_start_experience": 20, "supply_consumption": -0.1}),
    "XIN": ("Jade Gate", "Whoever holds the Gate holds the road to the west.", {"farm_rgo_eff": 0.1, "mine_rgo_eff": 0.1, "tax_efficiency": 0.03}),
}
'''
    open("config.py", "w", encoding="utf-8").write(c)

# ------------------------------------------------------------------ 02_world.py
s = open("02_world.py", encoding="utf-8").read()
if "CMAP" in s:
    raise SystemExit("02 already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


# cultures, religion, pop merging -------------------------------------------------------------
rep('''def run_pops(fac, write):''', r'''# ------------------------------------------------------------------ one religion, merged cultures
# Whole culture groups collapse into one culture each (targets are existing vanilla keys, so every
# vanilla script that names a culture stays valid). Pops of the same type that end up identical
# are merged into one pop, which is the main lag saving.
RELIGION = "placeholder"
GROUP_TARGET = {
    "germanic": "north_german", "beneluxian": "dutch", "pan_swiss": "north_german", "scandinavian": "swedish",
    "british": "british", "italian": "north_italian", "iberian": "spanish", "french": "french",
    "south_slavic": "serb", "pan_romanian": "romanian", "hungarian_culture_group": "hungarian",
    "polish_culture_group": "polish", "czecho_slovak_culture_group": "czech", "east_slavic": "russian",
    "baltic": "latvian", "levantine": "greek", "turko_semitic": "turkish",
    "native_american": "native_american_minor", "american_cultures": "yankee", "neo_european_cultures": "anglo_canadian",
    "latin_american_cultures": "mexican", "african_diaspora_cultures": "afro_american",
    "west_african": "hausa", "central_african": "african_minor", "east_african": "amhara",
    "southern_african": "zulu", "oceanic": "polynesian",
}
CULTURE_NAMES = {
    "north_german": "German", "dutch": "Netherlandish", "swedish": "Scandinavian", "north_italian": "Italian",
    "spanish": "Iberian", "serb": "South Slav", "russian": "East Slav", "latvian": "Baltic", "greek": "Levantine",
    "czech": "Czechoslovak", "native_american_minor": "Native American", "yankee": "American",
    "anglo_canadian": "Colonial European", "mexican": "Latin American", "afro_american": "Afro-American",
    "hausa": "West African", "african_minor": "Central African", "amhara": "East African", "zulu": "Southern African",
    "polynesian": "Oceanian", "beifaren": "Northern Han", "nanfaren": "Yangtze Han", "yue": "Cantonese", "min": "Hokkien",
}
CMAP = {}
_ct = re.sub(r"#.*", "", rd("common", "cultures.txt"))
ALL_CULTURES = set()
for _g, _body, _s, _e in blocks(_ct):
    for _k, _b, _s2, _e2 in blocks(_body):
        ALL_CULTURES.add(_k)
        if _g in GROUP_TARGET:
            CMAP[_k] = GROUP_TARGET[_g]
for _v in GROUP_TARGET.values():
    assert _v in ALL_CULTURES, _v
# China: five cultures instead of eleven
CMAP.update({"hakka": "yue", "zhuang": "yue", "miao": "nanfaren", "yi": "nanfaren", "ainu": "japanese"})
CHINA_CMAP = {"asian_minor": "nanfaren", "korean": "manchu", "siberian": "manchu", "kazak": "uighur", "yakut": "manchu"}


def cmap(c, in_china=False):
    if in_china and c in CHINA_CMAP:
        return CHINA_CMAP[c]
    return CMAP.get(c, c)


def simplify_pops(body, in_china):
    """Map cultures, set the single religion and merge pops that become identical."""
    merged = collections.OrderedDict()
    for pk, pb, _s, _e in blocks(body):
        cu = re.search(r"culture\s*=\s*(\w+)", pb)
        sz = re.search(r"size\s*=\s*(\d+)", pb)
        if not cu or not sz:
            continue
        key = (pk, cmap(cu.group(1), in_china))
        merged[key] = merged.get(key, 0) + int(sz.group(1))
    return "".join("\n\t%s = {\n\t\tculture = %s\n\t\treligion = %s\n\t\tsize = %d\n\t}\n" % (pk, cu, RELIGION, n)
                   for (pk, cu), n in merged.items())


def fix_cult(text):
    """Country history: single religion, merged cultures, no duplicate accepted cultures."""
    text = re.sub(r"(?m)^(\s*religion\s*=\s*)\w+", r"\g<1>" + RELIGION, text)
    pm = re.search(r"(?m)^\s*primary_culture\s*=\s*(\w+)", text)
    prim = cmap(pm.group(1)) if pm else None
    seen, out = {prim}, []
    for l in text.split("\n"):
        m1 = re.match(r"\s*primary_culture\s*=\s*(\w+)", l)
        m2 = re.match(r"\s*culture\s*=\s*(\w+)", l)
        if m1:
            out.append("primary_culture = %s" % prim)
        elif m2:
            cu = cmap(m2.group(1))
            if cu not in seen:
                seen.add(cu)
                out.append("culture = %s" % cu)
        else:
            out.append(l)
    return "\n".join(out)


def hw(rel, text):
    wr(rel, fix_cult(text))


_rel = rd("common", "religion.txt")
_m = re.search(r"christian\s*=\s*\{", _rel)
wr_religion = _rel[:_m.end()] + "\n\n\t%s = {\n\t\ticon = 1\n\t\tcolor = { 0.6 0.6 0.6 }\n\t}\n" % RELIGION + _rel[_m.end():]


def run_pops(fac, write):''')
rep('''            if p == 2131 and WORLD_BANK:
                body = BANK_POPS
''', '''            if p == 2131 and WORLD_BANK:
                body = BANK_POPS
            body = simplify_pops(body, p in CHINA)
''')

# successors: fewer and larger; micro-states absorbed ------------------------------------------
rep("len(ps) < 14:", "len(ps) < 24:")
rep("groups = _kmeans(sorted(ps), max(2, round(len(ps) / 8)))", "groups = _kmeans(sorted(ps), max(2, round(len(ps) / 14)))")
rep('''print("successor states created:", len(SUCCESSOR), "from", len({v[0] for v in SUCCESSOR.values()}), "countries")
''', r'''print("successor states created:", len(SUCCESSOR), "from", len({v[0] for v in SUCCESSOR.values()}), "countries")

# micro-states of three provinces or fewer are absorbed by the neighbour they share most border with
KEEP_SMALL = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK"}
_absorbed = 0
while True:
    _cnt = collections.Counter(o for o in owner.values() if o)
    _small = sorted((n, t) for t, n in _cnt.items() if n <= 3 and t not in KEEP_SMALL)
    _done = False
    for n, t in _small:
        edge = collections.Counter()
        for p in ALLP:
            if owner[p] == t:
                for q in ADJ.get(p, ()):
                    o2 = owner.get(q)
                    if o2 and o2 != t and o2 not in WARLORDS and o2 != "WBK":
                        edge[o2] += 1
        if not edge:
            continue
        tgt = max(edge, key=lambda x: (edge[x], _cnt[x]))
        for p in ALLP:
            if owner[p] == t:
                owner[p] = tgt
        SUCCESSOR.pop(t, None)
        _absorbed += 1
        _done = True
        break
    if not _done:
        break
print("micro-states absorbed by neighbours:", _absorbed)
''')

# reforms: never enough to westernize on day one ------------------------------------------------
rep('''PARTIAL_REF = ["admin_reform", "finance_reform", "education_reform", "foreign_training", "foreign_weapons", "foreign_officers", "foreign_naval_officers"]
SPECIAL_REF = ["land_reform", "admin_reform", "finance_reform", "education_reform", "transport_improv",
               "foreign_training", "foreign_weapons", "military_constructions", "foreign_officers", "army_schools"]
''', r'''PARTIAL_REF = ["admin_reform", "foreign_training", "foreign_weapons"]
SPECIAL_REF = ["land_reform", "foreign_training", "foreign_weapons", "military_constructions", "foreign_officers"]
# westernization needs 100% progress; check what these sets add up to from the game's own numbers
_iss = re.sub(r"#.*", "", rd("common", "issues.txt"))
PROGRESS = {m_.group(1): float(m_.group(2)) for m_ in re.finditer(r"yes_(\w+)\s*=\s*\{[^{}]*?civilization_progress_modifier\s*=\s*([\d\.]+)", _iss)}
for _nm, _set in (("partial", PARTIAL_REF), ("special", SPECIAL_REF)):
    _tot = sum(PROGRESS.get(r, 0.2) for r in _set)
    print("  westernization progress of %s reform set: %d%%" % (_nm, round(_tot * 100)))
    assert _tot <= 0.6, (_nm, _tot)
''')

# literacy and warlord variety -------------------------------------------------------------------
rep('''        if re.match(r"(civilized|oob|decision|capital|schools|set_country_flag|prestige)\\b", ls):''',
    '''        if re.match(r"(civilized|oob|decision|capital|schools|set_country_flag|prestige|literacy|non_state_culture_literacy)\\b", ls):''')
rep('''    s = "capital = %d\\n" % capital[tag] + "\\n".join(keep) + "\\ncivilized = no\\n"''',
    '''    lit = {"partial": (0.10, 0.05), "unciv": (0.04, 0.02), "primitive": (0.01, 0.01)}[t]
    s = "capital = %d\\n" % capital[tag] + "\\n".join(keep) + "\\nliteracy = %s\\nnon_state_culture_literacy = %s\\ncivilized = no\\n" % lit''')
rep('''    s += "religion = %s\\n" % ("gelugpa" if cul == "tibetan" else "mahayana")
    s += "government = presidential_dictatorship\\nplurality = 5.0\\nnationalvalue = %s\\n" % ("nv_order" if i % 3 else "nv_equality" if i % 2 else "nv_liberty")''',
    '''    _n, _a, gov, ideo, nv = STYLE[tag]
    s += "religion = %s\\n" % RELIGION
    s += "government = %s\\nplurality = 5.0\\nnationalvalue = %s\\n" % (gov, nv)
    if gov in ("democracy", "hms_government", "prussian_constitutionalism"):
        s += "last_election = 1834.1.1\\n"''')
rep('''    s += POLREF + "ruling_party = %s\\n" % chi_rx.replace("CHI_", tag + "_") + UH
    s += "schools''', '''    s += POLREF + "ruling_party = %s\\n" % party_of("CHI", ideo).replace("CHI_", tag + "_") + UH
    s += "schools''')

# every country history goes through the culture/religion fixer -----------------------------------
n = s.count('wr("history/countries/')
s = s.replace('wr("history/countries/', 'hw("history/countries/')
print("history writers routed through fix_cult:", n)

# religion file, culture names, export the culture map for the gameplay stage ---------------------
rep('L += loc("WBK", "World Bank")', '''L += loc(RELIGION, "Customary Faith")
for _k, _v in CULTURE_NAMES.items():
    L += loc(_k, _v)
L += loc("WBK", "World Bank")''')
rep('''    "vtags": list(vtags),''', '''    "cmap": CMAP, "vtags": list(vtags),''')
s += '''
wr("common/religion.txt", wr_religion)
'''
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched 02_world.py")
