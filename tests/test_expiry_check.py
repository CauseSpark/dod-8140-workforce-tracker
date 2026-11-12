from datetime import date

import pytest

from src.common import TRACKER_PATH, read_csv
from src.expiry_check import bucket_for, check_expirations, main

AS_OF = date(2026, 11, 11)


def row(emp, exp, name="Test Person", qual="Cert X"):
    return {
        "employee_id": emp,
        "name": name,
        "dcwf_code": "511",
        "qualification_name": qual,
        "expiration_date": exp,
    }


@pytest.mark.parametrize(
    "days, expected",
    [
        (-1, "EXPIRED"),
        (0, "30"),
        (30, "30"),
        (31, "60"),
        (60, "60"),
        (61, "90"),
        (90, "90"),
        (91, None),
    ],
)
def test_bucket_boundaries(days, expected):
    assert bucket_for(days) == expected


def test_blank_expiration_is_skipped():
    assert check_expirations([row("E1", "")], AS_OF) == []


def test_flags_sorted_soonest_first():
    rows = [row("E1", "2027-01-30"), row("E2", "2026-01-01"), row("E3", "2026-11-20")]
    flags = check_expirations(rows, AS_OF)
    assert [f.employee_id for f in flags] == ["E2", "E3", "E1"]
    assert [f.bucket for f in flags] == ["EXPIRED", "30", "90"]


def test_far_future_not_flagged():
    assert check_expirations([row("E1", "2028-01-01")], AS_OF) == []


def test_bad_date_raises():
    with pytest.raises(ValueError):
        check_expirations([row("E1", "12/01/2026")], AS_OF)


def test_sample_tracker_expected_flags():
    flags = check_expirations(read_csv(TRACKER_PATH), AS_OF)
    got = {(f.employee_id, f.qualification_name): f.bucket for f in flags}
    assert got == {
        ("HCS-001", "CompTIA Security+"): "EXPIRED",
        ("HCS-005", "ISACA CISM"): "EXPIRED",
        ("HCS-001", "CompTIA CySA+"): "30",
        ("HCS-002", "GIAC GCFA"): "60",
        ("HCS-003", "CompTIA PenTest+"): "90",
    }


def test_cli_strict_exit_code_and_csv(tmp_path, capsys):
    out = tmp_path / "expiry.csv"
    code = main(["--as-of", "2026-11-11", "--strict", "--csv", str(out)])
    assert code == 1
    assert "2 expired" in capsys.readouterr().out
    assert out.read_text().count("\n") == 6  # header + 5 flags


def test_cli_non_strict_returns_zero():
    assert main(["--as-of", "2026-11-11"]) == 0
