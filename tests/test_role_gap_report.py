from datetime import date

import pytest

from src.common import OPTIONS_PATH, ROLES_PATH, TRACKER_PATH, read_csv
from src.role_gap_report import build_option_index, evaluate, main, qualifies

AS_OF = date(2026, 11, 11)

ROLES = [{"dcwf_code": "511", "work_role_name": "Cyber Defense Analyst"}]
OPTIONS = [
    {"dcwf_code": "511", "proficiency_level": "Basic", "qualification_name": "Cert B"},
    {"dcwf_code": "511", "proficiency_level": "Advanced", "qualification_name": "Cert A"},
]


def person(emp="E1", level="Intermediate", qual="Cert A", exp="", res="Y", code="511"):
    return {
        "employee_id": emp,
        "name": "Test Person",
        "dcwf_code": code,
        "proficiency_level": level,
        "qualification_name": qual,
        "expiration_date": exp,
        "residential_qualified": res,
    }


def test_higher_level_option_qualifies_lower_assignment():
    index = build_option_index(OPTIONS)
    assert qualifies("511", "Intermediate", "Cert A", index)
    assert qualifies("511", "Basic", "cert a", index)  # case-insensitive


def test_lower_level_option_does_not_qualify_higher_assignment():
    index = build_option_index(OPTIONS)
    assert not qualifies("511", "Intermediate", "Cert B", index)


def test_fully_qualified_person():
    [s] = evaluate([person()], ROLES, OPTIONS, AS_OF)
    assert s.fully_qualified and s.qualifying_option == "Cert A"


def test_expired_cert_creates_gap():
    [s] = evaluate([person(exp="2026-01-01")], ROLES, OPTIONS, AS_OF)
    assert not s.foundational_met
    assert any("expired" in g for g in s.gaps)


def test_valid_second_record_overrides_expired_first():
    rows = [person(exp="2026-01-01"), person(qual="Cert A", exp="2028-01-01")]
    [s] = evaluate(rows, ROLES, OPTIONS, AS_OF)
    assert s.foundational_met


def test_no_qualification_and_no_residential():
    [s] = evaluate([person(qual="", res="N")], ROLES, OPTIONS, AS_OF)
    assert s.gaps == [
        "Foundational: no qualification on record",
        "Residential: not yet qualified",
    ]


def test_unknown_role_code_flagged():
    [s] = evaluate([person(code="999")], ROLES, OPTIONS, AS_OF)
    assert s.work_role_name == "UNKNOWN ROLE"
    assert any("not in sample role list" in g for g in s.gaps)


def test_unknown_proficiency_level_raises():
    with pytest.raises(ValueError):
        evaluate([person(level="Expert")], ROLES, OPTIONS, AS_OF)


def test_sample_tracker_expected_results():
    results = evaluate(
        read_csv(TRACKER_PATH), read_csv(ROLES_PATH), read_csv(OPTIONS_PATH), AS_OF
    )
    by_id = {s.employee_id: s for s in results}
    assert len(results) == 8
    assert {e for e, s in by_id.items() if s.fully_qualified} == {
        "HCS-001", "HCS-002", "HCS-004", "HCS-008"
    }
    assert by_id["HCS-003"].gaps == ["Residential: not yet qualified"]
    assert "expired" in by_id["HCS-005"].gaps[0]
    assert "no qualification on record" in by_id["HCS-006"].gaps[0]
    assert "Advanced level or higher" in by_id["HCS-007"].gaps[0]


def test_cli_writes_csv_and_strict_exit(tmp_path, capsys):
    out = tmp_path / "gaps.csv"
    assert main(["--as-of", "2026-11-11", "--csv", str(out), "--strict"]) == 1
    assert "4/8 fully qualified" in capsys.readouterr().out
    assert out.read_text().count("\n") == 9  # header + 8 people
