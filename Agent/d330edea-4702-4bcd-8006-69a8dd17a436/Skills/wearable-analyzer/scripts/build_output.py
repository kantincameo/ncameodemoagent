#!/usr/bin/env python3
"""
build_output.py — Scaffolds the 8-object output shell with valid GUIDs
and the current UTC ISO-8601 timestamp, so Claude only has to fill in
"text", "rationale", and "referencesource" per object — never hand-write
IDs/dates/group order.

Usage:
    python3 build_output.py > shell.json

Then fill in the "text" / "rationale" / "referencesource" fields for each
of the 8 objects per the group table in SKILL.md, and save as the final
output JSON before running validate_output.py on it.
"""
import uuid
import json
from datetime import datetime, timezone

GROUPS = [
    "Internal Notes",
    "Understanding Your Results",
    "Priority Actions - Next 30 Days",
    "Long-Term Strategy",
]


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_shell():
    objects = []
    for group in GROUPS:
        for obj_type in ("highlight", "note"):
            objects.append({
                "id": str(uuid.uuid4()),
                "date": now_iso(),
                "type": obj_type,
                "text": "",
                "group": group,
                "rationale": "",
                "referencesource": "",
            })
    return objects


if __name__ == "__main__":
    print(json.dumps(build_shell(), indent=2, ensure_ascii=False))
