"""Research: what IGoRDoD 7.31's host / national value / tech school decisions depend on."""
import os, re, glob, collections
from config import *

A = os.path.join(V, "mod", "IGoRDoD 7.31")
strip = lambda t: re.sub(r"#.*", "", t)
rdA = lambda *p: open(os.path.join(A, *p), encoding=ENC, errors="replace").read()
allev = ""
for f in glob.glob(os.path.join(A, "events", "*.txt")):
    allev += "\n#FILE " + os.path.basename(f) + "\n" + strip(open(f, encoding=ENC, errors="replace").read())
mods_a = strip(rdA("common", "event_modifiers.txt"))
mods_v = strip(rd("common", "event_modifiers.txt"))
mods_o = strip(open(os.path.join(OUT, "common", "event_modifiers.txt"), encoding=ENC).read())
schools_o = strip(open(os.path.join(OUT, "common", "technology.txt"), encoding=ENC).read())
nv_o = strip(open(os.path.join(OUT, "common", "nationalvalues.txt"), encoding=ENC).read())
for fn in ("host_nation_decisions.txt", "NV_Changes.txt", "Tech_School_Changes.txt"):
    t = strip(rdA("decisions", fn))
    inner = t[t.index("{") + 1:t.rindex("}")]
    keys = [k for k, b, s, e in blocks(inner)]
    print("==", fn, len(keys), keys)
    print("  pictures:", sorted(set(re.findall(r"picture\s*=\s*\"?(\w+)", t))))
    print("  pictures present in IGoRDoD:", {p: os.path.exists(os.path.join(A, "gfx", "pictures", "decisions", p + ".dds")) for p in set(re.findall(r"picture\s*=\s*\"?(\w+)", t))})
    ev = sorted(set(re.findall(r"country_event\s*=\s*(\d+)", t)) | set(re.findall(r"id\s*=\s*(\d+)", t)))
    print("  events fired:", ev)
    for e in ev:
        m = re.search(r"id\s*=\s*%s\b" % e, allev)
        if m:
            fpos = allev.rfind("#FILE", 0, m.start())
            print("     ", e, "in", allev[fpos + 6:allev.find("\n", fpos)])
    md = sorted(set(re.findall(r"(?:has_country_modifier|name)\s*=\s*(\w+)", t)))
    print("  modifiers:", {m_: ("mine" if re.search(r"(?m)^%s\s*=" % m_, mods_o) else "igor" if re.search(r"(?m)^%s\s*=" % m_, mods_a) else "?") for m_ in md})
    print("  tags:", collections.Counter(re.findall(r"\b([A-Z]{3})\b", t)).most_common(12))
    print("  schools:", {s_: bool(re.search(r"\b%s\s*=" % s_, schools_o)) for s_ in set(re.findall(r"tech_school\s*=\s*(\w+)", t))})
    print("  national values:", {s_: bool(re.search(r"(?m)^%s\s*=" % s_, nv_o)) for s_ in set(re.findall(r"nationalvalue\s*=\s*(\w+)", t))})
    print("  flags:", sorted(set(re.findall(r"(?:has|set|clr)_(?:country|global)_flag\s*=\s*(\w+)", t))))
    tok = collections.Counter(re.findall(r"([a-z_]+)\s*=", t))
    print("  tokens:", dict(tok.most_common(70)))
for m_ in ("national_confusion", "academic_confusion"):
    mm = re.search(r"(?m)^%s\s*=\s*\{[^}]*\}" % m_, mods_a)
    print(mm.group(0) if mm else (m_, "not in igor modifiers"))
