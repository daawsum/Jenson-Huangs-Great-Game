"""One-off (v4): regional Han cultures, clique line-ups, starting relations, civilized South East
Asia, Taiwan as an immigrant nation."""
s = open("02_world.py", encoding="utf-8").read()
if "from content import" in s:
    raise SystemExit("already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


rep("from config import *\n", '''from config import *
from content import *

# cultures of each clique come from content.py
for _t, (_p, _acc, _han) in CLIQUE_CULTURE.items():
    if _t in WARLORDS:
        _w = WARLORDS[_t]
        WARLORDS[_t] = (_w[0], _w[1], _w[2], _p, _acc, _w[5], _w[6], _w[7])
''')

# ---- new regional cultures: cloned from a vanilla Han culture, new key and colour
rep('''def cmap(c, in_china=False):''', r'''def _culture_span(text, key):
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


def cmap(c, in_china=False):''')
rep('''def simplify_pops(body, in_china):''', '''def simplify_pops(body, in_china, han=None):''')
rep('''        key = (pk, cmap(cu.group(1), in_china))''', '''        cul = cmap(cu.group(1), in_china)
        if han and cul in ("beifaren", "nanfaren"):      # ordinary Han pops take the regional culture of the land they live on
            cul = han
        key = (pk, cul)''')
rep('''            body = simplify_pops(body, p in CHINA)''',
    '''            body = simplify_pops(body, p in CHINA, CLIQUE_CULTURE.get(owner.get(p), (None, None, None))[2] if p in CHINA else None)''')
rep('''wr("common/religion.txt", wr_religion)''', '''wr("common/religion.txt", wr_religion)
wr("common/cultures.txt", wr_cultures)''')
rep('''L += loc(RELIGION, "Customary Faith")''', '''L += loc(RELIGION, "Customary Faith")
for _k, (_nm, _tmpl, _col) in NEW_CULTURES.items():
    L += loc(_k, _nm)''')

# ---- technology by line-up
rep('''def techs(names):''', r'''TECHCAT = {}
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


def techs(names):''')
rep("    s += techs(WARLORD_TECH)\n    s += 'oob = \"%s_oob.txt\"\\n' % tag\n    return s", "    s += techs(clique_techs(tag))\n    s += 'oob = \"%s_oob.txt\"\\n' % tag\n    return s")

# ---- factories by line-up
rep('''            picks = [FACTORIES[(k + j) % len(FACTORIES)] for j in range(4 if WARLORDS[o][6] else 1)]''',
    '''            nfac = {"industry": 6, "commerce": 4, "army": 3, "navy": 3, "frontier": 2}.get(ARCHETYPE.get(o), 1)
            picks = [FACTORIES[(k + j) % len(FACTORIES)] for j in range(nfac)]''')

# ---- armies, fleets and starting relations by line-up
rep('''    s = leaders(tag)
    if tag == "PAN":''', '''    s = relations(tag) + leaders(tag)
    if tag == "PAN":''')
rep('''    elif t == "warlord":
        major = WARLORDS[tag][6]
        k = 2 if major else 1
        for i in range(k):
            s += army("%s %s Army" % (adjn, ["First", "Second"][i]), cap if i == 0 else homes[-1],
                      ["infantry"] * (6 if major else 5) + ["cavalry"] + (["artillery"] if major else []), homes)
        ports = [p for p in ps if p in PORTS]
        if ports:
            port = cap if cap in ports else max(ports, key=lambda q: popsize[q])
            s += navy("%s Fleet" % adjn, port, (["manowar", "frigate", "frigate"] if major else ["frigate"]) + ["clipper_transport"] * (4 if major else 2))''',
    '''    elif t == "warlord":
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
            ships = (["manowar"] * 2 + ["frigate"] * 3 + ["clipper_transport"] * 6) if arch == "navy" else \\
                    (["manowar", "frigate", "frigate"] + ["clipper_transport"] * 4) if major else (["frigate"] + ["clipper_transport"] * 2)
            s += navy("%s Fleet" % adjn, port, ships)''')
rep('''def army(name, loc, regs, homes):''', '''def relations(tag):
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
    return "".join("%s = {\\n\\tvalue = %d\\n}\\n\\n" % (k_, v_) for k_, v_ in rel.items() if k_ in owned)


def army(name, loc, regs, homes):''')

# ---- Taiwan joins the South East Asian continent (pops only emigrate to another continent)
rep('''for k in contblocks:
    ids = contblocks[k][0]
    ids += [c[0] for p in list(ids) for c in SPLIT.get(p, [])]''', '''sea_c |= {p for p in ALLP if owner.get(p) == "TWN"}
for k in contblocks:
    ids = contblocks[k][0]
    ids += [c[0] for p in list(ids) for c in SPLIT.get(p, [])]''')

# ---- South East Asian states are civilized so they can receive immigrants; Taiwan gets the same flags
rep('''for tag in SEA_MIGRANT:
    path = os.path.join(OUT, "history", "countries", hname[tag])
    open(path, "a", encoding=ENC, newline="\\r\\n").write("set_country_flag = new_world_nation\\nset_country_flag = old_world_colony\\n")''',
    r'''MIGRANT_FLAGS = "set_country_flag = new_world_nation\nset_country_flag = old_world_colony\n"
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
open(_tw, "a", encoding=ENC, newline="\r\n").write(MIGRANT_FLAGS)''')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched 02_world.py")
