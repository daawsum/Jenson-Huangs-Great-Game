"""One-off patch of 03a_tech.py: map goods icons, and a national value icon strip in this mod's own order."""
s = open("03a_tech.py", encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep(r'''(spriteType|corneredTileSpriteType|maskedShieldType|progressbartype)''', r'''(spriteType|corneredTileSpriteType|maskedShieldType|progressbartype|billboardType)''')
rep(r'''ours = {f.lower() for f in os.listdir(os.path.join(OUT, "gfx", "interface"))}''',
    r'''ours = {os.path.splitext(f.lower())[0] for f in os.listdir(os.path.join(OUT, "gfx", "interface"))}      # .tga and .dds are interchangeable''')
rep(r'''        if nm in vs and vs[nm][0] == tex and vs[nm][1] != fr and tex not in ours and os.path.splitext(tex)[0] + ".tga" not in ours:''',
    r'''        if nm in vs and vs[nm][0] == tex and vs[nm][1] != fr and os.path.splitext(tex)[0] not in ours:''')
rep(r'''ngoods = len(re.findall(''', r'''assert any("tradegoods" in x for x in fixed) and any("GFX_resources " in x + " " for x in fixed), fixed
ngoods = len(re.findall(''')
rep(r'''# ---- the synthetic rubber factory''', r'''# ---- national value icons: one strip, in the order of THIS mod's national values
# (vanilla's strip is order, liberty, equality; RobloxDoD's is order, equality, productivity, education,
#  diplomacy - used as it was, liberty and everything after it showed its neighbour's icon)
from PIL import Image
import struct


def read_strip(path):
    b = open(path, "rb").read()
    h_, w_ = struct.unpack("<II", b[12:20])
    assert b[84:88] == b"\x00\x00\x00\x00" and struct.unpack("<I", b[88:92])[0] == 32, "expected an uncompressed 32-bit strip: " + path
    return Image.frombytes("RGBA", (w_, h_), b[128:128 + w_ * h_ * 4], "raw", "BGRA"), b[:128]


v_im, v_hdr = read_strip(os.path.join(V, "gfx", "interface", "politics_nationalvalue.dds"))
r_im, r_hdr = read_strip(os.path.join(R, "gfx", "interface", "politics_nationalvalue.dds"))
fw = v_im.size[1]
frame = {}
for i, k in enumerate(re.findall(r"(?m)^(\w+)\s*=\s*\{", strip(nv_v))):
    frame[k] = v_im.crop((i * fw, 0, (i + 1) * fw, fw))
for i, k in enumerate(re.findall(r"(?m)^(\w+)\s*=\s*\{", strip(nv_r))):
    frame.setdefault(k, r_im.crop((i * fw, 0, (i + 1) * fw, fw)))
order = re.findall(r"(?m)^(\w+)\s*=\s*\{", strip(open(os.path.join(OUT, "common", "nationalvalues.txt"), encoding=ENC).read()))
assert all(k in frame for k in order), [k for k in order if k not in frame]
sheet = Image.new("RGBA", (fw * len(order), fw))
for i, k in enumerate(order):
    sheet.paste(frame[k], (i * fw, 0))
hdr = bytearray(v_hdr)
hdr[12:16] = struct.pack("<I", fw)
hdr[16:20] = struct.pack("<I", fw * len(order))
hdr[20:24] = struct.pack("<I", fw * len(order) * 4)          # pitch
open(os.path.join(OUT, "gfx", "interface", "politics_nationalvalue.dds"), "wb").write(bytes(hdr) + sheet.tobytes("raw", "BGRA"))
p_ = os.path.join(OUT, "interface", "country_politics.gfx")
t_ = open(p_, encoding=ENC, errors="replace").read()
t_, n_ = re.subn(r'(name\s*=\s*"GFX_politics_nationalvalue"\s*texturefile\s*=\s*"[^"]+"\s*noOfFrames\s*=\s*)\d+', lambda m_: m_.group(1) + str(len(order)), t_)
assert n_ == 1
open(p_, "w", encoding=ENC, newline="").write(t_)
print("national value icons:", order)

# ---- the synthetic rubber factory''')
open("03a_tech.py", "w", encoding="utf-8").write(s)
print("patched")
