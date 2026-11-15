"""One-off patch of 03_gameplay.py: decisions stay hidden until their technology and territory
prerequisites are met; the mod's own national-value-changing decisions go (IGoRDoD's replace them)."""
import re
p = "03_gameplay.py"
s = open(p, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


rep(r'''    if tech:
        assert tech in _TECHS, (key, tech)
        allow = "%s = 1\n%s" % (tech, allow)
''', r'''    if tech:
        assert tech in _TECHS, (key, tech)
        potential = "%s\n%s = 1" % (potential, tech)
    # a decision is not listed at all until its technology is known and the land it needs is held;
    # what is left in "allow" is what a player can still work towards (money, peace, prestige, relations)
    show, keep = _prereq(allow)
    if show:
        potential = potential + "\n" + show
    allow = keep
    HIDDEN[bool(tech) + bool(show)] += 1
''')
rep(r'''def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):''', r'''HIDDEN = collections.Counter()


def _prereq(allow):
    """split an allow block into (territory conditions, the rest), statement by statement"""
    st, cur, d = [], [], 0
    for l in allow.strip("\n").split("\n"):
        if not l.strip() and not d:
            continue
        cur.append(l)
        d += l.count("{") - l.count("}")
        if d == 0:
            st.append("\n".join(cur))
            cur = []
    assert not cur, allow
    terr = lambda x: bool(re.match(r"\s*owns\s*=\s*\d+\s*$", x)) or \
        bool(re.match(r"\s*OR\s*=\s*\{(\s*owns\s*=\s*\d+)+\s*\}\s*$", x)) or \
        bool(re.match(r"\s*any_owned_province\s*=\s*\{", x))
    return "\n".join(x for x in st if terr(x)), "\n".join(x for x in st if not terr(x))


def decision(key, title, desc, potential, allow, effect, ai=1, tech=None):''')

# the creed choice changed national values: IGoRDoD's own national value decisions do that now
a = s.index('choice("creed", IDEO, [')
b = s.index('choice("opium", ENL, [')
s = s[:a] + r'''once("grant_provincial_constitution", "Grant a Provincial Constitution", "Promise the gentry an assembly and self-rule: our province first, the nation later.",
     WL, "war = no\nprestige = 20", "any_pop = { consciousness = 1 }", "federal_self_rule")
''' + s[b:]
assert "nationalvalue" not in s and "tech_school" not in s
rep(r'''print("decisions:", len(DEC), "| technology required:", dict(GATES.most_common()))''',
    r'''print("decisions:", len(DEC), "| technology required:", dict(GATES.most_common()))
print("hidden until prerequisites are met: by technology and territory %d, by one of them %d, always listed %d" % (HIDDEN[2], HIDDEN[1], HIDDEN[0]))''')
open(p, "w", encoding="utf-8").write(s)
b = open("build.sh", encoding="utf-8").read()
if "03e_igor" not in b:
    b = b.replace("python 03_gameplay.py | tail -2", "python 03_gameplay.py | tail -3\npython 03e_igor.py")
    open("build.sh", "w", encoding="utf-8", newline="\n").write(b)
print("patched")
