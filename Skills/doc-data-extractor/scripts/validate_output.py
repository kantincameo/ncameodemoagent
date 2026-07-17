#!/usr/bin/env python3
"""
validate_output.py

Validates that extracted JSON conforms to the fixed customer-record
output schema defined in SKILL.md before it is returned to the user.

IMPORTANT: the expected output format for multiple records is NOT a
JSON array. It is multiple standalone JSON objects separated by commas,
e.g.:  {...}, {...}, {...}
This script parses that format by wrapping it in [ ] internally just
for validation purposes -- the actual response to the user must NOT
have those brackets.

Usage:
    python3 validate_output.py '<json-text>'
    python3 validate_output.py --file <path-to-text-file>

Exit codes:
    0 -> valid
    1 -> invalid (details printed to stderr)

The schema is intentionally duplicated here (not imported from SKILL.md)
so this script has zero dependencies and stays runnable standalone.
Update FIELD_TYPES below whenever the schema in SKILL.md changes.
"""

import sys
import json

# Keep this in sync with the "Output Schema" section in SKILL.md.
# Order matters -- it defines the expected key order.
FIELD_TYPES = {
    "businessId": str,
    "customerId": str,
    "externalCustomerId": str,
    "firstName": str,
    "lastName": str,
    "email": str,
    "phone": str,
    "dob": str,
    "gender": str,
    "address": str,
    "primaryLocationId": str,
    "joinedDate": str,
    "lastVisitDate": str,
    "totalVisits": (int, float),
    "totalSpend": (int, float),
    "lifetimeValue": (int, float),
    "activeMembershipId": str,
    "activeMembershipTier": str,
    "activePackageIds": list,
    "tags": list,
    "preferredContactMethod": str,
    "marketingOptInEmail": bool,
    "marketingOptInSms": bool,
    "customAttributes": dict,
}

REQUIRED_FIELDS = list(FIELD_TYPES.keys())

EMPTY_VALUE_HINT = {
    str: '""',
    bool: "false",
    list: "[]",
    dict: "{}",
    (int, float): "0",
}


def type_hint_for(field: str) -> str:
    t = FIELD_TYPES[field]
    return EMPTY_VALUE_HINT.get(t, str(t))


def validate_record(record: dict, index=None) -> list:
    errors = []
    label = f"record[{index}]" if index is not None else "record"

    if not isinstance(record, dict):
        return [f"{label}: expected a JSON object, got {type(record).__name__}"]

    record_keys = list(record.keys())
    if record_keys != REQUIRED_FIELDS:
        missing = [f for f in REQUIRED_FIELDS if f not in record]
        extra = [f for f in record_keys if f not in REQUIRED_FIELDS]
        if missing:
            errors.append(f"{label}: missing required field(s): {missing}")
        if extra:
            errors.append(f"{label}: unexpected extra field(s): {extra}")
        if not missing and not extra and record_keys != REQUIRED_FIELDS:
            errors.append(f"{label}: field order does not match schema order")

    for field, expected_type in FIELD_TYPES.items():
        if field not in record:
            continue
        value = record[field]

        if value is None:
            hint = type_hint_for(field)
            errors.append(f"{label}.{field}: is null — use {hint} instead (never null)")
            continue

        # bool is a subclass of int in Python, so check bool fields strictly
        # and exclude bool from matching int/float-typed fields.
        if expected_type is bool:
            if not isinstance(value, bool):
                errors.append(f"{label}.{field}: expected boolean (true/false), got {type(value).__name__}")
        elif expected_type == (int, float):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"{label}.{field}: expected number, got {type(value).__name__}")
        elif expected_type is str:
            if not isinstance(value, str):
                errors.append(f"{label}.{field}: expected string, got {type(value).__name__}")
        elif expected_type is list:
            if not isinstance(value, list):
                errors.append(f"{label}.{field}: expected array, got {type(value).__name__}")
        elif expected_type is dict:
            if not isinstance(value, dict):
                errors.append(f"{label}.{field}: expected object, got {type(value).__name__}")

    return errors


def parse_comma_separated_objects(raw: str):
    """
    Parses the expected output format: one or more JSON objects
    separated by commas, WITHOUT an outer [ ] array wrapper.
    Also tolerates a real JSON array or a single object, for
    flexibility when checking intermediate drafts.
    """
    stripped = raw.strip()

    # Case 1: already a single object or a real array -- parse directly.
    try:
        data = json.loads(stripped)
        if isinstance(data, (dict, list)):
            return data
    except json.JSONDecodeError:
        pass

    # Case 2: comma-separated objects without brackets -- wrap and parse.
    try:
        data = json.loads(f"[{stripped}]")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not parse as JSON object(s): {e}")


def validate(data) -> list:
    errors = []

    if isinstance(data, list):
        if len(data) == 0:
            errors.append("No JSON object(s) found — expected at least one record.")
        for i, record in enumerate(data):
            errors.extend(validate_record(record, i))
    elif isinstance(data, dict):
        errors.extend(validate_record(data))
    else:
        errors.append(f"Top-level content must be object(s), got {type(data).__name__}")

    return errors


def check_no_array_brackets(raw: str, record_count: int):
    """Warn if multiple records were wrapped in [ ] -- not allowed per spec."""
    stripped = raw.strip()
    if record_count > 1 and stripped.startswith("[") and stripped.endswith("]"):
        return ("Output uses [ ] array brackets for multiple records — "
                "this is NOT allowed. Multiple records must be comma-separated "
                "standalone objects: {...}, {...}, {...} with NO surrounding brackets.")
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_output.py '<json-text>'  OR  "
              "python3 validate_output.py --file <path>", file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] == "--file":
        if len(sys.argv) != 3:
            print("Usage: python3 validate_output.py --file <path>", file=sys.stderr)
            sys.exit(1)
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raw = sys.argv[1]

    try:
        data = parse_comma_separated_objects(raw)
    except ValueError as e:
        print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)

    record_count = len(data) if isinstance(data, list) else 1
    bracket_error = check_no_array_brackets(raw, record_count)

    errors = validate(data)
    if bracket_error:
        errors.insert(0, bracket_error)

    if errors:
        print("INVALID — schema violations found:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    print(f"VALID: {record_count} record(s) conform to schema.")
    sys.exit(0)


if __name__ == "__main__":
    main()
