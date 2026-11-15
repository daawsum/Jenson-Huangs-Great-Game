"""Stage 3c: state size flags, implemented the way DoD Heartbreaker MP does it.

How Heartbreaker's system works (read from its cb_types.txt, defines.lua, State Sizing.txt):
  * Five dummy tags (TIN SMA MED LRG HUG). A yearly event stamps the matching tag's core on every
    province according to the population of its state.
  * common/defines.lua sets PEACE_COST_PRESTIGE = 4000. Every state-taking war goal exists in five
    sizes, carries `po_remove_prestige = yes` and a tiny `peace_cost_factor`, so its war score cost
    is a FIXED percentage (4000 x factor) instead of scaling with population:
        acquire core 4/12/16/24/32 %, acquire state 12/24/32/48/64 %, concession 8/16/24/32/40 %,
        place in the sun 4/8/12/16/20 %, free peoples 12/24/32/48/64 %.
  * `allowed_states` of each size only matches states carrying that size's core.
This file rebuilds that on top of vanilla's cb_types.txt, using Heartbreaker's numbers, names and
flag art. Vanilla's unsized war goals stay defined (vanilla events grant some of them) but can no
longer be justified. Run after 03b_worldbank.py.
"""
import os, re, glob, shutil
from config import *

if not STATE_FLAGS:
    print("STATE_FLAGS is switched off in config.py; skipped")
    raise SystemExit(0)

HB = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
if not os.path.isdir(HB):
    raise SystemExit("DoD Heartbreaker MP 4.9.5 is not installed; its state flag art and numbers are needed")

SIZES = [("TIN", "tiny", "Tiny"), ("SMA", "small", "Small"), ("MED", "medium", "Medium"), ("LRG", "large", "Large"), ("HUG", "huge", "Huge")]
# family -> peace_cost_factor per size (Heartbreaker's values; x 4000 = war score %)
FAMILIES = {
    "acquire_core_state": [0.001, 0.003, 0.004, 0.006, 0.008],
    "acquire_state": [0.003, 0.006, 0.008, 0.012, 0.016],
    "place_in_the_sun": [0.001, 0.002, 0.003, 0.004, 0.005],
    "free_peoples": [0.003, 0.006, 0.008, 0.012, 0.016],
    "demand_concession_casus_belli": [0.002, 0.004, 0.006, 0.008, 0.010],
    "unification_casus_belli": [0.002, 0.004, 0.008, 0.012, 0.016],
    "warlord_take_state": [0.002, 0.004, 0.006, 0.009, 0.012],          # this mod's own war goal
}
ERAS = [(880201, None, 1860, [200000, 900000, 1500000, 2100000]),       # Heartbreaker's years, twice its thresholds
        (880202, 1860, 1900, [300000, 1300000, 2100000, 3000000]),
        (880203, 1900, None, [400000, 1600000, 2800000, 4000000])]
RUNNER = "WBK" if WORLD_BANK else "ZHL"


def path(rel):
    return os.path.join(OUT, rel)


def read(rel):
    return open(path(rel), encoding=ENC).read()


def write(rel, t):
    wr(rel, t.replace("\r\n", "\n"))


# ---------------------------------------------------------------- tags, flags, history
ct = read("common/countries.txt")
if "WE_TIN" not in ct:
    add = "".join('%s\t\t= "countries/WE_%s.txt"\n' % (t[0], t[0]) for t in SIZES)
    ct = ct.replace("# Warlord Era\n", "# Warlord Era\n" + add, 1)
    assert "WE_TIN" in ct
    write("common/countries.txt", ct)
POL = ("slavery = no_slavery\nupper_house_composition = appointed\nvote_franschise = none_voting\npublic_meetings = no_meeting\n"
       "press_rights = censored_press\ntrade_unions = no_trade_unions\nvoting_system = first_past_the_post\npolitical_parties = underground_parties\n"
       "wage_reform = no_minimum_wage\nwork_hours = no_work_hour_limit\nsafety_regulations = no_safety\nhealth_care = no_health_care\n"
       "unemployment_subsidies = no_subsidies\npensions = no_pensions\nschool_reforms = no_schools\n")
os.makedirs(path("gfx/flags"), exist_ok=True)
for tag, key, name in SIZES:
    wr("common/countries/WE_%s.txt" % tag,
       'color = { 255 255 255 }\ngraphical_culture = EuropeanGC\n\nparty = {\n\tname = "%s_flag"\n\tstart_date = 1800.1.1\n\tend_date = 2000.1.1\n\n'
       '\tideology = reactionary\n\n\teconomic_policy = state_capitalism\n\ttrade_policy = protectionism\n\treligious_policy = moralism\n'
       '\tcitizenship_policy = residency\n\twar_policy = anti_military\n}\n' % tag)
    wr("history/countries/%s - %s State Flag.txt" % (tag, name),
       "primary_culture = british\nreligion = placeholder\ngovernment = absolute_monarchy\nplurality = 100\nnationalvalue = nv_order\n"
       "literacy = 1\ncivilized = no\nis_releasable_vassal = no\n" + POL + "ruling_party = %s_flag\n" % tag +
       "upper_house = {\n\tfascist = 0\n\tliberal = 25\n\tconservative = 65\n\treactionary = 10\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n")
    for suf in ["", "_communist", "_fascist", "_monarchy", "_republic"]:      # Heartbreaker's flag art
        shutil.copyfile(os.path.join(HB, "gfx", "flags", tag + suf + ".tga"), path("gfx/flags/%s%s.tga" % (tag, suf)))

# ---------------------------------------------------------------- defines: prestige-based fixed cost
dl = rd("common", "defines.lua")
dl, n = re.subn(r"(PEACE_COST_PRESTIGE\s*=\s*)[\d\.]+", r"\g<1>4000", dl)
assert n == 1
write("common/defines.lua", dl)

# ---------------------------------------------------------------- war goals
cb = read("common/cb_types.txt")


def block_span(text, name):
    m = re.search(r"(?m)^%s\s*=\s*\{" % re.escape(name), text)
    if not m:
        return None
    d, j = 1, m.end()
    while d and j < len(text):
        c = text[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
        elif c == "#":
            while j < len(text) and text[j] != "\n":
                j += 1
        j += 1
    return m.start(), j


def set_field(b, key, val):
    if re.search(r"(?m)^\s*%s\s*=" % key, b):
        return re.sub(r"(?m)^(\s*%s\s*=\s*)[\w\.\-]+" % key, r"\g<1>%s" % val, b, count=1)
    i = b.index("{") + 1
    return b[:i] + "\n\t%s = %s" % (key, val) + b[i:]


def add_flag(b, line):
    if line.split()[0] in re.sub(r"#.*", "", b):
        return b
    k = b.rindex("}")
    return b[:k] + "\t%s\n" % line + b[k:]


def inject(b, section, line):
    """Put `line` first inside `section = { ... }`; create the section if it is missing."""
    m = re.search(r"(?m)^\s*%s\s*=\s*\{" % section, b)
    if m:
        return b[:m.end()] + "\n\t\t%s" % line + b[m.end():]
    k = b.rindex("}")
    return b[:k] + "\t%s = {\n\t\t%s\n\t}\n" % (section, line) + b[k:]


order = []
if "acquire_state_tiny" not in cb:
    cb = re.sub(r"(?ms)^warlord_take_state_(tiny|small|medium|large|huge) = \{.*?\n\}\n", "", cb)      # older split, if present
    for fam, factors in FAMILIES.items():
        sp = block_span(cb, fam)
        assert sp, "war goal not found in cb_types.txt: " + fam
        base = cb[sp[0]:sp[1]]
        variants = ""
        for (tag, key, name), f in zip(SIZES, factors):
            v = base.replace("%s = {" % fam, "%s_%s = {" % (fam, key), 1)
            v = set_field(v, "peace_cost_factor", f)
            v = add_flag(v, "po_remove_prestige = yes")
            v = inject(v, "allowed_states", "any_owned_province = { is_core = %s }" % tag)
            v = inject(v, "can_use", "any_owned_province = { is_core = %s }" % tag)
            variants += v + "\n\n"
            order.append("%s_%s" % (fam, key))
        # the unsized original: still defined for vanilla events, costed like a medium state, not justifiable
        orig = set_field(base, "peace_cost_factor", factors[2])
        orig = add_flag(orig, "po_remove_prestige = yes")
        orig = re.sub(r"(?m)^\s*always\s*=\s*yes\s*\n", "", orig)
        orig = set_field(orig, "constructing_cb", "no")
        if fam == "warlord_take_state":
            orig = ""
        cb = cb[:sp[0]] + variants + orig + cb[sp[1]:]
    # war goals that only remove prestige were costed for PEACE_COST_PRESTIGE = 1; give them Heartbreaker's 16%
    for name in ("humiliate", "rude_boy"):
        sp = block_span(cb, name)
        if sp:
            cb = cb[:sp[0]] + set_field(cb[sp[0]:sp[1]], "peace_cost_factor", 0.004) + cb[sp[1]:]
    po = re.search(r"peace_order\s*=\s*\{", cb)
    cb = cb[:po.end()] + "\n" + "\n".join(order) + cb[po.end():]
    cb = re.sub(r"(?m)^warlord_take_state\s*\n", "", cb)
    write("common/cb_types.txt", cb)
print("war goals split by state size:", len(order), "| PEACE_COST_PRESTIGE = 4000")

# ---------------------------------------------------------------- yearly sizing event
def stamp(lo, hi, tag):
    cond = ("\t\t\t\t\t\ttotal_pops = %d\n" % lo if lo else "") + ("\t\t\t\t\t\tNOT = { total_pops = %d }\n" % hi if hi else "")
    others = "".join("\t\t\t\tremove_core = %s\n" % t[0] for t in SIZES if t[0] != tag)
    return ("\t\tany_country = {\n\t\t\tlimit = {\n\t\t\t\twar = no\n\t\t\t}\n\t\t\tany_owned = {\n\t\t\t\tlimit = {\n\t\t\t\t\tstate_scope = {\n"
            + cond + "\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t\tadd_core = %s\n" % tag + others + "\t\t\t}\n\t\t}\n")


EV = "\n# ------------------------------------------------------------------ State sizing (after DoD Heartbreaker)\n"
for eid, y0, y1, th in ERAS:
    trig = "\t\ttag = %s\n\t\tNOT = { has_country_modifier = sizing_cooldown }\n" % RUNNER
    trig += ("\t\tyear = %d\n" % y0 if y0 else "") + ("\t\tNOT = { year = %d }\n" % y1 if y1 else "")
    b = [None] + th + [None]
    EV += ('country_event = {\n\tid = %d\n\ttitle = "EVTNAME880201"\n\tdesc = "EVTDESC880201"\n\tpicture = "Upperhouse"\n\ttrigger = {\n%s\t}\n'
           '\tmean_time_to_happen = {\n\t\tdays = 1\n\t}\n\timmediate = {\n\t\tadd_country_modifier = {\n\t\t\tname = sizing_cooldown\n\t\t\tduration = 365\n\t\t}\n\t}\n'
           '\toption = {\n\t\tname = "EVTOPTA880201"\n' % (eid, trig))
    for i, t in enumerate(SIZES):
        EV += stamp(b[i], b[i + 1], t[0])
    EV += "\t}\n}\n\n"
ev = read("events/WarlordEra.txt")
if "880201" not in ev:
    write("events/WarlordEra.txt", ev + EV)
em = read("common/event_modifiers.txt")
if "sizing_cooldown" not in em:
    write("common/event_modifiers.txt", em + "sizing_cooldown = {\n\ticon = 10\n}\n\n")

# ---------------------------------------------------------------- text: Heartbreaker's names, this mod's numbers
hbloc = {}
for f in glob.glob(os.path.join(HB, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        p = l.split(";")
        if len(p) > 1 and p[0] and p[0] not in hbloc:
            hbloc[p[0]] = p[1]
loc = []
k = lambda n: ("%gM" % (n / 1e6)) if n >= 1e6 else ("%dk" % (n // 1000))
cost = lambda fam, i: round(FAMILIES[fam][i] * 4000)
for i, (tag, key, name) in enumerate(SIZES):
    def rng(th):
        return ("Less than %s POPs" % k(th[0])) if i == 0 else ("Greater than %s POPs" % k(th[3])) if i == 4 else ("%s to %s POPs" % (k(th[i - 1]), k(th[i])))
    text = ("\xa7G%s State Flag\\n\xa7WThis province is in a state that meets the following criteria:\\n"
            "\xa7Y1836 - 1860 \xa7W%s\\n\xa7Y1860 - 1900 \xa7W%s\\n\xa7Y1900+ \xa7W%s\\n\\n"
            "\xa7RWarscore Costs\\n\xa7WTaking this state costs:\\n"
            "\xa7YWarlord Claim: \xa7W%d%% Warscore\\n\xa7YAcquire Core: \xa7W%d%% Warscore\\n\xa7YAcquire State: \xa7W%d%% Warscore\\n"
            "\xa7YDemand Concession: \xa7W%d%% Warscore\\n\xa7YPlace in the Sun: \xa7W%d%% Warscore\\n\xa7YFree Peoples: \xa7W%d%% Warscore") % (
        name, rng(ERAS[0][3]), rng(ERAS[1][3]), rng(ERAS[2][3]), cost("warlord_take_state", i), cost("acquire_core_state", i),
        cost("acquire_state", i), cost("demand_concession_casus_belli", i), cost("place_in_the_sun", i), cost("free_peoples", i))
    loc += [(tag, text), (tag + "_ADJ", "%s State" % name), (tag + "_flag", "State Size Marker")]
    for fam in FAMILIES:
        for suf in ("", "_short", "_desc", "_setup"):
            key2 = "%s_%s%s" % (fam, key, suf)
            if fam == "warlord_take_state":
                txt = {"": "Warlord Claim (%s State)" % name, "_short": "Warlord Claim (%s)" % name,
                       "_desc": "Seize a \xa7Y%s state\xa7W from a rival warlord." % key, "_setup": "Take $STATE$ from $RECIPIENT$"}[suf]
            else:
                txt = hbloc.get(key2) or "%s (%s State)" % (fam.replace("_", " ").title(), name)
            loc.append((key2, txt))
loc += [("EVTNAME880201", "State Sizes Reassessed"), ("EVTOPTA880201", "Noted."),
        ("EVTDESC880201", "Every state in the world has been re-measured and given its Tiny, Small, Medium, Large or Huge marker."),
        ("sizing_cooldown", "State Sizing Cooldown"), ("desc_sizing_cooldown", "State sizes are measured once a year.")]
lp = "localisation/00_warlord_era_gameplay.csv"
t = read(lp)
if "\nTIN;" not in t:
    write(lp, t + "".join("%s;%s;;;;;;;;;;;;;x\n" % (a, b.replace(";", ",")) for a, b in loc))
print("state size flags written (Heartbreaker style):", [s[0] for s in SIZES])
