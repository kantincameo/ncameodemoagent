---
name: approvals
description: List what is waiting in the Sentinel inbox for you (or everyone), with the rule behind each
---

Use the sentinel-approvals skill. Call `approvals_pending(approver_id="$ARGUMENTS")` (omit the argument for everyone). For each item show: tier, client, what it is, rule, who requested it, how long it has waited, and auto-send progress for templates. Remind the user that approving happens in the TaxPilot UI, not here.
