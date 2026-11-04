---
name: goal
description: Give TaxPilot a goal for a return (e.g. "get Patel ready for Priya's review") and it plans, runs and pauses at approvals
---

Goal: $ARGUMENTS

1. Identify the return and your persona's scope. If the return is outside your assignment, say so and stop.
2. Write a short plan: numbered steps, each with the tool, its tier (0 read, 1 draft, 2 needs approval, 3 human only) and the person who approves where one is needed. Use the skills: return-preparation, review-packet, pipeline-management, client-notifications, sentinel-approvals.
3. Run the tier 0 and 1 steps. For tier 2, call `approval_request` and stop at that step, saying who must approve. Never attempt tier 3 or human-only steps; name the person who does them.
4. Finish with: what is done, what is waiting and on whom, and the next step once the approval lands.
