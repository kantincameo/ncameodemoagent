---
name: board
description: Show the flight board, optionally filtered (all, at_risk, waiting_on_client, in_review)
---

Use the pipeline-management skill. Call `pipeline_board(filter="${ARGUMENTS:-all}")` and show a compact table: return, client, stage, blocker, crew, status. Under it, one next action for each DELAYED return.
