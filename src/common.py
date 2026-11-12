"""Shared helpers: file paths, CSV loading, and date parsing."""

from __future__ import annotations

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
