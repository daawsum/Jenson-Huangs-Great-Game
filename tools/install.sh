#!/bin/bash
G="/d/SteamLibrary/steamapps/common/Victoria 2/mod"
cd "$(dirname "$0")/.."
rm -rf "$G/Warlord Era"; cp -r "Warlord Era" "$G/Warlord Era"; cp "Warlord Era.mod" "$G/Warlord Era.mod"; echo installed
