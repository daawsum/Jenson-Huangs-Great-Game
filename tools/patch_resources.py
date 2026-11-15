"""One-off patch: Ottoman and Persian mergers, Chinese minerals, oil, life ratings, three new buffs."""
import re

# ------------------------------------------------------------------ content.py: data
c = open("content.py", encoding="utf-8").read()
if "CN_MINERALS" not in c:
    c += r'''

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
    1599: "coal",   # Kumul (Hami)
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
    (1885, 1600),   # Dihua: Dushanzi and the Dzungarian fields
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
           "TIB": 25, "TWN": 45}
CN_LIFE_PROV = {1604: 40, 1605: 40, 1606: 40, 1609: 40, 1608: 40,             # Hangzhou bay
                1493: 40, 3276: 40, 1496: 40, 1498: 40,                        # Pearl River delta
                1578: 40, 3356: 40, 3354: 40,                                  # Chengdu plain
                1582: 30, 3358: 30, 3359: 30,                                  # the Sichuan highlands
                3339: 31, 1561: 31,                                            # northern Shaanxi
                1488: 27, 3268: 27, 3269: 27,                                  # the Hexi corridor
                1601: 35, 1602: 35}                                            # Kunming and Dali basins
'''
    open("content.py", "w", encoding="utf-8").write(c)

# ------------------------------------------------------------------ 02_world.py
p = "02_world.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep(r'''EMPTIED = {p for p in ALLP if owner[p] is None''', r'''# The Ottoman Empire holds the Balkans, the Caucasus, Anatolia, the Levant, Arabia and Egypt as one
# country; Persia holds Iraq.
OTTO_TAGS = {"GRE", "SER", "WAL", "MOL", "MON", "BOS", "BUL", "ALB", "ION", "ROM", "CRE", "CYP", "GEO", "ARM", "AZB", "CIR",
             "SYR", "LEB", "HDJ", "NEJ", "ABU", "YEM", "EGY"}
_n = [0, 0]
for p in ALLP:
    if p in CHINA or p not in vprov or not owner.get(p) or owner[p] == "HRE":
        continue
    v = vprov[p]
    if owner[p] == "IRQ" or "IRQ" in v["cores"]:
        owner[p] = "PER"
        _n[1] += 1
    elif owner[p] in OTTO_TAGS or (owner[p] == "OMA" and cont.get(p) == "asia") or (cont.get(p) == "europe" and PFOLDER.get(p) == "balkan"):
        owner[p] = "TUR"
        _n[0] += 1
print("provinces merged into the Ottoman Empire: %d | Iraq to Persia: %d" % tuple(_n))

EMPTIED = {p for p in ALLP if owner[p] is None''')
rep(r'''NO_SUCCESSORS = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK",''', r'''NO_SUCCESSORS = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK", "TUR",''')
rep(r'''    if goods:
        L.append("trade_goods = %s" % goods)
    lr = v["lr"]
''', r'''    if p in CHINA:                  # minerals only where China's deposits are (content.py)
        if p in CN_MINERALS:
            goods = CN_MINERALS[p]
        elif goods in ("coal", "iron", "sulphur"):
            goods = CN_FALLBACK.get(o, "grain")
    if goods:
        L.append("trade_goods = %s" % goods)
    lr = v["lr"]
    if p in CHINA:
        lr = CN_LIFE_PROV.get(p, CN_LIFE[o])
    elif cont.get(p) == "europe" and lr:
        lr -= 5                     # Europe is a poorer place to live in this world
''')
rep(r'''    if tag == "HRE":
        lit = (0.02, 0.01)
''', r'''    if tag == "HRE":
        lit = (0.02, 0.01)
    if tag == "PER":
        lit = (0.20, 0.20)
''')
rep(r'''owned = collections.defaultdict(list)
for p in ALLP:
    if owner[p]:
        owned[owner[p]].append(p)
''', r'''owned = collections.defaultdict(list)
for p in ALLP:
    if owner[p]:
        owned[owner[p]].append(p)
_cl = [CN_LIFE_PROV.get(p, CN_LIFE[owner[p]]) for p in ALLP if p in CHINA]
print("china: average life rating %.1f over %d provinces | minerals %s" % (sum(_cl) / len(_cl), len(_cl), dict(collections.Counter(CN_MINERALS.values()))))
assert all(q in CHINA for q in CN_MINERALS), [q for q in CN_MINERALS if q not in CHINA]
for _t in ("TWN",):
    assert {CN_MINERALS.get(q) for q in ALLP if owner[q] == _t} <= {"coal", "iron", "sulphur"}, _t
''')
open(p, "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ 03_gameplay.py
p = "03_gameplay.py"
s = open(p, encoding="utf-8").read()
rep(r'''formable("KLS", "the Khalsa Raj", "khalsa_raj", ["Lahore", "Delhi", "Kabul", "Multan", "Srinagar"], "tag = PAN",
         "add_accepted_culture = avadhi\nadd_accepted_culture = kashmiri\nadd_accepted_culture = pashtun\nany_owned = { add_core = KLS }\n",
         "From Kabul to Delhi the Khalsa rules. Proclaim the Raj.", 100)''',
    r'''formable("KLS", "the Khalsa Raj", "khalsa_raj", ["Lahore", "Delhi", "Kabul", "Multan", "Srinagar"], "tag = PAN",
         "add_accepted_culture = kashmiri\nadd_accepted_culture = pashtun\nany_owned = { add_core = KLS }\n"
         "add_country_modifier = { name = khalsa_raj_order duration = -1 }\n",
         "From Kabul to Delhi the Khalsa rules. Proclaim the Raj: its schools and its courts will make one people of the north.", 100, tech=STATE)''')
rep(r'''formable("PSE", "the Persian Empire", "persian_empire", ["Tehran", "Baghdad", "Herat", "Baku"], "tag = PER",
         "add_accepted_culture = azerbaijani\nadd_accepted_culture = kurdish\nadd_accepted_culture = pashtun\nany_owned = { add_core = PSE }\n",
         "Tehran, Baghdad, Herat and Baku are ours again. The empire of Nader Shah is restored.", 100)''',
    r'''formable("PSE", "the Persian Empire", "persian_empire", ["Baku", "Diyarbakir", "Hakkari", "Tashkent"], "tag = PER",
         "add_accepted_culture = azerbaijani\nadd_accepted_culture = kurdish\nadd_accepted_culture = pashtun\nany_owned = { add_core = PSE }\n"
         "add_country_modifier = { name = persianate_revival duration = -1 }\n",
         "Baku, Kurdistan and Tashkent are ours. The empire of Nader Shah is restored, and Persian is again the tongue of every court from the Tigris to the Syr Darya.", 100, tech=STATE)''')
rep(r'''for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
''', r'''mod("persianate_revival", "Persianate Revival", "Persian is the language of school, court and bazaar across the empire.",
    global_assimilation_rate=1.0, education_efficiency_modifier=0.15)
mod("khalsa_raj_order", "Order of the Khalsa Raj", "One law and one school system from Kabul to Delhi.",
    global_assimilation_rate=0.5, education_efficiency_modifier=0.15)
mod("taiwanese_dream", "The Taiwanese Dream", "A new land for anyone willing to cross the strait: free soil, honest officials, and mines and mills that never stop.",
    global_immigrant_attract=1.0, administrative_efficiency_modifier=0.5, RGO_throughput=0.25, factory_throughput=0.25)

for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
''')
rep(r'''for _t, (_name, _desc, _kw) in TRAITS.items():
    setup("tag = %s" % _t, "trait_" + _t, _name, _desc)
''', r'''for _t, (_name, _desc, _kw) in TRAITS.items():
    setup("tag = %s" % _t, "trait_" + _t, _name, _desc)
setup("tag = TWN", "taiwanese_dream", "The Taiwanese Dream",
      "Formosa is rich in coal, iron and sulphur and short of hands. Its government promises land and work to anyone who crosses the strait.")

# ---- oil where China's fields are: vanilla's own oil event, once per field, with our provinces
_goods = rd("events", "Goods.txt")
_m = re.search(r"province_event\s*=\s*\{\s*id\s*=\s*1109\b", _goods)
_d, _j = 1, _goods.index("{", _m.start()) + 1
while _d:
    _d += _goods[_j] == "{"
    _d -= _goods[_j] == "}"
    _j += 1
_tmpl = _goods[_m.start():_j]
_or = re.search(r"or\s*=\s*\{(\s*province_id\s*=\s*\d+[^\n]*\n)+\s*\}", _tmpl)
assert _or and "trade_goods = oil" in _tmpl
_new = ""
for _i, (_yr, _pv) in enumerate(CN_OIL):
    assert OWNER.get(_pv) in WARLORDS, _pv
    _e = _tmpl[:_or.start()] + "province_id = %d\t\t# %s" % (_pv, PNAME[_pv]) + _tmpl[_or.end():]
    _e = re.sub(r"id\s*=\s*1109\b", "id = %d" % (880401 + _i), _e, count=1)
    _e, _k = re.subn(r"year\s*=\s*\d+", "year = %d" % _yr, _e, count=1)
    assert _k == 1
    _new += _e + "\n\n"
# the gold strike at Caozhou goes: only the World Bank's bankers can work gold in this mod
_goods = re.sub(r"[ \t]*province_id\s*=\s*1564\b[^\n]*\n", "", _goods, count=1)
wr("events/Goods.txt", _goods.rstrip() + "\n\n##### Warlord Era: the oil fields of China #####\n" + _new)
print("oil events for chinese fields:", len(CN_OIL))
''')
open(p, "w", encoding="utf-8").write(s)
print("patched")
