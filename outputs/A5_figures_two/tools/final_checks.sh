#!/bin/bash
# Final checks for the five figures in this folder. Reads only; prints each check's own output line and exit code.
# Run: bash tools/final_checks.sh    (from anywhere)
set -u
A5="$(cd "$(dirname "$0")/.." && pwd)"
NV=.
PY=python3
R=$NV/scripts/render_and_look.py
ARG=$NV/research/cn_chip_policy_20261120/argument
TB=$NV/research/cn_chip_policy_20261120/tables
fail=0
echo "checked at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
for pair in "12_who_inside_beijing who_inside_beijing" "13_paper_against_practice paper_against_practice" "16_micron_and_nvidia micron_and_nvidia" "17_ladder_of_evidence ladder_of_evidence" "19_us_side_steps us_side_steps"; do
  set -- $pair; d=$A5/$1; n=$2
  echo "== $1"
  out=$(python3 -I $NV/scripts/cn_has.py $d/quotes.tsv); rc=$?; echo "cn_has.py quotes.tsv: $out | exit $rc"; [ $rc -ne 0 ] && fail=1
  # round 4: each look also depends on the project tables (and, for 17, the argument files) its build reads
  case "$n" in
    who_inside_beijing) extra="$TB/state_media_items.tsv $TB/provinces_31.tsv $TB/chip_evaluations.tsv" ;;
    paper_against_practice) extra="$TB/provinces_31.tsv" ;;
    micron_and_nvidia) extra="$TB/state_media_items.tsv" ;;
    ladder_of_evidence) extra="$ARG/argument_refs.tsv $ARG/argument_base.txt $TB/state_media_items.tsv" ;;
    us_side_steps) extra="$TB/house_licence_table.tsv" ;;
  esac
  out=$($PY $R --check $d/$n.html --with $d/data.txt $d/build.py $A5/common.py $d/quotes.tsv $extra); rc=$?; echo "look --check $n.html: ${out%% |*} | exit $rc"; [ $rc -ne 0 ] && fail=1
  out=$($PY $R --check $d/$n.png --with $d/$n.html $d/data.txt $d/build.py $A5/common.py $d/quotes.tsv $extra); rc=$?; echo "look --check $n.png: ${out%% |*} | exit $rc"; [ $rc -ne 0 ] && fail=1
done
echo "== all: $([ $fail -eq 0 ] && echo every check passed || echo SOMETHING FAILED)"
exit $fail
