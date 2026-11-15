"""One-off: break the large old-world countries into successor states named after their chief cities."""
s = open("02_world.py", encoding="utf-8").read()
if "SUCCESSOR" in s:
    raise SystemExit("already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


# 1 split after the first population pass (city sizes are known by then)
rep("run_pops({}, False)\n", r'''run_pops({}, False)

# ------------------------------------------------------------------ successor states
# The old world is left behind AND broken up: every large non-Chinese country is cut into regional
# successor states of roughly eight provinces, each named after its biggest city. The piece holding
# the old capital keeps the original tag. History and parties are the parent's own (vanilla text).
NO_SUCCESSORS = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK", "SIA", "DAI", "BUR", "CAM", "LUA", "JOH", "ATJ", "BRU", "BAL", "JAV", "PHI"}
SUCCESSOR = collections.OrderedDict()        # new tag -> (parent tag, name, colour)


def _kmeans(ps, k):
    pts = {p: CENT[p] for p in ps}
    cs = [pts[min(ps)]]
    while len(cs) < k:
        cs.append(max(pts.values(), key=lambda c: min((c[0] - d[0]) ** 2 + (c[1] - d[1]) ** 2 for d in cs)))
    for _ in range(30):
        g = [[] for _ in cs]
        for p, c in pts.items():
            g[min(range(k), key=lambda i: (c[0] - cs[i][0]) ** 2 + (c[1] - cs[i][1]) ** 2)].append(p)
        cs = [(sum(pts[p][0] for p in gg) / len(gg), sum(pts[p][1] for p in gg) / len(gg)) if gg else cs[i] for i, gg in enumerate(g)]
    return [gg for gg in g if gg]


def _colour(tag):
    mm = re.search(r"color\s*=\s*\{\s*(\d+)\s+(\d+)\s+(\d+)", rd("common", "countries", vtags[tag]))
    return tuple(int(x) for x in mm.groups()) if mm else (150, 150, 150)


_byown = collections.defaultdict(list)
for p in ALLP:
    if owner[p]:
        _byown[owner[p]].append(p)
_taken = set(vtags) | set(WARLORDS) | {"WBK", "TIN", "SMA", "MED", "LRG", "HUG"}
_codes = ("X%s%s" % (a, b) for a in "ABCDEFGHJKLMNPQRSTUVWYZ" for b in "ABCDEFGHJKLMNPQRSTUVWYZ0123456789")
_names = set()
for ptag in sorted(_byown):
    ps = _byown[ptag]
    if ptag in NO_SUCCESSORS or ptag not in vtags or len(ps) < 14:
        continue
    groups = _kmeans(sorted(ps), max(2, round(len(ps) / 8)))
    keep = max(groups, key=lambda g: (vcap.get(ptag) in g, sum(popsize[q] for q in g)))
    base = _colour(ptag)
    for gi, g in enumerate(groups):
        if g is keep or sum(popsize[q] for q in g) < 20000:
            continue
        seat = max(g, key=lambda q: popsize[q])
        name = PNAME[seat]
        if name in _names or len(name) < 3:
            continue
        code = next(c for c in _codes if c not in _taken)
        _taken.add(code)
        _names.add(name)
        col = tuple(max(25, min(235, base[i] + ((gi * (37 + 23 * i)) % 121) - 60)) for i in range(3))
        SUCCESSOR[code] = (ptag, name, col)
        for q in g:
            owner[q] = code
print("successor states created:", len(SUCCESSOR), "from", len({v[0] for v in SUCCESSOR.values()}), "countries")
''')

# 2 cores: a successor state also carries its parent's core, so the parent can reunify
rep('''            cores = [o] if o == "WBK" else [o] + [c for c in v["cores"] if c != o and c not in BIG]''',
    '''            cores = [o] if o == "WBK" else [o] + ([SUCCESSOR[o][0]] if o in SUCCESSOR else []) + [c for c in v["cores"] if c != o and c not in BIG]''')

# 3 country definitions: the parent's own country file with a new colour
rep('lines[ins:ins] = ["# Warlord Era"] + add + [""]\n', r'''for t, (ptag, name, col) in SUCCESSOR.items():
    add.append('%s\t\t= "countries/WE_%s.txt"' % (t, t))
    pf = rd("common", "countries", vtags[ptag])
    pf = re.sub(r"color\s*=\s*\{[^}]*\}", "color = { %d %d %d }" % col, pf, count=1)
    wr("common/countries/WE_%s.txt" % t, pf)
lines[ins:ins] = ["# Warlord Era"] + add + [""]
''')

# 4 history: the parent's converted history, with the successor's own capital and army file
rep('''def generic_history(tag, t, special=False):
    h = vhist.get(tag, "")''', '''def generic_history(tag, t, special=False, src=None):
    h = vhist.get(src or tag, "")''')
rep('wr("history/countries/WBK - World Bank.txt",', r'''for t, (ptag, name, col) in SUCCESSOR.items():
    wr("history/countries/%s - %s.txt" % (t, re.sub(r'[\\/:*?"<>|]', "", name)), fix_party(ptag, generic_history(t, tier[t], False, ptag)))

wr("history/countries/WBK - World Bank.txt",''')

# 5 flags and names
rep('allnew = [("WBK", (250, 250, 250))]', 'allnew = [(t, v[2]) for t, v in SUCCESSOR.items()] + [("WBK", (250, 250, 250))]')
rep('L += loc("WBK", "World Bank")', '''for t, (ptag, name, col) in SUCCESSOR.items():
    L += loc(t, name) + loc(t + "_ADJ", name)
L += loc("WBK", "World Bank")''')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched")
