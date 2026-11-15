"""One-off: the mod's display name. The folder and .mod file keep their names, because the map's
definition path and every player's install path are built from the folder name."""
NAME = "Jenson Huang's Great Game"
c = open("config.py", encoding="utf-8").read()
if "MOD_NAME" not in c:
    c = c.replace('MOD_DIR = "Warlord Era"', 'MOD_NAME = "%s"   # what the launcher and the lobby show\nMOD_DIR = "Warlord Era"' % NAME, 1)
    assert "MOD_NAME" in c
    open("config.py", "w", encoding="utf-8").write(c)
s = open("02_world.py", encoding="utf-8").read()
a = '''wr("../Warlord Era.mod", 'name = "Warlord Era"\\n'''
assert a in s, "mod line"
s = s.replace(a, '''wr("../Warlord Era.mod", 'name = "' + MOD_NAME + '"\\n''', 1)
a = 'loc("GC_NAME", "The Warlord Era")'
assert a in s
s = s.replace(a, 'loc("GC_NAME", MOD_NAME)', 1)
open("02_world.py", "w", encoding="utf-8").write(s)
r = open("05_package.py", encoding="utf-8").read()
a = "WARLORD ERA - a Victoria 2"
assert a in r
r = r.replace(a, "JENSON HUANG'S GREAT GAME - a Victoria 2", 1)
r = r.replace('tick "Warlord Era" in the launcher', 'tick "Jenson Huang\'s Great Game" in the launcher', 1)
open("05_package.py", "w", encoding="utf-8").write(r)
print("renamed to", NAME)
