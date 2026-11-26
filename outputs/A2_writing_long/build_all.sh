#!/bin/bash
# Rebuild the six prose pieces of this folder. Each line stops with "NOT WRITTEN" if any quotation or hidden check fails.
# Run: bash build_all.sh     (from anywhere; it changes nothing outside this folder)
set -u
cd "$(dirname "$(readlink -f "$0")")" || exit 2
B=scripts/cn_doc_build.py
rc=0
one() { ( cd "$1" && python3 -I "$B" "$2"_base.txt --refs ../extra_refs.tsv --title "$3" --eyebrow "$4" ) || rc=1; }
one 06_article article "Chip Policy Article" "China chip policy · the project's argument, as an article"
one 07_other_side other_side "The Other Side" "China chip policy · the best case against the claim"
one 43_guidance_not_law guidance "Guidance, Not Law" "China chip policy · how the pressure was applied"
one 44_two_governments two_governments "Two Governments, One Chip" "China chip policy · the H200, step by step"
one 45_companies_in_the_middle companies "Companies In The Middle" "China chip policy · the buyers' side"
one 46_what_us_curbs_did us_curbs "What US Curbs Did" "China chip policy · the push from Washington"
exit $rc
