"""Apply test variants to the INSTALLED copy of the mod (for crash bisecting only).
usage: variant.py name [name ...]"""
import os, re, glob, sys, json, shutil

V = r"D:\SteamLibrary\steamapps\common\Victoria 2"
G = os.path.join(V, "mod", "Warlord Era")
ENC = "cp1252"
W = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "world.json")))
OWNER = {int(k): v for k, v in W["owner"].items()}


def files(sub):
    return glob.glob(os.path.join(G, *sub.split("/"), "**", "*.txt"), recursive=True)


def edit(f, fn):
    t = open(f, encoding=ENC).read()
    open(f, "w", encoding=ENC, newline="\r\n").write(fn(t))


def pid(f):
    return int(re.match(r"\s*(\d+)", os.path.basename(f)).group(1))


for v in sys.argv[1:]:
    if v == "nounits":
        for f in files("history/units"):
            open(f, "w").write("")
    elif v.startswith("nonavy:"):         # nonavy:TAG,TAG  strip the fleet of these tags only
        for t_ in v.split(":")[1].split(","):
            f = os.path.join(G, "history", "units", t_ + "_oob.txt")
            edit(f, lambda t: t[:t.find("navy = {")] if "navy = {" in t else t)
    elif v == "nonavy":
        for f in files("history/units"):
            edit(f, lambda t: t[:t.find("navy = {")] if "navy = {" in t else t)
    elif v == "nonavalbase":
        for f in files("history/provinces"):
            edit(f, lambda t: re.sub(r"naval_base = 1\r?\n", "", t))
    elif v == "nofort":
        for f in files("history/provinces"):
            edit(f, lambda t: re.sub(r"fort = 1\r?\n", "", t))
    elif v.startswith("unown:"):          # unown:china | unown:world | unown:new | unown:TAG,TAG
        what = v.split(":")[1]
        for f in files("history/provinces"):
            p = pid(f)
            o = OWNER.get(p)
            hit = (what == "china" and "china" in f.replace("\\", "/").split("/")[-2]) or \
                  (what == "world" and "china" not in f.replace("\\", "/").split("/")[-2]) or \
                  (what == "new" and p > 3248) or (o in what.split(","))
            if hit:
                edit(f, lambda t: re.sub(r"(owner|controller|add_core) = \w+\r?\n", "", t))
    elif v.startswith("half:"):           # half:a/b  unown owned provinces whose tag hashes into slice a of b
        a, b = map(int, v.split(":")[1].split("/"))
        tags = sorted({o for o in OWNER.values() if o})
        sel = set(tags[a::b])
        print("unowning tags:", " ".join(sorted(sel)))
        for f in files("history/provinces"):
            if OWNER.get(pid(f)) in sel:
                edit(f, lambda t: re.sub(r"(owner|controller|add_core) = \w+\r?\n", "", t))
    elif v.startswith("rm:"):             # rm:relative/path inside the installed mod
        t = os.path.normpath(os.path.join(G, v[3:]))
        assert t.startswith(G + os.sep)
        shutil.rmtree(t) if os.path.isdir(t) else os.remove(t)
    elif v == "norp":                     # drop every replace_path from the installed .mod
        mp = G + ".mod"
        t = open(mp).read()
        open(mp, "w").write("".join(l for l in t.splitlines(True) if "replace_path" not in l))
    elif v.startswith("norp:"):           # drop one replace_path
        mp = G + ".mod"
        t = open(mp).read()
        open(mp, "w").write("".join(l for l in t.splitlines(True) if v[5:] not in l))
    elif v.startswith("chist:"):          # drop lines matching a regex from every country history file
        rx = re.compile(v[6:])
        for f in files("history/countries"):
            edit(f, lambda t: "\n".join(l for l in t.splitlines() if not rx.search(l)) + "\n")
    elif v.startswith("vhist:"):          # vhist:a/b  give slice a of b of the country history files vanilla's text back
        a_, b_ = map(int, v.split(":")[1].split("/"))
        fs = sorted(files("history/countries"), key=lambda f: os.path.basename(f))
        sel = fs[a_::b_]
        van = {os.path.basename(f)[:3]: f for f in glob.glob(os.path.join(V, "history", "countries", "*.txt"))}
        print("vanilla text for:", " ".join(os.path.basename(f)[:3] for f in sel))
        for f in sel:
            tag = os.path.basename(f)[:3]
            if tag in van:
                shutil.copyfile(van[tag], f)
            else:
                os.remove(f)
    elif v == "vanillapoptypes":
        shutil.rmtree(os.path.join(G, "poptypes"), ignore_errors=True)
    elif v == "nobank":
        shutil.rmtree(os.path.join(G, "poptypes"), ignore_errors=True)
        for n in ("production_types.txt", "issues.txt"):
            try:
                os.remove(os.path.join(G, "common", n))
            except OSError:
                pass
        for f in files("history/provinces"):
            if pid(f) in (2131, 2133):
                edit(f, lambda t: re.sub(r"(owner|controller|add_core) = \w+\r?\n", "", t).replace("precious_metal", "fish"))
        for f in files("history/pops"):
            edit(f, lambda t: t.replace("bankers", "farmers"))
    elif v == "nocores":
        for f in files("history/provinces"):
            edit(f, lambda t: "\n".join(l for l in t.splitlines() if not l.startswith("add_core") or l.split()[-1] == (OWNER.get(pid(f)) or "")) + "\n")
    else:
        raise SystemExit("unknown variant " + v)
print("applied", sys.argv[1:])
