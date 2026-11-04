---
name: client-notifications
description: Send the right client notification on the right channel at the right time — organizers, document received, missing documents, retakes, ready to sign, filed and accepted, estimated tax reminders, IRS letter acknowledgments — through approved templates and the Sentinel approval flow. Use for any outbound client message and for the Inbox screen.
---

# Client notifications

**Screens:** C4 Inbox (client), O5 Sentinel inbox (staff).
**Agents:** client-concierge (reads), client-services-admin and engagement-manager (send).
**Tools:** `notifications_list` (0), `notification_prefs_set` (1), `approval_request` (1), `client_send_message` (2).

## Catalog
| Notification | Trigger | Template | Approval |
| --- | --- | --- | --- |
| Document received | Upload recorded | tpl-doc-received | Auto (cleared) |
| Missing documents | Checklist gap after 5 days | tpl-missing-doc | First send per client; auto after 50 clean sends |
| Retake request | Quality check failed | (sent by intake) | Auto |
| Second 8879 reminder | 8879 unsigned after 2 days | tpl-8879-reminder | Client services (S-2.4) |
| Return ready to sign | Reviewer sign-off | tpl-return-ready | Reviewer, always (S-2.1) |
| Recommendation (extension, estimates) | Manager's at-risk list | tpl-advice | Manager, always (S-3.2) |
| IRS letter received | Notice registered | (sent by notice_register) | Auto acknowledgment only |
| Filed / accepted | E-file acknowledgment | — | Auto |

## Sending
1. `approval_request(kind="client_message", template_id=…, return_id=…, channel=…, preview=…)`.
2. If it comes back `approved` (template cleared for auto-send), send with `client_send_message(approval_id)`.
3. If `pending`, stop. The approver acts in the Sentinel inbox; you send only after it is approved. Never reword and resubmit to get around a denial.

## Respect the client
- Channel preferences and quiet hours (9 pm–8 am) — `client_send_message` schedules for 8 am when needed.
- At most one reminder per day. After three reminders with no reply, escalate to the engagement manager instead of sending a fourth.
- Edited approvals do not count toward a template's clean-send total.
