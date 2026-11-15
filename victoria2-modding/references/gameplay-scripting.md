# Gameplay scripting patterns that worked

Each pattern names the installed mod it was taken from, so you can open the original.
Common files are whole-file overrides: copy vanilla's file and add to it.

## Decisions (`decisions/*.txt`)

```
political_decisions = {
	my_decision = {
		potential = { has_country_flag = my_flag NOT = { has_country_flag = did_my_decision } }
		allow = { war = no money = 20000 }
		effect = {
			set_country_flag = did_my_decision
			treasury = -20000
			add_country_modifier = { name = my_modifier duration = -1 }
		}
		ai_will_do = { factor = 1 }
	}
}
```

Localisation: `my_decision_title` and `my_decision_desc`. `duration = -1` is permanent.
The AI takes cheap decisions on day one; price or gate them if that matters.

Formable nation: `allow` lists `owns = <province id>` lines; `effect` ends with
`change_tag = NEW`. The country keeps its flags, modifiers and civilized status.

Claims: `TAG = { any_owned = { add_core = THIS } }` then
`casus_belli = { target = TAG type = conquest months = 60 }`.

## Events (`events/*.txt`)

One-time set-up per country (history cannot add modifiers):

```
country_event = {
	id = 880001
	title = "EVTNAME880001"
	desc = "EVTDESC880001"
	picture = "Upperhouse"
	trigger = { tag = XXX NOT = { has_country_modifier = my_modifier } }
	mean_time_to_happen = { days = 1 }
	option = {
		name = "EVTOPTA880001"
		add_country_modifier = { name = my_modifier duration = -1 }
	}
}
```

Pick an id range no vanilla or included file uses. `immediate = { }` runs before the option.

## Modifiers (`common/event_modifiers.txt`)

`name = { key = value ... icon = N }`, localised as `name` and `desc_name`.
Keys confirmed on the 3.04 exe: land_organisation, naval_organisation, org_regain,
land_unit_start_experience, mobilisation_size, mobilisation_economy_impact, supply_consumption,
leadership, max_attrition, war_exhaustion, research_points_modifier, tax_efficiency,
factory_throughput, farm_rgo_eff, mine_rgo_eff, rgo_output, loan_interest, prestige,
core_pop_militancy_modifier, global_pop_militancy_modifier, global_pop_consciousness_modifier,
global_immigrant_attract, global_population_growth, diplomatic_points_modifier,
cb_generation_speed_modifier, land_attack_modifier, land_defense_modifier,
self_unciv_military_modifier, self_unciv_economic_modifier.

## War goals (`common/cb_types.txt`)

A war goal that is always available between certain countries, cloned from vanilla's
`acquire_core_state` (which is always available for cores):

```
my_claim = {
	sprite_index = 5
	is_triggered_only = yes
	months = 12
	badboy_factor = 0.4
	prestige_factor = 3
	peace_cost_factor = 0.8
	penalty_factor = 1
	always = yes
	... (copy the remaining factor lines from acquire_core_state) ...
	can_use = {
		has_country_flag = my_flag
		THIS = { has_country_flag = my_flag }
		NOT = { is_our_vassal = THIS }
		number_of_states = 3
	}
	allowed_states = { not = { any_owned_province = { is_capital = yes } } }
	po_demand_state = yes
	war_name = WAR_TAKE_NAME
}
```

Add the name to the `peace_order` list at the top of the file. Needs `name`, `name_desc`,
`name_setup`, `name_short` in localisation. In `can_use` the scope is the target and `THIS` is
the attacker.

## State size flags (IGoR puir, `events/State Sizing.txt`)

Five dummy tags (Tiny/Small/Medium/Large/Huge State) that are never released
(`is_releasable_vassal = no`). A yearly event on a country that always exists adds the matching
tag's core to every province by state population and removes the other four:

```
any_country = {
	limit = { war = no }
	any_owned = {
		limit = { state_scope = { total_pops = 100000 NOT = { total_pops = 400000 } } }
		add_core = SMA
		remove_core = TIN ...
	}
}
```

The core's flag shows the state size in the province view, and war goals can test
`any_owned_province = { is_core = SMA }` to scale cost by size. Guard the event with a
365-day country modifier as a cooldown.

## World bank (IGoR puir, Liechtenstein)

A dummy uncivilized country whose only pops are a custom rich pop type (`poptypes/bankers.txt`,
no needs, `promote_to = { }`, migration factor 0) working a precious-metal RGO through a custom
template in `common/production_types.txt`. Its party uses two extra party issues added to
`common/issues.txt` (tax locked at 99-100%, tariffs near zero). Events keep it uncivilized,
at zero prestige and out of every sphere. Its national bank fills up and lends to everyone.
Because gold is now mined only by that pop type, change other gold provinces to another good.
If it is reachable by sea, add an event that ends any war declared on it.

## Migration targets (Vae Victis, `poptypes/*.txt`)

Each pop type file has `country_migration_target = { factor = 1 modifier = { ... } }`.
Gate emigration on a country flag:

```
modifier = { factor = -10000 NOT = { has_country_flag = new_world_nation } }
modifier = { factor = -10000 has_country_flag = old_world_colony has_global_flag = new_world_opened }
```

Set the flags in country history and clear them by event. Pops only emigrate to a country on
another continent.

## Releasing a puppet from owned land

`any_owned = { limit = { region = X } add_core = NEW }` then `release_vassal = NEW`, then
`NEW = { ... }` to set flags and modifiers. `secede_province = NEW` hands later conquests over.
`region = KEY` is a valid province trigger (HPM uses it everywhere) though vanilla never does.

## National focuses (IGoR puir)

`common/national_focus.txt` is a whole-file override. More focuses than vanilla's 31 need more
icon frames: copy the wider icon strips (`gfx/interface/province_natfocus_strip*.dds`) and raise
`noOfFrames` for `national_focus` in `interface/mapitems.gfx` and for the two
`GFX_province_natfocus_strip*` sprites in `interface/province_interface.gfx`. Tiers are gated with
`limit = { owner = { has_country_flag = tier_2 } }`; set the flags by event.

## Loading screens and the map look

- `gfx/loadingscreens/load_1.dds` .. `load_7.dds`; see pitfalls for the 4:3 canvas rule.
- A map reskin (terrain textures, colour maps, borders, water, shaders in `gfx/FX`) is graphics
  only and works on any province layout. It lives in `map/terrain/` and `gfx/FX/`.
