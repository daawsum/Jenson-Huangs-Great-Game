"""One-off: make the World Bank and the state size flags switchable from config.py (both off)."""
import re


def edit(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        assert a in s, (path, a)
        s = s.replace(a, b, 1)
    open(path, "w", encoding="utf-8").write(s)


c = open("config.py", encoding="utf-8").read()
if "WORLD_BANK" not in c:
    c = c.replace('ENC = "cp1252"\n', 'ENC = "cp1252"\nWORLD_BANK = False     # IGoR-style bank country on the Falklands with gold-mining bankers\nSTATE_FLAGS = False    # Tiny/Small/Medium/Large/Huge State marker tags and size-split war goals\n', 1)
    open("config.py", "w", encoding="utf-8").write(c)

edit("02_world.py", [
    ("WBK_PROVS = [2131, 2133]\n", "WBK_PROVS = [2131, 2133] if WORLD_BANK else []\n"),
    ("            if p == 2131:\n                body = BANK_POPS\n", "            if p == 2131 and WORLD_BANK:\n                body = BANK_POPS\n"),
    ("if popsize[2131] == 0:\n", "if WORLD_BANK and popsize[2131] == 0:\n"),
    ('    if p == 2131:\n        goods = "precious_metal"\n    elif goods == "precious_metal":',
     '    if p == 2131 and WORLD_BANK:\n        goods = "precious_metal"\n    elif goods == "precious_metal" and WORLD_BANK:'),
    ("add.append('WBK\\t\\t= \"countries/WE_WBK.txt\"')\n", "if WORLD_BANK:\n    add.append('WBK\\t\\t= \"countries/WE_WBK.txt\"')\n"),
])
s = open("02_world.py", encoding="utf-8").read()
if "remove World Bank leftovers" not in s:
    s += '''
# remove World Bank leftovers when it is switched off (the tag is then not in countries.txt)
if not WORLD_BANK:
    for rel in ["common/countries/WE_WBK.txt", "history/countries/WBK - World Bank.txt", "history/units/WBK_oob.txt"] + \\
               ["gfx/flags/WBK%s.tga" % x for x in ["", "_communist", "_fascist", "_monarchy", "_republic"]]:
        p_ = os.path.join(OUT, rel)
        if os.path.exists(p_):
            os.remove(p_)
'''
    open("02_world.py", "w", encoding="utf-8").write(s)

for path, flag in (("03b_worldbank.py", "WORLD_BANK"), ("03c_statesize.py", "STATE_FLAGS")):
    t = open(path, encoding="utf-8").read()
    if "raise SystemExit(0)" not in t:
        t = t.replace("from config import *\n", "from config import *\n\nif not %s:\n    print(\"%s is switched off in config.py; skipped\")\n    raise SystemExit(0)\n" % (flag, flag), 1)
        open(path, "w", encoding="utf-8").write(t)

r = open("05_package.py", encoding="utf-8").read()
a = r[r.index("  - World Bank: a neutral dummy country"):r.index("  - Map look: Belle Cartographie Dark.")]
r = r.replace(a, "").replace("  World Bank and state sizing adapted from IGoR puir.\n", "")
open("05_package.py", "w", encoding="utf-8").write(r)
print("patched")
