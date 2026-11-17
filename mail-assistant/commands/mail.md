---
description: Write a new email (DIN 5008 layout, attachments, images, fonts) and open it as a draft
argument-hint: <to whom, what about> [file paths]
---

Write a new email with the `write-email` skill (if that skill is not available, follow the Mail Assistant server instructions): $ARGUMENTS

- Default: German DIN 5008 layout and Calibri 11 pt, unless the user or the profile wants something else.
- Pass salutation, body and closing as separate fields; the server sets spacing, dates, times, amounts and phone numbers.
- A person's name ("Mehdi") goes into `to` as is: the server looks up the saved contact. Unknown person: ask for the address and offer `/mail-contacts`.
- Files named vaguely ("die letzte Rechnung"): `email_find_files`, show the hits, attach only what the user confirms.
- Recurring kind of mail (invoice, appointment, cancellation, follow-up, offer): consider a template (`email_templates`).
- Files the user names go into `attachments` (pictures to show inside the text into `inline_images`).
- Create the draft with `email_draft`, then follow the permission level. Never send in level `draft_only`.
- If no request was given, ask in one sentence who the mail is for and what it is about.
