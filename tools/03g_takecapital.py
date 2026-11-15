"""Stage 3g: the "take capital" war goal from DoD Heartbreaker MP 4.9.5.

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
cb = cb.rstrip() + "\n\n# from DoD Heartbreaker MP 4.9.5\n" + block + "\n"

# Heartbreaker shields its China from fabricated war goals. Here the cliques are fair game for each
# other, so nothing of that is kept; the shield goes to the Holy Roman Empire instead, for as long as
# it has not westernized. It covers every war goal except the three that end or answer a war
# (status quo, civil war, independence), so it cannot be attacked by decision-granted goals either.
for word in ("tag = CHI", "is_culture_group = east_asian", "substate_of = CHI"):
    for ln in cb.split("\n"):
        assert not (word in ln and "NOT" in ln), ("a war goal still shields China", ln)
SHIELD = "\n\t\tNOT = {\n\t\t\ttag = HRE\n\t\t\tcivilized = no\n\t\t}"
out, i, shielded, skipped = [], 0, [], []
for m in re.finditer(r"(?m)^(\w+)\s*=\s*\{", cb):
    if m.start() < i or m.group(1) == "peace_order":
        continue
    d, j = 1, m.end()
    while d:
        if cb[j] == "#":
            j = cb.index("\n", j)
            continue
        d += cb[j] == "{"
        d -= cb[j] == "}"
        j += 1
    body = cb[m.start():j]
    bare = re.sub(r"#.*", "", body)
    cu = re.search(r"(?m)^\tcan_use\s*=\s*\{", body)
    if cu and m.group(1) not in ("status_quo", "civil_war", "become_independent"):
        body = body[:cu.end()] + SHIELD + body[cu.end():]
        shielded.append(m.group(1))
    else:
        skipped.append(m.group(1))
    out.append(cb[i:m.start()] + body)
    i = j
cb = "".join(out) + cb[i:]
wr("common/cb_types.txt", cb)
print("war goals that cannot be fabricated on an unwesternized HRE: %d | left alone: %d" % (len(shielded), len(skipped)))
lr = {}
for f in sorted(glob.glob(os.path.join(H, "localisation", "*.csv"))):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        q = l.split(";")
        if len(q) > 1 and q[0] and q[0] not in lr:
            lr[q[0]] = q[1]
keys = ["take_capital", "take_capital_desc", "take_capital_setup", "take_capital_short"]
assert all(lr.get(k) for k in keys)
wr("localisation/00_warlord_era_takecapital.csv", "\n".join("%s;%s;;;;;;;;;;;;;x" % (k, lr[k]) for k in keys) + "\n")
used = set(re.findall(r"casus_belli\s*=\s*\{[^}]*?type\s*=\s*(\w+)", open(os.path.join(OUT, "decisions", "WarlordEra.txt"), encoding=ENC).read()))
have = set(re.findall(r"(?m)^(\w+)\s*=\s*\{", cb)) | {"take_capital"}
assert used <= have, ("decisions grant a war goal that does not exist", used - have)
print("take_capital war goal from Heartbreaker added | war goals granted by decisions:", sorted(used))
