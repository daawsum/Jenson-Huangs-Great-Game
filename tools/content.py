"""Clique identity data: regional cultures, rivals, partners, expansion targets, starting line-ups
and unique decisions. Imported by 02_world.py and 03_gameplay.py."""

# ------------------------------------------------------------------ regional Han cultures
# key: (name, vanilla culture whose name lists and unit look are cloned, colour)
NEW_CULTURES = {
    "jilu": ("Jilu", "beifaren", (214, 190, 110)),
    "zhongyuan": ("Zhongyuan", "beifaren", (196, 160, 110)),
    "jin": ("Jin", "beifaren", (160, 120, 80)),
    "guanzhong": ("Guanzhong", "beifaren", (120, 160, 120)),
    "dongbei": ("Dongbei", "beifaren", (170, 190, 90)),
    "jianghuai": ("Jianghuai", "nanfaren", (130, 160, 210)),
    "wu": ("Wu", "nanfaren", (140, 210, 190)),
    "chu": ("Chu", "nanfaren", (180, 120, 180)),
    "xiang": ("Xiang", "nanfaren", (225, 110, 80)),
    "gan": ("Gan", "nanfaren", (235, 180, 100)),
    "bashu": ("Ba-Shu", "nanfaren", (165, 80, 80)),
    "dian": ("Dian", "nanfaren", (140, 100, 160)),
}
HAN = list(NEW_CULTURES) + ["yue", "min"]
# clique: (primary culture, accepted cultures, culture given to the ordinary Han pops on its land)
CLIQUE_CULTURE = {
    "ZHL": ("jilu", ["zhongyuan"], "jilu"), "SDG": ("jilu", ["jianghuai"], "jilu"), "RHE": ("jilu", ["mongol"], "jilu"),
    "CHH": ("mongol", ["jin"], "jin"), "SYN": ("jin", ["mongol"], "jin"), "SXI": ("jin", ["zhongyuan"], "jin"),
    "HNA": ("zhongyuan", ["jilu"], "zhongyuan"), "XZC": ("zhongyuan", ["jianghuai"], "zhongyuan"),
    "GMJ": ("guanzhong", ["jin"], "guanzhong"), "XBI": ("guanzhong", ["tibetan"], "guanzhong"),
    "NXA": ("guanzhong", ["mongol"], "guanzhong"), "QHI": ("guanzhong", ["tibetan"], "guanzhong"),
    "XIN": ("guanzhong", ["uighur"], "guanzhong"), "KSG": ("uighur", ["guanzhong"], "guanzhong"),
    "FTN": ("dongbei", ["manchu"], "dongbei"), "JLN": ("manchu", ["dongbei"], "dongbei"), "HLJ": ("dongbei", ["manchu", "mongol"], "dongbei"),
    "AHC": ("jianghuai", ["zhongyuan"], "jianghuai"), "JSU": ("jianghuai", ["wu"], "jianghuai"),
    "ZHJ": ("wu", ["min"], "wu"), "SHG": ("wu", ["jianghuai"], "wu"),
    "HBE": ("chu", ["xiang"], "chu"), "HNC": ("xiang", ["chu"], "xiang"), "JXI": ("gan", ["chu"], "gan"),
    "SZC": ("bashu", ["dian"], "bashu"), "CQG": ("bashu", ["chu"], "bashu"), "XKG": ("tibetan", ["bashu"], "bashu"),
    "YNN": ("dian", ["bashu"], "dian"), "GZH": ("dian", ["xiang"], "dian"),
    "GDG": ("yue", ["min"], "yue"), "GXI": ("yue", ["dian"], "yue"), "HNI": ("yue", [], "yue"),
    "FUJ": ("min", ["wu"], "min"), "TWN": ("min", [], "min"), "TIB": ("tibetan", [], "bashu"), "MGL": ("mongol", [], "jin"),
}
FORMABLE_CULTURES = {
    "CHI": HAN + ["manchu"], "BYG": ["jilu", "zhongyuan", "jin"], "LGG": ["yue", "min"], "SHU": ["bashu", "dian"],
    "WUU": ["wu", "jianghuai"], "CHU": ["chu", "xiang", "gan"], "DIA": ["dian", "bashu"],
    "NWF": ["guanzhong", "uighur", "mongol", "tibetan"], "MZG": ["dongbei", "manchu"],
}

# ------------------------------------------------------------------ rivals, partners, targets, patrons
RIVALS = [("ZHL", "FTN"), ("AHC", "JSU"), ("SXI", "GMJ"), ("SDG", "HNA"), ("ZHJ", "FUJ"),
          ("GDG", "GXI"), ("HNC", "GZH"), ("HBE", "JXI"), ("SZC", "YNN"), ("XBI", "XIN")]
PARTNERS = [("ZHL", "SDG"), ("FTN", "AHC"), ("JSU", "ZHJ"), ("SXI", "HNA"), ("GMJ", "XBI"),
            ("FUJ", "GDG"), ("GXI", "HNC"), ("YNN", "GZH"), ("SZC", "HBE"), ("JXI", "XIN")]
RIVAL = {a: b for a, b in RIVALS}
RIVAL.update({b: a for a, b in RIVALS})
PARTNER = {a: b for a, b in PARTNERS}
PARTNER.update({b: a for a, b in PARTNERS})
# the weaker neighbour each major claims; several are claimed twice on purpose
TARGET = {"ZHL": "RHE", "FTN": "JLN", "AHC": "XZC", "SXI": "SYN", "GMJ": "NXA", "SDG": "KOR", "HNA": "XZC", "JSU": "SHG",
          "ZHJ": "TWN", "FUJ": "TWN", "GDG": "HNI", "GXI": "DAI", "HNC": "CQG", "HBE": "CQG", "SZC": "XKG", "YNN": "BUR",
          "GZH": "CQG", "XBI": "QHI", "XIN": "KSG", "JXI": "SHG"}
# the major a minor naturally looks to; the major can absorb it by treaty instead of war
PATRON = {"JLN": "FTN", "HLJ": "FTN", "RHE": "ZHL", "CHH": "ZHL", "SYN": "SXI", "NXA": "XBI", "QHI": "XBI", "XKG": "SZC",
          "CQG": "SZC", "HNI": "GDG", "TWN": "FUJ", "SHG": "JSU", "XZC": "AHC", "KSG": "XIN", "TIB": "XIN"}

# ------------------------------------------------------------------ starting line-up
# army: extra army techs, three field armies with artillery | navy: full naval techs, a real fleet
# industry: full industry techs, six factories | commerce: full commerce techs, cheap loans
# frontier: cavalry armies, fewer techs, cheap supply
ARCHETYPE = {"ZHL": "army", "FTN": "army", "GMJ": "army", "GXI": "army", "HNC": "army",
             "SDG": "navy", "FUJ": "navy", "GDG": "navy", "ZHJ": "navy",
             "SXI": "industry", "HBE": "industry", "JSU": "industry", "AHC": "industry",
             "JXI": "commerce", "SZC": "commerce", "HNA": "commerce",
             "XBI": "frontier", "XIN": "frontier", "YNN": "frontier", "GZH": "frontier"}
CAPITALS = {"ZHL": 1612, "FTN": 1479, "AHC": 1470, "JSU": 2221, "SXI": 1572, "GMJ": 1559, "SDG": 1563, "HNA": 1508, "ZHJ": 1604,
            "FUJ": 1482, "GDG": 1493, "GXI": 1503, "HNC": 1524, "GZH": 1505, "HBE": 1522, "JXI": 1545, "SZC": 1578, "YNN": 1601,
            "XBI": 1490, "XIN": 1600}

# ------------------------------------------------------------------ unique decisions
# tag: [identity decision, development decision, ambition]
#   identity:    (title, text, {modifier})                     free, available from day one
#   development: (title, text, cost, {modifier})               costs money, needs peace
#   ambition:    (title, text, modifier name, {modifier})      needs the rival's capital
IDENTITY = {
    "ZHL": [("Convene the Peking Parliament", "Whoever holds the old capital speaks for China abroad.", {"diplomatic_points_modifier": 0.5, "prestige": 0.02}),
            ("Baoding Military Academy", "The school that trained a generation of northern officers.", 40000, {"leadership": 2, "land_unit_start_experience": 15}),
            ("Break the Fengtian Menace", "Mukden has fallen. No army can now come through the Pass.", "Master of the North", {"land_organisation": 0.15, "tax_efficiency": 0.08, "mobilisation_size": 0.02})],
    "FTN": [("South Manchurian Railway Zone", "Rail, coal and soybeans make Manchuria the richest frontier in Asia.", {"factory_throughput": 0.1, "rgo_output": 0.08}),
            ("Expand the Mukden Arsenal", "Mortars, shells and an armoured train works.", 50000, {"supply_consumption": -0.15, "land_attack_modifier": 0.08}),
            ("Enter the Pass", "The Fengtian army rides into Beijing.", "Generalissimo of the North", {"land_organisation": 0.1, "prestige": 0.03, "mobilisation_size": 0.03})],
    "AHC": [("Found the Anfu Club", "A parliamentary machine bought and paid for.", {"diplomatic_points_modifier": 0.3, "loan_interest": -0.3}),
            ("Raise the War Participation Army", "Foreign money, foreign instructors, our officers.", 45000, {"land_organisation": 0.1, "land_unit_start_experience": 15}),
            ("Seize the Southern Capital", "Nanjing is ours and the lower Yangtze with it.", "Lord of the Lower Yangtze", {"tax_efficiency": 0.1, "factory_throughput": 0.08})],
    "JSU": [("League of Five Provinces", "A merchants' compact from Nanjing to the sea.", {"tax_efficiency": 0.08, "factory_throughput": 0.05}),
            ("Jinling Arsenal", "Modern guns from the oldest arsenal on the Yangtze.", 45000, {"supply_consumption": -0.1, "land_defense_modifier": 0.08}),
            ("Humble the Anhui Clique", "Anqing has fallen and the river is ours to its head.", "Master of the River", {"rgo_output": 0.08, "naval_organisation": 0.15, "tax_efficiency": 0.05})],
    "SXI": [("Village Government System", "Every village a school, a militia and a ledger.", {"tax_efficiency": 0.1, "core_pop_militancy_modifier": -0.02}),
            ("Taiyuan Arsenal", "Shanxi makes its own rifles, its own rails, its own gauge.", 45000, {"factory_throughput": 0.12, "supply_consumption": -0.1}),
            ("Take the Passes of Guanzhong", "Xian is ours. The northwest opens.", "Lord Within the Passes", {"land_defense_modifier": 0.12, "farm_rgo_eff": 0.1})],
    "GMJ": [("Soldiers of the People", "Drill, hymns, road-building and no looting.", {"org_regain": 0.2, "global_pop_militancy_modifier": -0.01}),
            ("Northwest Colonisation Bureau", "Settle soldiers on the frontier land.", 35000, {"farm_rgo_eff": 0.12, "mobilisation_size": 0.02}),
            ("Break the Model Province", "Taiyuan's arsenals now arm our divisions.", "Marshal of the Northwest", {"land_organisation": 0.12, "factory_throughput": 0.08})],
    "SDG": [("Hire the White Russians", "Armoured trains and men with nowhere else to go.", {"land_unit_start_experience": 20, "mobilisation_size": 0.02}),
            ("Qingdao Naval Yard", "A deep-water port with German docks.", 50000, {"naval_organisation": 0.2}),
            ("Take the Central Plains", "Kaifeng has fallen; the Yellow River is ours.", "Lord of the Yellow River", {"farm_rgo_eff": 0.12, "tax_efficiency": 0.06})],
    "HNA": [("Enrol the Red Spears", "The village societies will fight for whoever arms them.", {"mobilisation_size": 0.04, "core_pop_militancy_modifier": -0.01}),
            ("Zhengzhou Rail Junction", "Where the north-south and east-west lines cross.", 40000, {"factory_throughput": 0.08, "rgo_output": 0.05}),
            ("March to the Sea", "Jinan is taken and Shandong's ports with it.", "Master of the Plains and Ports", {"tax_efficiency": 0.08, "naval_organisation": 0.1})],
    "ZHJ": [("Ningbo Banking Guild", "The financiers of Shanghai are Ningbo men.", {"loan_interest": -0.5, "tax_efficiency": 0.06}),
            ("Zhoushan Fleet Base", "An island anchorage commanding the coast.", 50000, {"naval_organisation": 0.2}),
            ("Close the Fujian Coast", "Fuzhou is ours. The whole southeast coast answers to Hangzhou.", "Admiral of the Southeast", {"naval_organisation": 0.15, "rgo_output": 0.08})],
    "FUJ": [("Kinsmen in the Southern Seas", "Every Fujian family has a cousin in Manila, Malacca or Batavia.", {"global_immigrant_attract": 0.1, "tax_efficiency": 0.05, "naval_organisation": 0.1}),
            ("Mawei Shipyard", "The Foochow arsenal builds a modern squadron.", 50000, {"naval_organisation": 0.2, "factory_throughput": 0.05}),
            ("Take Hangzhou", "Zhejiang's silk and silver flow south.", "Lord of the Coast", {"tax_efficiency": 0.1, "factory_throughput": 0.06})],
    "GDG": [("Revolutionary Party", "A party with a programme, cadres and a cause.", {"research_points_modifier": 0.1, "global_pop_consciousness_modifier": 0.01}),
            ("Canton Merchant Volunteer Corps", "The guilds pay for their own regiments.", 35000, {"mobilisation_size": 0.02, "tax_efficiency": 0.05}),
            ("Unite the Two Guangs", "Guilin is taken; Liangguang is one.", "Generalissimo of the South", {"land_organisation": 0.12, "research_points_modifier": 0.08})],
    "GXI": [("Militia of Every Village", "The Guangxi system: every man trained, every village a company.", {"mobilisation_size": 0.05, "land_defense_modifier": 0.08}),
            ("Liuzhou Machine Works", "Workshops in the hills where no fleet can reach.", 35000, {"factory_throughput": 0.08, "supply_consumption": -0.1}),
            ("Take Canton", "The richest city of the south is ours.", "Master of the Pearl River", {"tax_efficiency": 0.12, "naval_organisation": 0.1})],
    "HNC": [("Hunan Provincial Constitution", "Hunan for the Hunanese, by its own charter.", {"core_pop_militancy_modifier": -0.03, "research_points_modifier": 0.05}),
            ("Changsha Normal School", "Teachers, and trouble, for all of China.", 30000, {"research_points_modifier": 0.1, "global_pop_consciousness_modifier": 0.01}),
            ("Subdue the Guizhou Hills", "Guiyang is ours and the hill roads are open.", "Lord of the Southern Roads", {"land_organisation": 0.1, "mine_rgo_eff": 0.12})],
    "GZH": [("Opium Road Tolls", "Every caravan from Yunnan pays at our passes.", {"tax_efficiency": 0.1, "global_pop_militancy_modifier": 0.01}),
            ("Hill Forts", "Stone, altitude and patience.", 30000, {"land_defense_modifier": 0.15, "max_attrition": -1}),
            ("Descend on Changsha", "The hill men hold the rice plain.", "Lord of Hills and Plain", {"farm_rgo_eff": 0.15, "mobilisation_size": 0.02})],
    "HBE": [("Hanyeping Iron and Coal", "The only integrated iron works in China.", {"factory_throughput": 0.12, "mine_rgo_eff": 0.1}),
            ("Wuhan River Flotilla", "Gunboats command a thousand miles of river.", 40000, {"naval_organisation": 0.15, "rgo_output": 0.05}),
            ("Take Nanchang", "Jiangxi's porcelain and tungsten are ours.", "Master of the Middle Yangtze", {"tax_efficiency": 0.08, "factory_throughput": 0.08})],
    "JXI": [("Jingdezhen Kilns", "Porcelain is still the world's favourite Chinese word.", {"factory_throughput": 0.08, "tax_efficiency": 0.06}),
            ("Tungsten Monopoly", "Every arsenal in the world needs what our hills hold.", 40000, {"mine_rgo_eff": 0.2, "loan_interest": -0.3}),
            ("Take the Three Towns", "Wuhan is ours: iron, river and rail.", "Lord of the Middle Kingdom's Heart", {"factory_throughput": 0.1, "land_organisation": 0.08})],
    "SZC": [("Garrison Area System", "Every general his own district, his own taxes, his own army.", {"mobilisation_size": 0.04, "tax_efficiency": -0.03, "land_defense_modifier": 0.08}),
            ("Zigong Salt Wells", "Brine, gas and the oldest deep drilling on Earth.", 35000, {"tax_efficiency": 0.1, "rgo_output": 0.05}),
            ("March on Kunming", "Yunnan's tin and the Burma road are ours.", "King of the Southwest", {"mine_rgo_eff": 0.15, "land_organisation": 0.08})],
    "YNN": [("National Protection Army", "The army that once marched to save the Republic.", {"land_organisation": 0.1, "prestige": 0.02}),
            ("Gejiu Tin Mines", "The richest tin field in Asia, and a railway to the sea.", 40000, {"mine_rgo_eff": 0.2, "tax_efficiency": 0.05}),
            ("Descend into Sichuan", "Chengdu is ours, and the granary of the west.", "Protector of the Southwest", {"farm_rgo_eff": 0.15, "mobilisation_size": 0.03})],
    "XBI": [("The Ma Family Compact", "Three houses, one name, one cavalry.", {"land_unit_start_experience": 20, "org_regain": 0.1}),
            ("Hexi Corridor Garrisons", "A fort at every oasis from Lanzhou to the Jade Gate.", 30000, {"land_defense_modifier": 0.1, "supply_consumption": -0.1}),
            ("Take Urumqi", "The Silk Road is ours from end to end.", "Lord of the Silk Road", {"tax_efficiency": 0.1, "rgo_output": 0.08})],
    "XIN": [("Closed Frontier", "No newspapers, no railways, no trouble.", {"core_pop_militancy_modifier": -0.04, "research_points_modifier": -0.05, "tax_efficiency": 0.06}),
            ("Karez and Oasis Farms", "Water under the desert feeds a new province.", 30000, {"farm_rgo_eff": 0.2, "global_population_growth": 0.0005}),
            ("Take Lanzhou", "The Yellow River's upper course is ours.", "Viceroy of the West", {"land_organisation": 0.1, "mobilisation_size": 0.03})],
}


# Literacy at the start. The examination heartlands (Jiangnan, Zhejiang, Anhui's academies, Hunan's
# Yuelu school), the merchant south (Canton, Fujian) and the capital read; the frontier does not.
LITERACY = {"JSU": 0.45, "ZHJ": 0.45, "SHG": 0.50, "GDG": 0.40, "FUJ": 0.38, "ZHL": 0.38, "AHC": 0.36, "HNC": 0.34,
            "SDG": 0.30, "HBE": 0.30, "JXI": 0.30, "SXI": 0.28, "SZC": 0.26, "CQG": 0.26, "FTN": 0.24, "HNA": 0.22,
            "TWN": 0.24, "XZC": 0.20, "GXI": 0.18, "HNI": 0.16, "GMJ": 0.16, "YNN": 0.14, "GZH": 0.12, "JLN": 0.14,
            "HLJ": 0.10, "RHE": 0.10, "CHH": 0.08, "SYN": 0.08, "NXA": 0.08, "XBI": 0.08, "QHI": 0.05, "XKG": 0.05,
            "XIN": 0.06, "KSG": 0.05, "TIB": 0.06}

# Who may proclaim which Chinese state. The eight regional states can each go on to proclaim China.
FORMERS = {"BYG": ["ZHL", "AHC", "SDG", "HNA"], "LGG": ["GDG", "GXI"], "SHU": ["SZC", "CQG"], "WUU": ["JSU", "ZHJ", "SHG"],
           "CHU": ["HBE", "HNC", "JXI"], "DIA": ["YNN", "GZH"], "NWF": ["GMJ", "XBI", "XIN"], "MZG": ["FTN", "JLN", "HLJ"]}
FORMERS["CHI"] = ["ZHL", "FTN", "GDG", "JSU", "AHC", "HBE"] + [t for t in FORMERS]
