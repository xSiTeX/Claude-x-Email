---
name: proofread-email
description: Use when the user wants an email checked, corrected, shortened, made more polite/formal/friendly, laid out to DIN 5008, or translated before sending.
---

# Proofreading an email

1. Fix spelling, grammar, punctuation and wrong salutations. Keep the user's voice and facts unchanged.
2. Apply requested changes only (shorter, more formal, translate). Do not add new claims.
3. Split the result into salutation, body and closing and run `email_check` with them (or `draft_path` for an existing draft). It fixes spacing to DIN 5008 and lists remaining problems.
4. Reply with the corrected layout from the tool first, then at most 3 bullets on what changed. Flag anything risky (attachment mentioned but missing, unclear request, wrong recipient name, missing deadline).
5. If the mail mentions an attachment ("anbei", "attached") but no file is named, ask which file.
6. If the user wants a draft, continue with `write-email` steps 4-6.
