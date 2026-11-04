---
name: onboard-client
description: Onboard a new client from their previous year's tax return — scan the 1040 to create the household, filers, dependents, filing status and state, store the prior return under its own year, pre-fill this year's expected-document checklist with issuers, and queue the engagement letter, consent and IRS access forms. Use for "new client", "onboard the Okonkwos", "they sent last year's return".
---

# Onboard a client from a prior return

**Screen:** C0 Onboarding (what the client confirms) and O2 Flight board (where the new return appears).
**Agents:** client-services-admin, engagement-manager. **Tool:** `onboard_from_prior_return` (1).

## Steps
1. Get the prior-year Form 1040 (PDF or photos). Nothing else is needed to start.
2. `onboard_from_prior_return(household_name, filename, mime, content_base64 | source_path)`. The scanner must recognize a Form 1040; anything else is refused.
3. What it creates:
   - the household and its people: filers (primary, spouse), dependents; the primary's SSN masked, raw value hashed to a vault reference;
   - the prior-year return (stage `accepted`) with the 1040 stored at `clients/{household}/{prior_year}/…` and its main lines captured as trend history;
   - this year's return (stage `intake`) with a checklist built from every form on the prior return, each with its issuer and owner (`source: prior_year`), plus the prior-year return itself as a received item;
   - client approvals waiting: engagement letter, consent to use tax information, Form 8821;
   - a welcome notification asking the client to confirm the pre-fill.
4. Tell the manager what was created and hand the return to pipeline-management for assignment.
5. The client confirms or corrects the pre-fill in the app (C0). Corrections and life events (new job, new dependent, moved, sold a home) update the checklist through client-intake.

## Rules
- Never retype identifiers or copy them into notes. The scanner masks them.
- The prior firm's figures are history, not a template: this year's return is prepared from this year's documents.
- An existing household is never recreated; use `document_ingest` on its return instead.
