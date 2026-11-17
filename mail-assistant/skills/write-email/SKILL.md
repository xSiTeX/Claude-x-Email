---
name: write-email
description: Use whenever the user wants to write, compose, draft or send an email, in any language. Lays the mail out to DIN 5008 (German) or international business style, applies the saved profile (name, closing, signature, font), attaches files and inline images, and follows the user's permission level for sending.
---

# Writing an email

## 1. Profile
Call `email_profile_get` once per session: `name`, `closing`, `signature`, `language`, `tone`, `font`, permission level. No profile and the user writes regularly: suggest `/mail-profile` once, do not block on it.

## 2. Gather only what is missing
Needed: recipient, purpose, key facts (dates, amounts, names), files. Ask one short question if something essential is missing, otherwise write. Never invent facts, dates, prices or promises.
- **Recipient by name** ("Mehdi"): put the name into `to`. The server takes the address, du/Sie, salutation and language from the saved contact (`email_contacts`). Unknown name: ask for the address and offer to save it with `email_contact_set` (du/Sie, Frau/Herr).
- **Write in the contact's form of address**: "du" → du, dich, dein (lower case); "sie" → Sie, Ihnen, Ihr.
- **Recurring mails** (invoice, appointment, cancellation, follow-up, offer, own ones): `email_templates`, then `template` + `fields` in `email_draft`.
- **Vague files** ("die letzte Rechnung", "das Foto von gestern"): `email_find_files`, show the hits, attach only after the user confirmed which file.

## 3. Write the content
- **Subject:** specific, max ~60 characters ("Rechnung 2026-114 für Oktober", not "Frage"). No "Betreff:".
- **Salutation:** fits language and relationship (de: "Sehr geehrte Frau Müller," / "Hallo Max,"; en: "Dear Ms Miller," / "Hi Max,"). Use the recipient's language or the thread's.
- **Body:** purpose in the first sentence, short paragraphs (2-4 sentences), one clear request or next step with a deadline if there is one. German after "Anrede," starts lower case.
- **Tone:** the user's wish, else profile `tone`, else polite and direct. No filler, no exaggerated apologies.
- **Attachments:** mention each file in the text ("Im Anhang finden Sie die Rechnung als PDF.").
- **Closing:** pick one that fits the tone ("Freundliche Grüße", "Viele Grüße", "Kind regards,"), else leave it to the profile.

## 4. Pass the parts separately (the server does the layout)
Call `email_draft` with:
- `salutation`: only the salutation line
- `body` (or `html_body`): only the main text. **No salutation, closing, name or signature inside.**
- `closing`: only if it differs from the profile
- `attachments` (absolute paths), `inline_images` (pictures inside the text, `<img src="cid:img1">` in `html_body`)
- `font` / `font_size` only if the user wants something other than the profile (any font name works; fallbacks are added)
- `salutation` may be left out when the recipient is a saved contact; the server then uses the contact's salutation. Pass your own only if it should differ, and pass on any "Please check" about it.
- `target: "outlook"` puts the draft into classic Outlook's Drafts folder (or set it once in the profile, `draft_target`). If Outlook is not available the .eml file opens instead; say so.

The server then sets exactly one blank line between all blocks, the DIN 5008 closing (no comma, blank line, name), the signature separator and the font on every paragraph. Use `html_body` only for bold, lists, links, tables or mixed fonts. Full rules: `references/din5008.md`.

Unsure about a layout or a long text? Run `email_check` with the same fields first. It shows the final layout with line numbers and writes nothing.

## 5. After the draft: permission level
- **draft_only:** stop. The draft is open in the mail app, unsent; the user sends it.
- **ask_before_send:** show recipients, subject, text and attachments, ask "Senden?". Only after an explicit yes call `email_send` with `confirmed: true`.
- **autonomous:** call `email_send` without `confirmed`. If it answers CONFIRMATION REQUIRED, ask like ask_before_send.
Details and changes: `email-permissions` skill.

## 6. Report
Show subject and the layout from the tool result, name attachments, and pass on "Fixed automatically" and "Please check" points briefly. State exactly what happened: draft only, or sent to whom. Never claim a mail was sent unless `email_send` returned "Sent to". Offer one concrete adjustment (shorter, more formal, other language).

Do not attach files the user did not name. Ask before attaching anything sensitive.
