# dod-8140-workforce-tracker

[![tests](https://github.com/CauseSpark/dod-8140-workforce-tracker/actions/workflows/tests.yml/badge.svg)](https://github.com/CauseSpark/dod-8140-workforce-tracker/actions/workflows/tests.yml)

A small Python toolkit for tracking a cyber workforce against **DoD Manual 8140.03**.
It flags certifications that are about to expire and shows which people have a
qualification gap for their assigned DCWF work role. All personnel and the company
are **fictional**, and the qualification data is a **small illustrative sample**.

> ⚠️ **This is a portfolio project. It is not the official DoD 8140 qualification matrix, it is not
> endorsed by DoD or DoW, and it is not a compliance tool.** See the [Disclaimer](#disclaimer).

## Purpose

This repo shows how a GRC analyst might automate two recurring 8140 tasks:

1. **Certification expiry monitoring.** Catch lapses before a certification stops
   counting toward someone's foundational qualification.
2. **Work-role gap analysis.** Compare each person's assigned DCWF work role and
   proficiency level with the qualifications they hold, and report the gaps.

## Current DoD 8140 status (checked November 11, 2026)

| Item | Status |
|---|---|
| Governing issuance | **DoDM 8140.03**, *Cyberspace Workforce Qualification and Management Program*, signed **Feb 15, 2023**. It cancelled DoD 8570.01-M and is still the current issuance. |
| Qualification matrix | **DoD 8140 Foundational Qualification Matrix V2.1, effective Sept 19, 2025.** The official qualification-matrices page lists it as current and V2.0 as archived. |
| Phased deadlines | Cybersecurity element (foundational): Feb 15, 2025. IT, cyber effects, cyber (intelligence), and cyber enabler elements: Feb 15, 2026. Residential for the remaining elements: Feb 15, 2027. |

The matrix is updated periodically, so confirm the version on the official page
before you rely on it. Some official pages now carry "DoW CIO" branding.

**Official sources:**
- DoD 8140 Program: <https://www.cyberworkforce.mil/DoD-8140/>
- DoD 8140 Qualification Matrices: <https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices>
- DoDM 8140.03 (PDF): <https://www.esd.whs.mil/Portals/54/Documents/DD/issuances/dodm/814003p.PDF>
- Implementation timeline (PDF): <https://dodcio.defense.gov/Portals/0/Documents/Cyber/DoD8140-ImplementationTimeline.pdf>

For a plain-language background, see [`docs/overview.md`](docs/overview.md). It covers
8570 → 8140, the work-role approach, and foundational vs. residential qualification.

## Quick start

Requires Python 3.10+. The tools use only the standard library; pytest is needed only for the tests.

```bash
git clone https://github.com/CauseSpark/dod-8140-workforce-tracker.git
cd dod-8140-workforce-tracker
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Certifications expired or expiring within 30 / 60 / 90 days
python -m src.expiry_check --as-of 2026-11-11

# Who has a foundational or residential qualification gap
python -m src.role_gap_report --as-of 2026-11-11

# Export CSVs; --strict exits 1 if there is a finding (useful in CI)
python -m src.expiry_check --csv reports/expiry.csv --strict
python -m src.role_gap_report --csv reports/gaps.csv --strict

# Tests
python -m pytest -v
```

Leave out `--as-of` to run against today's date.

### Sample output (`role_gap_report`, abridged)

```
[OK ] HCS-001 Avery Quill - 511 Cyber Defense Analyst (Intermediate)
       foundational via: CompTIA CySA+
[GAP] HCS-005 Emery Faircloth - 722 Information Systems Security Manager (Advanced)
       - Foundational: qualifying certification has expired
[GAP] HCS-007 Gray Holloway - 511 Cyber Defense Analyst (Advanced)
       - Foundational: no listed option held for 511 at Advanced level or higher

Summary: 4/8 fully qualified (50%) | foundational 5/8 | residential 6/8
```

## Repository layout

```
data/dcwf_roles_sample.csv              6 SAMPLE DCWF work roles (codes + names, linked to the official source)
data/qualification_options_sample.csv   ILLUSTRATIVE options per role/level; not the official matrix
trackers/workforce_tracker.csv          Fictional personnel at "Harborlight Cyber Solutions"
src/expiry_check.py                     30/60/90-day and expired certification flags
src/role_gap_report.py                  Foundational + residential gap analysis
src/common.py                           CSV loading, date parsing, proficiency ranking
tests/                                  pytest suite (logic, boundaries, CLI, data integrity)
docs/overview.md                        DoD 8140 background
.github/workflows/tests.yml             CI on Python 3.10-3.12
```

## How the gap logic works

- Each person has a single assigned `dcwf_code` and `proficiency_level` (Basic / Intermediate / Advanced).
- A held qualification counts toward the **foundational** requirement only if it is listed for that work role
  at the assigned level **or higher**, because higher-level options satisfy lower levels.
- A certification past its `expiration_date` does not count.
- **Residential** qualification is a Y/N flag that the organization maintains.
- Unknown DCWF codes and unknown proficiency levels are reported or rejected; they are not ignored.

## What this demonstrates

- **GRC domain knowledge:** the DoDM 8140.03 role-based model, DCWF work roles, proficiency levels,
  foundational vs. residential qualification, and why a lapsed certification is a compliance gap.
- **Automating compliance checks:** repeatable, date-pinned reports with CSV export and
  CI-friendly exit codes (`--strict`).
- **Testing discipline:** boundary tests (exactly 30, 31, 60, and 90 days), edge cases (blank dates,
  bad formats, unknown roles), CLI tests, and data-integrity tests. One integrity test requires every
  sample option to be labeled as illustrative.
- **Source discipline:** links to authoritative sources instead of copying them, with the policy and matrix
  versions stated and dated.
- **Engineering hygiene:** standard library only, small focused commits, GitHub Actions CI.

## Disclaimer

- **Fictional data.** "Harborlight Cyber Solutions" and every person in `trackers/` are made up.
  Any resemblance to real people, organizations, or units is coincidental. The repo contains no real
  personnel, unit, or mission information.
- **Not the official matrix.** `data/` holds a **small sample subset** of DCWF work roles and
  **illustrative** qualification options chosen for demonstration. They may not match the official
  DoD 8140 Qualification Matrix. Always use the [official matrix](https://www.cyber.mil/dod-workforce-innovation-directorate/dod8140/qualification-matrices)
  for real qualification decisions.
- **No official status.** This project is not affiliated with, endorsed by, or certified by the
  Department of Defense / Department of War, DoD CIO, DISA, or any certification body. It does not
  determine anyone's qualification status.
- Provided "as is" under the [MIT License](LICENSE).

## Author

Peyton Seay ([@CauseSpark](https://github.com/CauseSpark)). Cyber network defender transitioning into GRC.
