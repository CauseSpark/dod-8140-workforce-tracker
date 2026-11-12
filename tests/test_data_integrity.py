"""Guardrails on the sample data: schema, referential integrity, and labeling."""

from src.common import OPTIONS_PATH, PROFICIENCY_ORDER, ROLES_PATH, TRACKER_PATH, parse_date, read_csv

TRACKER_COLUMNS = [
    "employee_id", "name", "team", "dcwf_code", "proficiency_level",
    "qualification_type", "qualification_name", "earned_date",
    "expiration_date", "residential_qualified",
]
QUAL_TYPES = {"Education", "Training", "Certification", "Experience"}


def test_tracker_has_expected_columns():
    assert list(read_csv(TRACKER_PATH)[0].keys()) == TRACKER_COLUMNS


def test_tracker_roles_exist_in_sample_roles():
    codes = {r["dcwf_code"] for r in read_csv(ROLES_PATH)}
    assert {r["dcwf_code"] for r in read_csv(TRACKER_PATH)} <= codes


def test_option_roles_exist_in_sample_roles():
    codes = {r["dcwf_code"] for r in read_csv(ROLES_PATH)}
    assert {o["dcwf_code"] for o in read_csv(OPTIONS_PATH)} <= codes


def test_valid_enumerations_and_dates():
    for r in read_csv(TRACKER_PATH):
        assert r["proficiency_level"] in PROFICIENCY_ORDER
        assert r["residential_qualified"] in {"Y", "N"}
        assert r["qualification_type"] in QUAL_TYPES | {""}
        earned, exp = parse_date(r["earned_date"]), parse_date(r["expiration_date"])
        if earned and exp:
            assert earned < exp, r["employee_id"]
    for o in read_csv(OPTIONS_PATH):
        assert o["proficiency_level"] in PROFICIENCY_ORDER
        assert o["qualification_type"] in QUAL_TYPES


def test_each_person_has_one_role_assignment():
    seen = {}
    for r in read_csv(TRACKER_PATH):
        key = (r["dcwf_code"], r["proficiency_level"])
        assert seen.setdefault(r["employee_id"], key) == key


def test_every_option_is_labeled_as_sample():
    for o in read_csv(OPTIONS_PATH):
        assert "ILLUSTRATIVE SAMPLE" in o["note"]


def test_roles_link_to_official_dod_source():
    for r in read_csv(ROLES_PATH):
        assert r["official_reference"].startswith("https://www.cyberworkforce.mil/")
