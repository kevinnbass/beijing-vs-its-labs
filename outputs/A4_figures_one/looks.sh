#!/bin/bash
# Render every page and image of this folder with scripts/render_and_look.py, or record or check the looks.
#   bash looks.sh render            render each (prints the screenshots to open)
#   bash looks.sh check             exit 0 only if every page and image has a recorded look of its present bytes
#   bash looks.sh looked NAME N "what the N screenshots showed"    record the look of the one file whose path ends in NAME
#   bash looks.sh render NAME       render only the file whose path contains NAME
# Each line below: the file, then every file it is built from (all after ONE --with).
set -u
PY=python3; RAL=scripts/render_and_look.py
D=outputs/A4_figures_one
FIG=figure/beijing_vs_labs_top.png
TB=tables
HT=$TB/house_licence_table.tsv     # Washington's table of licence applications: the card, the funnel and the brief sum it
SM=$TB/state_media_items.tsv       # the state-media items: the six sentences and the brief count its warnings
items() { cat <<LIST
$D/09_card/card.html|$D/09_card/build.py $D/09_card/quotes.tsv $D/h200_funnel.tsv $D/a4lib.py $HT
$D/09_card/card.png|$D/09_card/card.html $D/09_card/build.py $D/09_card/quotes.tsv $D/h200_funnel.tsv $D/a4lib.py $HT
$D/11_h200_funnel/funnel.html|$D/11_h200_funnel/build.py $D/11_h200_funnel/quotes.tsv $D/h200_funnel.tsv $D/a4lib.py $HT
$D/11_h200_funnel/funnel.png|$D/11_h200_funnel/funnel.html $D/11_h200_funnel/build.py $D/11_h200_funnel/quotes.tsv $D/h200_funnel.tsv $D/a4lib.py $HT
$D/14_nvidia_share/share.html|$D/14_nvidia_share/build.py $D/14_nvidia_share/quotes.tsv $D/14_nvidia_share/share.tsv $D/14_nvidia_share/trendforce.tsv $D/a4lib.py
$D/14_nvidia_share/share.png|$D/14_nvidia_share/share.html $D/14_nvidia_share/build.py $D/14_nvidia_share/quotes.tsv $D/14_nvidia_share/share.tsv $D/14_nvidia_share/trendforce.tsv $D/a4lib.py
$D/15_six_sentences/six_sentences.html|$D/15_six_sentences/build.py $D/15_six_sentences/quotes.tsv $D/15_six_sentences/sentences.tsv $D/a4lib.py $SM
$D/15_six_sentences/six_sentences.png|$D/15_six_sentences/six_sentences.html $D/15_six_sentences/build.py $D/15_six_sentences/quotes.tsv $D/15_six_sentences/sentences.tsv $D/a4lib.py $SM
$D/21_brief/brief.html|$D/21_brief/build.py $D/21_brief/quotes.tsv $D/21_brief/brief.txt $D/a4lib.py $FIG $HT $SM
$D/21_brief/brief_A4.png|$D/21_brief/brief_A4.pdf $D/21_brief/brief.html $D/21_brief/build.py $D/21_brief/quotes.tsv $D/21_brief/brief.txt $D/a4lib.py $FIG $HT $SM
$D/21_brief/brief_Letter.png|$D/21_brief/brief_Letter.pdf $D/21_brief/brief.html $D/21_brief/build.py $D/21_brief/quotes.tsv $D/21_brief/brief.txt $D/a4lib.py $FIG $HT $SM
LIST
}
mode=${1:-check}; only=${2:-}; rc=0
while IFS='|' read -r f deps; do
  if [ "$mode" = looked ]; then [[ "$f" == *"/$only" ]] || continue; elif [ -n "$only" ] && [[ "$f" != *"$only"* ]]; then continue; fi
  case "$mode" in
    render) if [[ "$f" == *.html ]]; then "$PY" "$RAL" "$f" --with $deps --widths 1280,390 || rc=1; else "$PY" "$RAL" "$f" --with $deps || rc=1; fi ;;
    check)  "$PY" "$RAL" --check "$f" --with $deps || rc=1 ;;
    looked) "$PY" "$RAL" --looked "$f" --with $deps --saw "$3" --note "$4" || rc=1 ;;
    *) echo "mode: render, looked or check"; exit 2 ;;
  esac
done < <(items)
exit $rc
