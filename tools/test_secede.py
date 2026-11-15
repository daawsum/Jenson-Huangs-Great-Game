"""Test helper: add a temporary decision to the INSTALLED copy so the AI Taiwan takes unowned Sydney,
owned Tananarive, and moves its capital, on day one. Reinstall the clean build afterwards."""
import os
from config import *

p = os.path.join(V, "mod", "Warlord Era", "decisions", "WarlordEra.txt")
t = open(p, encoding=ENC).read()
assert "zz_test_secede" not in t
i = t.rindex("}")
t = t[:i] + '''\tzz_test_secede = {
\t\tpotential = {
\t\t\ttag = TWN
\t\t\tNOT = { has_country_flag = zz_test_done }
\t\t}
\t\tallow = {
\t\t\twar = no
\t\t}
\t\teffect = {
\t\t\tset_country_flag = zz_test_done
\t\t\t2468 = { secede_province = THIS }
\t\t\t2468 = { add_core = THIS }
\t\t\t2115 = { secede_province = THIS }
\t\t\tcapital = 2468
\t\t}
\t\tai_will_do = {
\t\t\tfactor = 1
\t\t}
\t}
}
'''
open(p, "w", encoding=ENC, newline="\r\n").write(t)
print("test decision added to the installed copy")
