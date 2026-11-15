"""One-off patch: Yunnan's road to Burma and Bengal, the Ladakh pass, primitive Russia and Ottomans,
and a build check that the protectorate war goal is usable."""
s = open("02_world.py", encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)


rep('''for t, (ptag, name, col) in SUCCESSOR.items():      # a successor is as backward as its parent
    if t in tier and ptag in tier:
        tier[t] = tier[ptag]
''', '''for t, (ptag, name, col) in SUCCESSOR.items():      # a successor is as backward as its parent
    if t in tier and ptag in tier:
        tier[t] = tier[ptag]
# Russia never became a state at all in this world, and the Ottoman Empire is a hollow giant: every
# country standing on what was Russian land, and the Ottomans, are primitive.
RUSSIAN = {tag for tag, ps in owned.items() if tag not in WARLORDS and tag != "HRE"
           and sum(1 for q in ps if q in vprov and vprov[q]["owner"] == "RUS") * 2 > len(ps)}
for tag in RUSSIAN | {"TUR"}:
    tier[tag] = "primitive"
print("made primitive:", sorted(RUSSIAN | {"TUR"}))
''')
rep('''wr("map/region.txt", "\\n".join(out) + "\\n")''', '''wr("map/region.txt", "\\n".join(out) + "\\n")
# The Ladakh road: vanilla walls Leh off from western Tibet as impassable, so the Sikhs could never
# reach Tibet at all. That one border is opened; every other mountain wall stays.
_adj = rd("map", "adjacencies.csv").replace("\\r\\n", "\\n")
_open = [l for l in _adj.split("\\n") if l.startswith("1226;1592;impassable")]
assert len(_open) == 1, _open
wr("map/adjacencies.csv", _adj.replace(_open[0] + "\\n", ""))''')
open("02_world.py", "w", encoding="utf-8").write(s)

s = open("03_gameplay.py", encoding="utf-8").read()
rep('''NO_TECH = {"open_nanyang_ports", "taiwan_claims"}''', '''NO_TECH = {"open_nanyang_ports", "taiwan_claims", "yunnan_burma_road"}''')
rep('''"claim_korea": NATIO, "claim_annam": NATIO, "form_china": REVO, "japan_accept_koreans": STATE,''',
    '''"claim_korea": NATIO, "claim_annam": NATIO, "form_china": REVO, "japan_accept_koreans": STATE,
    "yunnan_road_to_bengal": STATE, "yunnan_lords_of_bengal": STATE,''')
rep('''# ---- every great clique chooses its road once it has swallowed the neighbour it claimed
''', '''# ---- Yunnan: over the mountains to Burma, and down the Brahmaputra to Bengal
_YN = "OR = {\\n\\ttag = YNN\\n\\ttag = NZO\\n}"
_burma = sorted(p for p, o in OWNER.items() if o == "BUR")
_dacca = P("Dacca")
_bengal = OWNER[_dacca]
assert _burma and _bengal and _bengal not in WARLORDS, _bengal
once("yunnan_burma_road", "The Burma Road", "The caravan road from Kunming over the Salween to Mandalay is older than any border. Claim Burma for Yunnan and take the Burmese in as our own people.",
     _YN, "war = no", "".join("%d = { add_core = THIS }\\n" % p for p in _burma) + "add_accepted_culture = %s\\nprestige = 5" % _culture("burmese"))
once("yunnan_road_to_bengal", "The Road to Bengal", "Beyond Burma the Brahmaputra runs down to Dacca and the sea. A state that can build roads can march an army along them: prepare the conquest of Bengal.",
     _YN + "\\nhas_country_flag = did_yunnan_burma_road\\nexists = %s" % _bengal, "war = no",
     "casus_belli = { target = %s type = conquest months = 120 }\\nprestige = 5" % _bengal)
once("yunnan_lords_of_bengal", "From the Mountains to the Sea", "Dacca is ours. Yunnan has a port, a delta and thirty million new subjects. Its governors will rule them as Yunnanese: one script, one law, one school.",
     _YN + "\\nhas_country_flag = did_yunnan_road_to_bengal", "war = no\\nowns = %d" % _dacca, "prestige = 10", "yunnan_delta")

# ---- every great clique chooses its road once it has swallowed the neighbour it claimed
''')
rep('''mod("taiwanese_dream", "The Taiwanese Dream",''', '''mod("yunnan_delta", "From the Mountains to the Sea", "Yunnan's governors make one people of everyone from Kunming to the Bay of Bengal.", global_assimilation_rate=1.0)
mod("taiwanese_dream", "The Taiwanese Dream",''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)

g = open("03g_takecapital.py", encoding="utf-8").read()
a = 'print("free peoples is switched off and has no sized versions")'
assert g.count(a) == 1
g = g.replace(a, a + '''
# the protectorate goal (a civilized country against a small uncivilized one) must be vanilla's, plus the HRE shield only
import difflib
def _one(text, name):
    m_ = re.search(r"(?m)^%s\\s*=\\s*\\{" % name, text)
    d_, j_ = 1, m_.end()
    while d_:
        d_ += text[j_] == "{"
        d_ -= text[j_] == "}"
        j_ += 1
    return [l.strip() for l in re.sub(r"#.*", "", text[m_.start():j_]).split("\\n") if l.strip()]
_v = _one(rd("common", "cb_types.txt").replace("\\r\\n", "\\n"), "establish_protectorate_casus_belli")
_m = _one(cb, "establish_protectorate_casus_belli")
_extra = [l[2:] for l in difflib.ndiff(_v, _m) if l[:2] in ("+ ", "- ")]
assert _extra == ["NOT = {", "AND = {", "tag = HRE", "civilized = no", "}", "}"], _extra
print("establish protectorate: vanilla's rules, usable by civilized countries on small uncivilized ones")''')
open("03g_takecapital.py", "w", encoding="utf-8").write(g)
print("patched")
