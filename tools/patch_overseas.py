"""One-off patch: overseas holdings of Taiwan and Shanghai, Taiwan's heritage and claim, infamy for claims."""
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep(r'''EMPTIED = {p for p in ALLP if owner[p] is None''', r'''# The two island traders start with footholds overseas.
OVERSEAS = {
    "TWN": [1397,                              # Sandakan, North Borneo
            2127],                             # Seychelles
    "SHG": [658,                               # Hawaii
            2125,                              # Mauritius
            1321, 1322, 1323, 1324, 1325, 2128],   # all of the Ceylon state: Colombo, Jaffna, Kandy, Trincomalee, Maldives, Diego Garcia
}
for _t, _ps in OVERSEAS.items():
    for p in _ps:
        assert p in vprov and p not in CHINA, p
        owner[p] = _t

EMPTIED = {p for p in ALLP if owner[p] is None''')
rep(r'''    assert {CN_MINERALS.get(q) for q in ALLP if owner[q] == _t} <= {"coal", "iron", "sulphur"}, _t''',
    r'''    assert {CN_MINERALS.get(q) for q in ALLP if owner[q] == _t and q in CHINA} <= {"coal", "iron", "sulphur"}, _t''')
# Taiwan's home port is a large naval station: in this engine the naval limit comes from base levels
rep(r'''        if "naval_base" not in t:
            open(path, "w", encoding=ENC, newline="\r\n").write(t + "naval_base = 1\n")''',
    r'''        lvl = 3 if tag == "TWN" else 1
        t = re.sub(r"(?m)^naval_base = \d+\n", "", t)
        open(path, "w", encoding=ENC, newline="\r\n").write(t + "naval_base = %d\n" % lvl)''')
open("02_world.py", "w", encoding="utf-8").write(s)

s = open("03_gameplay.py", encoding="utf-8").read()
rep(r'''def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):
    effect = _map_cultures(effect)
''', r'''def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):
    effect = _map_cultures(effect)
    # claiming land or a war goal by decree is noticed: 2 infamy for cores on foreign land, 1 for a casus belli
    bb = 2 * bool(re.search(r"add_core\s*=\s*THIS", effect)) + bool(re.search(r"\bcasus_belli\s*=", effect))
    if bb:
        effect = effect.rstrip("\n") + "\nbadboy = %d" % bb
        desc = "%s (+%d infamy)" % (desc, bb)
        INFAMY[bb] += 1
''')
rep(r'''HIDDEN = collections.Counter()
''', r'''HIDDEN = collections.Counter()
INFAMY = collections.Counter()
''')
rep(r'''NO_TECH = {"open_nanyang_ports"}''', r'''NO_TECH = {"open_nanyang_ports", "taiwan_claims"}''')
rep(r'''# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''', r'''# ---- Taiwan: available from the first day
_hainan = sorted(p for p, o in OWNER.items() if o == "HNI")
assert _hainan
once("taiwan_claims", "The Two Islands and the River Mouth", "Hainan is Formosa's sister island, and whoever holds Shanghai holds the trade of the Yangtze. Claim Hainan as our own and prepare to take Shanghai itself.",
     "tag = TWN", "war = no",
     "".join("%d = { add_core = THIS }\n" % p for p in _hainan) + "casus_belli = { target = SHG type = take_capital months = 120 }")

# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''')
rep(r'''mod("taiwanese_dream", "The Taiwanese Dream",''', r'''mod("taiwanese_maritime_heritage", "Taiwanese Maritime Heritage", "Formosa has lived by the sea since Koxinga's fleets: its captains, its yards and its navigators are the best in the China seas.",
    leadership=2, research_points_modifier=0.25, naval_organisation=0.1)
mod("taiwanese_dream", "The Taiwanese Dream",''')
rep(r'''setup("tag = TWN", "taiwanese_dream", "The Taiwanese Dream",''', r'''setup("tag = TWN", "taiwanese_maritime_heritage", "Taiwanese Maritime Heritage",
      "Formosa has lived by the sea since Koxinga's fleets. Our captains and navigators are the best in the China seas, and the great naval station at our capital can keep a fleet far larger than an island this size should.")
setup("tag = TWN", "taiwanese_dream", "The Taiwanese Dream",''')
rep(r'''print("hidden until prerequisites are met:''', r'''print("decisions that now give infamy: +1 (casus belli) %d, +2 (cores) %d, +3 (both) %d" % (INFAMY[1], INFAMY[2], INFAMY[3]))
print("hidden until prerequisites are met:''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)

open("03g_takecapital.py", "w", encoding="utf-8").write(r'''"""Stage 3g: the "take capital" war goal from DoD Heartbreaker MP 4.9.5.

Heartbreaker's take_capital block is copied unchanged except for three lines that name tags this
mod does not have or uses differently (LCT, GHO, and Heartbreaker's rule that China may neither use
it nor be its target). It can only be granted by a decision or event (is_triggered_only).
Run after 03c_statesize.py, which writes common/cb_types.txt.
"""
import os, re, glob
from config import *

H = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
if not os.path.isdir(H):
    raise SystemExit("DoD Heartbreaker MP 4.9.5 is not installed")
hb = open(os.path.join(H, "common", "cb_types.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
m = re.search(r"(?m)^take_capital\s*=\s*\{", hb)
d, j = 1, m.end()
while d:
    if hb[j] == "#":
        j = hb.index("\n", j)
        continue
    d += hb[j] == "{"
    d -= hb[j] == "}"
    j += 1
block = hb[m.start():j]
for line in ("NOT = { tag = LCT }", "NOT = { tag = GHO }", "NOT = { tag = CHI }", "this = { NOT = { tag = CHI } }"):
    block, n = re.subn(r"(?m)^[ \t]*%s[ \t]*\n" % re.escape(line), "", block)
    assert n == 1, line
assert not re.search(r"\b(LCT|GHO)\b", block)
p = os.path.join(OUT, "common", "cb_types.txt")
cb = open(p, encoding=ENC).read().replace("\r\n", "\n")
assert not re.search(r"(?m)^take_capital\s*=", cb)
po = re.search(r"(?m)^peace_order\s*=\s*\{", cb)
cb = cb[:po.end()] + "\n\ttake_capital" + cb[po.end():]
wr("common/cb_types.txt", cb.rstrip() + "\n\n# from DoD Heartbreaker MP 4.9.5\n" + block + "\n")
lr = {}
for f in sorted(glob.glob(os.path.join(H, "localisation", "*.csv"))):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        q = l.split(";")
        if len(q) > 1 and q[0] and q[0] not in lr:
            lr[q[0]] = q[1]
keys = ["take_capital", "take_capital_desc", "take_capital_setup", "take_capital_short"]
assert all(lr.get(k) for k in keys)
wr("localisation/00_warlord_era_takecapital.csv", "\n".join("%s;%s;;;;;;;;;;;;;x" % (k, lr[k]) for k in keys) + "\n")
used = set(re.findall(r"type\s*=\s*(\w+)", open(os.path.join(OUT, "decisions", "WarlordEra.txt"), encoding=ENC).read()))
have = set(re.findall(r"(?m)^(\w+)\s*=\s*\{", cb)) | {"take_capital"}
assert used <= have, ("decisions grant a war goal that does not exist", used - have)
print("take_capital war goal from Heartbreaker added | war goals granted by decisions:", sorted(used))
''')
b = open("build.sh", encoding="utf-8").read()
if "03g_takecapital" not in b:
    b = b.replace("python 03c_statesize.py", "python 03c_statesize.py\npython 03g_takecapital.py")
    open("build.sh", "w", encoding="utf-8", newline="\n").write(b)
print("patched")
