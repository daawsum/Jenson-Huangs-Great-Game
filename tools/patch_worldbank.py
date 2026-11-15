"""One-off: teach 02_world.py about the World Bank on the Falklands."""
s = open("02_world.py", encoding="utf-8").read()
if "WBK_PROVS" in s:
    raise SystemExit("already patched")


def rep(a, b, count=1):
    global s
    assert s.count(a) >= 1, a
    s = s.replace(a, b, count)


# 1 ownership
rep('EMPTIED = {p for p in ALLP',
    '# the World Bank (after IGoR puir) sits on the Falkland Islands\n'
    'WBK_PROVS = [2131, 2133]\n'
    'BANK_POPS = "\\n\\tbankers = {\\n\\t\\tculture = british\\n\\t\\treligion = protestant\\n\\t\\tsize = 100000\\n\\t}\\n"\n'
    'for p in WBK_PROVS:\n    owner[p] = "WBK"\n\n'
    'EMPTIED = {p for p in ALLP')
# 2 pops
rep('            p = int(k)\n',
    '            p = int(k)\n            if p == 2131:\n                body = BANK_POPS\n')
rep('run_pops(POPFAC, True)\n',
    'run_pops(POPFAC, True)\n'
    'if popsize[2131] == 0:\n'
    '    wr("history/pops/1836.1.1/World Bank.txt", "2131 = {%s}\\n" % BANK_POPS)\n'
    '    popsize[2131] = 100000\n')
# 3 cores and goods
rep('            cores = [o] + [c for c in v["cores"] if c != o and c not in BIG]\n',
    '            cores = [o] if o == "WBK" else [o] + [c for c in v["cores"] if c != o and c not in BIG]\n')
rep('    if v["goods"]:\n        L.append("trade_goods = %s" % v["goods"])\n',
    '    goods = v["goods"]\n'
    '    if p == 2131:\n        goods = "precious_metal"\n'
    '    elif goods == "precious_metal":          # only bankers can mine gold now, so other deposits change\n'
    '        goods = ["iron", "coal", "sulphur"][p % 3]\n'
    '    if goods:\n        L.append("trade_goods = %s" % goods)\n')
# 4 country definition
rep('lines[ins:ins] = ["# Warlord Era"] + add + [""]\n',
    'add.append(\'WBK\\t\\t= "countries/WE_WBK.txt"\')\n'
    'wr("common/countries/WE_WBK.txt", \'color = { 255 255 255 }\\ngraphical_culture = EuropeanGC\\n\\nparty = {\\n\\tname = "WBK_exclusive"\\n\'\n'
    '   \'\\tstart_date = 1800.1.1\\n\\tend_date = 2000.1.1\\n\\n\\tideology = reactionary\\n\\n\\teconomic_policy = world_bank_economics\\n\'\n'
    '   \'\\ttrade_policy = world_bank\\n\\treligious_policy = pluralism\\n\\tcitizenship_policy = full_citizenship\\n\\twar_policy = anti_military\\n}\\n\')\n'
    'lines[ins:ins] = ["# Warlord Era"] + add + [""]\n')
# 5 history
rep('# dominions and formables: civilized Chinese states\n',
    'wr("history/countries/WBK - World Bank.txt",\n'
    '   "capital = 2131\\nprimary_culture = british\\nreligion = protestant\\ngovernment = absolute_monarchy\\nplurality = 100\\n"\n'
    '   "nationalvalue = nv_order\\nliteracy = 1\\ncivilized = no\\nis_releasable_vassal = no\\n"\n'
    '   "set_country_flag = world_bank_off\\nset_country_flag = ghostland\\nset_country_flag = world_bank\\n"\n'
    '   + POLREF + "ruling_party = WBK_exclusive\\n" + UH + reforms([]) + \'oob = "WBK_oob.txt"\\n\')\n\n'
    '# dominions and formables: civilized Chinese states\n')
# 6 no army
rep('    homes = sorted(ps, key=lambda q: -soldiers[q])[:8] or ps\n',
    '    if tag == "WBK":\n        wr("history/units/WBK_oob.txt", "# the World Bank has no army\\n")\n        continue\n'
    '    homes = sorted(ps, key=lambda q: -soldiers[q])[:8] or ps\n')
# 7 flag + names
rep('allnew = [(t, WARLORDS[t][5]) for t in WARLORDS]', 'allnew = [("WBK", (250, 250, 250))] + [(t, WARLORDS[t][5]) for t in WARLORDS]')
rep('L += loc("PAN", "Sikh Empire")', 'L += loc("WBK", "World Bank") + loc("WBK_ADJ", "World Bank") + loc("WBK_exclusive", "Board of Governors")\nL += loc("PAN", "Sikh Empire")')
open("02_world.py", "w", encoding="utf-8").write(s)
print("patched")
