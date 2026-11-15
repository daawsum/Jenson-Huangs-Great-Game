"""One-off patch: ruling parties that fit their government; Mongolia civilized with two culture decisions;
Xinjiang may take both of its roads."""
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (a[:70], s.count(a))
    s = s.replace(a, b)


# ---- ruling party must be of an ideology the form of government allows
rep(r'''    mm = re.search(r'ruling_party\s*=\s*"?(\w+)"?', text)
    if mm and mm.group(1) in valid:
        return text
    for want in ("conservative", "reactionary", "liberal"):
        pick = [n for n, i in valid.items() if i == want]''', r'''    mm = re.search(r'ruling_party\s*=\s*"?(\w+)"?', text)
    gv = re.search(r"(?m)^government\s*=\s*(\w+)", text)
    allowed = GOV_IDEOLOGIES.get(gv.group(1)) if gv else None
    fits = lambda n: allowed is None or valid[n] in allowed
    if mm and mm.group(1) in valid and fits(mm.group(1)):
        return text
    if not any(fits(n) for n in valid):
        # no party of an allowed kind exists in 1836 (a "presidential dictatorship" with no reactionary
        # party): the country becomes an absolute monarchy, which every party of the time can serve
        print("  government of %s changed: %s -> absolute_monarchy (no party it allows exists in 1836)" % (tag, gv.group(1)))
        text = text[:gv.start(1)] + "absolute_monarchy" + text[gv.end(1):]
        allowed = GOV_IDEOLOGIES["absolute_monarchy"]
        mm = re.search(r'ruling_party\s*=\s*"?(\w+)"?', text)
        if mm and mm.group(1) in valid and fits(mm.group(1)):
            return text
    for want in ("conservative", "reactionary", "liberal"):
        pick = [n for n, i in valid.items() if i == want and fits(n)]''')
rep(r'''def fix_party(tag, text):''', r'''GOV_IDEOLOGIES = {}
for _g, _b, _s, _e in blocks(re.sub(r"#.*", "", rd("common", "governments.txt"))):
    GOV_IDEOLOGIES[_g] = set(re.findall(r"(\w+)\s*=\s*yes", _b)) - {"election", "appoint_ruling_party"}


def fix_party(tag, text):''')

# ---- Mongolia starts civilized
rep(r'''_tw = glob.glob(os.path.join(OUT, "history", "countries", "TWN - *.txt"))[0]''', r'''_mg = os.path.join(OUT, "history", "countries", hname["MGL"])
t_ = open(_mg, encoding=ENC).read().replace("\r\n", "\n")
assert "civilized = no" in t_
t_ = t_.replace("civilized = no", "civilized = yes")
t_ = re.sub(r"(?m)^\w+ = (yes|no)_(%s)\n" % "|".join(REF_E + REF_M), "", t_)
t_ = t_.replace("set_country_flag = partial_nation\n", "")
t_ += "schools = army_tech_school\n" + techs(HORDE_TECH)
open(_mg, "w", encoding=ENC, newline="\r\n").write(t_)
tier["MGL"] = "horde"
_tw = glob.glob(os.path.join(OUT, "history", "countries", "TWN - *.txt"))[0]''')
open("02_world.py", "w", encoding="utf-8").write(s)

c = open("content.py", encoding="utf-8").read()
a = '''["KSG", "KOK", "BUK", "KHI"], ["uighur"], dict('''
assert c.count(a) == 1
c = c.replace(a, '''["KSG", "KOK", "BUK", "KHI"], ["uighur", "kazak", "kirgiz", "uzbek", "turkmen", "tajik"], dict(''')
open("content.py", "w", encoding="utf-8").write(c)

s = open("03_gameplay.py", encoding="utf-8").read()
rep(r'''    choice("road_" + tag, STATE, built, potential="tag = %s" % tag)''', r'''    if tag == "XIN":                # Xinjiang faces both ways at once: it may take both roads
        for key, title, text, allow, eff, modname in built:
            once(key, title, text, "tag = XIN", allow, eff, modname, tech=STATE)
    else:
        choice("road_" + tag, STATE, built, potential="tag = %s" % tag)''')
rep(r'''once("call_the_kurultai",''', r'''once("mongol_felt_tents", "Khan of All Who Live in Felt Tents", "Chinggis took that title when the steppe peoples swore to him. The Kazakhs, Kirghiz, Uzbeks, Turkmen, Tajiks and Uighurs are of the same world as we are: they ride in the horde as equals.",
     MG, "war = no", "".join("add_accepted_culture = %s\n" % k for k in ("uighur", "kazak", "kirgiz", "uzbek", "turkmen", "tajik")) + "prestige = 5")
once("mongol_scourge_of_the_north", "Scourge of the North", "The forest peoples of Siberia and the Manchu banners were our subjects and our kin by marriage before they were anyone else's. They ride with us again.",
     MG, "war = no", "add_accepted_culture = siberian\nadd_accepted_culture = manchu\nprestige = 5")
once("call_the_kurultai",''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
