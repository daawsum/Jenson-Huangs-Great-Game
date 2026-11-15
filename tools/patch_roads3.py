"""One-off patch: write the modifier file after every modifier is defined; report claim tags with no land."""
import json, collections
s = open("03_gameplay.py", encoding="utf-8").read()
a = r'''em = rd("common", "event_modifiers.txt") + "\n\n##### WARLORD ERA #####\n"
for k, (kw, icon) in MODS.items():
    em += "%s = {\n%s\ticon = %d\n}\n\n" % (k, "".join("\t%s = %s\n" % (a, b) for a, b in kw.items()), icon)
wr("common/event_modifiers.txt", em)
'''
if s.count(a) == 1:
    s = s.replace(a, r'''def write_modifiers():
    em = rd("common", "event_modifiers.txt") + "\n\n##### WARLORD ERA #####\n"
    for k, (kw, icon) in MODS.items():
        em += "%s = {\n%s\ticon = %d\n}\n\n" % (k, "".join("\t%s = %s\n" % (a, b) for a, b in kw.items()), icon)
    wr("common/event_modifiers.txt", em)


write_modifiers()
''')
    c = 'print("clique roads:", dict(ROAD_REPORT))\n'
    assert s.count(c) == 1
    s = s.replace(c, c + 'write_modifiers()          # again: the roads above define their own modifiers\n')
    open("03_gameplay.py", "w", encoding="utf-8").write(s)
    print("patched")
W = json.load(open("work/world.json"))
n = collections.Counter(W["owner"].values())
from content import ROADS
tags = sorted({c for o in ROADS.values() for x in o for c in x[2] if c != "SIBERIA"})
print("claim tags without land:", [t for t in tags if not n.get(t)])
print("south east asia owners:", {t: n[t] for t in ("SIA", "DAI", "BUR", "CAM", "LUA", "JOH", "ATJ", "BRU", "BAL", "JAV", "PHI", "KOR", "KOK", "BUK", "KHI", "JAP")})
