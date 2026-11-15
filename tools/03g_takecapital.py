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
# NOT with two conditions means "neither of them", so the two must sit inside an AND: without it this
# line forbade every war goal against any uncivilized country at all.
SHIELD = "\n\t\tNOT = {\n\t\t\tAND = {\n\t\t\t\ttag = HRE\n\t\t\t\tcivilized = no\n\t\t\t}\n\t\t}"

# Free Peoples goes: its "who to free" list offered the five state-size marker tags, which have a core
# on every province in the world but are not countries, and pointing at one crashed the game. The
# five sized versions are removed outright; the original stays in the file, never usable, so nothing
# that names it by key is left dangling.
def _block(text, name):
    m_ = re.search(r"(?m)^%s\s*=\s*\{" % name, text)
    if not m_:
        return None
    d_, j_ = 1, m_.end()
    while d_:
        if text[j_] == "#":
            j_ = text.index("\n", j_)
            continue
        d_ += text[j_] == "{"
        d_ -= text[j_] == "}"
        j_ += 1
    return m_.start(), j_


n_lists = 0      # no other list is touched: only free peoples offered the marker tags, and FROM does not exist in every list
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
    if cu and m.group(1) not in ("status_quo", "civil_war", "become_independent", "free_peoples"):
        body = body[:cu.end()] + SHIELD + body[cu.end():]
        shielded.append(m.group(1))
    else:
        skipped.append(m.group(1))
    out.append(cb[i:m.start()] + body)
    i = j
cb = "".join(out) + cb[i:]
wr("common/cb_types.txt", cb)
print("war goals that cannot be fabricated on an unwesternized HRE: %d | left alone: %d" % (len(shielded), len(skipped)))
assert "free_peoples_tiny" not in cb and cb.count("{") == cb.count("}"), "war goal file is unbalanced"
assert re.search(r"(?s)free_peoples = \{.*?always = no", cb), "free peoples must stay switched off"
for m in re.finditer(r"NOT\s*=\s*\{\s*tag\s*=\s*HRE\s*civilized", cb):
    raise SystemExit("the HRE shield is written without AND")
print("free peoples is switched off and has no sized versions")
# the protectorate goal (a civilized country against a small uncivilized one) must be vanilla's, plus the HRE shield only
import difflib
def _one(text, name):
    m_ = re.search(r"(?m)^%s\s*=\s*\{" % name, text)
    d_, j_ = 1, m_.end()
    while d_:
        d_ += text[j_] == "{"
        d_ -= text[j_] == "}"
        j_ += 1
    return [l.strip() for l in re.sub(r"#.*", "", text[m_.start():j_]).split("\n") if l.strip()]
_v = _one(rd("common", "cb_types.txt").replace("\r\n", "\n"), "establish_protectorate_casus_belli")
_m = _one(cb, "establish_protectorate_casus_belli")
_extra = [l[2:] for l in difflib.ndiff(_v, _m) if l[:2] in ("+ ", "- ")]
assert _extra == ["NOT = {", "AND = {", "tag = HRE", "civilized = no", "}", "}"], _extra
print("establish protectorate: vanilla's rules, usable by civilized countries on small uncivilized ones")
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


# ---- Heartbreaker's money injection (events/money.txt): on the first day every country's treasury is
# topped up so the game does not open with a world of bankrupt states. Heartbreaker's event is fired by
# its ghost country GHO and gives 250,000 to great powers and 100,000 to everyone else; here the World
# Bank fires it (the one country that always exists) and every country gets the 250,000.
ev = open(os.path.join(H, "events", "money.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
assert ev.count("tag = GHO") == 1 and ev.count("treasury = 250000") == 1 and ev.count("treasury = 100000") == 1
ev = ev.replace("tag = GHO", "tag = WBK")
a_ = ev.index("any_country = {")
b_ = ev.rindex("}", 0, ev.rindex("}", 0, ev.rindex("}")))        # end of the second any_country block
ev = ev[:a_] + "any_country = {\n\t\t\ttreasury = 250000\n\t\t}\n\t" + ev[b_ + 1:].lstrip("\n")
assert ev.count("{") == ev.count("}") and "is_greater_power" not in ev and ev.count("treasury = 250000") == 1, ev
eid = re.search(r"id\s*=\s*(\d+)", ev).group(1)
for f in glob.glob(os.path.join(OUT, "events", "*.txt")):
    if os.path.basename(f) != "money.txt":
        assert not re.search(r"\bid\s*=\s*%s\b" % eid, open(f, encoding=ENC, errors="replace").read()), f
assert re.search(r"(?m)^WBK\s*=", open(os.path.join(OUT, "common", "countries.txt"), encoding=ENC).read())
wr("events/money.txt", ev)
print("money injection from Heartbreaker: event", eid, "- 250,000 to every country on day one")
