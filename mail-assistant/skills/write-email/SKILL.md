---
name: write-email
description: Use whenever the user wants to write, compose, draft or send an email, in any language. Applies good email craft, the saved profile (name, signature, language, font), attachments, inline images and the user's permission level for sending.
---

# Writing an email

## 1. Load the profile and permission level
Call `get_profile` once per session. Use its `language`, `name`, `signature`, `tone`, font and `autonomy.mode`. If there is no profile and the user wants one, offer `set_profile`. Run `check_setup` if anything misbehaves.

## 2. Gather only what is missing
Needed: recipient, purpose, key facts (dates, amounts, names), files and images. Ask one short question if something essential is missing, otherwise write. Never invent facts, dates, prices or promises.

## 3. Write it well
- **Subject:** specific, under ~8 words ("Invoice 2026-114 attached", not "Question").
- **Opening:** salutation that fits language and relationship (de: "Sehr geehrte Frau X," formal / "Hallo Max," informal; en: "Dear Ms X," / "Hi Max,"). Use the recipient's language or the thread's.
- **Body:** purpose in the first sentence, short paragraphs, one clear request or next step with a deadline if there is one. 3-6 sentences for simple mails.
- **Tone:** the user's wish, else the profile `tone`, else polite and direct. No filler ("I hope this finds you well"), no exaggerated apologies.
- **Attachments:** mention each attached file in the text ("Im Anhang finden Sie ...") so text and attachments agree.
- **Closing:** matching sign-off; the profile signature is appended automatically.

## 4. Format (fonts, images, files)
- Default font is the profile font, else Calibri 11pt. Any font name works via `font` / `font_size` (a fallback stack is added automatically).
- Plain `body` is converted to clean paragraphs. For bold, lists, links, tables or mixed fonts pass `html_body` (inner HTML, `<span style="font-family:Cambria">` for a different font in one passage).
- Files: `attachments` (absolute paths). Pictures shown inside the text: `inline_images`, referenced as `<img src="cid:img1">` (img2, img3 ...). Pictures not referenced are placed at the end.
- Check sizes with `list_attachments_preview` when files are large (limit ~25 MB).

## 5. Create the draft, then follow the permission level
Always call `create_email_draft` first (`open: true`). Then:
- **draft_only:** stop. Say the draft is open in the mail app, unsent, and the user sends it.
- **ask_before_send:** show recipients, subject, text and attachment names, ask "Soll ich senden?". Only after an explicit yes call `send_email` with `confirmed: true`.
- **autonomous:** call `send_email` (without `confirmed`). If the tool answers CONFIRMATION REQUIRED, treat it as ask_before_send.
See the `email-permissions` skill for details and for changing the level.

## 6. Report
Show final subject and text, name attachments and images, and state exactly what happened: draft only, or sent to whom. Never claim a mail was sent unless `send_email` returned "Sent". Offer one concrete adjustment (shorter, more formal, other language).

Do not attach files the user did not name. Ask before attaching anything sensitive.
