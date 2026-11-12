"""Flag certifications that are expired or that expire within 30, 60, or 90 days.

Usage:
    python -m src.expiry_check                       # as of today
    python -m src.expiry_check --as-of 2026-11-11    # repeatable run on a fixed date
    python -m src.expiry_check --csv reports/expiry.csv --strict
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from src.common import TRACKER_PATH, parse_date, read_csv

WINDOWS = (30, 60, 90)


@dataclass(frozen=True)
class ExpiryFlag:
    employee_id: str
    name: str
    dcwf_code: str
    qualification_name: str
    expiration_date: str
    days_remaining: int
    bucket: str  # "EXPIRED", "30", "60", or "90"


def bucket_for(days_remaining: int) -> str | None:
    """Map days remaining to the smallest window it falls in, or None if beyond 90."""
    if days_remaining < 0:
        return "EXPIRED"
    for window in WINDOWS:
        if days_remaining <= window:
            return str(window)
    return None


def check_expirations(rows: list[dict[str, str]], as_of: date) -> list[ExpiryFlag]:
    """Return a flag for every row whose expiration date is past or within 90 days.

    Rows without an expiration date are skipped. This covers degrees and records
    with no qualification.
    """
    flags: list[ExpiryFlag] = []
    for row in rows:
        exp = parse_date(row.get("expiration_date"))
        if exp is None:
            continue
        days = (exp - as_of).days
        bucket = bucket_for(days)
        if bucket is None:
            continue
        flags.append(
            ExpiryFlag(
                employee_id=row["employee_id"],
                name=row["name"],
                dcwf_code=row["dcwf_code"],
                qualification_name=row["qualification_name"],
                expiration_date=exp.isoformat(),
                days_remaining=days,
                bucket=bucket,
            )
        )
    flags.sort(key=lambda f: (f.days_remaining, f.employee_id))
    return flags


def format_table(flags: list[ExpiryFlag], as_of: date) -> str:
    lines = [f"Certification expiry check as of {as_of.isoformat()}"]
    if not flags:
        lines.append("No certifications expired or expiring within 90 days.")
        return "\n".join(lines)
    header = f"{'BUCKET':<8} {'DAYS':>5}  {'EMPLOYEE':<9} {'NAME':<18} {'ROLE':<5} {'QUALIFICATION':<20} EXPIRES"
    lines += [header, "-" * len(header)]
    for f in flags:
        label = "EXPIRED" if f.bucket == "EXPIRED" else f"<={f.bucket}d"
        lines.append(
            f"{label:<8} {f.days_remaining:>5}  {f.employee_id:<9} {f.name:<18} "
            f"{f.dcwf_code:<5} {f.qualification_name:<20} {f.expiration_date}"
        )
    counts = {b: sum(1 for f in flags if f.bucket == b) for b in ("EXPIRED", "30", "60", "90")}
    lines.append("")
    lines.append(
        f"Summary: {counts['EXPIRED']} expired, {counts['30']} within 30d, "
        f"{counts['60']} within 31-60d, {counts['90']} within 61-90d"
    )
    return "\n".join(lines)


def write_csv(flags: list[ExpiryFlag], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(ExpiryFlag.__dataclass_fields__))
        writer.writeheader()
        for f in flags:
            writer.writerow(asdict(f))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tracker", default=TRACKER_PATH, help="Path to workforce tracker CSV")
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today(), help="Date to check against (YYYY-MM-DD)")
    parser.add_argument("--csv", help="Optional path to also write results as CSV")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any certification is already expired")
    args = parser.parse_args(argv)

    flags = check_expirations(read_csv(args.tracker), args.as_of)
    print(format_table(flags, args.as_of))
    if args.csv:
        write_csv(flags, args.csv)
    if args.strict and any(f.bucket == "EXPIRED" for f in flags):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
