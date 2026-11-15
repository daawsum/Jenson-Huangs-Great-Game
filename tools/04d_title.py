"""Stage 4d: the title (main menu) picture.

The main menu draws gfx/interface/frontend_main_bg.dds centred at its own pixel size
(1876 x 652, uncompressed 32-bit; not scaled to the screen). The menu buttons sit over the
bottom-centre of it. A 16:9 source cannot fill that 2.9:1 strip without losing its top and
bottom, so the whole picture is shown at full height in the middle and the sides are filled
with a blurred, darkened copy that fades to black at the edges, like vanilla's vignette.
Source: the first picture in tools/assets/title.
"""
import os, glob, struct
from PIL import Image, ImageFilter, ImageDraw
from config import *

REF = os.path.join(V, "gfx", "interface", "frontend_main_bg.dds")
src = sorted(glob.glob(os.path.join(HERE, "assets", "title", "*.jpg")) + glob.glob(os.path.join(HERE, "assets", "title", "*.png")))
if not src:
    raise SystemExit("no picture in tools/assets/title")
header = open(REF, "rb").read(128)
H, W = struct.unpack("<2I", header[12:20])
assert header[:4] == b"DDS " and os.path.getsize(REF) == 128 + W * H * 4, "unexpected vanilla title image format"

pic = Image.open(src[0]).convert("RGB")
# backdrop: the picture scaled to cover the strip, blurred and darkened
bw = W
bh = round(bw * pic.height / pic.width)
back = pic.resize((bw, bh), Image.LANCZOS).crop((0, (bh - H) // 2, W, (bh - H) // 2 + H))
back = back.filter(ImageFilter.GaussianBlur(22)).point(lambda v: int(v * 0.38))
# the whole picture at full height, with feathered left and right edges
fw = round(H * pic.width / pic.height)
front = pic.resize((fw, H), Image.LANCZOS)
mask = Image.new("L", (fw, H), 255)
d = ImageDraw.Draw(mask)
feather = 70
for i in range(feather):
    a = int(255 * i / feather)
    d.line([(i, 0), (i, H)], fill=a)
    d.line([(fw - 1 - i, 0), (fw - 1 - i, H)], fill=a)
back.paste(front, ((W - fw) // 2, 0), mask)
# fade the outer edges of the strip to black
shade = Image.new("L", (W, H), 255)
d = ImageDraw.Draw(shade)
edge = 220
for i in range(edge):
    a = int(255 * (i / edge) ** 1.5)
    d.line([(i, 0), (i, H)], fill=a)
    d.line([(W - 1 - i, 0), (W - 1 - i, H)], fill=a)
out = Image.composite(back, Image.new("RGB", (W, H), (0, 0, 0)), shade).convert("RGBA")
r, g, b, a = out.split()
dst = os.path.join(OUT, "gfx", "interface", "frontend_main_bg.dds")
os.makedirs(os.path.dirname(dst), exist_ok=True)
open(dst, "wb").write(header + Image.merge("RGBA", (b, g, r, a)).tobytes())
out.convert("RGB").resize((W // 2, H // 2)).save(os.path.join(WORK, "title_preview.png"))
print("title picture: %s -> frontend_main_bg.dds (%dx%d)" % (os.path.basename(src[0]), W, H))
