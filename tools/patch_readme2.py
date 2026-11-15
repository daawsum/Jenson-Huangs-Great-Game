"""One-off: readme for the v2 feature set."""
s = open("05_package.py", encoding="utf-8").read()
a = s[s.index("WHAT IS DIFFERENT"):s.index('"""\nopen(os.path.join(OUT, "readme.txt")')]
new = '''WHAT IS DIFFERENT
  - Only the 35 Chinese cliques are civilized. They differ: republics, regencies, leagues,
    garrison commands and free cities, each major with its own permanent strength.
  - 137 new Chinese provinces (IDs 3249-3385), 92 Chinese states.
  - Cultures: China has five (Northern Han, Yangtze Han, Cantonese, Hokkien, Manchu) plus the
    frontier peoples, and a clique accepts only its own. Europe, Africa and the New World have
    one culture per culture group. There is a single religion. Identical pops are merged.
  - The old world is uncivilized, barely literate and broken up, with about 20 successor
    states named after their chief cities. Micro-states were absorbed by their neighbours.
  - The Americas, Oceania, sub-Saharan Africa, Siberia, the steppe and the outer
    East Indies are empty and colonizable from day one.
  - Any clique can always declare "Warlord Claim" (take a state; the cost depends on the
    state's size flag) or "Absorb Clique" (annex a clique with two states or fewer).
  - Emigrants go to South East Asia until the first overseas dominion is chartered.
  - Decisions: "Charter the Dominion of ..." turns your colonies in a region into a
    puppet; "Hand New Lands to ..." passes later conquests to it.
  - Formables: Republic of China, Beiyang Government, Liangguang, Shu, Wu, Chu, Dian,
    Northwest Federation, Manchuria, Mongol Empire, Khalsa Raj, Persian Empire, India,
    the Commonwealth, United Baltic Duchy, Czechoslovakia (plus vanilla's own).
  - World Bank: a neutral dummy country on the Falkland Islands whose bankers are the only
    pops that can mine gold. Its bank always has money to lend. It cannot be attacked.
  - State size flags: every province carries a Tiny/Small/Medium/Large/Huge State core,
    re-measured yearly.
  - National focuses: IGoR puir's tiered focuses. Tiers 2-6 unlock for civilized countries
    in 1845, 1855, 1865, 1880 and 1895.
  - Map look: Belle Cartographie Dark.

CREDITS
  Migration flag system adapted from the Vae Victis mod.
  World Bank, state sizing and national focuses adapted from IGoR puir.
  Map graphics: Belle Cartographie, via the "GFM Belle Cartographie Dark" submod by Jman,
  layered on Greater Flavor Mod's terrain files. These are their authors' work; ask them
  before redistributing this mod publicly.
'''
s = s.replace(a, new)
open("05_package.py", "w", encoding="utf-8").write(s)
print("readme updated")
