"""Stage 2: province owners, pops, countries, armies, states, continents, flags, localisation."""
import os, re, json, glob, math, collections, shutil
from PIL import Image, ImageDraw
from config import *
from content import *

# cultures of each clique come from content.py
for _t, (_p, _acc, _han) in CLIQUE_CULTURE.items():
    if _t in WARLORDS:
        _w = WARLORDS[_t]
        WARLORDS[_t] = (_w[0], _w[1], _w[2], _p, _acc, _w[5], _w[6], _w[7])

M = json.load(open(os.path.join(WORK, "map.json")))
SPLIT = {int(k): v for k, v in M["split"].items()}
FRACP = {int(k): v for k, v in M["frac_parent"].items()}
PNAME = {int(k): v for k, v in M["pname"].items()}
PFOLDER = {int(k): v for k, v in M["pfolder"].items()}
CENT = {int(k): v for k, v in M["centroid"].items()}
COASTAL = {int(k): v for k, v in M["coastal"].items()}
ADJ = {int(k): set(v) for k, v in M["adj"].items()}
SEA = set(M["sea"])
PARENT = {c[0]: p for p, ks in SPLIT.items() for c in ks}
TERRAIN = {int(k): v for k, v in json.load(open(os.path.join(WORK, "terrain.json"))).items()}

# lakes are listed as sea provinces too: keep only the big connected ocean
_seen, _best = set(), set()
for s0 in SEA:
    if s0 in _seen:
        continue
    comp, stack = {s0}, [s0]
    while stack:
        q = stack.pop()
        for r in ADJ.get(q, ()):
            if r in SEA and r not in comp:
                comp.add(r); stack.append(r)
    _seen |= comp
    if len(comp) > len(_best):
        _best = comp
OCEAN = _best
COASTAL = {p: [q for q in v if q in OCEAN] for p, v in COASTAL.items()}
COASTAL = {p: v for p, v in COASTAL.items() if v}
# a usable port: the engine reads the port's sea zone from the naval_base marker in positions.txt,
# so only provinces whose marker is known to sit in the open sea may hold a naval base or a fleet
_vport = {int(k) for k, b_, s_, e_ in blocks(rd("map", "positions.txt")) if k.isdigit() and re.search(r"naval_base\s*=\s*\{", b_)}
_redo = set(SPLIT) | set(PARENT)
_ocean = set(M["ocean"])
PORTS = {p for p in COASTAL if (p in _redo and M["port_zone"].get(str(p)) in _ocean) or (p not in _redo and p in _vport)}

# clean previously generated history
for d in ("history", "common", "gfx", "localisation", "poptypes", "events", "decisions"):
    shutil.rmtree(os.path.join(OUT, d), ignore_errors=True)

# ------------------------------------------------------------------ vanilla data
cont = {}
conttext = rd("map", "continent.txt")
contblocks = collections.OrderedDict()
for k, body, s, e in blocks(conttext):
    mm = re.search(r"provinces\s*=\s*\{([^}]*)\}", body)
    ids = [int(x) for x in mm.group(1).split()]
    rest = (body[:mm.start()] + body[mm.end():]).strip()
    contblocks[k] = [ids, rest]
    for p in ids:
        cont[p] = k

regions = collections.OrderedDict()
for k, body, s0, e0 in blocks(re.sub(r"#.*", "", rd("map", "region.txt"))):
    regions[k] = [int(x) for x in body.split()]
region_of = {p: r for r, ps in regions.items() for p in ps}

vprov = {}
VBASE = {}          # province id -> vanilla's own file name, so a mod file always overrides it by name
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    mm = re.match(r"\s*(\d+)", os.path.basename(f))
    if not mm:
        continue
    VBASE[int(mm.group(1))] = os.path.basename(f)
    t = open(f, encoding=ENC, errors="replace").read()
    t = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=", "\n" + t)[0]
    t = re.sub(r"#.*", "", t)
    o = re.search(r"\bowner\s*=\s*(\w+)", t)
    lr = re.search(r"life_rating\s*=\s*(\d+)", t)
    tg = re.search(r"trade_goods\s*=\s*(\w+)", t)
    vprov[int(mm.group(1))] = {
        "owner": o.group(1) if o else None,
        "cores": re.findall(r"add_core\s*=\s*(\w+)", t),
        "lr": int(lr.group(1)) if lr else None,
        "goods": tg.group(1) if tg else None,
        "fort": bool(re.search(r"\bfort\s*=\s*\d", t)),
        "naval": bool(re.search(r"\bnaval_base\s*=\s*\d", t)),
        "rail": bool(re.search(r"\brailroad\s*=\s*\d", t)),
        "terrain": (re.search(r"terrain\s*=\s*(\w+)", t) or [None, None])[1],
    }

# vanilla countries
ctext = rd("common", "countries.txt")
vtags = collections.OrderedDict(re.findall(r'^(\w{3})\s*=\s*"countries/([^"]+)"', ctext, re.M))
vhist = {}
for f in glob.glob(os.path.join(V, "history", "countries", "*.txt")):
    vhist[os.path.basename(f)[:3]] = open(f, encoding=ENC, errors="replace").read()
vcap = {t: int(re.search(r"capital\s*=\s*(\d+)", h).group(1)) for t, h in vhist.items() if re.search(r"capital\s*=\s*(\d+)", h)}

corecount = collections.Counter(c for v in vprov.values() for c in v["cores"])

# ------------------------------------------------------------------ owners
CHINA = tag_of_vanilla_province()
for c, p in PARENT.items():
    CHINA[c] = CHINA[p]
BIG = {"ENG", "RUS", "FRA", "AUS", "TUR", "SPA", "NET", "PRU", "POR", "SWE", "DEN", "USA"}
EXCL = {"GER", "ITA", "SCA", "PLC", "YUG", "HND", "UBD", "ROM", "CZH", "SAF", "GCO", "UCA", "CHI", "ARA", "INO"}
NEWWORLD = {"north_america", "south_america", "oceania"}
RUMP_ALL = {"HAI", "HAW", "PRG"}
RUMP_CAPSTATE = {"MEX", "PEU"}

owner, pending_india = {}, []
ALLP = sorted(set(vprov) | set(PARENT))
for p in ALLP:
    if p in CHINA:
        owner[p] = CHINA[p]
        continue
    v = vprov[p]
    o, c = v["owner"], cont.get(p)
    if o is None:
        owner[p] = None
    elif c in NEWWORLD:
        if o in RUMP_ALL or (o in RUMP_CAPSTATE and region_of.get(p) == region_of.get(vcap[o])):
            owner[p] = o
        else:
            owner[p] = None
    elif o in ("CHI", "GXI", "YNN", "XBI", "MCK", "XIN", "SXI"):
        owner[p] = None
    elif o in BIG:
        cands = [x for x in v["cores"] if x != o and x not in EXCL and x not in BIG]
        if cands:
            owner[p] = min(cands, key=lambda x: (corecount[x], x))
        elif c == "africa":
            owner[p] = None
        elif c == "asia":
            if o == "TUR":
                owner[p] = "TUR"
            elif o in ("ENG", "FRA", "POR") and ("HND" in v["cores"] or PFOLDER.get(p) == "india"):
                owner[p] = None
                pending_india.append(p)
            else:
                owner[p] = None
        else:
            owner[p] = o
    else:
        owner[p] = o

INDIA_SKIP = BIG | {"PAN", "NEP", "BHU", "AFG", "BUR", "TIB", "PER", "KAL", "MAK"}
india_tags = {owner[p] for p in ALLP if PFOLDER.get(p) == "india" and owner[p]} - INDIA_SKIP
seeds = [p for p in ALLP if owner[p] in india_tags]
for p in pending_india:
    x, y = CENT[p]
    best = min(seeds, key=lambda q: (CENT[q][0] - x) ** 2 + (CENT[q][1] - y) ** 2)
    owner[p] = owner[best]

# the World Bank (after IGoR puir) sits on the Falkland Islands
WBK_PROVS = [2131, 2133] if WORLD_BANK else []
BANK_POPS = "\n\tbankers = {\n\t\tculture = british\n\t\treligion = protestant\n\t\tsize = 100000\n\t}\n"
for p in WBK_PROVS:
    owner[p] = "WBK"

# Europe west of Russia and north of the Balkans is one backward empire: Iberia, France, Britain,
# Scandinavia, Germany with the Low Countries and the Alps, Italy, Poland and Greater Hungary.
HRE_FOLDERS = {"spain", "portugal", "france", "united kingdom", "scandinavia", "germany", "austria", "italy", "low countries"}
HRE_PROVS = {p for p in vprov if cont.get(p) == "europe" and vprov[p]["owner"] and p not in CHINA
             and (PFOLDER.get(p) in HRE_FOLDERS or vprov[p]["owner"] == "AUS" or {"POL", "HUN", "KRA"} & set(vprov[p]["cores"]))}
for p in HRE_PROVS:
    owner[p] = "HRE"
vcap["HRE"] = 619                      # Vienna
print("holy roman empire provinces:", len(HRE_PROVS))

EMPTIED = {p for p in ALLP if owner[p] is None and p in vprov and vprov[p]["owner"] is not None}

# ------------------------------------------------------------------ pops
popsize = collections.Counter()
soldiers = collections.Counter()
pdir = os.path.join(V, "history", "pops", "1836.1.1")


def scale_block(body, f):
    def rep(mm):
        return "size = %d" % max(25, int(int(mm.group(1)) * f))
    return re.sub(r"size\s*=\s*(\d+)", rep, body)


def tally(p, body):
    for k, b, s, e in blocks(body):
        mm = re.search(r"size\s*=\s*(\d+)", b)
        if mm:
            popsize[p] += int(mm.group(1))
            if k == "soldiers":
                soldiers[p] += int(mm.group(1))


FACTORIES = ["fabric_factory", "steel_factory", "lumber_mill", "liquor_distillery", "canned_food_factory", "glass_factory",
             "ammunition_factory", "small_arms_factory", "winery", "furniture_factory", "paper_mill"]
NATIVE_POPS = {"aristocrats", "clergymen", "artisans", "soldiers", "farmers", "slaves", "labourers"}


# ------------------------------------------------------------------ one religion, merged cultures
# Whole culture groups collapse into one culture each (targets are existing vanilla keys, so every
# vanilla script that names a culture stays valid). Pops of the same type that end up identical
# are merged into one pop, which is the main lag saving.
RELIGION = "placeholder"
GROUP_TARGET = {
    "germanic": "north_german", "beneluxian": "dutch", "pan_swiss": "north_german", "scandinavian": "swedish",
    "british": "british", "italian": "north_italian", "iberian": "spanish", "french": "french",
    "south_slavic": "serb", "pan_romanian": "romanian", "hungarian_culture_group": "hungarian",
    "polish_culture_group": "polish", "czecho_slovak_culture_group": "czech", "east_slavic": "russian",
    "baltic": "latvian", "levantine": "greek", "turko_semitic": "turkish",
    "native_american": "native_american_minor", "american_cultures": "yankee", "neo_european_cultures": "anglo_canadian",
    "latin_american_cultures": "mexican", "african_diaspora_cultures": "afro_american",
    "west_african": "hausa", "central_african": "african_minor", "east_african": "amhara",
    "southern_african": "zulu", "oceanic": "polynesian",
}
CULTURE_NAMES = {
    "north_german": "German", "dutch": "Netherlandish", "swedish": "Scandinavian", "north_italian": "Italian",
    "spanish": "Iberian", "serb": "South Slav", "russian": "East Slav", "latvian": "Baltic", "greek": "Levantine",
    "czech": "Czechoslovak", "native_american_minor": "Native American", "yankee": "American",
    "anglo_canadian": "Colonial European", "mexican": "Latin American", "afro_american": "Afro-American",
    "hausa": "West African", "african_minor": "Central African", "amhara": "East African", "zulu": "Southern African",
    "polynesian": "Oceanian", "beifaren": "Northern Han", "nanfaren": "Yangtze Han", "yue": "Cantonese", "min": "Hokkien",
}
CMAP = {}
_ct = re.sub(r"#.*", "", rd("common", "cultures.txt"))
ALL_CULTURES = set()
for _g, _body, _s, _e in blocks(_ct):
    for _k, _b, _s2, _e2 in blocks(_body):
        ALL_CULTURES.add(_k)
        if _g in GROUP_TARGET:
            CMAP[_k] = GROUP_TARGET[_g]
for _v in GROUP_TARGET.values():
    assert _v in ALL_CULTURES, _v
# China: five cultures instead of eleven
CMAP.update({"hakka": "yue", "zhuang": "yue", "miao": "nanfaren", "yi": "nanfaren", "ainu": "japanese"})
CHINA_CMAP = {"asian_minor": "nanfaren", "korean": "manchu", "siberian": "manchu", "kazak": "uighur", "yakut": "manchu"}


def _culture_span(text, key):
    m_ = re.search(r"\n\t%s\s*=\s*\{" % key, text)
    d_, j_ = 1, m_.end()
    while d_:
        ch = text[j_]
        d_ += ch == "{"
        d_ -= ch == "}"
        j_ += 1
    return m_.start(), j_


_new = ""
for _k, (_nm, _tmpl, _col) in NEW_CULTURES.items():
    a_, b_ = _culture_span(_ct, _tmpl)
    blk = _ct[a_:b_].replace("\n\t%s" % _tmpl, "\n\t%s" % _k, 1)
    blk = re.sub(r"color\s*=\s*\{[^}]*\}", "color = { %d %d %d }" % _col, blk, count=1)
    _new += blk
    ALL_CULTURES.add(_k)
a_, b_ = _culture_span(_ct, "beifaren")
wr_cultures = _ct[:a_] + _new + _ct[a_:]


def cmap(c, in_china=False):
    if in_china and c in CHINA_CMAP:
        return CHINA_CMAP[c]
    return CMAP.get(c, c)


def simplify_pops(body, in_china, han=None, also=()):
    """Map cultures, set the single religion and merge pops that become identical."""
    merged = collections.OrderedDict()
    for pk, pb, _s, _e in blocks(body):
        cu = re.search(r"culture\s*=\s*(\w+)", pb)
        sz = re.search(r"size\s*=\s*(\d+)", pb)
        if not cu or not sz:
            continue
        cul = cmap(cu.group(1), in_china)
        if han and (cul in ("beifaren", "nanfaren") or cul in also):      # ordinary Han pops take the regional culture of the land they live on
            cul = han
        key = (pk, cul)
        merged[key] = merged.get(key, 0) + int(sz.group(1))
    return "".join("\n\t%s = {\n\t\tculture = %s\n\t\treligion = %s\n\t\tsize = %d\n\t}\n" % (pk, cu, RELIGION, n)
                   for (pk, cu), n in merged.items())


def fix_cult(text):
    """Country history: single religion, merged cultures, no duplicate accepted cultures."""
    text = re.sub(r"(?m)^(\s*religion\s*=\s*)\w+", r"\g<1>" + RELIGION, text)
    pm = re.search(r"(?m)^\s*primary_culture\s*=\s*(\w+)", text)
    prim = cmap(pm.group(1)) if pm else None
    seen, out = {prim}, []
    for l in text.split("\n"):
        m1 = re.match(r"\s*primary_culture\s*=\s*(\w+)", l)
        m2 = re.match(r"\s*culture\s*=\s*(\w+)", l)
        if m1:
            out.append("primary_culture = %s" % prim)
        elif m2:
            cu = cmap(m2.group(1))
            if cu not in seen:
                seen.add(cu)
                out.append("culture = %s" % cu)
        else:
            out.append(l)
    return "\n".join(out)


def hw(rel, text):
    wr(rel, fix_cult(text))


_rel = rd("common", "religion.txt")
_m = re.search(r"christian\s*=\s*\{", _rel)
wr_religion = _rel[:_m.end()] + "\n\n\t%s = {\n\t\ticon = 1\n\t\tcolor = { 0.6 0.6 0.6 }\n\t}\n" % RELIGION + _rel[_m.end():]


def run_pops(fac, write):
    popsize.clear(); soldiers.clear()
    for f in sorted(glob.glob(os.path.join(pdir, "*.txt"))):
        t = open(f, encoding=ENC, errors="replace").read()
        out = []
        for k, body, s, e in blocks(t):
            if not k.isdigit():
                continue
            p = int(k)
            if p == 2131 and WORLD_BANK:
                body = BANK_POPS
            body = simplify_pops(body, p in CHINA, CLIQUE_CULTURE.get(owner.get(p), (None, None, None))[2] if p in CHINA else None,
                                 ("manchu",) if owner.get(p) in ("FTN", "HLJ") else ())   # Fengtian and Heilongjiang are settler country
            parts = [(p, FRACP[p])] + [(c[0], c[2]) for c in SPLIT[p]] if p in SPLIT else [(p, 0.15 if p in EMPTIED else 1.0)]
            for q, fr in parts:
                fr *= fac.get(owner.get(q), 1.0)
                b = body if fr == 1.0 else scale_block(body, fr)
                if owner.get(q) is None:
                    # vanilla's unowned provinces only ever hold these pop types; anything else crashes on game start
                    kept = ["\n\t%s = {%s}\n" % (pk, pb) for pk, pb, _s, _e in blocks(b) if pk in NATIVE_POPS]
                    b = "".join(kept) or "\n\tfarmers = {\n\t\tculture = %s\n\t\treligion = %s\n\t\tsize = 100\n\t}\n" % (
                        (re.search(r"culture\s*=\s*(\w+)", body) or [0, "british"])[1],
                        (re.search(r"religion\s*=\s*(\w+)", body) or [0, "protestant"])[1])
                out.append("%d = {%s}\n" % (q, b))
                tally(q, b)
        if write:
            wr("history/pops/1836.1.1/" + os.path.basename(f), "\n".join(out))


run_pops({}, False)

# ------------------------------------------------------------------ successor states
# The old world is left behind AND broken up: every large non-Chinese country is cut into regional
# successor states of roughly eight provinces, each named after its biggest city. The piece holding
# the old capital keeps the original tag. History and parties are the parent's own (vanilla text).
NO_SUCCESSORS = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK", "SIA", "DAI", "BUR", "CAM", "LUA", "JOH", "ATJ", "BRU", "BAL", "JAV", "PHI"}
SUCCESSOR = collections.OrderedDict()        # new tag -> (parent tag, name, colour)
SUCCESSOR["HRE"] = ("AUS", "Holy Roman Empire", (214, 196, 120))    # Austria's own country file and history, verbatim


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
    if ptag in NO_SUCCESSORS or ptag not in vtags or len(ps) < 24:
        continue
    groups = _kmeans(sorted(ps), max(2, round(len(ps) / 14)))
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

# micro-states of three provinces or fewer are absorbed by the neighbour they share most border with
KEEP_SMALL = set(WARLORDS) | {"PAN", "PER", "MGL", "WBK", "HRE"}
_absorbed = 0
while True:
    _cnt = collections.Counter(o for o in owner.values() if o)
    _small = sorted((n, t) for t, n in _cnt.items() if n <= 3 and t not in KEEP_SMALL)
    _done = False
    for n, t in _small:
        edge = collections.Counter()
        for p in ALLP:
            if owner[p] == t:
                for q in ADJ.get(p, ()):
                    o2 = owner.get(q)
                    if o2 and o2 != t and o2 not in WARLORDS and o2 != "WBK":
                        edge[o2] += 1
        if not edge:
            continue
        tgt = max(edge, key=lambda x: (edge[x], _cnt[x]))
        for p in ALLP:
            if owner[p] == t:
                owner[p] = tgt
        SUCCESSOR.pop(t, None)
        _absorbed += 1
        _done = True
        break
    if not _done:
        break
print("micro-states absorbed by neighbours:", _absorbed)
# a country with no population crashes the game when history is executed (Jan Mayen did)
_tot = collections.Counter()
for p in ALLP:
    if owner[p]:
        _tot[owner[p]] += popsize[p]
for p in ALLP:
    if owner[p] and _tot[owner[p]] < 5000 and owner[p] not in WARLORDS:
        print("  almost no population, left unowned:", owner[p], p)
        owner[p] = None
    elif owner[p] and popsize[p] == 0 and owner[p] not in WARLORDS:
        print("  empty province left unowned:", owner[p], p)
        owner[p] = None
POPFAC = {}
for tag, w in WARLORDS.items():
    tot = sum(popsize[p] for p in ALLP if owner[p] == tag) * 4 / 1e6
    lo, hi = (12.0, 24.0) if w[6] else (0.8, 7.0)
    if tot < lo:
        POPFAC[tag] = lo / tot
    elif tot > hi:
        POPFAC[tag] = hi / tot
print("population balancing factors:", {k: round(v, 2) for k, v in POPFAC.items()})
run_pops(POPFAC, True)
if WORLD_BANK and popsize[2131] == 0:
    wr("history/pops/1836.1.1/World Bank.txt", "2131 = {%s}\n" % BANK_POPS)
    popsize[2131] = 100000

# ------------------------------------------------------------------ province history
for p in ALLP:
    v = vprov[PARENT.get(p, p)]
    o = owner[p]
    L = []
    if o:
        L += ["owner = %s" % o, "controller = %s" % o]
        if p in CHINA:
            cores = [o] if o == "MGL" else [o, "CHI"]
        else:
            cores = [o] if o == "WBK" else [o] + ([SUCCESSOR[o][0]] if o in SUCCESSOR and o != "HRE" else []) + [c for c in v["cores"] if c != o and c not in BIG]
        L += ["add_core = %s" % c for c in dict.fromkeys(cores)]
    goods = v["goods"]
    if p == 2131 and WORLD_BANK:
        goods = "precious_metal"
    elif goods == "precious_metal" and WORLD_BANK:          # only bankers can mine gold now, so other deposits change
        goods = ["iron", "coal", "sulphur"][p % 3]
    if goods:
        L.append("trade_goods = %s" % goods)
    lr = v["lr"]
    if o is None:
        lr = max(lr or 0, 35)
    if lr:
        L.append("life_rating = %d" % lr)
    # provinces added by a mod come out as ocean unless their terrain is stated (see 01b_terrain.py)
    terr = v["terrain"] or TERRAIN.get(p)
    if terr:
        L.append("terrain = %s" % terr)
    if o:
        if v["fort"] and p not in PARENT:
            L.append("fort = 1")
        if v["naval"] and p in COASTAL and p not in PARENT:
            L.append("naval_base = 1")
        # starting industry in every clique's capital state (vanilla format, vanilla factory types)
        if o in WARLORDS and p == WARLORDS[o][2]:
            k = list(WARLORDS).index(o)
            nfac = {"industry": 6, "commerce": 4, "army": 3, "navy": 3, "frontier": 2}.get(ARCHETYPE.get(o), 1)
            picks = [FACTORIES[(k + j) % len(FACTORIES)] for j in range(nfac)]
            for b in dict.fromkeys(picks):
                L.append("state_building = {\n\tlevel = 1\n\tbuilding = %s\n\tupgrade = yes\n}" % b)
    fname = VBASE.get(p) or "%d - %s.txt" % (p, re.sub(r'[\\/:*?"<>|]', "", PNAME[p]))
    wr("history/provinces/%s/%s" % (PFOLDER[p], fname), "\n".join(L) + "\n")

owned = collections.defaultdict(list)
for p in ALLP:
    if owner[p]:
        owned[owner[p]].append(p)

# every coastal major gets a naval base in its best port
for tag, w in WARLORDS.items():
    ports = [p for p in owned[tag] if p in PORTS]
    if ports:
        cap = w[2] if w[2] in ports else max(ports, key=lambda q: popsize[q])
        path = glob.glob(os.path.join(OUT, "history", "provinces", "*", "%d - *.txt" % cap))[0]
        t = open(path, encoding=ENC).read()
        if "naval_base" not in t:
            open(path, "w", encoding=ENC, newline="\r\n").write(t + "naval_base = 1\n")

# ------------------------------------------------------------------ tiers
PARTIAL_X = {"JAP", "TUR", "EGY", "PAN", "PER", "MGL"}
CIVIL_AFR = {"EGY", "MOR", "TUN", "TRI", "ALD", "ETH", "OMA"}
capital, tier = {}, {}
for tag, ps in owned.items():
    if tag in WARLORDS:
        capital[tag] = WARLORDS[tag][2]
        tier[tag] = "warlord"
        continue
    c = vcap.get(tag)
    if c not in ps:
        c = max(ps, key=lambda q: popsize[q])
    capital[tag] = c
    cc = cont.get(PARENT.get(c, c))
    if tag in PARTIAL_X or cc == "europe":
        tier[tag] = "partial"
    elif cc in NEWWORLD or (cc == "africa" and tag not in CIVIL_AFR):
        tier[tag] = "primitive"
    else:
        tier[tag] = "unciv"
for tag in WARLORDS:
    assert capital[tag] in owned[tag], tag
for t, (ptag, name, col) in SUCCESSOR.items():      # a successor is as backward as its parent
    if t in tier and ptag in tier:
        tier[t] = tier[ptag]

# ------------------------------------------------------------------ new tags
DOMINIONS = collections.OrderedDict([
    # tag: (name, adj, colour)
    ("DFS", ("Fusang", "Fusang", (200, 60, 60))),
    ("DJS", ("Jinshan", "Jinshan", (220, 180, 40))),
    ("DBZ", ("Beizhou", "Beizhou", (150, 200, 230))),
    ("DMX", ("Moxige", "Moxige", (60, 140, 80))),
    ("DJL", ("Jialebi", "Jialebi", (80, 200, 200))),
    ("DAD", ("Andisi", "Andisi", (170, 110, 60))),
    ("DBX", ("Baxi", "Baxi", (90, 180, 90))),
    ("DYH", ("Yinhe", "Yinhe", (160, 190, 240))),
    ("DNZ", ("Nanzhou", "Nanzhou", (230, 140, 60))),
    ("DXL", ("Xinxilan", "Xinxilan", (120, 120, 200))),
    ("DXF", ("Xifei", "Xifei", (210, 170, 110))),
    ("DZF", ("Zhongfei", "Zhongfei", (110, 150, 70))),
    ("DDF", ("Dongfei", "Dongfei", (190, 100, 130))),
    ("DNF", ("Nanfei", "Nanfei", (230, 200, 120))),
    ("DBH", ("Beihai", "Beihai", (190, 210, 220))),
    ("DXY", ("Xiyu", "Xiyu", (200, 170, 90))),
    ("DNY", ("Nanyang", "Nanyang", (100, 200, 160))),
])
FORMABLES = collections.OrderedDict([
    ("BYG", ("Beiyang Government", "Beiyang", (225, 190, 70), "beifaren")),
    ("LGG", ("Liangguang", "Liangguang", (50, 110, 200), "yue")),
    ("SHU", ("Shu", "Shu", (170, 50, 50), "nanfaren")),
    ("WUU", ("Wu", "Wu", (240, 130, 140), "nanfaren")),
    ("CHU", ("Chu", "Chu", (200, 90, 150), "nanfaren")),
    ("DIA", ("Dian", "Dian", (140, 80, 170), "nanfaren")),
    ("NWF", ("Northwest Federation", "Northwestern", (70, 160, 120), "beifaren")),
    ("MZG", ("Manchuria", "Manchurian", (180, 200, 60), "beifaren")),
    ("KHG", ("Mongol Empire", "Mongol", (120, 170, 220), "mongol")),
    ("KLS", ("Khalsa Raj", "Khalsa", (240, 150, 30), "panjabi")),
    ("PSE", ("Persian Empire", "Persian", (60, 160, 90), "persian")),
])
NEWTAGS = [t for t in WARLORDS if t not in vtags] + list(DOMINIONS) + list(FORMABLES)
clash = [t for t in list(DOMINIONS) + list(FORMABLES) if t in vtags]
assert not clash, clash
bad = [t for t in WARLORDS if t in vtags and t not in ("SXI", "GXI", "YNN", "XBI", "XIN", "TIB")]
assert not bad, bad
print("new tags:", len(NEWTAGS), "reused vanilla warlord tags:", [t for t in WARLORDS if t in vtags])

china_cf = rd("common", "countries", "China.txt")
china_parties = china_cf[china_cf.index("party"):]


def country_file(col, tag):
    return "color = { %d %d %d }\ngraphical_culture = ChineseGC\n\n%s" % (col[0], col[1], col[2], china_parties.replace('"CHI_', '"%s_' % tag))


lines = []
for l in ctext.splitlines():
    mm = re.match(r"^(\w{3})\s*=", l)
    if mm and mm.group(1) in WARLORDS:
        continue
    lines.append(l)
ins = next(i for i, l in enumerate(lines) if l.startswith("ENG"))
add = []
for t, w in WARLORDS.items():
    add.append('%s\t\t= "countries/WE_%s.txt"' % (t, t))
    wr("common/countries/WE_%s.txt" % t, country_file(w[5], t))
for t, d in list(DOMINIONS.items()) + list(FORMABLES.items()):
    add.append('%s\t\t= "countries/WE_%s.txt"' % (t, t))
    wr("common/countries/WE_%s.txt" % t, country_file(d[2], t))
if WORLD_BANK:
    add.append('WBK\t\t= "countries/WE_WBK.txt"')
wr("common/countries/WE_WBK.txt", 'color = { 255 255 255 }\ngraphical_culture = EuropeanGC\n\nparty = {\n\tname = "WBK_exclusive"\n'
   '\tstart_date = 1800.1.1\n\tend_date = 2000.1.1\n\n\tideology = reactionary\n\n\teconomic_policy = world_bank_economics\n'
   '\ttrade_policy = world_bank\n\treligious_policy = pluralism\n\tcitizenship_policy = full_citizenship\n\twar_policy = anti_military\n}\n')
for t, (ptag, name, col) in SUCCESSOR.items():
    add.append('%s\t\t= "countries/WE_%s.txt"' % (t, t))
    pf = rd("common", "countries", vtags[ptag])
    pf = re.sub(r"color\s*=\s*\{[^}]*\}", "color = { %d %d %d }" % col, pf, count=1)
    wr("common/countries/WE_%s.txt" % t, pf)
lines[ins:ins] = ["# Warlord Era"] + add + [""]
wr("common/countries.txt", "\n".join(lines) + "\n")
wr("common/bookmarks.txt", 'bookmark =\n{\n\tname = "GC_NAME"\n\tdesc = "GC_DESC"\n\tdate = 1836.1.1\n\tcameraX = 4520\n\tcameraY = 1300\n}\n')

# ------------------------------------------------------------------ tech lists
alltech = set()
for f in glob.glob(os.path.join(V, "technologies", "*.txt")):
    for k, b, s, e in blocks(open(f, encoding=ENC, errors="replace").read()):
        alltech.add(k)


TECHCAT = {}
for _f in glob.glob(os.path.join(V, "technologies", "*.txt")):
    for _k, _b, _s, _e in blocks(open(_f, encoding=ENC, errors="replace").read()):
        TECHCAT[_k] = os.path.basename(_f)[:-4]
SPECIALITY = {"army": "army_tech", "navy": "navy_tech", "industry": "industry_tech", "commerce": "commerce_tech", "frontier": "army_tech"}


def clique_techs(tag):
    """Everyone has the cultural basics; a clique has the whole tree only in its speciality."""
    arch = ARCHETYPE.get(tag)
    spec = SPECIALITY.get(arch)
    bycat = collections.OrderedDict()
    for t_ in WARLORD_TECH:
        bycat.setdefault(TECHCAT.get(t_, "?"), []).append(t_)
    out = []
    for cat, ts in bycat.items():
        if cat == spec or cat == "culture_tech":
            keep = len(ts)
        elif arch is None or arch == "frontier":
            keep = max(1, len(ts) // 2)
        else:
            keep = max(1, round(len(ts) * 0.65))
        out += ts[:keep]
    return out


def techs(names):
    bad = [n for n in names if n not in alltech]
    if bad:
        print("  unknown techs dropped:", bad)
    return "".join("%s = 1\n" % n for n in names if n in alltech)


eng = vhist["ENG"].split("# Inventions")[0]
WARLORD_TECH = [x for x in re.findall(r"^(\w+)\s*=\s*1\s*$", eng, re.M)]
PARTIAL_TECH = ["post_napoleonic_thought", "flintlock_rifles", "bronze_muzzle_loaded_artillery", "post_nelsonian_thought",
                "private_banks", "no_standard", "guild_based_production", "classicism_n_early_romanticism",
                "late_enlightenment_philosophy", "water_wheel_power", "malthusian_thought"]
UNCIV_TECH = ["post_napoleonic_thought", "flintlock_rifles", "no_standard", "guild_based_production"]
HORDE_TECH = PARTIAL_TECH + ["military_staff_system", "army_command_principle", "muzzle_loaded_rifles",
                             "iron_muzzle_loaded_artillery", "strategic_mobility", "military_plans",
                             "army_professionalism", "army_decision_making", "clipper_design", "publishing_industry",
                             "mechanized_mining", "experimental_railroad", "freedom_of_trade"]
REF_E = ["land_reform", "admin_reform", "finance_reform", "education_reform", "transport_improv", "pre_indust", "industrial_construction"]
REF_M = ["foreign_training", "foreign_weapons", "military_constructions", "foreign_officers", "army_schools",
         "foreign_naval_officers", "naval_schools", "foreign_navies"]
PARTIAL_REF = ["admin_reform", "foreign_training", "foreign_weapons"]
SPECIAL_REF = ["land_reform", "foreign_training", "foreign_weapons", "military_constructions", "foreign_officers"]
# westernization needs 100% progress; check what these sets add up to from the game's own numbers
_iss = re.sub(r"#.*", "", rd("common", "issues.txt"))
PROGRESS = {m_.group(1): float(m_.group(2)) for m_ in re.finditer(r"yes_(\w+)\s*=\s*\{[^{}]*?civilization_progress_modifier\s*=\s*([\d\.]+)", _iss)}
for _nm, _set in (("partial", PARTIAL_REF), ("special", SPECIAL_REF)):
    _tot = sum(PROGRESS.get(r, 0.2) for r in _set)
    print("  westernization progress of %s reform set: %d%%" % (_nm, round(_tot * 100)))
    assert _tot <= 0.6, (_nm, _tot)


def reforms(on):
    return "".join("%s = %s_%s\n" % (r, "yes" if r in on else "no", r) for r in REF_E + REF_M)


def party_of(tag, ideology):
    cf = rd("common", "countries", vtags[tag]) if tag in vtags else china_cf
    for k, b, s, e in blocks(cf):
        if k != "party":
            continue
        nm = re.search(r'name\s*=\s*"([^"]+)"', b).group(1)
        sd = re.search(r"start_date\s*=\s*(\d+)", b)
        ed = re.search(r"end_date\s*=\s*(\d+)", b)
        if re.search(r"ideology\s*=\s*" + ideology + r"\b", b) and int(sd.group(1)) <= 1836 < int(ed.group(1)):
            return nm
    return None


SCHOOLS = ["army_tech_school", "naval_tech_school", "industrial_tech_school", "culture_tech_school", "commerce_tech_school"]
UH = "upper_house = {\n\tfascist = 0\n\tliberal = 10\n\tconservative = 40\n\treactionary = 50\n\tanarcho_liberal = 0\n\tsocialist = 0\n\tcommunist = 0\n}\n"
POLREF = ("slavery = no_slavery\nupper_house_composition = appointed\nvote_franschise = none_voting\npublic_meetings = no_meeting\n"
          "press_rights = state_press\ntrade_unions = no_trade_unions\nvoting_system = first_past_the_post\npolitical_parties = underground_parties\n"
          "wage_reform = no_minimum_wage\nwork_hours = no_work_hour_limit\nsafety_regulations = no_safety\nhealth_care = no_health_care\n"
          "unemployment_subsidies = no_subsidies\npensions = no_pensions\nschool_reforms = no_schools\n")

# ------------------------------------------------------------------ country history
chi_rx = party_of("CHI", "reactionary")
assert chi_rx


def warlord_history(tag, i):
    name, adj, cap, cul, acc, col, major, _ = WARLORDS[tag]
    s = "capital = %d\nprimary_culture = %s\n" % (cap, cul)
    s += "".join("culture = %s\n" % a for a in acc)
    _n, _a, gov, ideo, nv = STYLE[tag]
    s += "religion = %s\n" % RELIGION
    s += "government = %s\nplurality = 5.0\nnationalvalue = %s\n" % (gov, nv)
    if gov in ("democracy", "hms_government", "prussian_constitutionalism"):
        s += "last_election = 1834.1.1\n"
    s += "literacy = %.2f\nnon_state_culture_literacy = %.2f\ncivilized = yes\nprestige = %d\n" % (LITERACY[tag], LITERACY[tag] / 2, 25 if major else 5)
    s += "set_country_flag = chinese_warlord\n" + ("set_country_flag = major_warlord\n" if major else "set_country_flag = minor_warlord\n")
    s += POLREF + "ruling_party = %s\n" % party_of("CHI", ideo).replace("CHI_", tag + "_") + UH
    s += "schools = %s\n" % SCHOOLS[i % len(SCHOOLS)]
    s += "consciousness = 1\nnonstate_consciousness = 1\n"
    s += techs(clique_techs(tag))
    s += 'oob = "%s_oob.txt"\n' % tag
    return s


def generic_history(tag, t, special=False, src=None):
    h = vhist.get(src or tag, "")
    h = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=\s*\{", "\n" + h)[0]
    h = re.sub(r"#.*", "", h)
    h = re.sub(r"foreign_investment\s*=\s*\{[^}]*\}", "", h)
    keep = []
    for l in h.splitlines():
        ls = l.strip()
        if not ls:
            continue
        if re.match(r"(civilized|oob|decision|capital|schools|set_country_flag|prestige|literacy|non_state_culture_literacy)\b", ls):
            continue
        if re.match(r"\w+\s*=\s*(1|yes)\s*$", ls):          # techs and inventions
            continue
        if re.match(r"(%s)\s*=" % "|".join(REF_E + REF_M), ls):
            continue
        keep.append(l)
    lit = {"partial": (0.10, 0.05), "unciv": (0.04, 0.02), "primitive": (0.01, 0.01)}[t]
    if tag == "HRE":
        lit = (0.02, 0.01)
    s = "capital = %d\n" % capital[tag] + "\n".join(keep) + "\nliteracy = %s\nnon_state_culture_literacy = %s\ncivilized = no\n" % lit
    if special:
        s += reforms(SPECIAL_REF) + "set_country_flag = great_horde\n"
    elif t == "partial":
        s += reforms(PARTIAL_REF)
    elif t == "unciv":
        s += reforms([])
    else:
        s += reforms([])
    s += "set_country_flag = %s_nation\n" % t
    if tag in owned:
        s += 'oob = "%s_oob.txt"\n' % tag
    return s


def fix_party(tag, text):
    """A country that now exists in 1836 must have a ruling party that is active in 1836."""
    if tag not in owned or tag not in vtags:
        return text
    def dnum(sv):
        y, mo, da = sv.split(".")
        return int(y) * 10000 + int(mo) * 100 + int(da)
    valid = {}
    for k, b, s, e in blocks(re.sub(r"#.*", "", rd("common", "countries", vtags[tag]))):
        if k == "party":
            nm = re.search(r'name\s*=\s*"([^"]+)"', b).group(1)
            a = dnum(re.search(r"start_date\s*=\s*([\d\.]+)", b).group(1))
            z = dnum(re.search(r"end_date\s*=\s*([\d\.]+)", b).group(1))
            if a <= 18360101 < z:
                valid[nm] = re.search(r"ideology\s*=\s*(\w+)", b).group(1)
    mm = re.search(r'ruling_party\s*=\s*"?(\w+)"?', text)
    if mm and mm.group(1) in valid:
        return text
    for want in ("conservative", "reactionary", "liberal"):
        pick = [n for n, i in valid.items() if i == want]
        if pick:
            print("  ruling party of %s replaced: %s -> %s" % (tag, mm.group(1) if mm else None, pick[0]))
            if mm:
                return text[:mm.start()] + "ruling_party = %s" % pick[0] + text[mm.end():]
            return text + "ruling_party = %s\n" % pick[0]
    raise SystemExit("no valid 1836 party for " + tag)


hname = {}
for f in glob.glob(os.path.join(V, "history", "countries", "*.txt")):
    hname[os.path.basename(f)[:3]] = os.path.basename(f)

SPECIAL = {"PAN", "MGL", "PER"}
SEA_MIGRANT = set()
for i, tag in enumerate(WARLORDS):
    hw("history/countries/%s - %s.txt" % (tag, WARLORDS[tag][0]), warlord_history(tag, i))
for tag in vtags:
    if tag in WARLORDS or tag == "REB":
        continue
    t = tier.get(tag)
    if t is None:      # does not exist at start: keep a de-civilized copy so releases are uncivilized too
        c = vcap.get(tag)
        if tag not in vhist or c is None:
            continue
        capital[tag] = c
        cc = cont.get(c)
        t = "partial" if cc == "europe" else "primitive" if cc in NEWWORLD else "unciv"
    hw("history/countries/" + hname.get(tag, "%s - %s.txt" % (tag, tag)), fix_party(tag, generic_history(tag, t, tag in SPECIAL)))

for t, (ptag, name, col) in SUCCESSOR.items():
    hw("history/countries/%s - %s.txt" % (t, re.sub(r'[\\/:*?"<>|]', "", name)), fix_party(ptag, generic_history(t, tier[t], False, ptag)))

hw("history/countries/WBK - World Bank.txt",
   "capital = 2131\nprimary_culture = british\nreligion = protestant\ngovernment = absolute_monarchy\nplurality = 100\n"
   "nationalvalue = nv_order\nliteracy = 1\ncivilized = no\nis_releasable_vassal = no\n"
   "set_country_flag = world_bank_off\nset_country_flag = ghostland\nset_country_flag = world_bank\n"
   + POLREF + "ruling_party = WBK_exclusive\n" + UH + reforms([]) + 'oob = "WBK_oob.txt"\n')

# dominions and formables: civilized Chinese states
for tag, d in list(DOMINIONS.items()) + list(FORMABLES.items()):
    cul = d[3] if len(d) > 3 else "nanfaren"
    civ = tag not in ("KHG", "KLS", "PSE")
    s = "capital = 1612\nprimary_culture = %s\n" % cul
    if civ:
        s += "culture = beifaren\nculture = nanfaren\nculture = yue\nculture = min\nculture = hakka\n".replace("culture = %s\n" % cul, "")
    rel = {"mongol": "gelugpa", "panjabi": "sikh", "persian": "shiite"}.get(cul, "mahayana")
    s += "religion = %s\ngovernment = %s\nplurality = 5.0\nnationalvalue = nv_order\nliteracy = 0.2\n" % (rel, "presidential_dictatorship" if civ else "absolute_monarchy")
    s += "civilized = %s\n" % ("yes" if civ else "no")
    s += POLREF + "ruling_party = %s\n" % (chi_rx if civ else party_of("CHI", "conservative")).replace("CHI_", tag + "_") + UH
    if civ:
        s += techs(WARLORD_TECH)
    else:
        s += reforms(SPECIAL_REF)
    hw("history/countries/%s - %s.txt" % (tag, d[0]), s)

# ------------------------------------------------------------------ armies
def relations(tag):
    """Starting relations, written the way vanilla's oob files do: rivals hate, partners and patrons trust."""
    rel = {}
    if tag in RIVAL:
        rel[RIVAL[tag]] = -150
    if tag in PARTNER:
        rel[PARTNER[tag]] = 150
    if tag in PATRON:
        rel[PATRON[tag]] = 125
    for minor, major in PATRON.items():
        if major == tag:
            rel[minor] = 125
    return "".join("%s = {\n\tvalue = %d\n}\n\n" % (k_, v_) for k_, v_ in rel.items() if k_ in owned)


def army(name, loc, regs, homes):
    s = 'army = {\n\tname = "%s"\n\tlocation = %d\n' % (name, loc)
    for i, typ in enumerate(regs):
        s += '\tregiment = {\n\t\tname = "%d. %s"\n\t\ttype = %s\n\t\thome = %d\n\t}\n' % (i + 1, name, typ, homes[i % len(homes)])
    return s + "}\n\n"


def navy(name, loc, ships):
    s = 'navy = {\n\tname = "%s"\n\tlocation = %d\n' % (name, loc)
    for i, typ in enumerate(ships):
        s += '\tship = {\n\t\tname = "%s %d"\n\t\ttype = %s\n\t}\n' % (name, i + 1, typ)
    return s + "}\n\n"


def leaders(tag):
    f = os.path.join(V, "history", "units", "%s_oob.txt" % tag)
    if not os.path.exists(f):
        return ""
    t = open(f, encoding=ENC, errors="replace").read()
    return "".join("leader = {%s}\n\n" % b for k, b, s, e in blocks(t)
                   if k == "leader" and not re.search(r"regiment|ship\s*=|location", b))


for tag, ps in owned.items():
    if tag == "WBK":
        wr("history/units/WBK_oob.txt", "# the World Bank has no army\n")
        continue
    homes = sorted(ps, key=lambda q: -soldiers[q])[:8] or ps
    cap = capital[tag]
    adjn = WARLORDS[tag][1] if tag in WARLORDS else tag
    t = tier[tag]
    n = len(ps)
    s = relations(tag) + leaders(tag)
    if tag == "PAN":
        for i in range(6):
            s += army("Fauj-i-Khas %d" % (i + 1) if i < 2 else "Fauj-i-Ain %d" % (i - 1), cap if i < 3 else homes[i % len(homes)],
                      ["infantry"] * 6 + ["cavalry"] * 2 + ["artillery"] * 2, homes)
    elif tag == "MGL":
        for i in range(6):
            s += army("Tumen %d" % (i + 1), cap if i < 3 else homes[i % len(homes)], ["cavalry"] * 7 + ["infantry"] * 1, homes)
    elif tag == "PER":
        for i in range(3):
            s += army("Nizam %d" % (i + 1), cap if i == 0 else homes[i % len(homes)], ["infantry"] * 5 + ["cavalry"] * 2 + ["artillery"], homes)
    elif tag == "HRE":
        for i in range(8):
            s += army("Reichsarmee %d" % (i + 1), cap if i == 0 else homes[i % len(homes)], ["infantry"] * 8 + ["cavalry"] * 2, homes)
    elif t == "warlord":
        major = WARLORDS[tag][6]
        arch = ARCHETYPE.get(tag)
        count, comp = {"army": (3, ["infantry"] * 6 + ["cavalry"] + ["artillery"] * 2),
                       "navy": (2, ["infantry"] * 5 + ["cavalry"] + ["artillery"]),
                       "industry": (2, ["infantry"] * 6 + ["artillery"] * 2),
                       "commerce": (2, ["infantry"] * 5 + ["cavalry"] + ["artillery"]),
                       "frontier": (2, ["cavalry"] * 4 + ["infantry"] * 3)}.get(arch, (1, ["infantry"] * 5 + ["cavalry"]))
        for i in range(count):
            s += army("%s %s Army" % (adjn, ["First", "Second", "Third"][i]), cap if i == 0 else homes[-i], comp, homes)
        ports = [p for p in ps if p in PORTS]
        if ports:
            port = cap if cap in ports else max(ports, key=lambda q: popsize[q])
            ships = (["manowar"] * 2 + ["frigate"] * 3 + ["clipper_transport"] * 6) if arch == "navy" else \
                    (["manowar", "frigate", "frigate"] + ["clipper_transport"] * 4) if major else (["frigate"] + ["clipper_transport"] * 2)
            s += navy("%s Fleet" % adjn, port, ships)
    elif t == "partial":
        k = min(12, max(2, n // 3))
        s += army("Army of %s" % PNAME.get(cap, tag), cap, ["infantry"] * k + ["cavalry"] * (k // 4), homes)
    elif t == "unciv":
        k = min(6, max(1, n // 3))
        s += army("Host of %s" % PNAME.get(cap, tag), cap, ["irregular"] * k + ["cavalry"] * (k // 4), homes)
    else:
        k = min(3, max(1, n // 4))
        s += army("Warband of %s" % PNAME.get(cap, tag), cap, ["irregular"] * k, homes)
    wr("history/units/%s_oob.txt" % tag, s)

# No starting alliances, unions, guarantees or substates. Vanilla's files are overridden one by one
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

# ------------------------------------------------------------------ states of China
def cluster(ps, k):
    if k <= 1 or len(ps) <= k:
        return [ps] if k <= 1 else [[p] for p in ps]
    pts = {p: CENT[p] for p in ps}
    cs = [pts[min(ps)]]
    while len(cs) < k:
        cs.append(max(pts.values(), key=lambda c: min((c[0] - d[0]) ** 2 + (c[1] - d[1]) ** 2 for d in cs)))
    for _ in range(25):
        g = [[] for _ in cs]
        for p, c in pts.items():
            g[min(range(k), key=lambda i: (c[0] - cs[i][0]) ** 2 + (c[1] - cs[i][1]) ** 2)].append(p)
        cs = [(sum(pts[p][0] for p in gg) / len(gg), sum(pts[p][1] for p in gg) / len(gg)) if gg else cs[i] for i, gg in enumerate(g)]
    return [gg for gg in g if gg]


newregions, regname, dropped = collections.OrderedDict(), {}, set()
for r, ps in regions.items():
    full = ps + [c[0] for p in ps for c in SPLIT.get(p, [])]
    if not all(p in CHINA for p in ps):
        if any(p in SPLIT for p in ps):
            regions[r] = full
        continue
    dropped.add(r)
    byown = collections.defaultdict(list)
    for p in full:
        byown[owner[p]].append(p)
    for o, grp in byown.items():
        for g in cluster(sorted(grp), max(1, round(len(grp) / 3.4))):
            key = "WE_%d" % min(g)
            newregions[key] = sorted(g)
            regname[key] = PNAME[max(g, key=lambda q: popsize[q])]
out = ["%s = { %s }" % (r, " ".join(map(str, ps))) for r, ps in regions.items() if r not in dropped]
out += ["", "# Warlord Era states"] + ["%s = { %s } # %s" % (r, " ".join(map(str, ps)), regname[r]) for r, ps in newregions.items()]
wr("map/region.txt", "\n".join(out) + "\n")
print("chinese states:", len(newregions), "replacing", len(dropped))
final_regions = {r: ps for r, ps in regions.items() if r not in dropped}
final_regions.update(newregions)

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

# ------------------------------------------------------------------ continents (+ south east asia)
SEA_OWNERS = {"SIA", "DAI", "BUR", "CAM", "LUA", "JOH", "ATJ", "BRU", "BAL", "JAV", "PHI"}
sea_c = set()
for p in vprov:
    v = vprov[p]
    if cont.get(p) != "asia" or p in CHINA:
        continue
    if PFOLDER.get(p) == "indonesia" or v["owner"] in SEA_OWNERS or owner[p] in SEA_OWNERS or \
            (v["owner"] in ("NET", "SPA")) or set(v["cores"]) & SEA_OWNERS:
        sea_c.add(p)
xs = [CENT[p][0] for p in sea_c]; ys = [CENT[p][1] for p in sea_c]
grow = True
while grow:                                   # swallow unowned asian pockets surrounded by the region
    grow = False
    for p in vprov:
        if p in sea_c or cont.get(p) != "asia" or p in CHINA or vprov[p]["owner"] is not None:
            continue
        nb = [q for q in ADJ.get(p, ()) if q not in SEA]
        if nb and sum(q in sea_c for q in nb) * 2 >= len(nb):
            sea_c.add(p); grow = True
sea_c |= {p for p in ALLP if owner.get(p) == "TWN"}
for k in contblocks:
    ids = contblocks[k][0]
    ids += [c[0] for p in list(ids) for c in SPLIT.get(p, [])]
contblocks["asia"][0] = [p for p in contblocks["asia"][0] if p not in sea_c]
contblocks["southeast_asia"] = [sorted(sea_c), contblocks["asia"][1]]
s = ""
for k, (ids, rest) in contblocks.items():
    s += "%s = {\n\tprovinces = {\n" % k
    for i in range(0, len(ids), 25):
        s += "\t\t" + " ".join(map(str, ids[i:i + 25])) + "\n"
    s += "\t}\n\t%s\n}\n\n" % rest.replace("\n", "\n\t")
wr("map/continent.txt", s)
print("south east asia provinces:", len(sea_c), sorted({PNAME[p] for p in sea_c})[:40])
for tag in owned:
    if tag not in WARLORDS and capital[tag] in sea_c:
        SEA_MIGRANT.add(tag)
print("south east asian nations:", sorted(SEA_MIGRANT))
MIGRANT_FLAGS = "set_country_flag = new_world_nation\nset_country_flag = old_world_colony\n"
for tag in SEA_MIGRANT:
    path = os.path.join(OUT, "history", "countries", hname[tag])
    t_ = open(path, encoding=ENC).read().replace("\r\n", "\n")
    t_ = t_.replace("civilized = no", "civilized = yes")
    t_ = re.sub(r"(?m)^\w+ = (yes|no)_(%s)\n" % "|".join(REF_E + REF_M), "", t_)
    t_ = re.sub(r"(?m)^literacy = [\d\.]+", "literacy = 0.12", t_)
    t_ = t_.replace("set_country_flag = unciv_nation\n", "").replace("set_country_flag = partial_nation\n", "")
    t_ += "schools = traditional_academic\n" + techs(PARTIAL_TECH) + "set_country_flag = nanyang_state\n" + MIGRANT_FLAGS
    open(path, "w", encoding=ENC, newline="\r\n").write(t_)
    tier[tag] = "nanyang"
_tw = glob.glob(os.path.join(OUT, "history", "countries", "TWN - *.txt"))[0]
open(_tw, "a", encoding=ENC, newline="\r\n").write(MIGRANT_FLAGS)
final_cont = {p: k for k, (ids, rest) in contblocks.items() for p in ids}

# ------------------------------------------------------------------ flags
def flag(col, style):
    im = Image.new("RGBA", (93, 64), col + (255,))
    d = ImageDraw.Draw(im)
    dark = tuple(max(0, c - 90) for c in col) + (255,)
    light = (245, 240, 225, 255)
    if style == 0:
        d.rectangle([0, 0, 92, 20], fill=dark); d.rectangle([0, 43, 92, 63], fill=dark)
        d.ellipse([34, 20, 58, 44], fill=light)
    elif style == 1:
        d.rectangle([0, 0, 30, 63], fill=dark)
        d.ellipse([6, 22, 24, 40], fill=light)
    elif style == 2:
        d.polygon([(0, 0), (40, 32), (0, 63)], fill=dark)
        d.ellipse([4, 24, 20, 40], fill=light)
    elif style == 3:
        d.rectangle([0, 26, 92, 37], fill=light); d.rectangle([40, 0, 52, 63], fill=light)
    else:
        d.rectangle([0, 0, 46, 31], fill=dark)
        d.ellipse([14, 7, 32, 25], fill=light)
    return im


allnew = [(t, v[2]) for t, v in SUCCESSOR.items()] + [("WBK", (250, 250, 250))] + [(t, WARLORDS[t][5]) for t in WARLORDS] + [(t, d[2]) for t, d in list(DOMINIONS.items()) + list(FORMABLES.items())]
os.makedirs(os.path.join(OUT, "gfx", "flags"), exist_ok=True)
for i, (t, col) in enumerate(allnew):
    for j, suf in enumerate(["", "_communist", "_fascist", "_monarchy", "_republic"]):
        c = col if j in (0, 3, 4) else ((190, 30, 30) if j == 1 else (40, 40, 40))
        flag(c, (i + (j if j in (1, 2) else 0)) % 5).save(os.path.join(OUT, "gfx", "flags", "%s%s.tga" % (t, suf)), compression="tga_rle")

# ------------------------------------------------------------------ localisation
def loc(k, v):
    return "%s;%s;;;;;;;;;;;;;x\n" % (k, v)


L = ""
for t, w in WARLORDS.items():
    L += loc(t, w[0]) + loc(t + "_ADJ", w[1])
for t, d in list(DOMINIONS.items()) + list(FORMABLES.items()):
    L += loc(t, d[0]) + loc(t + "_ADJ", d[1])
_pn = {"conservative": "Old Guard", "liberal": "Reform Society", "reactionary": "Military Clique", "socialist": "Labour Union",
       "communist": "Soviet Committee", "fascist": "Blue Shirts", "anarcho_liberal": "Free Association"}
for t in list(WARLORDS) + list(DOMINIONS) + list(FORMABLES):
    for pn in re.findall(r'name\s*=\s*"CHI_(\w+)"', china_parties):
        L += loc("%s_%s" % (t, pn), _pn.get(re.sub(r"_\d+$", "", pn), "Party"))
for t, (ptag, name, col) in SUCCESSOR.items():
    L += loc(t, name) + loc(t + "_ADJ", name)
L += loc(RELIGION, "Customary Faith")
for _k, (_nm, _tmpl, _col) in NEW_CULTURES.items():
    L += loc(_k, _nm)
for _k, _v in CULTURE_NAMES.items():
    L += loc(_k, _v)
L += loc("WBK", "World Bank") + loc("WBK_ADJ", "World Bank") + loc("WBK_exclusive", "Board of Governors")
L += loc("PAN", "Sikh Empire") + loc("PAN_ADJ", "Sikh") + loc("MGL", "Mongolia") + loc("PER", "Persia")
for c, p in PARENT.items():
    L += loc("PROV%d" % c, PNAME[c])
for r, n in regname.items():
    L += loc(r, n)
L += loc("southeast_asia", "South East Asia")
L += loc("GC_NAME", MOD_NAME) + loc("GC_DESC", "China is shattered between thirty-five warlord cliques, the only modern states on Earth. The rest of the world lies divided, backward and open for the taking.")
wr("localisation/00_warlord_era.csv", L)

wr("../Warlord Era.mod", 'name = "' + MOD_NAME + '"\npath = "mod/Warlord Era"\nuser_dir = "WarlordEra"\n'
   + "".join('replace_path = "%s"\n' % r for r in ["history/provinces", "history/countries", "history/pops/1836.1.1", "history/units", "history/diplomacy", "history/wars"]))

# ------------------------------------------------------------------ report + state
print("\ncountries at start:", len(owned), collections.Counter(tier.values()))
print("unowned land provinces:", sum(1 for p in ALLP if owner[p] is None))
for t in ("warlord",):
    for tag in WARLORDS:
        ps = owned[tag]
        print("  %s %-20s prov %2d  pop %5.1fM  %s%s" % (tag, WARLORDS[tag][0], len(ps), sum(popsize[p] for p in ps) * 4 / 1e6,
                                                        "MAJOR" if WARLORDS[tag][6] else "minor", "  coast" if any(p in COASTAL for p in ps) else ""))
for t in ("partial", "unciv", "primitive"):
    print(t, sorted("%s:%d" % (tag, len(owned[tag])) for tag in owned if tier[tag] == t))

json.dump({
    "owner": {str(p): o for p, o in owner.items()}, "tier": tier, "capital": capital,
    "regions": final_regions, "cont": {str(p): k for p, k in final_cont.items()},
    "popsize": {str(p): n for p, n in popsize.items()}, "sea_migrant": sorted(SEA_MIGRANT),
    "dominions": {k: list(v) for k, v in DOMINIONS.items()}, "formables": {k: list(v) for k, v in FORMABLES.items()},
    "cmap": CMAP, "vtags": list(vtags), "warlord_tech": WARLORD_TECH,
}, open(os.path.join(WORK, "world.json"), "w"))

# remove World Bank leftovers when it is switched off (the tag is then not in countries.txt)
if not WORLD_BANK:
    for rel in ["common/countries/WE_WBK.txt", "history/countries/WBK - World Bank.txt", "history/units/WBK_oob.txt"] + \
               ["gfx/flags/WBK%s.tga" % x for x in ["", "_communist", "_fascist", "_monarchy", "_republic"]]:
        p_ = os.path.join(OUT, rel)
        if os.path.exists(p_):
            os.remove(p_)

wr("common/religion.txt", wr_religion)
wr("common/cultures.txt", wr_cultures)
