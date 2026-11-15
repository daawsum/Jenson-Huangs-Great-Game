"""Research 2: the dependencies of RobloxDoD 1.8's technologies and inventions."""
import os, re, glob, collections
from config import *

R = os.path.join(V, "mod", "RobloxDOD 1.8")
strip = lambda t: re.sub(r"#.*", "", t)
rdR = lambda *p: strip(open(os.path.join(R, *p), encoding=ENC, errors="replace").read())
goods_v = set(re.findall(r"^\t(\w+)\s*=\s*\{", strip(rd("common", "goods.txt")), re.M))
goods_r = set(re.findall(r"^\t(\w+)\s*=\s*\{", rdR("common", "goods.txt"), re.M))
print("goods only in roblox:", sorted(goods_r - goods_v), "| only vanilla:", sorted(goods_v - goods_r))
text = ""
for d in ("technologies", "inventions"):
    for f in glob.glob(os.path.join(R, d, "*.txt")):
        text += strip(open(f, encoding=ENC, errors="replace").read()) + "\n"
# goods named inside goods-modifier blocks
gm = set()
for m in re.finditer(r"(rgo_goods_output|rgo_goods_throughput|factory_goods_output|factory_goods_input|factory_goods_throughput|rgo_size)\s*=\s*\{([^}]*)\}", text):
    gm |= set(re.findall(r"(\w+)\s*=", m.group(2)))
print("goods referenced by tech/inventions that vanilla lacks:", sorted(gm - goods_v))
print("religions tested:", collections.Counter(re.findall(r"pop_majority_religion\s*=\s*(\w+)|(?<!_)religion\s*=\s*(\w+)", text)).most_common(5))
print("flags tested:", collections.Counter(re.findall(r"has_country_flag\s*=\s*(\w+)", text)).most_common(12))
print("tags tested:", collections.Counter(re.findall(r"\btag\s*=\s*(\w+)", text)).most_common(12))
print("governments/ideologies etc:", collections.Counter(re.findall(r"(government|ruling_party_ideology|nationalvalue|has_country_modifier|culture|primary_culture|is_culture_group|continent)\s*=\s*(\w+)", text)).most_common(25))
tr = rdR("common", "technology.txt")
tv = strip(rd("common", "technology.txt"))
print("schools roblox:", re.findall(r"\n\t(\w+)\s*=\s*\{?\s*\n?\s*army_tech_research_bonus", tr)[:12])
print("schools vanilla:", re.findall(r"\n\t(\w+)\s*=\s*\{?\s*\n?\s*army_tech_research_bonus", tv)[:12])
for u in ("infantry_offensive", "artillery_defensive", "infantry"):
    print("== unit", u, "\n", rdR("units", u + ".txt").strip()[:520].replace("\n", " | "))
b = rdR("common", "buildings.txt")
i = b.find("synthetic_rubber_factory")
print("== building:", b[i:i + 420].replace("\n", " | "))
p = rdR("common", "production_types.txt")
i = p.find("synthetic_rubber_factory")
print("== production:", p[i:i + 300].replace("\n", " | "))
print("roblox ships interface gfx:", sorted(os.listdir(os.path.join(R, "interface")))[:40] if os.path.isdir(os.path.join(R, "interface")) else None)
print("unit icon strips in roblox gfx/interface:", [f for f in os.listdir(os.path.join(R, "gfx", "interface")) if "unit" in f.lower()][:20] if os.path.isdir(os.path.join(R, "gfx", "interface")) else None)
