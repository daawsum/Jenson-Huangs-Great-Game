"""Research for the HRE: which vanilla folders / cores cover the regions asked for."""
import os, re, glob, collections
from config import *

cont = {}
for k, body, s, e in blocks(rd("map", "continent.txt")):
    for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", body).group(1).split():
        cont[int(p)] = k
fold = collections.Counter()
own = collections.defaultdict(collections.Counter)
corec = collections.defaultdict(collections.Counter)
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    m = re.match(r"\s*(\d+)", os.path.basename(f))
    if not m or cont.get(int(m.group(1))) != "europe":
        continue
    d = os.path.basename(os.path.dirname(f))
    t = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=", "\n" + open(f, encoding=ENC, errors="replace").read())[0]
    o = re.search(r"\bowner\s*=\s*(\w+)", t)
    fold[d] += 1
    own[d][o.group(1) if o else None] += 1
    for c in re.findall(r"add_core\s*=\s*(\w+)", t):
        corec[d][c] += 1
for d, n in fold.most_common():
    print("%-16s %3d owners %s | cores %s" % (d, n, dict(own[d].most_common(8)), dict(corec[d].most_common(10))))
ct = rd("common", "countries.txt")
print("HRE tag in vanilla:", bool(re.search(r"(?m)^HRE\s*=", ct)), "| capital AUS:", re.search(r"capital\s*=\s*(\d+)", open(glob.glob(os.path.join(V, "history", "countries", "AUS*"))[0]).read()).group(1))
print("warlords:", {t: (w[0], w[6]) for t, w in WARLORDS.items()})
f = glob.glob(os.path.join(OUT, "history", "pops", "1836.1.1", "China*.txt"))
print(f[:3])
if f:
    print(open(f[0], encoding=ENC).read()[:700])
R = os.path.join(V, "mod", "RobloxDOD 1.8")
tr = re.sub(r"#.*", "", open(os.path.join(R, "common", "technology.txt"), encoding=ENC, errors="replace").read())
print("schools:", re.findall(r"(?m)^\t(\w+)\s*=\s*\{?\s*$", tr[tr.find("schools"):])[:30])
rt = set()
cat = {}
for g in glob.glob(os.path.join(R, "technologies", "*.txt")):
    for k, b, s, e in blocks(re.sub(r"#.*", "", open(g, encoding=ENC, errors="replace").read())):
        rt.add(k); cat[k] = (os.path.basename(g)[:-4], re.search(r"area\s*=\s*(\w+)", b).group(1), int(re.search(r"year\s*=\s*(\d+)", b).group(1)))
eng = open(glob.glob(os.path.join(V, "history", "countries", "ENG*"))[0], encoding=ENC, errors="replace").read().split("# Inventions")[0]
wt = re.findall(r"^(\w+)\s*=\s*1\s*$", eng, re.M)
print("ENG 1836 techs missing from roblox:", [t for t in wt if t not in rt])
areas = collections.defaultdict(list)
for k, (f_, a, y) in cat.items():
    areas[a].append((y, k))
for a in ("political_thought", "social_thought", "philosophy", "aesthetics", "psychology", "army_doctrine", "army_leadership", "naval_doctrine", "infrastructure", "economic_theory", "financial_institutions", "market_structure", "organization", "power", "mechanization", "naval_engineering", "military_science", "light_armament", "heavy_armament", "ship_construction", "naval_science", "naval_leadership", "chemistry", "metallurgy", "monetary_system", "flexible_firepower"):
    if a in areas:
        print(a, sorted(areas[a]))
print("other areas:", sorted(set(areas) ))
