---
name: client-status
description: Answer a taxpayer's "where is my return?" from their own file — stage in plain words, the one next action, who has it, and the flight log. Use for any status question in the client app (Home screen) or by text or email.
---

# Client status

**Screen:** C1 Home. **Agent:** client-concierge. **Tools:** `status_for_client` (tier 0).

## Steps
1. Call `status_for_client(return_id)` for the household's return. Never guess a stage.
2. Reply in this order, in three short lines at most:
   - where it is: `status_line`, and who has it (`with`) when that helps;
   - the one thing needed from them (`next_action`), or "nothing needed from you right now";
   - what happens next, from `remaining_stages[0]`.
3. If they ask about timing, use only what the file shows plus the standard line: "most e-filed refunds arrive within 21 days of IRS acceptance."

## Example
> Your return is in final review with Priya Shah, CPA. One thing is needed from you: proof of your January 14 estimated payment. After that, it comes to you to sign, usually within 2 days.

## Never
- Quote refund or balance amounts before the reviewer has signed off (the tool returns none until then).
- Speculate about why something is taking long; say who has it and offer `question_handoff`.
