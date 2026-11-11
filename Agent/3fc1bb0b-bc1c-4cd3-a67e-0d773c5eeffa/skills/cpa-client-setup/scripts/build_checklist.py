"""Step 8 of cpa-client-setup: build the client's document checklist (Tasks.json) for the year being prepared.

stdin (JSON object):
  companyId      from prepare_client.py
  year           the year being prepared (from build_1040_record.py; without a 1040, see SKILL.md)
  payload        the sign-up payload (names, state, spouse, dependents, has1040)
  extracted1040  the same `extracted` object you passed to build_1040_record.py, or null when no 1040 was attached
  existingTasks  exactly what read_file returned for Tasks.json ("File not found." / text / array), or null

The 1040 -> document mapping is in this script, so the same return always gives the same checklist. Items already on
the list (same DocumentType + Issuer + Owner) are kept and not duplicated. Every new item starts as "Pending".

stdout (JSON object):
  { success, added, skipped, total, newItems: [titles], saveFileArgs: {...Tasks.json...} }
  or { success: false, error }
"""
import json
import re
import sys
import uuid
from datetime import datetime, timezone

CONTAINER = "cpadata"
TASK_TYPE = "DocumentChecklist"
NO_INCOME_TAX_STATES = {"AK", "FL", "NV", "NH", "SD", "TN", "TX", "WA", "WY"}

SSN = re.compile(r"\b\d{3}-\d{2}-(\d{4})\b")
EIN = re.compile(r"\b\d{2}-\d{3}(\d{4})\b")

# Normalise the form names people and models write ("w2", "1099 int", "Form 1098-T") to one spelling.
FORM_ALIASES = {
    "W2": "W-2", "W-2": "W-2", "W2G": "W-2G", "W-2G": "W-2G",
    "1099INT": "1099-INT", "1099DIV": "1099-DIV", "1099B": "1099-B", "1099R": "1099-R", "1099G": "1099-G",
    "1099NEC": "1099-NEC", "1099K": "1099-K", "1099MISC": "1099-MISC", "1099SA": "1099-SA", "1099Q": "1099-Q",
    "1099OID": "1099-OID", "SSA1099": "SSA-1099", "RRB1099": "RRB-1099", "1098": "1098", "1098E": "1098-E",
    "1098T": "1098-T", "1095A": "1095-A", "5498": "5498", "5498SA": "5498-SA", "K1": "K-1", "SCHEDULEK1": "K-1",
}

# 1040 line -> (DocumentType, what to ask for, reason). Asked for once per line unless an issuer already covers it.
LINE_RULES = [
    (("1a", "1z"), "W-2", "W-2 from each employer", "1040 line 1a wages"),
    (("2a", "2b"), "1099-INT", "1099-INT from each bank or broker", "1040 line 2b interest"),
    (("3a", "3b"), "1099-DIV", "1099-DIV from each broker or fund", "1040 line 3b dividends"),
    (("4a", "4b"), "1099-R", "1099-R for IRA distributions", "1040 line 4b IRA distributions"),
    (("5a", "5b"), "1099-R", "1099-R for pensions and annuities", "1040 line 5b pensions"),
    (("6a", "6b"), "SSA-1099", "SSA-1099 Social Security benefit statement", "1040 line 6a Social Security"),
    (("7",), "1099-B", "1099-B (consolidated 1099) from each broker", "1040 line 7 capital gain or loss"),
    (("26",), "Estimated payments", "Dates and amounts of federal and state estimated tax payments", "1040 line 26 estimated payments"),
]

# Schedule 1 line -> document
SCHEDULE1_RULES = [
    ("1", "1099-G", "1099-G for the state tax refund", "Schedule 1 line 1 taxable state refund"),
    ("2a", "Alimony", "Divorce decree or alimony payment records", "Schedule 1 line 2a alimony received"),
    ("7", "1099-G", "1099-G for unemployment compensation", "Schedule 1 line 7 unemployment"),
    ("11", "Educator expenses", "Receipts for classroom supplies", "Schedule 1 line 11 educator expenses"),
    ("16", "Retirement contributions", "SEP / SIMPLE / solo 401(k) contribution statements", "Schedule 1 line 16 self-employed retirement"),
    ("17", "Health insurance premiums", "Self-employed health insurance premium statements", "Schedule 1 line 17 health insurance"),
    ("20", "5498", "Form 5498 or IRA contribution confirmation", "Schedule 1 line 20 IRA deduction"),
    ("21", "1098-E", "1098-E from each student loan lender", "Schedule 1 line 21 student loan interest"),
]

SCHEDULE_RULES = {
    "A": [("1098", "1098 mortgage interest statement from each lender", "Schedule A itemized deductions"),
          ("Property tax", "Property tax bills", "Schedule A state and local taxes"),
          ("Charitable receipts", "Donation receipts and acknowledgment letters", "Schedule A charitable gifts")],
    "C": [("1099-NEC", "1099-NEC / 1099-K / 1099-MISC from each payer", "Schedule C business income"),
          ("Schedule C records", "Business income and expense records, mileage log, home-office details", "Schedule C business")],
    "D": [("1099-B", "1099-B (consolidated 1099) from each broker", "Schedule D capital gains")],
    "E": [("Schedule E records", "Rental income and expenses, 1098 and property tax for each rental", "Schedule E rentals / royalties")],
    "F": [("Schedule F records", "Farm income and expense records", "Schedule F farm income")],
}

FORM_RULES = {
    "2441": ("Childcare statement", "Statement from each childcare provider (name, address, amount paid)", "Form 2441 child and dependent care"),
    "4797": ("Form 4797 records", "Sale documents and depreciation records for business property", "Form 4797 sale of business property"),
    "5695": ("Energy improvements", "Invoices for qualifying home energy improvements", "Form 5695 energy credits"),
    "8606": ("5498", "Form 5498 and IRA basis records", "Form 8606 nondeductible IRA"),
    "8839": ("Adoption expenses", "Adoption expense records", "Form 8839 adoption credit"),
    "8863": ("1098-T", "1098-T from each school, plus tuition and book receipts", "Form 8863 education credits"),
    "8889": ("5498-SA", "1099-SA and 5498-SA for the HSA", "Form 8889 HSA"),
    "8936": ("Clean vehicle", "Vehicle purchase agreement and dealer time-of-sale report", "Form 8936 clean vehicle credit"),
    "8949": ("1099-B", "1099-B (consolidated 1099) from each broker", "Form 8949 sales of securities"),
    "8962": ("1095-A", "1095-A from the Health Insurance Marketplace", "Form 8962 premium tax credit"),
}


def fail(message):
    print(json.dumps({"success": False, "error": message}))
    sys.exit(0)


def text(value):
    return value.strip() if isinstance(value, str) else ""


def mask_text(value):
    value = SSN.sub(lambda m: "***-**-" + m.group(1), value)
    return EIN.sub(lambda m: "**-***" + m.group(1), value)


def norm_form(name):
    key = re.sub(r"[^A-Z0-9]", "", text(str(name)).upper().replace("FORM", ""))
    return FORM_ALIASES.get(key, text(str(name)))


def norm_schedule(name):
    s = text(str(name)).upper().replace("SCHEDULE", "").replace("SCH", "").strip(" .-")
    return s


def nonzero(value):
    if value is None or isinstance(value, bool):
        return False
    try:
        return float(str(value).replace(",", "").replace("$", "")) != 0
    except ValueError:
        return bool(text(str(value)))


def parse_existing(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [t for t in raw if isinstance(t, dict)]
    if isinstance(raw, str):
        stripped = raw.strip()
        if not stripped.startswith("["):
            return []  # "File not found." or any other non-JSON reply means there is no checklist yet
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError:
            fail("existingTasks is not valid JSON; pass exactly what read_file returned.")
        return [t for t in data if isinstance(t, dict)]
    fail("existingTasks must be what read_file returned, or null.")


def key_of(task):
    return "|".join(text(str(task.get(k) or "")).lower() for k in ("DocumentType", "Issuer", "Owner"))


def main():
    try:
        args = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        fail("Arguments must be a JSON object.")

    company_id, year = text(str(args.get("companyId") or "")), text(str(args.get("year") or ""))
    try:
        uuid.UUID(company_id)
    except ValueError:
        fail("companyId must be a GUID.")
    if not (len(year) == 4 and year.isdigit() and 2000 <= int(year) <= 2100):
        fail("year must be 4 digits, e.g. \"2026\".")

    payload = args.get("payload") or {}
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {}
    f1040 = args.get("extracted1040")
    if isinstance(f1040, str):
        try:
            f1040 = json.loads(f1040)
        except json.JSONDecodeError:
            fail("extracted1040 must be a JSON object or null.")
    f1040 = f1040 if isinstance(f1040, dict) else None

    primary = f"{text(payload.get('firstName'))} {text(payload.get('lastName'))}".strip()
    wanted = []  # (DocumentType, Issuer, Owner, Title, Reason, Source)

    def want(doc_type, issuer, owner, title, reason, source):
        wanted.append((doc_type, issuer or "", owner or "", title, reason, source))

    # ---- from the prior-year 1040 ----------------------------------------------------------------------------
    if f1040:
        issuer_types = set()
        for item in f1040.get("issuers") or []:
            if not isinstance(item, dict):
                continue
            doc_type = norm_form(item.get("form") or item.get("documentType") or "")
            issuer = text(item.get("issuer"))
            if not doc_type or not issuer:
                continue
            issuer_types.add(doc_type)
            owner = text(item.get("owner")) or primary
            want(doc_type, issuer, owner, f"{doc_type} — {issuer}", f"{doc_type} from {issuer} on the prior-year return", "prior_1040")

        lines = {text(str(k)).lower(): v for k, v in (f1040.get("lines") or {}).items()}
        for keys, doc_type, title, reason in LINE_RULES:
            if any(nonzero(lines.get(k)) for k in keys) and doc_type not in issuer_types:
                want(doc_type, "", primary, title, reason, "prior_1040")

        sch1 = {text(str(k)).lower(): v for k, v in (f1040.get("schedule1") or {}).items()}
        for line, doc_type, title, reason in SCHEDULE1_RULES:
            if nonzero(sch1.get(line)) and doc_type not in issuer_types:
                want(doc_type, "", primary, title, reason, "prior_1040")

        for sched in {norm_schedule(s) for s in f1040.get("schedules") or []}:
            for doc_type, title, reason in SCHEDULE_RULES.get(sched, []):
                if doc_type not in issuer_types:
                    want(doc_type, "", primary, title, reason, "prior_1040")

        for form in {re.sub(r"\D", "", str(f)) for f in f1040.get("forms") or []}:
            if form in FORM_RULES:
                doc_type, title, reason = FORM_RULES[form]
                if doc_type not in issuer_types:
                    want(doc_type, "", primary, title, reason, "prior_1040")

    # ---- base list --------------------------------------------------------------------------------------------
    filers = [primary] if primary else []
    spouse = text(payload.get("spouse"))
    for filer in (f1040 or {}).get("filers") or []:
        name = text(filer.get("name")) if isinstance(filer, dict) else ""
        if name and name.lower() not in (f.lower() for f in filers):
            filers.append(name)
    if spouse and spouse.lower() not in (f.lower() for f in filers):
        filers.append(spouse)
    for person in filers:
        want("Photo ID", "", person, f"Photo ID — {person}", "Identity verification for each filer", "base")

    want("Bank account", "", primary, "Bank account for the refund or payment",
         "Routing and account number go in the secure form, never in a message", "base")

    state = text(payload.get("state") or (f1040 or {}).get("state")).upper()
    if state and state not in NO_INCOME_TAX_STATES:
        want("State return", state, primary, f"Last year's {state} state return", f"{state} has a state income tax", "base")

    dependents = (f1040 or {}).get("dependents") or []
    names = [text(d.get("name")) for d in dependents if isinstance(d, dict) and text(d.get("name"))]
    if not names and text(payload.get("dependents")):
        names = [n.strip() for n in re.split(r"[,;\n]", text(payload.get("dependents"))) if n.strip()]
    for dep in names:
        want("Dependent documents", "", dep, f"Childcare / education statements — {dep}",
             "Dependent credits (childcare, education) if they apply", "base")

    if not f1040 and text(str(payload.get("has1040"))).lower() in ("yes", "true", "y"):
        want("Prior-year Form 1040", "", primary, "Prior-year Form 1040",
             "The client said they have last year's return; it decides the rest of this checklist", "base")

    # ---- merge with the existing checklist ---------------------------------------------------------------------
    existing = parse_existing(args.get("existingTasks"))
    keys = {key_of(t) for t in existing}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    added, skipped, new_titles = 0, 0, []
    for doc_type, issuer, owner, title, reason, source in wanted:
        task = {"DocumentType": doc_type, "Issuer": issuer, "Owner": owner}
        if key_of(task) in keys:
            skipped += 1
            continue
        keys.add(key_of(task))
        task.update({
            "id": str(uuid.uuid4()),
            "ProfileId": company_id,
            "Year": year,
            "TaskType": TASK_TYPE,
            "Title": mask_text(title),
            "Reason": mask_text(reason),
            "Source": source,
            "Status": "Pending",
            "FileUrl": None,
            "UploadedOn": None,
            "CreatedDate": now,
        })
        existing.append(task)
        added += 1
        new_titles.append(task["Title"])

    print(json.dumps({
        "success": True,
        "added": added,
        "skipped": skipped,
        "total": len(existing),
        "newItems": new_titles,
        "saveFileArgs": {
            "content": json.dumps(existing, indent=2),
            "fileName": "Tasks.json",
            "fileType": "json",
            "blobPath": f"{company_id}/{year}/Tasks.json",
            "containerName": CONTAINER,
        },
    }))


if __name__ == "__main__":
    main()
