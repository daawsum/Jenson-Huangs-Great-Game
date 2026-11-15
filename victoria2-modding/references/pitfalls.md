# Silent failures

Found while building one large mod on Victoria 2 3.04 (Heart of Darkness). In every case
`error.log` was empty. "Launch" means between starting the exe and the main menu; "Play" means
after pressing Play in the lobby.

Entries are marked by how sure the evidence is:

- **[isolated]** — bisected in the running game down to this one cause; fixing it alone fixed it.
- **[fixed alongside]** — corrected during a crash hunt that had other causes too, so it was
  never proven to crash on its own. Still do it vanilla's way; just do not treat it as the
  certain culprit when debugging.

Calibration: GFM, HPM and Vae Victis all run with things a strict reading of "do exactly what
vanilla does" would forbid (uncivilized countries with a technology, units whose home province
they do not own, countries with a few thousand pops). Vanilla-conformity is the safe default,
not a law.

## Map

**New provinces render as water; ownership inside the edited area looks scrambled; clicking a
province selects the wrong country.**
The engine reads `definition.csv` from the *base game* unless `map/default.map` points into the
mod: `definitions = "../mod/<Mod Folder>/map/definition.csv"`. GFM and IGoR both do this. A tell:
the cache file `adjacencies.bin` comes out *smaller* than vanilla's even though you added
provinces. Changing colours, positions, regions, continents, climate or terrain makes no
difference until this line is right.

**Map still wrong after a fix.** The cache in `Documents/Paradox Interactive/Victoria
II/<user_dir>/map/cache` is reused. Delete it or use a new `user_dir`.

**`provinces.bmp` orientation.** The file is stored so that image libraries load it vertically
flipped: array row == the `y` used in `positions.txt`. Verify with one known province before
generating positions. Save it back as 24-bit BMP; safest is to keep vanilla's header bytes and
replace only the pixel data.

**Fleet start crashes Play.** The `naval_base` marker in `positions.txt` sits *in the adjacent
sea province* in vanilla (1029 of 1038 markers). The engine reads the port's sea zone from that
spot. A marker on land makes any navy that starts in that province crash the game. Only place
fleets and `naval_base` buildings in provinces whose marker you know is in open sea.

**Lakes count as sea.** Lakes are listed in `sea_starts`. "Adjacent to a sea province" is not
"coastal": use the largest connected group of sea provinces as the ocean.

## History

**Crash at "Executing History" (launch).**
- **[isolated]** Jan Mayen made into its own country (one province, 15 farmers). Bisecting the
  country list ended on that single tag. Leaving near-empty territory unowned fixed it. The exact
  trigger was not pinned down further: GFM and HPM run countries of a few thousand pops, so it is
  not "small population" in general.
- **[fixed alongside]** A `ruling_party` whose `start_date` is after the game's start date. This
  appears when a releasable country (Norway, Scotland, Hungary, Albania ...) is made to exist in
  1836. Vanilla never has it for a country that exists at start.
- **[fixed alongside]** A value that only exists in another mod, e.g. `nationalvalue =
  nv_tradition` (HPM). Vanilla has `nv_order`, `nv_liberty`, `nv_equality`. The launch stopped
  crashing after 15 seconds once this was fixed, but another bug was still present.

**Crash on Play.**
- **[isolated]** `history/wars` overridden and holding no real war file. A comment-only file or
  an empty folder crashes. Ship a real war that ended before the start date under every vanilla
  war file name.
- **[isolated]** A fleet starting in a province whose port marker is on land (see Map).
- **[isolated]** Too few civilized countries: zero and one both crashed, seven worked. The game
  needs great powers.

**[isolated] Vanilla diplomacy survives.** With `replace_path = "history/diplomacy"` and only one
file in the mod's folder, vanilla's `PuppetStates.txt` still made countries substates (visible in
the province panel, absent from the save once fixed). Write a file for *each* vanilla name
(Alliances, Guarantees, PuppetStates, Unions); a comment-only file is fine here.

**Province history file names.** A few vanilla files have odd names (`3246  JanMayen.txt`, no
dash). If your generated name differs, both files may load. Reuse vanilla's exact base name.

**[fixed alongside] Uncivilized countries.** In vanilla they have no technologies and no `schools`
line in history. HPM gives some of its uncivilized countries a technology and runs, so this is a
convention, not a crash.

**[fixed alongside] Unowned provinces.** Vanilla keeps only aristocrats, clergymen, artisans,
soldiers, farmers, slaves and labourers there. HPM has a few officers in unowned land and runs.

**Westernization.** Each `yes_<reform>` in `common/issues.txt` has a
`civilization_progress_modifier` (economic 0.15 to 0.35, military 0.1). If a country's starting
reforms total 1.0 it can westernize on day one. Sum them from the file and stay well under.

**Country file names used twice.** Party names can repeat across countries (IGoR does it), but
giving each tag its own `TAG_ideology` names is the vanilla convention and avoids surprises.

## Scripting

**Trigger and modifier names.** Vanilla's own files are not the full vocabulary: `region = X`,
`num_of_vassals`, `end_war`, `land_attack_modifier`, `land_defense_modifier` are valid on this
exe but appear only in mods. Before using a name that vanilla does not use, find it in a mod
that runs on the same exe.

**No unit-type modifiers outside technologies.** "Infantry attack +X" cannot be a country
modifier. `land_attack_modifier` / `land_defense_modifier` apply to all land units.

**`civilized = yes` in a decision did not stop an uncivilized country** from taking a decision
in one test. Gate on a country flag you set in history when it matters.

**Tag clashes.** New tags must not collide with vanilla's 271 (SCH is Schleswig, ANH is Anhalt,
SIC is Sicily, HUN is Hungary, HAI is Haiti ...). Check against `common/countries.txt`.

## Start-up

**Intro video.** A mod cannot override `movies/game_intro.bik`. Removing or renaming that file
makes fullscreen start-up stop on a "Bink Error" box (windowed mode hides the problem because it
never plays the video). To skip the intro, rename `movies/binkplay.exe`. This is a base-game
change: it applies to all mods on that machine and Steam's verify undoes it.

**Loading screens.** Seven files, `gfx/loadingscreens/load_1.dds` to `load_7.dds`. The 1024x1024
texture is shown as a 4:3 picture scaled to the screen width and cropped top and bottom. Put a
16:9 picture in the middle of a 4:3 canvas, then squash the canvas to 1024x1024. Uncompressed
32-bit DDS works (Vae Victis uses it).
