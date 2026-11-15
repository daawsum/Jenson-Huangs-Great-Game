"""Stage 3e: host decisions, national value changes and tech school changes from IGoRDoD 7.31.

Copied as they are: decisions/host_nation_decisions.txt, NV_Changes.txt, Tech_School_Changes.txt,
events/host_decision_events.txt, their decision pictures, modifiers and names.
Adapted, because IGoRDoD is built around its own tags:
  * IGoRDoD's host is always its tag LCT. Here any human player may take the host decision once.
  * The two "total war" host switches are left out: they only set a flag that IGoRDoD's own war
    goals read, and this mod has no such war goals.
  * The two nation-swap events list one block per country tag; they are rebuilt, in IGoRDoD's own
    form, from this mod's tags.
Run after 03_gameplay.py (which writes common/event_modifiers.txt).
"""
import os, re, glob, shutil
from config import *

A = os.path.join(V, "mod", "IGoRDoD 7.31")
if not os.path.isdir(A):
    raise SystemExit("IGoRDoD 7.31 is not installed")
rdA = lambda *p: open(os.path.join(A, *p), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
strip = lambda t: re.sub(r"#.*", "", t)


def span(text, start):
    """index just past the brace block whose '{' is the first one at or after start"""
    j = text.index("{", start) + 1
    d = 1
    while d:
        d += text[j] == "{"
        d -= text[j] == "}"
        j += 1
    return j


def de_lct(t):
    t = re.sub(r"LCT\s*=\s*\{\s*country_event\s*=\s*(\d+)\s*\}", r"country_event = \1", t)
    t = re.sub(r"(?m)^[ \t]*tag\s*=\s*LCT[ \t]*\n", "", t)
    assert "LCT" not in strip(t), re.findall(r".*LCT.*", strip(t))[:3]
    return t


# ---- decisions
host = rdA("decisions", "host_nation_decisions.txt")
for k in ("total_war_cb", "total_war_cb_safety"):
    m = re.search(r"(?m)^\t%s\s*=\s*\{" % k, host)
    host = host[:m.start()] + host[span(host, m.start()):]
host = de_lct(host)
wr("decisions/host_nation_decisions.txt", host)
nv = rdA("decisions", "NV_Changes.txt")
ts = rdA("decisions", "Tech_School_Changes.txt")
wr("decisions/NV_Changes.txt", nv)
wr("decisions/Tech_School_Changes.txt", ts)

# ---- events: the two swap events get one block per tag of this mod
TAGS = [t for t in re.findall(r'(?m)^(\w{3})\s*=\s*"countries/', open(os.path.join(OUT, "common", "countries.txt"), encoding=ENC).read()) if t != "REB"]
ONE = "\t\trandom_country = {\n\t\t\tlimit = {\n\t\t\t\ttag = FROM\n\t\t\t\ttag = %s\n\t\t\t}\n\t\t\tTHIS = { change_tag_no_core_switch = %s }\n\t\t}\n"
TWO = ("\t\trandom_country = {\n\t\t\tlimit = {\n\t\t\t\ttag = FROM\n\t\t\t\ttag = %s\n\t\t\t\tNOT = { has_global_flag = host_flag_tagmove }\n\t\t\t}\n"
       "\t\t\tTHIS = { change_tag_no_core_switch = %s }\n\t\t}\n"
       "\t\trandom_country = {\n\t\t\tlimit = {\n\t\t\t\ttag = FROM\n\t\t\t\ttag = %s\n\t\t\t\thas_global_flag = host_flag_tagmove\n\t\t\t}\n"
       "\t\t\tFROM = { set_country_flag = host_nation }\n\t\t\tTHIS = {\n\t\t\t\tclr_country_flag = host_nation\n\t\t\t\tchange_tag_no_core_switch = %s\n\t\t\t}\n\t\t}\n")
ev = rdA("events", "host_decision_events.txt")
for eid, tmpl in (("1000007123", ONE), ("1000003123", TWO)):
    m = re.search(r"country_event\s*=\s*\{\s*id\s*=\s*%s\b" % eid, ev)
    end = span(ev, m.start())
    block = ev[m.start():end]
    i = block.index("immediate")
    j = span(block, i)
    body = "".join(tmpl % ((t,) * tmpl.count("%s")) for t in TAGS)
    ev = ev[:m.start()] + block[:i] + "immediate = {\n" + body + "\t}" + block[j:] + ev[end:]
ev = de_lct(ev)
wr("events/host_decision_events.txt", ev)
ids = re.findall(r"(?m)^\tid\s*=\s*(\d+)", ev)
fired = set(re.findall(r"country_event\s*=\s*(\d+)", strip(host + ev)))
assert fired <= set(ids), fired - set(ids)
mine = set()
for f in glob.glob(os.path.join(OUT, "events", "*.txt")):
    if os.path.basename(f) != "host_decision_events.txt":
        mine |= set(re.findall(r"\bid\s*=\s*(\d+)", open(f, encoding=ENC, errors="replace").read()))
assert not (set(ids) & mine), set(ids) & mine

# ---- modifiers
emf = os.path.join(OUT, "common", "event_modifiers.txt")
em = open(emf, encoding=ENC).read().replace("\r\n", "\n")
src = strip(rdA("common", "event_modifiers.txt"))
used = set(re.findall(r"(?:has_country_modifier|name)\s*=\s*(\w+)", strip(host + nv + ts + ev)))
add = ""
for k in sorted(used):
    if re.search(r"(?m)^%s\s*=" % k, strip(em)):
        continue
    m = re.search(r"(?m)^%s\s*=\s*\{" % k, src)
    assert m, k
    add += src[m.start():span(src, m.start())] + "\n\n"
wr("common/event_modifiers.txt", em.rstrip() + "\n\n##### from IGoRDoD 7.31 #####\n" + add)

# ---- every school and national value the decisions name must exist here
schools = strip(open(os.path.join(OUT, "common", "technology.txt"), encoding=ENC).read())
nvs = strip(open(os.path.join(OUT, "common", "nationalvalues.txt"), encoding=ENC).read())
for s_ in set(re.findall(r"tech_school\s*=\s*(\w+)", strip(ts))):
    assert re.search(r"\b%s\s*=" % s_, schools), s_
for s_ in set(re.findall(r"nationalvalue\s*=\s*(\w+)", strip(nv))):
    assert re.search(r"(?m)^%s\s*=" % s_, nvs), s_

# ---- pictures
pics = set(re.findall(r'picture\s*=\s*"?(\w+)"?', strip(host + nv + ts)))
os.makedirs(os.path.join(OUT, "gfx", "pictures", "decisions"), exist_ok=True)
n = 0
for p in sorted(pics):
    f = os.path.join(A, "gfx", "pictures", "decisions", p + ".dds")
    if os.path.exists(f):
        shutil.copyfile(f, os.path.join(OUT, "gfx", "pictures", "decisions", p + ".dds"))
        n += 1
    else:
        assert os.path.exists(os.path.join(V, "gfx", "pictures", "decisions", p + ".dds")), p

# ---- names
lr = {}
for f in sorted(glob.glob(os.path.join(A, "localisation", "*.csv"))):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        p = l.split(";")
        if len(p) > 1 and p[0] and p[0] not in lr:
            lr[p[0]] = p[1]
keys = []
for t in (host, nv, ts):
    inner = strip(t)
    inner = inner[inner.index("{") + 1:inner.rindex("}")]
    for k, b, s_, e_ in blocks(inner):
        keys += [k + "_title", k + "_desc"]
keys += [k for m_ in sorted(used) for k in (m_, "desc_" + m_, m_ + "_desc")]
lines = ["%s;%s;;;;;;;;;;;;;x" % (k, lr[k].replace(";", ",")) for k in keys if lr.get(k)]
unnamed = [k for k in keys if not lr.get(k) and k.endswith("_title")]
wr("localisation/00_warlord_era_igor.csv", "\n".join(lines) + "\n")
print("IGoRDoD decisions: host %d, national value %d, tech school %d | swap events rebuilt for %d tags | modifiers added: %s | pictures %d | names %d, titles without a name: %s"
      % (len(re.findall(r"(?m)^\t\w+\s*=\s*\{", host)), len(re.findall(r"(?m)^\t\w+\s*=\s*\{", nv)), len(re.findall(r"(?m)^\t\w+\s*=\s*\{", ts)),
         len(TAGS), re.findall(r"(?m)^(\w+)\s*=", add), n, len(lines), unnamed))
