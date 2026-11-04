# TaxPilot office — cloud edition (0.7.0)

Everything runs on Claude. There is no server to start and nothing to configure on your computer.

- **The app**: the published TaxPilot page — https://claude.ai/artifact/BP2UExpoTbyKg3RSqxEapD. Staff sign in by name; clients sign in with their `client:` login from onboarding.
- **The chat edition**: https://claude.ai/artifact/RwusfMNDf7S34W9LgcEfx7 — the same database and agents with no screens; the whole flow (onboard, sign, upload, approve, prepare, review, final 1040, file) by message, with buttons for anything a person must decide.
- **This plugin**: the same office agents (partner, engagement manager, preparer, reviewer, admin, billing, security) as a conversational front door in Claude. They read and write the page's database directly — the `cloud-brain` skill is the data contract — so what you ask here and what you click there are one record.

Install: Claude → Customize → Plugins → add `taxpilot-office-cloud.plugin`. Then, in a chat: "I'm Marcus, manager — what's waiting on me?"

Heavy agent work (scanning, draft writing, computing, packaging, sending) happens in the page, where Sentinel gates it; the plugin reads results, decides approvals, opens questions, moves returns along the allowed transitions and adds checklist items.


## What's new in 0.7.0
- Data contract covers the filed 1040 from the tax software (`final_lines`, `final_variance`), the year-over-year comparison (`return_compare`), the client organizer (`organizer_get`) and `not_needed` checklist items.
- Points to the chat edition as a second front end on the same database.
