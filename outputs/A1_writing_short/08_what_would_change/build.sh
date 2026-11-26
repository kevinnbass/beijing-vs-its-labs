#!/bin/bash
# Idea 8: rebuild the page. Every quotation and hidden statement is checked against the saved copies; nothing is written if one fails.
set -euo pipefail
cd "$(dirname "$0")"
# item 8 says the saved record of Nvidia's filings shows no report for the quarter ended Oct 25, 2026: check that first
python3 -I check_filing_feed.py
# the page's numbers, ids and note names against the project's tables and folders
python3 -I check_numbers.py
python3 -I scripts/cn_doc_build.py what_would_change_base.txt --refs extra_refs.tsv --title "What Would Change" --eyebrow "China chip policy · the documents that would test it"
