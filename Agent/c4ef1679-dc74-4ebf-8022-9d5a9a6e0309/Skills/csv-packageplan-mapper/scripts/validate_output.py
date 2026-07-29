#!/usr/bin/env python3
"""
Validates that a Package Knowledge Builder output file matches the fixed target schema
structurally (keys present, types roughly right, packages<->packageKnowledge joinable,
and that the four mandatory fields per package are present).
This does NOT judge writing quality/content — only structure.

Usage:
    python3 validate_output.py <path-to-output.json>

Exits 0 and prints "OK" if everything checks out; otherwise prints each problem found
and exits 1.
"""
import json
import sys


REQUIRED_TOP_LEVEL = ["packages", "packageKnowledge"]

REQUIRED_PACKAGE_FIELDS = [
    "id", "businessId", "packageId", "locationId", "packageCode", "packageName",
    "description", "packageCategory", "businessName", "price", "priceSource",
    "expiryDuration", "onlineBookingEnabled", "taxGroup", "centerTaxId",
    "hasPackageSales", "hasServices", "hasServiceDiscount", "hasFreeProducts",
    "hasBundledProducts", "hasForms", "hasClasses", "hasWorkshops", "hasDayPackage",
    "benefits", "ownerType", "ownerName", "isActive", "createdAt", "updatedAt",
    "_etag", "_ts",
]

# The four fields the user's workflow treats as mandatory before a package is "complete"
MANDATORY_FIELDS = {
    "packageName": lambda v: bool(v),
    "price": lambda v: isinstance(v, (int, float)) and v >= 0,
    "expiryDuration": lambda v: bool(v),
    "benefits": lambda v: isinstance(v, list) and len(v) > 0,
}

REQUIRED_KNOWLEDGE_FIELDS = [
    "packageId", "packageName", "summary", "valueProposition", "idealFor",
    "includedServiceNames", "expirySummary", "commonQuestions", "keywords", "notes",
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

    packages = data.get("packages", [])
    if not isinstance(packages, list):
        problems.append("packages must be a list")
        packages = []

    package_ids = set()
    for i, p in enumerate(packages):
        for field in REQUIRED_PACKAGE_FIELDS:
            if field not in p:
                problems.append(f"packages[{i}] missing field: {field}")

        for field, check in MANDATORY_FIELDS.items():
            if field not in p or not check(p.get(field)):
                problems.append(
                    f"packages[{i}] fails mandatory-field check: {field} = {p.get(field)!r}"
                )

        for j, b in enumerate(p.get("benefits", []) or []):
            for bf in ("serviceNameRaw", "serviceId", "totalCredits"):
                if bf not in b:
                    problems.append(f"packages[{i}].benefits[{j}] missing field: {bf}")

        pid = p.get("id")
        if pid:
            package_ids.add(pid)
        else:
            problems.append(f"packages[{i}] has empty/missing id")

    knowledge = data.get("packageKnowledge", [])
    if not isinstance(knowledge, list):
        problems.append("packageKnowledge must be a list")
        knowledge = []

    knowledge_ids = set()
    for i, k in enumerate(knowledge):
        for field in REQUIRED_KNOWLEDGE_FIELDS:
            if field not in k:
                problems.append(f"packageKnowledge[{i}] missing field: {field}")
        pid = k.get("packageId")
        knowledge_ids.add(pid)
        if pid not in package_ids:
            problems.append(
                f"packageKnowledge[{i}].packageId {pid!r} has no matching packages[].id"
            )

    if len(packages) != len(knowledge):
        problems.append(
            f"packages has {len(packages)} entries but packageKnowledge has "
            f"{len(knowledge)} — they should be 1:1"
        )

    missing_knowledge = package_ids - knowledge_ids
    for pid in missing_knowledge:
        problems.append(f"package id {pid} has no corresponding packageKnowledge entry")

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
