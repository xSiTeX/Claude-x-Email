---
description: Send a finished draft (follows your permission level)
argument-hint: [draft path; empty = choose from the newest drafts]
---

Send a draft: $ARGUMENTS

1. No path given: call `email_list_drafts` and let the user pick one (just one question).
2. Call `email_send` with `draft_path` (without `confirmed`).
3. If the answer is CONFIRMATION REQUIRED: show recipients, subject, attachments and the text, ask "Senden?" and wait. Only after an explicit yes call `email_send` again with `confirmed: true`.
4. Level `draft_only`: say the draft stays unsent and that `/mail-permissions` changes this.

Say "sent" only if the tool answered "Sent to ...".
