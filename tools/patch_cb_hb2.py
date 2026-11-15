"""One-off patch of 03c_statesize.py: unification stays vanilla-based (Heartbreaker's is rewritten for its own countries)."""
s = open("03c_statesize.py", encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('HB_FAMILIES = ["acquire_core_state", "acquire_state", "place_in_the_sun", "demand_concession_casus_belli", "unification_casus_belli"]',
    'HB_FAMILIES = ["acquire_core_state", "acquire_state", "place_in_the_sun", "demand_concession_casus_belli"]\n'
    '# (Heartbreaker rewrote unification_casus_belli for four countries of its own, so that family is sized here like the warlord goal)')
a = s.index("# this mod's own goal between cliques, sized the same way: marker in allowed_states only")
b = s.index("# free peoples: never usable")
s = s[:a] + r'''# this mod's own goal between cliques and vanilla's unification goal, sized the same way: marker in allowed_states only
for fam in ("warlord_take_state", "unification_casus_belli"):
    sp = block_span(cb, fam)
    base = cb[sp[0]:sp[1]]
    variants = ""
    for (tag, key, name), f in zip(SIZES, FAMILIES[fam]):
        v = base.replace("%s = {" % fam, "%s_%s = {" % (fam, key), 1)
        v = set_field(v, "peace_cost_factor", f)
        v = add_flag(v, "po_remove_prestige = yes")
        v = inject(v, "allowed_states", "any_owned_province = { is_core = %s }" % tag)
        variants += v + "\n\n"
        order.append("%s_%s" % (fam, key))
    orig = ""
    if fam != "warlord_take_state":
        orig = set_field(add_flag(set_field(base, "peace_cost_factor", FAMILIES[fam][2]), "po_remove_prestige = yes"), "constructing_cb", "no")
    cb = cb[:sp[0]] + variants + orig + cb[sp[1]:]
''' + s[b:]
rep('for fam in HB_FAMILIES + ["warlord_take_state"]:\n    for tag, key, name in SIZES:',
    'for fam in HB_FAMILIES + ["warlord_take_state", "unification_casus_belli"]:\n    for tag, key, name in SIZES:')
open("03c_statesize.py", "w", encoding="utf-8").write(s)
print("patched")
