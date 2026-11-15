"""Make contact sheets of the fetched candidates so one can be picked per category."""
import os, json, sys
from PIL import Image, ImageDraw

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "pictures", "candidates")
rec = json.load(open(os.path.join(SRC, "candidates.json"), encoding="utf-8"))
keys = sorted(rec)
per, cols, cw, ch = 40, 8, 190, 150
for n in range(0, len(keys), per):
    part = keys[n:n + per]
    rows = (len(part) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rows * ch), (25, 25, 25))
    d = ImageDraw.Draw(sheet)
    for i, k in enumerate(part):
        try:
            im = Image.open(os.path.join(SRC, k + ".jpg")).convert("RGB")
        except Exception:
            continue
        im.thumbnail((cw - 6, ch - 22))
        x, y = (i % cols) * cw, (i // cols) * ch
        sheet.paste(im, (x + 3, y + 18))
        d.text((x + 4, y + 3), k, fill=(255, 230, 120))
    out = os.path.join(os.path.dirname(SRC), "sheet_%d.png" % (n // per + 1))
    sheet.save(out)
    print(out, len(part))
