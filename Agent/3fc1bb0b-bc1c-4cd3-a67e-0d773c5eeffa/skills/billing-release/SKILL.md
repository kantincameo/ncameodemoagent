---
name: billing-release
description: Draft and send invoices from the engagement letter plus complexity flags, route over-tolerance invoices for manager approval, and confirm payment before a return is released for filing. Use for "invoice the Hoffmann return", "is Feld clear to file?", or billing items in the Sentinel inbox.
---

# Billing release

**Screen:** O5 Sentinel inbox (billing queue). **Agent:** billing-agent.
**Tools:** `invoice_draft` (1), `invoice_send` (2), `billing_release_status` (0), `approval_request(kind="invoice")` (1).

## Steps
1. `invoice_draft(return_id, over_estimate_pct)` with the complexity adjustment the preparer logged (new K-1, rental schedule, extra state).
2. If `needs_approval` is false (within the 10% tolerance): `invoice_send(invoice_id)`.
3. If true: `approval_request(kind="invoice", preview=<reason for the increase>)`. After the manager approves, `invoice_send(invoice_id, approval_id)`.
4. Before a return moves to `ready_to_file`: `billing_release_status`. Released = paid or a payment arrangement on file. Otherwise the return holds and client services sends the payment reminder template.

## Never
- Take or store card or bank details. Payment happens in the secure checkout.
- Write off, discount, or exceed tolerance without the manager's approval.
