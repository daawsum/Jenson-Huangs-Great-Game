# Adding or splitting provinces

A new province needs an entry in **every** one of these, or it is broken in some way that
nothing reports.

| File | What to add |
|---|---|
| `map/provinces.bmp` | pixels in a colour no other province uses |
| `map/definition.csv` | `id;r;g;b;Name;x`, new IDs continuing after vanilla's last (3248) |
| `map/default.map` | `max_provinces = <highest id + 1>` **and** `definitions = "../mod/<Mod Folder>/map/definition.csv"` |
| `map/positions.txt` | a block for the province (unit, text, city, buildings, `naval_base` if coastal) |
| `map/region.txt` | the province inside exactly one state |
| `map/continent.txt` | the province on exactly one continent |
| `map/climate.txt` | the province in a climate list |
| `history/provinces/<area>/<id> - <Name>.txt` | owner, controller, cores, `trade_goods`, `life_rating`, `terrain` |
| `history/pops/<date>/<file>.txt` | a pop block for the ID |
| `localisation/*.csv` | `PROV<id>;Name;...` |

New land province IDs after the sea-zone IDs are fine (GFM goes to 3553).

## The bitmap

- 5616 x 2160, 24-bit. Loaded with an image library it comes out vertically flipped relative to a
  north-up map; do not "fix" it. Row index equals `positions.txt` y.
- Build an id map with numpy: unique colours, look each up in definition.csv.
- Vanilla contains a few dozen stray colours that are in no definition line. Leave them.
- To split a province by script: take its pixels, find the principal axis, cut at the median (or
  terciles for three parts). A low-frequency sine added to the cut line makes borders look less
  ruled; skip the wobble for small or thin provinces or it produces stripes.
- Keep the original ID on the part that contains the old city marker.
- When writing the file, keep vanilla's 54-byte header and append the pixel rows bottom-up in
  BGR order. Read it back and compare.

## positions.txt

For provinces you changed, regenerate the block:

- interior point for `unit`, `text_position`, `city`, `factory`, etc.: the pixel farthest from
  the province edge (distance transform) is a good anchor.
- `building_position = { fort = ... railroad = ... naval_base = ... }`.
- **`naval_base` goes on a pixel of the adjacent open-sea province**, not on land. Pick the sea
  zone the province shares the most coast with. Record which provinces got a valid marker and
  only allow fleets and naval bases there.

Provinces you did not touch keep vanilla's block untouched.

## States, continents, terrain

- A state (`region.txt`) can be split between owners, but owner-homogeneous states are tidier:
  cluster each owner's provinces into groups of three or four.
- Region keys need localisation (`KEY;Name`).
- Continents are just province lists with modifiers. You may add a continent (GFM and Vae
  Victis do). Emigration only goes to a country on a *different continent* from the pop, which
  is why a mod that wants migration inside Asia splits Asia.
- Put `terrain = <type>` in the history of new provinces, as GFM does for most of its own.
  Derive the type from `terrain.bmp` (palette index to type via `map/terrain.txt`).

## Pops and economy for new provinces

- Split the parent's pops between the pieces by area.
- Children inherit `trade_goods` and `life_rating`.
- Uncolonized land needs `life_rating` at or above the coloniser's limit (35 at game start) to be
  colonizable immediately.

## Checking

`check_mod.py` verifies: definition path, `max_provinces`, every bitmap colour for a new ID is
present, each history province is in one region and one continent, new provinces have positions,
history, pops and a name. Then look at the lobby map: a broken map is visible at a glance.
