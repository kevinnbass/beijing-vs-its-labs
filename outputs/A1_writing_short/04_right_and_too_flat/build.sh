#!/bin/bash
# Idea 4: rebuild the sheet. Every quotation and hidden statement is checked against the saved copies; nothing is written if one fails.
set -euo pipefail
cd "$(dirname "$0")"
python3 -I scripts/cn_doc_build.py right_too_flat_base.txt --refs extra_refs.tsv --title "Right And Too Flat" --eyebrow "China chip policy · Palmer Luckey's clip against the record"
