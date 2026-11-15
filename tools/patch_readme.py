"""One-off: bring the readme text in 05_package.py up to date."""
s = open("05_package.py", encoding="utf-8").read()
a = s[s.index('readme = """'):s.index('open(os.path.join(OUT, "readme.txt")')]
new = '''readme = """WARLORD ERA - a Victoria 2 (3.04, Heart of Darkness) multiplayer mod

An alternate history: China westernised and then shattered into warlord cliques, while Europe
and the rest of the old world were left behind and broke apart.

INSTALL
  Copy the folder "Warlord Era" and the file "Warlord Era.mod" into
  <Victoria 2>/mod/ and tick "Warlord Era" in the launcher.
  Every player must use this exact copy or the checksums will differ.

PLAYER SLOTS
  20 major cliques: Zhili, Fengtian, Anhui, Shanxi, Guominjun, Shandong, Henan, Jiangsu,
  Zhejiang, Fujian, Guangdong, Guangxi, Hunan, Hubei, Jiangxi, Sichuan, Yunnan, Guizhou,
  Ma, Xinjiang.
  3 playable outsiders (not civilized, heavily buffed): Sikh Empire, Mongolia, Persia.
  15 minor cliques are selectable but small.

WHAT IS DIFFERENT
  - Only the 35 Chinese cliques are civilized. Each starts with factories in its capital.
  - 137 new Chinese provinces (IDs 3249-3385), 92 Chinese states.
  - The old world is uncivilized and broken up: 57 successor states named after their chief
    cities (Lyon, Caen, Cologne, Kyoto, Valencia, Nizhni Novgorod, Damascus, Khartoum ...).
    Each keeps a core of its parent country, so the parent can reunify.
  - The Americas, Oceania, sub-Saharan Africa, Siberia, the steppe and the outer
    East Indies are empty and colonizable from day one.
  - Any clique can always declare "Warlord Claim" (take a state) or "Absorb Clique"
    (annex a clique with two states or fewer) on another clique.
  - Emigrants go to South East Asia until the first overseas dominion is chartered.
    After that they go to the dominions.
  - Decisions: "Charter the Dominion of ..." turns your colonies in a region into a
    puppet; "Hand New Lands to ..." passes later conquests to it.
  - Formables: Republic of China, Beiyang Government, Liangguang, Shu, Wu, Chu, Dian,
    Northwest Federation, Manchuria, Mongol Empire, Khalsa Raj, Persian Empire, India,
    the Commonwealth, United Baltic Duchy, Czechoslovakia (plus vanilla's own).
  - World Bank: a neutral dummy country on the Falkland Islands. Its bankers are the
    only pops that can mine gold, so its bank always has money to lend. It cannot be
    attacked or sphered.
  - State size flags: every province carries a Tiny/Small/Medium/Large/Huge State
    marker, updated yearly. Warlord Claim costs more war score for bigger states.
  - Map look: Belle Cartographie Dark.

CREDITS
  Migration flag system adapted from the Vae Victis mod.
  World Bank and state sizing adapted from IGoR puir.
  Map graphics: Belle Cartographie, via the "GFM Belle Cartographie Dark" submod by Jman,
  layered on Greater Flavor Mod's terrain files. These are their authors' work; ask them
  before redistributing this mod publicly.
"""
'''
s = s.replace(a, new)
open("05_package.py", "w", encoding="utf-8").write(s)
print("readme updated")
