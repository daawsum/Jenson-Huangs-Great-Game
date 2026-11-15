#!/bin/bash
# rebuild stages 2-5 and validate (does NOT touch the game folder)
set -e
cd "$(dirname "$0")"
python 02_world.py | grep -E "countries at start|ruling party"
python 03a_tech.py | tail -3
python 03_gameplay.py | tail -2
python 03b_worldbank.py
python 03c_statesize.py
python 03d_focus.py
python 04b_mapstyle.py
python 04c_loadscreens.py
python 04d_title.py
python 05_package.py | tail -1
python 04_validate.py | sed -n '/tokens not seen/p;/PROBLEMS/,$p'
