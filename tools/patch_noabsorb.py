"""One-off patch: the Absorb Clique war goal (warlord_annex) is removed."""
import re
s = open("03_gameplay.py", encoding="utf-8").read()
a = '"acquire_core_state \\nannex_core_country\\nwarlord_take_state\\nwarlord_annex"'
assert s.count(a) == 1
s = s.replace(a, '"acquire_core_state \\nannex_core_country\\nwarlord_take_state"')
i = s.index("\nwarlord_annex = {")
j = s.index('"""\nwr("common/cb_types.txt", cb)', i)
s = s[:i] + "\n" + s[j:]
s, n = re.subn(r'(?m)^loc\("warlord_annex[^\n]*\n', "", s)
assert n == 4, n
assert "warlord_annex" not in s
open("03_gameplay.py", "w", encoding="utf-8").write(s)
p = open("05_package.py", encoding="utf-8").read()
k = p.index('or "Absorb Clique"')
print("readme line was:", p[p.rfind("\n", 0, k - 80):p.index("\n", k)].strip()[:260])
p2 = re.sub(r'\s*\(annex a clique with two states or fewer\)', "", p.replace(' or "Absorb Clique"', ""))
open("05_package.py", "w", encoding="utf-8").write(p2)
print("patched")
