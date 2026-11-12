"""Report personnel who lack a valid foundational or residential qualification.

The tracker is compared with the SAMPLE qualification options in
data/qualification_options_sample.csv. Those options are illustrative, not the
official DoD 8140 matrix, so this report demonstrates the logic only.

Rules applied:
  * A qualification counts only if it is listed for the person's DCWF work role
    at their assigned proficiency level or higher (higher levels qualify lower).
  * A certification past its expiration date (as of the report date) does not count.
  * Residential qualification is read from the tracker's Y/N flag.

Usage:
    python -m src.role_gap_report
    python -m src.role_gap_report --as-of 2026-11-11 --csv reports/gaps.csv --strict
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

from src.common import (
    OPTIONS_PATH,
    ROLES_PATH,
    TRACKER_PATH,
    parse_date,
    proficiency_rank,
    read_csv,
)


@dataclass
class PersonStatus:
    employee_id: str
    name: str
    dcwf_code: str
    work_role_name: str
    proficiency_level: str
    foundational_met: bool
    residential_met: bool
    qualifying_option: str = ""
    gaps: list[str] = field(default_factory=list)

    @property
    def fully_qualified(self) -> bool:
        return not self.gaps


def build_option_index(options: list[dict[str, str]]) -> dict[str, list[tuple[int, str]]]:
    """Map a DCWF code to a list of (proficiency rank, lowercased qualification name)."""
    index: dict[str, list[tuple[int, str]]] = {}
    for opt in options:
        index.setdefault(opt["dcwf_code"], []).append(
            (proficiency_rank(opt["proficiency_level"]), opt["qualification_name"].lower())
        )
    return index


def qualifies(dcwf_code: str, level: str, qual_name: str, index) -> bool:
    """Return True if qual_name is listed for this role at the given level or higher."""
    needed = proficiency_rank(level)
    return any(
        rank >= needed and name == qual_name.lower()
        for rank, name in index.get(dcwf_code, [])
    )


def evaluate(
    tracker: list[dict[str, str]],
    roles: list[dict[str, str]],
    options: list[dict[str, str]],
    as_of: date,
) -> list[PersonStatus]:
    role_names = {r["dcwf_code"]: r["work_role_name"] for r in roles}
    index = build_option_index(options)

    people: "OrderedDict[str, list[dict[str, str]]]" = OrderedDict()
    for row in tracker:
        people.setdefault(row["employee_id"], []).append(row)

    results: list[PersonStatus] = []
    for emp_id, rows in people.items():
        first = rows[0]
        code, level = first["dcwf_code"], first["proficiency_level"]
        status = PersonStatus(
            employee_id=emp_id,
            name=first["name"],
            dcwf_code=code,
            work_role_name=role_names.get(code, "UNKNOWN ROLE"),
            proficiency_level=level,
            foundational_met=False,
            residential_met=any(r.get("residential_qualified", "").upper() == "Y" for r in rows),
        )

        if code not in role_names:
            status.gaps.append(f"DCWF code {code} not in sample role list")

        expired_match = False
        for r in rows:
            name = r.get("qualification_name", "")
            if not name or not qualifies(code, level, name, index):
                continue
            exp = parse_date(r.get("expiration_date"))
            if exp is not None and exp < as_of:
                expired_match = True
                continue
            status.foundational_met = True
            status.qualifying_option = name
            break

        if not status.foundational_met:
            if expired_match:
                status.gaps.append("Foundational: qualifying certification has expired")
            elif not any(r.get("qualification_name") for r in rows):
                status.gaps.append("Foundational: no qualification on record")
            else:
                status.gaps.append(
                    f"Foundational: no listed option held for {code} at {level} level or higher"
                )
        if not status.residential_met:
            status.gaps.append("Residential: not yet qualified")
        results.append(status)
    return results


def format_report(results: list[PersonStatus], as_of: date) -> str:
    lines = [
        f"DoD 8140 role gap report (SAMPLE data) as of {as_of.isoformat()}",
        "",
    ]
    for s in results:
        mark = "OK " if s.fully_qualified else "GAP"
        lines.append(
            f"[{mark}] {s.employee_id} {s.name} - {s.dcwf_code} {s.work_role_name} ({s.proficiency_level})"
        )
        if s.qualifying_option:
            lines.append(f"       foundational via: {s.qualifying_option}")
        for gap in s.gaps:
            lines.append(f"       - {gap}")
    total = len(results)
    ok = sum(s.fully_qualified for s in results)
    found = sum(s.foundational_met for s in results)
    res = sum(s.residential_met for s in results)
    pct = (100 * ok / total) if total else 0.0
    lines += [
        "",
        f"Summary: {ok}/{total} fully qualified ({pct:.0f}%) | "
        f"foundational {found}/{total} | residential {res}/{total}",
    ]
    return "\n".join(lines)


def write_csv(results: list[PersonStatus], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(PersonStatus.__dataclass_fields__) + ["fully_qualified"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for s in results:
            row = asdict(s)
            row["gaps"] = "; ".join(s.gaps)
            row["fully_qualified"] = s.fully_qualified
            writer.writerow(row)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tracker", default=TRACKER_PATH)
    parser.add_argument("--roles", default=ROLES_PATH)
    parser.add_argument("--options", default=OPTIONS_PATH)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--csv", help="Optional path to also write results as CSV")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if anyone has a gap")
    args = parser.parse_args(argv)

    results = evaluate(
        read_csv(args.tracker), read_csv(args.roles), read_csv(args.options), args.as_of
    )
    print(format_report(results, args.as_of))
    if args.csv:
        write_csv(results, args.csv)
    if args.strict and not all(s.fully_qualified for s in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
