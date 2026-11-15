"""Stage 4f: a flag of its own for every clique, a variant for each kind of government, and
government-specific country names.

Flags are drawn here (93x64, like vanilla's). Where a clique has a historical flag it is the model:
the five-colour flag of the Beiyang republic for Zhili, the Blue Sky and White Sun for Canton, the
iron-blood eighteen-star flag for Hubei, the red-over-blue with a yellow star of the Fujian People's
Government, the yellow tiger of the Republic of Formosa, the bordered banners for the Manchu and
Mongol leagues, the crescent for the Muslim north-west, the sun and rays for Tibet.
Each flag has four variants the game picks by government (governments.txt flagType):
  republic  - a five-colour band along the foot of the flag
  monarchy  - an imperial yellow border and a red pearl
  communist - red field and yellow star, the clique's flag in the corner
  fascist   - dark blue field and white sun, the clique's flag in the canton
Names: <TAG>_<government> localisation keys, as vanilla does (e.g. CHI_absolute_monarchy).
Run after 02_world.py (which writes plain flags for every new tag).
"""
import os, math
from PIL import Image, ImageDraw
from config import *

W, H = 93, 64
R, Y, B, WH, K, G = (200, 30, 35), (245, 200, 40), (25, 60, 150), (245, 240, 230), (25, 25, 25), (30, 120, 70)
SKY, P, O, TEAL, NAVY = (70, 150, 220), (120, 60, 140), (230, 120, 30), (30, 130, 140), (15, 30, 90)
FIVE = [R, Y, B, WH, K]


def new(c):
    im = Image.new("RGB", (W, H), c)
    return im, ImageDraw.Draw(im)


def hstripes(d, cols, y0=0, y1=H):
    n = len(cols)
    for i, c in enumerate(cols):
        d.rectangle([0, y0 + (y1 - y0) * i // n, W, y0 + (y1 - y0) * (i + 1) // n - 1], fill=c)


def vstripes(d, cols):
    n = len(cols)
    for i, c in enumerate(cols):
        d.rectangle([W * i // n, 0, W * (i + 1) // n - 1, H], fill=c)


def star(d, cx, cy, r, c, points=5, inner=0.4, rot=-90):
    pts = []
    for i in range(points * 2):
        a = math.radians(rot + i * 180 / points)
        rr = r if i % 2 == 0 else r * inner
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=c)


def sun(d, cx, cy, r, c, rays=12):
    star(d, cx, cy, r, c, rays, 0.55)
    d.ellipse([cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5], fill=c)


def disc(d, cx, cy, r, c):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def crescent(d, cx, cy, r, c, bg):
    disc(d, cx, cy, r, c)
    disc(d, cx + r * 0.38, cy, r * 0.82, bg)


def border(d, c, w=5):
    for i in range(w):
        d.rectangle([i, i, W - 1 - i, H - 1 - i], outline=c)


def banner(field, edge, emblem):          # the bordered banners of the Manchu and Mongol leagues
    im, d = new(field)
    border(d, edge, 7)
    disc(d, W // 2, H // 2, 12, emblem)
    return im


def f_ZHL():
    im, d = new(R); hstripes(d, FIVE); return im
def f_FTN():
    im, d = new(Y); d.rectangle([0, 50, W, H], fill=K); sun(d, 46, 26, 17, R, 8); return im
def f_AHC():
    im, d = new(WH); d.rectangle([0, 10, W, 19], fill=B); d.rectangle([0, 44, W, 53], fill=B); star(d, 46, 32, 11, R); return im
def f_SXI():
    im, d = new(B); border(d, WH, 4); star(d, 46, 32, 17, Y); return im
def f_GMJ():
    im, d = new(R); d.rectangle([0, 0, 45, 31], fill=NAVY); sun(d, 22, 16, 12, WH); return im
def f_SDG():
    im, d = new(WH); d.polygon([(0, 0), (42, 32), (0, 63)], fill=B); disc(d, 62, 32, 13, R); return im
def f_HNA():
    im, d = new(Y); d.rectangle([0, 24, W, 39], fill=K); star(d, 46, 32, 9, R); return im
def f_JSU():
    im, d = new(R); vstripes(d, FIVE); return im
def f_ZHJ():
    im, d = new(SKY); d.rectangle([0, 40, W, 45], fill=WH); d.rectangle([0, 52, W, 57], fill=WH); sun(d, 20, 18, 12, Y); return im
def f_FUJ():
    im, d = new(R); d.rectangle([0, 32, W, H], fill=B); star(d, 46, 32, 14, Y); return im
def f_GDG():
    im, d = new(NAVY); sun(d, 46, 32, 24, WH); return im
def f_GXI():
    im, d = new(R); d.rectangle([0, 0, 40, 28], fill=NAVY); sun(d, 20, 14, 10, WH); d.rectangle([0, 52, W, H], fill=WH); return im
def f_HNC():
    im, d = new(WH); d.rectangle([0, 0, W, 13], fill=R); d.rectangle([0, 50, W, H], fill=B); star(d, 46, 32, 12, Y); return im
def f_HBE():
    im, d = new(R); star(d, 46, 32, 27, K, 9, 0.5)
    for i in range(18):
        a = math.radians(i * 20 + (10 if i % 2 else 0)); rr = 24 if i % 2 == 0 else 12
        disc(d, 46 + rr * math.cos(a), 32 + rr * math.sin(a), 2, Y)
    return im
def f_JXI():
    im, d = new(R); d.polygon([(0, 50), (0, 63), (20, 63), (92, 13), (92, 0), (72, 0)], fill=WH); star(d, 16, 14, 9, Y); return im
def f_SZC():
    im, d = new(R); disc(d, 46, 32, 20, WH); disc(d, 46, 32, 14, K); disc(d, 46, 32, 9, WH); return im
def f_YNN():
    im, d = new(G); d.rectangle([0, 0, 22, H], fill=Y); star(d, 56, 32, 14, WH); return im
def f_GZH():
    im, d = new(TEAL); d.polygon([(0, 0), (46, 32), (0, 63), (0, 49), (26, 32), (0, 14)], fill=WH); star(d, 68, 32, 9, Y); return im
def f_XBI():
    im, d = new(G); crescent(d, 40, 32, 17, WH, G); star(d, 60, 32, 8, WH); return im
def f_XIN():
    im, d = new(Y); d.rectangle([0, 0, 24, H], fill=B); star(d, 58, 32, 13, R); return im
def f_KSG():
    im, d = new(SKY); crescent(d, 40, 32, 17, WH, SKY); star(d, 60, 32, 8, WH); return im
def f_SYN():
    im, d = new(Y); d.rectangle([0, 24, W, 39], fill=B); disc(d, 46, 32, 10, WH); return im
def f_NXA():
    im, d = new(G); border(d, WH, 4); crescent(d, 46, 32, 16, Y, G); return im
def f_QHI():
    im, d = new(G); d.rectangle([0, 44, W, 49], fill=WH); d.rectangle([0, 54, W, 59], fill=WH); sun(d, 46, 22, 14, Y); return im
def f_XKG():
    im, d = new(O); d.polygon([(0, 0), (38, 32), (0, 63)], fill=B); sun(d, 62, 32, 13, WH); return im
def f_CQG():
    im, d = new(K); d.rectangle([0, 26, W, 37], fill=R); star(d, 46, 32, 17, Y, 8, 0.7); disc(d, 46, 32, 6, K); return im
def f_TIB():
    im, d = new(B)
    for i in range(12):
        a0, a1 = math.radians(180 + i * 15), math.radians(180 + (i + 1) * 15)
        d.polygon([(46, 44), (46 + 90 * math.cos(a0), 44 + 90 * math.sin(a0)), (46 + 90 * math.cos(a1), 44 + 90 * math.sin(a1))], fill=R if i % 2 == 0 else B)
    d.polygon([(8, 63), (46, 30), (84, 63)], fill=WH); disc(d, 46, 26, 9, Y); border(d, Y, 3); return im
def f_HNI():
    im, d = new(SKY); d.rectangle([0, 46, W, H], fill=G); sun(d, 46, 26, 15, Y); return im
def f_TWN():
    im, d = new(B); d.polygon([(46, 8), (78, 32), (46, 56), (14, 32)], fill=Y)
    for x in (34, 44, 54):
        d.line([(x, 22), (x + 6, 42)], fill=K, width=3)
    return im
def f_SHG():
    im, d = new(WH); d.line([(0, 0), (92, 63)], fill=R, width=9); d.line([(0, 63), (92, 0)], fill=R, width=9); disc(d, 46, 32, 11, WH); disc(d, 46, 32, 7, B); return im
def f_XZC():
    im, d = new(Y); d.polygon([(0, 40), (30, 28), (60, 40), (92, 26), (92, 36), (60, 50), (30, 38), (0, 50)], fill=B); disc(d, 74, 14, 8, R); return im


FLAGS = {"ZHL": f_ZHL, "FTN": f_FTN, "AHC": f_AHC, "SXI": f_SXI, "GMJ": f_GMJ, "SDG": f_SDG, "HNA": f_HNA, "JSU": f_JSU, "ZHJ": f_ZHJ,
         "FUJ": f_FUJ, "GDG": f_GDG, "GXI": f_GXI, "HNC": f_HNC, "HBE": f_HBE, "JXI": f_JXI, "SZC": f_SZC, "YNN": f_YNN, "GZH": f_GZH,
         "XBI": f_XBI, "XIN": f_XIN, "KSG": f_KSG, "SYN": f_SYN, "NXA": f_NXA, "QHI": f_QHI, "XKG": f_XKG, "CQG": f_CQG, "TIB": f_TIB,
         "HNI": f_HNI, "TWN": f_TWN, "SHG": f_SHG, "XZC": f_XZC,
         "JLN": lambda: banner(Y, B, R), "HLJ": lambda: banner(WH, R, B), "RHE": lambda: banner(B, R, Y), "CHH": lambda: banner(R, WH, Y)}
assert set(FLAGS) == set(WARLORDS), set(WARLORDS) ^ set(FLAGS)


def republic(base):
    im = base.copy(); hstripes(ImageDraw.Draw(im), FIVE, 54, H); return im


def monarchy(base):
    im = base.copy(); d = ImageDraw.Draw(im); border(d, (240, 190, 20), 5); disc(d, 80, 13, 6, R); disc(d, 80, 13, 3, WH); return im


def communist(base):
    im, d = new((190, 25, 25)); star(d, 22, 20, 15, Y); im.paste(base.resize((36, 25), Image.LANCZOS), (52, 34)); d.rectangle([51, 33, 88, 59], outline=Y); return im


def fascist(base):
    im, d = new(NAVY); sun(d, 60, 38, 19, WH); im.paste(base.resize((36, 25), Image.LANCZOS), (3, 3)); d.rectangle([2, 2, 39, 28], outline=WH); return im


dst = os.path.join(OUT, "gfx", "flags")
seen = {}
for tag, fn in FLAGS.items():
    base = fn()
    key = base.tobytes()
    assert key not in seen, (tag, seen.get(key))
    seen[key] = tag
    for suf, im in (("", base), ("_republic", republic(base)), ("_monarchy", monarchy(base)), ("_communist", communist(base)), ("_fascist", fascist(base))):
        assert os.path.exists(os.path.join(dst, "%s%s.tga" % (tag, suf))), tag          # 02_world.py wrote a plain one; replace it
        im.convert("RGBA").save(os.path.join(dst, "%s%s.tga" % (tag, suf)), compression="tga_rle")

# ---- names by government
PLACE = {"ZHL": "Zhili", "FTN": "Fengtian", "AHC": "Anhui", "SXI": "Shanxi", "GMJ": "Shaanxi", "SDG": "Shandong", "HNA": "Henan", "JSU": "Jiangsu",
         "ZHJ": "Zhejiang", "FUJ": "Fujian", "GDG": "Guangdong", "GXI": "Guangxi", "HNC": "Hunan", "HBE": "Hubei", "JXI": "Jiangxi", "SZC": "Sichuan",
         "YNN": "Yunnan", "GZH": "Guizhou", "XBI": "Gansu", "XIN": "Xinjiang", "JLN": "Jilin", "HLJ": "Heilongjiang", "RHE": "Rehe", "CHH": "Chahar",
         "SYN": "Suiyuan", "NXA": "Ningxia", "QHI": "Qinghai", "XKG": "Xikang", "CQG": "Chongqing", "TIB": "Tibet", "HNI": "Hainan", "TWN": "Formosa",
         "SHG": "Shanghai", "XZC": "Xuzhou", "KSG": "Kashgaria"}
FORMS = {"absolute_monarchy": "Kingdom of %s", "prussian_constitutionalism": "Constitutional Kingdom of %s", "hms_government": "United Kingdom of %s",
         "democracy": "Republic of %s", "bourgeois_dictatorship": "%s Directorate", "proletarian_dictatorship": "%s Soviet Republic",
         "fascist_dictatorship": "National State of %s"}
SPECIAL = {("TIB", "absolute_monarchy"): "Ganden Phodrang", ("TIB", "proletarian_dictatorship"): "Tibetan People's Republic",
           ("SHG", "democracy"): "Free City of Shanghai", ("SHG", "absolute_monarchy"): "Shanghai International Settlement",
           ("SHG", "proletarian_dictatorship"): "Shanghai Commune", ("TWN", "absolute_monarchy"): "Kingdom of Tungning",
           ("XZC", "absolute_monarchy"): "Restored Qing at Xuzhou", ("JXI", "proletarian_dictatorship"): "Chinese Soviet Republic",
           ("FUJ", "democracy"): "People's Republic of Fujian", ("GDG", "fascist_dictatorship"): "Nationalist Government",
           ("GDG", "democracy"): "Republic of China at Canton", ("ZHL", "democracy"): "Beiyang Republic",
           ("FTN", "absolute_monarchy"): "Manchu Regency", ("XBI", "absolute_monarchy"): "Emirate of Gansu",
           ("KSG", "absolute_monarchy"): "Emirate of Kashgaria", ("KSG", "democracy"): "Republic of East Turkestan",
           ("HNC", "democracy"): "Autonomous Republic of Hunan", ("SXI", "fascist_dictatorship"): "Model State of Shanxi"}
govs = set(k for k, b, s_, e_ in blocks(__import__("re").sub(r"#.*", "", rd("common", "governments.txt"))))
assert set(FORMS) <= govs, set(FORMS) - govs
lines = []
for tag in WARLORDS:
    for gov, form in FORMS.items():      # presidential_dictatorship keeps the clique's own name
        lines.append("%s_%s;%s;;;;;;;;;;;;;x" % (tag, gov, SPECIAL.get((tag, gov), form % PLACE[tag])))
wr("localisation/00_warlord_era_names.csv", "\n".join(lines) + "\n")
print("clique flags: %d designs x 5 government variants | government names: %d" % (len(FLAGS), len(lines)))

sheet = Image.new("RGB", (7 * 100, 5 * 72 * 1 + 5 * 72), (40, 40, 40))
for i, tag in enumerate(FLAGS):
    sheet.paste(FLAGS[tag](), ((i % 7) * 100 + 3, (i // 7) * 72 + 4))
b0 = FLAGS["FUJ"]()
for i, im in enumerate((b0, republic(b0), monarchy(b0), communist(b0), fascist(b0))):
    sheet.paste(im, (i * 100 + 3, 5 * 72 + 40))
os.makedirs(WORK, exist_ok=True)
sheet.save(os.path.join(WORK, "flags_sheet.png"))
