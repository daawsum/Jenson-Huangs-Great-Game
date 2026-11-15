"""Research 2: what Heartbreaker's political and social reform blocks contain."""
import os, re, glob, collections
from config import *

H = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
strip = lambda t: re.sub(r"#.*", "", t)
raw = open(os.path.join(H, "common", "issues.txt"), encoding=ENC, errors="replace").read()
hi = strip(raw)
vi = strip(rd("common", "issues.txt"))
allv = ""
for d in ("common", "events", "decisions", "technologies", "inventions"):
    for f in glob.glob(os.path.join(V, d, "*.txt")):
        allv += strip(open(f, encoding=ENC, errors="replace").read())
vk = set(re.findall(r"([A-Za-z_]\w*)\s*=", allv))
for g, body, s, e in blocks(hi):
    if g not in ("political_reforms", "social_reforms"):
        continue
    toks = collections.Counter(re.findall(r"([A-Za-z_]\w*)\s*=", body))
    print("==", g, "| tokens vanilla never uses anywhere:", {k: n for k, n in toks.items() if k not in vk})
    print("   all tokens:", dict(toks.most_common(80)))
    print("   flags set:", sorted(set(re.findall(r"set_country_flag\s*=\s*(\w+)", body))))
    print("   governments named:", sorted(set(re.findall(r"government\s*=\s*(\w+)", body))))
    for iss, b2, s2, e2 in blocks(body):
        if iss in ("vote_franschise", "school_reforms", "press_rights"):
            print("--", iss, "\n", b2.strip()[:1500])
flags = sorted(set(re.findall(r"set_country_flag\s*=\s*(\w+)", hi)))
use = collections.Counter()
for d in ("common", "poptypes", "events", "decisions", "inventions"):
    for f in glob.glob(os.path.join(H, d, "**", "*.txt"), recursive=True):
        if os.path.basename(f) == "issues.txt":
            continue
        t = strip(open(f, encoding=ENC, errors="replace").read())
        for fl in flags:
            n = len(re.findall(r"\b%s\b" % fl, t))
            if n:
                use[(os.path.relpath(f, H), fl)] += n
print("where those flags are read:", dict(use.most_common(30)))
gv = strip(rd("common", "governments.txt"))
print("vanilla governments:", re.findall(r"(?m)^(\w+)\s*=\s*\{", gv))
