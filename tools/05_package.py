"""Stage 5: make provinces.bmp byte-compatible with vanilla's header, write the readme, zip the mod."""
import os, zipfile
import numpy as np
from PIL import Image
from config import *

Image.MAX_IMAGE_PIXELS = None
vb = open(os.path.join(V, "map", "provinces.bmp"), "rb").read()
nbp = os.path.join(OUT, "map", "provinces.bmp")
img = np.array(Image.open(nbp).convert("RGB"))
off = int.from_bytes(vb[10:14], "little")
data = img[::-1, :, ::-1].tobytes()           # BMP rows run bottom-up, pixels are BGR
assert len(data) == img.shape[0] * img.shape[1] * 3 and img.shape[1] * 3 % 4 == 0
out = vb[:off] + data + vb[off + len(data):]
assert len(out) == len(vb)
open(nbp, "wb").write(out)
chk = np.array(Image.open(nbp).convert("RGB"))
assert (chk == img).all()
print("provinces.bmp rewritten with vanilla header,", len(out), "bytes")

readme = """JENSON HUANG'S GREAT GAME - a Victoria 2 (3.04, Heart of Darkness) multiplayer mod

An alternate history: China westernised and then shattered into warlord cliques, while Europe
and the rest of the old world were left behind and broke apart.

INSTALL
  Copy the folder "Warlord Era" and the file "Warlord Era.mod" into
  <Victoria 2>/mod/ and tick "Jenson Huang's Great Game" in the launcher.
  Every player must use this exact copy or the checksums will differ.

PLAYER SLOTS
  20 major cliques: Zhili, Fengtian, Anhui, Shanxi, Guominjun, Shandong, Henan, Jiangsu,
  Zhejiang, Fujian, Guangdong, Guangxi, Hunan, Hubei, Jiangxi, Sichuan, Yunnan, Guizhou,
  Ma, Xinjiang.
  3 playable outsiders (not civilized, heavily buffed): Sikh Empire, Mongolia, Persia.
  15 minor cliques are selectable but small.

WHAT IS DIFFERENT
  - Only the 35 Chinese cliques are civilized. They differ: republics, regencies, leagues,
    garrison commands and free cities, each major with its own permanent strength.
  - 137 new Chinese provinces (IDs 3249-3385), 92 Chinese states.
  - Cultures: China has five (Northern Han, Yangtze Han, Cantonese, Hokkien, Manchu) plus the
    frontier peoples, and a clique accepts only its own. Europe, Africa and the New World have
    one culture per culture group. There is a single religion. Identical pops are merged.
  - The old world is uncivilized, barely literate and broken up, with about 20 successor
    states named after their chief cities. Micro-states were absorbed by their neighbours.
  - The Americas, Oceania, sub-Saharan Africa, Siberia, the steppe and the outer
    East Indies are empty and colonizable from day one.
  - Any clique can always declare "Warlord Claim" (take a state; the cost depends on the
    state's size flag).
  - Emigrants go to South East Asia until the first overseas dominion is chartered.
  - Decisions: "Charter the Dominion of ..." turns your colonies in a region into a
    puppet; "Hand New Lands to ..." passes later conquests to it.
  - Formables: Republic of China, Beiyang Government, Liangguang, Shu, Wu, Chu, Dian,
    Northwest Federation, Manchuria, Mongol Empire, Khalsa Raj, Persian Empire, India,
    the Commonwealth, United Baltic Duchy, Czechoslovakia (plus vanilla's own).
  - World Bank: a neutral dummy country on the Falkland Islands whose bankers are the only
    pops that can mine gold. Its bank always has money to lend. It cannot be attacked.
  - State size flags: every province carries a Tiny/Small/Medium/Large/Huge State core,
    re-measured yearly.
  - National focuses: IGoR puir's tiered focuses. Tiers 2-6 unlock for civilized countries
    in 1845, 1855, 1865, 1880 and 1895.
  - Map look: Belle Cartographie Dark.

CREDITS
  Migration flag system adapted from the Vae Victis mod.
  World Bank, state sizing and national focuses adapted from IGoR puir.
  Map graphics: Belle Cartographie, via the "GFM Belle Cartographie Dark" submod by Jman,
  layered on Greater Flavor Mod's terrain files. These are their authors' work; ask them
  before redistributing this mod publicly.
"""
open(os.path.join(OUT, "readme.txt"), "w", encoding="utf-8").write(readme)

root = os.path.dirname(OUT)
zp = os.path.join(root, "Warlord Era.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    z.write(os.path.join(root, "Warlord Era.mod"), "Warlord Era.mod")
    n = 0
    for d, _, fs in os.walk(OUT):
        for f in fs:
            full = os.path.join(d, f)
            z.write(full, os.path.join("Warlord Era", os.path.relpath(full, OUT)))
            n += 1
print("zip:", zp, n, "files,", round(os.path.getsize(zp) / 1e6, 1), "MB")
