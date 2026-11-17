---
description: "Show or set your mail profile (name, closing, signature, language, font)"
argument-hint: "[e.g. \"name Max Muster, closing Viele Grüße, font Calibri 11pt\"]"
---

Mail profile: $ARGUMENTS

- Nothing given: call `email_profile_get` and show name, closing, signature, language, font and the sign-off preview in a short list.
- Values given: save them with `email_profile_set`, then show the sign-off preview from the result.
- Keep the parts apart: `closing` = Grußformel ("Freundliche Grüße"), `name` = sender name, `signature` = contact block only (company, address, phone in DIN format like +49 30 1234567, web).
- Optional: `logo` (image path, shown under the signature, `logo_width` in px), `signature_html` (rich signature), `draft_target` `outlook` (drafts straight into classic Outlook on Windows) or `file`.
- Missing a value the user clearly wants? Ask once. Never store passwords.
