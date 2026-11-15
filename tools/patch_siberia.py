"""One-off patch: no Russians in Siberia; nobody may fabricate a war goal on the HRE before it westernizes."""
s = open("02_world.py", encoding="utf-8").read()
a = "run_pops(POPFAC, True)\n"
assert s.count(a) == 1
s = s.replace(a, a + r'''
# ------------------------------------------------------------------ Siberia without Russians
# Russia never crossed the Urals in this world. In the empty lands that were Russian Asia, a
# province of forest peoples (or one that had only settlers) becomes wholly Siberian; in a steppe
# province the settlers take the culture of the people already living there.
SIBERIA = {p for p in vprov if cont.get(p) == "asia" and vprov[p]["owner"] == "RUS" and owner.get(p) is None}
SLAVS = {"russian", "ukrainian", "byelorussian"} | {k for k, v in CMAP.items() if v in ("russian", "ukrainian", "byelorussian")}
SLAVS |= {CMAP.get(k, k) for k in list(SLAVS)}
FOREST = {"siberian", "yakut"}
_sib = collections.Counter()


def _siberia(text):
    out, i = [], 0
    for m_ in re.finditer(r"(?m)^(\d+)\s*=\s*\{", text):
        if m_.start() < i:
            continue
        d, j = 1, m_.end()
        while d:
            d += text[j] == "{"
            d -= text[j] == "}"
            j += 1
        body = text[m_.end():j - 1]
        if int(m_.group(1)) in SIBERIA:
            size = collections.Counter()
            for b_ in re.finditer(r"culture\s*=\s*(\w+)[^}]*?size\s*=\s*(\d+)", body):
                size[b_.group(1)] += int(b_.group(2))
            native = [c_ for c_, n_ in size.most_common() if c_ not in SLAVS]
            if not native or native[0] in FOREST:
                body = re.sub(r"culture\s*=\s*\w+", "culture = siberian", body)
                _sib["siberian"] += sum(size.values())
            else:
                body = re.sub(r"culture\s*=\s*(%s)\b" % "|".join(sorted(SLAVS)), "culture = " + native[0], body)
                _sib[native[0]] += sum(size.values())
        out.append(text[i:m_.end()] + body + "}")
        i = j
    return "".join(out) + text[i:]


for f in glob.glob(os.path.join(OUT, "history", "pops", "1836.1.1", "*.txt")):
    t_ = open(f, encoding=ENC).read().replace("\r\n", "\n")
    n_ = _siberia(t_)
    if n_ != t_:
        open(f, "w", encoding=ENC, newline="\r\n").write(n_)
print("siberia: %d provinces, pops by culture now (thousands): %s" % (len(SIBERIA), {k: v * 4 // 1000 for k, v in _sib.most_common()}))
''')
open("02_world.py", "w", encoding="utf-8").write(s)

g = open("03g_takecapital.py", encoding="utf-8").read()
if "HRE" not in g:
    a = '''wr("common/cb_types.txt", cb.rstrip() + "\\n\\n# from DoD Heartbreaker MP 4.9.5\\n" + block + "\\n")\n'''
    assert g.count(a) == 1, "anchor"
    g = g.replace(a, r'''cb = cb.rstrip() + "\n\n# from DoD Heartbreaker MP 4.9.5\n" + block + "\n"

# Heartbreaker shields its China from fabricated war goals. Here the cliques are fair game for each
# other, so nothing of that is kept; the shield goes to the Holy Roman Empire instead, for as long as
# it has not westernized. It covers every war goal a country can fabricate (not the ones that only
# decisions and events hand out, and not the ones that end or answer a war).
for word in ("tag = CHI", "is_culture_group = east_asian", "substate_of = CHI"):
    for ln in cb.split("\n"):
        assert not (word in ln and "NOT" in ln), ("a war goal still shields China", ln)
SHIELD = "\n\t\tNOT = {\n\t\t\ttag = HRE\n\t\t\tcivilized = no\n\t\t}"
out, i, shielded, skipped = [], 0, [], []
for m in re.finditer(r"(?m)^(\w+)\s*=\s*\{", cb):
    if m.start() < i or m.group(1) == "peace_order":
        continue
    d, j = 1, m.end()
    while d:
        if cb[j] == "#":
            j = cb.index("\n", j)
            continue
        d += cb[j] == "{"
        d -= cb[j] == "}"
        j += 1
    body = cb[m.start():j]
    bare = re.sub(r"#.*", "", body)
    cu = re.search(r"(?m)^\tcan_use\s*=\s*\{", body)
    if cu and not re.search(r"is_triggered_only\s*=\s*yes|constructing_cb\s*=\s*no", bare):
        body = body[:cu.end()] + SHIELD + body[cu.end():]
        shielded.append(m.group(1))
    else:
        skipped.append(m.group(1))
    out.append(cb[i:m.start()] + body)
    i = j
cb = "".join(out) + cb[i:]
wr("common/cb_types.txt", cb)
print("war goals that cannot be fabricated on an unwesternized HRE: %d | left alone (granted or automatic): %d" % (len(shielded), len(skipped)))
''')
    open("03g_takecapital.py", "w", encoding="utf-8").write(g)
print("patched")
