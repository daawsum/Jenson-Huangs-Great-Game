"""Research: who owns the Near East now, and the Chinese provinces with their goods and life rating."""
import os, re, glob, json, collections
from config import *

strip = lambda t: re.sub(r"#.*", "", t)
cont = {}
for k, body, s, e in blocks(open(os.path.join(OUT, "map", "continent.txt"), encoding=ENC).read()):
    for p in re.search(r"provinces\s*=\s*\{([^}]*)\}", body).group(1).split():
        cont[int(p)] = k
names = {}
for f in glob.glob(os.path.join(V, "localisation", "*.csv")) + glob.glob(os.path.join(OUT, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        m = re.match(r"PROV(\d+);([^;]*)", l)
        if m:
            names[int(m.group(1))] = m.group(2)
prov = {}
for f in glob.glob(os.path.join(OUT, "history", "provinces", "*", "*.txt")):
    m = re.match(r"\s*(\d+)", os.path.basename(f))
    t = open(f, encoding=ENC).read()
    g = lambda k: (re.search(r"\b%s\s*=\s*(\w+)" % k, t) or [0, None])[1]
    prov[int(m.group(1))] = dict(folder=os.path.basename(os.path.dirname(f)), owner=g("owner"), goods=g("trade_goods"), lr=g("life_rating"),
                                 cores=re.findall(r"add_core\s*=\s*(\w+)", t))
vown = {}
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    m = re.match(r"\s*(\d+)", os.path.basename(f))
    if m:
        o = re.search(r"\bowner\s*=\s*(\w+)", strip(open(f, encoding=ENC, errors="replace").read()))
        vown[int(m.group(1))] = o.group(1) if o else None
byf = collections.defaultdict(collections.Counter)
for p, v in prov.items():
    if cont.get(p) in ("asia", "africa", "europe") and v["owner"] and v["owner"] not in WARLORDS and v["owner"] != "HRE":
        byf[(cont[p], v["folder"])][v["owner"]] += 1
for k, c in sorted(byf.items()):
    print(k, dict(c))
print("-- cores IRQ/KDS/AZB/UZB provinces:")
for tag in ("IRQ", "KDS", "KUR", "AZB", "ARM", "GEO", "SYR", "EGY"):
    print("  ", tag, [(p, names.get(p), v["owner"]) for p, v in prov.items() if tag in v["cores"]][:14])
for n in ("Baku", "Tashkent", "Tehran", "Baghdad", "Mosul", "Kirkuk", "Diyarbakir", "Van", "Sulaymaniyah", "Sanandaj", "Kermanshah", "Hakkari", "Lahore"):
    print("  name", n, [(p, prov[p]["owner"], prov[p]["cores"][:4]) for p, x in names.items() if x == n and p in prov])
print("-- china")
china = [p for p, v in prov.items() if v["owner"] in WARLORDS]
gc = collections.Counter(prov[p]["goods"] for p in china)
print("goods:", dict(gc.most_common()))
lrs = [int(prov[p]["lr"] or 0) for p in china]
print("life rating: mean %.1f, distribution %s" % (sum(lrs) / len(lrs), dict(sorted(collections.Counter(lrs).items()))))
by = collections.defaultdict(list)
for p in sorted(china):
    by[prov[p]["owner"]].append("%d %s %s %s" % (p, names.get(p, "?"), prov[p]["goods"], prov[p]["lr"]))
for o in WARLORDS:
    print(o, "|", " ; ".join(by[o]))
eu = [int(v["lr"]) for p, v in prov.items() if cont.get(p) == "europe" and v["lr"]]
print("europe provinces", len(eu), "mean lr %.1f" % (sum(eu) / len(eu)))
for d in (V, OUT):
    for sub in ("events", "decisions", "inventions", "technologies"):
        for f in glob.glob(os.path.join(d, sub, "*.txt")):
            t = strip(open(f, encoding=ENC, errors="replace").read())
            n = len(re.findall(r"trade_goods\s*=\s*oil", t))
            if n or "oil" in os.path.basename(f).lower():
                print("oil:", os.path.relpath(f, d), "in", "vanilla" if d == V else "mod", "| trade_goods = oil x", n)
sm = strip(rd("common", "static_modifiers.txt") + rd("common", "event_modifiers.txt") + rd("common", "issues.txt") + rd("common", "nationalvalues.txt"))
for k in ("global_assimilation_rate", "assimilation_rate", "education_efficiency_modifier", "administrative_efficiency_modifier", "rgo_throughput", "RGO_throughput", "factory_throughput", "global_immigrant_attract", "immigrant_attract", "local_rgo_throughput", "local_factory_throughput"):
    print("modifier key", k, len(re.findall(r"\b%s\b" % k, sm)))
