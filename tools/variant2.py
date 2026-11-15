"""More test variants for the INSTALLED copy (crash hunting only).
  vone:TAG[,TAG]        restore vanilla country history text for these tags
  civ:TAG[,TAG]         in my history for these tags, set civilized = yes
  sub:TAG:regex:repl    regex-substitute inside one tag's history file
  addline:TAG:text      append a line to one tag's history file
"""
import os, re, glob, sys, shutil

V = r"D:\SteamLibrary\steamapps\common\Victoria 2"
G = os.path.join(V, "mod", "Warlord Era")
ENC = "cp1252"


def hist(tag, root=G):
    r = glob.glob(os.path.join(root, "history", "countries", tag + "*.txt"))
    return r[0] if r else None


for v in sys.argv[1:]:
    kind, _, rest = v.partition(":")
    if kind == "vone":
        for t in rest.split(","):
            shutil.copyfile(hist(t, V), hist(t))
    elif kind == "civ":
        for t in rest.split(","):
            f = hist(t)
            s = open(f, encoding=ENC).read().replace("civilized = no", "civilized = yes")
            open(f, "w", encoding=ENC, newline="\r\n").write(s)
    elif kind == "sub":
        t, rx, repl = rest.split(":", 2)
        f = hist(t)
        s = re.sub(rx, repl, open(f, encoding=ENC).read(), flags=re.M)
        open(f, "w", encoding=ENC, newline="\r\n").write(s)
    elif kind == "addline":
        t, text = rest.split(":", 1)
        f = hist(t)
        open(f, "a", encoding=ENC, newline="\r\n").write(text + "\n")
    else:
        raise SystemExit("unknown " + v)
print("applied2", sys.argv[1:])
