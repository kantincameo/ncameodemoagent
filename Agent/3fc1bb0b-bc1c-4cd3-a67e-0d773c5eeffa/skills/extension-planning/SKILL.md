---
name: extension-planning
description: Find returns that will not make the filing deadline, decide with the manager between an extension, filing with estimates, or a push to finish, and draft the client message for approval. Use from early March for April 15, and in the final weeks before October 15 for extended returns.
---

# Extension planning

**Screen:** O2 Flight board. **Agent:** engagement-manager.
**Tools:** `extension_candidates`, `pipeline_board` (0); `approval_request(kind="advice")` (1); `client_send_message` (2).

## Steps
1. `extension_candidates` → returns early in the pipeline with a blocker.
2. For each, classify:
   - **Not yet extended, before April 15** → recommend Form 4868 with an estimated payment from available data. Remind: an extension gives more time to file, not to pay.
   - **Already extended, near October 15** → no second extension. Options: finish now, or file with estimated figures (e.g. a late K-1) and amend with Form 1040-X when the real figures arrive. The CPA chooses.
3. Draft the client message in plain language, then `approval_request(kind="advice", template_id="tpl-advice")`. The manager approves; the CPA owns the recommendation.
4. After approval, `client_send_message`. If the client agrees to an extension, a person files it.

## Never
- Tell a client they "don't need to worry about the deadline".
- File anything. Filing is a human action in the tax software.
