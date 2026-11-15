# History files

The start state of the world. Almost every crash in a world-rewrite mod lives here.

## Override by name

For each vanilla history file you do not want, ship a file with the same folder and file name.
Do not count on `replace_path` to make vanilla files disappear.

- `history/provinces/<area>/<vanilla file name>` — reuse vanilla's exact name per province ID.
- `history/countries/<TAG> - <Name>.txt` — write one for every vanilla tag, including countries
  that do not exist at start, so a later release comes out the way your setting wants.
- `history/units/<TAG>_oob.txt`
- `history/diplomacy/` — Alliances.txt, Guarantees.txt, PuppetStates.txt, Unions.txt (a comment
  line is enough to blank each).
- `history/wars/` — every vanilla file name, each containing a real war that ended before the
  start date (copy `AmericanWarOfIndependence.txt`, change the `name`). Never an empty folder.
- `history/pops/<date>/` — same file names as vanilla.

## Countries

A new tag needs:

1. a line in `common/countries.txt` (before `dynamic_tags = yes`) pointing to
2. a file in `common/countries/` with `color`, `graphical_culture` and `party` blocks, and
3. five flags in `gfx/flags/`: `TAG.tga`, `TAG_communist.tga`, `TAG_fascist.tga`,
   `TAG_monarchy.tga`, `TAG_republic.tga` — 93x64, 32-bit, RLE TGA (Pillow:
   `im.save(path, compression="tga_rle")` matches vanilla's header), and
4. `TAG;Name` and `TAG_ADJ;Adjective` in localisation, plus names for its parties, and
5. a history file.

Easiest safe route for the country file: copy an existing country's file and change the colour
and the party names.

History file, civilized country (copy the shape from a vanilla great power):
`capital`, `primary_culture`, `culture` (accepted), `religion`, `government`, `plurality`,
`nationalvalue`, `literacy`, `non_state_culture_literacy`, `civilized = yes`, `prestige`, the
political and social reform lines, `ruling_party`, `upper_house`, `schools`, technologies
(`name = 1`), `oob = "TAG_oob.txt"`. `set_country_flag = x` works in history.

Rules to keep (vanilla always satisfies them; see pitfalls.md for which were proven fatal):

- `capital` must be a province the country owns.
- `ruling_party` must be a party in that country's file that is active at the start date, with an
  ideology the government allows (`common/governments.txt`). Ideologies also have unlock dates in
  `common/ideologies.txt`; stay with reactionary, conservative and liberal in 1836.
- Elective governments (democracy, hms_government, prussian_constitutionalism) carry
  `last_election`.
- Every culture and religion named must exist.

Uncivilized country, the vanilla way: no technologies, no `schools`; `civilized = no`; reform lines
(`land_reform = yes_land_reform` ...) chosen so their progress values total well under 100%.

When converting vanilla histories by script, drop the dated blocks (`1861.1.1 = { ... }`) and
`decision =` lines, keep `govt_flag` blocks and `is_releasable_vassal`, and afterwards re-check
the ruling party against the start date.

The world needs several civilized countries or pressing Play crashes.

## Provinces

```
owner = TAG
controller = TAG
add_core = TAG
trade_goods = tea
life_rating = 32
terrain = plains
fort = 1
naval_base = 1
state_building = {
	level = 1
	building = fabric_factory
	upgrade = yes
}
```

- `naval_base` only where the port marker is valid (see map reference).
- An unowned province has no owner/controller/core lines.
- Factories come only from `state_building` blocks. If you rebuild province history and drop
  them, nobody starts with industry.

## Pops

```
1612 = {
	farmers = {
		culture = beifaren
		religion = mahayana
		size = 22000
	}
}
```

- Every owned province needs pops. Do not let a generator create countries out of near-empty
  land: Jan Mayen as a 15-pop country crashed the launch.
- Merging cultures or religions lets you merge identical pops (same type, culture, religion) by
  summing sizes; fewer pops is the main lag saving. Map to *existing* culture keys so vanilla
  scripts that name cultures stay valid, and rename them in localisation.
- Adding a religion: add it to an existing group in `common/religion.txt` (keep the others so
  vanilla references stay valid).

## Units

```
army = {
	name = "First Army"
	location = 1612
	regiment = {
		name = "1st Infantry"
		type = infantry
		home = 1612
	}
}
navy = {
	name = "Home Fleet"
	location = 1617
	ship = {
		name = "Flagship"
		type = manowar
	}
}
```

`location` and `home` must be provinces the country owns. A navy's `location` is a land
province with a valid port. `leader = { ... }` blocks can be carried over from vanilla.
