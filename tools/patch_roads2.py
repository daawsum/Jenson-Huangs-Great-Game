"""One-off patch: great wars by technology, Japan's decisions, and hand-written roads for the 20 great cliques."""
import re

# ------------------------------------------------------------------ content.py
c = open("content.py", encoding="utf-8").read()
a = c.index("# ------------------------------------------------------------------ the two roads of each great clique")
c = c[:a] + r'''# ------------------------------------------------------------------ the two roads of each great clique
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
             ["SIBERIA", "KOR"], ["korean", "siberian"], dict(global_immigrant_attract=0.5, farm_rgo_eff=0.1, mine_rgo_eff=0.1, colonial_migration=0.25), None)],
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
             ["BRU", "PHI", "JAV"], ["malay", "javan"], dict(naval_organisation=0.15, global_immigrant_attract=0.5, colonial_migration=0.25), "LFG"),
            ("The Min-Yue Confederacy", "Before the Han came there was Minyue and Nanyue, one coast from the Min river to Hainan. Canton, Formosa and Hainan belong with us.",
             ["GDG", "TWN", "HNI"], ["yue"], dict(tax_efficiency=0.05, naval_organisation=0.1, land_organisation=0.05), None)],
    "GDG": [("The Northern Expedition", "Swear the army at Whampoa and march: Hunan, Jiangxi and Hubei first, then the Yangtze. The revolution will not stay in one province.",
             ["HNC", "JXI", "HBE"], ["xiang", "gan", "chu"], dict(land_organisation=0.1, org_regain=0.1, war_exhaustion=-0.01, cb_generation_speed_modifier=0.5), None),
            ("The Canton System Abroad", "For a century every foreign ship was made to trade at Canton alone. Now Canton's merchants will hold the foreign ports: Hanoi, Singapore and Bangkok.",
             ["DAI", "JOH", "SIA"], ["vietnamese", "malay", "thai"], dict(naval_organisation=0.1, tax_efficiency=0.1, factory_throughput=0.05), None)],
    "GXI": [("The Annam Protectorate", "The Black Flags of Guangxi fought for Annam when the court would not. Go back over the border and stay: Vietnam, Laos and Cambodia are claimed.",
             ["DAI", "LUA", "CAM"], ["vietnamese", "lao", "khmer"], dict(supply_consumption=-0.15, land_organisation=0.08, max_attrition=-1), None),
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
    "YNN": [("The Kingdom of Nanzhao", "Nanzhao ruled from Dali to the Irrawaddy and sacked Chengdu. Its heirs go south again: Burma, Laos and Siam are claimed for a kingdom of the mountains.",
             ["BUR", "LUA", "SIA"], ["burmese", "lao", "thai"], dict(max_attrition=-2, supply_consumption=-0.15, land_organisation=0.08), "NZO"),
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
             ["KSG", "KOK", "BUK", "KHI"], ["uighur"], dict(supply_consumption=-0.2, land_organisation=0.08, diplomatic_points_modifier=0.25), "WRP"),
            ("Back through the Jade Gate", "Zuo Zongtang came out through the Jade Gate with coffins in his baggage train. We go back in the same way, for Lanzhou and Xian.",
             ["XBI", "NXA", "GMJ"], ["tibetan"], dict(land_organisation=0.1, org_regain=0.1, max_attrition=-1), None)],
    "JXI": [("Down to the Sea", "Jiangxi's porcelain and tea go to the world through other men's ports. Take them: Fujian and Zhejiang.",
             ["FUJ", "ZHJ"], ["min", "wu"], dict(tax_efficiency=0.08, naval_organisation=0.1, factory_throughput=0.05), None),
            ("The Nanchang Uprising", "An army was born in Nanchang once and went on to take the country. Begin with the middle Yangtze: Wuhan and Changsha.",
             ["HBE", "HNC"], ["chu", "xiang"], dict(land_organisation=0.1, mobilisation_size=0.03, core_pop_militancy_modifier=-0.01), None)],
}
ROAD_TAGS = {"LFG": ("Lanfang Republic", "Lanfang", (60, 150, 200), "min"), "NZO": ("Nanzhao", "Nanzhao", (150, 90, 160), "nanfaren"),
             "DGN": ("Dunganistan", "Dungan", (40, 140, 90), "beifaren"), "WRP": ("Protectorate of the Western Regions", "Western Regions", (210, 170, 90), "beifaren")}
'''
open("content.py", "w", encoding="utf-8").write(c)

# ------------------------------------------------------------------ 02_world.py: the four new countries
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep(r'''    ("SUV", ("Suvarnabhumi", "Suvarnabhumi", (225, 175, 55), "thai")),
])''', r'''    ("SUV", ("Suvarnabhumi", "Suvarnabhumi", (225, 175, 55), "thai")),
] + list(ROAD_TAGS.items()))''')
open("02_world.py", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ 03_gameplay.py
s = open("03_gameplay.py", encoding="utf-8").read()
rep(r'''         "great_wars_enabled = yes\nset_global_flag = great_wars_enabled\n",''', r'''         "",''')
rep(r''' A reunited China ends the age of small wars: from this day the powers of the world fight Great Wars.", 100)''', r'''", 100)''')

a = s.index("_wcaps = sorted({w[2] for w in WARLORDS.values()})")
b = s.index("# ---- every major: identity, development, ambition against its rival, a contested claim, an accord")
s = s[:a] + r'''_japan = sorted(p for p, o in OWNER.items() if o and PFOLDER.get(p) == "japan" and CONT.get(p) == "asia" and o not in WARLORDS)
assert 30 < len(_japan) < 60 and _CAP["JAP"] in _japan, len(_japan)
once("japan_continental_victory", "The Realm United", "Every domain of the islands answers to one government at last. With the whole country's rice, silver and shipwrights behind it, Japan can learn everything the cliques know.",
     "tag = JAP\ncivilized = no", owns(*_japan),
     "years_of_research = 5\nprestige = 20", "continental_lessons")
once("japan_accept_koreans", "One Realm across the Strait", "The peninsula and the islands share scripts, sages and enemies. Declare the Koreans subjects equal before the Emperor.",
     "tag = JAP", "war = no", "add_accepted_culture = %s\nprestige = 5" % _culture("korean"))

# ---- every great clique chooses its road once it has swallowed the neighbour it claimed
_siberia = sorted(p for p in OWNER if area(p) == "DBH")
assert len(_siberia) > 30
ROAD_REPORT = collections.Counter()
for tag, opts in ROADS.items():
    target = TARGET[tag]
    own_cu = {CM.get(x, x) for x in [CLIQUE_CULTURE[tag][0]] + list(CLIQUE_CULTURE[tag][1])}
    built = []
    for i, (title, text, claims, accept, kw, newtag) in enumerate(opts):
        key = "%s_road_%s" % (tag, "ab"[i])
        provs = []
        for cl in claims:
            ps = _siberia if cl == "SIBERIA" else sorted(p for p, o in OWNER.items() if o == cl)
            assert ps, (tag, cl)
            provs += ps
        eff = "".join("%d = { add_core = THIS }\n" % p for p in provs)
        eff += "".join("add_accepted_culture = %s\n" % k for k in dict.fromkeys(_culture(k) for k in accept) if k not in own_cu)
        eff += "prestige = 10"
        if newtag:
            eff += "\nchange_tag = %s" % newtag
        mod(key, title, text, **kw)
        ROAD_REPORT["tall" if not claims else "new country" if newtag else "conquest"] += 1
        built.append((key, title, text, "war = no\nowns = %d" % _CAP[target], eff, key))
    choice("road_" + tag, STATE, built, potential="tag = %s" % tag)
print("clique roads:", dict(ROAD_REPORT))

''' + s[b:]
rep(r'''mod("road_of_conquest", "Road of Conquest", "The army has its orders and the nation its enemy.", land_organisation=0.05, org_regain=0.1, cb_generation_speed_modifier=0.25)
mod("road_of_consolidation", "Road of Consolidation", "One law and one school for everyone under our flag.", global_assimilation_rate=0.25, core_pop_militancy_modifier=-0.02, tax_efficiency=0.03)
''', "")
rep(r'''mod("continental_lessons", "Lessons of the Continental War", "Captured arsenals, dockyards and engineers.",''',
    r'''mod("continental_lessons", "The Realm United", "One government commands every shipyard and school in the islands.",''')
# great wars: the day anyone at all understands revolution and counterrevolution
rep(r'''event("The Sea Lanes Turn",''', r'''event("The Age of Great Wars", "The doctrines of revolution and counter-revolution have been set down, and with them the idea that a whole nation, not merely its army, goes to war. From this day the great powers of the world fight Great Wars.",
      "revolution_n_counterrevolution = 1\nNOT = { has_global_flag = great_wars_enabled }",
      [("Then let us be ready.", "great_wars_enabled = yes\nset_global_flag = great_wars_enabled")])
event("The Sea Lanes Turn",''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
