#!/bin/bash
# t.sh [label] : launch the installed mod, report MENU (reached frontend) or CRASH, then close the game
G="/d/SteamLibrary/steamapps/common/Victoria 2"
D="$(cygpath "$USERPROFILE")/Documents/Paradox Interactive/Victoria II/Warlord Era/logs"
taskkill //F //IM v2game.exe >/dev/null 2>&1; sleep 1
rm -f "$D/system.log" "$D/game.log" "$D/error.log"
cd "$G"
powershell -NoProfile -Command "Start-Process -FilePath '.\v2game.exe' -ArgumentList '-mod=mod/Warlord Era.mod' -WorkingDirectory '$(cygpath -w "$G")'"
res="TIMEOUT"
for i in $(seq 1 60); do
  sleep 3
  if grep -q "entering frontend" "$D/system.log" 2>/dev/null; then res="MENU after $((i*3))s"; break; fi
  if ! tasklist 2>/dev/null | grep -qi v2game; then res="CRASH after $((i*3))s at: $(tail -1 "$D/system.log" | sed 's/.*Load text *//')"; break; fi
done
sleep 2
taskkill //F //IM v2game.exe >/dev/null 2>&1
echo "[$1] $res | error.log lines: $(wc -l < "$D/error.log" 2>/dev/null)"
