#!/bin/bash
# lobby.sh <name> [play] : launch the installed mod windowed, open the single player lobby,
# save tools/work/<name>.png, optionally press Play and save <name>_game.png, then close the game.
cd "$(dirname "$0")"
G="/d/SteamLibrary/steamapps/common/Victoria 2"
U="$(cygpath "$USERPROFILE")/Documents/Paradox Interactive/Victoria II/WarlordEra"
P="powershell -NoProfile -ExecutionPolicy Bypass -File win.ps1"
taskkill //F //IM v2game.exe >/dev/null 2>&1; sleep 1
rm -f "$U/logs/system.log" "$U/logs/game.log" "$U/logs/error.log"
(cd "$G" && powershell -NoProfile -Command "Start-Process -FilePath '.\v2game.exe' -ArgumentList '-mod=mod/Warlord Era.mod' -WorkingDirectory '$(cygpath -w "$G")'")
ok=0
for i in $(seq 1 80); do
  sleep 3
  grep -q "done frontend" "$U/logs/system.log" 2>/dev/null && { ok=1; break; }
  if [ $i -gt 5 ] && ! tasklist 2>/dev/null | grep -qi v2game; then break; fi
done
if [ $ok = 0 ]; then echo "[$1] did not reach menu: $(tail -1 "$U/logs/system.log")"; taskkill //F //IM v2game.exe >/dev/null 2>&1; exit 1; fi
sleep 4
$P click 557 696 >/dev/null; sleep 6
$P shot "$(cygpath -w "$PWD/work/$1.png")" >/dev/null
echo "[$1] lobby captured"
if [ "$2" = "play" ]; then
  $P click 65 365 >/dev/null; sleep 2
  $P click 1500 850 >/dev/null
  alive=1
  miss=0
  for i in $(seq 1 25); do sleep 3; if tasklist 2>/dev/null | grep -qi v2game; then miss=0; else miss=$((miss+1)); fi; [ $miss -ge 2 ] && { alive=0; break; }; done
  if [ $alive = 1 ]; then
    $P shot "$(cygpath -w "$PWD/work/$1_game.png")" >/dev/null; echo "[$1] IN GAME after play (captured)"
  else
    echo "[$1] CRASH after play: $(tail -1 "$U/logs/game.log" | cut -c1-100)"
  fi
fi
[ "$3" = "keep" ] || taskkill //F //IM v2game.exe >/dev/null 2>&1
