"""Final verification of the water vending project pipeline."""

import os
import re
import sys


def has_cyrillic(text):
    return bool(re.search(r'[\u0400-\u04FF]', text))


def has_literal_n(text):
    return '\\n' in text


def check_file_utf8(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read()
        return True
    except UnicodeDecodeError:
        return False


def main():
    errors = []
    ok = []

    # 1. All files UTF-8
    for root in ["pipeline", "docs/pipeline"]:
        for dirs, files in os.walk(root):
            for fname in files:
                if fname.endswith((".md", ".py")):
                    path = os.path.join(root, fname)
                    if not check_file_utf8(path):
                        errors.append(f"NOT UTF-8: {path}")
                    else:
                        ok.append(path)

    # 2. No Cyrillic in estimate md files
    for root, dirs, files in os.walk("docs/pipeline/estimates"):
        for fname in files:
            if fname.endswith(".md"):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if has_cyrillic(content):
                    errors.append(f"CYRILLIC in {path}")

    # 3. No literal \n in md files
    for root, dirs, files in os.walk("docs"):
        for fname in files:
            if fname.endswith(".md"):
                path = os.path.join(root, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if has_literal_n(content):
                    errors.append(f"LITERAL \\n in {path}")

    # 4. INTEGRATION block exists
    if not os.path.exists("docs/pipeline/estimates/INTEGRATION.md"):
        errors.append("INTEGRATION.md not found")
    else:
        with open("docs/pipeline/estimates/INTEGRATION.md", "r", encoding="utf-8") as f:
            content = f.read()
        rows = content.count("| 10.")
        if rows < 15:
            errors.append(f"INTEGRATION.md has only {rows} rows, expected 15")

    # 5. SMETA_FINAL exists and has key numbers
    if not os.path.exists("docs/pipeline/consolidated/SMETA_FINAL.md"):
        errors.append("SMETA_FINAL.md not found")
    else:
        with open("docs/pipeline/consolidated/SMETA_FINAL.md", "r", encoding="utf-8") as f:
            content = f.read()
        for key in ["CAPEX всего", "OPEX в месяц", "Окупаемость"]:
            if key not in content:
                errors.append(f"SMETA_FINAL missing: {key}")

    # 6. TECH_SPEC exists
    if not os.path.exists("docs/technical/TECH_SPEC.md"):
        errors.append("TECH_SPEC.md not found")

    # 7. PRESENTATION exists
    if not os.path.exists("docs/technical/PRESENTATION.md"):
        errors.append("PRESENTATION.md not found")

    print(f"OK files: {len(ok)}")
    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  - {e}")

    if errors:
        sys.exit(1)
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()