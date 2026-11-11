"""Change one checklist item's status in Tasks.json.

stdin (JSON object):
  companyId      the company's GUID
  year           the year folder of the checklist, e.g. "2026"
  existingTasks  exactly what read_file returned for {companyId}/{year}/Tasks.json
  taskId         the item's id
  status         Pending | Uploaded | Received | Retake | NotNeeded
  actor          "client" (the client themself) or "staff"
  fileUrl        required when status is Uploaded — the uploaded document's URL
  note           optional, e.g. why a retake is needed

A client may only set Uploaded or NotNeeded; staff may set any status.

stdout (JSON object):
  { success, task, saveFileArgs: {...Tasks.json...} }   or   { success: false, error }
"""
import json
import re
import sys
import uuid
from datetime import datetime, timezone

CONTAINER = "cpadata"
STATUSES = ["Pending", "Uploaded", "Received", "Retake", "NotNeeded"]
CLIENT_STATUSES = {"Uploaded", "NotNeeded"}
SSN = re.compile(r"\b\d{3}-\d{2}-(\d{4})\b")
EIN = re.compile(r"\b\d{2}-\d{3}(\d{4})\b")


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

    company_id, year = text(str(args.get("companyId") or "")), text(str(args.get("year") or ""))
    try:
        uuid.UUID(company_id)
    except ValueError:
        fail("companyId must be a GUID.")
    if not (len(year) == 4 and year.isdigit()):
        fail("year must be 4 digits.")

    status = next((s for s in STATUSES if s.lower() == text(args.get("status")).lower()), None)
    if status is None:
        fail("status must be one of: " + ", ".join(STATUSES) + ".")
    actor = text(args.get("actor")).lower()
    if actor not in ("client", "staff"):
        fail("actor must be \"client\" or \"staff\".")
    if actor == "client" and status not in CLIENT_STATUSES:
        fail("A client can only set: Uploaded, NotNeeded.")
    file_url = text(args.get("fileUrl"))
    if status == "Uploaded" and not file_url:
        fail("fileUrl is required when the status is Uploaded.")

    raw = args.get("existingTasks")
    if isinstance(raw, str):
        if not raw.strip().startswith("["):
            fail("There is no checklist for this company and year (read_file did not return Tasks.json).")
        try:
            tasks = json.loads(raw)
        except json.JSONDecodeError:
            fail("existingTasks is not valid JSON; pass exactly what read_file returned.")
    elif isinstance(raw, list):
        tasks = raw
    else:
        fail("existingTasks is required.")

    task_id = text(str(args.get("taskId") or ""))
    task = next((t for t in tasks if isinstance(t, dict) and text(str(t.get("id"))).lower() == task_id.lower()), None)
    if task is None:
        fail("No checklist item has this taskId.")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    task["Status"] = status
    if file_url:
        task["FileUrl"] = file_url
    if status == "Uploaded":
        task["UploadedOn"] = now
    note = text(args.get("note"))
    if note:
        note = SSN.sub(lambda m: "***-**-" + m.group(1), note)
        task["Note"] = EIN.sub(lambda m: "**-***" + m.group(1), note)
    task["UpdatedBy"] = actor
    task["UpdatedDate"] = now

    print(json.dumps({
        "success": True,
        "task": task,
        "saveFileArgs": {
            "content": json.dumps(tasks, indent=2),
            "fileName": "Tasks.json",
            "fileType": "json",
            "blobPath": f"{company_id}/{year}/Tasks.json",
            "containerName": CONTAINER,
        },
    }))


if __name__ == "__main__":
    main()
