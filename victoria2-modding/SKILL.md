---
name: victoria2-modding
description: Build, fix and test Victoria 2 (Victoria II, Vic2, V2, Heart of Darkness 3.04) mods that actually load, start a game and stay usable in multiplayer. Use this whenever someone wants to make or change a Vic2 mod — new countries or tags, province or map edits, history files, pops, cultures, decisions, events, formables, war goals, modifiers, national focuses, loading screens, total conversions, submods of HPM/HFM/GFM/DoD/IGoR — and whenever a Vic2 mod crashes on launch, crashes when pressing Play, shows a broken or water-covered map, desyncs or has checksum problems. Vic2 fails silently (empty error.log) on small deviations from vanilla, so consult this before writing any Vic2 file rather than relying on general Paradox-game knowledge.
---

# Victoria 2 modding

Victoria 2 is a 2010 engine with almost no validation. A mod that looks correct on paper can crash
at start-up, crash when you press Play, or draw half the map as ocean, and the error log will be
empty every time. Everything in this skill was learned by building a large mod (new provinces, 60+
new tags, rewritten world history) and bisecting each failure in the running game.

The single most important habit: **do what vanilla and a working mod do, verbatim, and test in the
real game early.** General Paradox knowledge (EU4, HOI4, even "how Clausewitz works") is wrong
often enough here to cost hours.

## How to work

1. **Find the install and the reference mods.** Typical path:
   `<Steam library>/steamapps/common/Victoria 2`. Mods live in its `mod/` folder as a folder plus
   a `<name>.mod` file. Note which large mods are installed (HPM, HFM, GFM, Divergences, IGoR,
   Vae Victis ...): they are your documentation. Confirm the base is unmodified or at least know
   what was changed, because every player needs the same effective files.

2. **Before writing a file type for the first time, open vanilla's version and a working mod's
   version of that same file type** and copy the structure. Do not invent keys, values or layouts.
   `scripts/check_mod.py` automates much of this comparison for country history.

3. **Generate, don't hand-edit, anything large.** A world rewrite touches thousands of province
   and pop files. Write a script that reads vanilla and emits the mod, so a fix is one line and a
   rebuild. Keep the generator beside the mod.

4. **Run the static checker, then launch the game.** Static checks catch a lot but not
   everything; only the engine can tell you the mod works. See "Testing" below.

5. **Bisect, don't guess.** When it crashes with an empty log, strip the installed copy toward
   vanilla in halves until one file or one line is left. Guessing wasted far more time than
   bisecting ever did. `references/testing.md` has the method and the traps (some bisect
   configurations crash for their own unrelated reasons).

6. **Say what you verified.** "Loads to the menu", "starts a game", "ran N months", "multiplayer
   synced" are four different claims. Report the one you actually tested.

## The mod skeleton

```
mod/
  My Mod.mod
  My Mod/
    common/  history/  map/  events/  decisions/  localisation/  gfx/  interface/  poptypes/ ...
```

```
name = "My Mod"
path = "mod/My Mod"
user_dir = "MyMod"
replace_path = "history/provinces"
```

- `user_dir` gives the mod its own settings, save games and **map cache** under
  `Documents/Paradox Interactive/Victoria II/<user_dir>/`. Always set it. If you change the map
  after a cache was built, give players a fresh cache (new `user_dir`, or delete
  `<user_dir>/map/cache`).
- Mod files override vanilla files **with the same path and name**. Whole-file override: to
  change one line of `common/cb_types.txt` you ship the complete file.
- `replace_path` is not something to lean on. It did not stop vanilla's
  `history/diplomacy/PuppetStates.txt` from applying. Override each vanilla file you want gone
  with a same-named file of your own (see `references/history-files.md`).
- Text files are Windows-1252, CRLF. Localisation is `KEY;English;;;;;;;;;;;;;x` in a `.csv`
  under `localisation/`; name yours `00_something.csv` so it loads before vanilla's and wins.

## The crash list (read `references/pitfalls.md` before a first launch)

Each of these was isolated in the running game, with **nothing in error.log**:

| Symptom | Cause |
|---|---|
| New provinces drawn as water, ownership looks scrambled | `map/default.map` must say `definitions = "../mod/<Mod Folder>/map/definition.csv"`; otherwise vanilla's definition.csv is read |
| Crash at "Executing History" on launch | a country that should not exist (Jan Mayen, 15 pops, made independent by a generator) |
| Crash on pressing Play | `history/wars` holding no real war file; a fleet in a province whose `naval_base` marker is not in the sea; zero or one civilized country |
| Fullscreen never reaches the menu | `movies/game_intro.bik` removed (a blocking "Bink Error" box); rename `movies/binkplay.exe` instead to skip the intro |
| Uncivilized country can westernize on day one | starting reforms add up to 100% `civilization_progress_modifier` |
| Vassals or substates appear that you removed | vanilla diplomacy file still applied; override it by name |

`references/pitfalls.md` has the full list, the evidence, and which other fixes were made
along the way without being proven as causes. That distinction matters when you debug: do not
stop at the first deviation from vanilla you find, because working mods deviate too.

## Reference files

Read the one that matches the work; they are short.

- `references/pitfalls.md` — every confirmed silent failure, how it shows up, how to fix it.
- `references/map-and-provinces.md` — adding or splitting provinces: the bitmap, definition.csv,
  default.map, positions (ports!), regions, continents, terrain, history and pops for new IDs.
- `references/history-files.md` — countries, provinces, pops, units, diplomacy, wars: what vanilla
  does and what must match; new tags, parties, flags; uncivilized countries.
- `references/gameplay-scripting.md` — decisions, events, modifiers, war goals, pop types,
  migration, national focuses, loading screens: patterns that worked, with the working mod each
  was taken from.
- `references/multiplayer.md` — what makes a mod multiplayer-safe and how to ship it.
- `references/testing.md` — launching the game from a script, capturing the window, clicking,
  bisecting, and reading a save file to confirm effects.

## Scripts

All take the game folder and the mod folder name as arguments and need only Python 3
(`check_mod.py` uses Pillow and numpy for the bitmap check if they are installed).

- `scripts/check_mod.py "<game dir>" "<Mod Folder>"` — static checks for the crash list above
  and more. Run it after every build. A clean run does not prove the mod loads.
- `scripts/read_save.py "<save.v2>" [TAG ...]` — summarises a save: date, countries, money,
  civilized, modifiers, flags, cores, pops, cultures, religions. The reliable way to confirm an
  event or modifier really took effect.
- `scripts/launch_test.sh "<game dir>" "<Mod Folder>" "<user_dir>"` — launches the mod, reports
  whether it reached the main menu, and can press Play (Windows, Git Bash).
- `scripts/win.ps1` — capture only the game window, click, and send keys (used by the above).

## Testing, in short

1. `check_mod.py` clean.
2. Launch with `v2game.exe -mod=mod/<name>.mod`. Reaching the main menu proves the map and all
   history parsed.
3. Press Play. A crash here is a different class of bug from a launch crash (wars, fleets, too
   few civilized countries).
4. Run a few months with `autosave="MONTHLY"` in `<user_dir>/settings.txt`, then read the save
   with `read_save.py`. Look at a screenshot of the lobby map too; a broken map is obvious there.
5. Test **windowed and fullscreen**. They differ (the intro video only plays fullscreen).
6. For multiplayer, compare the checksum shown at the bottom-left of the main menu between two
   machines before anyone hosts.

## Things to tell the person you are helping

- Borders cut by script are geometric, not hand-drawn; flags you generate are placeholders.
- Art, shaders and code copied from other mods belong to their authors. Fine among friends; ask
  before public release, and credit them in the readme either way.
- Changes to the base game folder (for example skipping the intro) affect every mod and are
  undone by Steam's "verify integrity".
