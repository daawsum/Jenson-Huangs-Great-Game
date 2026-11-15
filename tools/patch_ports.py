"""One-off: put naval_base markers in the adjacent sea, as vanilla does."""
s = open("01_map.py", encoding="utf-8").read()
start = s.index("def coast_point(p):")
end = s.index("def posblock(p):")
new = '''def coast_point(p):
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


'''
s = s[:start] + new + s[end:]
a = "sea_list = np.array(sorted(sea))\n"
assert a in s
s = s.replace(a, a + '''# open sea = the largest connected group of sea provinces; the rest are lakes
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
''')
a = '''        rot = "\\tbuilding_rotation=\\n\\t{\\n\\t\\tnaval_base=%.6f\\n\\t}\\n" % cp[2]\n'''
assert a in s, "rot line"
s = s.replace(a, a + "        PORT_ZONE[p] = cp[3]\n")
a = '''    "sea": sorted(sea),\n'''
assert a in s
s = s.replace(a, a + '''    "port_zone": {str(k): v for k, v in PORT_ZONE.items()}, "ocean": sorted(ocean),\n''')
open("01_map.py", "w", encoding="utf-8").write(s)
print("patched")
