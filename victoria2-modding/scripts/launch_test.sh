#!/bin/bash
# Launch a Victoria 2 mod and report how far it gets. Windows, Git Bash.
#
# usage: launch_test.sh "<game dir>" "<Mod Name (the .mod file name without .mod)>" "<user_dir>" [play [row_y]] [keep]
#
#   menu test (default): start the game, wait for the main menu, report, close the game.
#   play:  also open the single-player lobby, pick the country at list row y (default 365, the
#          first row at 1600x900), press Play and report whether a game actually started.
#   keep:  leave the game running afterwards.
#
# For "play" the mod's settings must be windowed 1600x900: in
#   Documents/Paradox Interactive/Victoria II/<user_dir>/settings.txt
# set fullScreen=no, borderless=no, x=1600, y=900 (back the file up first and restore it after).
# Screenshots land next to this script as lobby.png / game.png.
HERE="$(cd "$(dirname "$0")" && pwd)"
G="$1"; MOD="$2"; UDIR="$3"; MODE="$4"; ROW="${5:-365}"
[ -z "$UDIR" ] && { sed -n '2,14p' "$0"; exit 2; }
KEEP=no; for a in "$@"; do [ "$a" = keep ] && KEEP=yes; done
DOCS="$(cygpath "$USERPROFILE")/Documents/Paradox Interactive/Victoria II/$UDIR"
PS="powershell -NoProfile -ExecutionPolicy Bypass -File $(cygpath -w "$HERE/win.ps1")"
finish() { [ "$KEEP" = yes ] || taskkill //F //IM v2game.exe >/dev/null 2>&1; taskkill //F //IM binkplay.exe >/dev/null 2>&1; }

if tasklist 2>/dev/null | grep -qi v2game; then echo "Victoria 2 is already running; close it first (it may be someone's game)."; exit 3; fi
rm -f "$DOCS/logs/system.log" "$DOCS/logs/game.log" "$DOCS/logs/error.log"
(cd "$G" && powershell -NoProfile -Command "Start-Process -FilePath '.\v2game.exe' -ArgumentList '-mod=mod/$MOD.mod' -WorkingDirectory '$(cygpath -w "$G")'")
menu=no
for i in $(seq 1 60); do
  sleep 3
  grep -q "done frontend" "$DOCS/logs/system.log" 2>/dev/null && { menu=yes; echo "MENU reached after $((i * 3))s"; break; }
  if [ $i -gt 4 ] && ! tasklist 2>/dev/null | grep -qi v2game; then
    echo "CRASH before the menu, during: $(tail -1 "$DOCS/logs/system.log" 2>/dev/null | sed 's/.*Load text *//')"; break
  fi
done
if [ $menu = no ]; then
  tasklist 2>/dev/null | grep -qi binkplay && echo "binkplay.exe is running: the intro video player may be showing an error box (is movies/game_intro.bik missing?)"
  tasklist 2>/dev/null | grep -qi v2game && echo "NO MENU after 180s but the game is still running (hung, or waiting on a dialog)"
  finish; exit 1
fi
echo "error.log lines: $(wc -l < "$DOCS/logs/error.log" 2>/dev/null || echo 0)"
if [ "$MODE" != play ]; then finish; exit 0; fi

sleep 4
$PS click 557 696 >/dev/null; sleep 6                      # Single Player
$PS click 65 "$ROW" >/dev/null; sleep 2                    # a country in the list
size=$($PS shot "$(cygpath -w "$HERE/lobby.png")" | sed -n 's/shot \([0-9]*\)x\([0-9]*\).*/\1 \2/p')
W=${size% *}; H=${size#* }
echo "lobby captured (${W}x${H}): look at lobby.png - a broken map is obvious there"
$PS click $((W - 100)) $((H - 50)) >/dev/null              # Play
started=no
for i in $(seq 1 15); do sleep 2; grep -q "Launching SINGLEPLAYER" "$DOCS/logs/game.log" 2>/dev/null && { started=yes; break; }; done
[ $started = no ] && { echo "Play did not start a game (no country selected? wrong window size?)"; finish; exit 1; }
miss=0
for i in $(seq 1 20); do
  sleep 3
  if tasklist 2>/dev/null | grep -qi v2game; then miss=0; else miss=$((miss + 1)); fi
  [ $miss -ge 2 ] && { echo "CRASH after Play (country: $(grep "Country:" "$DOCS/logs/game.log" | tail -1 | sed 's/.*Country: *//'))"; finish; exit 1; }
done
$PS shot "$(cygpath -w "$HERE/game.png")" >/dev/null
echo "IN GAME as $(grep "Country:" "$DOCS/logs/game.log" | tail -1 | sed 's/.*Country: *//') (see game.png)"
finish; exit 0
