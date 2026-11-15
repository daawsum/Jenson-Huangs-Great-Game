"""One-off patch: fixes for the goods icons, the war-goal shield, free peoples, and an unproven modifier key."""
import re

# ------------------------------------------------------------------ 03a_tech.py: goods icons
s = open("03a_tech.py", encoding="utf-8").read()
a = '''for f in glob.glob(os.path.join(R, "gfx", "interface", "*")):
    if os.path.isfile(f):
        shutil.copyfile(f, os.path.join(OUT, "gfx", "interface", os.path.basename(f)))
        g += 1
print("interface files:", n, "| interface textures:", g)
'''
assert s.count(a) == 1
s = s.replace(a, r'''# RobloxDoD has no "dye" good, so its goods icon strips hold 48 icons where this mod's goods list
# (vanilla's) has 49. Its strips and its frame counts must NOT come along, or every goods icon after
# dye is drawn one place off (coal shows as sulphur, opium as automobiles, ...).
GOODS_STRIPS = {"resources.dds", "resources_big.dds", "resources_small.dds"}
for f in glob.glob(os.path.join(R, "gfx", "interface", "*")):
    if os.path.isfile(f) and os.path.basename(f) not in GOODS_STRIPS:
        shutil.copyfile(f, os.path.join(OUT, "gfx", "interface", os.path.basename(f)))
        g += 1
for f in GOODS_STRIPS:
    p_ = os.path.join(OUT, "gfx", "interface", f)
    if os.path.exists(p_):
        os.remove(p_)
print("interface files:", n, "| interface textures:", g)


def sprites(text):
    """sprite name -> (texture, frames, span of the frames number) for every sprite block"""
    out = {}
    for m in re.finditer(r"(?is)(spriteType|corneredTileSpriteType|maskedShieldType|progressbartype)\s*=\s*\{(.*?)\n\t\}", text):
        b = m.group(2)
        nm = re.search(r'name\s*=\s*"([^"]+)"', b)
        tx = re.search(r'texture[fF]ile\s*=\s*"([^"]+)"', b)
        fr = re.search(r"(?i)noOfFrames\s*=\s*(\d+)", b)
        if nm and tx and fr:
            out[nm.group(1)] = (os.path.basename(tx.group(1).replace("\\\\", "/").replace("\\", "/")).lower(), int(fr.group(1)), (m.start(2) + fr.start(1), m.start(2) + fr.end(1)))
    return out


# A sprite whose picture is still vanilla's must keep vanilla's frame count, whatever RobloxDoD says.
ours = {f.lower() for f in os.listdir(os.path.join(OUT, "gfx", "interface"))}
fixed = []
for f in glob.glob(os.path.join(OUT, "interface", "*.gfx")):
    vf = os.path.join(V, "interface", os.path.basename(f))
    if not os.path.exists(vf):
        continue
    t = open(f, encoding=ENC, errors="replace").read()
    vs = sprites(open(vf, encoding=ENC, errors="replace").read())
    for nm, (tex, fr, sp) in sorted(sprites(t).items(), key=lambda x: -x[1][2][0]):
        if nm in vs and vs[nm][0] == tex and vs[nm][1] != fr and tex not in ours and os.path.splitext(tex)[0] + ".tga" not in ours:
            t = t[:sp[0]] + str(vs[nm][1]) + t[sp[1]:]
            fixed.append("%s %d->%d" % (nm, fr, vs[nm][1]))
    open(f, "w", encoding=ENC, newline="").write(t)
print("sprites put back to vanilla's frame count (their picture is vanilla's):", fixed)
ngoods = len(re.findall(r"(?m)^\t(\w+)\s*=\s*\{", strip(rd("common", "goods.txt"))))
for f in ("core.gfx", "mapitems.gfx"):
    for nm, (tex, fr, sp) in sprites(open(os.path.join(OUT, "interface", f), encoding=ENC, errors="replace").read()).items():
        if tex.startswith("resources"):
            assert fr == ngoods + 1, (f, nm, fr, ngoods)
''')
open("03a_tech.py", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ 03g_takecapital.py: shield, free peoples, marker tags
s = open("03g_takecapital.py", encoding="utf-8").read()
a = r'''SHIELD = "\n\t\tNOT = {\n\t\t\ttag = HRE\n\t\t\tcivilized = no\n\t\t}"'''
assert s.count(a) == 1
s = s.replace(a, r'''# NOT with two conditions means "neither of them", so the two must sit inside an AND: without it this
# line forbade every war goal against any uncivilized country at all.
SHIELD = "\n\t\tNOT = {\n\t\t\tAND = {\n\t\t\t\ttag = HRE\n\t\t\t\tcivilized = no\n\t\t\t}\n\t\t}"

# Free Peoples goes: its "who to free" list offered the five state-size marker tags, which have a core
# on every province in the world but are not countries, and pointing at one crashed the game. The
# five sized versions are removed outright; the original stays in the file, never usable, so nothing
# that names it by key is left dangling.
def _block(text, name):
    m_ = re.search(r"(?m)^%s\s*=\s*\{" % name, text)
    if not m_:
        return None
    d_, j_ = 1, m_.end()
    while d_:
        if text[j_] == "#":
            j_ = text.index("\n", j_)
            continue
        d_ += text[j_] == "{"
        d_ -= text[j_] == "}"
        j_ += 1
    return m_.start(), j_


for nm in ("free_peoples_tiny", "free_peoples_small", "free_peoples_medium", "free_peoples_large", "free_peoples_huge"):
    sp = _block(cb, nm)
    assert sp, nm
    cb = cb[:sp[0]] + cb[sp[1]:].lstrip("\n")
    cb, n_ = re.subn(r"(?m)^[ \t]*%s[ \t]*\n" % nm, "", cb)
    assert n_ == 1, (nm, n_)
sp = _block(cb, "free_peoples")
fp = cb[sp[0]:sp[1]]
cu = re.search(r"(?m)^\tcan_use\s*=\s*\{", fp)
fp = fp[:cu.end()] + "\n\t\talways = no" + fp[cu.end():]
fp = re.sub(r"(?m)^\tis_triggered_only\s*=\s*\w+", "\tis_triggered_only = yes", fp)
if "is_triggered_only" not in fp:
    fp = fp.replace("{", "{\n\tis_triggered_only = yes", 1)
if "constructing_cb" not in fp:
    fp = fp.replace("{", "{\n\tconstructing_cb = no", 1)
cb = cb[:sp[0]] + fp + cb[sp[1]:]
# every other "which country" list leaves the marker tags and the World Bank out, as Heartbreaker does
MARKERS = "\n\t\tfrom = {\n\t\t\tNOT = {\n\t\t\t\tOR = {\n" + "".join("\t\t\t\t\ttag = %s\n" % t_ for t_ in ("TIN", "SMA", "MED", "LRG", "HUG", "WBK")) + "\t\t\t\t}\n\t\t\t}\n\t\t}"
cb, n_lists = re.subn(r"(?m)^(\tallowed_countries\s*=\s*\{)", lambda m_: m_.group(1) + MARKERS, cb)''')
a = '''    if cu and m.group(1) not in ("status_quo", "civil_war", "become_independent"):'''
assert s.count(a) == 1
s = s.replace(a, '''    if cu and m.group(1) not in ("status_quo", "civil_war", "become_independent", "free_peoples"):''')
a = '''print("war goals that cannot be fabricated on an unwesternized HRE: %d | left alone: %d" % (len(shielded), len(skipped)))'''
assert s.count(a) == 1
s = s.replace(a, a + '''
assert "free_peoples_tiny" not in cb and cb.count("{") == cb.count("}"), "war goal file is unbalanced"
for m in re.finditer(r"NOT\\s*=\\s*\\{\\s*tag\\s*=\\s*HRE\\s*civilized", cb):
    raise SystemExit("the HRE shield is written without AND")
print("free peoples removed (5 sized war goals deleted, the original disabled) | country lists that now skip marker tags:", n_lists)''')
open("03g_takecapital.py", "w", encoding="utf-8").write(s)

# ------------------------------------------------------------------ 03_gameplay.py: drop the key no modifier file anywhere uses
s = open("03_gameplay.py", encoding="utf-8").read()
a = "    education_efficiency_modifier=0.15, supply_range=0.33)"
assert s.count(a) == 1
s = s.replace(a, "    education_efficiency_modifier=0.15, naval_organisation=0.15)       # naval range exists only as a technology effect")
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
