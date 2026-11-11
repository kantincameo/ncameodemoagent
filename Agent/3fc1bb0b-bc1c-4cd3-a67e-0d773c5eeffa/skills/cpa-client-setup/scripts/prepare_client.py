"""Step 2 of cpa-client-setup: check the sign-up payload and decide the company id and whether a login is needed.

stdin (JSON object):
  payload       the sign-up payload (firstName, lastName, email, phone, state, filingStatus, spouse, dependents, has1040, ...)
  existingUser  the `data` object returned by user_find(email) — { found, userId, companyId, ... } — or null

stdout (JSON object):
  { success, companyId, companyName, isExistingCompany, needsUserCreate, existingUserId, userCreateArgs }
  or { success: false, error }
"""
import json
import re
import sys
import uuid

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def fail(message):
    print(json.dumps({"success": False, "error": message}))
    sys.exit(0)


def text(value):
    return value.strip() if isinstance(value, str) else ""


def is_guid(value):
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False


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

    first, last = text(payload.get("firstName")), text(payload.get("lastName"))
    email, phone = text(payload.get("email")), text(payload.get("phone"))
    missing = [n for n, v in (("firstName", first), ("lastName", last), ("email", email), ("phone", phone)) if not v]
    if missing:
        fail("The sign-up is missing: " + ", ".join(missing) + ".")
    if not EMAIL.match(email):
        fail("The sign-up email is not a valid address.")

    existing = args.get("existingUser") or {}
    found = bool(existing.get("found"))
    existing_company = text(existing.get("companyId"))

    if found and is_guid(existing_company):
        company_id, is_existing_company = existing_company, True
    else:
        company_id, is_existing_company = str(uuid.uuid4()), False

    company_name = f"{first} {last}"
    print(json.dumps({
        "success": True,
        "companyId": company_id,
        "companyName": company_name,
        "isExistingCompany": is_existing_company,
        "needsUserCreate": not found,
        "existingUserId": existing.get("userId") if found else None,
        "userCreateArgs": None if found else {
            "firstName": first,
            "lastName": last,
            "email": email,
            "phone": phone,
            "companyId": company_id,
            "companyName": company_name,
        },
    }))


if __name__ == "__main__":
    main()
