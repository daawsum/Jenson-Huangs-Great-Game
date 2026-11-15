"""One-off (v4): per-clique decisions (identity, development, ambition, claim), accords between
partners, treaties with minor cliques, and formables that accept the right regional cultures."""
s = open("03_gameplay.py", encoding="utf-8").read()
if "from content import" in s:
    raise SystemExit("already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


rep("from config import *\n", "from config import *\nfrom content import *\n")

# ---- modifiers for the unique decisions (must exist before event_modifiers.txt is written)
rep('''for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
''', '''for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
for _t, (_id, _dev, _amb) in IDENTITY.items():
    mod("id_" + _t, _id[0], _id[1], **_id[2])
    mod("dev_" + _t, _dev[0], _dev[1], **_dev[3])
    mod("amb_" + _t, _amb[2], _amb[1], **_amb[3])
mod("clique_accord", "Accord Between Cliques", "Two cliques have agreed to stand together: shared customs posts, shared intelligence.",
    tax_efficiency=0.04, diplomatic_points_modifier=0.25, org_regain=0.05)
mod("protected_clique", "Under Protection", "A stronger clique guarantees our borders.", land_defense_modifier=0.1, core_pop_militancy_modifier=-0.01)
''')

# ---- formables accept the regional cultures that belong to them
a = s[s.index("# ---- Chinese formables"):s.index("# ---- the three playable outsiders")]
rep(a, r'''# ---- Chinese formables
def _acc(tag):
    return "".join("add_accepted_culture = %s\n" % c for c in FORMABLE_CULTURES[tag])


def formable(tag, name, key, cities, who, extra="", desc=None, prest=20):
    decision("form_%s" % key, "Proclaim %s" % name,
             desc or "With %s in our hands we can proclaim %s." % (", ".join(PNAME[x if isinstance(x, int) else P(x)] for x in cities), name),
             "%s\nNOT = { exists = %s }\nNOT = { tag = %s }" % (who, tag, tag),
             "war = no\n" + owns(*cities),
             "prestige = %d\n%schange_tag = %s" % (prest, extra, tag))


WL = "has_country_flag = chinese_warlord"
formable("CHI", "the Republic of China", "china", [1612, 2221, 1493, 1578, 1559, 1522, 1479], WL,
         _acc("CHI") + "add_country_modifier = { name = mandate_of_heaven duration = -1 }\nbadboy = -10\n",
         "Beijing, Nanjing, Canton, Chengdu, Xian, Wuchang and Mukden all fly our flag. The warlord era is over: proclaim one China.", 100)
formable("BYG", "the Beiyang Government", "beiyang", [1612, 1617, 1563, 1508, 1572], WL + "\nNOT = { exists = CHI }", _acc("BYG"))
formable("LGG", "Liangguang", "liangguang", [1493, 1502, 1503], WL + "\nNOT = { exists = CHI }", _acc("LGG"))
formable("SHU", "the State of Shu", "shu", [1578, 1577], WL + "\nNOT = { exists = CHI }", _acc("SHU"))
formable("WUU", "the State of Wu", "wu", [2221, 1538, 1604], WL + "\nNOT = { exists = CHI }", _acc("WUU"))
formable("CHU", "the State of Chu", "chu", [1522, 1524, 1516], WL + "\nNOT = { exists = CHI }", _acc("CHU"))
formable("DIA", "the State of Dian", "dian", [1601, 1505], WL + "\nNOT = { exists = CHI }", _acc("DIA"))
formable("NWF", "the Northwest Federation", "northwest", [1490, 1559, 1600], WL + "\nNOT = { exists = CHI }", _acc("NWF"))
formable("MZG", "Manchuria", "manchuria", [1479, 1555, 1552], WL + "\nNOT = { exists = CHI }", _acc("MZG"))

''')

# ---- the unique decisions themselves
rep('''wr("decisions/WarlordEra.txt", "political_decisions = {\\n" + "\\n".join(DEC) + "}\\n")''', r'''# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
NAMES = {t: w[0] for t, w in WARLORDS.items()}
NAMES.update({"KOR": "Korea", "DAI": "Dai Nam", "BUR": "Burma"})
for tag, (ident, dev, amb) in IDENTITY.items():
    me = "tag = %s" % tag
    rival, partner, target = RIVAL[tag], PARTNER[tag], TARGET[tag]
    once("%s_identity" % tag, ident[0], ident[1] + " Only %s can do this." % NAMES[tag], me, "war = no", "prestige = 3", "id_" + tag)
    once("%s_develop" % tag, dev[0], dev[1], me, "war = no\nmoney = %d" % dev[2], "treasury = -%d\nprestige = 5" % dev[2], "dev_" + tag)
    once("%s_ambition" % tag, amb[0], amb[1] + " Our rivalry with %s is settled." % NAMES[rival],
         me, "owns = %d" % CAPITALS[rival], "prestige = 25\nbadboy = -3", "amb_" + tag)
    once("%s_claim" % tag, "Assert Authority over %s" % NAMES[target],
         "%s lies within our natural sphere. Others think the same of it; whoever moves first holds the claim." % NAMES[target],
         me + "\nexists = %s" % target, "war = no\nprestige = 10",
         "%s = { any_owned = { add_core = THIS } }\ncasus_belli = { target = %s type = conquest months = 120 }\nrelation = { who = %s value = -100 }" % (target, target, target))
    once("%s_accord" % tag, "Sign an Accord with %s" % NAMES[partner],
         "%s and we share enemies and little else, which is enough. With good relations the accord can be signed: an alliance, and joint customs and intelligence for both." % NAMES[partner],
         me + "\nexists = %s" % partner, "war = no\nrelation = { who = %s value = 100 }\n%s = { war = no }" % (partner, partner),
         "create_alliance = %s\nrelation = { who = %s value = 50 }\n%s = { add_country_modifier = { name = clique_accord duration = -1 } }" % (partner, partner, partner),
         "clique_accord")
    once("%s_denounce" % tag, "Denounce %s" % NAMES[rival],
         "Publish the telegram: %s is a traitor to the nation. Our officers will fight them with a will, and the other cliques will take sides." % NAMES[rival],
         me + "\nexists = %s" % rival, "war = no",
         "relation = { who = %s value = -100 }\ncasus_belli = { target = %s type = humiliate months = 60 }\nprestige = 3" % (rival, rival))

# ---- minor cliques and their patrons: a peaceful road to absorption, and protection for the small
for minor, major in PATRON.items():
    once("%s_treaty_%s" % (major, minor), "Treaty of Union with %s" % NAMES[minor],
         "%s has long looked to us. If relations are excellent and it is not led by another player, it will accept union without a shot." % NAMES[minor],
         "tag = %s\nexists = %s\n%s = { ai = yes }" % (major, minor, minor),
         "war = no\nprestige = 20\nrelation = { who = %s value = 175 }\n%s = { war = no }" % (minor, minor),
         "inherit = %s\nprestige = 10\nbadboy = 2" % minor, ai=0)
    once("%s_protection" % minor, "Seek the Protection of %s" % NAMES[major],
         "We are small and our neighbours are not. %s would guarantee us, for a price in independence." % NAMES[major],
         "tag = %s\nexists = %s" % (minor, major), "war = no\nrelation = { who = %s value = 100 }" % major,
         "create_alliance = %s\nrelation = { who = %s value = 50 }" % (major, major), "protected_clique")

wr("decisions/WarlordEra.txt", "political_decisions = {\n" + "\n".join(DEC) + "}\n")''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched 03_gameplay.py")
