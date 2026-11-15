# Making a mod multiplayer-safe

Honest scope note: the mod this skill came from was tested in single player on one machine. The
rules below are the established practice for Vic2 multiplayer mods plus what was observed about
the checksum; treat a real two-machine session as the only proof.

## Everyone must run identical files

Victoria 2 computes a checksum of the game data at start-up and shows it at the bottom-left of
the main menu, e.g. `V2 v3.04 (KLGG)`. Players can only join a host with the same checksum. In
testing, the four-letter code changed with every change to the mod's data files, which makes it
a quick identity check for a build.

- Ship the mod as one archive containing the mod folder and the `.mod` file. Everyone extracts it
  into `<Victoria 2>/mod/` and deletes the old copy first, so no stale file survives.
- Never ask players to edit files by hand, and never rely on files in the base game folder being
  changed. A base-game edit on the host's machine (a patch, a skipped intro, a leftover from
  another mod installed over vanilla) is invisible in the mod archive.
- Because the base install must match too, have players verify their game files through Steam
  if checksums differ and the mod archive is identical.
- Before a session, have everyone read out the checksum from the main menu with the mod enabled.

## Make the mod self-contained

A mod that overrides only what it changes inherits everything else from each player's base game.
That is normal and fine when the base is unmodified. If you cannot trust that, override more
(whole `common/`, `events/`, `decisions/`) so the mod, not the base, decides the result.

Override vanilla history files by name rather than trusting `replace_path` (see
history-files.md); otherwise two players could in principle end up with different leftovers.

## Per-machine things that do not belong in the mod

- `Documents/Paradox Interactive/Victoria II/<user_dir>/settings.txt` (resolution, autosave).
- The map cache under `<user_dir>/map/cache`. It is rebuilt on first launch. If you ship a new
  version with map changes, tell players to delete that cache folder or bump `user_dir`.
- Save games. The host's save is what gets transferred on rehost.

## Design for humans

- Unowned, colonizable land and many small states are cheap; hundreds of countries and tens of
  thousands of pops are not. Lag grows with pop count and with the number of countries the AI
  runs. Merging cultures and religions lets you merge pops; absorbing one-province states cuts
  AI load.
- Decisions the AI can take for free get taken on day one by every eligible AI country.
- Give player slots comparable starts and say plainly which are not (landlocked, low pop).
- The lobby lists countries by rank. Old-world countries inherit vanilla prestige unless you
  clear it, which pushes your intended player slots down the list.
- Victoria 2 cannot lock countries in the lobby; "playable" is a convention you write down.

## Release checklist

1. `check_mod.py` clean on the build you are about to zip.
2. Launch, reach the menu, press Play, run at least a few months, read the save.
3. Test fullscreen as well as windowed.
4. Zip folder + `.mod`; note the checksum in the readme or release message.
5. On a second machine (or a clean copy of the game), install from the zip only and compare the
   checksum.
6. Credit anything taken from other mods.
