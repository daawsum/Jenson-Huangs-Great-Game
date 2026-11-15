"""Stage 1: cut Chinese provinces in provinces.bmp and rewrite the map text files."""
import os, re, json, math, random, glob
import numpy as np
from PIL import Image
from scipy import ndimage
from config import *

Image.MAX_IMAGE_PIXELS = None
random.seed(1911)
os.makedirs(WORK, exist_ok=True)

# ---------- definitions ----------
deflines = rd("map", "definition.csv").splitlines()
id2rgb, used = {}, set()
for l in deflines[1:]:
    p = l.split(";")
    if len(p) < 4 or not p[1].strip():
        continue
    rgb = tuple(int(float(x)) for x in p[1:4])
    used.add(rgb)
    if p[0].strip():
        id2rgb[int(p[0])] = rgb
MAXID = max(id2rgb)

# ---------- bitmap ----------
img = np.array(Image.open(os.path.join(V, "map", "provinces.bmp")).convert("RGB"))
H, W, _ = img.shape
code = (img[:, :, 0].astype(np.int32) << 16) | (img[:, :, 1].astype(np.int32) << 8) | img[:, :, 2]
uniq, inv = np.unique(code, return_inverse=True)
c2id = {(r << 16) | (g << 8) | b: i for i, (r, g, b) in id2rgb.items()}
lut = np.array([c2id.get(int(c), 0) for c in uniq], dtype=np.int32)
pid = lut[inv].reshape(H, W)
print("map", W, H, "provinces in bmp", len(set(lut.tolist())) - 1)

m = re.search(r"sea_starts\s*=\s*\{([^}]*)\}", rd("map", "default.map"))
sea = {int(x) for x in m.group(1).split()}

# province names + vanilla history folder
pname, pfolder = {}, {}
for f in glob.glob(os.path.join(V, "history", "provinces", "*", "*.txt")):
    mm = re.match(r"\s*(\d+)\s*-?\s*(.*)\.txt", os.path.basename(f))
    if mm:
        pname[int(mm.group(1))] = mm.group(2).strip()
        pfolder[int(mm.group(1))] = os.path.basename(os.path.dirname(f))

# positions (vic2 y is measured from the bottom of the map)
postext = rd("map", "positions.txt")
posblocks = {}
for k, body, s, e in blocks(postext):
    if k.isdigit():
        posblocks[int(k)] = body


def unitpos(p):
    b = posblocks.get(p, "")
    for key in ("city", "unit", "text_position"):
        mm = re.search(key + r"\s*=\s*\{\s*x\s*=\s*([\d\.]+)\s*y\s*=\s*([\d\.]+)", b)
        if mm:
            return float(mm.group(1)), float(mm.group(2))
    return None


# sanity: Beijing's unit marker must fall inside Beijing
ux, uy = unitpos(1612)
print("position check, Beijing marker lies in province", pid[int(uy), int(ux)])

owner_of = tag_of_vanilla_province()
objs = ndimage.find_objects(pid, max_label=MAXID + 400)

# ---------- choose what to split ----------
targets = []
for p, tag in owner_of.items():
    if tag == "MGL" or tag in NO_SPLIT_TAGS or p in NO_SPLIT:
        continue
    sl = objs[p - 1]
    area = int((pid[sl] == p).sum())
    if area < 260:
        continue
    targets.append((p, area))
areas = sorted(a for _, a in targets)
cut3 = areas[int(len(areas) * 0.80)]  # biggest fifth are cut in three
print("split targets", len(targets), "three-way above", cut3, "px")


def newcolor():
    while True:
        c = (random.randint(1, 254), random.randint(1, 254), random.randint(1, 254))
        if c not in used:
            used.add(c)
            return c


names_used = {v.lower() for v in pname.values()}
split, frac_parent, newdefs = {}, {}, []
next_id = MAXID + 1
for p, area in sorted(targets):
    sl = objs[p - 1]
    y0, x0 = sl[0].start, sl[1].start
    mask = pid[sl] == p
    ys, xs = np.nonzero(mask)
    pts = np.stack([xs, ys], 1).astype(float)
    c = pts.mean(0)
    u, s, vt = np.linalg.svd(pts - c, full_matrices=False)
    t = (pts - c) @ vt[0]
    w = (pts - c) @ vt[1]
    rng = t.max() - t.min()
    wl = max(18.0, (w.max() - w.min()) / 1.6)
    t2 = (t + 0.07 * rng * np.sin(2 * math.pi * w / wl + random.random() * 6.28)
          + 0.03 * rng * np.sin(2 * math.pi * w / (wl / 2.7) + random.random() * 6.28))
    if area < 700 or (w.max() - w.min()) < 16:
        t2 = t
    n = 3 if area >= cut3 else 2
    qs = np.quantile(t2, [i / n for i in range(1, n)])
    part = np.searchsorted(qs, t2)
    keep = 0
    up = unitpos(p)
    if up:
        ux, uy = int(round(up[0])) - x0, int(round(up[1])) - y0
        keep = int(part[((xs - ux) ** 2 + (ys - uy) ** 2).argmin()])
    kids, k = [], 0
    for q in range(n):
        if q == keep:
            continue
        sel = part == q
        cid = next_id
        next_id += 1
        col = newcolor()
        img[y0 + ys[sel], x0 + xs[sel]] = col
        pid[y0 + ys[sel], x0 + xs[sel]] = cid
        cand = SPLIT_NAMES.get(pname[p], [])
        nm = None
        if k < len(cand) and cand[k].lower() not in names_used:
            nm = cand[k]
        if nm is None:
            cc = pts[sel].mean(0) - pts[part == keep].mean(0)
            d8 = ("East" if cc[0] > 0 else "West") if abs(cc[0]) > abs(cc[1]) else ("North" if cc[1] > 0 else "South")
            nm = d8 + " " + pname[p]
            if nm.lower() in names_used:
                nm = "Outer " + pname[p]
        names_used.add(nm.lower())
        pname[cid] = nm
        pfolder[cid] = pfolder[p]
        kids.append((cid, nm, float(sel.sum()) / area))
        newdefs.append((cid, col, nm))
        k += 1
    split[p] = kids
    frac_parent[p] = float((part == keep).sum()) / area
NEWMAX = next_id - 1
print("new provinces", len(newdefs), "ids", MAXID + 1, "-", NEWMAX)

os.makedirs(os.path.join(OUT, "map"), exist_ok=True)
Image.fromarray(img, "RGB").save(os.path.join(OUT, "map", "provinces.bmp"))

# ---------- geometry for every province ----------
objs = ndimage.find_objects(pid, max_label=NEWMAX)
idx = np.arange(1, NEWMAX + 1)
com = ndimage.center_of_mass(np.ones_like(pid, dtype=np.uint8), pid, idx)
centroid = {int(i): (float(c[1]), float(c[0])) for i, c in zip(idx, com) if not math.isnan(c[0])}

adj = {}


def addpairs(a, b):
    mk = a != b
    pr = np.unique(np.stack([a[mk], b[mk]], 1), axis=0)
    for x, y in pr.tolist():
        if x and y:
            adj.setdefault(x, set()).add(y)
            adj.setdefault(y, set()).add(x)


addpairs(pid[:, :-1], pid[:, 1:])
addpairs(pid[:-1, :], pid[1:, :])
coastal = {p: sorted(n for n in ns if n in sea) for p, ns in adj.items() if p not in sea}
coastal = {p: v for p, v in coastal.items() if v}
sea_list = np.array(sorted(sea))
# open sea = the largest connected group of sea provinces; the rest are lakes
_seen, ocean = set(), set()
for s0 in sea:
    if s0 in _seen:
        continue
    comp, stack = {s0}, [s0]
    while stack:
        q = stack.pop()
        for r in adj.get(q, ()):
            if r in sea and r not in comp:
                comp.add(r)
                stack.append(r)
    _seen |= comp
    if len(comp) > len(ocean):
        ocean = comp
ocean_list = np.array(sorted(ocean))
PORT_ZONE = {}


# ---------- positions for split provinces ----------
def interior_point(p):
    sl = objs[p - 1]
    mask = np.pad(pid[sl] == p, 1)
    dt = ndimage.distance_transform_edt(mask)
    y, x = np.unravel_index(dt.argmax(), dt.shape)
    return sl[1].start + x - 1, sl[0].start + y - 1, float(dt.max())


def coast_point(p):
    """Port marker for province p. Vanilla puts the naval_base marker IN the sea province the port
    opens onto (1029 of its 1038 markers); the engine reads the port's sea zone from that spot.
    A marker left on land makes any fleet that starts there crash the game."""
    sl = objs[p - 1]
    y0, x0 = max(sl[0].start - 3, 0), max(sl[1].start - 3, 0)
    sub = pid[y0:sl[0].stop + 3, x0:sl[1].stop + 3]
    mine = sub == p
    for pool in (ocean_list, sea_list):               # prefer the open sea over a lake
        water = np.isin(sub, pool)
        touch = ndimage.binary_dilation(mine, iterations=1) & water
        ys, xs = np.nonzero(touch)
        if len(ys):
            break
    else:
        return None
    # take the sea zone this province shares the longest coast with, then a pixel in the middle of that coast
    zones, counts = np.unique(sub[ys, xs], return_counts=True)
    zone = zones[counts.argmax()]
    k = np.nonzero(sub[ys, xs] == zone)[0]
    i = k[len(k) // 2]
    my, mx = np.nonzero(mine)
    j = ((my - ys[i]) ** 2 + (mx - xs[i]) ** 2).argmin()
    ang = math.atan2(ys[i] - my[j], xs[i] - mx[j])
    assert pid[y0 + ys[i], x0 + xs[i]] == zone
    return x0 + xs[i], y0 + ys[i], ang, int(zone)


def posblock(p):
    x, y, r = interior_point(p)
    Y = y
    off = max(1.0, min(4.0, r / 3))

    def pt(dx, dy):
        return "\t{\n\t\tx=%.6f\n\t\ty=%.6f\n\t}\n" % (x + dx * off, Y + dy * off)

    s = "%d = \n{\n" % p
    s += "\tunit=\n" + pt(0, 0)
    s += "\ttext_position=\n" + pt(0, 0)
    s += "\ttext_scale=%.3f\n" % max(1.2, min(4.0, r / 4))
    s += "\tcity=\n" + pt(-1, 1)
    s += "\ttown=\n" + pt(1, -1)
    s += "\tbuilding_construction=\n" + pt(1, 1)
    s += "\tmilitary_construction=\n" + pt(-1, -1)
    s += "\tfactory=\n" + pt(0, 1)
    bp = "\t\tfort=\n\t\t{\n\t\t\tx=%.6f\n\t\t\ty=%.6f\n\t\t}\n" % (x + off, Y)
    bp += "\t\trailroad=\n\t\t{\n\t\t\tx=%.6f\n\t\t\ty=%.6f\n\t\t}\n" % (x - off, Y)
    cp = coast_point(p)
    rot = ""
    if cp:
        bp += "\t\tnaval_base=\n\t\t{\n\t\t\tx=%.6f\n\t\t\ty=%.6f\n\t\t}\n" % (cp[0], cp[1])
        rot = "\tbuilding_rotation=\n\t{\n\t\tnaval_base=%.6f\n\t}\n" % cp[2]
        PORT_ZONE[p] = cp[3]
    s += "\tbuilding_position=\n\t{\n" + bp + "\t}\n" + rot + "}\n"
    return s


redo = set(split) | {c for ks in split.values() for c, _, _ in ks}
chunks, last = [], 0
for k, body, s, e in blocks(postext):
    if k.isdigit() and int(k) in redo:
        chunks.append(postext[last:s])
        last = e
chunks.append(postext[last:])
out = "".join(chunks).rstrip() + "\n"
for p in sorted(redo):
    out += posblock(p)
wr("map/positions.txt", out)

# ---------- definition.csv / default.map ----------
body = [deflines[0]] + [l for l in deflines[1:] if l.split(";")[0].strip()]
tail = [l for l in deflines[1:] if not l.split(";")[0].strip()]
for cid, col, nm in newdefs:
    body.append("%d;%d;%d;%d;%s;x" % (cid, col[0], col[1], col[2], nm))
wr("map/definition.csv", "\n".join(body + tail) + "\n")
dm = rd("map", "default.map")
dm = re.sub(r"max_provinces\s*=\s*\d+", "max_provinces = %d" % (NEWMAX + 1), dm)
# Victoria 2 reads definition.csv from the BASE game unless this path points into the mod folder.
# Without it every new province colour is unknown to the engine and is drawn as water.
dm = re.sub(r'definitions\s*=\s*"[^"]*"', 'definitions = "../mod/%s/map/definition.csv"' % MOD_DIR, dm)
assert "../mod/" in dm
wr("map/default.map", dm)


# ---------- climate ----------
def add_children(text):
    """Append each child id to every `{ ... }` id list that contains its parent."""
    def fix(mm):
        ids = mm.group(0)
        nums = set(re.findall(r"\b\d+\b", ids))
        extra = [str(c) for p, ks in split.items() if str(p) in nums for c, _, _ in ks]
        if not extra:
            return ids
        return ids[:-1] + " " + " ".join(extra) + "\n}"
    return re.sub(r"\{[\d\s]+\}", fix, text)


wr("map/climate.txt", add_children(rd("map", "climate.txt")))

json.dump({
    "H": H, "W": W, "MAXID": MAXID, "NEWMAX": NEWMAX,
    "split": {str(p): ks for p, ks in split.items()},
    "frac_parent": {str(p): f for p, f in frac_parent.items()},
    "pname": {str(k): v for k, v in pname.items()},
    "pfolder": {str(k): v for k, v in pfolder.items()},
    "centroid": {str(k): v for k, v in centroid.items()},
    "adj": {str(k): sorted(v) for k, v in adj.items()},
    "coastal": {str(k): v for k, v in coastal.items()},
    "sea": sorted(sea),
    "port_zone": {str(k): v for k, v in PORT_ZONE.items()}, "ocean": sorted(ocean),
}, open(os.path.join(WORK, "map.json"), "w"))
print("done")
