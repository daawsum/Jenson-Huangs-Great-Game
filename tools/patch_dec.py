"""One-off patch of 03_gameplay.py: technology requirements, restricted formables, exclusive choices."""
import re
p = "03_gameplay.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:60], s.count(a))
    s = s.replace(a, b)


# ---- 1. every decision names a technology
rep(r'''def decision(key, title, desc, potential, allow, effect, ai=1):
    effect = _map_cultures(effect)
''', r'''# Every decision of a country that can research needs a technology, mostly from the political thought
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
''')
rep(r'''def formable(tag, name, key, cities, who, extra="", desc=None, prest=20):''', r'''def formable(tag, name, key, cities, who, extra="", desc=None, prest=20, tech=None):''')
rep(r'''             "prestige = %d\n%schange_tag = %s" % (prest, extra, tag))
''', r'''             "prestige = %d\n%schange_tag = %s" % (prest, extra, tag), tech=tech)
''')
rep(r'''    formable(tag, name, key, cities, "OR = {\n" + "\n".join("\ttag = %s" % t for t in tags) + "\n}", extra)''',
    r'''    formable(tag, name, key, cities, "OR = {\n" + "\n".join("\ttag = %s" % t for t in tags) + "\n}", extra, tech=False)''')

# ---- 2. only its own cliques may proclaim a Chinese state
a = s.index('formable("BYG"')
b = s.index('formable("MZG"')
b = s.index("\n", b) + 1
s = s[:a] + r'''_FN = {"BYG": ("the Beiyang Government", "beiyang", [1612, 1617, 1563, 1508, 1572]), "LGG": ("Liangguang", "liangguang", [1493, 1502, 1503]),
       "SHU": ("the State of Shu", "shu", [1578, 1577]), "WUU": ("the State of Wu", "wu", [2221, 1538, 1604]),
       "CHU": ("the State of Chu", "chu", [1522, 1524, 1516]), "DIA": ("the State of Dian", "dian", [1601, 1505]),
       "NWF": ("the Northwest Federation", "northwest", [1490, 1559, 1600]), "MZG": ("Manchuria", "manchuria", [1479, 1555, 1552])}


def _who(tags):
    return "OR = {\n" + "\n".join("\ttag = %s" % t for t in tags) + "\n}"


for _t, (_nm, _key, _cities) in _FN.items():
    formable(_t, _nm, _key, _cities, _who(FORMERS[_t]) + "\nNOT = { exists = CHI }", _acc(_t),
             "With %s in our hands we can proclaim %s. Only %s may do so." % (", ".join(PNAME[x] for x in _cities), _nm, ", ".join(WARLORDS[x][0] for x in FORMERS[_t])))
''' + s[b:]
rep(r'''formable("CHI", "the Republic of China", "china", [1612, 2221, 1493, 1578, 1559, 1522, 1479], WL,''',
    r'''formable("CHI", "the Republic of China", "china", [1612, 2221, 1493, 1578, 1559, 1522, 1479],
         "OR = {\n" + "\n".join("\ttag = %s" % t for t in FORMERS["CHI"]) + "\n}",''')
rep(r'''"Beijing, Nanjing, Canton, Chengdu, Xian, Wuchang and Mukden all fly our flag. The warlord era is over: proclaim one China.", 100)''',
    r'''"Beijing, Nanjing, Canton, Chengdu, Xian, Wuchang and Mukden all fly our flag. The warlord era is over: proclaim one China. Only the six great cliques and the eight regional states may do so.", 100)''')

# ---- 3. the one-off decisions that become exclusive choices
for k in ("reform_salt_gabelle", "raise_likin", "opium_monopoly_dec", "hire_foreign_advisors", "recruit_bandits", "introduce_conscription",
          "grant_provincial_constitution", "arm_village_militia", "adopt_three_principles", "restore_confucian_order", "claim_the_mandate"):
    m = re.search(r'(?m)^once\("%s".*\n' % k, s)
    assert m, k
    s = s[:m.start()] + s[m.end():]

rep(r'''# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''', r'''# ---- exclusive choices (after Heartbreaker): one decision of a group closes the others for good
def choice(group, tech, options, potential=WL):
    for key, title, desc, allow, effect, modname in options:
        others = " or ".join(o[1] for o in options if o[0] != key)
        eff = "set_country_flag = chose_%s\nset_country_flag = did_%s\n" % (group, key)
        if modname:
            eff += "add_country_modifier = { name = %s duration = -1 }\n" % modname
        decision(key, title, "%s §RWe can then never choose: %s.§!" % (desc, others),
                 potential + "\nNOT = { has_country_flag = chose_%s }" % group, allow, eff + effect, tech=tech)


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
     "money = 25000", "treasury = -25000", None),
    ("found_national_academy", "Found a National Academy", "Build our own schools of western learning at home: less at once, but for good.",
     "money = 25000\nwar = no", "treasury = -25000\nprestige = 5", "national_academy")])
rep_marker = None
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
''')
# students abroad keeps its twenty-year modifier
rep(r'''     "money = 25000", "treasury = -25000", None),''', r'''     "money = 25000", "treasury = -25000\nadd_country_modifier = { name = foreign_advisors duration = 7300 }", None),''')
rep("rep_marker = None\n", "")

# ---- 4. a rival is either denounced or reconciled, never both; reconciling gives up the ambition
rep(r'''    once("%s_ambition" % tag, amb[0], amb[1] + " Our rivalry with %s is settled." % NAMES[rival],
         me, "owns = %d" % CAPITALS[rival], "prestige = 25\nbadboy = -3", "amb_" + tag)''',
    r'''    once("%s_ambition" % tag, amb[0], amb[1] + " Our rivalry with %s is settled." % NAMES[rival],
         me + "\nNOT = { has_country_flag = did_%s_detente }" % tag, "owns = %d" % CAPITALS[rival], "prestige = 25\nbadboy = -3", "amb_" + tag)''')
rep(r'''         me + "\nexists = %s" % rival, "war = no",
         "relation = { who = %s value = -100 }\ncasus_belli = { target = %s type = humiliate months = 60 }\nprestige = 3" % (rival, rival))''',
    r'''         me + "\nexists = %s\nNOT = { has_country_flag = did_%s_detente }" % (rival, tag), "war = no",
         "relation = { who = %s value = -100 }\ncasus_belli = { target = %s type = humiliate months = 60 }\nprestige = 3" % (rival, rival))
    once("%s_detente" % tag, "Offer a Truce to %s" % NAMES[rival],
         "Send an envoy to %s: the feud serves neither of us while others grow. §RWe can then never denounce them, and we give up our ambition against them.§!" % NAMES[rival],
         me + "\nexists = %s\nNOT = { has_country_flag = did_%s_denounce }\nNOT = { has_country_flag = did_%s_ambition }" % (rival, tag, tag),
         "war = no\nNOT = { war_with = %s }" % rival,
         "relation = { who = %s value = 200 }\nprestige = -3\nbadboy = -2" % rival, "clique_truce")''')

# ---- 5. modifiers for the new choices
rep(r'''for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)
''', r'''mod("opium_suppression", "Opium Suppressed", "The dens are closed and the chests burned.", research_points_modifier=0.05, global_pop_militancy_modifier=-0.01, tax_efficiency=-0.03)
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
''')
rep(r'''print("decisions:", len(DEC))''', r'''print("decisions:", len(DEC), "| technology required:", dict(GATES.most_common()))''')
open(p, "w", encoding="utf-8").write(s)
print("patched")
