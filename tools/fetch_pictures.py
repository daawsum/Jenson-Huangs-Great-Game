"""Fetch candidate pictures for decisions and events from Wikimedia Commons (public domain only).

For every category it searches Commons, keeps up to three bitmap results whose licence is public
domain or CC0, saves a 640-pixel-wide copy to tools/assets/pictures/candidates/<category>_<n>.jpg and
records title, author, licence and source page in candidates.json. A person then picks one per
category (PICKS in 04e_pictures.py); nothing here goes into the mod by itself.
"""
import os, sys, json, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(HERE, "assets", "pictures", "candidates")
os.makedirs(DST, exist_ok=True)
UA = {"User-Agent": "Victoria2ModPictureFetch/1.0 (build script; public domain images only)"}
API = "https://commons.wikimedia.org/w/api.php"

QUERIES = {
    "china": "Forbidden City Beijing 1900 photograph",
    "regional": "Nanjing city wall",
    "dominion": "Chinese junk ship painting 19th century",
    "settle": "Chinese emigration 19th century",
    "claim": "map of China provinces 1910s",
    "accord": "Beiyang government 1912",
    "denounce": "Shen Bao newspaper",
    "detente": "Chinese teahouse",
    "identity": "Beiyang Army",
    "develop": "Hanyang Arsenal",
    "ambition": "Chinese soldiers 1920s",
    "protection": "Great Wall of China 1900s",
    "road_war": "Northern Expedition 1926",
    "tall": "Chinese school 1910s",
    "opium": "opium smokers China",
    "opium_burn": "destruction of opium Humen",
    "revenue": "Zigong salt well",
    "bandits": "Honghuzi",
    "army": "New Army Qing",
    "economy": "silk reeling China",
    "learning": "Chinese Educational Mission",
    "outlook": "Dingyuan ironclad",
    "legitimacy": "Yuan Shikai",
    "republic": "Sun Yat-sen 1912",
    "land": "rice farmers China",
    "mass": "National Assembly Republic of China 1913",
    "whampoa": "Whampoa Military Academy",
    "shipyard": "Foochow Arsenal",
    "university": "Imperial University of Peking",
    "railway": "Peking Mukden railway locomotive",
    "treasure": "Zheng He ship",
    "mint": "Yuan Shikai dollar",
    "tibet": "Potala Palace 1904",
    "mongolia": "Urga 1913",
    "korea": "Gyeongbokgung 1900s",
    "annam": "Hue citadel 1900s",
    "sikh": "Ranjit Singh",
    "persia": "Naser al-Din Shah Qajar",
    "japan": "samurai Felice Beato",
    "taiwan": "Fort Zeelandia",
    "suvar": "Wat Arun 1900s",
    "nanyang": "Singapore harbour 1890s",
    "advisors": "Charles George Gordon Ever Victorious Army",
    "militia": "Boxer rebellion militia",
    "conscript": "Chinese warlord soldiers",
    "ev_warlords": "Zhang Zuolin",
    "ev_sea": "junk Hong Kong harbour 1880s",
    "ev_students": "May Fourth Movement",
    "ev_taiwan": "Koxinga",
    "ev_horde": "Mongolian soldiers 1921",
    "ev_khalsa": "Sikh Empire army painting",
    "ev_persia": "Persian Cossack Brigade",
    "ev_oil": "oil derrick 1900s",
    "ev_greatwar": "Chinese Labour Corps",
}


PAUSE = 2.5          # seconds between any two requests


def get(url):
    import urllib.error
    for attempt in range(4):
        time.sleep(PAUSE)
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 60 * (attempt + 1)
            print("   server asked us to slow down; waiting %d s" % min(wait, 300), flush=True)
            time.sleep(min(wait, 300))
    raise RuntimeError("still rate limited")


def free(meta):
    lic = (meta.get("LicenseShortName", {}).get("value", "") + " " + meta.get("License", {}).get("value", "")).lower()
    return any(k in lic for k in ("public domain", "pd", "cc0")) and "cc-by" not in lic and "cc by" not in lic


def strip_html(x):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x or "")).strip()[:160]


recf = os.path.join(DST, "candidates.json")
rec = json.load(open(recf, encoding="utf-8")) if os.path.exists(recf) else {}
only = set(sys.argv[1:])
for cat, q in QUERIES.items():
    if only and cat not in only:
        continue
    if not only and any(k.startswith(cat + "_") for k in rec):
        continue
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrlimit": 14, "gsrsearch": q + " filetype:bitmap",
         "prop": "imageinfo", "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 500}
    try:
        data = json.loads(get(API + "?" + urllib.parse.urlencode(p)))
    except Exception as e:
        print(cat, "search failed:", e)
        continue
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda x: x.get("index", 99))
    n = 0
    for pg in pages:
        ii = (pg.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 380 or not free(meta) or not ii.get("thumburl"):
            continue
        n += 1
        key = "%s_%d" % (cat, n)
        try:
            open(os.path.join(DST, key + ".jpg"), "wb").write(get(ii["thumburl"]))
        except Exception as e:
            print(key, "download failed:", e)
            n -= 1
            continue
        rec[key] = {"title": pg["title"], "author": strip_html(meta.get("Artist", {}).get("value")), "licence": strip_html(meta.get("LicenseShortName", {}).get("value")),
                    "page": ii.get("descriptionurl"), "query": q}
        if n == 2:
            break
    print("%-12s %d candidates" % (cat, n), flush=True)
    json.dump(rec, open(recf, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("candidates on disk:", len(rec))
