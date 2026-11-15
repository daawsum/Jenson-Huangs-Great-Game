"""One-off patch: the Holy Roman Empire, per-clique literacy and staffed industry in 02_world.py."""
p = "02_world.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a, s.count(a))
    s = s.replace(a, b)


rep(r'''EMPTIED = {p for p in ALLP if owner[p] is None''', r'''# Europe west of Russia and north of the Balkans is one backward empire: Iberia, France, Britain,
# Scandinavia, Germany with the Low Countries and the Alps, Italy, Poland and Greater Hungary.
HRE_FOLDERS = {"spain", "portugal", "france", "united kingdom", "scandinavia", "germany", "austria", "italy", "low countries"}
HRE_PROVS = {p for p in vprov if cont.get(p) == "europe" and vprov[p]["owner"] and p not in CHINA
             and (PFOLDER.get(p) in HRE_FOLDERS or vprov[p]["owner"] == "AUS" or {"POL", "HUN", "KRA"} & set(vprov[p]["cores"]))}
for p in HRE_PROVS:
    owner[p] = "HRE"
vcap["HRE"] = 619                      # Vienna
print("holy roman empire provinces:", len(HRE_PROVS))

EMPTIED = {p for p in ALLP if owner[p] is None''')
rep(r'''SUCCESSOR = collections.OrderedDict()        # new tag -> (parent tag, name, colour)
''', r'''SUCCESSOR = collections.OrderedDict()        # new tag -> (parent tag, name, colour)
SUCCESSOR["HRE"] = ("AUS", "Holy Roman Empire", (214, 196, 120))    # Austria's own country file and history, verbatim
''')
rep(r'''KEEP_SMALL = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK"}''', r'''KEEP_SMALL = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK", "HRE"}''')
rep(r'''cores = [o] if o == "WBK" else [o] + ([SUCCESSOR[o][0]] if o in SUCCESSOR else [])''',
    r'''cores = [o] if o == "WBK" else [o] + ([SUCCESSOR[o][0]] if o in SUCCESSOR and o != "HRE" else [])''')
rep(r'''    s += "literacy = 0.22\nnon_state_culture_literacy = 0.10\ncivilized = yes\nprestige = %d\n" % (25 if major else 5)''',
    r'''    s += "literacy = %.2f\nnon_state_culture_literacy = %.2f\ncivilized = yes\nprestige = %d\n" % (LITERACY[tag], LITERACY[tag] / 2, 25 if major else 5)''')
rep(r'''    lit = {"partial": (0.10, 0.05), "unciv": (0.04, 0.02), "primitive": (0.01, 0.01)}[t]
''', r'''    lit = {"partial": (0.10, 0.05), "unciv": (0.04, 0.02), "primitive": (0.01, 0.01)}[t]
    if tag == "HRE":
        lit = (0.02, 0.01)
''')
rep(r'''    elif t == "warlord":
        major = WARLORDS[tag][6]''', r'''    elif tag == "HRE":
        for i in range(8):
            s += army("Reichsarmee %d" % (i + 1), cap if i == 0 else homes[i % len(homes)], ["infantry"] * 8 + ["cavalry"] * 2, homes)
    elif t == "warlord":
        major = WARLORDS[tag][6]''')
rep(r'''final_regions.update(newregions)
''', r'''final_regions.update(newregions)

# ------------------------------------------------------------------ industry
# Every clique starts with factories in several states, not only its capital, and with the craftsmen,
# clerks and capitalists to run them (taken out of the farmers of the same provinces).
STATE_OF = {p: r for r, ps in final_regions.items() for p in ps}
IND_STATES = {"industry": 6, "commerce": 5, "navy": 4, "army": 4, "frontier": 2}
CAP_FACT = {"industry": 6, "commerce": 4, "army": 3, "navy": 3, "frontier": 2}
WORKERS = collections.Counter()      # province -> factory hands wanted
OWNERS_ = collections.Counter()      # province -> capitalists wanted
IND_REPORT = {}
for k, (tag, w) in enumerate(WARLORDS.items()):
    arch = ARCHETYPE.get(tag)
    mine = collections.defaultdict(list)
    for p in owned[tag]:
        mine[STATE_OF[p]].append(p)
    capst = STATE_OF[w[2]]
    plan = [(capst, w[2], CAP_FACT.get(arch, 1), [])]
    rest = sorted((r for r in mine if r != capst), key=lambda r: -sum(popsize[q] for q in mine[r]))
    for j, r in enumerate(rest[:IND_STATES.get(arch, 2 if w[6] else 1) - 1]):
        seat = max(mine[r], key=lambda q: popsize[q])
        picks = list(dict.fromkeys(FACTORIES[(k + 5 + 3 * j + i) % len(FACTORIES)] for i in range(2)))
        plan.append((r, seat, len(picks), picks))
    for r, seat, n, picks in plan:
        if picks:
            path = glob.glob(os.path.join(OUT, "history", "provinces", "*", "%d - *.txt" % seat))[0]
            t_ = open(path, encoding=ENC).read().replace("\r\n", "\n")
            t_ += "".join("state_building = {\n\tlevel = 1\n\tbuilding = %s\n\tupgrade = yes\n}\n" % b for b in picks)
            open(path, "w", encoding=ENC, newline="\r\n").write(t_)
        tot = sum(popsize[q] for q in mine[r]) or 1
        for q in mine[r]:
            WORKERS[q] += int(n * 10000 * popsize[q] / tot)
        OWNERS_[seat] += 150 * n
    IND_REPORT[tag] = (len(plan), sum(x[2] for x in plan))


def _industrialise(text):
    out, i = [], 0
    for m_ in re.finditer(r"(?m)^(\d+)\s*=\s*\{", text):
        if m_.start() < i:
            continue
        d, j = 1, m_.end()
        while d:
            d += text[j] == "{"
            d -= text[j] == "}"
            j += 1
        p = int(m_.group(1))
        body = text[m_.end():j - 1]
        if WORKERS.get(p, 0) > 0:
            best = None
            for b_ in re.finditer(r"(farmers|labourers)\s*=\s*\{[^}]*?size\s*=\s*(\d+)[^}]*\}", body):
                if best is None or int(b_.group(2)) > int(best.group(2)):
                    best = b_
            if best:
                size = int(best.group(2))
                take = min(WORKERS[p], int(size * 0.35))
                cap_ = min(OWNERS_.get(p, 0), int(size * 0.01))
                cul = re.search(r"culture\s*=\s*(\w+)", best.group(0)).group(1)
                rel = re.search(r"religion\s*=\s*(\w+)", best.group(0)).group(1)
                new = re.sub(r"size\s*=\s*\d+", "size = %d" % (size - take - cap_), best.group(0))
                add = ""
                for typ, n_ in (("craftsmen", int(take * 0.85)), ("clerks", take - int(take * 0.85)), ("capitalists", cap_)):
                    if n_ >= 25:
                        add += "\n\t%s = {\n\t\tculture = %s\n\t\treligion = %s\n\t\tsize = %d\n\t}\n" % (typ, cul, rel, n_)
                body = body[:best.start()] + new + body[best.end():].rstrip() + "\n" + add
                WORKERS[p] = -take
        out.append(text[i:m_.end()] + body + "}")
        i = j
    return "".join(out) + text[i:]


for f in glob.glob(os.path.join(OUT, "history", "pops", "1836.1.1", "*.txt")):
    t_ = open(f, encoding=ENC).read().replace("\r\n", "\n")
    n_ = _industrialise(t_)
    if n_ != t_:
        open(f, "w", encoding=ENC, newline="\r\n").write(n_)
print("industry (states, factories):", IND_REPORT)
print("factory hands placed:", -sum(n for n in WORKERS.values() if n < 0), "| provinces where no farmers were found:", [p for p, n in WORKERS.items() if n > 0][:10])
''')
open(p, "w", encoding="utf-8").write(s)

# literacy by clique: the lower Yangtze, the treaty-port south and the old capital read; the frontier does not
c = open("content.py", encoding="utf-8").read()
if "LITERACY" not in c:
    c += '''

# Literacy at the start. The examination heartlands (Jiangnan, Zhejiang, Anhui's academies, Hunan's
# Yuelu school), the merchant south (Canton, Fujian) and the capital read; the frontier does not.
LITERACY = {"JSU": 0.45, "ZHJ": 0.45, "SHG": 0.50, "GDG": 0.40, "FUJ": 0.38, "ZHL": 0.38, "AHC": 0.36, "HNC": 0.34,
            "SDG": 0.30, "HBE": 0.30, "JXI": 0.30, "SXI": 0.28, "SZC": 0.26, "CQG": 0.26, "FTN": 0.24, "HNA": 0.22,
            "TWN": 0.24, "XZC": 0.20, "GXI": 0.18, "HNI": 0.16, "GMJ": 0.16, "YNN": 0.14, "GZH": 0.12, "JLN": 0.14,
            "HLJ": 0.10, "RHE": 0.10, "CHH": 0.08, "SYN": 0.08, "NXA": 0.08, "XBI": 0.08, "QHI": 0.05, "XKG": 0.05,
            "XIN": 0.06, "KSG": 0.05, "TIB": 0.06}

# Who may proclaim which Chinese state. The eight regional states can each go on to proclaim China.
FORMERS = {"BYG": ["ZHL", "AHC", "SDG", "HNA"], "LGG": ["GDG", "GXI"], "SHU": ["SZC", "CQG"], "WUU": ["JSU", "ZHJ", "SHG"],
           "CHU": ["HBE", "HNC", "JXI"], "DIA": ["YNN", "GZH"], "NWF": ["GMJ", "XBI", "XIN"], "MZG": ["FTN", "JLN", "HLJ"]}
FORMERS["CHI"] = ["ZHL", "FTN", "GDG", "JSU", "AHC", "HBE"] + [t for t in FORMERS]
'''
    open("content.py", "w", encoding="utf-8").write(c)
b = open("build.sh", encoding="utf-8").read()
if "03a_tech" not in b:
    b = b.replace("python 03_gameplay.py | tail -1", "python 03a_tech.py | tail -3\npython 03_gameplay.py | tail -2")
    open("build.sh", "w", encoding="utf-8", newline="\n").write(b)
w = open("03b_worldbank.py", encoding="utf-8").read()
if 'pt = rd("common", "production_types.txt")' in w:
    w = w.replace('pt = rd("common", "production_types.txt")',
                  '_ptf = os.path.join(OUT, "common", "production_types.txt")       # 03a_tech.py may have added to it\n'
                  'pt = open(_ptf, encoding=ENC).read().replace("\\r\\n", "\\n") if os.path.exists(_ptf) else rd("common", "production_types.txt")')
    open("03b_worldbank.py", "w", encoding="utf-8").write(w)
print("patched")
