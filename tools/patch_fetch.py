"""One-off patch of fetch_pictures.py: polite pacing (back off when the server says so) and simpler searches."""
s = open("fetch_pictures.py", encoding="utf-8").read()
a = '''def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
'''
assert s.count(a) == 1
s = s.replace(a, '''PAUSE = 5.0          # seconds between any two requests


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
''')
s = s.replace("        time.sleep(0.4)\n", "").replace("    time.sleep(0.6)\n", "")
s = s.replace('print("%-12s %d candidates" % (cat, n))', 'print("%-12s %d candidates" % (cat, n), flush=True)')
new = {
    "regional": "Nanjing city wall", "settle": "Chinese emigration 19th century", "accord": "Beiyang government 1912",
    "denounce": "Shen Bao newspaper", "detente": "Chinese teahouse", "identity": "Beiyang Army", "ambition": "Chinese soldiers 1920s",
    "protection": "Great Wall of China 1900s", "road_war": "Northern Expedition 1926", "tall": "Chinese school 1910s",
    "opium": "opium smokers China", "opium_burn": "destruction of opium Humen", "revenue": "Zigong salt well",
    "bandits": "Honghuzi", "army": "New Army Qing", "economy": "silk reeling China", "learning": "Chinese Educational Mission",
    "outlook": "Dingyuan ironclad", "legitimacy": "Yuan Shikai", "republic": "Sun Yat-sen 1912", "land": "rice farmers China",
    "mass": "National Assembly Republic of China 1913", "whampoa": "Whampoa Military Academy", "shipyard": "Foochow Arsenal",
    "university": "Imperial University of Peking", "railway": "Peking Mukden railway locomotive", "treasure": "Zheng He ship",
    "mint": "Yuan Shikai dollar", "tibet": "Potala Palace 1904", "mongolia": "Urga 1913", "korea": "Gyeongbokgung 1900s",
    "annam": "Hue citadel 1900s", "sikh": "Ranjit Singh", "persia": "Naser al-Din Shah Qajar", "japan": "samurai Felice Beato",
    "taiwan": "Fort Zeelandia", "suvar": "Wat Arun 1900s", "nanyang": "Singapore harbour 1890s", "advisors": "Charles George Gordon Ever Victorious Army",
    "militia": "Boxer rebellion militia", "conscript": "Chinese warlord soldiers", "ev_warlords": "Zhang Zuolin", "ev_sea": "junk Hong Kong harbour 1880s",
    "ev_students": "May Fourth Movement", "ev_taiwan": "Koxinga", "ev_horde": "Mongolian soldiers 1921", "ev_khalsa": "Sikh Empire army painting",
    "ev_persia": "Persian Cossack Brigade", "ev_oil": "oil derrick 1900s", "ev_greatwar": "Chinese Labour Corps",
}
import re
for k, v in new.items():
    s, n = re.subn(r'(?m)^    "%s": "[^"]*",' % k, '    "%s": "%s",' % (k, v), s)
    assert n == 1, k
open("fetch_pictures.py", "w", encoding="utf-8").write(s)
print("patched")
