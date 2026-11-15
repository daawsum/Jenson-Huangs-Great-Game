"""Research: how Heartbreaker's cb_types.txt differs from this mod's, and what it depends on."""
import os, re, glob, collections
from config import *

H = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
strip = lambda t: re.sub(r"#.*", "", t)
hb = strip(open(os.path.join(H, "common", "cb_types.txt"), encoding=ENC, errors="replace").read())
mine = strip(open(os.path.join(OUT, "common", "cb_types.txt"), encoding=ENC).read())
van = strip(rd("common", "cb_types.txt"))


def parts(t):
    out = collections.OrderedDict()
    for k, b, s, e in blocks(t):
        out[k] = b
    return out


ph, pm, pv = parts(hb), parts(mine), parts(van)
print("war goals: heartbreaker %d, mine %d, vanilla %d" % (len(ph) - 1, len(pm) - 1, len(pv) - 1))
print("only heartbreaker:", [k for k in ph if k not in pm])
print("only mine:", [k for k in pm if k not in ph])
# where the size marker is tested
for name in ("acquire_state_small", "acquire_core_state_small", "place_in_the_sun_small", "demand_concession_casus_belli_small", "unification_casus_belli_small"):
    for lab, p in (("HB", ph), ("ME", pm)):
        b = p.get(name)
        if b is None:
            print(lab, name, "absent")
            continue
        sec = {}
        for k, bb, s, e in blocks(b):
            sec[k] = bb
        print(lab, name, "| is_triggered_only", re.findall(r"is_triggered_only\s*=\s*(\w+)", b)[:1], "| constructing_cb", re.findall(r"constructing_cb\s*=\s*(\w+)", b)[:1],
              "| SMA in can_use:", "SMA" in sec.get("can_use", ""), "| in allowed_states:", "SMA" in sec.get("allowed_states", ""),
              "| in allowed_countries:", "SMA" in sec.get("allowed_countries", ""), "| sections:", [k for k in sec])
print("--- HB acquire_state_small in full:")
print(ph["acquire_state_small"][:1800])
print("--- MINE acquire_state_small in full:")
print(pm["acquire_state_small"][:1800])
# dependencies of the heartbreaker file
tags = collections.Counter(re.findall(r"\b([A-Z][A-Z0-9]{2})\b", hb))
ct = open(os.path.join(OUT, "common", "countries.txt"), encoding=ENC).read()
have = set(re.findall(r"(?m)^(\w{3})\s*=", ct))
print("tags heartbreaker's file names that this mod lacks:", {t: n for t, n in tags.items() if t not in have and t not in ("NOT", "AND", "THIS", "FROM", "WAR", "ALL")})
print("flags:", collections.Counter(re.findall(r"has_(?:country|global)_flag\s*=\s*(\w+)", hb)).most_common(20))
print("modifiers:", collections.Counter(re.findall(r"has_country_modifier\s*=\s*(\w+)", hb)).most_common(10))
toks = collections.Counter(re.findall(r"([a-z_]+)\s*=", hb))
vt = set(re.findall(r"([a-z_]+)\s*=", van))
print("keys heartbreaker uses that vanilla's file never does:", {k: n for k, n in toks.items() if k not in vt and k not in ph})
techs = set()
for f in glob.glob(os.path.join(OUT, "technologies", "*.txt")) + glob.glob(os.path.join(OUT, "inventions", "*.txt")):
    techs |= {k for k, b, s, e in blocks(strip(open(f, encoding=ENC, errors="replace").read()))}
print("technologies/inventions it names that this mod lacks:", sorted({k for k in re.findall(r"(?:invention\s*=\s*|\b)(\w+)\s*=\s*1\b", hb) if k not in techs and not k.isdigit()})[:20])
lh = set()
for f in glob.glob(os.path.join(H, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        lh.add(l.split(";")[0])
print("heartbreaker war goals without their own name in its localisation:", [k for k in ph if k != "peace_order" and k not in lh][:10])
lm = set()
for f in glob.glob(os.path.join(OUT, "localisation", "*.csv")) + glob.glob(os.path.join(V, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        lm.add(l.split(";")[0])
print("MY war goals without a name anywhere:", [k for k in pm if k != "peace_order" and k not in lm][:20])
print("MY war goals missing _short/_desc/_setup:", [k + s for k in pm if k != "peace_order" for s in ("_short", "_desc", "_setup") if k + s not in lm][:30])
