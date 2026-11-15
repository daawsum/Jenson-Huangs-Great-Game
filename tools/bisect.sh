#!/bin/bash
# bisect.sh r m : culprit tag is known to be in tags[r::m]; keep halving until one tag is left
cd "$(dirname "$0")"
r=$1; m=$2
while [ $m -lt 256 ]; do
  m2=$((m * 2))
  bash install.sh >/dev/null
  python variant.py nounits nobank half:$r/$m2 | grep unowning
  out=$(bash t.sh "half:$r/$m2")
  echo "$out"
  if echo "$out" | grep -q MENU; then :; else r=$((r + m)); fi
  m=$m2
done
echo "culprit slice: $r/$m"
bash install.sh >/dev/null
python variant.py nounits nobank half:$r/$m | grep unowning
bash t.sh "confirm $r/$m"
