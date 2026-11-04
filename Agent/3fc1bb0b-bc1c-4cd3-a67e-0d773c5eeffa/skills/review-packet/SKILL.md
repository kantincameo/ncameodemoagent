---
name: review-packet
description: Build the signing CPA's one-page review packet — refund or balance due vs prior year, what moved and why, transcript tie-out, diagnostics and a ranked judgment queue with facts, options and a recommendation. Use when a return enters review or the reviewer asks "what do I need to look at on Patel?".
---

# Review packet

**Screen:** O4 Review. **Agent:** reviewer (independent; no write tools on the return).
**Tools:** `review_packet`, `document_fields`, `transcript_tieout` (0); `return_advance` for send-back (1).

## Build it
1. `review_packet(return_id)` → figures, judgment items, tie-out.
2. **Headline:** federal refund or balance due; state; prior year for comparison.
3. **What moved, and why:** each material line change (over 10% or $1,000) with its cause tied to a document. "Wages +18%: new job at Northwind Labs; both W-2s tie to the transcript."
4. **Tie-out:** matched/total and any exception.
5. **Diagnostics:** errors first, then warnings, each with a one-line explanation.
6. **Judgment queue,** most consequential first. For each: facts, options, your recommendation and why, and the rule or threshold involved (e.g. the $25,000 rental allowance phases out between $100,000 and $150,000 MAGI).

## After the CPA decides
`judgment_decide` and `review_sign_off` happen in the UI. Sign-off moves the return to `client_approval` and queues the client message (rule S-2.1) for the reviewer's approval.

## Send back
If something is wrong, `return_advance(to_stage="in_prep", note=…)` with specific, actionable notes.

## Never
- Read the preparer agent's reasoning or notes before forming your view.
- Present a recommendation as a decision.
