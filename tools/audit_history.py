"""Audit my country history files line by line against vanilla and working mods on this machine."""
import os, re, glob, collections, sys
from config import *

MODS = ["", "mod/GFM", "mod/HPM", "mod/HFM", "mod/Vae Victis 0.4.1", "mod/IGoR_puir 13.0.4 (Naval Cap+OSC)", "mod/Divergences of Darkness"]


def strip(t):
    return re.sub(r"#.*", "", t)


def base(t):
    """Text before the first dated block."""
    return re.split(r"\n\s*\d{1,4}\.\d+\.\d+\s*=\s*\{", "\n" + strip(t))[0]


ref_keys = collections.Counter()
ref_pairs = collections.defaultdict(collections.Counter)      # key -> values seen
unciv_gov, civ_gov = collections.Counter(), collections.Counter()
unciv_combo = collections.Counter()
n = 0
for m in MODS:
    for f in glob.glob(os.path.join(V, m, "history", "countries", "*.txt")):
        t = base(open(f, encoding=ENC, errors="replace").read())
        n += 1
        kv = re.findall(r"^\s*([A-Za-z_]\w*)\s*=\s*\"?([^\s\"{}]+)", t, re.M)
        d = dict(kv)
        for k, v in kv:
            ref_keys[k] += 1
            ref_pairs[k][v] += 1
        civ = d.get("civilized") == "yes"
        (civ_gov if civ else unciv_gov)[d.get("government")] += 1
        if not civ:
            for k in ("vote_franschise", "upper_house_composition", "political_parties", "voting_system", "press_rights", "trade_unions", "public_meetings"):
                unciv_combo[(k, d.get(k))] += 1
print("reference country files:", n)
print("governments of UNCIVILIZED countries in references:", dict(unciv_gov))

mine = glob.glob(os.path.join(OUT, "history", "countries", "*.txt"))
bad_keys, bad_vals = collections.Counter(), collections.Counter()
my_unciv_gov = collections.Counter()
weird = collections.Counter()
ENUM = ["government", "nationalvalue", "schools", "slavery", "upper_house_composition", "vote_franschise", "public_meetings", "press_rights",
        "trade_unions", "voting_system", "political_parties", "wage_reform", "work_hours", "safety_regulations", "health_care",
        "unemployment_subsidies", "pensions", "school_reforms", "civilized", "is_releasable_vassal",
        "land_reform", "admin_reform", "finance_reform", "education_reform", "transport_improv", "pre_indust", "industrial_construction",
        "foreign_training", "foreign_weapons", "military_constructions", "foreign_officers", "army_schools", "foreign_naval_officers",
        "naval_schools", "foreign_navies"]
for f in mine:
    raw = open(f, encoding=ENC).read()
    t = strip(raw)
    kv = re.findall(r"^\s*([A-Za-z_]\w*)\s*=\s*\"?([^\s\"{}]+)", t, re.M)
    d = dict(kv)
    if d.get("civilized") != "yes":
        my_unciv_gov[d.get("government")] += 1
    for k, v in kv:
        if k not in ref_keys:
            bad_keys[k] += 1
        elif k in ENUM and v not in ref_pairs[k]:
            bad_vals[(k, v)] += 1
    # structural oddities
    for l in raw.splitlines():
        if l.strip() and not re.match(r"^\s*(#.*|[A-Za-z_]\w*\s*=\s*(\"[^\"]*\"|[^\s{}]+|\{)?\s*(#.*)?|\}|[a-z_]+\s*=\s*-?[\d\.]+)\s*$", l):
            weird[l.strip()[:60]] += 1
    if t.count("{") != t.count("}"):
        weird["BRACES " + os.path.basename(f)] += 1
    for k in ("capital", "primary_culture", "religion", "government", "ruling_party"):
        if k not in d and os.path.basename(f)[:3] not in ("TIN", "SMA", "MED", "LRG", "HUG"):
            weird["missing %s" % k] += 1
    dup = [k for k, c in collections.Counter(k for k, v in kv if k in ("capital", "government", "civilized", "ruling_party", "primary_culture", "religion", "nationalvalue", "literacy", "plurality")).items() if c > 1]
    for k in dup:
        weird["duplicate key %s" % k] += 1
print("\nmy files:", len(mine))
print("keys never used in any reference country history:", dict(bad_keys))
print("values never used in references:", dict(bad_vals))
print("structural oddities:", dict(weird.most_common(25)))
print("governments of MY uncivilized countries:", dict(my_unciv_gov))
never = {g: c for g, c in my_unciv_gov.items() if g not in unciv_gov}
print("  of which NEVER uncivilized in any reference:", never)
print("last_election lines in my uncivilized files:", sum(1 for f in mine if "last_election" in open(f, encoding=ENC).read() and "civilized = no" in open(f, encoding=ENC).read()))
