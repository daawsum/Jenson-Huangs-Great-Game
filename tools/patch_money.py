"""One-off patch: Mongolia starts with 80 prestige; Heartbreaker's day-one money injection."""
s = open("02_world.py", encoding="utf-8").read()
a = '''t_ += "schools = army_tech_school\\n" + techs(HORDE_TECH)'''
assert s.count(a) == 1
s = s.replace(a, '''t_ += "prestige = 80\\nschools = army_tech_school\\n" + techs(HORDE_TECH)''')
open("02_world.py", "w", encoding="utf-8").write(s)

g = open("03g_takecapital.py", encoding="utf-8").read()
if "money.txt" not in g:
    g += r'''

# ---- Heartbreaker's money injection (events/money.txt): on the first day every country's treasury is
# topped up so the game does not open with a world of bankrupt states. Heartbreaker's event is fired by
# its ghost country GHO and gives 250,000 to great powers and 100,000 to everyone else; here the World
# Bank fires it (the one country that always exists) and every country gets the 250,000.
ev = open(os.path.join(H, "events", "money.txt"), encoding=ENC, errors="replace").read().replace("\r\n", "\n")
assert ev.count("tag = GHO") == 1 and ev.count("treasury = 250000") == 1 and ev.count("treasury = 100000") == 1
ev = ev.replace("tag = GHO", "tag = WBK")
a_ = ev.index("any_country = {")
b_ = ev.rindex("}", 0, ev.rindex("}", 0, ev.rindex("}")))        # end of the second any_country block
ev = ev[:a_] + "any_country = {\n\t\t\ttreasury = 250000\n\t\t}\n\t" + ev[b_ + 1:].lstrip("\n")
assert ev.count("{") == ev.count("}") and "is_greater_power" not in ev and ev.count("treasury = 250000") == 1, ev
eid = re.search(r"id\s*=\s*(\d+)", ev).group(1)
for f in glob.glob(os.path.join(OUT, "events", "*.txt")):
    if os.path.basename(f) != "money.txt":
        assert not re.search(r"\bid\s*=\s*%s\b" % eid, open(f, encoding=ENC, errors="replace").read()), f
assert re.search(r"(?m)^WBK\s*=", open(os.path.join(OUT, "common", "countries.txt"), encoding=ENC).read())
wr("events/money.txt", ev)
print("money injection from Heartbreaker: event", eid, "- 250,000 to every country on day one")
'''
    open("03g_takecapital.py", "w", encoding="utf-8").write(g)
print("patched")
