"""Stage 4c: loading screens.

Vanilla has exactly seven (gfx/loadingscreens/load_1.dds .. load_7.dds). The mod replaces each
one by name. Sources are the pictures in tools/assets/loading; with fewer than seven pictures,
some are used twice so that no vanilla screen is left over.

How the game shows them (measured from a screenshot): the 1024x1024 texture is treated as a
4:3 picture, scaled to the screen's WIDTH and cropped top and bottom. So a 16:9 picture is
placed in the middle of a 4:3 canvas; on a 16:9 screen exactly the picture is visible, with no
stretching. Wider screens crop a little off the top and bottom of the picture.
Format follows Vae Victis's loading screens: uncompressed 32-bit, 1024x1024, no mipmaps.
"""
import os, glob
from PIL import Image, ImageFilter
from config import *

SRC = os.path.join(HERE, "assets", "loading")
REF = os.path.join(V, "mod", "Vae Victis 0.4.1", "gfx", "loadingscreens", "load_1.dds")
vanilla = sorted(glob.glob(os.path.join(V, "gfx", "loadingscreens", "load_*.dds")))
pics = sorted(glob.glob(os.path.join(SRC, "*.jpg")) + glob.glob(os.path.join(SRC, "*.png")))
if not pics:
    raise SystemExit("no pictures in " + SRC)
header = open(REF, "rb").read(128)
assert header[:4] == b"DDS " and os.path.getsize(REF) == 128 + 1024 * 1024 * 4

# which picture fills which slot; repeats chosen by hand when there are five pictures
ORDER = [0, 1, 2, 3, 4, 3, 0] if len(pics) == 5 else [i % len(pics) for i in range(len(vanilla))]
if len(pics) > len(vanilla):
    print("NOTE: %d pictures but only %d loading screens; the last %d are not used" % (len(pics), len(vanilla), len(pics) - len(vanilla)))
if len(pics) < len(vanilla):
    print("NOTE: %d pictures for %d loading screens; %d are used twice" % (len(pics), len(vanilla), len(vanilla) - len(pics)))
CW, CH = 1600, 1200                                   # the 4:3 canvas the game expects
for slot, f in enumerate(vanilla):
    src = pics[ORDER[slot]]
    pic = Image.open(src).convert("RGB")
    # 86% of the canvas width: a 16:9 screen shows the whole picture with a thin blurred margin, and an
    # ultrawide (21:9) screen, which shows only the middle 56% of the canvas height, loses very little
    w = round(CW * 0.86)
    h = round(w * pic.height / pic.width)
    canvas = pic.resize((CW, CH), Image.LANCZOS).filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.45))
    canvas.paste(pic.resize((w, h), Image.LANCZOS), ((CW - w) // 2, (CH - h) // 2))
    im = canvas.resize((1024, 1024), Image.LANCZOS).convert("RGBA")
    r, g, b, a = im.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()                           # DDS stores BGRA
    dst = os.path.join(OUT, "gfx", "loadingscreens", os.path.basename(f))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "wb").write(header + data)
    print("  %s <- %s" % (os.path.basename(f), os.path.basename(src)))
