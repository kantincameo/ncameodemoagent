---
name: partner-brief
description: Write the partner's morning brief and cockpit view — in-flight vs on-track, at-risk returns by cause, review capacity and a concrete rebalance, and the short list that needs a partner's eye. Use at 6 am on a schedule, or when the partner asks "how are we doing?".
---

# Partner brief

**Screen:** O1 Cockpit. **Agent:** partner-agent.
**Tools:** `morning_brief`, `capacity_report`, `pipeline_board`, `assignment_suggest`, `approvals_pending` (all tier 0); `approval_request` for a rebalance.

## Steps
1. `morning_brief` → in-flight count, by stage, at-risk list, over-capacity staff, pending approvals.
2. `capacity_report` → who is over and by how much.
3. Write the brief:
   - **Sentence 1:** in flight and on track. **Sentence 2:** at risk, with the main cause. **Sentence 3:** the bottleneck with numbers.
   - Then up to 5 bullets under "Needs a partner's eye".
4. If a reviewer is over capacity, propose a rebalance: move the simplest returns (single W-2, no judgment items) to reviewers with room. Queue it with `approval_request(kind="assignment")`; never apply it yourself.

## Escalate to the partner
- A client with 3+ reminders and no reply, close to a deadline.
- An IRS notice due within 10 days.
- A return the agent recommends filing with estimates.
- A Sentinel denial that suggests a process problem (repeated bank-detail requests, stale access).

## Never
- Invent a figure. If a tool does not return it, say "not available".
