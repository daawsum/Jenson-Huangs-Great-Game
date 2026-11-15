#!/bin/bash
# launch Victoria 2 with the mod, wait, and report whether it survived start-up
G="/d/SteamLibrary/steamapps/common/Victoria 2"
D="$(cygpath "$USERPROFILE")/Documents/Paradox Interactive/Victoria II/Warlord Era/logs"
WAIT=${1:-90}
cd "$G"
powershell -NoProfile -Command "Start-Process -FilePath '.\v2game.exe' -ArgumentList '-mod=mod/Warlord Era.mod' -WorkingDirectory '$(cygpath -w "$G")'"
alive=1
for i in $(seq 1 $((WAIT / 5))); do
  sleep 5
  if ! tasklist 2>/dev/null | grep -qi v2game; then echo "PROCESS EXITED after about $((i * 5))s"; alive=0; break; fi
done
[ $alive = 1 ] && echo "STILL RUNNING after ${WAIT}s"
echo "--- system.log tail"; tail -4 "$D/system.log"
echo "--- game.log"; tail -5 "$D/game.log"
echo "--- error.log lines: $(wc -l < "$D/error.log")"
awk '{$1=""; print}' "$D/error.log" | cut -c1-110 | sort | uniq -c | sort -rn | head -${2:-40}
