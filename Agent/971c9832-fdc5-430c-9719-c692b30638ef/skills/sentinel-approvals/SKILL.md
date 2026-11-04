---
name: sentinel-approvals
description: How every TaxPilot agent handles actions that leave the firm — risk tiers 0 to 3, approval_request, who approves what, auto-send graduation, and what to do when Sentinel denies a call. Use before any outbound message, invoice, recommendation, IRS response or assignment, and whenever a tool call is refused with a [Sentinel] reason.
---

# Sentinel approvals

Full policy: `${CLAUDE_PLUGIN_ROOT}/policy/sentinel-policy.json`. Screen: O5 Sentinel inbox.

## Tiers
| Tier | Meaning | What happens |
| --- | --- | --- |
| 0 Read | Looks at data in scope | Allowed, logged |
| 1 Draft | Internal, reversible | Allowed, logged with source |
| 2 External | Leaves the firm | Needs an approved `approval_id` (or a template cleared for auto-send, or an invoice within tolerance) |
| 3 Irreversible / regulated | E-file, sign, move money, bank details, tax advice | Always refused for agents |
| human | Approve, sign off, decide judgment items, revoke access | Recorded only from a person's click in the UI |

## Who approves
| Rule | Action | Approver |
| --- | --- | --- |
| S-2.1 | Client message with return figures | Reviewer |
| S-2.3 / S-2.4 | First template send / later reminders | Client services |
| S-3.2 | Recommendation to a client | Manager (the CPA owns the advice) |
| B-1 | Invoice over the 10% fee tolerance | Manager |
| N-1 | IRS correspondence | Signing CPA |
| M-1 | Assign or reassign a return | Manager |

Unanswered approvals escalate to the engagement manager after 4 working hours. Nothing proceeds without a person.

## When Sentinel says no
The refusal starts with `[Sentinel <rule>]` and says why. Then:
- **P-1 identifier in input** — remove it; refer to documents and people by id or masked value.
- **S-* / B-1 / M-1 needs approval** — call `approval_request`, tell the user who must approve, and stop.
- **pending / denied** — wait or report the denial reason. Never reword or resend to get around it.
- **T-3 / H-*** — this is a person's job. Say who should do it and what they need.
- **A-0 / A-1** — outside your persona or assignment. Do not look for another route to the data.

## Auto-send graduation
A template becomes eligible after 50 approved sends with no edits. A partner switches auto-send on; Sentinel never does it by itself. Templates with figures, advice or fees are never eligible.
