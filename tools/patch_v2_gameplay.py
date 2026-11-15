"""One-off (v2): Sikh buff rework, clique traits, culture-mapped decisions."""
import re
s = open("03_gameplay.py", encoding="utf-8").read()
if "TRAITS" in s:
    raise SystemExit("already patched")


def rep(a, b):
    global s
    assert a in s, a
    s = s.replace(a, b, 1)


# Sikh buff: organisation plus attack and defence; smaller mobilisation; no research bonus
a = s[s.index('mod("khalsa_army"'):s.index('mod("mongol_horde"')]
rep(a, '''mod("khalsa_army", "The Khalsa Army", "The Fauj-i-Khas, drilled by veterans of Napoleon, is the finest army in Asia. It is a small professional force, not a levy.",
    land_organisation=0.6, org_regain=0.5, land_attack_modifier=0.25, land_defense_modifier=0.25,
    land_unit_start_experience=50, mobilisation_size=-0.02, supply_consumption=-0.2, leadership=2)
''')

# traits for the twenty majors
rep('''em = rd("common", "event_modifiers.txt") + "\\n\\n##### WARLORD ERA #####\\n"''',
    '''for _t, (_name, _desc, _kw) in TRAITS.items():
    mod("trait_" + _t, _name, _desc, **_kw)

em = rd("common", "event_modifiers.txt") + "\\n\\n##### WARLORD ERA #####\\n"''')
rep('''event("The Sea Lanes Turn",''', '''for _t, (_name, _desc, _kw) in TRAITS.items():
    setup("tag = %s" % _t, "trait_" + _t, _name, _desc)

event("The Sea Lanes Turn",''')

# decisions name cultures: run them through the same culture map as the pops
rep('''def decision(key, title, desc, potential, allow, effect, ai=1):
''', '''CM = Wd.get("cmap", {})


def _map_cultures(effect):
    seen, out = set(), []
    for l in effect.split("\\n"):
        m = re.match(r"(\\s*)add_accepted_culture\\s*=\\s*(\\w+)", l)
        if m:
            cu = CM.get(m.group(2), m.group(2))
            if cu in seen:
                continue
            seen.add(cu)
            l = "%sadd_accepted_culture = %s" % (m.group(1), cu)
        out.append(l)
    return "\\n".join(out)


def decision(key, title, desc, potential, allow, effect, ai=1):
    effect = _map_cultures(effect)
''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched 03_gameplay.py")
