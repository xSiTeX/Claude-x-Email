# Claude x Email — Mail Assistant

A complete email upgrade for **Claude Code** and the **Claude Desktop app**.

1. **Better emails.** Skills for writing, replying and proofreading with proper structure, subject, tone, language and signature.
2. **Attachments and images.** Attach any files and place pictures inside the mail text (inline).
3. **Any font.** Calibri by default, any other font by name, with fallbacks so the layout survives on other systems. Mixed fonts, bold, lists, links and tables via HTML.
4. **Permission levels.** From "drafts only" to "autonomous sending", with an allow-list and a daily limit.

Mails are built as `.eml` files that open as unsent drafts in Outlook, Thunderbird or Apple Mail. Sending is **off by default**.

## Permission levels

| Level | Behaviour |
|---|---|
| `draft_only` (default) | Claude creates drafts. It cannot send. You press Send yourself. |
| `ask_before_send` | Claude shows recipients, subject, text and attachments, asks you, and sends only after your explicit yes. |
| `autonomous` | Claude sends without asking, but only to **allow-listed** recipients (`name@x.com` or `@company.com`) and within the daily limit (default 10). Everything else falls back to asking. |

Only you change the level (tell Claude "set sending to ask before send"). Safeguards in the code: only drafts from Claude's drafts folder can be sent, the password is never stored in the profile, and `confirmed` must come from a yes in chat. Claude Code additionally asks permission for the `send_email` tool call unless you allow it.

## Install

Requires **Python 3** (`python --version`).

### Claude Code

```
/plugin marketplace add xSiTeX/Claude-x-Email
/plugin install mail-assistant@mail-tools
```

Or without installing, for one session:

```bash
claude --plugin-dir path/to/Claude-x-Email/mail-assistant
```

Then use `/mail Invoice for Mr Schmidt, attach C:\path\invoice.pdf`, or just ask in plain language.

### Claude Desktop app

- **Extension (recommended):** open `dist/mail-assistant.mcpb` (or build it, see below) and click *Install*. SMTP fields are optional and only needed for sending.
- **Skills:** upload the zips from `dist/skills/` in *Settings > Capabilities > Skills* so Claude also knows the writing rules.
- **Manual alternative:** add to `claude_desktop_config.json`:

```json
{ "mcpServers": { "mail-assistant": { "command": "python", "args": ["C:/path/to/Claude-x-Email/mail-assistant/server/server.py"] } } }
```

## First steps

1. *"Save my mail profile: name Max Muster, signature 'Freundliche Grüße, Max Muster', language German, font Calibri."*
2. *"Write Mr Schmidt that the invoice is attached, and attach C:\Users\me\invoice.pdf."* → draft opens in your mail app.
3. Pictures in the text: *"... and show logo.png inside the mail."*
4. Run `check_setup` ("check my mail setup") if something does not work.

## Enabling sending (optional)

1. Create an **app password** at your provider (Gmail or Outlook.com: account security > app passwords).
2. Claude Code: set environment variable `MAIL_SMTP_PASSWORD`. Desktop extension: enter it in the extension settings.
3. Tell Claude: *"Set up SMTP for smtp.gmail.com port 587 with user me@gmail.com"*, then *"set sending to ask before send"*. For autonomous: *"Allow autonomous sending to my own address and @mycompany.com, limit 5 per day."*

Never type the password in chat.

## Layout

| Path | Content |
|---|---|
| `mail-assistant/` | The plugin: `.claude-plugin/`, `.mcp.json`, `commands/`, `skills/`, `server/server.py` |
| `.claude-plugin/marketplace.json` | Lets Claude Code install the plugin from this repo |
| `desktop/` | `manifest.json` and `build.py` for the Desktop extension and skill zips |
| `dist/` | Built `mail-assistant.mcpb` and skill zips (`python desktop/build.py` rebuilds) |
| `tests/` | `python -m unittest discover -s tests` |

## Limits

- Total attachment size ~25 MB. Mail app rendering of fonts depends on the app and the fonts installed on the recipient's system.
- Sending uses plain SMTP with an app password. OAuth (Gmail API, Microsoft Graph) and reading the inbox are not included.
- Drafts are `.eml` files in `Documents/ClaudeEmailDrafts`, not entries in your mailbox's Drafts folder.

MIT License.
