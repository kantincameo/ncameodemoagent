"""Step 5 of cpa-client-setup: build CompanyProfile.json once the client's userId is known.

stdin (JSON object):
  payload      the sign-up payload
  companyType  required, e.g. "Individual"
  companyId    from prepare_client.py
  userId       from user_create (or user_find when the user already existed)

stdout (JSON object):
  { success, saveFileArgs: { content, fileName, fileType, blobPath, containerName } }
  or { success: false, error }
"""
import json
import sys
import uuid
from datetime import datetime, timezone

CONTAINER = "cpadata"


def fail(message):
    print(json.dumps({"success": False, "error": message}))
    sys.exit(0)


def text(value):
    return value.strip() if isinstance(value, str) else ""


def main():
    try:
        args = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        fail("Arguments must be a JSON object.")

    payload = args.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            fail("payload must be the sign-up JSON object.")
    if not isinstance(payload, dict):
        fail("payload is required.")

    company_type = text(args.get("companyType"))
    if not company_type:
        fail("companyType is required (e.g. \"Individual\").")
    company_id, user_id = text(args.get("companyId")), text(args.get("userId"))
    try:
        uuid.UUID(company_id)
    except ValueError:
        fail("companyId must be a GUID.")
    if not user_id:
        fail("userId is required — call user_create (or user_find) first.")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    first, last = text(payload.get("firstName")), text(payload.get("lastName"))
    profile = {
        "id": company_id,
        "Name": f"{first} {last}",
        "CompanyType": company_type,
        "UserId": user_id,
        "Users": [user_id],
        "FirstName": first,
        "LastName": last,
        "Email": text(payload.get("email")),
        "Phone": text(payload.get("phone")),
        "State": text(payload.get("state")) or None,
        "FilingStatus": text(payload.get("filingStatus")) or None,
        "Spouse": text(payload.get("spouse")) or None,
        "Dependents": text(payload.get("dependents")) or None,
        "Source": text(payload.get("source")) or None,
        "SignupStatus": text(payload.get("status")) or None,
        "CreatedDate": now,
        "UpdatedDate": now,
    }

    print(json.dumps({
        "success": True,
        "saveFileArgs": {
            "content": json.dumps(profile, indent=2),
            "fileName": "CompanyProfile.json",
            "fileType": "json",
            "blobPath": f"{company_id}/CompanyProfile.json",
            "containerName": CONTAINER,
        },
    }))


if __name__ == "__main__":
    main()
