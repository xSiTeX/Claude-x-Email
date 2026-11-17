---
description: Write a new email (DIN 5008 layout, attachments, images, fonts) and open it as a draft
argument-hint: <to whom, what about> [file paths]
---

Write a new email with the `write-email` skill: $ARGUMENTS

- Files the user names go into `attachments` (pictures to show inside the text into `inline_images`).
- Create the draft with `email_draft`, then follow the permission level. Never send in level `draft_only`.
- If no request was given, ask in one sentence who the mail is for and what it is about.
