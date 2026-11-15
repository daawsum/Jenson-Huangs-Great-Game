"""One-off patch: sized war goals are Heartbreaker's own blocks, not this mod's approximation of them."""
s = open("03c_statesize.py", encoding="utf-8").read()
a = s.index("order = []\nif \"acquire_state_tiny\" not in cb:")
b = s.index('print("war goals split by state size:"')
s = s[:a] + r'''# The sized war goals are Heartbreaker's own blocks, copied as they stand. What matters in them:
#   * the size marker (is_core = TIN/SMA/...) is tested ONLY inside allowed_states, together with the
#     other province conditions. It is never in can_use: can_use is what the game turns into the
#     tooltip of the war goal list, and a marker tag there is what crashed on hover.
#   * every one is is_triggered_only (it must be justified), with Heartbreaker's costs and truces.
# Taken out of each block: the lines naming Heartbreaker's own tags (LCT, GHO) and its rule that
# China can neither use the goal nor be its target.
# Free Peoples is not split by size here and the original is switched off: its list of countries to
# free offered the marker tags themselves.
hb_cb = open(os.path.join(HB, "common", "cb_types.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
HB_FAMILIES = ["acquire_core_state", "acquire_state", "place_in_the_sun", "demand_concession_casus_belli", "unification_casus_belli"]
DROP = [r"NOT\s*=\s*\{\s*tag\s*=\s*LCT\s*\}", r"NOT\s*=\s*\{\s*tag\s*=\s*GHO\s*\}", r"NOT\s*=\s*\{\s*tag\s*=\s*CHI\s*\}",
        r"this\s*=\s*\{\s*NOT\s*=\s*\{\s*tag\s*=\s*CHI\s*\}\s*\}"]
have_tags = set(re.findall(r"(?m)^(\w{3})\s*=", read("common/countries.txt"))) | {"REB"}


def from_heartbreaker(name):
    sp = block_span(hb_cb, name)
    assert sp, "Heartbreaker has no war goal " + name
    v = hb_cb[sp[0]:sp[1]]
    for rx in DROP:
        v = re.sub(r"(?mi)^[ \t]*%s[ \t]*(#.*)?\n" % rx, "", v)
    bare = re.sub(r"#.*", "", v)
    odd = set(re.findall(r"\btag\s*=\s*([A-Z][A-Z0-9]{2})\b", bare)) - have_tags - {"THIS", "FROM"}
    assert not odd, (name, "names tags this mod does not have", odd)
    cu = bare[bare.index("can_use"):bare.index("allowed_states")] if "allowed_states" in bare and "can_use" in bare else ""
    assert not re.search(r"is_core\s*=\s*(TIN|SMA|MED|LRG|HUG)", cu), (name, "marker tag inside can_use")
    assert bare.count("{") == bare.count("}"), name
    return v


order = []
cb = re.sub(r"(?ms)^warlord_take_state_(tiny|small|medium|large|huge) = \{.*?\n\}\n", "", cb)
for fam in HB_FAMILIES:
    sp = block_span(cb, fam)
    assert sp, "war goal not found in cb_types.txt: " + fam
    base = cb[sp[0]:sp[1]]
    variants = ""
    for tag, key, name in SIZES:
        variants += from_heartbreaker("%s_%s" % (fam, key)) + "\n\n"
        order.append("%s_%s" % (fam, key))
    # the unsized original stays defined (vanilla events grant it by name) but cannot be justified
    orig = set_field(base, "peace_cost_factor", FAMILIES[fam][2])
    orig = add_flag(orig, "po_remove_prestige = yes")
    orig = re.sub(r"(?m)^\s*always\s*=\s*yes\s*\n", "", orig)
    orig = set_field(orig, "constructing_cb", "no")
    cb = cb[:sp[0]] + variants + orig + cb[sp[1]:]
# this mod's own goal between cliques, sized the same way: marker in allowed_states only
sp = block_span(cb, "warlord_take_state")
base = cb[sp[0]:sp[1]]
variants = ""
for (tag, key, name), f in zip(SIZES, FAMILIES["warlord_take_state"]):
    v = base.replace("warlord_take_state = {", "warlord_take_state_%s = {" % key, 1)
    v = set_field(v, "peace_cost_factor", f)
    v = add_flag(v, "po_remove_prestige = yes")
    v = inject(v, "allowed_states", "any_owned_province = { is_core = %s }" % tag)
    variants += v + "\n\n"
    order.append("warlord_take_state_%s" % key)
cb = cb[:sp[0]] + variants + cb[sp[1]:]
# free peoples: never usable
sp = block_span(cb, "free_peoples")
fp = cb[sp[0]:sp[1]]
fp = set_field(fp, "is_triggered_only", "yes")
fp = set_field(fp, "constructing_cb", "no")
fp = re.sub(r"(?m)^\s*always\s*=\s*yes\s*\n", "", fp)
fp = inject(fp, "can_use", "always = no")
cb = cb[:sp[0]] + fp + cb[sp[1]:]
for name in ("humiliate", "rude_boy"):      # prestige-only goals were costed for PEACE_COST_PRESTIGE = 1; Heartbreaker's 16%
    sp = block_span(cb, name)
    if sp:
        cb = cb[:sp[0]] + set_field(cb[sp[0]:sp[1]], "peace_cost_factor", 0.004) + cb[sp[1]:]
po = re.search(r"peace_order\s*=\s*\{", cb)
cb = cb[:po.end()] + "\n" + "\n".join(order) + cb[po.end():]
cb = re.sub(r"(?m)^warlord_take_state\s*\n", "", cb)
for fam in HB_FAMILIES + ["warlord_take_state"]:
    for tag, key, name in SIZES:
        sp = block_span(cb, "%s_%s" % (fam, key))
        bare = re.sub(r"#.*", "", cb[sp[0]:sp[1]])
        i, j = bare.index("can_use"), bare.index("allowed_states")
        assert "is_core = %s" % tag not in bare[i:j] and "is_core = %s" % tag in bare[j:], (fam, key)
assert cb.count("{") == cb.count("}")
write("common/cb_types.txt", cb)

# the two modifiers Heartbreaker's blocks test for (never applied here, but they must exist to be named)
emp = path("common/event_modifiers.txt")
em = open(emp, encoding=ENC).read().replace("\r\n", "\n")
hb_em = re.sub(r"#.*", "", open(os.path.join(HB, "common", "event_modifiers.txt"), encoding=ENC, errors="replace").read())
addm = ""
for k in sorted(set(re.findall(r"has_country_modifier\s*=\s*(\w+)", re.sub(r"#.*", "", cb)))):
    if not re.search(r"(?m)^%s\s*=" % k, re.sub(r"#.*", "", em)):
        sp = block_span(hb_em, k)
        assert sp, k
        addm += hb_em[sp[0]:sp[1]] + "\n\n"
if addm:
    write("common/event_modifiers.txt", em.rstrip() + "\n\n##### named by Heartbreaker's war goals #####\n" + addm)
print("modifiers added so the war goals can name them:", re.findall(r"(?m)^(\w+)\s*=", addm))
''' + s[b:]
s = s.replace('''    "free_peoples": [0.003, 0.006, 0.008, 0.012, 0.016],\n''', "")
open("03c_statesize.py", "w", encoding="utf-8").write(s)

g = open("03g_takecapital.py", encoding="utf-8").read()
i = g.index('for nm in ("free_peoples_tiny", "free_peoples_small"')
j = g.index("n_lists = 0")
g = g[:i] + g[j:]
g = g.replace('assert "free_peoples_tiny" not in cb and cb.count("{") == cb.count("}"), "war goal file is unbalanced"',
              'assert "free_peoples_tiny" not in cb and cb.count("{") == cb.count("}"), "war goal file is unbalanced"\nassert re.search(r"(?s)free_peoples = \\{.*?always = no", cb), "free peoples must stay switched off"')
g = g.replace('print("free peoples removed (5 sized war goals deleted, the original disabled) | country lists that now skip marker tags:", n_lists)',
              'print("free peoples is switched off and has no sized versions")')
open("03g_takecapital.py", "w", encoding="utf-8").write(g)
print("patched")
