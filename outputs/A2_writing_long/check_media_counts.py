#!/usr/bin/env python3
"""Check the state and Party media counts printed in the article and guidance piece."""
import csv
import re
import sys
from calendar import month_name
from datetime import date
from pathlib import Path


FAMILY = Path(__file__).resolve().parent
TABLE = FAMILY.parents[1] / "tables" / "state_media_items.tsv"
BASES = (
    FAMILY / "06_article" / "article_base.txt",
    FAMILY / "43_guidance_not_law" / "guidance_base.txt",
)
SOURCE_MARK = re.compile(r"[ \t]*\[(?:cn|ms|man|cnpol|clip)-[A-Za-z0-9-]+\]")


def main(paths=BASES):
    with TABLE.open(encoding="utf-8") as stream:
        rows = list(csv.DictReader(
            (line for line in stream if line.strip() and not line.startswith("#")),
            delimiter="\t",
        ))
    dates = [date.fromisoformat(row["date"]) for row in rows]
    first, last = min(dates), max(dates)
    period = f"{month_name[first.month]} {first.year} to {month_name[last.month]} {last.year}"
    warnings = [day for row, day in zip(rows, dates) if row["stance"] == "warns"]
    summer = sum(date(2025, 7, 31) <= day <= date(2025, 9, 24) for day in warnings)
    winter = sum(date(2025, 12, 9) <= day <= date(2026, 1, 14) for day in warnings)
    expected = (
        f"Of {len(rows)} state and Party media items on Nvidia and its chips found from {period}, "
        f"{len(warnings)} only warn about the chips, and {summer} of those date "
        "from Jul 31 to Sept 24, 2025.",
        f"Another {winter} warnings date from Dec 9, 2025 to Jan 14, 2026, "
        "in coverage of the US easing for the H200.",
    )
    for path in paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        visible = SOURCE_MARK.sub("", "\n".join(line for line in lines if not line.startswith("!!")))
        for sentence in expected:
            if visible.count(sentence) != 1:
                sys.exit(f"{path}: expected one visible occurrence of {sentence!r}")
    print(f"Media count check: {len(rows)} items from {period}, {len(warnings)} warnings, "
          f"{summer} in the summer window, {winter} in the winter window; both bases agree")


if __name__ == "__main__":
    main()
