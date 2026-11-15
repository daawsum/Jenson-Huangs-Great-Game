"""One-off patch: grain, fruit and fish in China where they belong (tea and silk were everywhere)."""
c = open("content.py", encoding="utf-8").read()


def crep(a, b):
    global c
    assert c.count(a) == 1, a
    c = c.replace(a, b)


if "CN_CROPS" not in c:
    # Hami is the melon oasis; Xinjiang's coal is the Urumqi field, so Urumqi no longer turns to oil
    crep('    1599: "coal",   # Kumul (Hami)\n', '    1600: "coal",   # Dihua (the Urumqi coalfield)\n')
    crep('    (1885, 1600),   # Dihua: Dushanzi and the Dzungarian fields\n', '')
    c += r'''

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
    3347: "fish",    # Rizhao
    3320: "fish",    # Haizhou (the Haizhou bay ground)
    1541: "fish",    # Tongzhou (the Lusi ground)
    1538: "fish",    # Shanghai (the mouth of the Yangtze)
    1608: "fish",    # Ningbo (the Zhoushan ground, the largest in China)
    1611: "fish",    # Wenzhou
    3262: "fish",    # Funing (yellow croaker of Sandu bay)
    3279: "fish",    # Haifeng (Shanwei)
    1496: "fish",    # Hong Kong
    1498: "fish",    # Macao
    1495: "fish",    # Zhanjiang (the Beibu gulf ground)
    # --- the Sichuan highlands herd yak; they never grew silk
    1582: "cattle", 3358: "cattle", 3359: "cattle",
}
CN_FISH = {p for p, g in CN_CROPS.items() if g == "fish"}
assert not set(CN_CROPS) & set(CN_MINERALS), set(CN_CROPS) & set(CN_MINERALS)
'''
    open("content.py", "w", encoding="utf-8").write(c)

s = open("02_world.py", encoding="utf-8").read()
a = '''        elif goods in ("coal", "iron", "sulphur"):
            goods = CN_FALLBACK.get(o, "cattle" if o == "MGL" else "grain")
'''
assert s.count(a) == 1
s = s.replace(a, '''        elif p in CN_CROPS:
            goods = CN_CROPS[p]
        elif goods in ("coal", "iron", "sulphur"):
            goods = CN_FALLBACK.get(o, "cattle" if o == "MGL" else "grain")
''')
a = '''assert all(q in CHINA for q in CN_MINERALS), [q for q in CN_MINERALS if q not in CHINA]
'''
assert s.count(a) == 1
s = s.replace(a, a + '''assert all(q in CHINA for q in CN_CROPS), [q for q in CN_CROPS if q not in CHINA]
assert CN_FISH <= COASTAL, ("fish in a province with no coast", sorted(CN_FISH - COASTAL))
''')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched")
