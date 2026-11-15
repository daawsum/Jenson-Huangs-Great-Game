#!/bin/bash
# rebuild stages 2-5, validate, and reinstall into the game mod folder
set -e
cd "$(dirname "$0")"
python 02_world.py | grep -E "countries at start"
python 03_gameplay.py | tail -1
python 05_package.py | tail -1
python 04_validate.py | grep -E "PROBLEMS" 
G="/d/SteamLibrary/steamapps/common/Victoria 2/mod"
rm -rf "$G/Warlord Era"
cp -r "../Warlord Era" "$G/Warlord Era"
cp "../Warlord Era.mod" "$G/Warlord Era.mod"
echo installed
