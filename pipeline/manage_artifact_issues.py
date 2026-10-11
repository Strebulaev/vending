#!/usr/bin/env python3
"""Idempotent GitHub issue creation/listing for the five pilot artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config/artifact-issues.json"


def run_gh(args: list[str]) -> str:
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI `gh` is not installed or not on PATH")
    result = subprocess.run(
        ["gh", *args], cwd=ROOT, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def repo_arg(repository: str) -> list[str]:
    return ["--repo", repository]


def list_issues(repository: str) -> list[dict]:
    raw = run_gh(["issue", "list", *repo_arg(repository), "--state", "all", "--limit", "1000", "--json", "number,title,state,url"])
    return json.loads(raw)


def create_missing() -> None:
    manifest = load_manifest()
    repository = manifest["repository"]
    existing = {item["title"]: item for item in list_issues(repository)}
    for spec in manifest["issues"]:
        title = spec["title"]
        if title in existing:
            issue = existing[title]
            print(f"EXISTS  #{issue['number']} [{issue['state']}] {title} — {issue['url']}")
            continue
        body_path = ROOT / spec["body_file"]
        if not body_path.is_file():
            raise RuntimeError(f"Issue body not found: {spec['body_file']}")
        output = run_gh([
            "issue", "create", *repo_arg(repository), "--title", title,
            "--body-file", str(body_path),
        ])
        print(f"CREATED {title} — {output.strip()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "create"), help="list tracked issues or create missing ones")
    args = parser.parse_args()
    try:
        manifest = load_manifest()
        repository = manifest["repository"]
        if args.command == "list":
            by_title = {item["title"]: item for item in list_issues(repository)}
            for spec in manifest["issues"]:
                issue = by_title.get(spec["title"])
                if issue:
                    print(f"#{issue['number']} [{issue['state']}] {spec['title']} — {issue['url']}")
                else:
                    print(f"MISSING  {spec['title']}")
        else:
            create_missing()
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
