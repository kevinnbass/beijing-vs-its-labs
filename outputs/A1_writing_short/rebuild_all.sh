#!/bin/bash
# Rebuild the five ideas of A1_writing_short and write build_log.txt (the check lines DONE.md quotes).
# Exit 1 while any build or any look check fails. After a text changes: render that page again, open every
# screenshot, record the look (render_and_look.py --looked), then run this again.
# Nothing is rendered here: the four look checks only read the records render_and_look.py already holds.
cd "$(dirname "$0")"
AR=argument/argument_refs.tsv
RL="python3 scripts/render_and_look.py"
fail=0
run() { echo "== $1: $2"; shift; shift; "$@"; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || fail=1; }
{
echo "== date"; date -u '+%Y-%m-%d %H:%M UTC'
run "core copies" "python3 -I check_core_copies.py" python3 -I check_core_copies.py
run "idea 3" "python3 -I 03_thread/make_thread_plain.py" python3 -I 03_thread/make_thread_plain.py
run "idea 4" "bash 04_right_and_too_flat/build.sh" bash 04_right_and_too_flat/build.sh
run "idea 5" "python3 -I 05_questions_and_answers/build.py" python3 -I 05_questions_and_answers/build.py
run "idea 8" "bash 08_what_would_change/build.sh" bash 08_what_would_change/build.sh
# round 10 (Nov 25, 2026): A1_SKIP_33="<reason>" leaves idea 33 as it is (a round told to rebuild only some items); unset, it is rebuilt
if [ -n "${A1_SKIP_33:-}" ]; then echo "== idea 33: not rebuilt: $A1_SKIP_33"
else run "idea 33" "python3 -I 33_timeline_plain_text/gen_timeline.py" python3 -I 33_timeline_plain_text/gen_timeline.py; fi
echo "== look checks (render_and_look.py --check; exit 0 required)"
$RL --check 03_thread/thread.html --with 03_thread/thread_base.txt $AR; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || fail=1
$RL --check 04_right_and_too_flat/right_too_flat.html --with 04_right_and_too_flat/right_too_flat_base.txt 04_right_and_too_flat/extra_refs.tsv $AR; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || fail=1
$RL --check 05_questions_and_answers/questions_answers.html --with 05_questions_and_answers/questions_answers_base.txt 05_questions_and_answers/extra_refs.tsv $AR; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || fail=1
$RL --check 08_what_would_change/what_would_change.html --with 08_what_would_change/what_would_change_base.txt 08_what_would_change/extra_refs.tsv $AR; rc=$?; echo "exit=$rc"; [ $rc -eq 0 ] || fail=1
echo "== result"; [ $fail -eq 0 ] && echo "all builds and look checks passed" || echo "FAILED: see the exit lines above"
} > build_log.txt 2>&1
tail -1 build_log.txt
exit $fail
