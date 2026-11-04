---
name: pipeline-management
description: Run the engagement manager's flight board — every return by stage, blocker, crew and status (on time, boarding, delayed, cleared); filter to at-risk, waiting on client or in review; suggest and route assignments; chase stuck returns. Use for "show me my board", "what's at risk", "who should take this return", "what's stuck".
---

# Pipeline management

**Screen:** O2 Flight board. **Agent:** engagement-manager.
**Tools:** `pipeline_board`, `assignment_suggest`, `return_readiness` (0); `approval_request`, `assignment_apply` (1, approval required).

## The return state machine
`intake → ready_for_prep → in_prep → in_review → client_approval → ready_to_file → filed → accepted` (and `rejected → in_prep`).
Agents may move: intake→ready_for_prep (manager), ready_for_prep→in_prep, in_prep→in_review (preparer, all fields written), in_review→in_prep (reviewer send-back), client_approval→ready_to_file (8879 signed and billing released). Sign-off and filing are human.

## Board statuses
- **DELAYED** — has a blocker and is not yet with the client.
- **BOARDING** — in review or waiting on the client's signature.
- **ON TIME** — moving, no blocker. **CLEARED** — ready to file or filed.

## Daily routine
1. `pipeline_board("at_risk")`. For each: blocker, owner, one next action.
2. Returns stuck in one stage more than 5 days → nudge the owner; if waiting on the client, check reminders sent (3 without reply → escalate to the partner).
3. New returns in `ready_for_prep` with no crew → `assignment_suggest`, then `approval_request(kind="assignment")`. Apply only with the approval id.

## Assignment heuristics
Match complexity (K-1, rental, multi-state) to preparers who have done it this season; keep reviewers under capacity; keep a client with last year's preparer when possible.
