"""Stage 4b: import a map look from mods installed on this machine.

Belle Cartographie Dark (the GFM submod by Jman) is a graphics-only reskin: terrain textures,
colour maps, borders, shore and water art, and two shaders. It is designed to sit on top of
GFM's terrain folder, so GFM's files are copied first and the submod's over them.
Nothing here touches provinces, so it is safe for any province layout.
"""
import os, shutil
from config import *

MODS = os.path.join(V, "mod")
LAYERS = [
    (os.path.join(MODS, "GFM", "map", "terrain"), os.path.join(OUT, "map", "terrain")),
    (os.path.join(MODS, "GFM Belle Dark", "map", "terrain"), os.path.join(OUT, "map", "terrain")),
    (os.path.join(MODS, "GFM Belle Dark", "gfx", "FX"), os.path.join(OUT, "gfx", "FX")),
]
n = size = 0
for src, dst in LAYERS:
    if not os.path.isdir(src):
        raise SystemExit("map style source missing: " + src)
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        p = os.path.join(src, f)
        if os.path.isfile(p) and " - Copy" not in f:
            shutil.copyfile(p, os.path.join(dst, f))
            n += 1
            size += os.path.getsize(p)
print("map style: copied %d files, %.0f MB (GFM terrain + Belle Cartographie Dark)" % (n, size / 1e6))
