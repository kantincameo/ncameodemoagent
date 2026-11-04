---
name: security-audit
description: Answer audit and access questions from the TaxPilot audit log — who opened a client file, why policy denials spiked, whether anyone tried to change bank details, which staff hold stale access — and prepare WISP evidence. Use for the Security and audit screen or any "who / when / was it allowed" question.
---

# Security audit

**Screen:** O6 Security and audit. **Agent:** security-officer.
**Tools:** `audit_query`, `access_review` (0). Revocation (`access_revoke`) is human-only.

## Answering a question
1. Translate it into filters: `return_id`, `actor_contains`, `rule_id`, `result`, `since`.
2. Run `audit_query`. Report: time window, events examined, grouped counts by person and agent, and the rule ids involved.
3. Agents always act for a named person — say "preparer agent for Ravi Iyer", never just "an agent".

## Common questions
| Question | Filters |
| --- | --- |
| Who opened the Patel file this week? | `return_id="TX-25-0417", since=<7 days ago>` |
| Why did denials spike Thursday? | `result="denied", since=<Thursday>` then group by actor and rule |
| Any bank-detail change attempts? | `rule_id="X-1"` |
| Any identifier leaks? | `rule_id="P-2"` (should be zero) |

## Access review (quarterly, or after a reassignment)
`access_review` → grants to returns the person is no longer assigned to. List them for revocation in the UI and export for the WISP file.

## Incidents
An allowed access outside assignment, or any P-2 event, is a possible incident: summarize facts and event ids for the security lead and follow the WISP playbook. Do not contact clients.
