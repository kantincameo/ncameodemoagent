---
name: irs-notice-triage
description: Handle an IRS notice end to end — register it, acknowledge the client ("we have it, don't pay yet"), compare the IRS figures with the filed return, draft the response, and route it for CPA signature. Use when a CP2000, CP14, CP501 or other IRS letter arrives in the portal, mail scan or inbox.
---

# IRS notice triage

**Screens:** O2 Flight board, O5 Sentinel inbox. **Agents:** engagement-manager, preparer.
**Tools:** `notice_register` (1), `notice_triage` (0), `approval_request(kind="irs_response")` (1).

## Steps
1. `notice_register(return_id, notice_type, tax_year, received_on, response_due, proposed_cents)`. This also sends the client the standard acknowledgment.
2. `notice_triage(notice_id)` → days to respond and the analysis.
3. Classify:
   - **CP2000 (underreported income)** — find the information return the IRS matched. Was it reported elsewhere (e.g. Schedule D line 8b), reported under another form, or truly missed?
   - **CP14 / CP501 (balance due)** — check payments on the account transcript; a missing estimated payment is common.
   - **Anything else** — summarize what the IRS says and what it asks for.
4. Draft the response: agree, partly agree, or disagree, with the schedule or document that supports it.
5. `approval_request(kind="irs_response")`. A CPA reviews and signs. Mailing or uploading is a human step.
6. Keep the client informed through client-notifications at each step.

## Never
- Tell the client to pay or not to pay beyond the standard acknowledgment. That is the CPA's call.
- Miss the response date: anything under 10 days goes on the partner's brief.
