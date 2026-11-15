"""One-off: checker severity. Only failures that were isolated in the running game stay PROBLEMS;
everything else becomes a WARNING, because working mods (GFM, HPM, Vae Victis) trip them."""
import re
p = r"..\victoria2-modding\scripts\check_mod.py"
s = open(p, encoding="utf-8").read()
keep_problem = ["definitions must be", "max_provinces =", "almost no population", "can westernize on day one",
                "fleet starts in province", "holds no real war file", "game_intro.bik is missing", "no .mod file in mod/"]
out, n = [], 0
for line in s.split("\n"):
    m = re.match(r"^(\s*)P\(", line)
    if m and not any(k in line for k in keep_problem):
        line = line.replace("P(", "W(", 1)
        n += 1
    out.append(line)
s = "\n".join(out)
# default.map: ignore commented-out lines (GFM keeps a commented definitions line above the real one)
a = '    dm = read(eff("map", "default.map"))\n'
assert a in s
s = s.replace(a, '    dm = strip(read(eff("map", "default.map")))\n')
# civilized count: 1 crashed, 7 worked
a = '''    if civilized < 8:
        W("only %d civilized countries exist at start; the game crashed on Play with 1 and worked with 7+" % civilized)'''
assert a in s, "civ"
s = s.replace(a, '''    if civilized < 2:
        P("only %d civilized countries exist at start: pressing Play crashed with 0 and with 1" % civilized)
    elif civilized < 7:
        W("only %d civilized countries exist at start; 1 crashed on Play and 7 worked, in between is untested" % civilized)''')
s = s.replace("is not active at the start date (crashes at Executing History)", "is not active at the start date (vanilla never does this for a country that exists at start)")
s = s.replace("does not exist in this game (crashes at launch)", "does not exist in this game")
s = s.replace('''Prints PROBLEMS (likely to crash or break something) and WARNINGS (worth a look).''',
              '''PROBLEMS are failures that were isolated in the running game (each one crashed it or broke the
map). WARNINGS are departures from what vanilla does; working mods trip some of them, so read
them as "check this", not "this is broken".''')
open(p, "w", encoding="utf-8").write(s)
print("downgraded", n, "checks to warnings")
