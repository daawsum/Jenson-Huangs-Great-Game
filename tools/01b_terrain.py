"""Stage 1b: work out the land terrain of every split province from terrain.bmp.

Victoria 2 does not reliably derive terrain for provinces added by a mod (they come out as
ocean and render as water), so each one gets an explicit `terrain = x` line in its history.
"""
import os, re, json, collections
import numpy as np
from PIL import Image
from config import *

Image.MAX_IMAGE_PIXELS = None
M = json.load(open(os.path.join(WORK, "map.json")))
split = {int(k): [c[0] for c in v] for k, v in M["split"].items()}
want = set(split) | {c for v in split.values() for c in v}

tt = re.sub(r"#.*", "", rd("map", "terrain.txt"))
idx2type = {}
for m in re.finditer(r"text_\d+\s*=\s*\{\s*type\s*=\s*(\w+)\s*color\s*=\s*\{\s*(\d+)\s*\}", tt):
    idx2type[int(m.group(2))] = m.group(1)
water = set(re.findall(r"(\w+)\s*=\s*\{[^{}]*is_water\s*=\s*yes", tt))
print("terrain palette entries:", len(idx2type), "water types:", water)

ter = np.array(Image.open(os.path.join(V, "map", "terrain.bmp")))          # palette indices
img = np.array(Image.open(os.path.join(OUT, "map", "provinces.bmp")).convert("RGB")).astype(np.int32)
assert ter.shape == img.shape[:2]
code = (img[:, :, 0] << 16) | (img[:, :, 1] << 8) | img[:, :, 2]
col = {}
for l in open(os.path.join(OUT, "map", "definition.csv"), encoding=ENC).read().splitlines()[1:]:
    p = l.split(";")
    if p[0].strip() and int(p[0]) in want:
        col[(int(float(p[1])) << 16) | (int(float(p[2])) << 8) | int(float(p[3]))] = int(p[0])

out, tally = {}, collections.Counter()
for c, pid in col.items():
    idx = ter[code == c]
    votes = collections.Counter()
    for i, n in zip(*np.unique(idx, return_counts=True)):
        t = idx2type.get(int(i))
        if t and t not in water:
            votes[t] += int(n)
    out[pid] = votes.most_common(1)[0][0] if votes else "plains"
    tally[out[pid]] += 1
assert len(out) == len(want)
json.dump(out, open(os.path.join(WORK, "terrain.json"), "w"))
print("terrain assigned to", len(out), "provinces:", dict(tally))
