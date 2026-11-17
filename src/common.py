"""Shared helpers: file paths, CSV reading and writing, date parsing, and common CLI options."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TRACKER_PATH = REPO_ROOT / "trackers" / "workforce_tracker.csv"
ROLES_PATH = REPO_ROOT / "data" / "dcwf_roles_sample.csv"
OPTIONS_PATH = REPO_ROOT / "data" / "qualification_options_sample.csv"

# DoD 8140 proficiency levels, lowest to highest.
PROFICIENCY_ORDER = {"Basic": 1, "Intermediate": 2, "Advanced": 3}


def read_csv(path: str | Path) -> list[dict[str, str]]:
    """Read a CSV into a list of dicts, stripping whitespace from every value."""
    with open(path, newline="", encoding="utf-8") as fh:
        return [
            {k.strip(): (v or "").strip() for k, v in row.items()}
            for row in csv.DictReader(fh)
        ]


def write_csv(path: str | Path, fieldnames: list[str], rows: list[dict]) -> None:
    """Write dict rows to a CSV, creating the parent folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def report_parser(description: str, strict_help: str) -> argparse.ArgumentParser:
    """Parser with the options both reports share: --tracker, --as-of, --csv, --strict."""
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tracker", default=TRACKER_PATH, help="Path to workforce tracker CSV")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(), help="Date to check against (YYYY-MM-DD)")
    parser.add_argument("--csv", help="Optional path to also write results as CSV")
    parser.add_argument("--strict", action="store_true", help=strict_help)
    return parser


def parse_date(value: str | None) -> date | None:
    """Parse an ISO date (YYYY-MM-DD). A blank value returns None."""
    if value is None or not value.strip():
        return None
    return date.fromisoformat(value.strip())


def proficiency_rank(level: str) -> int:
    """Return the numeric rank of a proficiency level. Raises ValueError if unknown."""
    try:
        return PROFICIENCY_ORDER[level]
    except KeyError:
        raise ValueError(
            f"Unknown proficiency level {level!r}; expected one of {list(PROFICIENCY_ORDER)}"
        ) from None
