"""Stage 3d: IGoR puir's tiered national focuses.

Copied verbatim from the IGoR mod on this machine: its national_focus.txt, the 67-frame focus
icon strips, and the focus names. IGoR unlocks tiers 2-6 through its own inventions; this mod
has vanilla technology, so the tiers unlock by date for civilized countries instead.
Run after 03_gameplay.py.
"""
import os, re, glob, shutil
from config import *

IG = os.path.join(V, "mod", "IGoR_puir 13.0.4 (Naval Cap+OSC)")
if not os.path.isdir(IG):
    raise SystemExit("IGoR puir is not installed; cannot port its national focuses")

nf = open(os.path.join(IG, "common", "national_focus.txt"), encoding=ENC, errors="replace").read()

# every key the focuses use must mean something to vanilla (pop types, goods, modifiers, triggers)
goods = set(re.findall(r"^\t(\w+)\s*=\s*\{", re.sub(r"#.*", "", rd("common", "goods.txt")), re.M))
pops = {os.path.basename(f)[:-4] for f in glob.glob(os.path.join(V, "poptypes", "*.txt"))}
vanilla_nf = set(re.findall(r"([A-Za-z_]\w*)\s*=", re.sub(r"#.*", "", rd("common", "national_focus.txt"))))
known = goods | pops | vanilla_nf | {"owner", "has_country_flag", "local_factory_output", "local_factory_input", "assimilation_rate",
                                     "mine_rgo_eff", "farm_rgo_eff", "immigrant_push", "immigrant_attract", "social_reform_desire",
                                     "political_reform_desire", "local_repair", "pop_militancy_modifier", "NOT", "OR", "AND", "year", "tag", "war", "is_colonial", "continent"}
clean = re.sub(r"#.*", "", nf)
names = []
for g, body, s_, e_ in blocks(clean):
    for k, b, s2, e2 in blocks(body):
        names.append(k)
unknown = sorted(set(re.findall(r"([A-Za-z_]\w*)\s*=", clean)) - known - set(names) - {g for g, b, s_, e_ in blocks(clean)})
print("national focuses:", len(names), "| keys vanilla does not know:", unknown)
if unknown:
    raise SystemExit("IGoR focus file needs keys vanilla lacks: %s" % unknown)
wr("common/national_focus.txt", nf)

# icon strips (67 frames) and the two sprite definitions that say how many frames they hold
for f in ("province_natfocus_strip.dds", "province_natfocus_strip_small.dds", "province_natfocus_bg.dds"):
    dst = os.path.join(OUT, "gfx", "interface", f)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(os.path.join(IG, "gfx", "interface", f), dst)
frames = int(re.search(r'name\s*=\s*"national_focus".*?noOfFrames\s*=\s*(\d+)', open(os.path.join(IG, "interface", "mapitems.gfx"), encoding=ENC, errors="replace").read(), re.S).group(1))
for gfx, sprite in (("mapitems.gfx", "national_focus"), ("province_interface.gfx", "GFX_province_natfocus_strip"), ("province_interface.gfx", "GFX_province_natfocus_strip_small")):
    p = os.path.join(OUT, "interface", gfx)
    t = open(p, encoding=ENC).read() if os.path.exists(p) else rd("interface", gfx)
    t, n = re.subn(r'(name\s*=\s*"%s"\s.*?noOfFrames\s*=\s*)\d+' % sprite, lambda m: m.group(1) + str(frames), t, count=1, flags=re.S)
    assert n == 1, (gfx, sprite)
    wr("interface/" + gfx, t.replace("\r\n", "\n"))
print("focus icon frames:", frames)

# names: IGoR's own lines for every focus and focus group
loc = {}
for f in glob.glob(os.path.join(IG, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        k = l.split(";", 1)[0]
        if k and k not in loc:
            loc[k] = l.split(";")[1] if ";" in l else ""
groups = [g for g, b, s_, e_ in blocks(clean)]
lines = []
for k in names + groups:
    if k in loc and loc[k]:
        lines.append("%s;%s;;;;;;;;;;;;;x" % (k, loc[k].replace(";", ",")))
missing = [k for k in names + groups if not loc.get(k)]
print("focus names copied:", len(lines), "| without a name in IGoR or vanilla:", missing[:8])

# tier unlocks, exactly as RobloxDoD 1.8 and DoD Heartbreaker do it (their files are identical):
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
