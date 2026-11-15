"""Read an autosave: every country's prestige, and how many wars have ended."""
import re, sys
t = open(sys.argv[1], encoding="cp1252", errors="replace").read()
print("date", re.search(r'date="([^"]+)"', t).group(1), "| ends cleanly:", t.rstrip().endswith("}"))
pres = []
for m in re.finditer(r"\n([A-Z][A-Z0-9]{2})=\n\{\n\ttax_base", t):
    b = t[m.end():m.end() + 6000]
    p = re.search(r"\n\tprestige=([\-\d\.]+)", b)
    if p:
        pres.append((float(p.group(1)), m.group(1)))
pres.sort(reverse=True)
print("countries:", len(pres), "| highest prestige:", [(tag, round(v, 1)) for v, tag in pres[:12]])
print("above 250:", [(tag, round(v)) for v, tag in pres if v > 250])
print("active wars:", len(re.findall(r"\nactive_war=", t)), "| wars ended:", len(re.findall(r"\nprevious_war=", t)))
goals = re.findall(r'casus_belli="(\w+)"', t)
import collections
print("war goals seen in wars:", dict(collections.Counter(goals).most_common(8)))
