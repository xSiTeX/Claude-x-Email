---
description: Use or manage templates for recurring mails (Rechnung, Termin, Absage, Nachfassen, Angebot, own)
argument-hint: [template name and values, e.g. "rechnung an Lisa, Nr 2026-114, 250 €, Frist 15.11." or "neu: ..."]
---

Templates: $ARGUMENTS

- Nothing given: `email_templates` and list them with their fields.
- Use a template: take the values from the user's words, call `email_check` with `template`, `fields` and the recipient (a contact name works), show the layout, then create the draft with `email_draft` and the same values. Ask once for missing fields.
- If the recipient is addressed with "du", rewrite the body to du form and pass it as `body` instead of using the template text unchanged.
- Save an own template: `email_template_set` with `name`, `subject`, `body` (placeholders as `{{feld}}`, without salutation and closing).
- Delete an own template only when the user clearly asks (`email_template_delete`).
