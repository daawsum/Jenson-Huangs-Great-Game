"""One-off (v3): do not rely on replace_path. In game, vanilla's PuppetStates.txt was still being
applied (cliques showed as substates of China), so every vanilla history file that must not
apply is now overridden by a mod file with the SAME NAME."""
s = open("02_world.py", encoding="utf-8").read()
if "VBASE" in s:
    raise SystemExit("already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


# 1 province files keep vanilla's exact file name (a few vanilla names have no dash)
rep('''vprov = {}
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    mm = re.match(r"\\s*(\\d+)", os.path.basename(f))
    if not mm:
        continue
''', '''vprov = {}
VBASE = {}          # province id -> vanilla's own file name, so a mod file always overrides it by name
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    mm = re.match(r"\\s*(\\d+)", os.path.basename(f))
    if not mm:
        continue
    VBASE[int(mm.group(1))] = os.path.basename(f)
''')
rep('''    wr("history/provinces/%s/%d - %s.txt" % (PFOLDER[p], p, re.sub(r'[\\\\/:*?"<>|]', "", PNAME[p])), "\\n".join(L) + "\\n")''',
    '''    fname = VBASE.get(p) or "%d - %s.txt" % (p, re.sub(r'[\\\\/:*?"<>|]', "", PNAME[p]))
    wr("history/provinces/%s/%s" % (PFOLDER[p], fname), "\\n".join(L) + "\\n")''')

# 2 diplomacy and wars: one harmless file for every vanilla file name
a = s[s.index('wr("history/diplomacy/Alliances.txt"'):s.index("# ------------------------------------------------------------------ states of China")]
rep(a, r'''# No starting alliances, unions, guarantees or substates. Vanilla's files are overridden one by one
# by name: in testing, replace_path alone did not stop PuppetStates.txt from making the cliques
# substates of a China that does not exist.
for f in glob.glob(os.path.join(V, "history", "diplomacy", "*.txt")):
    wr("history/diplomacy/" + os.path.basename(f), "# Warlord Era: nothing here on purpose\n")
# Wars: the folder must hold real war files or the game crashes on start, and none may be active
# in 1836. Every vanilla war file name gets a copy of a war that ended in 1783.
_old = rd("history", "wars", "AmericanWarOfIndependence.txt")
for f in glob.glob(os.path.join(V, "history", "wars", "*.txt")):
    nm = os.path.basename(f)
    wr("history/wars/" + nm, _old if nm == "AmericanWarOfIndependence.txt" else _old.replace("American War of Independence", "Old War (%s)" % nm[:-4]))

''')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched")
