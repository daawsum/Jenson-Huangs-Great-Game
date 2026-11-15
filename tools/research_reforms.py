"""Research: Heartbreaker's political and social reforms against vanilla's, and what else names them."""
import os, re, glob, collections
from config import *

H = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
strip = lambda t: re.sub(r"#.*", "", t)
hi = strip(open(os.path.join(H, "common", "issues.txt"), encoding=ENC, errors="replace").read())
vi = strip(rd("common", "issues.txt"))
oi = strip(open(os.path.join(OUT, "common", "issues.txt"), encoding=ENC).read())


def tree(t):
    out = collections.OrderedDict()
    for g, body, s, e in blocks(t):
        out[g] = collections.OrderedDict()
        for iss, b2, s2, e2 in blocks(body):
            out[g][iss] = collections.OrderedDict((o, b3) for o, b3, s3, e3 in blocks(b2))
    return out


th, tv, to = tree(hi), tree(vi), tree(oi)
for g in th:
    print("==", g, "| vanilla has group:", g in tv)
    for iss, opts in th[g].items():
        vo = tv.get(g, {}).get(iss)
        mark = "same options" if vo is not None and list(vo) == list(opts) else ("NEW ISSUE" if vo is None else "options differ: vanilla %s" % list(vo))
        body_same = vo is not None and all(re.sub(r"\s+", "", opts[o]) == re.sub(r"\s+", "", vo.get(o, "")) for o in opts)
        print("   %-26s %s | %s%s" % (iss, list(opts), mark, "" if body_same else " | effects differ"))
print("groups only in my current file:", [g for g in to if g not in th], "| issues only in mine:", [(g, i) for g in to for i in to[g] if i not in th.get(g, {})])
keys = collections.Counter(re.findall(r"([A-Za-z_]\w*)\s*=", hi))
vkeys = set(re.findall(r"([A-Za-z_]\w*)\s*=", vi))
print("keys heartbreaker uses in issues.txt that vanilla's issues.txt never does:", {k: n for k, n in keys.items() if k not in vkeys and not any(k in th[g] or any(k in th[g][i] for i in th[g]) for g in th)})
# who else names reform issues/options in heartbreaker (outside history, which this mod writes itself)
newnames = set()
for g in ("political_reforms", "social_reforms"):
    for iss, opts in th.get(g, {}).items():
        if iss not in tv.get(g, {}):
            newnames.add(iss)
        newnames |= {o for o in opts if o not in tv.get(g, {}).get(iss, {})}
print("new reform names:", sorted(newnames))
hits = collections.defaultdict(collections.Counter)
for d in ("common", "poptypes", "events", "decisions", "inventions", "technologies", "units", "interface"):
    for f in glob.glob(os.path.join(H, d, "**", "*.*"), recursive=True):
        if not f.endswith((".txt", ".gui", ".gfx", ".lua")) or os.path.basename(f) == "issues.txt":
            continue
        t = strip(open(f, encoding=ENC, errors="replace").read())
        for n in newnames:
            c = len(re.findall(r"\b%s\b" % n, t))
            if c:
                hits[os.path.relpath(f, H)][n] += c
for f, c in sorted(hits.items(), key=lambda x: -sum(x[1].values()))[:40]:
    print("   ", f, dict(c.most_common(6)))
print("files that name new reforms:", len(hits))
