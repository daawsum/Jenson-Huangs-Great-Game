"""One-off: only Chinese cliques (flag kept through tag changes) may charter or feed dominions."""
s = open("03_gameplay.py", encoding="utf-8").read()
a = r'"civilized = yes\nis_vassal = no\nNOT = { exists = %s }'
b = r'"has_country_flag = chinese_warlord\nis_vassal = no\nNOT = { exists = %s }'
assert a in s
s = s.replace(a, b)
a = r'"civilized = yes\n%s = { vassal_of = THIS }'
b = r'"has_country_flag = chinese_warlord\n%s = { vassal_of = THIS }'
assert a in s
s = s.replace(a, b)
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
