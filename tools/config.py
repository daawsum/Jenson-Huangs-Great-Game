"""Shared configuration for the Warlord Era mod generator."""
import os, re

V = r"D:\SteamLibrary\steamapps\common\Victoria 2"          # vanilla game
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Warlord Era")       # mod folder being generated
WORK = os.path.join(HERE, "work")                              # intermediate json
ENC = "cp1252"
WORLD_BANK = True     # IGoR-style bank country on the Falklands with gold-mining bankers
STATE_FLAGS = True    # Tiny/Small/Medium/Large/Huge State marker tags and size-split war goals
MOD_NAME = "Jenson Huang's Great Game"   # what the launcher and the lobby show
MOD_DIR = "Warlord Era"        # folder name inside <Victoria 2>/mod
USER_DIR = "WarlordEra"        # settings/cache folder under Documents (new name = fresh map cache)


def rd(*p):
    with open(os.path.join(V, *p), encoding=ENC, errors="replace") as f:
        return f.read()


def wr(rel, text):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=ENC, errors="replace", newline="\r\n") as f:
        f.write(text)


# tag: (name, adjective, capital, primary culture, accepted cultures, colour, major?, vanilla provinces)
WARLORDS = {
    # ---- 20 majors (player slots) ----
    "ZHL": ("Zhili Clique", "Zhili", 1612, "beifaren", ["nanfaren", "manchu"], (214, 178, 60), True,
            [1612, 1616, 1617, 1615, 1614, 1618]),
    "FTN": ("Fengtian Clique", "Fengtian", 1479, "beifaren", ["manchu"], (176, 190, 70), True,
            [1479, 1480, 1481]),
    "AHC": ("Anhui Clique", "Anhui", 1470, "beifaren", ["nanfaren"], (120, 150, 200), True,
            [1473, 1475, 1471, 1470, 1474, 1472, 1478, 1512, 1509, 1477]),
    "SXI": ("Shanxi Clique", "Shanxi", 1572, "beifaren", ["nanfaren"], (150, 110, 70), True,
            [1576, 1572, 1573, 1575, 1574]),
    "GMJ": ("Guominjun", "Guominjun", 1559, "beifaren", ["nanfaren"], (200, 120, 90), True,
            [2062, 1559, 1561, 1562]),
    "SDG": ("Shandong Clique", "Shandong", 1563, "beifaren", ["nanfaren"], (90, 160, 150), True,
            [1564, 1563, 1568, 1570, 1565, 1569, 1566, 1567, 1571]),
    "HNA": ("Henan Clique", "Henan", 1508, "beifaren", ["nanfaren"], (190, 160, 120), True,
            [1513, 1510, 1508, 1511, 1515, 1514]),
    "JSU": ("Jiangsu Clique", "Jiangsu", 2221, "nanfaren", ["beifaren"], (230, 120, 120), True,
            [2221, 1543, 1539, 1537, 1541, 1544]),
    "ZHJ": ("Zhejiang Clique", "Zhejiang", 1604, "nanfaren", ["beifaren", "min"], (120, 200, 170), True,
            [1611, 1607, 1610, 1608, 1609, 1604, 1605, 1606]),
    "FUJ": ("Fujian Clique", "Fujian", 1482, "min", ["nanfaren", "hakka"], (80, 140, 220), True,
            [1487, 1484, 1486, 1482, 1483]),
    "GDG": ("Guangdong Clique", "Guangdong", 1493, "yue", ["hakka", "nanfaren"], (40, 90, 190), True,
            [1493, 1501, 1494, 1497, 1500, 1496, 1498]),
    "GXI": ("Guangxi Clique", "Guangxi", 1503, "yue", ["zhuang", "nanfaren"], (100, 170, 90), True,
            [1502, 1503, 1504, 1495]),
    "HNC": ("Hunan Clique", "Hunan", 1524, "nanfaren", ["beifaren", "miao"], (220, 90, 60), True,
            [1529, 1526, 1525, 1528, 1524, 1527, 1530]),
    "HBE": ("Hubei Clique", "Hubei", 1522, "nanfaren", ["beifaren"], (170, 100, 170), True,
            [1516, 1518, 1522, 1517, 1523, 1519, 1521, 1520]),
    "JXI": ("Jiangxi Clique", "Jiangxi", 1545, "nanfaren", ["hakka", "beifaren"], (230, 170, 80), True,
            [1550, 1547, 1548, 1545, 1549, 1551, 1546]),
    "SZC": ("Sichuan Clique", "Sichuan", 1578, "nanfaren", ["beifaren", "yi"], (150, 60, 60), True,
            [1578, 1580, 1582, 1585]),
    "YNN": ("Yunnan Clique", "Yunnan", 1601, "nanfaren", ["yi", "miao"], (130, 90, 150), True,
            [1601, 1602, 1603]),
    "GZH": ("Guizhou Clique", "Guizhou", 1505, "nanfaren", ["miao", "yi"], (110, 130, 100), True,
            [1506, 1505, 1507]),
    "XBI": ("Ma Clique", "Ma", 1490, "beifaren", ["nanfaren", "mongol", "tibetan"], (60, 150, 110), True,
            [1490, 1488, 1489, 1492]),
    "XIN": ("Xinjiang Clique", "Xinjiang", 1600, "beifaren", ["uighur", "kazak"], (200, 200, 120), True,
            [1600, 1595, 1596, 1599, 2607]),
    # ---- 15 minors ----
    "JLN": ("Jilin Clique", "Jilin", 1555, "beifaren", ["manchu"], (140, 170, 110), False,
            [1555, 1554, 1082, 1083]),
    "HLJ": ("Heilongjiang Clique", "Heilongjiang", 1552, "beifaren", ["manchu", "mongol"], (100, 120, 80), False,
            [1552, 1553, 1002, 1084, 1085, 2617]),
    "RHE": ("Rehe Clique", "Rehe", 1613, "beifaren", ["mongol", "manchu"], (180, 140, 100), False,
            [1613, 1533]),
    "CHH": ("Chahar Clique", "Chahar", 1534, "beifaren", ["mongol"], (160, 150, 130), False,
            [1534]),
    "SYN": ("Suiyuan Clique", "Suiyuan", 1532, "beifaren", ["mongol"], (190, 180, 150), False,
            [1532, 1535]),
    "NXA": ("Ningxia Clique", "Ningxia", 1491, "beifaren", ["mongol"], (90, 180, 140), False,
            [1491]),
    "QHI": ("Qinghai Clique", "Qinghai", 1557, "beifaren", ["tibetan", "mongol"], (70, 120, 130), False,
            [1557, 1558, 1556]),
    "XKG": ("Xikang Clique", "Xikang", 1586, "nanfaren", ["tibetan", "yi"], (140, 100, 100), False,
            [1586, 1588]),
    "CQG": ("Chongqing Clique", "Chongqing", 1577, "nanfaren", ["beifaren"], (190, 80, 100), False,
            [1581, 1579, 1577, 1583, 1584]),
    "TIB": ("Tibet", "Tibetan", 1587, "tibetan", [], (230, 220, 160), False,
            [1591, 1592, 1589, 1587, 1590, 1593]),
    "HNI": ("Hainan Clique", "Hainan", 1499, "yue", ["nanfaren"], (60, 190, 200), False,
            [1499]),
    "TWN": ("Taiwan Clique", "Taiwan", 1485, "min", ["hakka", "nanfaren"], (70, 200, 120), False,
            [2562, 1485]),
    "SHG": ("Shanghai Clique", "Shanghai", 1538, "nanfaren", ["beifaren"], (240, 200, 200), False,
            [1538, 1540]),
    "XZC": ("Xuzhou Clique", "Xuzhou", 1542, "beifaren", ["nanfaren"], (160, 190, 220), False,
            [1542, 1536, 1476]),
    "KSG": ("Kashgar Clique", "Kashgar", 1594, "beifaren", ["uighur"], (220, 180, 100), False,
            [1594, 1598, 1597]),
}

MONGOLIA = [1465, 2608, 2679, 1468, 2678, 1466, 2207, 1467, 1469]

# provinces that are never split (frontier, tiny)
NO_SPLIT_TAGS = {"TIB", "XIN", "KSG", "QHI"}
NO_SPLIT = {1082, 1083, 1084, 1085, 2617, 1588, 1496, 1498}

# real place names for the new halves; fallback is compass direction
SPLIT_NAMES = {
    "Zhongding": ["Baoding"], "Beijing": ["Changping"], "Chengde": ["Chaoyang", "Chifeng"],
    "Shuntian": ["Langfang"], "Tianjin": ["Cangzhou"], "Jizhou": ["Hejian"], "Daming": ["Guangping"],
    "Caozhou": ["Jining"], "Jinan": ["Dongchang"], "Taian": ["Yanzhou"], "Wuding": ["Binzhou"],
    "Laizhou": ["Pingdu"], "Weihaiwei": ["Dengzhou"], "Qingdao": ["Jiaozhou"], "Qingzhou": ["Weixian"],
    "Yizhou": ["Rizhao"], "Datong": ["Shuoping"], "Taiyuan": ["Xinzhou"], "Fenzhou": ["Pingding"],
    "Pingyang": ["Puzhou"], "Luan": ["Zezhou"], "Shangzhou": ["Xingan"], "Xian": ["Fengxiang"],
    "Yenan": ["Yulin"], "Hanzhong": ["Ningqiang"], "Lanzhou": ["Liangzhou"], "Gansu": ["Jiuquan"],
    "Gongchang": ["Qinzhou"], "Ningxia": ["Lingzhou"], "Pingliang": ["Qingyang"],
    "Nanyang": ["Xichuan"], "Henan": ["Shanzhou"], "Kaifeng": ["Zhengzhou"], "Huaiqing": ["Zhangde"],
    "Weihui": ["Xinxiang"], "Runing": ["Xinyang"], "Fengyang": ["Bengbu"], "Yingzhou": ["Bozhou"],
    "Chenzhou": ["Xuchang"], "Guide": ["Shangqiu"], "Huizhou": ["Qimen"], "Ningguo": ["Guangde"],
    "Chizhou": ["Tongling"], "Anqing": ["Liuan"], "Luzhou": ["Chaohu"], "Sizhou": ["Suxian"],
    "Taiping": ["Wuhu"], "Huaian": ["Haizhou"], "Xuzhou": ["Pizhou"], "Yangzhou": ["Gaoyou"],
    "Nanjing": ["Jurong"], "Suzhou": ["Kunshan"], "Changzhou": ["Wuxi"], "Tongzhou": ["Rugao"],
    "Taicangzhou": ["Songjiang"], "Shanghai": ["Pudong"], "Zhenjiang": ["Danyang"],
    "Wenzhou": ["Chuzhou"], "Jinhua": ["Quzhou"], "Taizhou": ["Tiantai"], "Ningbo": ["Dinghai"],
    "Shaoxing": ["Shengxian"], "Hangzhou": ["Chunan"], "Huzhou": ["Anji"], "Jiaxing": ["Haining"],
    "Zhangzhou": ["Longyan"], "Quanzhou": ["Xinghua"], "Tingzhou": ["Yongan"], "Fuzhou": ["Funing"],
    "Jianning": ["Yanping"], "Tainan": ["Fengshan", "Taidong"], "Taibei": ["Xinzhu", "Yilan"],
    "Ganzhou": ["Nanan"], "Jian": ["Yuanzhou"], "Jianchang": ["Linchuan"], "Nanchang": ["Ruizhou"],
    "Jiujiang": ["Nankang"], "Raozhou": ["Jingdezhen"], "Guangxin": ["Yushan"],
    "Hanyang": ["Hankou"], "Huangzhou": ["Qizhou"], "Wuchang": ["Xianning"], "Dean": ["Suizhou"],
    "Xiangyang": ["Yunyang"], "Anlu": ["Jingmen"], "Shinan": ["Yichang"], "Jingzhou": ["Shashi"],
    "Yongshun": ["Fenghuang"], "Baoqing": ["Wugang"], "Changde": ["Lizhou"], "Yuezhou": ["Pingjiang"],
    "Changsha": ["Xiangtan", "Liuyang"], "Hengzhou": ["Chenxian"], "Yongzhou": ["Daozhou"],
    "Canton": ["Foshan", "Dongguan"], "Gauzhou": ["Leizhou"], "Hainan": ["Qiongzhou", "Sanya"],
    "Zhaoqing": ["Luoding"], "Chaozhou": ["Jiaying"], "Waizao": ["Haifeng"],
    "Shaozhou": ["Nanxiong", "Lianzhou"], "Nanning": ["Longzhou", "Baise"],
    "Guilin": ["Liuzhou", "Qingyuan"], "Pingle": ["Wuzhou", "Xunzhou"],
    "Kunming": ["Qujing", "Zhaotong"], "Dali": ["Lijiang", "Yongchang"], "Puer": ["Linan", "Kaihua"],
    "Anshun": ["Xingyi"], "Guiyang": ["Zunyi", "Dading"], "Zhenyuan": ["Liping", "Tongren"],
    "Chengdu": ["Mianzhou"], "Jiading": ["Meizhou"], "Longan": ["Songpan", "Maozhou"],
    "Yibin": ["Xuyong"], "Yazhou": ["Dajianlu"], "Kuizhou": ["Wanxian"], "Baotung": ["Guangyuan"],
    "Chongqing": ["Fuling", "Hezhou"], "Shunqing": ["Guangan"], "Tongchuan": ["Suining"],
    "Mukden": ["Liaoyang", "Tieling"], "Jinzhou": ["Xingcheng"], "Port Arthur": ["Andong"],
    "Jilin": ["Changchun", "Yanji"], "Ninguta": ["Sanxing", "Hunchun"], "Qiqihar": ["Hulan", "Mergen"],
    "Aigun": ["Xunke", "Huma"], "Manzhouli": ["Hailar", "Zhalantun"], "Jirim Chuulgan": ["Tongliao", "Taonan"],
    "Guihua Tumed": ["Baotou", "Fengzhen"], "Yeke Juu Chuulghan": ["Dongsheng", "Dingbian"],
    "Ulaan Chab Chuulghan": ["Dolonnur", "Zhangjiakou"],
}


def tag_of_vanilla_province():
    m = {}
    for tag, v in WARLORDS.items():
        for p in v[7]:
            assert p not in m, p
            m[p] = tag
    for p in MONGOLIA:
        assert p not in m
        m[p] = "MGL"
    return m


def blocks(text):
    """Yield (key, body, start, end) for top-level `key = { ... }` blocks."""
    i, n = 0, len(text)
    pat = re.compile(r"([\w\.\-]+)\s*=\s*\{")
    while True:
        m = pat.search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while j < n and depth:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif c == "#":
                while j < n and text[j] != "\n":
                    j += 1
            j += 1
        yield m.group(1), text[m.end():j - 1], m.start(), j
        i = j


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
