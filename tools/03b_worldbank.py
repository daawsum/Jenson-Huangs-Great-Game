"""Stage 3b: the World Bank on the Falklands, adapted from IGoR puir's Liechtenstein bank.

A dummy uncivilized country (WBK) whose `bankers` pops are the only pops able to work
precious metal. Its huge gold income fills its national bank, which every country can borrow from.
Run after 03_gameplay.py.
"""
import os, re, glob
from config import *

if not WORLD_BANK:
    print("WORLD_BANK is switched off in config.py; skipped")
    raise SystemExit(0)


def out(rel):
    return open(os.path.join(OUT, rel), encoding=ENC).read()


# ---- pop type: bankers (exists only where history places it: nobody promotes into it)
wr("poptypes/bankers.txt", """sprite = 5
color = { 18 129 10 }
strata = rich
unemployment = yes

rebel =
{
	cavalry = 0
	artillery = 0.1
	cuirassier = 0
	dragoon = 0
	guard = 0.3
	hussar = 0
	infantry = 0.6
	irregular = 0
}

everyday_needs = {
}

life_needs = {
}

luxury_needs = {
}

country_migration_target =
{
	factor = 0
}

migration_target =
{
	factor = 0
}

promote_to =
{
}

ideologies = {
}

issues =
{
}
""")

# ---- nobody migrates into a ghostland country
n = 0
for f in glob.glob(os.path.join(OUT, "poptypes", "*.txt")):
    if os.path.basename(f) == "bankers.txt":
        continue
    t = open(f, encoding=ENC).read()
    key = "\t# Warlord Era: only flagged immigrant nations"
    if key in t and "has_country_flag = ghostland" not in t:
        t = t.replace(key, "\tmodifier = {\n\t\tfactor = -1000\n\t\thas_country_flag = ghostland\n\t}\n" + key, 1)
        open(f, "w", encoding=ENC, newline="\r\n").write(t)
        n += 1
print("pop types given the ghostland rule:", n)

# ---- production: precious metal is worked by bankers only
_ptf = os.path.join(OUT, "common", "production_types.txt")       # 03a_tech.py may have added to it
pt = open(_ptf, encoding=ENC).read().replace("\r\n", "\n") if os.path.exists(_ptf) else rd("common", "production_types.txt")
tmpl = """RGO_template_bankers = {
	owner =
	{
		poptype = aristocrats
		effect = output
	}

	employees = {
		{
			poptype = bankers
			effect = throughput
			amount = 1
		}
	}

	type = rgo
	workforce = 400000
}

"""
old = re.search(r"precious_metal_mine\s*=\s*\{[^}]*\}", pt)
assert old
pt = pt[:old.start()] + tmpl + "precious_metal_mine = {\n\ttemplate = RGO_template_bankers\n\toutput_goods = precious_metal\n\tvalue = 10000\n\tmine = yes\n}" + pt[old.end():]
wr("common/production_types.txt", pt)

# ---- party policies used only by the bank
iss = rd("common", "issues.txt")
a = re.search(r"trade_policy\s*=\s*\{", iss)
iss = iss[:a.end()] + "\n\t\tworld_bank = {\n\t\t\tmax_tariff = 0.01\n\t\t\tmin_tariff = 0\n\t\t}" + iss[a.end():]
b = re.search(r"economic_policy\s*=\s*\{", iss)
rules = ["build_factory = yes", "expand_factory = yes", "open_factory = yes", "destroy_factory = no", "build_railway = no",
         "factory_priority = yes", "can_subsidise = yes", "pop_build_factory = no", "pop_expand_factory = no", "pop_open_factory = no",
         "delete_factory_if_no_input = no", "pop_build_factory_invest = no", "pop_expand_factory_invest = no", "open_factory_invest = no",
         "build_factory_invest = no", "expand_factory_invest = no", "build_railway_invest = no", "allow_foreign_investment = no",
         "can_invest_in_pop_projects = no"]
iss = iss[:b.end()] + "\n\t\tworld_bank_economics = {\n\t\t\tmax_tax = 1\n\t\t\tmin_tax = 0.99\n\n\t\t\trules = {\n" + \
    "".join("\t\t\t\t%s\n" % r for r in rules) + "\t\t\t}\n\t\t}" + iss[b.end():]
wr("common/issues.txt", iss)

# ---- modifier
em = out("common/event_modifiers.txt")
if "world_bank_rp_nerf" not in em:
    em += ("world_bank_rp_nerf = {\n\tdiplomatic_points_modifier = -1000.0\n\tglobal_pop_militancy_modifier = -100.0\n"
           "\tresearch_points_modifier = -1\n\tprestige = -10\n\ticon = 10\n}\n\n")
    open(os.path.join(OUT, "common", "event_modifiers.txt"), "w", encoding=ENC, newline="\r\n").write(em)

# ---- control events (ids follow the Warlord Era block)
EV = """
# ------------------------------------------------------------------ World Bank control (after IGoR puir)
country_event = {
	id = 880101
	title = "EVTNAME880101"
	desc = "EVTDESC880101"
	picture = "Upperhouse"
	fire_only_once = yes
	trigger = {
		tag = WBK
	}
	mean_time_to_happen = {
		days = 1
	}
	option = {
		name = "EVTOPTA880101"
		add_country_modifier = {
			name = world_bank_rp_nerf
			duration = -1
		}
	}
}

country_event = {
	id = 880102
	title = "EVTNAME880102"
	desc = "EVTDESC880102"
	picture = "Upperhouse"
	trigger = {
		tag = WBK
		prestige = 1
	}
	mean_time_to_happen = {
		days = 1
	}
	immediate = {
		prestige = -100
	}
	option = {
		name = "EVTOPTA880101"
	}
}

country_event = {
	id = 880103
	title = "EVTNAME880103"
	desc = "EVTDESC880103"
	picture = "Upperhouse"
	trigger = {
		tag = WBK
		civilized = yes
	}
	mean_time_to_happen = {
		days = 1
	}
	immediate = {
		civilized = no
	}
	option = {
		name = "EVTOPTA880101"
	}
}

country_event = {
	id = 880104
	title = "EVTNAME880104"
	desc = "EVTDESC880104"
	picture = "Upperhouse"
	trigger = {
		tag = WBK
		part_of_sphere = yes
	}
	mean_time_to_happen = {
		days = 1
	}
	immediate = {
		random_country = {
			limit = {
				is_sphere_leader_of = WBK
			}
			diplomatic_influence = {
				who = WBK
				value = -400
			}
			relation = {
				who = WBK
				value = -200
			}
		}
	}
	option = {
		name = "EVTOPTA880101"
	}
}

country_event = {
	id = 880105
	title = "EVTNAME880105"
	desc = "EVTDESC880105"
	picture = "Upperhouse"
	trigger = {
		tag = WBK
		war = yes
	}
	mean_time_to_happen = {
		days = 1
	}
	immediate = {
		any_country = {
			limit = {
				war_with = WBK
			}
			end_war = WBK
			badboy = 5
		}
	}
	option = {
		name = "EVTOPTA880101"
	}
}
"""
ev = out("events/WarlordEra.txt")
if "880101" not in ev:
    open(os.path.join(OUT, "events", "WarlordEra.txt"), "w", encoding=ENC, newline="\r\n").write(ev + EV)

L = [
    ("bankers", "Bankers"),
    ("world_bank", "World Bank Charter"),
    ("world_bank_economics", "World Bank Economics"),
    ("world_bank_rp_nerf", "World Bank Neutrality"),
    ("desc_world_bank_rp_nerf", "The World Bank does no research, plays no diplomacy and never revolts."),
    ("EVTNAME880101", "The World Bank"), ("EVTDESC880101", "The World Bank on the Falkland Islands lends to every government. It takes no part in politics."),
    ("EVTOPTA880101", "Noted."),
    ("EVTNAME880102", "World Bank Prestige Reset"), ("EVTDESC880102", "Keeps the World Bank out of the great power rankings."),
    ("EVTNAME880103", "World Bank Stays Uncivilized"), ("EVTDESC880103", "Keeps the World Bank from westernizing."),
    ("EVTNAME880104", "The World Bank Cannot Be Sphered"), ("EVTDESC880104", "Removes any great power's influence over the World Bank."),
    ("EVTNAME880105", "The World Bank Cannot Be Attacked"), ("EVTDESC880105", "Any war against the World Bank ends at once, and the attacker gains infamy."),
]
lp = os.path.join(OUT, "localisation", "00_warlord_era_gameplay.csv")
t = open(lp, encoding=ENC).read()
if "bankers;" not in t:
    open(lp, "w", encoding=ENC, newline="\r\n").write(t + "".join("%s;%s;;;;;;;;;;;;;x\n" % kv for kv in L))
print("world bank written")
