"""Which textures do the interface files name that exist nowhere - for vanilla's own files and RobloxDoD's?"""
import os, re, glob, filecmp
from config import *

R = os.path.join(V, "mod", "RobloxDOD 1.8")
strip = lambda t: re.sub(r"#.*", "", t)


def exists(rel, roots):
    base = os.path.splitext(rel)[0]
    for r in roots:
        for ext in (os.path.splitext(rel)[1], ".dds", ".tga", ".png"):
            if os.path.exists(os.path.join(r, base + ext)):
                return True
    return False


def missing(folder, roots):
    out = []
    for f in glob.glob(os.path.join(folder, "*.gfx")):
        for tex in re.findall(r'texture[fF]ile\s*=\s*"([^"]+)"', strip(open(f, encoding=ENC, errors="replace").read())):
            rel = tex.replace("\\\\", "/").replace("\\", "/")
            if not exists(rel, roots):
                out.append((os.path.basename(f), rel))
    return out


mv = missing(os.path.join(V, "interface"), [V])
mr = missing(os.path.join(R, "interface"), [R, V])
print("vanilla interface, textures missing even allowing .dds/.tga swap:", len(mv), mv[:5])
print("roblox interface, same test:", len(mr), mr[:10])
print("roblox-only missing:", sorted(set(mr) - set(mv))[:20])
# how do roblox's interface files differ from vanilla's?
for f in sorted(os.listdir(os.path.join(R, "interface"))):
    vf = os.path.join(V, "interface", f)
    rf = os.path.join(R, "interface", f)
    if not os.path.exists(vf):
        print("  only in roblox:", f)
        continue
    a = open(vf, encoding=ENC, errors="replace").read().splitlines()
    b = open(rf, encoding=ENC, errors="replace").read().splitlines()
    import difflib
    d = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    print("  %-28s vanilla %5d lines, roblox %5d, changed lines %d" % (f, len(a), len(b), len(d)))
print("roblox gfx/interface files:", sorted(os.listdir(os.path.join(R, "gfx", "interface"))))
print("roblox gfx subfolders:", sorted(os.listdir(os.path.join(R, "gfx"))))
