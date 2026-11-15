"""Stage 4: static checks on the generated mod."""
import os, re, glob, json, collections
from PIL import Image
import numpy as np
from config import *

M = json.load(open(os.path.join(WORK, "map.json")))
Wd = json.load(open(os.path.join(WORK, "world.json")))
OWNER = {int(k): v for k, v in Wd["owner"].items()}
SEA = set(M["sea"])
problems = []


def bad(*a):
    problems.append(" ".join(str(x) for x in a))


def strip(t):
    return re.sub(r"#.*", "", t)


def mod_or_vanilla(*rel):
    p = os.path.join(OUT, *rel)
    return p if os.path.exists(p) else os.path.join(V, *rel)


# 1 braces
files = glob.glob(os.path.join(OUT, "**", "*.txt"), recursive=True)
for f in files:
    t = re.sub(r'"[^"\n]*"', '""', strip(open(f, encoding=ENC, errors="replace").read()))
    if t.count("{") != t.count("}"):
        bad("brace mismatch", os.path.relpath(f, OUT), t.count("{"), t.count("}"))
print("text files checked:", len(files))

# tags, country files, flags
ctxt = open(os.path.join(OUT, "common", "countries.txt"), encoding=ENC).read()
cfile = dict(re.findall(r'^(\w{3})\s*=\s*"countries/([^"]+)"', ctxt, re.M))
tags = set(cfile)
for t, fn in cfile.items():
    if not os.path.exists(mod_or_vanilla("common", "countries", fn)):
        bad("missing country file", t, fn)
    for suf in ["", "_communist", "_fascist", "_monarchy", "_republic"]:
        if t != "REB" and not os.path.exists(mod_or_vanilla("gfx", "flags", t + suf + ".tga")):
            bad("missing flag", t + suf)

# vanilla vocabulary
vocab = set()
for d in ("events", "decisions", "common", "history/countries", "poptypes"):
    for f in glob.glob(os.path.join(V, d, "*.txt")):
        vocab |= set(re.findall(r"([A-Za-z_][\w]*)\s*=", strip(open(f, encoding=ENC, errors="replace").read())))
cultures = set(re.findall(r"^\t(\w+)\s*=\s*\{", open(mod_or_vanilla("common", "cultures.txt"), encoding=ENC).read(), re.M))
religions = set(re.findall(r"^\t(\w+)\s*=\s*\{", open(mod_or_vanilla("common", "religion.txt"), encoding=ENC).read(), re.M))
# every pop must use a culture and religion that exist
for f in glob.glob(os.path.join(OUT, "history", "pops", "1836.1.1", "*.txt")):
    t = open(f, encoding=ENC).read()
    for c in set(re.findall(r"culture\s*=\s*(\w+)", t)) - cultures:
        bad("pop culture does not exist", c)
    for r in set(re.findall(r"religion\s*=\s*(\w+)", t)) - religions:
        bad("pop religion does not exist", r)
mods = set(re.findall(r"^(\w+)\s*=\s*\{", open(os.path.join(OUT, "common", "event_modifiers.txt"), encoding=ENC).read(), re.M))
cbs = set(re.findall(r"^(\w+)\s*=\s*\{", open(os.path.join(OUT, "common", "cb_types.txt"), encoding=ENC).read(), re.M))
regions = {}
for k, body, s0, e0 in blocks(strip(open(os.path.join(OUT, "map", "region.txt"), encoding=ENC).read())):
    regions[k] = [int(x) for x in body.split()]

for rel in ("decisions/WarlordEra.txt", "events/WarlordEra.txt"):
    t = re.sub(r'"[^"\n]*"', '""', strip(open(os.path.join(OUT, rel), encoding=ENC).read()))
    unk = collections.Counter()
    for k in re.findall(r"([A-Za-z_]\w*)\s*=", t):
        if k in vocab or k in tags or k in mods or k == "political_decisions":
            continue
        if re.match(r"(charter_|settle_|form_)", k) or ("did_" + k) in t:
            continue
        unk[k] += 1
    print(rel, "tokens not seen in vanilla:", dict(unk))
    for a, b in re.findall(r"\b(tag|exists|change_tag|release_vassal|secede_province|add_core|target)\s*=\s*(\w+)", t):
        if b not in tags and b != "THIS":
            bad("unknown tag", rel, a, b)
    for b in re.findall(r"\b([A-Z]{3})\s*=\s*\{", t):
        if b not in tags and b not in ("NOT", "AND"):
            bad("unknown tag scope", rel, b)
    for b in re.findall(r"add_accepted_culture\s*=\s*(\w+)", t):
        if b not in cultures:
            bad("unknown culture", b)
    for b in re.findall(r"name\s*=\s*(\w+)\s+duration", t) + re.findall(r"has_country_modifier\s*=\s*(\w+)", t):
        if b not in mods:
            bad("unknown modifier", b)
    for b in re.findall(r"region\s*=\s*(\w+)", t):
        if b not in regions:
            bad("unknown region", b)
    for b in re.findall(r"type\s*=\s*(\w+)\s+months", t):
        if b not in cbs:
            bad("unknown cb", b)
    for b in re.findall(r"owns\s*=\s*(\d+)", t):
        if int(b) not in OWNER:
            bad("owns unknown province", b)

# modifier effect names
modvocab = set()
for f in ["event_modifiers.txt", "static_modifiers.txt", "nationalvalues.txt", "triggered_modifiers.txt", "issues.txt"]:
    modvocab |= set(re.findall(r"([a-z_]+)\s*=\s*-?[\d\.]+", strip(rd("common", f))))
for f in glob.glob(os.path.join(V, "technologies", "*.txt")) + glob.glob(os.path.join(V, "inventions", "*.txt")):
    modvocab |= set(re.findall(r"([a-z_]+)\s*=\s*-?[\d\.]+", strip(open(f, encoding=ENC, errors="replace").read())))
t = open(os.path.join(OUT, "common", "event_modifiers.txt"), encoding=ENC).read()
t = t[t.index("##### WARLORD ERA #####"):]
print("modifier effects not seen in vanilla:", sorted(set(re.findall(r"\t([a-z_]+)\s*=", t)) - modvocab))

# provinces
ids, defc = set(), {}
for l in open(os.path.join(OUT, "map", "definition.csv"), encoding=ENC).read().splitlines()[1:]:
    p = l.split(";")
    if p[0].strip():
        ids.add(int(p[0]))
        defc[(int(float(p[1])) << 16) | (int(float(p[2])) << 8) | int(float(p[3]))] = int(p[0])
hist = {}
for f in glob.glob(os.path.join(OUT, "history", "provinces", "*", "*.txt")):
    hist[int(re.match(r"\s*(\d+)", os.path.basename(f)).group(1))] = open(f, encoding=ENC).read()
print("definition ids:", len(ids), "max", max(ids), "history files", len(hist))
dm = open(os.path.join(OUT, "map", "default.map"), encoding=ENC).read()
if int(re.search(r"max_provinces\s*=\s*(\d+)", dm).group(1)) != max(ids) + 1:
    bad("max_provinces mismatch")
inreg = collections.Counter(p for ps in regions.values() for p in ps)
for p, c in inreg.items():
    if c > 1:
        bad("province in several regions", p)
    if p not in ids:
        bad("region lists unknown province", p)
missing = [p for p in hist if p not in inreg]
if missing:
    bad("history provinces not in any region", len(missing), missing[:20])
ct = open(os.path.join(OUT, "map", "continent.txt"), encoding=ENC).read()
cont = collections.Counter()
for k, body, s, e in blocks(ct):
    for x in re.search(r"provinces\s*=\s*\{([^}]*)\}", body).group(1).split():
        cont[int(x)] += 1
dup = [p for p, c in cont.items() if c > 1]
if dup:
    bad("province on two continents", dup[:10])
noc = [p for p in hist if p not in cont]
if noc:
    bad("history provinces without continent", len(noc), noc[:20])
pos = open(os.path.join(OUT, "map", "positions.txt"), encoding=ENC).read()
posids = {int(k) for k, b, s, e in blocks(pos) if k.isdigit()}
newp = [p for p in ids if p > M["MAXID"]]
if [p for p in newp if p not in posids]:
    bad("new province without positions")
if [p for p in newp if p not in hist]:
    bad("new province without history")
loct = open(os.path.join(OUT, "localisation", "00_warlord_era.csv"), encoding=ENC).read()
if [p for p in newp if "PROV%d;" % p not in loct]:
    bad("new province without name")

Image.MAX_IMAGE_PIXELS = None
img = np.array(Image.open(os.path.join(OUT, "map", "provinces.bmp")).convert("RGB")).astype(np.int32)
code = set(np.unique((img[:, :, 0] << 16) | (img[:, :, 1] << 8) | img[:, :, 2]).tolist())
print("colours on map:", len(code), "| undefined colours on map:", len(code - set(defc)))
if [defc[c] for c in defc if c not in code and defc[c] > M["MAXID"]]:
    bad("new province colour missing from bitmap")
vb, nb = os.path.join(V, "map", "provinces.bmp"), os.path.join(OUT, "map", "provinces.bmp")
print("bitmap header vanilla:", open(vb, "rb").read(54).hex()[:108])
print("bitmap header new    :", open(nb, "rb").read(54).hex()[:108])

# pops
pp = set()
for f in glob.glob(os.path.join(OUT, "history", "pops", "1836.1.1", "*.txt")):
    for k, b, s, e in blocks(open(f, encoding=ENC).read()):
        if k.isdigit():
            if int(k) in pp:
                bad("pops listed twice", k)
            pp.add(int(k))
if [p for p in pp if p not in ids]:
    bad("pops for unknown province")
nop = [p for p in hist if OWNER.get(p) and p not in pp]
print("owned provinces without pops:", len(nop), nop[:10])

# countries
owned = collections.defaultdict(set)
for p, o in OWNER.items():
    if o:
        owned[o].add(p)
govs = {}
for k, b, s, e in blocks(strip(rd("common", "governments.txt"))):
    govs[k] = set(re.findall(r"(\w+)\s*=\s*yes", b))
chist = {}
for f in glob.glob(os.path.join(OUT, "history", "countries", "*.txt")):
    chist[os.path.basename(f)[:3]] = open(f, encoding=ENC).read()
for tag in owned:
    if tag not in tags:
        bad("owner tag not defined", tag)
        continue
    h = chist.get(tag)
    if not h:
        bad("no history for", tag)
        continue
    cap = int(re.search(r"capital\s*=\s*(\d+)", h).group(1))
    if cap not in owned[tag]:
        bad("capital not owned", tag, cap)
    rp = re.search(r'ruling_party\s*=\s*"?(\w+)"?', h)
    gv = re.search(r"government\s*=\s*(\w+)", h)
    cf = open(mod_or_vanilla("common", "countries", cfile[tag]), encoding=ENC, errors="replace").read()
    if not rp or rp.group(1) not in cf:
        bad("ruling party missing", tag, rp and rp.group(1))
    else:
        for k, b, s, e in blocks(cf):
            if k == "party" and '"%s"' % rp.group(1) in b:
                ide = re.search(r"ideology\s*=\s*(\w+)", b).group(1)
                if gv and ide not in govs.get(gv.group(1), {ide}):
                    bad("party ideology not allowed by government", tag, gv.group(1), ide)
    for c in re.findall(r"culture\s*=\s*(\w+)", h):
        if c not in cultures:
            bad("unknown culture in history", tag, c)
    r = re.search(r"religion\s*=\s*(\w+)", h)
    if r and r.group(1) not in religions:
        bad("unknown religion", tag, r.group(1))
    oob = os.path.join(OUT, "history", "units", "%s_oob.txt" % tag)
    if not os.path.exists(oob):
        bad("no oob", tag)
        continue
    for hm in re.findall(r"(?:home|location)\s*=\s*(\d+)", open(oob, encoding=ENC).read()):
        if int(hm) not in owned[tag]:
            bad("unit home/location not owned", tag, hm)
civ = [t for t, h in chist.items() if re.search(r"civilized\s*=\s*yes", h)]
print("civilized in history:", len(civ), "| of which exist at start:", len([t for t in civ if t in owned]),
      "| non-warlord civilized at start:", sorted(t for t in civ if t in owned and t not in WARLORDS))

for f in glob.glob(os.path.join(OUT, "localisation", "*.csv")):
    for i, l in enumerate(open(f, encoding=ENC).read().splitlines()):
        if l and (l.count(";") != 14 or not l.endswith("x")):
            bad("bad localisation line", os.path.basename(f), i + 1, l[:60])
print("\nPROBLEMS:", len(problems))
for p in problems[:60]:
    print("  -", p)
