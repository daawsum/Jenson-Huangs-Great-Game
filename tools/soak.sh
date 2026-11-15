#!/bin/bash
# soak.sh <row y> <stop regex> [max seconds]
# Start a game from the lobby (country at list row y), then keep it running until game.log shows a
# line matching <stop regex> (e.g. "March, 1836"). Unpauses and dismisses pop-ups only when the
# date has stopped moving. Leaves the game running and paused-or-not; the caller closes it.
cd "$(dirname "$0")"
ROW=${1:-479}; STOP=${2:-"February, 1836"}; MAX=${3:-240}
G="/d/SteamLibrary/steamapps/common/Victoria 2"
U="$(cygpath "$USERPROFILE")/Documents/Paradox Interactive/Victoria II/WarlordEra"
P="powershell -NoProfile -ExecutionPolicy Bypass -File win.ps1"
taskkill //F //IM v2game.exe >/dev/null 2>&1; sleep 1
rm -f "$U/logs/system.log" "$U/logs/game.log" "$U/logs/error.log"
(cd "$G" && powershell -NoProfile -Command "Start-Process -FilePath '.\v2game.exe' -ArgumentList '-mod=mod/Warlord Era.mod' -WorkingDirectory '$(cygpath -w "$G")'")
for i in $(seq 1 60); do sleep 3; grep -q "done frontend" "$U/logs/system.log" 2>/dev/null && break; done
sleep 4
$P click 557 696 >/dev/null; sleep 6
$P click 65 $ROW >/dev/null; sleep 2
size=$($P shot "$(cygpath -w "$PWD/work/soak_lobby.png")" | sed 's/shot \([0-9]*\)x\([0-9]*\).*/\1 \2/')
W=${size% *}; H=${size#* }
$P click $((W - 100)) $((H - 50)) >/dev/null
for i in $(seq 1 20); do sleep 3; grep -q "Launching SINGLEPLAYER" "$U/logs/game.log" 2>/dev/null && break; done
sleep 25
$P key "{ADD}{ADD}{ADD}{ADD}" >/dev/null
last=""; t=0
while [ $t -lt $MAX ]; do
  tasklist 2>/dev/null | grep -qi v2game || { echo "GAME EXITED at: $(tail -1 "$U/logs/game.log" | cut -c25-90)"; exit 1; }
  grep -qE "$STOP" "$U/logs/game.log" 2>/dev/null && { echo "REACHED: $(grep -E "$STOP" "$U/logs/game.log" | head -1 | cut -c25-60)"; exit 0; }
  cur=$(tail -1 "$U/logs/game.log" | cut -c25-45)
  if [ "$cur" = "$last" ]; then
    $P click $((W / 2 - 5)) 664 >/dev/null; sleep 1      # dismiss an event pop-up if one is up
    $P key " " >/dev/null                                 # and toggle pause
  fi
  last="$cur"; sleep 6; t=$((t + 7))
done
echo "TIMEOUT at: $(tail -1 "$U/logs/game.log" | cut -c25-90)"
exit 2
