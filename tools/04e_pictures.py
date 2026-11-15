"""Stage 4e: pictures for the mod's own decisions and events.

Sources are public-domain images from Wikimedia Commons, fetched once by fetch_pictures.py into
tools/assets/pictures/candidates and chosen by hand (PICKS). Each is cropped, toned sepia like
vanilla's art and written in vanilla's own formats:
  decisions: gfx/pictures/decisions/<name>.dds, 95x95, 32-bit uncompressed (vanilla's header reused)
  events:    gfx/pictures/events/<name>.tga,  521x203, 24-bit uncompressed
Then every decision in decisions/WarlordEra.txt gets a "picture = ..." line, and the mod's events
get a fitting picture instead of the one stock picture they all shared.
Run after every stage that writes decisions or events (it edits their files).
"""
import os, re, json, glob, collections
from PIL import Image, ImageOps, ImageDraw
from config import *

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pictures", "candidates")
REC = json.load(open(os.path.join(SRC, "candidates.json"), encoding="utf-8"))

# category -> chosen candidate (file name without .jpg), picked by looking at them
PICKS = {
    "china": "china_3",              # the Forbidden City, old photograph
    "claim": "claim_2",              # map of China
    "taiwan": "claim_1",             # map of Formosa
    "accord": "legitimacy_2",        # officials gathered around the president
    "denounce": "denounce_3",        # the Shun Pao newspaper
    "ambition": "ambition_2",        # infantry charging
    "army": "army_1",                # troops drawn up on parade
    "conscript": "army_2",           # a crowd of soldiers
    "bandits": "bandits_2",          # riders on a country road
    "develop": "develop_3",          # a field gun and its crew
    "tall": "develop_1",             # a city seen from above
    "dominion": "dominion_2",        # an ocean-going junk
    "treasure": "dominion_1",        # junks under fire
    "economy": "economy_1",          # a weaver at his loom
    "identity": "identity_1",        # a column on the march
    "learning": "learning_1",        # students abroad
    "legitimacy": "legitimacy_1",    # Yuan Shikai in uniform
    "republic": "accord_1",          # the five-colour flag
    "mass": "accord_1",
    "opium": "opium_1",              # an opium den
    "opium_burn": "opium_burn_1",    # the destruction of the opium at Humen
    "protection": "protection_1",    # the Great Wall
    "regional": "regional_2",        # the Nanjing city wall
    "revenue": "revenue_1",          # the salt merchants' guild hall at Zigong
    "settle": "settle_2",            # an emigrant labourer
    "road_war": "road_war_1",        # the Northern Expedition
    "outlook": "outlook_2",          # an ironclad
    "militia": "protection_2",       # village men mustered
    "advisors": "ambition_1",        # a machine-gun crew under instruction
    "ev_warlords": "legitimacy_2", "ev_sea": "dominion_2", "ev_bandits": "bandits_2", "ev_greatwar": "ambition_1", "ev_students": "learning_1",
}
# never use: bandits_1 (gruesome), learning_2 (unrelated), detente_* and tall_* (modern or not Chinese)
# categories with no good candidate borrow a related picture
BORROW = {"regional": "china", "settle": "dominion", "accord": "identity", "denounce": "claim", "detente": "accord", "ambition": "road_war",
          "protection": "claim", "tall": "university", "opium_burn": "opium", "revenue": "mint", "bandits": "conscript", "army": "identity",
          "economy": "develop", "learning": "university", "outlook": "dominion", "legitimacy": "china", "republic": "legitimacy", "land": "claim",
          "mass": "republic", "whampoa": "army", "shipyard": "outlook", "university": "china", "railway": "develop", "treasure": "dominion",
          "mint": "claim", "tibet": "claim", "mongolia": "claim", "korea": "claim", "annam": "claim", "sikh": "claim", "persia": "claim",
          "japan": "claim", "taiwan": "dominion", "suvar": "claim", "nanyang": "dominion", "advisors": "army", "militia": "bandits",
          "conscript": "identity", "road_war": "identity", "develop": "claim", "identity": "claim", "dominion": "claim", "china": "claim",
          "ev_sea": "dominion", "ev_students": "mass", "ev_taiwan": "taiwan", "ev_horde": "mongolia", "ev_khalsa": "sikh", "ev_persia": "persia",
          "ev_oil": "develop", "ev_greatwar": "road_war", "ev_warlords": "identity", "ev_bandits": "bandits"}


def resolve(cat, seen=()):
    if cat in PICKS:
        return PICKS[cat]
    if cat in BORROW and cat not in seen:
        return resolve(BORROW[cat], seen + (cat,))
    return None


def sepia(im):
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=1)
    return ImageOps.colorize(g, (38, 24, 12), (238, 222, 190), mid=(150, 118, 78))


def crop_to(im, w, h, focus=0.4):
    """crop to the w:h shape (keeping the upper-middle of tall pictures, where faces usually are) and resize"""
    iw, ih = im.size
    if iw * h > ih * w:
        nw = ih * w // h
        x = (iw - nw) // 2
        im = im.crop((x, 0, x + nw, ih))
    else:
        nh = iw * h // w
        y = int((ih - nh) * focus)
        im = im.crop((0, y, iw, y + nh))
    return im.resize((w, h), Image.LANCZOS)


_hdr = open(glob.glob(os.path.join(V, "gfx", "pictures", "decisions", "*.dds"))[0], "rb").read(128)
os.makedirs(os.path.join(OUT, "gfx", "pictures", "decisions"), exist_ok=True)
os.makedirs(os.path.join(OUT, "gfx", "pictures", "events"), exist_ok=True)
made, credits = {}, collections.OrderedDict()


def picture(cat, kind):
    """returns the picture name for a category, making the file on first use; None if there is no source"""
    cand = resolve(cat)
    if cand is None:
        return None
    name = "we_%s_%s" % ("d" if kind == "decision" else "e", cand)
    if name not in made:
        im = Image.open(os.path.join(SRC, cand + ".jpg")).convert("RGB")
        if kind == "decision":
            im = sepia(crop_to(im, 95, 95))
            ImageDraw.Draw(im).rectangle([0, 0, 94, 94], outline=(30, 20, 10))
            r, g, b = im.split()
            raw = Image.merge("RGBA", (b, g, r, Image.new("L", im.size, 255))).tobytes()
            open(os.path.join(OUT, "gfx", "pictures", "decisions", name + ".dds"), "wb").write(_hdr + raw)
        else:
            sepia(crop_to(im, 521, 203)).save(os.path.join(OUT, "gfx", "pictures", "events", name + ".tga"), format="TGA")
        made[name] = cand
        credits[cand] = REC[cand]
    return name


# ---------------------------------------------------------------- which decision gets which picture
RULES = [
    (r"^form_china$", "china"), (r"^form_(beiyang|liangguang|shu|wu|chu|dian|northwest|manchuria)$", "regional"),
    (r"^(form_mongol_empire|mongol_|call_the_kurultai|revive_the_tumens|claim_inner_mongolia|ride_on_beijing|claim_dzungaria|claim_buryatia|reclaim_outer_mongolia)", "mongolia"),
    (r"^(form_khalsa_raj|expand_fauj_i_khas|hire_european_generals|seize_the_khyber|claim_hindustan|conquer_sindh|dogra_expedition)", "sikh"),
    (r"^(form_persian_empire|proclaim_nizam_e_jadid|found_dar_ul_funun|reclaim_herat|claim_mesopotamia|claim_the_caucasus|subdue_the_khanates)", "persia"),
    (r"^form_suvarnabhumi$", "suvar"), (r"^form_", "claim"), (r"^charter_", "dominion"), (r"^settle_", "settle"),
    (r"^(SXI|HNC)_road_a$", "tall"), (r"_road_[ab]$", "road_war"),
    (r"_identity$", "identity"), (r"_develop$", "develop"), (r"_ambition$", "ambition"), (r"_claim$", "claim"), (r"_accord$", "accord"),
    (r"_denounce$", "denounce"), (r"_detente$", "detente"), (r"_treaty_", "accord"), (r"_protection$", "protection"),
    (r"^opium_monopoly_dec$", "opium"), (r"^opium_suppression_dec$", "opium_burn"), (r"^(reform_salt_gabelle|raise_likin)$", "revenue"),
    (r"^(recruit_bandits|suppress_bandits)$", "bandits"), (r"^arm_village_militia$", "militia"), (r"^introduce_conscription$", "conscript"),
    (r"^raise_model_army$", "army"), (r"^(road_state_arsenals|expand_hanyang_arsenal)$", "develop"), (r"^road_merchant_enterprise$", "economy"),
    (r"^(road_agrarian_order|land_to_the_tiller|uphold_the_landlords)$", "land"), (r"^hire_foreign_advisors$", "learning"),
    (r"^(found_national_academy|found_peking_university)$", "university"), (r"^(maritime_policy|raise_beiyang_fleet)$", "outlook"),
    (r"^(continental_policy|launch_northern_expedition)$", "road_war"), (r"^claim_the_mandate$", "legitimacy"),
    (r"^proclaim_provisional_republic$", "republic"), (r"^(build_party_state|convene_parliament|grant_provincial_constitution)$", "mass"),
    (r"^found_whampoa$", "whampoa"), (r"^build_jiangnan_shipyard$", "shipyard"), (r"^build_longhai_railway$", "railway"),
    (r"^revive_treasure_fleet$", "treasure"), (r"^(collect_remittances|open_nanyang_ports)$", "nanyang"), (r"^start_new_life_movement$", "tall"),
    (r"^open_silver_mint$", "mint"), (r"^pacify_tibet$", "tibet"), (r"^claim_korea$", "korea"), (r"^claim_annam$", "annam"),
    (r"^hire_chinese_advisors$", "advisors"), (r"^(sonno_joi_dec|japan_)", "japan"), (r"^taiwan_", "taiwan"),
]
p = os.path.join(OUT, "decisions", "WarlordEra.txt")
t = open(p, encoding=ENC).read().replace("\r\n", "\n")
t = re.sub(r"(?m)^\t\tpicture = \w+\n", "", t)
used, nopic = collections.Counter(), []


def _dec(m):
    key = m.group(1)
    cat = next((c for rx, c in RULES if re.search(rx, key)), "claim")
    name = picture(cat, "decision")
    if not name:
        nopic.append(key)
        return m.group(0)
    used[cat] += 1
    return "%s\t\tpicture = %s\n" % (m.group(0), name)


t = re.sub(r"(?m)^\t(\w+) = \{\n", _dec, t)
wr("decisions/WarlordEra.txt", t)

# ---------------------------------------------------------------- events: by what their title says
loc = {}
for f in glob.glob(os.path.join(OUT, "localisation", "*.csv")):
    for l in open(f, encoding=ENC, errors="replace").read().splitlines():
        q = l.split(";")
        if len(q) > 1 and q[0].startswith("EVTNAME"):
            loc[q[0]] = q[1]
EV_RULES = [(r"Khalsa", "ev_khalsa"), (r"Horde", "ev_horde"), (r"Shah", "ev_persia"), (r"Taiwan", "ev_taiwan"),
            (r"Sea Lanes|Settlers|New World|Scramble", "ev_sea"), (r"Students", "ev_students"), (r"Great Wars", "ev_greatwar"),
            (r"Bandits", "ev_bandits"), (r"Defection|Silver Bullets", "conscript")]
p = os.path.join(OUT, "events", "WarlordEra.txt")
t = open(p, encoding=ENC).read().replace("\r\n", "\n")
evn = collections.Counter()


def _ev(m):
    title = loc.get(m.group(2), "")
    cat = next((c for rx, c in EV_RULES if re.search(rx, title)), "ev_warlords")
    name = picture(cat, "event")
    if not name:
        return m.group(0)
    evn[cat] += 1
    return '%s\tpicture = "%s"\n' % (m.group(1), name)


t = re.sub(r'((?:country_event) = \{\n\tid = \d+\n\ttitle = "(EVTNAME\d+)"\n\tdesc = "EVTDESC\d+"\n)\tpicture = "\w+"\n', _ev, t)
wr("events/WarlordEra.txt", t)

lines = ["Pictures of decisions and events in this mod are public-domain images from Wikimedia Commons,", "cropped and toned. Sources:", ""]
for cand, r in credits.items():
    lines.append("%s\n    %s | %s\n    %s" % (r["title"], r["author"] or "author unknown", r["licence"], r["page"]))
wr("picture_credits.txt", "\n".join(lines) + "\n")
print("pictures made: %d decision, %d event | decisions with a picture: %d, without: %d | events given a picture: %d"
      % (sum(1 for n in made if n.startswith("we_d_")), sum(1 for n in made if n.startswith("we_e_")), sum(used.values()), len(nopic), sum(evn.values())))
unsourced = sorted(c for c in set(c for _, c in RULES) | set(c for _, c in EV_RULES) | {"ev_warlords", "claim"} if c not in PICKS)
print("categories borrowing a related picture:", unsourced)
