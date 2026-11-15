"""One-off patch: Taiwan's second steps, the peninsula union, Japan, China and great wars, clique roads,
doubled state-size thresholds, Siberia at life rating 45."""
import re

# ------------------------------------------------------------------ 02_world.py
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep(r'''    ("PSE", ("Persian Empire", "Persian", (60, 160, 90), "persian")),
''', r'''    ("PSE", ("Persian Empire", "Persian", (60, 160, 90), "persian")),
    ("SMG", ("Southern Ming", "Ming", (200, 40, 40), "min")),
    ("TNG", ("Tungning", "Tungning", (40, 130, 170), "min")),
    ("SUV", ("Suvarnabhumi", "Suvarnabhumi", (225, 175, 55), "thai")),
''')
rep(r'''        lr = max(lr or 0, 35)
''', r'''        lr = max(lr or 0, 35)
        if p in SIBERIA:
            lr = 45                 # empty, rich and waiting: the great prize of the north
''')
open("02_world.py", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ 03c_statesize.py
s = open("03c_statesize.py", encoding="utf-8").read()
rep(r'''ERAS = [(880201, None, 1860, [100000, 450000, 750000, 1050000]),       # Heartbreaker's thresholds and years
        (880202, 1860, 1900, [150000, 650000, 1050000, 1500000]),
        (880203, 1900, None, [200000, 800000, 1400000, 2000000])]''',
    r'''ERAS = [(880201, None, 1860, [200000, 900000, 1500000, 2100000]),       # Heartbreaker's years, twice its thresholds
        (880202, 1860, 1900, [300000, 1300000, 2100000, 3000000]),
        (880203, 1900, None, [400000, 1600000, 2800000, 4000000])]''')
open("03c_statesize.py", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ content.py
c = open("content.py", encoding="utf-8").read()
if "ROADS" not in c:
    c += r'''

# ------------------------------------------------------------------ the two roads of each great clique
# Once a clique has State and Government and holds the capital of the small neighbour it claims
# (TARGET), it must choose: press on against its rival, or settle down and absorb what it has.
# tag: (name of the road of conquest, name of the road of consolidation)
ROADS = {
    "ZHL": ("Beyond the Pass", "The Capital Region"),
    "FTN": ("Enter the Pass", "The Three Eastern Provinces"),
    "AHC": ("Down the Yangtze", "The Huai Compact"),
    "SXI": ("Across the Yellow River", "The Model Province Extended"),
    "GMJ": ("East through Tongguan", "The Northwest Compact"),
    "SDG": ("The Central Plain Campaign", "The Yellow Sea Realm"),
    "HNA": ("March to the Sea", "Heart of the Central Plain"),
    "JSU": ("Up the River", "The Jiangnan League"),
    "ZHJ": ("The Fujian Expedition", "The Maritime Republic"),
    "FUJ": ("North along the Coast", "The Two Shores"),
    "GDG": ("The Western Expedition", "The Pearl River Commonwealth"),
    "GXI": ("Seize the Delta", "The Southern Frontier"),
    "HNC": ("Into the Hills", "The Federal Charter"),
    "HBE": ("Down to Poyang", "The Thoroughfare of Nine Provinces"),
    "SZC": ("The Southern Campaign", "The Land of Abundance"),
    "YNN": ("Into the Basin", "The Burma Road"),
    "GZH": ("Down the Yuan River", "The Mountain Compact"),
    "XBI": ("Through the Jade Gate", "The Hui Commonwealth"),
    "XIN": ("Back through the Corridor", "The Governorate of the Six Cities"),
    "JXI": ("Up to Wuhan", "The River and the Sea"),
}
FOREIGN_CULTURE = {"KOR": "korean", "DAI": "vietnamese", "BUR": "burmese"}
'''
    open("content.py", "w", encoding="utf-8").write(c)

# ------------------------------------------------------------------ 03_gameplay.py
s = open("03_gameplay.py", encoding="utf-8").read()
rep(r'''"claim_korea": NATIO, "claim_annam": NATIO, "form_china": NATIO,''',
    r'''"claim_korea": NATIO, "claim_annam": NATIO, "form_china": REVO, "japan_accept_koreans": STATE,''')
rep(r'''         _acc("CHI") + "add_country_modifier = { name = mandate_of_heaven duration = -1 }\nbadboy = -10\n",''',
    r'''         _acc("CHI") + "add_country_modifier = { name = mandate_of_heaven duration = -1 }\nbadboy = -10\n"
         "great_wars_enabled = yes\nset_global_flag = great_wars_enabled\n",''')
rep(r'''Only the six great cliques and the eight regional states may do so.", 100)''',
    r'''Only the six great cliques and the eight regional states may do so. A reunited China ends the age of small wars: from this day the powers of the world fight Great Wars.", 100)''')
rep(r'''# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''', r'''# ---- Taiwan's second step, after Nationalism and Imperialism
_CAP = {k: int(v) for k, v in Wd["capital"].items()}
_cu = open(os.path.join(OUT, "common", "cultures.txt"), encoding=ENC).read()
def _culture(k):
    k = CM.get(k, k)
    assert re.search(r"(?m)^\t%s = \{" % k, _cu), k
    return k


once("taiwan_restore_the_ming", "Restore the Ming", "Guangdong is ours. Koxinga held Formosa in the name of the Ming; we shall finish what he began. The peoples of the southern coast and of the Yellow River are our own, and the state takes the old dynasty's name.",
     "tag = TWN\nhas_country_flag = did_taiwan_great_game", "war = no\n" + owns(*_canton),
     "".join("add_accepted_culture = %s\n" % _culture(k) for k in ("wu", "jianghuai", "jilu", "zhongyuan", "jin", "guanzhong")) + "prestige = 25\nchange_tag = SMG", tech=NATIO)
_nsw = [p for p in REGIONS["ENG_2468"] if p != 2508]                      # New South Wales without Norfolk Island
_mad = sorted(p for r in ("MAD_2117", "MAD_2121") for p in REGIONS[r] if OWNER.get(p) == "MAD")
assert 2468 in _nsw and len(_mad) == 8
once("taiwan_southern_ocean", "Lords of the Southern Ocean", "Batavia is ours and no fleet contests these seas. Our captains have planted the flag at Sydney cove and on the great island of Madagascar: move the seat of government to the new southern continent and proclaim the realm Koxinga dreamed of.",
     "tag = TWN\nhas_country_flag = did_taiwan_maritime_hegemon", "war = no\nowns = 1413",
     "".join("%d = { secede_province = THIS }\n%d = { add_core = THIS }\n" % (p, p) for p in _nsw + _mad) + "capital = 2468\nprestige = 25\nchange_tag = TNG", tech=NATIO)

# ---- the golden peninsula: Siam, the Malay states and Dai Viet
formable("SUV", "Suvarnabhumi", "suvarnabhumi", [_CAP["SIA"], _CAP["JOH"], _CAP["DAI"]], "OR = {\n\ttag = SIA\n\ttag = JOH\n\ttag = DAI\n}",
         "".join("add_accepted_culture = %s\n" % _culture(k) for k in ("thai", "malay", "vietnamese"))
         + "any_owned = { add_core = SUV }\nadd_country_modifier = { name = golden_peninsula duration = -1 }\n",
         "Bangkok, Johor Bahru and Hanoi answer to one court. Siamese, Malays and Vietnamese shall be one realm, the Land of Gold of the old books, and the whole world's migrants are welcome in it.", 50)

# ---- Japan: outside the modern world until it beats a clique at its own game
_wcaps = sorted({w[2] for w in WARLORDS.values()})
once("japan_continental_victory", "Lessons of the Continental War", "We have taken a warlord's capital, and with it his arsenals, his dockyards and his engineers. Everything the cliques know, we can now learn.",
     "tag = JAP\ncivilized = no", "OR = {\n" + "\n".join("\towns = %d" % p for p in _wcaps) + "\n}",
     "years_of_research = 5\nprestige = 20", "continental_lessons")
once("japan_accept_koreans", "One Realm across the Strait", "The peninsula and the islands share scripts, sages and enemies. Make the Koreans subjects equal before the Emperor.",
     "tag = JAP", "war = no\nowns = %d" % _CAP["KOR"], "add_accepted_culture = %s\nprestige = 5" % _culture("korean"))

# ---- every great clique chooses its road once it has swallowed the neighbour it claimed
for tag, (t_war, t_peace) in ROADS.items():
    rival, partner, target = RIVAL[tag], PARTNER[tag], TARGET[tag]
    mine_cu = {CLIQUE_CULTURE[tag][0]} | set(CLIQUE_CULTURE[tag][1])
    cands = [FOREIGN_CULTURE.get(target) or CLIQUE_CULTURE[target][0]] + [CLIQUE_CULTURE[x][0] for x in (partner, rival)] + list(CLIQUE_CULTURE[target][1] if target in CLIQUE_CULTURE else [])
    newcu = next(_culture(k) for k in cands if CM.get(k, k) not in {CM.get(x, x) for x in mine_cu})
    rprov = sorted(p for p, o in OWNER.items() if o == rival)
    choice("road_" + tag, STATE, [
        ("%s_road_war" % tag, t_war, "%s is ours. Now turn the army on %s: every province they hold is declared rightfully ours." % (NAMES[target], NAMES[rival]),
         "war = no\nowns = %d" % _CAP[target], "".join("%d = { add_core = THIS }\n" % p for p in rprov) + "prestige = 10", "road_of_conquest"),
        ("%s_road_peace" % tag, t_peace, "%s is ours. Enough: bind what we hold into one country, take its people in as our own, and let %s keep what is theirs." % (NAMES[target], NAMES[rival]),
         "war = no\nowns = %d" % _CAP[target], "add_accepted_culture = %s\nrelation = { who = %s value = 100 }\nprestige = 10\nbadboy = -3" % (newcu, rival), "road_of_consolidation")],
        potential="tag = %s" % tag)

# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''')
rep(r'''mod("taiwanese_dream", "The Taiwanese Dream",''', r'''mod("golden_peninsula", "The Golden Peninsula", "Suvarnabhumi, the Land of Gold: every ship that rounds the cape brings settlers.", global_immigrant_attract=0.75)
mod("continental_lessons", "Lessons of the Continental War", "Captured arsenals, dockyards and engineers.", naval_organisation=0.1, research_points_modifier=0.25)
mod("road_of_conquest", "Road of Conquest", "The army has its orders and the nation its enemy.", land_organisation=0.05, org_regain=0.1, cb_generation_speed_modifier=0.25)
mod("road_of_consolidation", "Road of Consolidation", "One law and one school for everyone under our flag.", global_assimilation_rate=0.25, core_pop_militancy_modifier=-0.02, tax_efficiency=0.03)
mod("taiwanese_dream", "The Taiwanese Dream",''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
