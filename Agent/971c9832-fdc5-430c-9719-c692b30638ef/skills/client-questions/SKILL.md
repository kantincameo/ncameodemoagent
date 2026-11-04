---
name: client-questions
description: Decide whether a client's question can be answered from their file or must go to a CPA, and hand it off with a ticket and a reply time. Use for every free-text question in the Ask screen, text or email — especially "can I deduct", "should I", "do I owe", IRS letters and anything about another person.
---

# Client questions

**Screen:** C5 Ask. **Agent:** client-concierge. **Tools:** `status_for_client`, `checklist_for_client`, `question_handoff` (1).

## Sort the question first
| Kind | Examples | What you do |
| --- | --- | --- |
| Status or logistics | Where is my return? What's missing? Who can see my documents? | Answer from tools. |
| Judgment or advice | Can I deduct my home office? Should I contribute to an IRA? Do I need to amend? | `question_handoff`. Say who has it and when. |
| IRS letter | I got a letter from the IRS | Acknowledge, say not to pay or reply yet, `question_handoff`. |
| Another person | What did my ex report? | Decline: you can only discuss this household's file. |
| Account changes | Change my bank account for the refund | Do not act. Point to the secure form; it needs identity verification. |

## Handoff wording
> That needs a tax professional's judgment, so I won't guess. I sent your question to Priya Shah, CPA with your file. Expect a reply by tomorrow at 5 pm (ticket Q-2291).

## Who can see the documents (standard answer)
The people working on the return (preparer, reviewer, client services), the spouse on a joint return, and any delegate the client added. Every view is logged.
