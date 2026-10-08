"""Verify the estimate files: encoding, language, completeness, sources and scope.

Replaces the former verify.py, verify_final.py and verify_estimates.py.
Run from the repository root: python3 pipeline/verify.py
"""

import os
import re
import sys

from calculator import BLOCKS, SCOPE, parse_block, PIPELINE_DIR

CYRILLIC = re.compile(r"[Ѐ-ӿ]")
GRANT_PROGRAMS = ["Subsidija", "Vrati se", "Kapital za razvoj", "StarTech", "Smart Start", "beginning entrepreneurs"]


def main():
    errors = []

    # 1. Estimate files: UTF-8, English only (decision 0010)
    for block in BLOCKS:
        path = os.path.join(PIPELINE_DIR, f"{block}.md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except (OSError, UnicodeDecodeError) as e:
            errors.append(f"{path}: cannot read as UTF-8 ({e})")
            continue
        if CYRILLIC.search(text):
            errors.append(f"{path}: contains Cyrillic")

    # 2. Rows: completeness, sources, classification (decision 0009)
    for block in BLOCKS:
        rows = parse_block(block)
        if not rows:
            errors.append(f"{block}: no table rows parsed")
            continue
        for key, label in (("unit_price", "unit price"), ("total", "total")):
            filled = sum(1 for r in rows if r[key].strip())
            if filled / len(rows) < 0.8:
                errors.append(f"{block}: fewer than 80% of rows have a {label}")
        for r in rows:
            source = r["source"].strip()
            if not source or "TBD" in source.upper():
                errors.append(f"{block} {r['item']}: missing source")
            if r["item"] not in SCOPE:
                errors.append(f"{block} {r['item']}: not classified in calculator.SCOPE")
    integration = parse_block("INTEGRATION")
    if len(integration) < 15:
        errors.append(f"INTEGRATION: expected 15 rows, found {len(integration)}")

    # 3. Grants block names specific programs, not placeholders
    with open(os.path.join(PIPELINE_DIR, "GRANTS_AND_SUPPORT.md"), "r", encoding="utf-8") as f:
        grants = f.read()
    if "Serbian Gov" in grants or not any(name in grants for name in GRANT_PROGRAMS):
        errors.append("GRANTS_AND_SUPPORT: names no specific programs or has placeholders")

    # 4. No literal "\n" sequences in any markdown file
    for root, _, files in os.walk("docs"):
        for fname in files:
            if fname.endswith(".md"):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8") as f:
                    if "\\n" in f.read():
                        errors.append(f"{path}: contains a literal \\n")

    if errors:
        print(f"{len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("All estimate checks passed")


if __name__ == "__main__":
    main()
