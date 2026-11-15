"""One-off patch: the Warlord Claim war goal is removed; stray Ottoman provinces go back to the Ottomans."""
import re

s = open("03_gameplay.py", encoding="utf-8").read()
a = s.index("# ------------------------------------------------------------------ war goals between warlords")
b = s.index("# ------------------------------------------------------------------ modifiers")
s = s[:a] + s[b:]
assert "warlord_take_state" not in s and "cb_types" not in s[:b]
open("03_gameplay.py", "w", encoding="utf-8").write(s)

s = open("03c_statesize.py", encoding="utf-8").read()


def rep(x, y):
    global s
    assert s.count(x) == 1, (x[:70], s.count(x))
    s = s.replace(x, y)


rep('''    "warlord_take_state": [0.002, 0.004, 0.006, 0.009, 0.012],          # this mod's own war goal\n''', "")
rep('''for fam in ("warlord_take_state", "unification_casus_belli"):''', '''for fam in ("unification_casus_belli",):''')
rep('''for fam in HB_FAMILIES + ["warlord_take_state", "unification_casus_belli"]:''', '''for fam in HB_FAMILIES + ["unification_casus_belli"]:''')
rep(r'''            "\xa7YWarlord Claim: \xa7W%d%% Warscore\\n\xa7YAcquire Core: \xa7W%d%% Warscore\\n\xa7YAcquire State: \xa7W%d%% Warscore\\n"''',
    r'''            "\xa7YAcquire Core: \xa7W%d%% Warscore\\n\xa7YAcquire State: \xa7W%d%% Warscore\\n"''')
rep('''name, rng(ERAS[0][3]), rng(ERAS[1][3]), rng(ERAS[2][3]), cost("warlord_take_state", i), cost("acquire_core_state", i),''',
    '''name, rng(ERAS[0][3]), rng(ERAS[1][3]), rng(ERAS[2][3]), cost("acquire_core_state", i),''')
s = s.replace("this mod's own goal between cliques and vanilla's unification goal", "vanilla's unification goal")
open("03c_statesize.py", "w", encoding="utf-8").write(s)

p = open("05_package.py", encoding="utf-8").read()
m = re.search(r'  - Any clique can always declare "Warlord Claim"[^\n]*\n[^\n]*\n', p)
assert m
p = p[:m.start()] + "  - Wars between cliques need a justified war goal; taking a state costs war score by the\n    state's size flag (Tiny to Huge).\n" + p[m.end():]
open("05_package.py", "w", encoding="utf-8").write(p)

w = open("02_world.py", encoding="utf-8").read()
x = '''print("provinces merged into the Ottoman Empire: %d | Iraq to Persia: %d" % tuple(_n))'''
assert w.count(x) == 1
w = w.replace(x, '''# Ottoman land that the "empty the African holdings of the great powers" rule had left unowned
# (Deir ez-Zor on the Persian border counts as Africa in vanilla's continent file; Tobruk too)
_stray = [p for p in ALLP if p in vprov and vprov[p]["owner"] == "TUR" and owner.get(p) is None]
for p in _stray:
    owner[p] = "TUR"
print("ottoman provinces that had been left empty:", [(p, PNAME[p]) for p in _stray])
''' + x)
open("02_world.py", "w", encoding="utf-8").write(w)
print("patched")
