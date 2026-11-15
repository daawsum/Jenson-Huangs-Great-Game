#!/usr/bin/env python3
"""Summarise a Victoria 2 save game (plain text) to confirm that scripted effects really happened.

usage: read_save.py "<path to save.v2>" [TAG ...] [--cores TAG,TAG] [--province ID,ID]

Prints the date, global flags, counts of countries / pops / cultures / religions, diplomatic
relations, and for each TAG given: money, national bank, civilized, prestige, modifiers, flags.
--cores counts provinces carrying a core of each listed tag (e.g. state-size marker tags).
--province prints owner, controller, cores and goods of the listed provinces.

Tip: set autosave="MONTHLY" in <user_dir>/settings.txt, run a few months, then read
<user_dir>/save games/autosave.v2.
"""
import re, sys, collections


def block_at(t, start):
    d, j = 1, start
    while d and j < len(t):
        c = t[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
        j += 1
    return t[start:j]


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    opts = {}
    args = []
    it = iter(sys.argv[1:])
    for a in it:
        if a in ("--cores", "--province"):
            opts[a] = next(it).split(",")
        else:
            args.append(a)
    t = open(args[0], encoding="cp1252", errors="replace").read()
    tags = args[1:]
    print("save: %.1f MB | date %s | player %s" % (len(t) / 1e6, (re.search(r'date="([^"]+)"', t) or [0, "?"])[1], (re.search(r'player="(\w+)"', t) or [0, "?"])[1]))
    gf = re.search(r"\nflags=\s*\{([^}]*)\}", t)
    print("global flags:", re.findall(r"(\w+)=yes", gf.group(1)) if gf else [])
    countries = re.findall(r"\n([A-Z][A-Z0-9]{2})=\n\{\n\ttax_base", t) or re.findall(r"\n([A-Z][A-Z0-9]{2})=\n\{", t)
    print("country blocks:", len(set(countries)))
    pops = re.findall(r"\n\t\t(\w+)=(\w+)\n\t\tmoney=", t)          # culture=religion line inside each pop
    print("pops: %d | cultures: %d | religions: %s" % (len(pops), len({c for c, r in pops}), dict(collections.Counter(r for c, r in pops).most_common(6))))
    print("diplomacy: vassal blocks %d | alliance blocks %d | substate mentions %d | active wars %d" % (
        len(re.findall(r"\bvassal=\s*\{", t)), len(re.findall(r"\balliance=\s*\{", t)), len(re.findall(r"substate", t)), len(re.findall(r"\nactive_war=", t))))
    for tag in tags:
        m = re.search(r"\n%s=\n\{" % re.escape(tag), t)
        if not m:
            print("%s: no country block (does not exist)" % tag)
            continue
        b = block_at(t, m.end())
        g = lambda k: (re.search(r"\n\t%s=([^\n]+)" % k, b) or [0, "?"])[1]
        fl = re.search(r"\n\tflags=\s*\{([^}]*)\}", b)
        bank = re.search(r"\n\tbank=\s*\{[^}]*?money=([\d\.\-]+)", b)
        print("%s | money %s | bank %s | civilized %s | prestige %s | capital %s" % (tag, g("money"), bank.group(1) if bank else "?", g("civilized"), g("prestige"), g("capital")))
        print("    modifiers:", sorted(set(re.findall(r'modifier="(\w+)"', b))))
        print("    flags:", re.findall(r"(\w+)=yes", fl.group(1)) if fl else [])
        print("    reforms on:", re.findall(r"\n\t(\w+)=yes_\w+", b))
    if "--cores" in opts:
        cores = collections.Counter(re.findall(r'\n\tcore="(\w+)"', t))
        print("provinces with a core of:", {k: cores.get(k, 0) for k in opts["--cores"]})
    for pid in opts.get("--province", []):
        m = re.search(r"\n%s=\n\{" % pid, t)
        if not m:
            print("province %s: not found" % pid)
            continue
        b = block_at(t, m.end())
        print("province %s | name %s | owner %s | controller %s | cores %s | goods %s | life rating %s" % (
            pid, (re.search(r'name="([^"]*)"', b) or [0, "?"])[1], (re.search(r'owner="(\w+)"', b) or [0, None])[1],
            (re.search(r'controller="(\w+)"', b) or [0, None])[1], re.findall(r'core="(\w+)"', b),
            (re.search(r'goods_type="?(\w+)', b) or [0, "?"])[1], (re.search(r"life_rating=(\d+)", b) or [0, "?"])[1]))


if __name__ == "__main__":
    main()
