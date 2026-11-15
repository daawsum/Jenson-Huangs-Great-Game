"""One-off patch: Taiwan's two exclusive roads, and 70% literacy for Taiwan, Shanghai and Hainan."""
c = open("content.py", encoding="utf-8").read()
for a, b in (('"SHG": 0.50,', '"SHG": 0.70,'), ('"TWN": 0.24,', '"TWN": 0.70,'), ('"HNI": 0.16,', '"HNI": 0.70,')):
    assert c.count(a) == 1, a
    c = c.replace(a, b)
open("content.py", "w", encoding="utf-8").write(c)

s = open("03_gameplay.py", encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


rep(r'''# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''', r'''# ---- Taiwan, once it holds Hainan and Shanghai: the mainland or the ocean, never both
_canton = sorted(p for p, o in OWNER.items() if o == "GDG")
_java = sorted(p for r, ps in REGIONS.items() for p in ps if 1413 in ps)        # the state of Java, Madura included
assert len(_canton) > 5 and len(_java) > 5 and "javan = {" in open(os.path.join(OUT, "common", "cultures.txt"), encoding=ENC).read()
_tw_need = "war = no\n" + owns(*(_hainan + [1538]))
choice("taiwan_road", STATE, [
    ("taiwan_great_game", "The Great Game", "With Hainan and Shanghai in hand, Formosa is a mainland power. Claim Guangdong and take the Cantonese into the nation: the contest for China itself begins.",
     _tw_need, "".join("%d = { add_core = THIS }\n" % p for p in _canton) + "add_accepted_culture = yue\nprestige = 10", None),
    ("taiwan_maritime_hegemon", "The Maritime Hegemon", "With Hainan and Shanghai in hand, Formosa commands the China seas. Turn south instead: claim Java, take the Javanese into the nation, and school a generation of navigators.",
     _tw_need, "".join("%d = { add_core = THIS }\n" % p for p in _java) + "add_accepted_culture = javan\nprestige = 10", "maritime_hegemon")],
    potential="tag = TWN")

# ---- every major: identity, development, ambition against its rival, a contested claim, an accord
''')
rep(r'''mod("taiwanese_dream", "The Taiwanese Dream",''', r'''mod("maritime_hegemon", "Maritime Hegemon", "Formosa's schools turn out navigators and its squadrons keep the sea far from any friendly port.",
    education_efficiency_modifier=0.15, supply_range=0.33)
mod("taiwanese_dream", "The Taiwanese Dream",''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
