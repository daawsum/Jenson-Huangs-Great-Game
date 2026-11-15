#!/usr/bin/env python3
"""Static checks for a Victoria 2 mod: the silent failures that crash the game or break the map.

usage: check_mod.py "<game dir>" "<Mod Folder>" [--start 1836.1.1]

Reads the mod on top of vanilla (a mod file overrides the vanilla file with the same path).
PROBLEMS are failures that were isolated in the running game (each one crashed it or broke the
map). WARNINGS are departures from what vanilla does; working mods trip some of them, so read
them as "check this", not "this is broken".
A clean run does not prove the mod loads; launch the game as well.
"""
import os, re, sys, glob, collections

ENC = "cp1252"


def read(path):
    with open(path, encoding=ENC, errors="replace") as f:
        return f.read()


def strip(t):
    return re.sub(r"#.*", "", t)


def blocks(text):
    """Yield (key, body) for top-level `key = { ... }` blocks."""
    i, n = 0, len(text)
    pat = re.compile(r"([\w\.\-]+)\s*=\s*\{")
    while True:
        m = pat.search(text, i)
        if not m:
            return
        depth, j = 1, m.end()
        while j < n and depth:
            c = text[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        yield m.group(1), text[m.end():j - 1]
        i = j


def datenum(s):
    y, m, d = (s.split(".") + ["1", "1"])[:3]
    return int(y) * 10000 + int(m) * 100 + int(d)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        raise SystemExit(__doc__)
    V, name = args[0], args[1]
    start = datenum(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 18360101
    M = os.path.join(V, "mod", name)
    if not os.path.isdir(M):
        raise SystemExit("mod folder not found: " + M)
    problems, warnings = [], []
    P = lambda *a: problems.append(" ".join(str(x) for x in a))
    W = lambda *a: warnings.append(" ".join(str(x) for x in a))

    def eff(*rel):                       # the file the game will read
        p = os.path.join(M, *rel)
        return p if os.path.exists(p) else os.path.join(V, *rel)

    def listing(*rel):                   # union of vanilla and mod files in a folder, mod wins by name
        out = {}
        for root in (V, M):
            for f in glob.glob(os.path.join(root, *rel, "*")):
                if os.path.isfile(f):
                    out[os.path.basename(f).lower()] = f
        return out

    def tree(*rel):                      # same, one level of sub-folders (history/provinces/<area>/)
        out = {}
        for root in (V, M):
            for f in glob.glob(os.path.join(root, *rel, "*", "*.txt")):
                out[os.path.basename(f).lower()] = f
        return out

    # ---- the .mod file
    modfiles = [f for f in glob.glob(os.path.join(V, "mod", "*.mod")) if re.search(r'path\s*=\s*"mod/%s"' % re.escape(name), read(f))]
    if not modfiles:
        P("no .mod file in mod/ has path = \"mod/%s\"" % name)
    else:
        t = read(modfiles[0])
        if "user_dir" not in t:
            W(".mod has no user_dir: settings, saves and the map cache are shared with vanilla")
        for rp in re.findall(r'replace_path\s*=\s*"([^"]+)"', t):
            W("replace_path %s: do not rely on it, override vanilla files by name (vanilla diplomacy was seen to survive)" % rp)

    # ---- braces
    for f in glob.glob(os.path.join(M, "**", "*.txt"), recursive=True):
        t = re.sub(r'"[^"\n]*"', '""', strip(read(f)))
        if t.count("{") != t.count("}"):
            W("unbalanced braces:", os.path.relpath(f, M))

    # ---- map
    has_map = os.path.exists(os.path.join(M, "map", "definition.csv")) or os.path.exists(os.path.join(M, "map", "provinces.bmp"))
    dm = strip(read(eff("map", "default.map")))
    sea = {int(x) for x in re.search(r"sea_starts\s*=\s*\{([^}]*)\}", dm).group(1).split()}
    if has_map:
        d = re.search(r'definitions\s*=\s*"([^"]*)"', dm)
        if not d or ("../mod/%s/" % name).lower() not in d.group(1).lower():
            P('map/default.map: definitions must be "../mod/%s/map/definition.csv" or the game reads vanilla\'s definition.csv and new provinces render as water (found: %s)' % (name, d.group(1) if d else None))
    ids, colour = set(), {}
    for l in read(eff("map", "definition.csv")).splitlines()[1:]:
        p = l.split(";")
        if len(p) >= 4 and p[0].strip().isdigit():
            ids.add(int(p[0]))
            try:
                c = tuple(int(float(x)) for x in p[1:4])
            except ValueError:
                continue
            if c in colour:
                W("definition.csv: provinces %s and %s share colour %s" % (colour[c], p[0], c))
            colour[c] = int(p[0])
    mp = int(re.search(r"max_provinces\s*=\s*(\d+)", dm).group(1))
    if mp != max(ids) + 1:
        P("default.map max_provinces = %d but the highest province id is %d (must be id + 1)" % (mp, max(ids)))
    vanilla_ids = {int(l.split(";")[0]) for l in read(os.path.join(V, "map", "definition.csv")).splitlines()[1:] if l.split(";")[0].strip().isdigit()}
    new_ids = ids - vanilla_ids
    regions = {}
    for k, b in blocks(strip(read(eff("map", "region.txt")))):
        regions[k] = [int(x) for x in b.split() if x.isdigit()]
    inreg = collections.Counter(p for ps in regions.values() for p in ps)
    cont = collections.Counter()
    for k, b in blocks(strip(read(eff("map", "continent.txt")))):
        m = re.search(r"provinces\s*=\s*\{([^}]*)\}", b)
        if m:
            cont.update(int(x) for x in m.group(1).split())
    postext = strip(read(eff("map", "positions.txt")))
    pos = {int(k): b for k, b in blocks(postext) if k.isdigit()}

    # ---- province history
    prov = {}
    for base, f in tree("history", "provinces").items():
        m = re.match(r"\s*(\d+)", base)
        if not m:
            continue
        t = re.split(r"\n\s*\d{1,4}\.\d+\.\d+\s*=", "\n" + strip(read(f)))[0]
        o = re.search(r"\bowner\s*=\s*(\w+)", t)
        pid = int(m.group(1))
        if pid in prov and prov[pid]["file"] != f:
            W("two history files for province %d (%s and %s): give the mod file vanilla's exact name" % (pid, os.path.basename(prov[pid]["file"]), os.path.basename(f)))
        prov[pid] = {"owner": o.group(1) if o else None, "naval": bool(re.search(r"\bnaval_base\s*=\s*[1-9]", t)),
                     "terrain": bool(re.search(r"\bterrain\s*=", t)), "file": f, "text": t}
    for p in sorted(new_ids - sea):
        if p not in prov:
            W("new province %d has no history file" % p)
        elif not prov[p]["terrain"]:
            W("new province %d has no terrain = line (working mods set it)" % p)
        if p not in pos:
            W("new province %d has no positions.txt entry" % p)
    for p, d in prov.items():
        if p not in ids:
            W("history for province %d, which is not in definition.csv" % p)
        if d["owner"] and inreg[p] == 0:
            W("owned province %d is in no region (state)" % p)
        if inreg[p] > 1:
            W("province %d is in %d regions" % (p, inreg[p]))
        if d["owner"] and cont[p] == 0:
            W("owned province %d is on no continent" % p)
        if cont[p] > 1:
            W("province %d is on %d continents" % (p, cont[p]))

    # ---- bitmap: colours of new provinces present; port markers in the sea
    pidmap = None
    try:
        import numpy as np
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        img = np.array(Image.open(eff("map", "provinces.bmp")).convert("RGB")).astype(np.int32)
        code = (img[:, :, 0] << 16) | (img[:, :, 1] << 8) | img[:, :, 2]
        present = set(np.unique(code).tolist())
        c2id = {(r << 16) | (g << 8) | b: i for (r, g, b), i in colour.items()}
        for c, i in c2id.items():
            if i in new_ids and c not in present:
                W("new province %d: its colour is not on provinces.bmp" % i)
        uniq, inv = np.unique(code, return_inverse=True)
        pidmap = np.array([c2id.get(int(c), 0) for c in uniq])[inv].reshape(code.shape)
    except ImportError:
        W("numpy/Pillow not installed: bitmap and port-marker checks skipped")
    port_ok = {}
    if pidmap is not None:
        H, Wd = pidmap.shape
        for p, b in pos.items():
            m = re.search(r"naval_base\s*=\s*\{\s*x\s*=\s*([\d\.]+)\s*y\s*=\s*([\d\.]+)", b)
            if m:
                x, y = int(round(float(m.group(1)))), int(round(float(m.group(2))))
                port_ok[p] = 0 <= y < H and 0 <= x < Wd and int(pidmap[y, x]) in sea
        for p, d in prov.items():
            if d["naval"] and port_ok.get(p) is False:
                W("province %d has a naval base but its naval_base marker in positions.txt is not in a sea province" % p)

    # ---- pops
    pops, poptypes_in = collections.Counter(), collections.defaultdict(set)
    cultures_used, religions_used = set(), set()
    popdirs = [d for d in glob.glob(os.path.join(V, "history", "pops", "*")) if os.path.isdir(d)]
    popdir = sorted(os.path.basename(d) for d in popdirs)[0] if popdirs else "1836.1.1"
    for base, f in listing("history", "pops", popdir).items():
        for k, b in blocks(strip(read(f))):
            if k.isdigit():
                for pk, pb in blocks(b):
                    s = re.search(r"size\s*=\s*(\d+)", pb)
                    if s:
                        pops[int(k)] += int(s.group(1))
                        poptypes_in[int(k)].add(pk)
                    cultures_used.update(re.findall(r"culture\s*=\s*(\w+)", pb))
                    religions_used.update(re.findall(r"religion\s*=\s*(\w+)", pb))
    cultures = set()
    for g, b in blocks(strip(read(eff("common", "cultures.txt")))):
        cultures.update(k for k, _ in blocks(b))
    religions = set()
    for g, b in blocks(strip(read(eff("common", "religion.txt")))):
        religions.update(k for k, _ in blocks(b))
    for c in sorted(cultures_used - cultures):
        W("pops use culture '%s', which is not in cultures.txt" % c)
    for r in sorted(religions_used - religions):
        W("pops use religion '%s', which is not in religion.txt" % r)
    known_pop = {os.path.basename(f)[:-4] for f in listing("poptypes").values()}
    native = {"aristocrats", "clergymen", "artisans", "soldiers", "farmers", "slaves", "labourers"}
    odd = [p for p, d in prov.items() if d["owner"] is None and poptypes_in.get(p, set()) - native]
    if odd:
        W("%d unowned provinces hold pop types vanilla never leaves unowned (e.g. province %d: %s)" % (len(odd), odd[0], sorted(poptypes_in[odd[0]] - native)))
    for p in poptypes_in:
        for t in poptypes_in[p] - known_pop:
            W("province %d has pops of unknown type '%s'" % (p, t))

    # ---- countries
    ctext = read(eff("common", "countries.txt"))
    cfile = dict(re.findall(r'^(\w{3})\s*=\s*"countries/([^"]+)"', ctext, re.M))
    owned = collections.defaultdict(set)
    for p, d in prov.items():
        if d["owner"]:
            owned[d["owner"]].add(p)
    govs = {k: set(re.findall(r"(\w+)\s*=\s*yes", b)) for k, b in blocks(strip(read(eff("common", "governments.txt"))))}
    nvs = set(re.findall(r"^(\w+)\s*=\s*\{", strip(read(eff("common", "nationalvalues.txt"))), re.M))
    techs = set()
    for f in listing("technologies").values():
        techs.update(k for k, _ in blocks(strip(read(f))))
    progress = {m.group(1): float(m.group(2)) for m in re.finditer(r"yes_(\w+)\s*=\s*\{[^{}]*?civilization_progress_modifier\s*=\s*([\d\.]+)", strip(read(eff("common", "issues.txt"))))}
    hist = {os.path.basename(f)[:3].upper(): f for f in listing("history", "countries").values()}
    civilized = 0
    for tag in sorted(owned):
        if tag not in cfile:
            W("%s owns provinces but is not in common/countries.txt" % tag)
            continue
        if not os.path.exists(eff("common", "countries", cfile[tag])):
            W("%s: country file countries/%s is missing" % (tag, cfile[tag]))
            continue
        for suf in ("", "_communist", "_fascist", "_monarchy", "_republic"):
            if not os.path.exists(eff("gfx", "flags", tag + suf + ".tga")):
                W("%s: flag gfx/flags/%s%s.tga is missing" % (tag, tag, suf))
        if tag not in hist:
            W("%s owns provinces but has no history/countries file" % tag)
            continue
        h = re.split(r"\n\s*\d{1,4}\.\d+\.\d+\s*=\s*\{", "\n" + strip(read(hist[tag])))[0]
        get = lambda k: (re.search(r"(?m)^\s*%s\s*=\s*\"?([\w\.]+)" % k, h) or [None, None])[1]
        civ = get("civilized") == "yes"
        civilized += civ
        cap = get("capital")
        if not cap or int(cap) not in owned[tag]:
            W("%s: capital %s is not a province it owns" % (tag, cap))
        if sum(pops[p] for p in owned[tag]) < 200:
            W("%s: almost no population (%d). Jan Mayen as a 15-pop country crashed the launch; GFM and HPM run countries of a few thousand pops fine" % (tag, sum(pops[p] for p in owned[tag])))
        for p in owned[tag]:
            if pops[p] == 0:
                W("%s: owned province %d has no pops" % (tag, p))
        parties = {}
        for k, b in blocks(strip(read(eff("common", "countries", cfile[tag])))):
            if k == "party":
                nm = re.search(r'name\s*=\s*"?([^"\n]+)"?', b).group(1).strip()
                sd = re.search(r"start_date\s*=\s*([\d\.]+)", b)
                ed = re.search(r"end_date\s*=\s*([\d\.]+)", b)
                ide = re.search(r"ideology\s*=\s*(\w+)", b)
                parties[nm] = (datenum(sd.group(1)) if sd else 0, datenum(ed.group(1)) if ed else 99999999, ide.group(1) if ide else None)
        rp = get("ruling_party")
        if rp not in parties:
            W("%s: ruling_party %s is not a party in countries/%s" % (tag, rp, cfile[tag]))
        elif not (parties[rp][0] <= start < parties[rp][1]):
            W("%s: ruling_party %s is not active at the start date (vanilla never does this for a country that exists at start)" % (tag, rp))
        gv = get("government")
        if gv not in govs:
            W("%s: unknown government %s" % (tag, gv))
        nv = get("nationalvalue")
        if nv and nv not in nvs:
            W("%s: nationalvalue %s does not exist in this game" % (tag, nv))
        for c in re.findall(r"(?m)^\s*(?:primary_culture|culture)\s*=\s*(\w+)", h):
            if c not in cultures:
                W("%s: unknown culture %s" % (tag, c))
        r = get("religion")
        if r and r not in religions:
            W("%s: unknown religion %s" % (tag, r))
        mytechs = [k for k in re.findall(r"(?m)^\s*(\w+)\s*=\s*1\s*$", h) if k in techs]
        if not civ and mytechs:
            W("%s is uncivilized but starts with %d technologies (vanilla uncivs have none; HPM gives some and works)" % (tag, len(mytechs)))
        if not civ:
            tot = sum(v for k, v in progress.items() if re.search(r"(?m)^\s*%s\s*=\s*yes_%s" % (k, k), h))
            if tot >= 1.0:
                P("%s: starting reforms give %d%% westernization progress; it can westernize on day one" % (tag, round(tot * 100)))
        oob = get("oob")
        f = listing("history", "units").get(("%s_oob.txt" % tag).lower())
        if f:
            t = strip(read(f))
            for k, b in blocks(t):
                if k in ("army", "navy"):
                    for loc in re.findall(r"(?:location|home)\s*=\s*(\d+)", b):
                        if int(loc) not in owned[tag]:
                            W("%s: unit placed in or raised from province %s, which it does not own" % (tag, loc))
                if k == "navy":
                    loc = re.search(r"location\s*=\s*(\d+)", b)
                    if loc and port_ok and port_ok.get(int(loc.group(1))) is not True:
                        P("%s: fleet starts in province %s, whose naval_base marker is missing or not in the sea (crashes on Play)" % (tag, loc.group(1)))
    if civilized < 2:
        P("only %d civilized countries exist at start: pressing Play crashed with 0 and with 1" % civilized)
    elif civilized < 7:
        W("only %d civilized countries exist at start; 1 crashed on Play and 7 worked, in between is untested" % civilized)

    # ---- wars and diplomacy
    mod_wars = [f for f in glob.glob(os.path.join(M, "history", "wars", "*.txt"))]
    if os.path.isdir(os.path.join(M, "history", "wars")) or any("history/wars" in read(f) for f in modfiles):
        real = [f for f in mod_wars if re.search(r"add_attacker", strip(read(f)))]
        if not real:
            P("history/wars is overridden but holds no real war file (crashes on Play); ship a finished vanilla war")
        for f in real:
            t = strip(read(f))
            adds = [datenum(d) for d in re.findall(r"(\d{1,4}\.\d+\.\d+)\s*=\s*\{[^{}]*add_attacker", t)]
            rems = [datenum(d) for d in re.findall(r"(\d{1,4}\.\d+\.\d+)\s*=\s*\{[^{}]*rem_attacker", t)]
            if adds and min(adds) <= start and (not rems or max(rems) > start):
                W("war file %s is active at the start date; make sure every participant exists" % os.path.basename(f))
    for sub in ("diplomacy", "wars"):
        if os.path.isdir(os.path.join(M, "history", sub)):
            mine = {os.path.basename(f).lower() for f in glob.glob(os.path.join(M, "history", sub, "*.txt"))}
            for f in glob.glob(os.path.join(V, "history", sub, "*.txt")):
                if os.path.basename(f).lower() not in mine:
                    W("vanilla history/%s/%s is not overridden by name and may still apply" % (sub, os.path.basename(f)))

    # ---- localisation format
    for f in glob.glob(os.path.join(M, "localisation", "*.csv")):
        for i, l in enumerate(read(f).splitlines()):
            if l.strip() and not l.startswith("#") and l.count(";") < 2:
                W("localisation %s line %d has no ';' separators" % (os.path.basename(f), i + 1))
                break
    if os.path.isfile(os.path.join(V, "movies", "binkplay.exe")) and not os.path.isfile(os.path.join(V, "movies", "game_intro.bik")):
        P("movies/game_intro.bik is missing while binkplay.exe is present: fullscreen start-up will stop on a Bink Error box")

    print("mod: %s | provinces %d (%d new) | countries at start %d (%d civilized) | provinces with pops %d" % (name, len(ids), len(new_ids), len(owned), civilized, len(pops)))
    print("\nPROBLEMS: %d" % len(problems))
    for p in problems[:80]:
        print("  - " + p)
    print("\nWARNINGS: %d" % len(warnings))
    seen = collections.Counter()
    for w in warnings:
        key = re.sub(r"\d+", "#", w)[:60]
        seen[key] += 1
        if seen[key] <= 3:
            print("  - " + w)
    for k, n in seen.items():
        if n > 3:
            print("    (%d more like: %s...)" % (n - 3, k))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
