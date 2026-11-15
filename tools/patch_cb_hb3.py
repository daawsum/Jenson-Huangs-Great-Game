"""One-off patch of 03c_statesize.py: the state flag tooltip no longer lists Free Peoples."""
s = open("03c_statesize.py", encoding="utf-8").read()
a = r'''"\xa7YDemand Concession: \xa7W%d%% Warscore\\n\xa7YPlace in the Sun: \xa7W%d%% Warscore\\n\xa7YFree Peoples: \xa7W%d%% Warscore") % ('''
assert s.count(a) == 1
s = s.replace(a, r'''"\xa7YDemand Concession: \xa7W%d%% Warscore\\n\xa7YPlace in the Sun: \xa7W%d%% Warscore") % (''')
a = '''cost("acquire_state", i), cost("demand_concession_casus_belli", i), cost("place_in_the_sun", i), cost("free_peoples", i))'''
assert s.count(a) == 1
s = s.replace(a, '''cost("acquire_state", i), cost("demand_concession_casus_belli", i), cost("place_in_the_sun", i))''')
open("03c_statesize.py", "w", encoding="utf-8").write(s)
print("patched")
