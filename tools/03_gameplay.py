"""Stage 3: migration rules, war goals, modifiers, events, decisions, formables, dominions."""
import os, re, json, glob, collections
from config import *
from content import *

M = json.load(open(os.path.join(WORK, "map.json")))
Wd = json.load(open(os.path.join(WORK, "world.json")))
PNAME = {int(k): v for k, v in M["pname"].items()}
PFOLDER = {int(k): v for k, v in M["pfolder"].items()}
CENT = {int(k): v for k, v in M["centroid"].items()}
OWNER = {int(k): v for k, v in Wd["owner"].items()}
CONT = {int(k): v for k, v in Wd["cont"].items()}
REGIONS = Wd["regions"]
DOM = Wd["dominions"]
VT = set(Wd["vtags"])
LOC = []


def loc(k, v):
    LOC.append("%s;%s;;;;;;;;;;;;;x" % (k, v.replace(";", ",")))


_inv = collections.defaultdict(list)
for i, n in PNAME.items():
    _inv[n.lower()].append(i)


def P(name):
    r = _inv[name.lower()]
    assert len(r) == 1, (name, r)
    return r[0]


# ------------------------------------------------------------------ migration (after Vae Victis)
MIG = ("\n\t# Warlord Era: only flagged immigrant nations receive emigrants (system adapted from Vae Victis)\n"
       "\tmodifier = {\n\t\tfactor = -10000\n\t\tNOT = { has_country_flag = new_world_nation }\n\t}\n"
       "\tmodifier = {\n\t\tfactor = -10000\n\t\thas_country_flag = old_world_colony\n\t\thas_global_flag = new_world_opened\n\t}\n")
n = 0
for f in glob.glob(os.path.join(V, "poptypes", "*.txt")):
    t = open(f, encoding=ENC, errors="replace").read()
    mm = re.search(r"country_migration_target\s*=\s*\{\s*factor\s*=\s*[\d\.]+", t)
    if mm:
        t = t[:mm.end()] + MIG + t[mm.end():]
        n += 1
    wr("poptypes/" + os.path.basename(f), t)
print("pop types patched:", n)

# ------------------------------------------------------------------ war goals between warlords
cb = rd("common", "cb_types.txt")
cb = cb.replace("acquire_core_state \nannex_core_country", "acquire_core_state \nannex_core_country\nwarlord_take_state\nwarlord_annex", 1)
assert "warlord_take_state" in cb
COMMON = """	is_triggered_only = yes
	months = 12
	badboy_factor = %s
	prestige_factor = 3
	peace_cost_factor = 0.8
	penalty_factor = 1
	always = yes
	break_truce_prestige_factor = 5
	break_truce_infamy_factor = 2
	break_truce_militancy_factor = 2
	truce_months = 0
	good_relation_prestige_factor = 1
	good_relation_infamy_factor = 1
	good_relation_militancy_factor = 1
"""
cb += """
# ---------------------------------------------------------------- Warlord Era
# Any Chinese warlord may always press a claim on another warlord.
warlord_take_state = {
	sprite_index = 5
""" + COMMON % "0.4" + """	can_use = {
		has_country_flag = chinese_warlord
		THIS = { has_country_flag = chinese_warlord }
		NOT = { is_our_vassal = THIS }
		number_of_states = 3
	}
	allowed_states = {
		not = { any_owned_province = { is_capital = yes } }
	}
	po_demand_state = yes
	war_name = WAR_TAKE_NAME
}

warlord_annex = {
	sprite_index = 5
	crisis = no
""" + COMMON % "0.6" + """	can_use = {
		has_country_flag = chinese_warlord
		THIS = { has_country_flag = chinese_warlord }
		NOT = { is_our_vassal = THIS }
		NOT = { number_of_states = 3 }
	}
	po_annex = yes
	war_name = WAR_RESTORE_ORDER_NAME
}
"""
wr("common/cb_types.txt", cb)
loc("warlord_take_state", "Warlord Claim")
loc("warlord_take_state_desc", "Seize a state from a rival warlord.")
loc("warlord_take_state_setup", "Take $STATE$ from $RECIPIENT$")
loc("warlord_take_state_short", "Warlord Claim")
loc("warlord_annex", "Absorb Clique")
loc("warlord_annex_desc", "Absorb a rival clique that holds two states or fewer.")
loc("warlord_annex_setup", "Absorb $RECIPIENT$")
loc("warlord_annex_short", "Absorb Clique")

# ------------------------------------------------------------------ modifiers
MODS = collections.OrderedDict()


def mod(key, name, desc, icon=5, **kw):
    MODS[key] = (kw, icon)
    loc(key, name)
    loc("desc_" + key, desc)


mod("khalsa_army", "The Khalsa Army", "The Fauj-i-Khas, drilled by veterans of Napoleon, is the finest army in Asia. It is a small professional force, not a levy.",
    land_organisation=0.6, org_regain=0.5, land_attack_modifier=0.25, land_defense_modifier=0.25,
    land_unit_start_experience=50, mobilisation_size=-0.02, supply_consumption=-0.2, leadership=2)
mod("mongol_horde", "The Great Horde", "Every man a rider, every rider a soldier.",
    land_organisation=0.5, org_regain=0.75, land_unit_start_experience=50, mobilisation_size=0.15, supply_consumption=-0.5,
    leadership=2, max_attrition=-2, research_points_modifier=0.25, mobilisation_economy_impact=-0.5)
mod("qajar_nizam", "Nizam-e Jadid", "The Shah's new model army and reformed treasury.",
    land_organisation=0.2, org_regain=0.2, research_points_modifier=0.3, tax_efficiency=0.1, leadership=1, mobilisation_size=0.02)
mod("inland_heartland", "Inland Heartland", "Without a coast to defend, the clique's arsenals and granaries feed the army alone.",
    land_organisation=0.1, factory_throughput=0.1, farm_rgo_eff=0.1, supply_consumption=-0.1)
mod("whampoa_academy", "Whampoa Military Academy", "A modern officer school at Canton.", leadership=1, land_unit_start_experience=15, land_organisation=0.05)
mod("hanyang_arsenal", "Hanyang Arsenal", "The great arsenal on the Yangtze supplies rifles to the whole army.", supply_consumption=-0.1, land_organisation=0.05, factory_throughput=0.05)
mod("beiyang_fleet", "Beiyang Fleet", "A modern northern squadron based at Weihaiwei.", naval_organisation=0.15, prestige=0.01)
mod("jiangnan_shipyard", "Jiangnan Shipyard", "Shanghai's yards build and repair a steam navy.", naval_organisation=0.1, factory_throughput=0.05)
mod("salt_gabelle", "Reformed Salt Gabelle", "The salt monopoly finally pays the treasury rather than its collectors.", tax_efficiency=0.05)
mod("likin_tax", "Likin Barriers", "Transit dues on every road and river.", tax_efficiency=0.08, factory_throughput=-0.05)
mod("opium_monopoly", "Opium Monopoly", "Lucrative and corrosive.", tax_efficiency=0.1, global_pop_militancy_modifier=0.02, research_points_modifier=-0.05)
mod("foreign_advisors", "Foreign-Trained Advisors", "Students return from abroad with new sciences.", research_points_modifier=0.15)
mod("bandit_levies", "Bandit Levies", "Every bandit chief becomes a colonel.", mobilisation_size=0.04, global_pop_militancy_modifier=0.01)
mod("peking_university", "Peking University", "The centre of the new learning.", research_points_modifier=0.1, global_pop_consciousness_modifier=0.01)
mod("longhai_railway", "Longhai Railway", "The east-west trunk line ties the plains together.", factory_throughput=0.05, farm_rgo_eff=0.05, mine_rgo_eff=0.05)
mod("mandate_of_heaven", "Mandate of Heaven", "All under heaven acknowledges one government.", prestige=0.02, core_pop_militancy_modifier=-0.02, tax_efficiency=0.05)
mod("northern_expedition", "Northern Expedition", "The army marches north to end the warlord era.", land_organisation=0.1, org_regain=0.1, cb_generation_speed_modifier=0.5, war_exhaustion=-0.01)
mod("treasure_fleet", "Treasure Fleet Revival", "In the wake of Zheng He.", naval_organisation=0.1, prestige=0.01)
mod("overseas_remittances", "Overseas Remittances", "Silver flows home from the dominions.", tax_efficiency=0.05, factory_throughput=0.03)
mod("modern_conscription", "Modern Conscription", "A register of every able man.", mobilisation_size=0.02, mobilisation_economy_impact=-0.25)
mod("federal_self_rule", "Provincial Self-Rule", "A provincial constitution calms the gentry.", core_pop_militancy_modifier=-0.02, global_pop_consciousness_modifier=0.01)
mod("new_life_movement", "New Life Movement", "Discipline, hygiene and loyalty.", global_pop_militancy_modifier=-0.01, research_points_modifier=0.05)
mod("village_militia", "Village Militia", "Red Spears and self-defence corps guard the countryside.", mobilisation_size=0.02, core_pop_militancy_modifier=-0.01)
mod("mint_reform", "Silver Dollar Mint", "One sound coin instead of a hundred debased ones.", tax_efficiency=0.03, loan_interest=-0.25)
mod("fauj_i_khas", "Fauj-i-Khas Expansion", "More brigades on the French model.", land_organisation=0.1, mobilisation_size=0.02, leadership=1)
mod("european_generals", "European Generals", "Allard, Ventura, Avitabile and Court command the Khalsa.", leadership=2, land_unit_start_experience=20)
mod("dar_ul_funun", "Dar ul-Funun", "Persia's first modern polytechnic.", research_points_modifier=0.2)
mod("kurultai", "Great Kurultai", "The banners have sworn to one Khan.", core_pop_militancy_modifier=-0.03, prestige=0.02, leadership=1)
mod("revived_tumens", "Revived Tumens", "The old decimal levies ride again.", mobilisation_size=0.1, land_unit_start_experience=20)
mod("chinese_advisors", "Chinese Advisors", "Engineers and drillmasters hired from the warlords.", research_points_modifier=0.2, self_unciv_military_modifier=-0.1, self_unciv_economic_modifier=-0.1)
mod("sonno_joi", "Sonno Joi", "Revere the Emperor, expel the barbarians.", land_organisation=0.1, research_points_modifier=0.15, core_pop_militancy_modifier=-0.01)
mod("nanyang_haven", "Nanyang Haven", "Junks full of settlers arrive with every monsoon.", global_immigrant_attract=0.5)
mod("dominion_charter", "Colonial Charter", "A new Chinese country overseas.", global_immigrant_attract=1.0, global_population_growth=0.0005, research_points_modifier=0.1)

mod("opium_suppression", "Opium Suppressed", "The dens are closed and the chests burned.", research_points_modifier=0.05, global_pop_militancy_modifier=-0.01, tax_efficiency=-0.03)
mod("pacified_countryside", "Pacified Countryside", "No band dares the roads.", core_pop_militancy_modifier=-0.02, farm_rgo_eff=0.05, mine_rgo_eff=0.05)
mod("model_army", "Model Army", "Few, drilled and paid on time.", land_organisation=0.1, land_unit_start_experience=20, org_regain=0.1, mobilisation_size=-0.01)
mod("state_capitalism", "Government-Supervised Industry", "Arsenals and mills founded by the state.", factory_throughput=0.1, tax_efficiency=-0.02)
mod("merchant_enterprise", "Merchant Enterprise", "The guilds and native banks finance what they please.", tax_efficiency=0.05, loan_interest=-0.2)
mod("agrarian_order", "Agriculture is the Root", "Dykes mended, granaries full.", farm_rgo_eff=0.1, core_pop_militancy_modifier=-0.01)
mod("national_academy", "National Academy", "Western learning taught at home.", research_points_modifier=0.08)
mod("maritime_policy", "Maritime Policy", "Ships, ports and dominions.", naval_organisation=0.15, global_immigrant_attract=0.1, land_organisation=-0.03)
mod("continental_policy", "Continental Policy", "Armies will reunify the country.", land_organisation=0.08, cb_generation_speed_modifier=0.25, naval_organisation=-0.1)
mod("provisional_republic", "Provisional Republic", "The lawful republican government of all China.", prestige=0.02, research_points_modifier=0.05, global_pop_consciousness_modifier=0.01)
mod("land_to_tiller", "Land to the Tiller", "The fields belong to those who work them.", farm_rgo_eff=0.1, core_pop_militancy_modifier=-0.02, tax_efficiency=-0.03)
mod("landlord_compact", "Compact with the Gentry", "The landlords collect and command.", tax_efficiency=0.05, mobilisation_size=0.01, global_pop_militancy_modifier=0.01)
mod("party_state", "Party-State", "One party organises the whole people.", mobilisation_size=0.03, core_pop_militancy_modifier=-0.02, research_points_modifier=-0.05)
mod("constitutional_parliament", "National Assembly", "A constitution that binds the generals.", research_points_modifier=0.08, global_pop_militancy_modifier=-0.02, mobilisation_size=-0.01)
mod("clique_truce", "Truce with a Rival", "The old feud is set aside.", diplomatic_points_modifier=0.25, war_exhaustion=-0.01)

for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
for _t, (_id, _dev, _amb) in IDENTITY.items():
    mod("id_" + _t, _id[0], _id[1], **_id[2])
    mod("dev_" + _t, _dev[0], _dev[1], **_dev[3])
    mod("amb_" + _t, _amb[2], _amb[1], **_amb[3])
mod("clique_accord", "Accord Between Cliques", "Two cliques have agreed to stand together: shared customs posts, shared intelligence.",
    tax_efficiency=0.04, diplomatic_points_modifier=0.25, org_regain=0.05)
mod("protected_clique", "Under Protection", "A stronger clique guarantees our borders.", land_defense_modifier=0.1, core_pop_militancy_modifier=-0.01)

em = rd("common", "event_modifiers.txt") + "\n\n##### WARLORD ERA #####\n"
for k, (kw, icon) in MODS.items():
    em += "%s = {\n%s\ticon = %d\n}\n\n" % (k, "".join("\t%s = %s\n" % (a, b) for a, b in kw.items()), icon)
wr("common/event_modifiers.txt", em)

# ------------------------------------------------------------------ dominion areas
vowner = {}
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    mm = re.match(r"\s*(\d+)", os.path.basename(f))
    if mm:
        t = re.sub(r"#.*", "", open(f, encoding=ENC, errors="replace").read())
        o = re.search(r"\bowner\s*=\s*(\w+)", t)
        vowner[int(mm.group(1))] = o.group(1) if o else None
NORTH_AFR = {"EGY", "MOR", "TUN", "TRI", "ALD", "TUR", "FRA"}
STEPPE_KEEP = {"KOK", "BUK", "KHI", "PER", "AFG", "TUR", "PAN", "KAL", "MAK", "JAP", "KOR"}


def area(p):
    if OWNER.get(p) in WARLORDS:          # a clique's own homeland is never colonial land (Taiwan is on the Nanyang continent)
        return None
    c = CONT.get(p)
    x, y = CENT.get(p, (0, 0))
    lon = (x - 2808) / 15.6
    fo = PFOLDER.get(p, "")
    vo = vowner.get(p)
    if c == "north_america":
        if fo == "carribean":
            return "DJL"
        if fo == "canada":
            return "DBZ"
        if fo == "usa":
            return "DFS" if lon < -100 else "DJS"
        return "DMX"
    if c == "south_america":
        if vo == "BRZ":
            return "DBX"
        if vo in ("ARG", "URU", "PRG", "CHL"):
            return "DYH"
        if vo is None:
            return "DYH" if y < 420 else "DBX" if lon > -62 else "DAD"
        return "DAD"
    if c == "oceania":
        return "DNZ" if fo == "australia" else "DXL"
    if c == "africa":
        if vo in NORTH_AFR and y > 1030:
            return None
        if y > 1150:
            return None
        if y < 620:
            return "DNF"
        if x > 3245:
            return "DDF"
        if x < 2960 and y >= 760:
            return "DXF"
        return "DZF"
    if c == "southeast_asia":
        return "DNY"
    if c == "asia" and OWNER.get(p) is None and vo in ("RUS", None):
        return "DXY" if (y < 1730 and x < 4134) else "DBH"
    return None


dom_regions = collections.defaultdict(list)
for r, ps in REGIONS.items():
    votes = collections.Counter(area(p) for p in ps)
    best, cnt = votes.most_common(1)[0]
    if best and cnt * 2 > len(ps):
        dom_regions[best].append(r)
for d in DOM:
    print("  dominion %s %-9s regions %3d" % (d, DOM[d][0], len(dom_regions[d])))
    assert dom_regions[d], d

DOM_DESC = {
    "DFS": "the western shore of the northern continent, the fabled land beyond the eastern sea",
    "DJS": "the eastern half of the northern continent",
    "DBZ": "the cold northern reaches of the northern continent",
    "DMX": "the highlands and isthmus south of Fusang",
    "DJL": "the islands of the western sea",
    "DAD": "the mountain spine of the southern continent",
    "DBX": "the great river forests of the southern continent",
    "DYH": "the silver river and southern plains",
    "DNZ": "the southern island continent",
    "DXL": "the far islands of the great ocean",
    "DXF": "the western coast of Africa",
    "DZF": "the forests of central Africa",
    "DDF": "the eastern coast of Africa, where the treasure fleets once called",
    "DNF": "the southern cape of Africa",
    "DBH": "the forests north of the Amur and Lake Baikal",
    "DXY": "the western steppe beyond the Jade Gate",
    "DNY": "the southern seas",
}

# ------------------------------------------------------------------ decisions
DEC = []


def block(d, ind=2):
    return "\n".join("\t" * ind + l for l in d.strip("\n").split("\n"))


CM = Wd.get("cmap", {})


def _map_cultures(effect):
    seen, out = set(), []
    for l in effect.split("\n"):
        m = re.match(r"(\s*)add_accepted_culture\s*=\s*(\w+)", l)
        if m:
            cu = CM.get(m.group(2), m.group(2))
            if cu in seen:
                continue
            seen.add(cu)
            l = "%sadd_accepted_culture = %s" % (m.group(1), cu)
        out.append(l)
    return "\n".join(out)


# Every decision of a country that can research needs a technology, mostly from the political thought
# line (RobloxDoD's tree): 1836 enlightenment / ideological thought, 1840 state and government,
# 1850 nationalism and imperialism, 1870 revolution and counterrevolution, 1900 mass politics.
# Uncivilized countries cannot research, so their decisions carry no requirement.
ENL, IDEO, STATE, NATIO, REVO, MASS = ("enlightenment_thought", "ideological_thought", "state_n_government",
                                       "nationalism_n_imperialism", "revolution_n_counterrevolution", "mass_politics")
TECH_OF = {
    "found_whampoa": "army_professionalism", "expand_hanyang_arsenal": "interchangeable_parts", "raise_beiyang_fleet": "iron_steamers",
    "build_jiangnan_shipyard": "steamers", "found_peking_university": "idealism", "build_longhai_railway": "early_railroad",
    "launch_northern_expedition": NATIO, "revive_treasure_fleet": "steamers", "collect_remittances": STATE,
    "start_new_life_movement": REVO, "open_silver_mint": "private_bank_money_bill_printing", "pacify_tibet": NATIO,
    "reclaim_outer_mongolia": NATIO, "claim_korea": NATIO, "claim_annam": NATIO, "form_china": NATIO,
}
TECH_SUFFIX = [("_identity", ENL), ("_develop", IDEO), ("_ambition", NATIO), ("_claim", STATE), ("_accord", IDEO),
               ("_denounce", ENL), ("_detente", IDEO), ("_protection", ENL)]
NO_TECH = {"open_nanyang_ports"}
_TECHS = set()
for _f in glob.glob(os.path.join(OUT, "technologies", "*.txt")):
    _TECHS |= {k for k, b, s_, e_ in blocks(re.sub(r"#.*", "", open(_f, encoding=ENC, errors="replace").read()))}
assert _TECHS, "run 03a_tech.py first"
GATES = collections.Counter()


def tech_for(key, potential):
    if key in TECH_OF:
        return TECH_OF[key]
    if key in NO_TECH or re.search(r"civilized = no|tag = (PAN|KLS|PER|PSE|MGL|KHG|JAP)\b", potential):
        return None
    if key.startswith(("charter_", "settle_")):
        return STATE
    if "_treaty_" in key:
        return NATIO
    for suf, t in TECH_SUFFIX:
        if key.endswith(suf):
            return t
    return STATE if key.startswith("form_") else IDEO


def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):
    effect = _map_cultures(effect)
    if tech is None:
        tech = tech_for(key, potential)
    if tech:
        assert tech in _TECHS, (key, tech)
        allow = "%s = 1\n%s" % (tech, allow)
    GATES[tech or "(none: cannot research)"] += 1
    DEC.append("\t%s = {\n\t\tpotential = {\n%s\n\t\t}\n\t\tallow = {\n%s\n\t\t}\n\t\teffect = {\n%s\n\t\t}\n\t\tai_will_do = {\n\t\t\tfactor = %s\n\t\t}\n\t}\n"
               % (key, block(potential, 3), block(allow, 3), block(effect, 3), ai))
    loc(key + "_title", title)
    loc(key + "_desc", desc)


def owns(*names):
    return "\n".join("owns = %d" % (x if isinstance(x, int) else P(x)) for x in names)


def regs(tag):
    return "OR = {\n" + "\n".join("\tregion = %s" % r for r in dom_regions[tag]) + "\n}"


# ---- dominions (colonial puppets)
for tag, d in DOM.items():
    name = d[0]
    opened = "" if tag == "DNY" else "set_global_flag = new_world_opened\n"
    decision("charter_%s" % tag, "Charter the Dominion of %s" % name,
             "Our settlers hold land in %s. Grant them a charter: every province we own there becomes the Dominion of %s, a puppet state that draws migrants from across the world." % (DOM_DESC[tag], name),
             "has_country_flag = chinese_warlord\nis_vassal = no\nNOT = { exists = %s }\nNOT = { has_country_flag = chartered_%s }\ncapital_scope = {\n\tNOT = {\n%s\n\t}\n}\nany_owned_province = {\n%s\n}" % (tag, tag, block(regs(tag), 2), block(regs(tag), 1)),
             "war = no\nany_owned_province = {\n%s\n}" % block(regs(tag), 1),
             "any_owned = {\n\tlimit = {\n%s\n\t}\n\tadd_core = %s\n}\nrelease_vassal = %s\n%s = {\n\tcivilized = yes\n\tset_country_flag = new_world_nation\n\tset_country_flag = chinese_dominion\n\tadd_country_modifier = { name = dominion_charter duration = -1 }\n}\n%sprestige = 10" % (block(regs(tag), 2), tag, tag, tag, opened))
    decision("settle_%s" % tag, "Hand New Lands to %s" % name,
             "We have taken more land in %s. Transfer it to our dominion of %s." % (DOM_DESC[tag], name),
             "has_country_flag = chinese_warlord\n%s = { vassal_of = THIS }\nany_owned_province = {\n%s\n}" % (tag, block(regs(tag), 1)),
             "war = no",
             "any_owned = {\n\tlimit = {\n%s\n\t}\n\tadd_core = %s\n\tsecede_province = %s\n}\nprestige = 2" % (block(regs(tag), 2), tag, tag), ai=0)

# ---- Chinese formables
def _acc(tag):
    return "".join("add_accepted_culture = %s\n" % c for c in FORMABLE_CULTURES[tag])


def formable(tag, name, key, cities, who, extra="", desc=None, prest=20, tech=None):
    decision("form_%s" % key, "Proclaim %s" % name,
             desc or "With %s in our hands we can proclaim %s." % (", ".join(PNAME[x if isinstance(x, int) else P(x)] for x in cities), name),
             "%s\nNOT = { exists = %s }\nNOT = { tag = %s }" % (who, tag, tag),
             "war = no\n" + owns(*cities),
             "prestige = %d\n%schange_tag = %s" % (prest, extra, tag), tech=tech)


WL = "has_country_flag = chinese_warlord"
formable("CHI", "the Republic of China", "china", [1612, 2221, 1493, 1578, 1559, 1522, 1479],
         "OR = {\n" + "\n".join("\ttag = %s" % t for t in FORMERS["CHI"]) + "\n}",
         _acc("CHI") + "add_country_modifier = { name = mandate_of_heaven duration = -1 }\nbadboy = -10\n",
         "Beijing, Nanjing, Canton, Chengdu, Xian, Wuchang and Mukden all fly our flag. The warlord era is over: proclaim one China. Only the six great cliques and the eight regional states may do so.", 100)
_FN = {"BYG": ("the Beiyang Government", "beiyang", [1612, 1617, 1563, 1508, 1572]), "LGG": ("Liangguang", "liangguang", [1493, 1502, 1503]),
       "SHU": ("the State of Shu", "shu", [1578, 1577]), "WUU": ("the State of Wu", "wu", [2221, 1538, 1604]),
       "CHU": ("the State of Chu", "chu", [1522, 1524, 1516]), "DIA": ("the State of Dian", "dian", [1601, 1505]),
       "NWF": ("the Northwest Federation", "northwest", [1490, 1559, 1600]), "MZG": ("Manchuria", "manchuria", [1479, 1555, 1552])}


def _who(tags):
    return "OR = {\n" + "\n".join("\ttag = %s" % t for t in tags) + "\n}"


for _t, (_nm, _key, _cities) in _FN.items():
    formable(_t, _nm, _key, _cities, _who(FORMERS[_t]) + "\nNOT = { exists = CHI }", _acc(_t),
             "With %s in our hands we can proclaim %s. Only %s may do so." % (", ".join(PNAME[x] for x in _cities), _nm, ", ".join(WARLORDS[x][0] for x in FORMERS[_t])))

# ---- the three playable outsiders
formable("KHG", "the Mongol Empire", "mongol_empire", [1465, 1612, 1600, 1479], "tag = MGL",
         "add_accepted_culture = beifaren\nadd_accepted_culture = manchu\nadd_accepted_culture = uighur\nany_owned = { add_core = KHG }\n",
         "Urga, Beijing, Urumqi and Mukden bow to the Khan. Restore the empire of Chinggis.", 100)
formable("KLS", "the Khalsa Raj", "khalsa_raj", ["Lahore", "Delhi", "Kabul", "Multan", "Srinagar"], "tag = PAN",
         "add_accepted_culture = avadhi\nadd_accepted_culture = kashmiri\nadd_accepted_culture = pashtun\nany_owned = { add_core = KLS }\n",
         "From Kabul to Delhi the Khalsa rules. Proclaim the Raj.", 100)
formable("PSE", "the Persian Empire", "persian_empire", ["Tehran", "Baghdad", "Herat", "Baku"], "tag = PER",
         "add_accepted_culture = azerbaijani\nadd_accepted_culture = kurdish\nadd_accepted_culture = pashtun\nany_owned = { add_core = PSE }\n",
         "Tehran, Baghdad, Herat and Baku are ours again. The empire of Nader Shah is restored.", 100)

# ---- formables that reuse vanilla tags
def vformable(tag, name, key, cities, tags, extra=""):
    if tag not in VT:
        print("  skipped formable, no tag", tag)
        return
    tags = [t for t in tags if t in VT]
    formable(tag, name, key, cities, "OR = {\n" + "\n".join("\ttag = %s" % t for t in tags) + "\n}", extra, tech=False)


vformable("HND", "India", "india", ["Delhi", "Calcutta", "Bombay", "Madras"],
          ["HYD", "MYS", "MUG", "AWA", "ORI", "NAG", "BER", "BUN", "GWA", "IND", "BHO", "TRA", "JAI", "JOD", "MEW", "SIK", "SHI", "NEP"], "any_owned = { add_core = HND }\n")
vformable("PLC", "the Commonwealth", "commonwealth", ["Warsaw", "Vilnius", "Krakow"], ["POL", "LIT", "KRA"], "any_owned = { add_core = PLC }\n")
vformable("UBD", "the United Baltic Duchy", "baltic", ["Riga", "Reval"], ["EST", "LAT"], "any_owned = { add_core = UBD }\n")
vformable("CZH", "Czechoslovakia", "czechoslovakia", ["Prague", "Bratislava"], ["BOH", "SLV"], "any_owned = { add_core = CZH }\n")
vformable("INO", "Nusantara", "nusantara", ["Batavia", "Banda Aceh", "Brunei"], ["JAV", "ATJ", "BAL", "BRU", "JOH"], "any_owned = { add_core = INO }\n")

# ---- warlord flavour
def once(key, title, desc, potential, allow, effect, modname=None, dur=-1, ai=1):
    eff = effect
    if modname:
        eff = "add_country_modifier = { name = %s duration = %d }\n" % (modname, dur) + eff
    decision(key, title, desc, potential + "\nNOT = { has_country_flag = did_%s }" % key, allow, "set_country_flag = did_%s\n" % key + eff, ai)


once("found_whampoa", "Found the Whampoa Academy", "Open a modern officer school on Whampoa island below Canton.", WL + "\n" + owns(1493), "money = 30000", "treasury = -30000\nprestige = 5", "whampoa_academy")
once("expand_hanyang_arsenal", "Expand the Hanyang Arsenal", "Buy German machinery for the arsenal at Hanyang.", WL + "\n" + owns(1516), "money = 40000", "treasury = -40000", "hanyang_arsenal")
once("raise_beiyang_fleet", "Raise the Beiyang Fleet", "Base a modern squadron at Weihaiwei to guard the Gulf of Zhili.", WL + "\n" + owns(1617, 1569), "money = 50000", "treasury = -50000\nprestige = 5", "beiyang_fleet")
once("build_jiangnan_shipyard", "Build the Jiangnan Shipyard", "Lay down slips and a dry dock at Shanghai.", WL + "\n" + owns(1538), "money = 40000", "treasury = -40000", "jiangnan_shipyard")
once("found_peking_university", "Found Peking University", "Gather the country's scholars in the old capital.", WL + "\n" + owns(1612), "money = 30000\nwar = no", "treasury = -30000\nprestige = 10", "peking_university")
once("build_longhai_railway", "Build the Longhai Railway", "Drive a trunk line from Xuzhou through Kaifeng to Xian.", WL + "\n" + owns(1542, 1508, 1559), "money = 80000\nwar = no", "treasury = -80000\nprestige = 10", "longhai_railway")
once("launch_northern_expedition", "Launch the Northern Expedition", "Swear the army to march north and reunify the country.", WL + "\nOR = {\n\t" + "\n\t".join("tag = %s" % t for t in ["GDG", "GXI", "HNC", "YNN", "GZH", "FUJ", "JXI", "LGG", "DIA"]) + "\n}", "war = no\nprestige = 30", "prestige = 10\nany_pop = { militancy = -1 }", "northern_expedition", 3650)
once("revive_treasure_fleet", "Revive the Treasure Fleet", "Send a great squadron into the southern and western oceans, as the Ming once did.", WL + "\nOR = {\n\t" + "\n\t".join("owns = %d" % p for p in [1493, 1482, 1538, 1617, 1604, 2221]) + "\n}", "money = 60000\nwar = no", "treasury = -60000\nprestige = 15", "treasure_fleet")
once("collect_remittances", "Organise Overseas Remittances", "Charter banks to carry our dominions' silver home.", "civilized = yes\nnum_of_vassals = 1\nhas_global_flag = new_world_opened", "war = no", "prestige = 5", "overseas_remittances")
once("start_new_life_movement", "Start a New Life Movement", "A campaign for discipline and public morals.", WL, "war = no\nmoney = 15000", "treasury = -15000", "new_life_movement", 7300)
once("open_silver_mint", "Open a Silver Dollar Mint", "Strike one trusted coin for the whole clique.", WL, "money = 20000", "treasury = -20000", "mint_reform")
once("pacify_tibet", "Assert Suzerainty over Tibet", "Claim the roof of the world for the nation.", WL + "\nexists = TIB\nOR = { owns = 1578 owns = 1586 owns = 1557 }", "war = no\nprestige = 20", "TIB = { any_owned = { add_core = THIS } }\ncasus_belli = { target = TIB type = conquest months = 60 }")
once("reclaim_outer_mongolia", "Reclaim Outer Mongolia", "The steppe was ours under the Qing and will be again.", WL + "\nexists = MGL\nOR = { owns = 1612 owns = 1532 owns = 1534 }", "war = no\nprestige = 20", "MGL = { any_owned = { add_core = THIS } }\ncasus_belli = { target = MGL type = conquest months = 60 }")
once("claim_korea", "Claim the Korean Tributary", "Korea paid tribute to Beijing; it shall pay it to us.", WL + "\nexists = KOR\nowns = 1479", "war = no\nprestige = 20", "casus_belli = { target = KOR type = make_puppet months = 60 }")
once("claim_annam", "Claim the Annamese Tributary", "The southern kingdom once sent tribute north.", WL + "\nexists = DAI\nOR = { owns = 1502 owns = 1601 }", "war = no\nprestige = 20", "casus_belli = { target = DAI type = make_puppet months = 60 }")

# ---- Sikh Empire
SK = "OR = { tag = PAN tag = KLS }"
once("expand_fauj_i_khas", "Expand the Fauj-i-Khas", "Raise new brigades on the French model.", SK, "money = 20000", "treasury = -20000", "fauj_i_khas")
once("hire_european_generals", "Hire European Generals", "Veterans of Napoleon seek employment at Lahore.", SK, "money = 15000", "treasury = -15000", "european_generals")
once("seize_the_khyber", "Seize the Khyber", "The road to Kabul lies through Peshawar. Claim everything beyond it.", SK + "\nexists = AFG\n" + owns("Peshawar"), "war = no", "AFG = { any_owned = { add_core = THIS } }\ncasus_belli = { target = AFG type = conquest months = 60 }\nprestige = 5")
once("claim_hindustan", "Claim Hindustan", "The Khalsa shall rule from the Indus to the Ganges.", SK + "\nexists = MUG", "war = no\nprestige = 10", "MUG = { any_owned = { add_core = THIS } }\ncasus_belli = { target = MUG type = conquest months = 60 }")
once("conquer_sindh", "March on Sindh", "The Amirs of Sindh block our road to the sea.", SK + "\nexists = SIN", "war = no", "SIN = { any_owned = { add_core = THIS } }\ncasus_belli = { target = SIN type = conquest months = 60 }")
once("dogra_expedition", "The Dogra Expedition", "Send Zorawar Singh over the passes into Ladakh and Tibet.", SK + "\nexists = TIB\n" + owns("Srinagar"), "war = no", "casus_belli = { target = TIB type = conquest months = 60 }\nprestige = 5")

# ---- Persia
PS = "OR = { tag = PER tag = PSE }"
once("proclaim_nizam_e_jadid", "Expand the Nizam-e Jadid", "Enlarge the new model army.", PS, "money = 15000", "treasury = -15000\nprestige = 5")
once("found_dar_ul_funun", "Found the Dar ul-Funun", "A polytechnic in Tehran to train officers, doctors and engineers.", PS, "money = 20000\nwar = no", "treasury = -20000", "dar_ul_funun")
once("reclaim_herat", "Reclaim Herat", "Herat is the key to Khorasan and was always Persian.", PS + "\nexists = AFG", "war = no", "%d = { add_core = THIS }\nAFG = { any_owned = { add_core = THIS } }\ncasus_belli = { target = AFG type = conquest months = 60 }" % P("Herat"))
once("claim_mesopotamia", "Claim Mesopotamia", "The shrine cities of Najaf and Karbala belong under the Shah's protection.", PS + "\nexists = IRQ", "war = no", "IRQ = { any_owned = { add_core = THIS } }\ncasus_belli = { target = IRQ type = conquest months = 60 }")
once("claim_the_caucasus", "Reclaim the Caucasus", "Undo the treaties of Gulistan and Turkmenchay.", PS, "war = no\nprestige = 10",
     "\n".join("%s = { any_owned = { add_core = THIS } }" % t for t in ["AZB", "ARM", "GEO"] if t in VT) + "\nprestige = 5")
once("subdue_the_khanates", "Subdue the Khanates", "Khiva and Bukhara raid our borders for slaves. End it.", PS, "war = no\nprestige = 10",
     "\n".join("%s = { any_owned = { add_core = THIS } }" % t for t in ["KHI", "BUK"]) + "\nprestige = 5")

# ---- Mongolia
MG = "OR = { tag = MGL tag = KHG }"
once("call_the_kurultai", "Call the Great Kurultai", "Summon every banner prince to Urga and have them swear to one Khan.", MG, "war = no", "prestige = 20", "kurultai")
once("revive_the_tumens", "Revive the Tumens", "Restore the decimal levy of Chinggis.", MG, "prestige = 10", "", "revived_tumens")
once("claim_inner_mongolia", "Claim Inner Mongolia", "The banners south of the Gobi are our kin.", MG, "war = no",
     "\n".join("%s = { any_owned = { add_core = THIS } }" % t for t in ["SYN", "CHH", "RHE"]) + "\nprestige = 5")
once("ride_on_beijing", "Ride on Beijing", "Kublai's capital waits behind its walls.", MG + "\nexists = ZHL", "war = no\nprestige = 30", "ZHL = { any_owned = { add_core = THIS } }\ncasus_belli = { target = ZHL type = conquest months = 60 }")
once("claim_dzungaria", "Claim Dzungaria", "The western Mongols' pastures were stolen by the Qing.", MG + "\nexists = XIN", "war = no", "XIN = { any_owned = { add_core = THIS } }\ncasus_belli = { target = XIN type = conquest months = 60 }")
once("claim_buryatia", "Gather the Buryats", "The forest Mongols by Lake Baikal shall join the horde.", MG, "war = no", "%d = { add_core = THIS }\nprestige = 5" % P("Irkutsk"))

# ---- other peoples
once("hire_chinese_advisors", "Hire Chinese Advisors", "Only the warlords possess modern arms and machines. Pay their experts to teach us.", "civilized = no\nNOT = { has_country_flag = chinese_warlord }\nNOT = { has_country_flag = ghostland }", "money = 15000\nwar = no", "treasury = -15000", "chinese_advisors", 7300)
once("sonno_joi_dec", "Sonno Joi", "Rally the domains behind the Emperor against the Chinese fleets.", "tag = JAP", "war = no", "prestige = 10", "sonno_joi")
once("open_nanyang_ports", "Open the Ports to Chinese Settlers", "Chinese traders, miners and farmers will enrich the kingdom.", "has_country_flag = old_world_colony\nNOT = { has_global_flag = new_world_opened }", "war = no", "prestige = 5", "nanyang_haven", 7300)

# ---- exclusive choices (after Heartbreaker): one decision of a group closes the others for good
def choice(group, tech, options, potential=WL):
    _all = list(WARLORDS)
    _off = sum(map(ord, group))
    for _i, (key, title, desc, allow, effect, modname) in enumerate(options):
        others = " or ".join(o[1] for o in options if o[0] != key)
        # the AI of each clique leans to one option, so computer-run neighbours differ from each other
        _mine = [t_ for j_, t_ in enumerate(_all) if (j_ + _off) % len(options) == _i]
        ai = "1\n\t\t\tmodifier = {\n\t\t\t\tfactor = 0\n\t\t\t\tNOT = {\n\t\t\t\t\tOR = {\n%s\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}" % "\n".join("\t\t\t\t\t\ttag = %s" % t_ for t_ in _mine)
        eff = "set_country_flag = chose_%s\nset_country_flag = did_%s\n" % (group, key)
        if modname:
            eff += "add_country_modifier = { name = %s duration = -1 }\n" % modname
        decision(key, title, "%s §RWe can then never choose: %s.§!" % (desc, others),
                 potential + "\nNOT = { has_country_flag = chose_%s }" % group, allow, eff + effect, ai, tech=tech)


choice("creed", IDEO, [
    ("adopt_three_principles", "Adopt the Three Principles", "Nationalism, democracy and the people's livelihood become the creed of the state.",
     "war = no\nprestige = 20", "nationalvalue = nv_liberty\nany_pop = { consciousness = 1 }\nprestige = 5", None),
    ("restore_confucian_order", "Restore the Confucian Order", "Reopen the temples and the examinations.",
     "war = no\nprestige = 20", "nationalvalue = nv_order\nany_pop = { militancy = -1 }\nprestige = 5", None),
    ("grant_provincial_constitution", "Grant a Provincial Constitution", "Promise the gentry an assembly and self-rule: our province first, the nation later.",
     "war = no\nprestige = 20", "nationalvalue = nv_equality\nany_pop = { consciousness = 1 }", "federal_self_rule")])
choice("opium", ENL, [
    ("opium_monopoly_dec", "Establish an Opium Monopoly", "A suppression bureau that sells what it confiscates. The money is very good.",
     "war = no", "treasury = 60000\nprestige = -5", "opium_monopoly"),
    ("opium_suppression_dec", "Burn the Opium", "Burn the chests in public, as Lin Zexu did, and close the dens.",
     "war = no\nmoney = 10000", "treasury = -10000\nprestige = 10\nany_pop = { limit = { type = aristocrats } militancy = 1 }", "opium_suppression")])
choice("revenue", STATE, [
    ("reform_salt_gabelle", "Reform the Salt Gabelle", "Put the salt administration under salaried inspectors. Slow, honest money.",
     "war = no\nmoney = 10000", "treasury = -10000\nany_pop = { limit = { type = aristocrats } militancy = 2 }", "salt_gabelle"),
    ("raise_likin", "Raise Likin Barriers", "Tax every cart and junk that crosses our borders. Quick money, and trade will suffer.",
     "money = 1", "treasury = 15000", "likin_tax")])
choice("bandits", IDEO, [
    ("recruit_bandits", "Enrol the Bandit Chiefs", "Offer rank and pay to every bandit band in the hills.",
     "money = 1", "any_pop = { limit = { type = farmers } militancy = 1 }", "bandit_levies"),
    ("suppress_bandits", "Clear the Hills", "March columns through the back country until no band is left.",
     "war = no\nmoney = 15000", "treasury = -15000\nany_pop = { limit = { type = farmers } militancy = -1 }", "pacified_countryside"),
    ("arm_village_militia", "Arm the Village Militia", "Recognise the Red Spear societies as a home guard and let the villages defend themselves.",
     "money = 1", "prestige = 1", "village_militia")])
choice("army_model", STATE, [
    ("introduce_conscription", "Introduce Modern Conscription", "Register every household for service: a mass army.",
     "war = no\nmoney = 20000", "treasury = -20000\nany_pop = { limit = { type = farmers } militancy = 1 }", "modern_conscription"),
    ("raise_model_army", "Raise a Model Army", "A small, drilled, well-paid force on the foreign pattern: quality before numbers.",
     "war = no\nmoney = 30000", "treasury = -30000\nprestige = 5", "model_army")])
choice("economy", STATE, [
    ("road_state_arsenals", "Government Supervision, Merchant Management", "The state founds the arsenals and mills and merchants run them.",
     "war = no\nmoney = 25000", "treasury = -25000", "state_capitalism"),
    ("road_merchant_enterprise", "Free the Merchant Guilds", "Lift the old restrictions and let the guilds and native banks finance what they will.",
     "war = no", "prestige = -2", "merchant_enterprise"),
    ("road_agrarian_order", "Agriculture is the Root", "Dykes, granaries and light land tax: the old wisdom, properly funded.",
     "war = no\nmoney = 15000", "treasury = -15000\nany_pop = { limit = { type = farmers } militancy = -1 }", "agrarian_order")])
choice("learning", "idealism", [
    ("hire_foreign_advisors", "Send Students Abroad", "Fund a generation of engineers and officers in foreign schools: a great deal of new learning, for one generation.",
     "money = 25000", "treasury = -25000\nadd_country_modifier = { name = foreign_advisors duration = 7300 }", None),
    ("found_national_academy", "Found a National Academy", "Build our own schools of western learning at home: less at once, but for good.",
     "money = 25000\nwar = no", "treasury = -25000\nprestige = 5", "national_academy")])
choice("outlook", NATIO, [
    ("maritime_policy", "Look to the Sea", "Our future lies in the southern and western oceans: ships, ports and dominions.",
     "war = no\ntotal_amount_of_ships = 10", "prestige = 5", "maritime_policy"),
    ("continental_policy", "Look to the Land", "The country will be reunified by armies, not by fleets.",
     "war = no", "prestige = 5", "continental_policy")])
choice("legitimacy", NATIO, [
    ("claim_the_mandate", "Claim the Mandate of Heaven", "With the old capital and great prestige, found a new dynasty.",
     "prestige = 100\nwar = no\nowns = 1612", "prestige = 25", "mandate_of_heaven"),
    ("proclaim_provisional_republic", "Proclaim the Provisional Republic", "With Nanjing or Canton and great prestige, declare ourselves the lawful republican government.",
     "prestige = 100\nwar = no\nOR = {\n\towns = 2221\n\towns = 1493\n}", "prestige = 25\nany_pop = { consciousness = 1 }", "provisional_republic")])
choice("land", REVO, [
    ("land_to_the_tiller", "Land to the Tiller", "Break up the great estates and give the fields to those who work them.",
     "war = no", "any_pop = { limit = { type = aristocrats } militancy = 3 }\nany_pop = { limit = { type = farmers } militancy = -2 }", "land_to_tiller"),
    ("uphold_the_landlords", "Uphold the Gentry", "The landlords collect our taxes and officer our militia. Confirm their titles.",
     "war = no", "any_pop = { limit = { type = farmers } militancy = 1 }\nprestige = 3", "landlord_compact")])
choice("mass", MASS, [
    ("build_party_state", "Build the Party-State", "One party, one leader, one army: organise the whole people.",
     "war = no", "any_pop = { consciousness = -1 }\nprestige = 5", "party_state"),
    ("convene_parliament", "Convene a National Assembly", "Elections, a cabinet and a constitution that binds the generals.",
     "war = no", "any_pop = { militancy = -2 }\nprestige = 10", "constitutional_parliament")])

# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
NAMES = {t: w[0] for t, w in WARLORDS.items()}
NAMES.update({"KOR": "Korea", "DAI": "Dai Nam", "BUR": "Burma"})
for tag, (ident, dev, amb) in IDENTITY.items():
    me = "tag = %s" % tag
    rival, partner, target = RIVAL[tag], PARTNER[tag], TARGET[tag]
    once("%s_identity" % tag, ident[0], ident[1] + " Only %s can do this." % NAMES[tag], me, "war = no", "prestige = 3", "id_" + tag)
    once("%s_develop" % tag, dev[0], dev[1], me, "war = no\nmoney = %d" % dev[2], "treasury = -%d\nprestige = 5" % dev[2], "dev_" + tag)
    once("%s_ambition" % tag, amb[0], amb[1] + " Our rivalry with %s is settled." % NAMES[rival],
         me + "\nNOT = { has_country_flag = did_%s_detente }" % tag, "owns = %d" % CAPITALS[rival], "prestige = 25\nbadboy = -3", "amb_" + tag)
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
         me + "\nexists = %s\nNOT = { has_country_flag = did_%s_detente }" % (rival, tag), "war = no",
         "relation = { who = %s value = -100 }\ncasus_belli = { target = %s type = humiliate months = 60 }\nprestige = 3" % (rival, rival))
    once("%s_detente" % tag, "Offer a Truce to %s" % NAMES[rival],
         "Send an envoy to %s: the feud serves neither of us while others grow. §RWe can then never denounce them, and we give up our ambition against them.§!" % NAMES[rival],
         me + "\nexists = %s\nNOT = { has_country_flag = did_%s_denounce }\nNOT = { has_country_flag = did_%s_ambition }" % (rival, tag, tag),
         "war = no\nNOT = { war_with = %s }" % rival,
         "relation = { who = %s value = 200 }\nprestige = -3\nbadboy = -2" % rival, "clique_truce")

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

wr("decisions/WarlordEra.txt", "political_decisions = {\n" + "\n".join(DEC) + "}\n")
print("decisions:", len(DEC), "| technology required:", dict(GATES.most_common()))

# ------------------------------------------------------------------ events
EV = []
eid = [880000]
INLAND = [t for t, w in WARLORDS.items() if w[6] and t not in ("ZHL", "FTN", "SDG", "JSU", "ZHJ", "FUJ", "GDG", "GXI")]


def event(title, desc, trigger, options, mtth="days = 1", once_only=True, picture="Upperhouse"):
    eid[0] += 1
    i = eid[0]
    s = 'country_event = {\n\tid = %d\n\ttitle = "EVTNAME%d"\n\tdesc = "EVTDESC%d"\n\tpicture = "%s"\n' % (i, i, i, picture)
    if once_only:
        s += "\tfire_only_once = yes\n"
    s += "\ttrigger = {\n%s\n\t}\n\tmean_time_to_happen = {\n\t\t%s\n\t}\n" % (block(trigger, 2), mtth)
    for j, (nm, eff) in enumerate(options):
        k = "EVTOPT%s%d" % ("ABCD"[j], i)
        s += '\toption = {\n\t\tname = "%s"\n%s\n\t}\n' % (k, block(eff, 2))
        loc(k, nm)
    s += "}\n"
    loc("EVTNAME%d" % i, title)
    loc("EVTDESC%d" % i, desc)
    EV.append(s)
    return i


def setup(tag, modname, title, desc):
    eid[0] += 1
    i = eid[0]
    EV.append('country_event = {\n\tid = %d\n\ttitle = "EVTNAME%d"\n\tdesc = "EVTDESC%d"\n\tpicture = "Upperhouse"\n\ttrigger = {\n\t\t%s\n\t\tNOT = { has_country_modifier = %s }\n\t}\n'
              '\tmean_time_to_happen = {\n\t\tdays = 1\n\t}\n\toption = {\n\t\tname = "EVTOPTA%d"\n\t\tadd_country_modifier = { name = %s duration = -1 }\n\t}\n}\n'
              % (i, i, i, tag, modname, i, modname))
    loc("EVTNAME%d" % i, title)
    loc("EVTDESC%d" % i, desc)
    loc("EVTOPTA%d" % i, "So be it.")


setup("OR = { tag = PAN tag = KLS }", "khalsa_army", "The Khalsa Army",
      "Maharaja Ranjit Singh has built the most formidable army in Asia. The Sikh Empire is not yet a modern state, but no warlord can afford to ignore it.")
setup("OR = { tag = MGL tag = KHG }", "mongol_horde", "The Great Horde",
      "The banners of Mongolia have thrown off Chinese rule. They have no factories and no railways, but every herdsman is a cavalryman.")
setup("OR = { tag = PER tag = PSE }", "qajar_nizam", "The Shah's New Army",
      "Persia has begun to reform its army and treasury on modern lines.")
setup("OR = {\n\t\t\t" + "\n\t\t\t".join("tag = %s" % t for t in INLAND) + "\n\t\t}", "inland_heartland", "Inland Heartland",
      "Our clique has no coast. What we lack in ports we make up for in arsenals and granaries that no fleet can reach.")

for _t, (_name, _desc, _kw) in TRAITS.items():
    setup("tag = %s" % _t, "trait_" + _t, _name, _desc)

event("The Sea Lanes Turn", "Chinese dominions now exist beyond the oceans, and the junks that once carried settlers to our ports sail on to newer lands. The great migration to the southern seas is over.",
      "has_country_flag = old_world_colony\nhas_global_flag = new_world_opened",
      [("We must compete fairly now.", "clr_country_flag = new_world_nation\nclr_country_flag = old_world_colony\nremove_country_modifier = nanyang_haven")],
      once_only=False)
event("A New World Opens", "The first Chinese dominion has been chartered overseas. From now on emigrants will make for the new lands rather than the southern seas.",
      "has_country_flag = chinese_warlord\nhas_global_flag = new_world_opened\nNOT = { has_country_flag = saw_new_world }",
      [("Then we must not be left behind.", "set_country_flag = saw_new_world")], once_only=False)
event("The Scramble for the World", "China is divided between the cliques, but the cliques alone possess steamships, rifles and factories. Every shore on Earth lies open. Whoever takes the most will have the strength to reunify the country.",
      "has_country_flag = major_warlord\nyear = 1836\nNOT = { has_country_flag = saw_intro }",
      [("The world is ours to take.", "set_country_flag = saw_intro\nprestige = 1")], once_only=False)
event("Bandits in the Hills", "Disbanded soldiers have turned bandit in the back country.",
      "has_country_flag = chinese_warlord\nwar = no\naverage_militancy = 3",
      [("Hunt them down.", "treasury = -3000\nany_pop = { limit = { type = soldiers } militancy = -1 }"),
       ("Enlist them.", "any_pop = { limit = { type = farmers } militancy = 1 }\nprestige = 1")],
      mtth="months = 240", once_only=False, picture="Demonstration")
event("Defection of a Division", "A rival's division commander offers to bring his men over for a price.",
      "has_country_flag = chinese_warlord\nwar = yes\nmoney = 20000",
      [("Pay him.", "treasury = -15000\nwar_exhaustion = -5\nprestige = 2"), ("We do not buy traitors.", "prestige = 1")],
      mtth="months = 180", once_only=False)
event("Silver Bullets", "Our officers report that the enemy is bribing our garrison commanders.",
      "has_country_flag = chinese_warlord\nwar = yes\nwar_exhaustion = 10",
      [("Raise their pay.", "treasury = -10000"), ("Shoot the waverers.", "war_exhaustion = 3\nany_pop = { limit = { type = soldiers } militancy = 1 }")],
      mtth="months = 200", once_only=False)
event("Students Demand Reunification", "Students march in the capital demanding an end to the division of the country.",
      "has_country_flag = chinese_warlord\nNOT = { exists = CHI }\nyear = 1850",
      [("They speak for the nation.", "any_pop = { consciousness = 1 }\nprestige = 3"), ("Clear the streets.", "any_pop = { militancy = 1 }")],
      mtth="months = 300", once_only=False, picture="Demonstration")
event("Settlers Sail for the South Seas", "Poor farmers from the coast are leaving for the southern seas in their thousands.",
      "has_country_flag = chinese_warlord\nNOT = { has_global_flag = new_world_opened }\nyear = 1837",
      [("Let them go, and tax their remittances.", "treasury = 4000"), ("Our colonies need them more.", "prestige = 1")],
      mtth="months = 240", once_only=False)
wr("events/WarlordEra.txt", "\n".join(EV))
print("events:", len(EV))

wr("localisation/00_warlord_era_gameplay.csv", "\n".join(LOC) + "\n")
