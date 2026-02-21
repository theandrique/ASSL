#!/usr/bin/env python3
"""Basic static validation for the ASSL website."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", ROOT / "about.html"]
ATTR_PATTERN = re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']", re.IGNORECASE)
TITLE_PATTERN = re.compile(r"<title>\s*(.*?)\s*</title>", re.IGNORECASE | re.DOTALL)


def is_local_asset(ref: str) -> bool:
    return not ref.startswith(("http://", "https://", "mailto:", "tel:", "#", "javascript:", "data:", "//"))


def validate_page(page: Path) -> list[str]:
    issues: list[str] = []
    if not page.exists():
        return [f"Missing page: {page.name}"]

    html = page.read_text(encoding="utf-8", errors="ignore")

    title_match = TITLE_PATTERN.search(html)
    if not title_match or not title_match.group(1).strip():
        issues.append(f"{page.name}: missing or empty <title> tag")

    for ref in ATTR_PATTERN.findall(html):
        if not is_local_asset(ref):
            continue
        local_ref = ref.split("?", 1)[0].split("#", 1)[0].lstrip("/")
        if not local_ref:
            continue
        if not (ROOT / local_ref).exists():
            issues.append(f"{page.name}: missing local asset -> {ref}")

    return issues


def main() -> int:
    all_issues: list[str] = []
    for page in PAGES:
        all_issues.extend(validate_page(page))

    if all_issues:
        print("❌ Website validation failed:")
        for issue in all_issues:
            print(f" - {issue}")
        return 1

    print("✅ Website validation passed: pages exist, titles are set, and local asset references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
