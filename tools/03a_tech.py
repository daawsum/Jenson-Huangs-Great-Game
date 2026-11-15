"""Stage 3a: technologies and inventions taken verbatim from RobloxDoD 1.8.

Copied unchanged: technologies/*.txt, inventions/*.txt, common/technology.txt, units/*.txt.
Those files need things vanilla does not have, so these come along with them:
  * four unit types (infantry and artillery, offensive and defensive) with their icons and the
    interface files that list them,
  * the synthetic rubber factory (building + production type),
  * three national values the inventions test for (productivity, education, diplomacy),
  * names for every technology, invention, unit, school and national value.
Vanilla's national values stay (every country history uses them); RobloxDoD's are added.
Run after 03_gameplay.py and before 03b/03d, which patch files this stage writes.
"""
import os, re, glob, shutil
from config import *

R = os.path.join(V, "mod", "RobloxDOD 1.8")
if not os.path.isdir(R):
    raise SystemExit("RobloxDoD 1.8 is not installed")
strip = lambda t: re.sub(r"#.*", "", t)
rr = lambda *p: open(os.path.join(R, *p), encoding=ENC, errors="replace").read()


def copy_folder(rel, pattern="*"):
    dst = os.path.join(OUT, rel)
    shutil.rmtree(dst, ignore_errors=True)
    os.makedirs(dst)
    n = 0
    for f in glob.glob(os.path.join(R, rel, pattern)):
        if os.path.isfile(f):
            shutil.copyfile(f, os.path.join(dst, os.path.basename(f)))
            n += 1
    return n


print("technologies:", copy_folder("technologies", "*.txt"), "| inventions:", copy_folder("inventions", "*.txt"), "| units:", copy_folder("units", "*.txt"))
shutil.copyfile(os.path.join(R, "common", "technology.txt"), os.path.join(OUT, "common", "technology.txt"))

# ---- interface for the new unit types: RobloxDoD's interface files and the textures they name
n = copy_folder("interface")
os.makedirs(os.path.join(OUT, "gfx", "interface"), exist_ok=True)
g = 0
for f in glob.glob(os.path.join(R, "gfx", "interface", "*")):
    if os.path.isfile(f):
        shutil.copyfile(f, os.path.join(OUT, "gfx", "interface", os.path.basename(f)))
        g += 1
print("interface files:", n, "| interface textures:", g)
missing = []
for f in glob.glob(os.path.join(OUT, "interface", "*.gfx")):
    for tex in re.findall(r'texture[fF]ile\s*=\s*"([^"]+)"', strip(open(f, encoding=ENC, errors="replace").read())):
        rel = tex.replace("\\\\", "/").replace("\\", "/")
        base = os.path.splitext(rel)[0]   # the engine loads .dds when a .tga is named and the reverse
        if not any(os.path.exists(os.path.join(r_, base + e_)) for r_ in (OUT, V) for e_ in (".dds", ".tga")):
            for extra in (os.path.join(R, rel),):
                if os.path.exists(extra):
                    os.makedirs(os.path.dirname(os.path.join(OUT, rel)), exist_ok=True)
                    shutil.copyfile(extra, os.path.join(OUT, rel))
                    break
            else:
                missing.append((os.path.basename(f), rel))
print("textures named by the interface files but found nowhere:", len(missing), missing[:6])

# ---- national values: vanilla's plus the ones RobloxDoD's inventions test for
nv_v = rd("common", "nationalvalues.txt")
nv_r = rr("common", "nationalvalues.txt")
have = set(re.findall(r"^(\w+)\s*=\s*\{", strip(nv_v), re.M))
add = ""
for k, b, s_, e_ in blocks(strip(nv_r)):
    if k not in have:
        add += "\n%s = {%s}\n" % (k, b)
        have.add(k)
wr("common/nationalvalues.txt", nv_v.rstrip() + "\n" + add)
print("national values now:", sorted(have))

# ---- the synthetic rubber factory
def grab(text, name):
    m = re.search(r"(?m)^%s\s*=\s*\{" % name, text)
    d, j = 1, m.end()
    while d:
        d += text[j] == "{"
        d -= text[j] == "}"
        j += 1
    return text[m.start():j]


b_v = rd("common", "buildings.txt")
if "synthetic_rubber_factory" not in b_v:
    wr("common/buildings.txt", b_v.rstrip() + "\n\n" + grab(strip(rr("common", "buildings.txt")), "synthetic_rubber_factory") + "\n")
p_v = rd("common", "production_types.txt")
if "synthetic_rubber_factory" not in p_v:
    wr("common/production_types.txt", p_v.rstrip() + "\n\n" + grab(strip(rr("common", "production_types.txt")), "synthetic_rubber_factory") + "\n")

# ---- everything the technology files switch on must exist
text = ""
for d in ("technologies", "inventions"):
    for f in glob.glob(os.path.join(OUT, d, "*.txt")):
        text += strip(open(f, encoding=ENC, errors="replace").read())
units = {os.path.basename(f)[:-4] for f in glob.glob(os.path.join(OUT, "units", "*.txt"))}
builds = set(re.findall(r"(?m)^(\w+)\s*=\s*\{", strip(open(os.path.join(OUT, "common", "buildings.txt"), encoding=ENC).read())))
bad_u = sorted(set(re.findall(r"activate_unit\s*=\s*(\w+)", text)) - units)
bad_b = sorted(set(re.findall(r"activate_building\s*=\s*(\w+)", text)) - builds)
bad_nv = sorted(set(re.findall(r"nationalvalue\s*=\s*(\w+)", text)) - have)
assert not (bad_u or bad_b or bad_nv), (bad_u, bad_b, bad_nv)
print("every unit, building and national value the technologies name exists")

# ---- names: RobloxDoD's text for anything vanilla has no text for
def keys_of(root):
    out = {}
    for f in sorted(glob.glob(os.path.join(root, "localisation", "*.csv"))):
        for l in open(f, encoding=ENC, errors="replace").read().splitlines():
            p = l.split(";")
            if len(p) > 1 and p[0] and p[0] not in out:
                out[p[0]] = p[1]
    return out


lv, lr = keys_of(V), keys_of(R)
want = set()
for d in ("technologies", "inventions"):
    for f in glob.glob(os.path.join(OUT, d, "*.txt")):
        for k, b, s_, e_ in blocks(strip(open(f, encoding=ENC, errors="replace").read())):
            want |= {k, k + "_desc"}
want |= units | {u + "_desc" for u in units} | have | {k + "_desc" for k in have}
want |= set(re.findall(r"\n\t(\w+_tech_school|traditional_academic)\s*=", strip(rr("common", "technology.txt"))))
want |= set(re.findall(r"(?m)^\t(\w+)\s*=\s*\{", strip(rr("common", "technology.txt"))))
lines = ["%s;%s;;;;;;;;;;;;;x" % (k, lr[k].replace(";", ",")) for k in sorted(want) if k in lr and lr[k] and lv.get(k) != lr[k]]
wr("localisation/00_warlord_era_tech.csv", "\n".join(lines) + "\n")
print("names copied from RobloxDoD:", len(lines))
