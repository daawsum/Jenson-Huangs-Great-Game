"""One-off patch of 03d_focus.py: focus tiers unlock the way RobloxDoD / Heartbreaker do it."""
p = "03d_focus.py"
s = open(p, encoding="utf-8").read()
a = s.index("# tier unlocks: IGoR's event, with a date instead of its inventions")
new = r'''# tier unlocks, exactly as RobloxDoD 1.8 and DoD Heartbreaker do it (their files are identical):
#   technology (associationism, experimental_psychology, psychological_intelligence, psychoanalysis,
#   behaviorism) -> invention pop_shift_invention_2..6 (inventions/pop_shift_psychology_inventions.txt,
#   copied by 03a_tech.py) -> event 370032..370036 "Thank you, Reno!" sets country flag tier_2..6
#   -> common/national_focus.txt lists a focus only with that flag.
RB = os.path.join(V, "mod", "RobloxDOD 1.8")
flags = open(os.path.join(RB, "events", "national_focus_flags.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
wr("events/national_focus_flags.txt", flags)
inv = ""
for f in glob.glob(os.path.join(OUT, "inventions", "*.txt")):
    inv += re.sub(r"#.*", "", open(f, encoding=ENC, errors="replace").read())
techs = set()
for f in glob.glob(os.path.join(OUT, "technologies", "*.txt")):
    techs |= {k for k, b, s_, e_ in blocks(re.sub(r"#.*", "", open(f, encoding=ENC, errors="replace").read()))}
chain = {}
for iv, fl in re.findall(r"invention\s*=\s*(\w+)\s*NOT\s*=\s*\{\s*has_country_flag\s*=\s*(\w+)", re.sub(r"#.*", "", flags)):
    m = re.search(r"(?m)^%s\s*=\s*\{\s*limit\s*=\s*\{\s*(\w+)\s*=\s*1" % iv, inv)
    assert m, "invention %s is not in this mod" % iv
    assert m.group(1) in techs, m.group(1)
    assert "set_country_flag = %s" % fl in flags and "has_country_flag = %s" % fl in clean, fl
    chain[fl] = "%s -> %s" % (m.group(1), iv)
assert sorted(chain) == ["tier_%d" % i for i in range(2, 7)], chain
mine = ""
for f in glob.glob(os.path.join(OUT, "events", "*.txt")):
    if os.path.basename(f) != "national_focus_flags.txt":
        mine += open(f, encoding=ENC, errors="replace").read()
for i in re.findall(r"\bid\s*=\s*(\d+)", flags):
    assert not re.search(r"\bid\s*=\s*%s\b" % i, mine), i
assert os.path.exists(os.path.join(V, "gfx", "pictures", "events", "troy.tga"))
rl = {}
for f in sorted(glob.glob(os.path.join(RB, "localisation", "*.csv"))):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        q = l.split(";")
        if len(q) > 1 and q[0] and q[0] not in rl:
            rl[q[0]] = q[1]
for k in re.findall(r'(?:title|desc)\s*=\s*"(\w+)"', flags):
    assert rl.get(k), k
    lines.append("%s;%s;;;;;;;;;;;;;x" % (k, rl[k].replace(";", ",")))
wr("localisation/00_warlord_era_focus.csv", "\n".join(lines) + "\n")
print("national focus tiers unlock by:", chain)
'''
s = s[:a] + new
open(p, "w", encoding="utf-8").write(s)
print("patched; check that focus names are no longer written twice")
