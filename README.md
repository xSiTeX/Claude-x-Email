# Claude x Email — Mail Assistant

A complete email upgrade for **Claude Code** and the **Claude Desktop app**.

1. **Correct layout.** Every mail is laid out to **DIN 5008** (German) or international business style: exactly one blank line between salutation, paragraphs, closing, name and signature, no comma after a German closing, lower-case start after "Anrede,", clean subject. The server does the spacing, so it is right every time.
2. **Better emails.** Skills for writing, replying and proofreading with structure, tone, language and signature.
3. **Attachments and images.** Attach any files and place pictures inside the text.
4. **Any font.** Calibri 11 pt by default, any other font by name, with fallbacks. Font set on every paragraph so Outlook keeps it.
5. **Permission levels.** From "drafts only" to "autonomous sending", with an allow-list and a daily limit.

Mails are built as `.eml` files that open as unsent drafts in Outlook, Thunderbird or Apple Mail. Sending is **off by default**.

## Commands

| Command | What it does |
|---|---|
| `/mail <request> [files]` | Write a new email as a draft |
| `/mail-reply <mail>` | Answer a received email |
| `/mail-check [text or draft]` | Check against DIN 5008 and correct |
| `/mail-send [draft]` | Send a draft (by permission level) |
| `/mail-profile [values]` | Name, closing, signature, language, font |
| `/mail-permissions [level]` | Draft only / ask before send / autonomous |
| `/mail-setup` | Overview and diagnosis |

You can also just ask in plain language ("Schreib Herrn Schmidt, dass die Rechnung im Anhang ist").

## What a mail looks like (DIN 5008)

```
Sehr geehrte Frau Müller,

anbei erhalten Sie die Rechnung für Oktober.

Bei Fragen melden Sie sich gerne.

Freundliche Grüße

Max Muster

-- 
Muster GmbH
Telefon +49 30 1234567
```

Fixed automatically: missing blank lines, double spaces, indents, extra blank lines, comma after the salutation, comma after a German closing, "Betreff:" and a final full stop in the subject, "Ich/Vielen Dank" after "Anrede," to lower case.
Warnings: attachment not mentioned (or mentioned but missing), phone format (`+49 30 1234567`), long subject, capitals, "!!", long paragraphs, font size outside 10 to 12 pt, invalid addresses.

Full rules: [`din5008.md`](mail-assistant/skills/write-email/references/din5008.md).

## Tools (MCP server)

| Tool | Purpose |
|---|---|
| `email_draft` | Create the draft (salutation, body, closing as separate fields) |
| `email_check` | Show the exact layout with line numbers and norm warnings; writes nothing |
| `email_send` | Send a draft, following the permission level |
| `email_list_drafts` | Newest drafts |
| `email_profile_get` / `email_profile_set` | Profile and sign-off preview |
| `email_permissions_set` | Change the permission level |
| `email_setup_check` | Diagnosis |
| `email_files_check` | File sizes against the 25 MB limit |

The version 3 tool names (`create_email_draft`, `send_email`, ...) still work.

## Permission levels

| Level | Behaviour |
|---|---|
| `draft_only` (default) | Claude creates drafts. It cannot send. You press Send yourself. |
| `ask_before_send` | Claude shows recipients, subject, text and attachments, asks you, and sends only after your explicit yes. |
| `autonomous` | Claude sends without asking, but only to **allow-listed** recipients (`name@x.com` or `@company.com`) and within the daily limit (default 10). Everything else falls back to asking. |

Only you change the level (`/mail-permissions`). Safeguards in the code: only drafts from Claude's drafts folder can be sent, the password is never stored, and `confirmed` must come from a yes in chat. Claude Code also asks permission for the `email_send` call unless you allow it.

## Install

Requires **Python 3** (`python --version`).

### Claude Code

```
/plugin marketplace add xSiTeX/Claude-x-Email
/plugin install mail-assistant@mail-tools
```

Update later with `/plugin marketplace update mail-tools`. Without installing, for one session:

```bash
claude --plugin-dir path/to/Claude-x-Email/mail-assistant
```

### Claude Desktop app

- **Extension:** open `dist/mail-assistant.mcpb` and click *Install*. SMTP fields are optional and only needed for sending.
- **Skills:** upload the zips from `dist/skills/` in *Settings > Capabilities > Skills* so Claude knows the writing and layout rules. (Slash commands are a Claude Code feature; in the Desktop app just ask in plain language.)
- **Manual alternative:** add to `claude_desktop_config.json`:

```json
{ "mcpServers": { "mail-assistant": { "command": "python", "args": ["C:/path/to/Claude-x-Email/mail-assistant/server/server.py"] } } }
```

## First steps

1. `/mail-profile name Max Muster, closing Freundliche Grüße, signature "Muster GmbH, Telefon +49 30 1234567", language de, font Calibri 11pt`
2. `/mail Herr Schmidt, Rechnung Oktober im Anhang, C:\Users\me\rechnung.pdf` → draft opens in your mail app.
3. Pictures in the text: "... and show logo.png inside the mail."
4. `/mail-setup` if something does not work.

## Enabling sending (optional)

1. Create an **app password** at your provider (Gmail or Outlook.com: account security > app passwords).
2. Claude Code: set environment variable `MAIL_SMTP_PASSWORD`. Desktop extension: enter it in the extension settings.
3. Tell Claude: *"Set up SMTP for smtp.gmail.com port 587 with user me@gmail.com"*, then `/mail-permissions ask_before_send`. For autonomous: `/mail-permissions autonomous me@gmail.com @mycompany.com limit 5`.

Never type the password in chat.

## Layout of this repo

| Path | Content |
|---|---|
| `mail-assistant/` | The plugin: `.claude-plugin/`, `.mcp.json`, `commands/`, `skills/`, `server/server.py` |
| `.claude-plugin/marketplace.json` | Lets Claude Code install the plugin from this repo |
| `desktop/` | `manifest.json` and `build.py` for the Desktop extension and skill zips |
| `dist/` | Built `mail-assistant.mcpb` and skill zips (`python desktop/build.py` rebuilds) |
| `tests/` | `python -m unittest discover -s tests` |

## Limits

- Total attachment size ~25 MB. Font rendering depends on the mail app and the fonts installed on the recipient's system.
- Sending uses plain SMTP with an app password. OAuth (Gmail API, Microsoft Graph) and reading the inbox are not included.
- Drafts are `.eml` files in `Documents/ClaudeEmailDrafts`, not entries in your mailbox's Drafts folder.

MIT License.
