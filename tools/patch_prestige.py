"""One-off patch: the prestige defines that belong with PEACE_COST_PRESTIGE = 4000; no ticking prestige in this mod's modifiers."""
s = open("03c_statesize.py", encoding="utf-8").read()
a = '''dl, n = re.subn(r"(PEACE_COST_PRESTIGE\\s*=\\s*)[\\d\\.]+", r"\\g<1>4000", dl)
assert n == 1
'''
assert s.count(a) == 1, s.count(a)
s = s.replace(a, a + '''# Heartbreaker's fixed war-score costs work by making every sized goal a "prestige" goal that costs
# PEACE_COST_PRESTIGE x its factor. That only works with the prestige such a goal moves switched off,
# which Heartbreaker does in the same file. Without these, every state taken paid the winner
# prestige scaled by the 4000 (tens of thousands of prestige per war).
hb_dl = open(os.path.join(HB, "common", "defines.lua"), encoding=ENC, errors="replace").read()
PRESTIGE_DEFINES = ["PRESTIGE_PRESTIGE_BASE", "PRESTIGE_PRESTIGE", "PRESTIGE_REDUCTION_BASE", "PRESTIGE_REDUCTION", "INFAMY_PRESTIGE"]
copied = {}
for key in PRESTIGE_DEFINES:
    m = re.search(r"(?m)^\\s*%s\\s*=\\s*([\\d\\.]+)" % key, hb_dl)
    assert m, key
    dl, n = re.subn(r"(?m)^(\\s*%s\\s*=\\s*)[\\d\\.]+" % key, lambda x: x.group(1) + m.group(1), dl)
    assert n == 1, key
    copied[key] = m.group(1)
assert float(copied["PRESTIGE_PRESTIGE"]) == 0 and float(copied["PRESTIGE_PRESTIGE_BASE"]) == 0
print("prestige defines taken from Heartbreaker:", copied)
''')
open("03c_statesize.py", "w", encoding="utf-8").write(s)

g = open("03_gameplay.py", encoding="utf-8").read()
a = '''def mod(key, name, desc, icon=5, **kw):
    MODS[key] = (kw, icon)
'''
assert g.count(a) == 1
g = g.replace(a, '''def mod(key, name, desc, icon=5, **kw):
    # no modifier of this mod gives prestige over time: prestige comes once, from the decision itself
    kw = {k_: v_ for k_, v_ in kw.items() if k_ != "prestige"}
    assert kw, key
    MODS[key] = (kw, icon)
''')
a = '''def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):
    effect = _map_cultures(effect)
'''
assert g.count(a) == 1
g = g.replace(a, a + '''    for _v in re.findall(r"(?m)^\\s*prestige\\s*=\\s*(-?[\\d\\.]+)", effect):       # a one-time gift above 100 is reserved for nothing at all
        assert abs(float(_v)) <= 100, (key, _v)
''')
open("03_gameplay.py", "w", encoding="utf-8").write(g)
print("patched")
