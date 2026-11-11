"""Step 6 of cpa-client-setup: turn what you read from the client's Form 1040 into 1040.json.

stdin (JSON object):
  companyId   from prepare_client.py
  extracted   JSON object of what you read from the 1040 (see SKILL.md for the shape); taxYear is required
  attachmentFileName  optional — the attached 1040's file name, so the original keeps its extension

The year being prepared is the 1040's own tax year + 1. Full SSNs / EINs are masked to the last 4 digits.

stdout (JSON object):
  { success, year, saveFileArgs: {...1040.json...}, saveAttachmentArgs: { blobPath, containerName } }
  or { success: false, error }
"""
import json
import re
import sys
import uuid
from datetime import datetime, timezone

CONTAINER = "cpadata"
SSN = re.compile(r"\b\d{3}-\d{2}-(\d{4})\b")
EIN = re.compile(r"\b\d{2}-\d{3}(\d{4})\b")
ID_FIELD = re.compile(r"ssn|social_?security|taxpayer_?id|\btin\b|^tin|ein$|^ein|itin", re.IGNORECASE)


def fail(message):
    print(json.dumps({"success": False, "error": message}))
    sys.exit(0)


def mask_text(value):
    value = SSN.sub(lambda m: "***-**-" + m.group(1), value)
    return EIN.sub(lambda m: "**-***" + m.group(1), value)


def mask(node):
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if ID_FIELD.search(key) and isinstance(value, (str, int)) and not isinstance(value, bool):
                digits = re.sub(r"\D", "", str(value))
                out[key] = "***" + digits[-4:] if len(digits) >= 4 else "***"
            else:
                out[key] = mask(value)
        return out
    if isinstance(node, list):
        return [mask(item) for item in node]
    if isinstance(node, str):
        return mask_text(node)
    return node


def main():
    try:
        args = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        fail("Arguments must be a JSON object.")

    company_id = str(args.get("companyId") or "").strip()
    try:
        uuid.UUID(company_id)
    except ValueError:
        fail("companyId must be a GUID.")

    extracted = args.get("extracted")
    if isinstance(extracted, str):
        try:
            extracted = json.loads(extracted)
        except json.JSONDecodeError:
            fail("extracted must be a JSON object.")
    if not isinstance(extracted, dict):
        fail("extracted is required.")

    try:
        tax_year = int(str(extracted.get("taxYear")).strip())
    except (TypeError, ValueError):
        fail("extracted.taxYear is required (the tax year printed on the 1040, e.g. 2025).")
    if not 2000 <= tax_year <= 2099:
        fail("extracted.taxYear must be between 2000 and 2099.")
    year = str(tax_year + 1)

    # Keep the original file's own extension (a photographed 1040 is not a PDF).
    attachment = str(args.get("attachmentFileName") or "")
    ext = ("." + attachment.rsplit(".", 1)[-1].lower()) if "." in attachment else ".pdf"
    if ext not in {".pdf", ".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff"}:
        ext = ".pdf"
    original_path = f"{company_id}/{year}/1040{ext}"

    record = mask(extracted)
    record["taxYear"] = tax_year
    record["preparedYear"] = int(year)
    record["sourceFileName"] = attachment or None
    record["sourceFilePath"] = original_path
    record["extractedDate"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    print(json.dumps({
        "success": True,
        "year": year,
        "saveFileArgs": {
            "content": json.dumps(record, indent=2),
            "fileName": "1040.json",
            "fileType": "json",
            "blobPath": f"{company_id}/{year}/1040.json",
            "containerName": CONTAINER,
        },
        "saveAttachmentArgs": {
            "blobPath": original_path,
            "containerName": CONTAINER,
            "fileName": attachment or None,
        },
    }))


if __name__ == "__main__":
    main()
