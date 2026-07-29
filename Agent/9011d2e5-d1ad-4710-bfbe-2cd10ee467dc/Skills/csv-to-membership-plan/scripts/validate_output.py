#!/usr/bin/env python3
"""
Validates that a Membership Knowledge Builder output file matches the fixed target schema
structurally (keys present, types roughly right, memberships<->membershipKnowledge joinable,
and that the four mandatory fields per membership are present).
This does NOT judge writing quality/content — only structure.

Usage:
    python3 validate_output.py <path-to-output.json>

Exits 0 and prints "OK" if everything checks out; otherwise prints each problem found
and exits 1.
"""
import json
import sys


REQUIRED_TOP_LEVEL = ["memberships", "membershipKnowledge"]

REQUIRED_MEMBERSHIP_FIELDS = [
    "id", "businessId", "planId", "locationId", "externalMembershipId",
    "membershipName", "membershipCode", "membershipTypeKind", "descriptionRaw",
    "price", "priceSource", "billingCycle", "membershipDuration", "isUnlimited",
    "setupFee", "annualFee", "declineFee", "buyOutFee", "freezeFee", "downgradeFee",
    "upgradeFee", "guestPassFee", "guestPassVisits", "numVisits", "advanceBookingDays",
    "saleStartDate", "centerAssigned", "soldInCenter", "benefits", "isActive",
    "createdAt", "updatedAt", "_etag", "_ts",
]

# The four fields the user's workflow treats as mandatory before a membership is "complete"
MANDATORY_FIELDS = {
    "membershipName": lambda v: bool(v),
    "price": lambda v: isinstance(v, (int, float)) and v >= 0,
    "membershipDuration": lambda v: bool(v),
    "benefits": lambda v: isinstance(v, list) and len(v) > 0,
}

REQUIRED_KNOWLEDGE_FIELDS = [
    "membershipId", "membershipName", "summary", "valueProposition", "idealFor",
    "includedServiceNames", "commonQuestions", "keywords", "notes",
    "createdAt", "updatedAt",
]


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_output.py <path-to-output.json>")
        sys.exit(1)

    path = sys.argv[1]
    problems = []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Could not read/parse JSON: {e}")
        sys.exit(1)

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            problems.append(f"Missing top-level key: {key}")

    if problems:
        _report(problems)

    memberships = data.get("memberships", [])
    if not isinstance(memberships, list):
        problems.append("memberships must be a list")
        memberships = []

    membership_ids = set()
    for i, m in enumerate(memberships):
        for field in REQUIRED_MEMBERSHIP_FIELDS:
            if field not in m:
                problems.append(f"memberships[{i}] missing field: {field}")

        for field, check in MANDATORY_FIELDS.items():
            if field not in m or not check(m.get(field)):
                problems.append(
                    f"memberships[{i}] fails mandatory-field check: {field} = {m.get(field)!r}"
                )

        for j, b in enumerate(m.get("benefits", []) or []):
            for bf in ("serviceNameRaw", "serviceId", "totalCredits"):
                if bf not in b:
                    problems.append(f"memberships[{i}].benefits[{j}] missing field: {bf}")

        mid = m.get("id")
        if mid:
            membership_ids.add(mid)
        else:
            problems.append(f"memberships[{i}] has empty/missing id")

    knowledge = data.get("membershipKnowledge", [])
    if not isinstance(knowledge, list):
        problems.append("membershipKnowledge must be a list")
        knowledge = []

    knowledge_ids = set()
    for i, k in enumerate(knowledge):
        for field in REQUIRED_KNOWLEDGE_FIELDS:
            if field not in k:
                problems.append(f"membershipKnowledge[{i}] missing field: {field}")
        mid = k.get("membershipId")
        knowledge_ids.add(mid)
        if mid not in membership_ids:
            problems.append(
                f"membershipKnowledge[{i}].membershipId {mid!r} has no matching memberships[].id"
            )

    if len(memberships) != len(knowledge):
        problems.append(
            f"memberships has {len(memberships)} entries but membershipKnowledge has "
            f"{len(knowledge)} — they should be 1:1"
        )

    missing_knowledge = membership_ids - knowledge_ids
    for mid in missing_knowledge:
        problems.append(f"membership id {mid} has no corresponding membershipKnowledge entry")

    _report(problems)


def _report(problems):
    if problems:
        print(f"Found {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    else:
        print("OK — structure matches the fixed target schema.")
        sys.exit(0)


if __name__ == "__main__":
    main()