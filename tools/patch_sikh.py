"""One-off patch: the Khalsa Army's bonuses cut to a quarter, its mobilisation penalty raised to 10%."""
s = open("03_gameplay.py", encoding="utf-8").read()
a = '''    land_organisation=0.6, org_regain=0.5, land_attack_modifier=0.25, land_defense_modifier=0.25,
    land_unit_start_experience=50, mobilisation_size=-0.02, supply_consumption=-0.2, leadership=2)'''
assert s.count(a) == 1
s = s.replace(a, '''    land_organisation=0.15, org_regain=0.125, land_attack_modifier=0.0625, land_defense_modifier=0.0625,
    land_unit_start_experience=12.5, mobilisation_size=-0.1, supply_consumption=-0.05, leadership=0.5)''')
open("03_gameplay.py", "w", encoding="utf-8").write(s)
print("patched")
