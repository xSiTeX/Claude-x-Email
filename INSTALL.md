# Setup instructions for Claude

**This file is for you, Claude (or any AI assistant).** A user sent you the link to this repository because they want the Mail Assistant set up. Follow these steps in order. Talk to the user in their language (usually German), in short plain sentences; they may not be technical. Do the work yourself where you can; ask only for what only the user can decide or click.

Repository: https://github.com/xSiTeX/Claude-x-Email

## Step 0: What can you do here?

- **You can run shell commands** (Claude Code, or Claude Desktop with a terminal/computer tool): follow **Path A**. It sets up everything automatically.
- **You cannot run commands** (normal chat in the Claude Desktop app or claude.ai): follow **Path B**. Guide the user click by click.

---

## Path A: automatic setup (you run the commands)

### A1. Python

Run `python --version`. On Windows also try `py --version` if that fails.

- Needs **Python 3.8 or newer**. If you get a version, go to A2.
- On Windows, "python" may open the Microsoft Store or print nothing. Treat that as "not installed".
- **Not installed:** tell the user Python is needed and ask for permission to install it. Then:
  - Windows: `winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements`
  - macOS: `brew install python` (if Homebrew exists), otherwise ask the user to install it from https://www.python.org/downloads/
  - Linux: the system package manager, e.g. `sudo apt install python3` (the user has to type the sudo password themselves)
  
  After installing, open a new terminal (or use the full path, for example `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`) and check `python --version` again.

### A2. Get the repository

Install to the user's home folder:

- With git: `git clone https://github.com/xSiTeX/Claude-x-Email.git "<HOME>/Claude-x-Email"`. If the folder already exists, run `git -C "<HOME>/Claude-x-Email" pull` instead.
- Without git: download https://github.com/xSiTeX/Claude-x-Email/archive/refs/heads/main.zip, extract it, and rename the folder to `Claude-x-Email` in the home folder.

### A3. Ask the user for their profile (one message, all questions at once)

1. Full name (shown under the closing)
2. Closing: default "Freundliche Grüße"
3. Signature lines: company, address, phone, website. Optional, may be empty.
4. Language of their mails: default German (`de`)
5. Font: default Calibri 11pt
6. Their own email address (optional)
7. Which Claude they use: Claude Code, the Claude Desktop app, or both

Suggest the defaults so the user can just answer "ja, Standard".

### A4. Run the installer

From the repository folder:

```
python install.py --name "<name>" --closing "<closing>" --signature "<line 1>|<line 2>|<line 3>" --language de --font Calibri --font-size 11pt --from "<email>"
```

- Leave out options the user did not give. Separate signature lines with `|`.
- Add `--no-desktop` if they do not use the Desktop app, or `--no-code` if they do not use Claude Code.
- The installer checks Python and installs the plugin in Claude Code (`claude plugin marketplace add` + `claude plugin install`). It also opens the Desktop extension installer and saves the profile. Last, it runs a self-test.
- If opening the Desktop installer fails, or the user prefers no clicking: `python install.py --desktop-config --no-code`. This writes `claude_desktop_config.json` and keeps a `.bak` backup.

Read the output. Every `[X]` is an error you must fix or explain. Every `[!]` needs the action it describes.

### A5. Tell the user what to do now

- **Claude Code:** start a new session, then type `/mail-setup`.
- **Desktop app:** in the window that opened, click **Installieren** and leave the SMTP fields empty. Then fully quit the app (also from the system tray) and start it again. With `--desktop-config`, only the restart is needed.
- **First test:** "Schreib eine Test-Mail an mich selbst" or `/mail-help`.

### A6. Do NOT do these on your own

- Do not enable sending and do not change the permission level. It stays `draft_only` until the user asks for more; then use `/mail-permissions` or the `email-permissions` skill.
- Never ask for a password in the chat. Sending needs an app password that the user sets themselves as an environment variable. Run `/mail-help Senden einrichten` for the steps.
- Do not add contacts or templates unless the user asks. Offer it once at the end: "Soll ich deine wichtigsten Kontakte anlegen? Dann reicht später `/mail Name, …`."

---

## Path B: the user clicks (you cannot run commands)

Send the user these steps in German, one block at a time, and wait until they say each is done.

1. **Python installieren** (falls noch nicht da):
   - Windows: https://www.python.org/downloads/ öffnen, auf „Download Python“ klicken, die Datei starten.
   - **Wichtig:** Unten im ersten Fenster den Haken **„Add python.exe to PATH“** setzen, dann „Install Now“.
2. **Erweiterung herunterladen:** https://github.com/xSiTeX/Claude-x-Email/raw/main/dist/mail-assistant.mcpb
3. **Installieren:** Die heruntergeladene Datei `mail-assistant.mcpb` doppelklicken. Wenn das nicht geht: in der Claude Desktop-App *Einstellungen → Erweiterungen* öffnen und die Datei dorthin ziehen. Dann auf **Installieren** klicken. Die SMTP-Felder leer lassen.
4. **Claude neu starten:** die App ganz beenden (auch unten rechts im Infobereich) und wieder öffnen.
5. **Profil anlegen:** Schreib mir „Richte mein Mail-Profil ein: Name …, Grußformel Freundliche Grüße, Signatur …“.
6. **Testen:** „Schreib eine Test-Mail an mich selbst.“

After step 4 you have the `email_*` tools. Use `email_profile_set` for step 5 and `email_setup_check` to verify.

Optional: the skill zips at https://github.com/xSiTeX/Claude-x-Email/tree/main/dist/skills can be uploaded under *Einstellungen → Fähigkeiten → Skills*. This is not required, because the extension brings its own rules.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python` not found after installing | New terminal; Windows: reinstall with "Add python.exe to PATH", or `winget install -e --id Python.Python.3.12` |
| `[!] Der Befehl 'python' fehlt im PATH` | Same as above. For the Desktop app only, `python install.py --desktop-config` works with the full path |
| `claude plugin ...` failed | Have the user type in Claude Code: `/plugin marketplace add xSiTeX/Claude-x-Email`, then `/plugin install mail-assistant@mail-tools` |
| Desktop shows no Mail Assistant tools | Fully quit and restart the app; check *Einstellungen → Erweiterungen*; or `python install.py --desktop-config` |
| Anything else | `python install.py --check` and the "Fehlerbehebung" section of `mail-assistant/ANLEITUNG.md` |

When everything works, give the user a short summary: what is installed, where the drafts are saved (`Dokumente\ClaudeEmailDrafts`), and the three most useful commands: `/mail`, `/mail-contacts`, `/mail-help`. In the Desktop app, they can just ask in normal sentences.
