---
name: client-approvals
description: Guide a taxpayer through what they must approve — engagement letter, consent to use tax information (§7216), IRS records access (Form 8821), extension, the return summary and Form 8879, and the invoice. Use on the Approvals screen or when a client asks "what do I need to sign?".
---

# Client approvals

**Screen:** C3 Approvals. **Agent:** client-concierge. **Tools:** `client_approvals_list` (0).
Signing itself is `client_sign`, which is human-only: it is recorded by the portal's e-signature flow when the client taps the button, never by you.

## Steps
1. `client_approvals_list(return_id)`. Lead with what is waiting, then what is done.
2. Explain each waiting item in one plain sentence:
   - **Engagement letter** — what the firm will do and the fee.
   - **Consent to use tax information** — permission the firm needs to use your information this way.
   - **Form 8821** — lets the firm see your IRS records so nothing the IRS has is missed.
   - **Extension (Form 4868)** — more time to file, not more time to pay.
   - **Form 8879** — lets the firm file electronically for you. Sign only after reviewing the summary.
   - **Invoice** — paid in the secure checkout.
3. Point to the button in the app. If something in the return summary looks wrong, offer `question_handoff` before they sign.

## Never
- Sign, accept or pay on the client's behalf.
- Explain how a figure on the return was calculated beyond the "what changed" lines the reviewer wrote. Questions about figures go to the reviewer.
