#!/usr/bin/env python3
"""
Validates that a Customer Knowledge Builder output file matches the fixed target schema
structurally (keys present, types roughly right, customers<->customerKnowledge joinable,
customerMemberships<->customers linked, and that mandatory fields are present).
This does NOT judge writing quality/content — only structure.

Usage:
    python3 validate_output.py <path-to-output.json>

Exits 0 and prints "OK" if everything checks out; otherwise prints each problem found
and exits 1.
"""
import json
import sys


REQUIRED_TOP_LEVEL = ["customers", "customerMemberships", "customerKnowledge"]

REQUIRED_CUSTOMER_FIELDS = [
    "id", "businessId", "firstName", "lastName", "email", "phone", "dob", "gender",
    "address", "locationId", "joinedDate", "lastVisitDate", "totalVisits", "totalSpend",
    "lifetimeValue", "tags", "preferredContactMethod", "activeMemberships",
    "createdAt", "updatedAt", "_etag", "_ts",
]

REQUIRED_MEMBERSHIP_RECORD_FIELDS = [
    "id", "businessId", "customerId", "membershipPlanId", "membershipName", "planKind",
    "locationId", "invoiceNo", "benefitType", "saleDate", "startDate", "endDate",
    "salesAmount", "salesAmountInclTax", "balanceValue", "cancelledValue", "expiredValue",
    "membershipStatus", "recurrenceStatus", "nextRecurrenceDate", "benefits",
    "createdAt", "updatedAt", "_etag", "_ts",
]

REQUIRED_KNOWLEDGE_FIELDS = [
    "customerId", "customerName", "summary", "engagementLevel", "valueSegment",
    "activePlans", "preferredServices", "commonQuestions", "keywords", "notes",
    "createdAt", "updatedAt",
]


def has_contact(c):
    return bool(c.get("email")) or bool(c.get("phone"))


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

    customers = data.get("customers", [])
    if not isinstance(customers, list):
        problems.append("customers must be a list")
        customers = []

    customer_ids = set()
    for i, c in enumerate(customers):
        for field in REQUIRED_CUSTOMER_FIELDS:
            if field not in c:
                problems.append(f"customers[{i}] missing field: {field}")
        if not c.get("firstName") or not c.get("lastName"):
            problems.append(f"customers[{i}] missing firstName/lastName")
        if not has_contact(c):
            problems.append(f"customers[{i}] has neither email nor phone")
        cid = c.get("id")
        if cid:
            customer_ids.add(cid)
        else:
            problems.append(f"customers[{i}] has empty/missing id")

    memberships = data.get("customerMemberships", [])
    if not isinstance(memberships, list):
        problems.append("customerMemberships must be a list")
        memberships = []

    for i, m in enumerate(memberships):
        for field in REQUIRED_MEMBERSHIP_RECORD_FIELDS:
            if field not in m:
                problems.append(f"customerMemberships[{i}] missing field: {field}")
        cid = m.get("customerId")
        if not cid or cid not in customer_ids:
            problems.append(
                f"customerMemberships[{i}].customerId {cid!r} has no matching customers[].id"
            )
        if not m.get("startDate"):
            problems.append(f"customerMemberships[{i}] missing startDate")
        if not m.get("membershipName"):
            problems.append(f"customerMemberships[{i}] missing membershipName (use \"Other\" if unmatched)")
        benefits = m.get("benefits")
        if not isinstance(benefits, list) or len(benefits) == 0:
            problems.append(f"customerMemberships[{i}] has no benefits entries")
        else:
            for j, b in enumerate(benefits):
                for bf in ("serviceNameRaw", "serviceId", "totalCredits", "redeemedCredits",
                           "refundedCredits", "expiredCredits", "balanceCredits"):
                    if bf not in b:
                        problems.append(f"customerMemberships[{i}].benefits[{j}] missing field: {bf}")

    knowledge = data.get("customerKnowledge", [])
    if not isinstance(knowledge, list):
        problems.append("customerKnowledge must be a list")
        knowledge = []

    knowledge_ids = set()
    for i, k in enumerate(knowledge):
        for field in REQUIRED_KNOWLEDGE_FIELDS:
            if field not in k:
                problems.append(f"customerKnowledge[{i}] missing field: {field}")
        cid = k.get("customerId")
        knowledge_ids.add(cid)
        if cid not in customer_ids:
            problems.append(
                f"customerKnowledge[{i}].customerId {cid!r} has no matching customers[].id"
            )

    if len(customers) != len(knowledge):
        problems.append(
            f"customers has {len(customers)} entries but customerKnowledge has "
            f"{len(knowledge)} — they should be 1:1"
        )

    missing_knowledge = customer_ids - knowledge_ids
    for cid in missing_knowledge:
        problems.append(f"customer id {cid} has no corresponding customerKnowledge entry")

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
