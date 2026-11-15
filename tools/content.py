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
LITERACY = {"JSU": 0.45, "ZHJ": 0.45, "SHG": 0.70, "GDG": 0.40, "FUJ": 0.38, "ZHL": 0.38, "AHC": 0.36, "HNC": 0.34,
            "SDG": 0.30, "HBE": 0.30, "JXI": 0.30, "SXI": 0.28, "SZC": 0.26, "CQG": 0.26, "FTN": 0.24, "HNA": 0.22,
            "TWN": 0.70, "XZC": 0.20, "GXI": 0.18, "HNI": 0.70, "GMJ": 0.16, "YNN": 0.14, "GZH": 0.12, "JLN": 0.14,
            "HLJ": 0.10, "RHE": 0.10, "CHH": 0.08, "SYN": 0.08, "NXA": 0.08, "XBI": 0.08, "QHI": 0.05, "XKG": 0.05,
            "XIN": 0.06, "KSG": 0.05, "TIB": 0.06}

# Who may proclaim which Chinese state. The eight regional states can each go on to proclaim China.
FORMERS = {"BYG": ["ZHL", "AHC", "SDG", "HNA"], "LGG": ["GDG", "GXI"], "SHU": ["SZC", "CQG"], "WUU": ["JSU", "ZHJ", "SHG"],
           "CHU": ["HBE", "HNC", "JXI"], "DIA": ["YNN", "GZH"], "NWF": ["GMJ", "XBI", "XIN"], "MZG": ["FTN", "JLN", "HLJ"]}
FORMERS["CHI"] = ["ZHL", "FTN", "GDG", "JSU", "AHC", "HBE"] + [t for t in FORMERS]


# ------------------------------------------------------------------ minerals of China
# Every coal, iron and sulphur province in China is reset and placed again where the deposits are.
# Sources: USGS Open-File Report 00-047 (coal-bearing regions and major mines of China), US Bureau
# of Mines Minerals Yearbooks (China), "Spatio-temporal distribution and tectonic settings of the
# major iron deposits in China", Earth Science Frontiers 2018 25(3) on China's sulphur resources.
CN_MINERALS = {
    # coal
    1576: "coal",   # Datong (Datong-Ningwu field)
    1572: "coal",   # Taiyuan (Xishan)
    3349: "coal",   # Pingding (Yangquan)
    1574: "coal",   # Luan (Changzhi)
    3350: "coal",   # Zezhou (Jincheng anthracite)
    1573: "coal",   # Fenzhou (Fenxi)
    1616: "coal",   # Tangshan (Kailuan)
    3379: "coal",   # Guangping (Fengfeng, Handan)
    3260: "coal",   # Tieling (Fushun and Tiefa)
    3377: "coal",   # Chaoyang (Beipiao, Fuxin)
    3296: "coal",   # Xinxiang (Jiaozuo)
    1514: "coal",   # Runing (Pingdingshan)
    1567: "coal",   # Qingzhou (Zibo, Boshan)
    3345: "coal",   # Yanzhou
    3342: "coal",   # Jining (Zaozhuang)
    1472: "coal",   # Fengyang (Huainan)
    1542: "coal",   # Xuzhou (Jiawang, Huaibei)
    3325: "coal",   # Yuanzhou (Pingxiang, the Hanyeping collieries)
    1526: "coal",   # Baoqing (Lianyuan, Lengshuijiang)
    3339: "coal",   # Yulin (Shenmu-Fugu)
    3318: "coal",   # Dongsheng (Ordos)
    1083: "coal",   # Boli (Jixi, Qitaihe)
    3334: "coal",   # Sanxing (Hegang, Shuangyashan)
    3360: "coal",   # Guangan (Huaying mountain)
    3289: "coal",   # Xingyi (Liupanshui, Panxian)
    1506: "coal",   # Anshun
    3366: "coal",   # Qujing (Fuyuan)
    3274: "coal",   # Lingzhou (Lingwu, Ningdong)
    1600: "coal",   # Dihua (the Urumqi coalfield)
    3273: "coal",   # North Lanzhou (Yaojie, Jingyuan)
    3265: "coal",   # Xinzhu (north Taiwan coal measures)
    # iron
    3259: "iron",   # Liaoyang (Anshan, Benxi)
    1615: "iron",   # Jizhou (East Hebei: Zunhua, Qianan)
    3317: "iron",   # Zhangjiakou (Xuanhua, Longyan)
    1613: "iron",   # Chengde (Damiao)
    1522: "iron",   # Wuchang (Daye)
    1477: "iron",   # Taiping (Maanshan, Dangtu)
    1568: "iron",   # Taian (Laiwu)
    3348: "iron",   # Xinzhou (Lvliang-Taiyuan-Xinzhou district)
    1575: "iron",   # Pingyang (Linfen)
    3312: "iron",   # Baotou (Bayan Obo)
    1499: "iron",   # Hainan (Shilu)
    3267: "iron",   # Longyan (Makeng)
    1500: "iron",   # Shaozhou (Dabaoshan)
    1555: "iron",   # Jilin (Tonghua)
    1488: "iron",   # Jiayuguan (Jingtieshan)
    3368: "iron",   # Lijiang (Panzhihua)
    2562: "iron",   # Tainan
    3385: "iron",   # Fengshan
    # sulphur
    3282: "sulphur",   # Luoding (Yunfu, the largest pyrite deposit in China)
    3252: "sulphur",   # Tongling (pyrite)
    3362: "sulphur",   # Xuyong (Xuyong-Gulin pyrite)
    3309: "sulphur",   # Pingjiang (Liuyang)
    1597: "sulphur",   # Aksu (Kuqa native sulphur)
    1595: "sulphur",   # Ili
    1485: "sulphur",   # Taibei (Datun volcanoes, Beitou)
}
# what a province grows once it loses a mineral it should not have had
CN_FALLBACK = {"SXI": "grain", "GMJ": "grain", "HNA": "grain", "HNC": "tea", "HBE": "tea", "JXI": "tea", "SZC": "silk", "XBI": "wool",
               "XIN": "wool", "KSG": "cotton", "JLN": "timber", "HLJ": "timber", "RHE": "cattle", "SYN": "wool", "QHI": "wool", "FTN": "timber"}

# Oil found where China's oil fields are (vanilla's oil event, with these provinces): (year, province)
CN_OIL = [
    (1877, 3265),   # Xinzhu: Chuhuangkeng in Miaoli, drilled 1877
    (1880, 1561),   # Yenan: Yanchang, the mainland's first well (1907)
    (1885, 3268),   # Jiuquan: Yumen (1939)
    (1890, 1596),   # Tulta: Karamay (1955)
    (1890, 3330),   # Hulan: Daqing (1959)
    (1890, 1552),   # Qiqihar: Daqing
    (1895, 3346),   # Binzhou: Shengli, the Yellow River delta
    (1895, 1480),   # Jinzhou: Liaohe
    (1895, 3382),   # Cangzhou: Dagang and Huabei
    (1895, 3336),   # Changchun: Jilin field (Songyuan)
    (1900, 1556),   # Makhai: Qaidam (Lenghu)
    (1900, 1583),   # Shunqing: central Sichuan (Nanchong)
    (1900, 1614),   # Daming: Zhongyuan (Puyang)
    (1900, 1513),   # Nanyang
    (1900, 1520),   # Jingzhou: Jianghan (Qianjiang)
    (1900, 3275),   # Qingyang: Changqing (Ordos basin)
]

# ------------------------------------------------------------------ life rating of China
# Where people have always lived thickest: the Yangtze and Pearl deltas and the Chengdu plain (40),
# the North China plain, the middle Yangtze and the Sichuan basin (37-38), then hill country, the
# loess plateau and Manchuria (32-35), the steppe and the dry north-west (27-31), and Tibet (25).
# Taiwan is 45.
CN_LIFE = {"JSU": 40, "SHG": 40, "ZHJ": 38, "GDG": 37, "ZHL": 38, "SDG": 38, "AHC": 38, "HBE": 38, "XZC": 37, "HNA": 37, "HNC": 37,
           "JXI": 37, "CQG": 37, "SZC": 37, "FUJ": 36, "FTN": 35, "GXI": 34, "SXI": 34, "GMJ": 34, "HNI": 34, "YNN": 33, "GZH": 32,
           "JLN": 32, "RHE": 31, "NXA": 31, "XBI": 30, "HLJ": 29, "CHH": 29, "SYN": 29, "XIN": 27, "KSG": 27, "XKG": 27, "QHI": 26,
           "TIB": 25, "TWN": 45, "MGL": 28}
CN_LIFE_PROV = {1604: 40, 1605: 40, 1606: 40, 1609: 40, 1608: 40,             # Hangzhou bay
                1493: 40, 3276: 40, 1496: 40, 1498: 40,                        # Pearl River delta
                1578: 40, 3356: 40, 3354: 40,                                  # Chengdu plain
                1582: 30, 3358: 30, 3359: 30,                                  # the Sichuan highlands
                3339: 31, 1561: 31,                                            # northern Shaanxi
                1488: 27, 3268: 27, 3269: 27,                                  # the Hexi corridor
                1601: 35, 1602: 35}                                            # Kunming and Dali basins


# ------------------------------------------------------------------ crops and fisheries of China
# Vanilla grows tea and silk almost everywhere south of the Yellow River. Tea stays in the real tea
# districts (Fujian, Huizhou and Liuan, Hangzhou, Xinyang, Hankou, Puer, Zunyi) and silk in the real
# silk districts (Suzhou, Hangzhou, Huzhou, Jiaxing, Yangzhou). The rest becomes what the place is
# known for.
CN_CROPS = {
    # --- grain: the wheat plain, the rice bowls and the four great rice markets
    1612: "grain",   # Beijing (the capital's wheat plain)
    3380: "grain",   # Langfang
    3381: "grain",   # North Shuntian
    3383: "grain",   # Baoding
    1511: "grain",   # Zhengzhou
    1478: "grain",   # Yingzhou (Huaibei wheat)
    3258: "grain",   # Bozhou
    1509: "grain",   # Guide
    3292: "grain",   # Shangqiu
    1512: "grain",   # Chenzhou
    3253: "grain",   # Bengbu
    1474: "grain",   # Luzhou (the Chaohu rice basin)
    3255: "grain",   # Chaohu
    3257: "grain",   # Wuhu (one of the four great rice markets)
    1476: "grain",   # Sizhou
    1536: "grain",   # Huaian (the Grand Canal granaries)
    1537: "grain",   # Changzhou (Wuxi, another of the four rice markets)
    3322: "grain",   # Gaoyou (the Lixiahe rice lowlands)
    1540: "grain",   # Taicangzhou (Taicang means "great granary")
    1516: "grain",   # Hanyang (the Jianghan plain)
    1517: "grain",   # Dean
    1519: "grain",   # Anlu
    1520: "grain",   # Jingzhou
    3301: "grain",   # Shashi
    3298: "grain",   # Suizhou
    3300: "grain",   # Jingmen
    1524: "grain",   # Changsha (rice market: "when Huguang ripens, the realm is fed")
    3305: "grain",   # Xiangtan
    1525: "grain",   # Changde (the Dongting lake plain)
    3306: "grain",   # Lizhou
    1527: "grain",   # Hengzhou
    1530: "grain",   # Yongzhou
    1545: "grain",   # Nanchang (the Poyang lake plain)
    1547: "grain",   # Jian
    3326: "grain",   # Linchuan
    1578: "grain",   # Chengdu (the Dujiangyan-irrigated plain)
    3354: "grain",   # Mianzhou
    3357: "grain",   # Wanxian
    3353: "grain",   # Fuling
    1583: "grain",   # Shunqing
    1601: "grain",   # Kunming (the Dian lake basin)
    1505: "grain",   # Guiyang
    # --- fruit
    3376: "fruit",   # Changping (peaches, persimmons and chestnuts of the hills north of Beijing)
    1618: "fruit",   # Zhongding (Zhaozhou snow pears)
    3382: "fruit",   # Cangzhou (golden-thread jujubes)
    3261: "fruit",   # Xingcheng (the pear and apple belt of western Liaoning)
    1565: "fruit",   # Laizhou (Laiyang pears, Yantai apples)
    3321: "fruit",   # Pizhou (the Dangshan pear country of the old Yellow River bed)
    1610: "fruit",   # Taizhou (Huangyan tangerines)
    1487: "fruit",   # Zhangzhou (citrus, lychee, longan, bananas)
    3264: "fruit",   # Xinghua (Putian lychee, longan and loquat)
    1494: "fruit",   # Chaozhou (Chaozhou mandarins)
    1497: "fruit",   # Huizhou (lychee)
    3277: "fruit",   # Jiaying (Meizhou pomelos)
    3278: "fruit",   # Leizhou (pineapple and tropical fruit)
    3280: "fruit",   # Qiongzhou (coconut and tropical fruit)
    3302: "fruit",   # Yichang (Yichang and Zigui oranges)
    3311: "fruit",   # Daozhou (Dao county oranges)
    3310: "fruit",   # Fenghuang (west Hunan citrus)
    1548: "fruit",   # Jianchang (Nanfeng tangerines)
    1550: "fruit",   # Ganzhou (the Gannan orange country)
    3363: "fruit",   # East Yibin (Luzhou and Hejiang lychee)
    1577: "fruit",   # Chongqing (Jiangjin oranges)
    1581: "fruit",   # Kuizhou (Fengjie oranges)
    3367: "fruit",   # Zhaotong (Zhaotong apples)
    3370: "fruit",   # Linan (Mengzi pomegranates)
    1490: "fruit",   # Lanzhou (melons, peaches and lily bulbs)
    1599: "fruit",   # Kumul (Hami melons)
    # --- fish: the fishing ports and the four great fishing grounds
    1617: "fish",    # Tianjin (Bohai bay)
    1481: "fish",    # Port Arthur (Dalian and the Liaodong grounds)
    1082: "fish",    # Haishenwai ("sea cucumber bay")
    1569: "fish",    # Weihaiwei (the Yantai-Weihai ground)
    1571: "fish",    # Yizhou (holds the Rizhao coast on this map)
    3320: "fish",    # Haizhou (the Haizhou bay ground)
    1541: "fish",    # Tongzhou (the Lusi ground)
    1538: "fish",    # Shanghai (the mouth of the Yangtze)
    1608: "fish",    # Ningbo (the Zhoushan ground, the largest in China)
    3375: "fish",    # Chuzhou (holds the Wenzhou coast on this map)
    1611: "fruit",   # Wenzhou (Ou mandarins; its piece of the map is inland)
    3262: "fish",    # Funing (yellow croaker of Sandu bay)
    3279: "grain",   # Haifeng (its piece of the map is inland; Hong Kong and Macao fish this coast)
    1496: "fish",    # Hong Kong
    1498: "fish",    # Macao
    1495: "fish",    # Zhanjiang (the Beibu gulf ground)
    # --- the Sichuan highlands herd yak; they never grew silk
    1582: "cattle", 3358: "cattle", 3359: "cattle",
}
CN_FISH = {p for p, g in CN_CROPS.items() if g == "fish"}
assert not set(CN_CROPS) & set(CN_MINERALS), set(CN_CROPS) & set(CN_MINERALS)


# ------------------------------------------------------------------ the two roads of each great clique
# Once a clique has State and Government and holds the capital of the small neighbour it claims
# (TARGET), it must choose one of two roads for good. Almost all are roads of conquest; Shanxi and
# Hunan may instead turn inward and play tall.
# option: (title, text, claims, accepted cultures, modifier effects, new tag or None)
#   claims are tags (every province they own at the start becomes a core) or "SIBERIA".
ROADS = {
    "ZHL": [("Beyond the Shanhai Pass", "The Qing came through the pass to take Beijing. We go out through it: Manchuria to the Amur is declared ours.",
             ["FTN", "JLN", "HLJ", "RHE"], ["dongbei", "manchu"], dict(land_organisation=0.08, cb_generation_speed_modifier=0.25), None),
            ("The Tribute Restored", "Seoul and Urga once sent envoys to kneel in Beijing. They will again, or be garrisoned: Korea and Mongolia are claimed for the capital.",
             ["KOR", "MGL", "CHH"], ["korean", "mongol"], dict(prestige=0.02, diplomatic_points_modifier=0.25, org_regain=0.1), None)],
    "FTN": [("Enter the Pass", "Every master of Manchuria has ended by riding through the Shanhai Pass. Zhili and the capital are ours by right of the strongest army.",
             ["ZHL", "RHE", "CHH"], ["jilu"], dict(land_organisation=0.1, mobilisation_size=0.02), None),
            ("The Great Northern Wilderness", "Turn our backs on the quarrels of China. The forests from the Amur to the Arctic are empty, rich and unguarded, and Korea lies open beside them.",
             ["SIBERIA", "KOR"], ["korean", "siberian"], dict(global_immigrant_attract=0.5, farm_rgo_eff=0.1, mine_rgo_eff=0.1), None)],
    "AHC": [("The Huai Army Marches Again", "Li Hongzhang's Huai Army took Jiangnan from the Taiping. It shall take it again: Nanjing, Suzhou and Shanghai are claimed.",
             ["JSU", "SHG", "ZHJ"], ["wu"], dict(land_organisation=0.08, tax_efficiency=0.05), None),
            ("Regent of the North", "Duan Qirui ruled Beijing through loans and bayonets. March on the plain: Henan, Xuzhou and Shandong first, the capital after.",
             ["HNA", "XZC", "SDG"], ["jilu"], dict(org_regain=0.15, loan_interest=-0.25, cb_generation_speed_modifier=0.25), None)],
    "SXI": [("The Model Province", "Let the others bleed each other white. Behind the passes we build arsenals, schools and a narrow-gauge railway no invader's trains can use.",
             [], [], dict(factory_throughput=0.2, education_efficiency_modifier=0.2, land_defense_modifier=0.2, tax_efficiency=0.1, research_points_modifier=0.1, mobilisation_size=-0.01), None),
            ("Out of the Passes", "Shanxi merchants financed half of China; Shanxi soldiers can own it. Down onto the Wei valley and out over the Great Wall.",
             ["GMJ", "SYN", "CHH", "NXA"], ["guanzhong", "mongol"], dict(land_organisation=0.08, tax_efficiency=0.03), None)],
    "GMJ": [("The Long March West", "The Northwest Army was made for empty country. Take the Hexi corridor, the oases and the Muslim marches as far as the Pamirs.",
             ["XBI", "NXA", "QHI", "XIN", "KSG"], ["uighur", "tibetan"], dict(supply_consumption=-0.15, land_organisation=0.08, max_attrition=-1), None),
            ("The Christian General's Crusade", "Feng Yuxiang baptised his regiments with a fire hose. Now he will cleanse the Central Plain of warlords: Shanxi and Henan are claimed for the people's army.",
             ["SXI", "HNA"], ["zhongyuan"], dict(land_unit_start_experience=20, core_pop_militancy_modifier=-0.02, org_regain=0.1), None)],
    "SDG": [("The Yellow Sea Realm", "From Qingdao and Weihaiwei the sea is ours. Korea is one night's sail away, and beyond it the islands of Japan.",
             ["KOR", "JAP"], ["korean"], dict(naval_organisation=0.15, land_organisation=0.05, prestige=0.01), None),
            ("Heirs of Qi and Lu", "This is the soil of Confucius and Mencius, and their country ran wider than our borders. Take the old states of the plain back.",
             ["HNA", "XZC", "ZHL"], ["zhongyuan"], dict(education_efficiency_modifier=0.1, core_pop_militancy_modifier=-0.02, land_organisation=0.05), None)],
    "HNA": [("Hunting the Deer on the Central Plain", "Whoever takes the plain takes the realm; so it has been since the Zhou. Every army that borders us is hunting the same deer: strike first, at Shandong and Shanxi.",
             ["SDG", "SXI", "ZHL"], ["jilu", "jin"], dict(land_organisation=0.1, org_regain=0.1), None),
            ("South to the Han River", "The plain feeds armies but cannot pay them. Hankou can: take the middle Yangtze and its customs houses.",
             ["HBE", "AHC"], ["chu", "jianghuai"], dict(tax_efficiency=0.08, supply_consumption=-0.1), None)],
    "JSU": [("The League of Seven Provinces", "Sun Chuanfang called himself commander of five provinces. Make it seven: Zhejiang, Fujian, Jiangxi and Anhui answer to Nanjing.",
             ["ZHJ", "FUJ", "JXI", "AHC"], ["min", "gan"], dict(tax_efficiency=0.05, land_organisation=0.05, diplomatic_points_modifier=0.25), None),
            ("The Treaty Port Empire", "Nanjing's wealth is the river's mouth. Seize Shanghai, then do to others what the treaty powers did to us: the Philippines and the Malay ports are claimed.",
             ["SHG", "PHI", "JOH"], ["malay"], dict(naval_organisation=0.15, tax_efficiency=0.08, factory_throughput=0.05), None)],
    "ZHJ": [("The Zhoushan Thalassocracy", "Ningbo's captains traded to Nagasaki and Manila before any European did. Formosa, the Ryukyus' masters in Japan and the Philippines are claimed for the fleet.",
             ["TWN", "JAP", "PHI"], ["japanese"], dict(naval_organisation=0.2, research_points_modifier=0.05, prestige=0.01), None),
            ("Heirs of Wuyue", "The kingdom of Wuyue held the whole delta and the Fujian coast in peace while the north burned. Take its old borders by force.",
             ["JSU", "SHG", "FUJ"], ["jianghuai"], dict(tax_efficiency=0.08, land_defense_modifier=0.1, education_efficiency_modifier=0.05), None)],
    "FUJ": [("The Lanfang Republic", "Hakka miners once ruled a republic of their own in Borneo. Fujian's sons are already in every port of the southern seas: follow them with a fleet and proclaim the republic again, from Brunei to Manila.",
             ["BRU", "PHI", "JAV"], ["malay", "javan"], dict(naval_organisation=0.15, global_immigrant_attract=0.5), "LFG"),
            ("The Min-Yue Confederacy", "Before the Han came there was Minyue and Nanyue, one coast from the Min river to Hainan. Canton, Formosa and Hainan belong with us.",
             ["GDG", "TWN", "HNI"], ["yue"], dict(tax_efficiency=0.05, naval_organisation=0.1, land_organisation=0.05), None)],
    "GDG": [("The Northern Expedition", "Swear the army at Whampoa and march: Hunan, Jiangxi and Hubei first, then the Yangtze. The revolution will not stay in one province.",
             ["HNC", "JXI", "HBE"], ["xiang", "gan", "chu"], dict(land_organisation=0.1, org_regain=0.1, war_exhaustion=-0.01, cb_generation_speed_modifier=0.5), None),
            ("The Canton System Abroad", "For a century every foreign ship was made to trade at Canton alone. Now Canton's merchants will hold the foreign ports: Hanoi, Singapore and Bangkok.",
             ["DAI", "JOH", "SIA"], ["vietnamese", "malay", "thai"], dict(naval_organisation=0.1, tax_efficiency=0.1, factory_throughput=0.05), None)],
    "GXI": [("The Annam Protectorate", "The Black Flags of Guangxi fought for Annam when the court would not. Go back over the border and stay: all Vietnam is claimed, and Siam beyond it.",
             ["DAI", "SIA"], ["vietnamese", "thai"], dict(supply_consumption=-0.15, land_organisation=0.08, max_attrition=-1), None),
            ("The New Guangxi Clique", "Li Zongren and Bai Chongxi made a poor province the best-drilled in China. Its army deserves a richer country: Canton, Hunan and Guizhou.",
             ["GDG", "HNC", "GZH"], ["xiang"], dict(land_organisation=0.12, land_unit_start_experience=20, mobilisation_size=0.02), None)],
    "HNC": [("Hunan for the Hunanese", "A provincial constitution, a provincial army, and no northern or southern troops on our soil ever again. Let them come and try the passes.",
             [], [], dict(land_defense_modifier=0.25, mobilisation_size=0.04, education_efficiency_modifier=0.15, core_pop_militancy_modifier=-0.03, farm_rgo_eff=0.1, research_points_modifier=0.1), None),
            ("The Xiang Army Reborn", "Zeng Guofan raised the Xiang Army from these villages and it conquered half of China. Raise it again: Hubei, Jiangxi and Guizhou.",
             ["HBE", "JXI", "GZH"], ["chu", "gan"], dict(land_organisation=0.1, land_unit_start_experience=25, mobilisation_size=0.02), None)],
    "HBE": [("Thoroughfare of Nine Provinces", "Every road and river in China crosses at Wuhan. Whoever sits here may reach in any direction: Henan, Hunan and Jiangxi are claimed.",
             ["HNA", "HNC", "JXI"], ["zhongyuan", "gan"], dict(tax_efficiency=0.08, supply_consumption=-0.1, land_organisation=0.05), None),
            ("Up the Three Gorges", "Liu Bei went up the river from Jingzhou and won a kingdom. Our gunboats can pass the gorges now: Chongqing and Sichuan are claimed.",
             ["CQG", "SZC"], ["bashu"], dict(naval_organisation=0.1, land_organisation=0.08, farm_rgo_eff=0.05), None)],
    "SZC": [("The Road to Lhasa", "Zhao Erfeng marched from Chengdu to Lhasa with two thousand men. We have more. The marches, Kokonor and Tibet itself are claimed.",
             ["XKG", "QHI", "TIB"], ["tibetan"], dict(max_attrition=-2, supply_consumption=-0.2, land_organisation=0.05), None),
            ("Zhuge Liang's Northern Expeditions", "Six times the Chancellor of Shu went out through the Qinling passes and six times he failed. The seventh expedition is ours: Hanzhong, the Wei valley and the north-west.",
             ["GMJ", "XBI", "CQG"], ["guanzhong"], dict(land_organisation=0.1, org_regain=0.15, land_unit_start_experience=15), None)],
    "YNN": [("The Kingdom of Nanzhao", "Nanzhao ruled from Dali to the Irrawaddy and sacked Chengdu. Its heirs go south again: Burma and Siam are claimed for a kingdom of the mountains.",
             ["BUR", "SIA"], ["burmese", "thai"], dict(max_attrition=-2, supply_consumption=-0.15, land_organisation=0.08), "NZO"),
            ("The National Protection War", "When Yuan Shikai made himself emperor it was Yunnan that marched to stop him. March again, down into Sichuan, Guizhou and Guangxi.",
             ["SZC", "GZH", "GXI"], ["bashu", "yue"], dict(land_organisation=0.1, land_unit_start_experience=20, prestige=0.01), None)],
    "GZH": [("The Opium Road to the Sea", "Our one crop needs a port. Force a road through Guangxi to the gulf and hold every toll station on it.",
             ["GXI", "HNI"], ["yue"], dict(tax_efficiency=0.12, supply_consumption=-0.1, land_organisation=0.05), None),
            ("Yelang Thinks Itself Great", "The king of Yelang asked the Han envoy whose realm was larger. Let no one laugh this time: Yunnan, Chongqing and western Hunan are claimed.",
             ["YNN", "CQG", "HNC"], ["bashu", "xiang"], dict(land_defense_modifier=0.15, land_organisation=0.08, max_attrition=-1), None)],
    "XBI": [("Dunganistan", "The Hui cavalry answers to no Han general. Ride west and carve a Muslim realm out of the oases: Xinjiang, Kashgaria and Kokand.",
             ["XIN", "KSG", "KOK"], ["uighur"], dict(land_organisation=0.1, org_regain=0.15, supply_consumption=-0.15), "DGN"),
            ("Lords of the Roof of the World", "Ma Bufang's riders broke the Tibetan tribes of Kokonor. Finish it: Qinghai, the marches and Lhasa.",
             ["QHI", "XKG", "TIB"], ["tibetan"], dict(max_attrition=-2, land_organisation=0.08, mobilisation_size=0.02), None)],
    "XIN": [("Protector-General of the Western Regions", "The Han and the Tang kept a Protector-General beyond the Pamirs. Revive the office: Kashgaria, Kokand, Bukhara and Khiva.",
             ["KSG", "KOK", "BUK", "KHI"], ["uighur", "kazak", "kirgiz", "uzbek", "turkmen", "tajik"], dict(supply_consumption=-0.2, land_organisation=0.08, diplomatic_points_modifier=0.25), "WRP"),
            ("Back through the Jade Gate", "Zuo Zongtang came out through the Jade Gate with coffins in his baggage train. We go back in the same way, for Lanzhou and Xian.",
             ["XBI", "NXA", "GMJ"], ["tibetan"], dict(land_organisation=0.1, org_regain=0.1, max_attrition=-1), None)],
    "JXI": [("Down to the Sea", "Jiangxi's porcelain and tea go to the world through other men's ports. Take them: Fujian and Zhejiang.",
             ["FUJ", "ZHJ"], ["min", "wu"], dict(tax_efficiency=0.08, naval_organisation=0.1, factory_throughput=0.05), None),
            ("The Nanchang Uprising", "An army was born in Nanchang once and went on to take the country. Begin with the middle Yangtze: Wuhan and Changsha.",
             ["HBE", "HNC"], ["chu", "xiang"], dict(land_organisation=0.1, mobilisation_size=0.03, core_pop_militancy_modifier=-0.01), None)],
}
ROAD_TAGS = {"LFG": ("Lanfang Republic", "Lanfang", (60, 150, 200), "min"), "NZO": ("Nanzhao", "Nanzhao", (150, 90, 160), "nanfaren"),
             "DGN": ("Dunganistan", "Dungan", (40, 140, 90), "beifaren"), "WRP": ("Protectorate of the Western Regions", "Western Regions", (210, 170, 90), "beifaren")}
