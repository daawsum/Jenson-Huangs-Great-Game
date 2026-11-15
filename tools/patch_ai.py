"""One-off patch: AI cliques spread over the options of an exclusive choice instead of all taking the first."""
p = "03_gameplay.py"
s = open(p, encoding="utf-8").read()
a = r'''    for key, title, desc, allow, effect, modname in options:
        others = " or ".join(o[1] for o in options if o[0] != key)'''
b = r'''    _all = list(WARLORDS)
    _off = sum(map(ord, group))
    for _i, (key, title, desc, allow, effect, modname) in enumerate(options):
        others = " or ".join(o[1] for o in options if o[0] != key)
        # the AI of each clique leans to one option, so computer-run neighbours differ from each other
        _mine = [t_ for j_, t_ in enumerate(_all) if (j_ + _off) % len(options) == _i]
        ai = "1\n\t\t\tmodifier = {\n\t\t\t\tfactor = 0\n\t\t\t\tNOT = {\n\t\t\t\t\tOR = {\n%s\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}" % "\n".join("\t\t\t\t\t\ttag = %s" % t_ for t_ in _mine)'''
assert s.count(a) == 1
s = s.replace(a, b)
a = r'''potential + "\nNOT = { has_country_flag = chose_%s }" % group, allow, eff + effect, tech=tech)'''
assert s.count(a) == 1
s = s.replace(a, r'''potential + "\nNOT = { has_country_flag = chose_%s }" % group, allow, eff + effect, ai, tech=tech)''')
open(p, "w", encoding="utf-8").write(s)
print("patched")
