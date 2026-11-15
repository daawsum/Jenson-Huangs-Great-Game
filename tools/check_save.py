"""Read an autosave: the HRE, pop literacy by owner, factories and their workers, technologies."""
import re, sys, collections

t = open(sys.argv[1], encoding="cp1252", errors="replace").read()
print("date", re.search(r'date="([^"]+)"', t).group(1), "| size %.1f MB" % (len(t) / 1e6), "| ends cleanly:", t.rstrip().endswith("}"))


def block_at(start):
    d, j = 1, start
    while d and j < len(t):
        d += t[j] == "{"
        d -= t[j] == "}"
        j += 1
    return t[start:j]


own = collections.Counter()
lit = collections.defaultdict(lambda: [0.0, 0])
types = collections.defaultdict(collections.Counter)
for m in re.finditer(r'\n(\d+)=\n\{\n\tname="[^"]*"\n\towner="(\w+)"', t):
    b = block_at(m.end())
    o = m.group(2)
    own[o] += 1
    for pm in re.finditer(r"\n\t(\w+)=\n\t\{\n\t\tid=\d+\n\t\tsize=(\d+)(.*?)\n\t\}", b, re.S):
        size = int(pm.group(2))
        l = re.search(r"literacy=([\d\.]+)", pm.group(3))
        types[o][pm.group(1)] += size
        if l:
            lit[o][0] += float(l.group(1)) * size
            lit[o][1] += size
tags = sys.argv[2:]
print("provinces owned:", {k: own[k] for k in tags})
for k in tags:
    if lit[k][1]:
        ty = types[k]
        print("%s literacy %.3f | pops %.1fM | craftsmen %d clerks %d capitalists %d" % (k, lit[k][0] / lit[k][1], lit[k][1] / 1e6, ty["craftsmen"], ty["clerks"], ty["capitalists"]))
for k in tags:
    m = re.search(r"\n%s=\n\{" % k, t)
    if not m:
        print(k, "no country block")
        continue
    b = block_at(m.end())
    fac = re.findall(r'state_buildings=\s*\{\s*building="(\w+)"\s*level=(\d+)(.*?)\n\t\t\}', b, re.S)
    emp = 0
    for nm, lv, rest in fac:
        emp += sum(int(x) for x in re.findall(r"count=(\d+)", rest))
    tech = re.search(r"\n\ttechnology=\s*\{(.*?)\n\t\}", b, re.S)
    techs = re.findall(r"(\w+)=\{1 ", tech.group(1)) if tech else []
    states = len(re.findall(r"\n\tstate=\s*\{", b))
    print("%s | civilized %s | states %d | factories %d %s | workers employed %d | techs %d | nv %s | research %s" % (
        k, (re.search(r"\n\tcivilized=(\w+)", b) or [0, "no"])[1], states, len(fac), dict(collections.Counter(f[0] for f in fac).most_common(4)), emp, len(techs),
        (re.search(r'nationalvalue="(\w+)"', b) or [0, "?"])[1], (re.search(r'\n\tresearch=\s*\{\s*technology="?(\w+)', b) or [0, "-"])[1]))
    mods = re.findall(r'modifier="(\w+)"', b)
    print("    modifiers:", mods[:8], "| flags:", re.findall(r"(\w+)=yes", (re.search(r"\n\tflags=\s*\{([^}]*)\}", b) or [0, ""])[1])[:10])
print("countries alive with provinces:", len(own), "| largest:", own.most_common(6))
