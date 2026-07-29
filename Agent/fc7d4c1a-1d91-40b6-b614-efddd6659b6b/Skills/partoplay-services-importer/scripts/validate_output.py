#!/usr/bin/env python3
"""
Validates that a Service Knowledge Builder output file matches the fixed target schema
structurally (keys present, types roughly right, services<->serviceKnowledge joinable).
This does NOT judge writing quality/content — only structure.

Usage:
    python3 validate_output.py <path-to-output.json>

Exits 0 and prints "OK" if everything checks out; otherwise prints each problem found
and exits 1.
"""
import json
import sys
import uuid


REQUIRED_TOP_LEVEL = ["businessKnowledge", "services", "serviceKnowledge"]

REQUIRED_BUSINESS_FIELDS = [
    "businessName", "businessUrl", "industry", "businessType",
    "businessDescription", "targetAudience", "locations", "brandTone",
    "additionalNotes",
]

REQUIRED_SERVICE_FIELDS = [
    "id", "businessId", "serviceId", "serviceCode", "serviceName", "serviceKind",
    "serviceCategory", "serviceSubCategory", "isAddOn", "durationMinutes", "price",
    "taxIncluded", "taxGroup", "onlineBookingEnabled", "requiresResource",
    "requiresProvider", "resourceType", "providerType", "isActive", "createdAt",
    "updatedAt", "_etag", "_ts",
]

REQUIRED_KNOWLEDGE_FIELDS = [
    "serviceId", "serviceName", "summary", "keyBenefits", "idealFor",
    "commonQuestions", "relatedServices", "keywords", "bookingNotes",
    "createdAt", "updatedAt",
]


def is_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError, TypeError):
        return False


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

    bk = data.get("businessKnowledge", {})
    for field in REQUIRED_BUSINESS_FIELDS:
        if field not in bk:
            problems.append(f"businessKnowledge missing field: {field}")

    services = data.get("services", [])
    if not isinstance(services, list):
        problems.append("services must be a list")
        services = []

    service_ids = set()
    for i, svc in enumerate(services):
        for field in REQUIRED_SERVICE_FIELDS:
            if field not in svc:
                problems.append(f"services[{i}] missing field: {field}")
        if "id" in svc:
            if not is_uuid(svc["id"]):
                problems.append(f"services[{i}].id is not a valid UUID: {svc['id']!r}")
            else:
                service_ids.add(svc["id"])
        if not svc.get("serviceName"):
            problems.append(f"services[{i}] has empty/missing serviceName")

    knowledge = data.get("serviceKnowledge", [])
    if not isinstance(knowledge, list):
        problems.append("serviceKnowledge must be a list")
        knowledge = []

    knowledge_ids = set()
    for i, sk in enumerate(knowledge):
        for field in REQUIRED_KNOWLEDGE_FIELDS:
            if field not in sk:
                problems.append(f"serviceKnowledge[{i}] missing field: {field}")
        sid = sk.get("serviceId")
        knowledge_ids.add(sid)
        if sid not in service_ids:
            problems.append(
                f"serviceKnowledge[{i}].serviceId {sid!r} has no matching services[].id"
            )

    if len(services) != len(knowledge):
        problems.append(
            f"services has {len(services)} entries but serviceKnowledge has "
            f"{len(knowledge)} — they should be 1:1"
        )

    missing_knowledge = service_ids - knowledge_ids
    for sid in missing_knowledge:
        problems.append(f"service id {sid} has no corresponding serviceKnowledge entry")

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
