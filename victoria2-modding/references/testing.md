# Testing a Vic2 mod from a script

The error log is usually empty, so testing means running the game and observing it.

## Launch and detect

```
"<game dir>/v2game.exe" -mod=mod/<Mod Name>.mod
```

Logs go to `Documents/Paradox Interactive/Victoria II/<user_dir>/logs/`:

- `system.log` — load stages. `done frontend` means the main menu was reached. The last
  "Load text" line before a crash names the stage (`Executing History` = history files).
- `game.log` — after Play: `[[ Launching SINGLEPLAYER-game ]]`, then dated message lines. The
  last date tells you how far a run got, and `Decision:` / `Event:` lines show what fired.
- `error.log` — worth reading, rarely useful.
- `map/cache/adjacencies.bin` smaller than vanilla's after adding provinces = the engine is not
  seeing your provinces.

A real crash leaves an "Application Error" entry for v2game.exe in the Windows Application event
log, with a fault offset that is identical for the same bug. No entry means the process was
closed some other way (including by a person at the keyboard).

`scripts/launch_test.sh` does launch, wait-for-menu, optional Play, and reporting.

## Seeing and clicking

Run windowed for tests: in `<user_dir>/settings.txt` set `fullScreen=no`, `borderless=no` and a
size such as 1600x900 (back up the file and restore it afterwards; the game rewrites it).
`scripts/win.ps1` then:

- `shot <file.png>` captures only the game window,
- `click <x> <y>` clicks at window coordinates,
- `key "<SendKeys string>"` sends keys (space toggles pause, `{ADD}` raises speed).

Main menu at 1600x900: Single Player is near (557, 696); in the lobby the country list rows
start near y = 365 with 19 px spacing, and Play is at the bottom-right. Take a screenshot before
trusting coordinates: the window can come up a different size, and a blind click can open or
close panels, move the camera or miss the button.

Look at the lobby map itself. Wrong colours, water patches over land, or a camera that jumps to
the wrong place when you select a country all mean the map files are wrong.

Also test once in fullscreen: some failures (the intro video player) only occur there.

## Confirming effects: read the save

Clicking through panels blind is unreliable. Instead:

1. set `autosave="MONTHLY"` in `<user_dir>/settings.txt`,
2. let the game run a few months,
3. read `<user_dir>/save games/autosave.v2` (plain text, Windows-1252) with
   `scripts/read_save.py`.

The save shows each country's money, bank, civilized flag, modifiers and flags, province owners
and cores, pops with culture and religion, and vassal/alliance blocks. That is how to prove a
yearly event stamped its cores, a modifier was applied, or a diplomatic relation is gone.

## Bisecting a silent crash

Work on the **installed copy**, not the source, and reinstall a clean copy before each test.

1. Find two endpoints: a configuration that works (vanilla, or the mod with a large part
   removed) and one that fails.
2. Move from the failing side toward the working side in halves: delete folders, drop
   `replace_path` lines, blank unit files, make half the countries own nothing.
3. When a group of files is implicated, bisect inside it: restore vanilla's text for half of the
   files, then half of the remainder.

Traps that produced false results:

- A stripped-down world can crash for its own reasons. Leaving no civilized countries, or only
  a handful of countries, crashes on Play regardless of the bug you are hunting. Keep each test
  configuration a valid world.
- If two independent bugs exist, removing one still crashes. When a test "should" pass and does
  not, build up from the working side instead: add one component at a time to the known-good
  configuration.
- A test harness that selects "the 7th country in the list" silently selects nothing when the
  list is shorter; the game then never starts and looks like a pass. Confirm from `game.log`
  that `Launching SINGLEPLAYER-game` appeared.
- Kill stray `v2game.exe` and `binkplay.exe` processes between runs.
- If someone else is using the machine, they may close or click the test window. A missing
  crash record in the event log is the tell.

## What each milestone proves

| Reached | Proves |
|---|---|
| Main menu | map files and all history parsed and executed |
| Lobby map looks right | provinces, definitions, ownership are consistent |
| Game starts after Play | wars, units, fleets, great-power set-up are valid |
| N months, empty error.log | daily events, decisions, AI are stable so far |
| Save shows the expected data | your scripted effects really happened |
| Same checksum on two machines | the build is identical for multiplayer |
