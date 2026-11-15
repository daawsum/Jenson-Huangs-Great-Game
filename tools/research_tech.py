"""Research: can RobloxDOD 1.8's technologies and inventions run on a vanilla-based mod?"""
import os, re, glob, collections
from config import *

R = os.path.join(V, "mod", "RobloxDOD 1.8")
print("mod file:", open(R + ".mod").read().replace("\n", " | ")[:400])


def strip(t):
    return re.sub(r"#.*", "", t)


def names(folder, root):
    out = collections.OrderedDict()
    for f in sorted(glob.glob(os.path.join(root, folder, "*.txt"))):
        for k, b, s, e in blocks(strip(open(f, encoding=ENC, errors="replace").read())):
            out[k] = (os.path.basename(f), b)
    return out


vt, rt = names("technologies", V), names("technologies", R)
vi, ri = names("inventions", V), names("inventions", R)
print("technologies vanilla/roblox:", len(vt), len(rt), "| only roblox:", [k for k in rt if k not in vt][:20], "| only vanilla:", [k for k in vt if k not in rt][:20])
print("inventions   vanilla/roblox:", len(vi), len(ri), "| only roblox:", len([k for k in ri if k not in vi]), "| only vanilla:", len([k for k in vi if k not in ri]))
print("tech files:", sorted({v[0] for v in rt.values()}), "| invention files:", sorted({v[0] for v in ri.values()}))

# what do roblox's files reference that vanilla may lack?
def idset(root, rel, pat=r"^(\w+)\s*=\s*\{"):
    p = os.path.join(root, *rel.split("/"))
    return set(re.findall(pat, strip(open(p, encoding=ENC, errors="replace").read()), re.M)) if os.path.exists(p) else set()


units_v = {os.path.basename(f)[:-4] for f in glob.glob(os.path.join(V, "units", "*.txt"))}
units_r = {os.path.basename(f)[:-4] for f in glob.glob(os.path.join(R, "units", "*.txt"))}
goods_v = set(re.findall(r"^\t(\w+)\s*=\s*\{", strip(rd("common", "goods.txt")), re.M))
builds_v = idset(V, "common/buildings.txt")
text = "\n".join(b for _, b in list(rt.values()) + list(ri.values()))
used_units = set(re.findall(r"activate_unit\s*=\s*(\w+)", text))
used_build = set(re.findall(r"activate_building\s*=\s*(\w+)", text))
unit_blocks = set()
for k, b in list(rt.values()) + list(ri.values()):
    for kk, bb, s, e in blocks(b):
        unit_blocks.add(kk)
print("units vanilla:", len(units_v), "| roblox:", len(units_r), "| roblox-only unit files:", sorted(units_r - units_v))
print("activate_unit not in vanilla units:", sorted(used_units - units_v))
print("activate_building not in vanilla buildings:", sorted(used_build - builds_v))
keys = collections.Counter(re.findall(r"([A-Za-z_]\w*)\s*=", text))
vkeys = set()
for d in ("technologies", "inventions", "common", "events", "decisions", "units"):
    for f in glob.glob(os.path.join(V, d, "*.txt")):
        vkeys |= set(re.findall(r"([A-Za-z_]\w*)\s*=", strip(open(f, encoding=ENC, errors="replace").read())))
vkeys |= goods_v | units_v | set(vt) | set(vi)
unk = {k: n for k, n in keys.items() if k not in vkeys and k not in rt and k not in ri}
print("keys in roblox tech/inventions unknown to vanilla:", dict(sorted(unk.items(), key=lambda x: -x[1])[:60]))
# the tech tree definition
tv = strip(rd("common", "technology.txt"))
tr = strip(open(os.path.join(R, "common", "technology.txt"), encoding=ENC, errors="replace").read())
print("common/technology.txt identical to vanilla:", tv.split() == tr.split())
m = re.search(r"culture_tech\s*=\s*\{(.*?)\n\}", tr, re.S)
print("culture folders in roblox technology.txt:", re.findall(r"(\w+)\s*=\s*\{([^}]*)\}", tr[tr.find("folders"):tr.find("folders") + 6000])[20:32] if "folders" in tr else None)
for k, (f, b) in rt.items():
    if f.startswith("culture"):
        a = re.search(r"area\s*=\s*(\w+)", b)
        y = re.search(r"year\s*=\s*(\d+)", b)
        if a and a.group(1) in ("political_thought", "social_thought"):
            print("   ", a.group(1), y.group(1) if y else "?", k)
