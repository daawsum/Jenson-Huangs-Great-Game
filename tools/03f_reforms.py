"""Stage 3f: the reforms of civilized countries from DoD Heartbreaker MP 4.9.5.

Heartbreaker's political_reforms and social_reforms blocks replace this mod's, text unchanged.
They have the same reforms and the same option names as vanilla (so every country history, party
and event still fits); what differs is what each option does: immigration pull on most steps,
factory throughput and administrative cost on social reforms, suppression and consciousness on
press rights, and so on.
Party issues (with the World Bank policies) and the reforms of uncivilized countries are left as
they are: Heartbreaker renames some uncivilized reform options, which the country histories here
do not use.
Run after 03b_worldbank.py, which writes common/issues.txt.
"""
import os, re
from config import *

H = os.path.join(V, "mod", "DoD Heartbreaker MP 4.9.5")
if not os.path.isdir(H):
    raise SystemExit("DoD Heartbreaker MP 4.9.5 is not installed")
strip = lambda t: re.sub(r"#.*", "", t)


def group(text, name):
    """(start, end) of a top-level group, comments ignored when matching braces"""
    m = re.search(r"(?m)^%s\s*=\s*\{" % name, text)
    assert m, name
    d, j, n = 1, m.end(), len(text)
    while d:
        c = text[j]
        if c == "#":
            j = text.find("\n", j)
            if j < 0:
                j = n
            continue
        d += c == "{"
        d -= c == "}"
        j += 1
    return m.start(), j


def shape(text):
    out = {}
    for iss, b, s_, e_ in blocks(text[text.index("{") + 1:text.rindex("}")]):
        out[iss] = [o for o, b2, s2, e2 in blocks(b)]
    return out


hb = open(os.path.join(H, "common", "issues.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
p = os.path.join(OUT, "common", "issues.txt")
mine = open(p, encoding=ENC).read().replace("\r\n", "\n") if os.path.exists(p) else rd("common", "issues.txt")
known = set(re.findall(r"([A-Za-z_]\w*)\s*=", strip(rd("common", "issues.txt") + rd("common", "event_modifiers.txt") + rd("common", "static_modifiers.txt"))))
known |= {"government", "has_country_flag", "year", "OR", "NOT", "AND"}      # triggers inside an "allow"
report = {}
for g in ("political_reforms", "social_reforms"):
    a, b = group(hb, g)
    new = hb[a:b]
    c, d = group(mine, g)
    old_shape, new_shape = shape(strip(mine[c:d])), shape(strip(new))
    assert old_shape == new_shape, (g, "reform or option names differ from this mod's")
    names = set(new_shape) | {o for v in new_shape.values() for o in v}
    odd = set(re.findall(r"([A-Za-z_]\w*)\s*=", strip(new))) - known - names
    assert not odd, (g, odd)
    mine = mine[:c] + new + mine[d:]
    report[g] = len(new_shape)
wr("common/issues.txt", mine)
print("civilized reforms from Heartbreaker:", report, "| option names unchanged, so histories and parties still fit")
