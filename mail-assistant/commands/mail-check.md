---
description: Check and correct an email text or draft against DIN 5008 (spacing, salutation, closing, spelling)
argument-hint: <pasted text or draft path; empty = newest draft>
---

Proofread with the `proofread-email` skill: $ARGUMENTS

- Pasted text: correct it, then run `email_check` with salutation, body and closing split apart, and show the layout.
- A path, or nothing: check that draft with `email_check` `draft_path` (nothing given: take the newest from `email_list_drafts`).
- Report what was fixed and what the user should look at. Create a new draft only if the user asks.
