"""One-off: make country histories follow vanilla conventions exactly."""
import re
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b)


# vanilla never gives an uncivilized country technologies or a tech school
rep(r'''        s += reforms(SPECIAL_REF) + techs(HORDE_TECH) + "set_country_flag = great_horde\n"''',
    r'''        s += reforms(SPECIAL_REF) + "set_country_flag = great_horde\n"''')
rep(r'''        s += reforms(PARTIAL_REF) + techs(PARTIAL_TECH)''', r'''        s += reforms(PARTIAL_REF)''')
rep(r'''        s += reforms([]) + techs(UNCIV_TECH)''', r'''        s += reforms([])''')
rep('        s += reforms(SPECIAL_REF) + techs(HORDE_TECH)\n', '        s += reforms(SPECIAL_REF)\n')
rep('(civilized|oob|decision|capital|is_releasable_vassal|set_country_flag)', '(civilized|oob|decision|capital|schools|set_country_flag)')
# party names unique per tag, as in every vanilla country file
rep(r'''def country_file(col):
    return "color = { %d %d %d }\ngraphical_culture = ChineseGC\n\n%s" % (col[0], col[1], col[2], china_parties)''',
    r'''def country_file(col, tag):
    return "color = { %d %d %d }\ngraphical_culture = ChineseGC\n\n%s" % (col[0], col[1], col[2], china_parties.replace('"CHI_', '"%s_' % tag))''')
s, n = re.subn(r"country_file\((w\[5\]|d\[2\])\)", r"country_file(\1, t)", s)
assert n == 2, n
rep(r'''    s += POLREF + "ruling_party = %s\n" % chi_rx + UH''',
    r'''    s += POLREF + "ruling_party = %s\n" % chi_rx.replace("CHI_", tag + "_") + UH''')
rep(r'''"ruling_party = %s\n" % (chi_rx if civ else party_of("CHI", "conservative")) + UH''',
    r'''"ruling_party = %s\n" % (chi_rx if civ else party_of("CHI", "conservative")).replace("CHI_", tag + "_") + UH''')
rep('"commerce_tech_school", "prussian_tech_school"]', '"commerce_tech_school"]')
# party names need text
rep('''for t, d in list(DOMINIONS.items()) + list(FORMABLES.items()):
    L += loc(t, d[0]) + loc(t + "_ADJ", d[1])''',
    '''for t, d in list(DOMINIONS.items()) + list(FORMABLES.items()):
    L += loc(t, d[0]) + loc(t + "_ADJ", d[1])
_pn = {"conservative": "Old Guard", "liberal": "Reform Society", "reactionary": "Military Clique", "socialist": "Labour Union",
       "communist": "Soviet Committee", "fascist": "Blue Shirts", "anarcho_liberal": "Free Association"}
for t in list(WARLORDS) + list(DOMINIONS) + list(FORMABLES):
    for pn in re.findall(r'name\\s*=\\s*"CHI_(\\w+)"', china_parties):
        L += loc("%s_%s" % (t, pn), _pn.get(re.sub(r"_\\d+$", "", pn), "Party"))''')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched")
