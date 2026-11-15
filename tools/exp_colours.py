"""Experiment on the INSTALLED copy: give the first 56 new provinces vanilla's reserved colours."""
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
G = r"D:\SteamLibrary\steamapps\common\Victoria 2\mod\Warlord Era\map"
lines = open(G + r"\definition.csv", encoding="cp1252").read().splitlines()
tail = [l for l in lines[1:] if not l.split(";")[0].strip() and l.strip()]
body = [l for l in lines[1:] if l.split(";")[0].strip()]
b = open(G + r"\provinces.bmp", "rb").read()
off = int.from_bytes(b[10:14], "little")
W, H = int.from_bytes(b[18:22], "little"), int.from_bytes(b[22:26], "little")
px = np.frombuffer(b[off:off + W * H * 3], dtype=np.uint8).reshape(H, W, 3).copy()   # BGR
code = (px[:, :, 2].astype(np.int32) << 16) | (px[:, :, 1].astype(np.int32) << 8) | px[:, :, 0]
n = 0
for i, l in enumerate(body):
    p = l.split(";")
    if int(p[0]) < 3249 or n >= len(tail):
        continue
    t = tail[n].split(";")
    old = (int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])
    r, g, bl = int(t[1]), int(t[2]), int(t[3])
    m = code == old
    px[m] = (bl, g, r)
    body[i] = "%s;%d;%d;%d;%s;x" % (p[0], r, g, bl, p[4])
    n += 1
open(G + r"\provinces.bmp", "wb").write(b[:off] + px.tobytes() + b[off + W * H * 3:])
open(G + r"\definition.csv", "w", encoding="cp1252", newline="\r\n").write("\n".join([lines[0]] + body + tail[n:]) + "\n")
print("recoloured", n, "new provinces with reserved colours; ids 3249 -", 3248 + n)
