#!/usr/bin/env python3
"""Mail Assistant installer (Python standard library only).

Sets everything up in one go:
  1. checks Python
  2. installs the plugin in Claude Code (if the `claude` command exists) and the short commands /mail, /mail-reply ...
     in ~/.claude/commands (plugin commands are otherwise only reachable as /mail-assistant:mail)
  3. installs the extension in the Claude Desktop app (opens the .mcpb, or writes the config with --desktop-config)
  4. saves the mail profile (name, closing, signature, language, font) if given
  5. runs a self-test of the mail server

Examples:
  python install.py
  python install.py --name "Max Muster" --closing "Freundliche Grüße" \
                    --signature "Muster GmbH|Musterstraße 1, 12345 Berlin|Telefon +49 30 1234567" \
                    --language de --font Calibri --font-size 11pt --from max@muster.de
  python install.py --check            only diagnose, change nothing
  python install.py --desktop-config   Desktop: write claude_desktop_config.json instead of opening the .mcpb

Signature lines are separated by "|".
"""
import argparse, glob, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(ROOT, "mail-assistant", "server", "server.py")
MCPB = os.path.join(ROOT, "dist", "mail-assistant.mcpb")
REPO = "xSiTeX/Claude-x-Email"
PLUGIN = "mail-assistant@mail-tools"

OK, WARN, FAIL, INFO = "[OK]  ", "[!]   ", "[X]   ", "      "
results = []


def say(tag, text):
    print(tag + text)
    results.append((tag, text))


def run(cmd, timeout=180):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except Exception as e:
        return 1, str(e)


# ------------------------------------------------------------------ 1. Python
def check_python():
    v = sys.version_info
    if v < (3, 8):
        say(FAIL, "Python %d.%d ist zu alt. Benötigt wird Python 3.8 oder neuer." % (v.major, v.minor))
        return False
    say(OK, "Python %d.%d.%d (%s)" % (v.major, v.minor, v.micro, sys.executable))
    # The plugin and the Desktop extension start the server with the command "python".
    code, out = run(["python", "--version"], 30) if shutil.which("python") else (1, "")
    if code == 0 and "Python 3" in out:
        say(OK, "Befehl 'python' funktioniert (%s)." % out)
    else:
        say(WARN, "Der Befehl 'python' fehlt im PATH. Claude Code und die Desktop-App starten den Mail-Server "
                  "aber mit 'python'. Windows: Python von python.org neu installieren und 'Add python.exe to "
                  "PATH' anhaken, oder 'winget install -e --id Python.Python.3.12'. macOS/Linux: einen Alias "
                  "'python' -> python3 anlegen. Für die Desktop-App hilft auch: install.py --desktop-config")
    return True


# ------------------------------------------------------------------ 2. Claude Code
def install_claude_code(check_only):
    exe = shutil.which("claude")
    if not exe:
        say(INFO, "Claude Code (Befehl 'claude') nicht gefunden, übersprungen. Falls Claude Code doch genutzt "
                  "wird, dort eingeben: /plugin marketplace add %s  und  /plugin install %s" % (REPO, PLUGIN))
        return
    if check_only:
        code, out = run([exe, "plugin", "list"], 60)
        say(OK if "mail-assistant" in out else INFO,
            "Claude Code: Plugin %s." % ("installiert" if "mail-assistant" in out else "noch nicht installiert"))
        return
    code, out = run([exe, "plugin", "marketplace", "add", REPO])
    if code != 0 and "already" not in out.lower():
        code2, out2 = run([exe, "plugin", "marketplace", "update", "mail-tools"])
        if code2 != 0:
            say(WARN, "Claude Code: Marketplace konnte nicht automatisch hinzugefügt werden (%s). Bitte in Claude "
                      "Code eingeben: /plugin marketplace add %s" % (out[-200:], REPO))
            return
    else:
        run([exe, "plugin", "marketplace", "update", "mail-tools"])
    code, out = run([exe, "plugin", "install", PLUGIN])
    if code == 0 or "already" in out.lower():
        say(OK, "Claude Code: Plugin installiert. Eine NEUE Claude-Code-Sitzung starten, dann gibt es /mail.")
    else:
        say(WARN, "Claude Code: automatische Installation fehlgeschlagen (%s). Bitte in Claude Code eingeben: "
                  "/plugin install %s" % (out[-200:], PLUGIN))


# ------------------------------------------------------------------ 2b. short command names
SHORTCUT_MARK = "<!-- mail-assistant shortcut: managed by install.py, safe to delete -->"


def install_shortcuts(check_only, remove=False):
    """Plugin commands are namespaced (/mail-assistant:mail). Personal commands in ~/.claude/commands give the short
    names /mail, /mail-reply, ... They contain the same instructions as the plugin commands."""
    src = os.path.join(ROOT, "mail-assistant", "commands")
    dst = os.path.join(os.path.expanduser("~"), ".claude", "commands")
    names = sorted(f for f in os.listdir(src) if f.endswith(".md"))
    done, skipped, present = [], [], []
    for fn in names:
        target = os.path.join(dst, fn)
        ours = False
        if os.path.isfile(target):
            with open(target, encoding="utf-8") as f:
                ours = SHORTCUT_MARK in f.read()
            present.append(fn) if ours else None
            if not ours:
                skipped.append(fn)
                continue
        if check_only:
            continue
        if remove:
            if ours:
                os.remove(target)
                done.append(fn)
            continue
        with open(os.path.join(src, fn), encoding="utf-8") as f:
            text = f.read().replace("\r\n", "\n")
        front = text.split("---", 2)[1].strip() if text.startswith("---") else ""
        name = fn[:-3]
        # A thin forwarder: always uses the current plugin version, never goes stale.
        body = ("---\n%s\n---\n\nUse the Skill tool to run the plugin command `mail-assistant:%s` with these "
                "arguments, and follow it exactly: $ARGUMENTS\n\nIf that skill does not exist, the Mail Assistant "
                "plugin is not installed or is disabled: tell the user to run `python install.py` in the "
                "Claude-x-Email folder (or `/plugin install mail-assistant@mail-tools`) and start a new session.\n\n%s\n"
                % (front, name, SHORTCUT_MARK))
        os.makedirs(dst, exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(body)
        done.append(fn)
    short = lambda lst: ", ".join("/" + f[:-3] for f in lst)
    if check_only:
        say(OK if len(present) == len(names) else INFO, "Kurze Befehle: %d von %d vorhanden (%s)." % (
            len(present), len(names), short(present) or "keine"))
    elif remove:
        say(OK, "Kurze Befehle entfernt: %s" % (short(done) or "keine"))
    else:
        say(OK, "Kurze Befehle angelegt: %s (in %s)." % (short(done), dst))
    if skipped:
        say(WARN, "Nicht überschrieben, weil dort schon eigene Befehle mit diesem Namen liegen: %s. Dafür gibt es "
                  "weiter /mail-assistant:<name>." % short(skipped))


# ------------------------------------------------------------------ 3. Claude Desktop
def desktop_dirs():
    """Folders where Claude Desktop keeps claude_desktop_config.json (classic and Microsoft Store install)."""
    dirs = []
    if sys.platform == "win32":
        appdata, local = os.environ.get("APPDATA", ""), os.environ.get("LOCALAPPDATA", "")
        dirs += glob.glob(os.path.join(local, "Packages", "Claude_*", "LocalCache", "Roaming", "Claude"))
        dirs.append(os.path.join(appdata, "Claude"))
    elif sys.platform == "darwin":
        dirs.append(os.path.expanduser("~/Library/Application Support/Claude"))
    else:
        dirs.append(os.path.expanduser("~/.config/Claude"))
    return [d for d in dirs if os.path.isdir(d)]


def build_mcpb():
    code, out = run([sys.executable, os.path.join(ROOT, "desktop", "build.py")], 120)
    return code == 0 and os.path.isfile(MCPB)


def install_desktop(check_only, write_config):
    dirs = desktop_dirs()
    if not dirs:
        say(INFO, "Claude Desktop-App nicht gefunden, übersprungen. Wird sie später installiert: install.py erneut "
                  "ausführen oder dist/mail-assistant.mcpb doppelklicken.")
        return
    if check_only:
        for d in dirs:
            cfg = load_cfg(os.path.join(d, "claude_desktop_config.json"))
            has = "mail-assistant" in (cfg.get("mcpServers") or {})
            say(OK if has else INFO, "Desktop-Konfiguration %s: Mail Assistant %s." % (
                d, "eingetragen" if has else "nicht eingetragen (oder als Erweiterung installiert)"))
        return
    if write_config:
        for d in dirs:
            path = os.path.join(d, "claude_desktop_config.json")
            cfg = load_cfg(path)
            if os.path.isfile(path):
                shutil.copy2(path, path + ".bak")
            cfg.setdefault("mcpServers", {})["mail-assistant"] = {
                "command": sys.executable, "args": [SERVER], "env": {"PYTHONIOENCODING": "utf-8"}}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cfg, f, ensure_ascii=False, indent=2)
            say(OK, "Desktop: Mail Assistant in %s eingetragen (Sicherung: .bak)." % path)
        say(INFO, "Die Claude Desktop-App jetzt ganz beenden (auch im Infobereich) und neu starten.")
        return
    if not build_mcpb():
        say(WARN, "Desktop: Erweiterung konnte nicht gebaut werden. Alternative: install.py --desktop-config")
        return
    try:
        if sys.platform == "win32":
            os.startfile(MCPB)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", MCPB])
        else:
            subprocess.Popen(["xdg-open", MCPB])
        say(OK, "Desktop: Installationsfenster geöffnet (%s). Dort auf 'Installieren' klicken. SMTP-Felder leer "
                "lassen, solange nur Entwürfe gewünscht sind." % MCPB)
    except Exception as e:
        say(WARN, "Desktop: .mcpb konnte nicht geöffnet werden (%s). Datei %s in der Desktop-App unter "
                  "Einstellungen > Erweiterungen installieren, oder install.py --desktop-config." % (e, MCPB))


def load_cfg(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


# ------------------------------------------------------------------ 4.+5. profile and self-test
def server_module():
    sys.path.insert(0, os.path.dirname(SERVER))
    import server  # noqa: E402
    return server


def save_profile(args):
    values = {"name": args.name, "closing": args.closing, "language": args.language, "font": args.font,
              "font_size": args.font_size, "from": getattr(args, "from_addr"), "logo": args.logo}
    if args.signature is not None:
        values["signature"] = "\n".join(s.strip() for s in args.signature.split("|"))
    values = {k: v for k, v in values.items() if v is not None}
    if not values:
        return
    text, err = server_module().HANDLERS["email_profile_set"](values)
    if err:
        say(FAIL, "Profil: " + text)
    else:
        say(OK, "Profil gespeichert. Der Schluss jeder Mail sieht so aus:\n" +
            "\n".join("        " + l for l in text.split("Sign-off now looks like:\n")[-1].splitlines()))


def self_test():
    s = server_module()
    resp = s.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    n = len(resp["result"]["tools"])
    text, err = s.HANDLERS["email_check"]({"subject": "Test", "salutation": "Hallo Test",
                                           "body": "Ich melde mich am 7.3.2026 um 9.30 Uhr."})
    ok = not err and "07.03.2026" in text and "9:30 Uhr" in text
    say(OK if ok else FAIL, "Selbsttest Mail-Server: %d Werkzeuge, DIN-5008-Prüfung %s." % (n, "läuft" if ok else "FEHLER"))
    print()
    print(s.HANDLERS["email_setup_check"]({})[0])


def main():
    ap = argparse.ArgumentParser(description="Mail Assistant installer")
    ap.add_argument("--check", action="store_true", help="only diagnose, change nothing")
    ap.add_argument("--no-code", action="store_true", help="skip Claude Code")
    ap.add_argument("--no-desktop", action="store_true", help="skip Claude Desktop")
    ap.add_argument("--desktop-config", action="store_true", help="write claude_desktop_config.json instead of .mcpb")
    ap.add_argument("--no-shortcuts", action="store_true", help="do not create the short commands /mail, /mail-reply ...")
    ap.add_argument("--remove-shortcuts", action="store_true", help="remove the short commands again")
    ap.add_argument("--name")
    ap.add_argument("--closing")
    ap.add_argument("--signature", help="lines separated by |")
    ap.add_argument("--language")
    ap.add_argument("--font")
    ap.add_argument("--font-size")
    ap.add_argument("--from", dest="from_addr")
    ap.add_argument("--logo")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    print("Mail Assistant - Einrichtung (%s)\n" % ROOT)
    if not check_python():
        sys.exit(1)
    if args.remove_shortcuts:
        install_shortcuts(False, remove=True)
    elif not args.no_code:
        install_claude_code(args.check)
        if not args.no_shortcuts:
            install_shortcuts(args.check)
    if not args.no_desktop:
        install_desktop(args.check, args.desktop_config)
    if not args.check:
        save_profile(args)
    self_test()
    fails = [t for tag, t in results if tag == FAIL]
    print("\nFertig%s." % (" mit Fehlern" if fails else ""))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
