---
description: "Check the mail setup and show all mail commands"
---

Run `email_setup_check` and report the result in a few lines, including any "To do" items.

Then show the commands:

| Command | What it does |
|---|---|
| `/mail <request> [files]` | Write a new email as a draft |
| `/mail-reply <mail>` | Answer a received email |
| `/mail-check [text or draft]` | Check against DIN 5008 and correct |
| `/mail-send [draft]` | Send a draft (by permission level) |
| `/mail-profile [values]` | Name, closing, signature, logo, language, font, Outlook |
| `/mail-contacts [data]` | Contacts with address, du/Sie, salutation |
| `/mail-templates [name]` | Templates for recurring mails |
| `/mail-permissions [level]` | Draft only / ask before send / autonomous |
| `/mail-setup` | This overview and diagnosis |
| `/mail-help [topic]` | Detailed explanation in German |

These short names exist when `install.py` created them; the plugin names `/mail-assistant:mail` etc. always work.

If the profile has no name yet, offer `/mail-profile` as the first step.
