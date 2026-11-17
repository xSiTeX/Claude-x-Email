#!/usr/bin/env python3
"""Mail Assistant MCP server (stdio, Python stdlib only).

Builds rich emails (any font, attachments, inline images) as .eml drafts and, depending on the
permission level chosen by the user, can send them via SMTP.

Permission levels (profile key "autonomy" -> "mode"):
  draft_only  (default)  Claude may only create drafts. Sending is refused.
  ask_before_send        Claude may send only after the user confirmed that exact draft in chat.
  autonomous             Claude may send without asking, but only to allow-listed recipients
                         and within the daily limit. Anything else falls back to ask_before_send.

SMTP password is NEVER stored in the profile. It is read from the environment variable
MAIL_SMTP_PASSWORD (Claude Desktop extension: entered once in the extension settings).
"""
import sys, json, os, re, mimetypes, subprocess, datetime, html, smtplib, ssl
from email.message import EmailMessage
from email.parser import BytesParser
from email import policy
from email.utils import formatdate, make_msgid, getaddresses

VERSION = "3.0.0"
MAX_TOTAL = 25 * 1024 * 1024
HOME = os.path.expanduser("~")
OUT_DIR = os.environ.get("EMAIL_DRAFT_DIR") or os.path.join(HOME, "Documents", "ClaudeEmailDrafts")
STATE_DIR = os.environ.get("MAIL_STATE_DIR") or os.path.join(HOME, ".claude-mail")
PROFILE_PATH = os.environ.get("MAIL_PROFILE") or os.path.join(STATE_DIR, "profile.json")
SENT_LOG = os.path.join(STATE_DIR, "sent.log")

MODES = ("draft_only", "ask_before_send", "autonomous")

# Fonts: the user's font first, then metric-compatible and generic fallbacks, so layout
# survives on systems where the font is not installed.
FONT_FALLBACKS = {
    "calibri": "Carlito, 'Segoe UI', Arial, sans-serif",
    "cambria": "Caladea, Georgia, 'Times New Roman', serif",
    "arial": "Helvetica, 'Liberation Sans', sans-serif",
    "helvetica": "Arial, 'Liberation Sans', sans-serif",
    "times new roman": "Times, 'Liberation Serif', serif",
    "georgia": "'Times New Roman', serif",
    "verdana": "Geneva, Tahoma, sans-serif",
    "tahoma": "Verdana, Geneva, sans-serif",
    "segoe ui": "Calibri, Arial, sans-serif",
    "consolas": "'Courier New', Courier, monospace",
    "courier new": "Courier, monospace",
    "comic sans ms": "'Comic Sans', cursive",
    "trebuchet ms": "Arial, sans-serif",
    "garamond": "'Times New Roman', serif",
    "aptos": "Calibri, Arial, sans-serif",
    "open sans": "Arial, sans-serif",
    "roboto": "Arial, sans-serif",
}


def font_stack(font):
    font = (font or "Calibri").strip().replace("'", "").replace('"', "").replace(";", "")
    fallback = FONT_FALLBACKS.get(font.lower(), "Arial, sans-serif")
    return "'%s', %s" % (font, fallback)


# ---------------------------------------------------------------- profile / state
def load_profile():
    try:
        with open(PROFILE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_profile(p):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)


def autonomy(p=None):
    p = p if p is not None else load_profile()
    a = dict(p.get("autonomy") or {})
    if a.get("mode") not in MODES:
        a["mode"] = "draft_only"
    a.setdefault("allowed_recipients", [])
    a.setdefault("daily_limit", 10)
    return a


def smtp_config(p=None):
    p = p if p is not None else load_profile()
    s = dict(p.get("smtp") or {})
    s.setdefault("security", "starttls")
    s["host"] = os.environ.get("MAIL_SMTP_HOST") or s.get("host")
    s["port"] = int(os.environ.get("MAIL_SMTP_PORT") or s.get("port") or 587)
    s["user"] = os.environ.get("MAIL_SMTP_USER") or s.get("user") or p.get("from")
    s["password_set"] = bool(os.environ.get("MAIL_SMTP_PASSWORD"))
    return s


def sent_today():
    today = datetime.date.today().isoformat()
    try:
        with open(SENT_LOG, encoding="utf-8") as f:
            return sum(1 for line in f if line.startswith(today))
    except Exception:
        return 0


def log_sent(path, recipients):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(SENT_LOG, "a", encoding="utf-8") as f:
        f.write("%s\t%s\t%s\n" % (datetime.datetime.now().isoformat(timespec="seconds"),
                                  ", ".join(recipients), os.path.basename(path)))


# ---------------------------------------------------------------- tools: profile
def get_profile(args):
    p = load_profile()
    out = {"profile_path": PROFILE_PATH, "profile": p, "autonomy": autonomy(p),
           "smtp": smtp_config(p), "sent_today": sent_today()}
    return json.dumps(out, ensure_ascii=False, indent=2), False


PROFILE_KEYS = ("name", "signature", "language", "tone", "font", "font_size", "from", "reply_to")


def set_profile(args):
    p = load_profile()
    for k in PROFILE_KEYS:
        if k in args:
            p[k] = args[k]
    if "autonomy" in args:
        a = autonomy(p)
        new = args["autonomy"] or {}
        if "mode" in new:
            if new["mode"] not in MODES:
                return "mode must be one of: " + ", ".join(MODES), True
            a["mode"] = new["mode"]
        if "allowed_recipients" in new:
            a["allowed_recipients"] = [x.strip().lower() for x in new["allowed_recipients"] if x.strip()]
        if "daily_limit" in new:
            a["daily_limit"] = max(0, int(new["daily_limit"]))
        p["autonomy"] = a
    if "smtp" in args:
        s = dict(p.get("smtp") or {})
        for k in ("host", "port", "user", "security"):
            if k in (args["smtp"] or {}):
                s[k] = args["smtp"][k]
        p["smtp"] = s  # no password key on purpose
    save_profile(p)
    return "Profile saved to %s\n%s" % (PROFILE_PATH, json.dumps(p, ensure_ascii=False)), False


# ---------------------------------------------------------------- tools: files
def check_files(paths):
    info, errors, total = [], [], 0
    for p in paths or []:
        p = os.path.expanduser(p)
        if not os.path.isfile(p):
            errors.append("Not found or not a file: " + p)
            continue
        s = os.path.getsize(p)
        total += s
        info.append((p, s))
    return info, errors, total


def preview(args):
    info, errors, total = check_files(args.get("attachments", []) + args.get("inline_images", []))
    lines = ["%s: %.1f KB" % (os.path.basename(p), s / 1024) for p, s in info] + errors
    lines.append("Total: %.2f MB (limit ~%d MB)" % (total / 1024 / 1024, MAX_TOTAL // 1024 // 1024))
    return "\n".join(lines), bool(errors) or total > MAX_TOTAL


def guess(path):
    ctype, _ = mimetypes.guess_type(path)
    return (ctype or "application/octet-stream").split("/", 1)


# ---------------------------------------------------------------- tool: create draft
def create(args):
    att_info, errors, total = check_files(args.get("attachments"))
    img_info, e2, t2 = check_files(args.get("inline_images"))
    errors += e2
    total += t2
    if errors:
        return "\n".join(errors), True
    if total > MAX_TOTAL:
        return ("Attachments total %.1f MB, over the ~25 MB mail limit. Use a share link instead."
                % (total / 1024 / 1024)), True
    prof = load_profile()
    msg = EmailMessage()
    msg["Subject"] = args["subject"]
    for h, k in (("To", "to"), ("Cc", "cc"), ("Bcc", "bcc")):
        if args.get(k):
            msg[h] = ", ".join(args[k])
    sender = args.get("from") or prof.get("from")
    if sender:
        msg["From"] = sender
    reply_to = args.get("reply_to") or prof.get("reply_to")
    if reply_to:
        msg["Reply-To"] = reply_to
    if args.get("in_reply_to"):
        msg["In-Reply-To"] = args["in_reply_to"]
        msg["References"] = args.get("references") or args["in_reply_to"]
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid()
    msg["X-Unsent"] = "1"  # mail apps open this as an unsent compose window

    body = args.get("body", "")
    sig = prof.get("signature", "") if args.get("signature", True) else ""
    if sig:
        body = body.rstrip() + "\n\n" + sig
    msg.set_content(body)

    font = args.get("font") or prof.get("font") or "Calibri"
    size = args.get("font_size") or prof.get("font_size") or "11pt"
    inner = args.get("html_body")
    if inner:
        if sig:
            inner += '<p style="margin:0">%s</p>' % html.escape(sig).replace("\n", "<br>")
    else:
        inner = "".join('<p style="margin:0 0 1em 0">%s</p>' % html.escape(par).replace("\n", "<br>")
                        for par in body.split("\n\n"))
    cids = []
    for i, (p, _) in enumerate(img_info, 1):
        cid = "img%d" % i
        cids.append((cid, p))
        if ("cid:" + cid) not in inner:  # not referenced: show it at the end
            inner += '<p><img src="cid:%s" alt="%s" style="max-width:100%%"></p>' % (
                cid, html.escape(os.path.basename(p)))
    doc = ('<html><head><meta charset="utf-8"></head><body>'
           '<div style="font-family:%s;font-size:%s;line-height:1.35">%s</div></body></html>'
           % (font_stack(font), size, inner))
    msg.add_alternative(doc, subtype="html")
    html_part = msg.get_payload()[1]
    for cid, p in cids:
        mt, st = guess(p)
        with open(p, "rb") as f:
            html_part.add_related(f.read(), maintype=mt, subtype=st, cid="<%s>" % cid,
                                  filename=os.path.basename(p), disposition="inline")
    for p, _ in att_info:
        mt, st = guess(p)
        with open(p, "rb") as f:
            msg.add_attachment(f.read(), maintype=mt, subtype=st, filename=os.path.basename(p))

    os.makedirs(OUT_DIR, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    safe = "".join(c if c.isalnum() or c in "-_ " else "_" for c in args["subject"])[:40].strip()
    out = os.path.join(OUT_DIR, "%s-%s.eml" % (stamp, safe))
    with open(out, "wb") as f:
        f.write(bytes(msg))
    note = ""
    if args.get("open", True):
        try:
            if sys.platform == "win32":
                os.startfile(out)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", out])
            else:
                subprocess.Popen(["xdg-open", out])
        except Exception as e:
            note = " (could not open automatically: %s)" % e
    names = ", ".join(os.path.basename(p) for p, _ in att_info) or "none"
    imgs = ", ".join(os.path.basename(p) for _, p in cids) or "none"
    return ("Draft created (NOT sent): %s\nAttachments: %s\nInline images: %s\nFont: %s%s\n"
            "Permission level: %s" % (out, names, imgs, font, note, autonomy(prof)["mode"])), False


# ---------------------------------------------------------------- tool: send
def recipients_of(msg):
    addrs = []
    for h in ("To", "Cc", "Bcc"):
        addrs += [a.lower() for _, a in getaddresses(msg.get_all(h, [])) if a]
    return addrs


def is_allowed(addr, allow):
    dom = addr.split("@")[-1]
    return any(addr == a or (a.startswith("@") and dom == a[1:]) or (("@" not in a) and dom == a)
               for a in allow)


def send_draft(args):
    path = os.path.abspath(os.path.expanduser(args["draft_path"]))
    if os.path.dirname(path) != os.path.abspath(OUT_DIR) or not path.endswith(".eml") or not os.path.isfile(path):
        return "Only .eml drafts created by create_email_draft in %s can be sent." % OUT_DIR, True
    prof = load_profile()
    a = autonomy(prof)
    mode = a["mode"]
    if mode == "draft_only":
        return ("Sending is disabled (permission level draft_only). The draft stays unsent: %s\n"
                "Tell the user to send it from their mail app, or to enable sending themselves "
                "(set_profile autonomy.mode = ask_before_send)." % path), True
    with open(path, "rb") as f:
        msg = BytesParser(policy=policy.default).parse(f)
    rcpts = recipients_of(msg)
    if not rcpts:
        return "Draft has no recipients.", True
    if a["daily_limit"] and sent_today() >= a["daily_limit"]:
        return "Daily send limit (%d) reached. Nothing sent." % a["daily_limit"], True
    auto_ok = mode == "autonomous" and all(is_allowed(r, a["allowed_recipients"]) for r in rcpts)
    if not auto_ok and not args.get("confirmed"):
        why = ("recipient not on the allow-list" if mode == "autonomous" else "level ask_before_send")
        return ("CONFIRMATION REQUIRED (%s). Show the user the recipients (%s), subject '%s' and "
                "attachments, ask for an explicit yes in chat, then call send_email again with "
                "confirmed=true. Do not set confirmed=true on your own."
                % (why, ", ".join(rcpts), msg["Subject"])), True
    s = smtp_config(prof)
    pw = os.environ.get("MAIL_SMTP_PASSWORD")
    if not (s["host"] and s["user"] and pw):
        return ("SMTP is not configured. Needed: host, user (profile smtp or MAIL_SMTP_HOST/USER) and "
                "the env variable MAIL_SMTP_PASSWORD (app password). The user must set these, "
                "never ask for or type the password in chat."), True
    if "X-Unsent" in msg:
        del msg["X-Unsent"]
    if not msg["From"]:
        msg["From"] = s["user"]
    ctx = ssl.create_default_context()
    try:
        if s["security"] == "ssl":
            srv = smtplib.SMTP_SSL(s["host"], s["port"], context=ctx, timeout=30)
        else:
            srv = smtplib.SMTP(s["host"], s["port"], timeout=30)
            if s["security"] == "starttls":
                srv.starttls(context=ctx)
        with srv:
            srv.login(s["user"], pw)
            srv.send_message(msg)
    except Exception as e:
        return "Sending failed: %s" % e, True
    log_sent(path, rcpts)
    return "Sent to %s (%s)." % (", ".join(rcpts), "autonomous" if auto_ok else "confirmed by user"), False


def check_setup(args):
    p = load_profile()
    s = smtp_config(p)
    a = autonomy(p)
    lines = ["Server version %s" % VERSION,
             "Drafts folder: %s" % OUT_DIR,
             "Profile: %s (%s)" % (PROFILE_PATH, "found" if p else "not created yet"),
             "Permission level: %s" % a["mode"],
             "Allow-list: %s" % (", ".join(a["allowed_recipients"]) or "empty"),
             "Daily limit: %s (sent today: %d)" % (a["daily_limit"], sent_today()),
             "SMTP host: %s  user: %s  password set: %s" % (s["host"], s["user"], s["password_set"])]
    return "\n".join(lines), False


# ---------------------------------------------------------------- MCP plumbing
STR = {"type": "string"}
STRS = {"type": "array", "items": STR}
TOOLS = [
    {"name": "get_profile", "description": "Read the mail profile, permission level and SMTP status.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "set_profile",
     "description": "Save mail profile: name, signature, language, tone, font (any font name, default Calibri), "
                    "font_size, from, reply_to, autonomy {mode: draft_only|ask_before_send|autonomous, "
                    "allowed_recipients: [addresses or @domains], daily_limit}, smtp {host, port, user, "
                    "security: starttls|ssl|none}. Only change autonomy when the user explicitly asks. "
                    "No password is ever stored.",
     "inputSchema": {"type": "object", "properties": {
         "name": STR, "signature": STR, "language": STR, "tone": STR, "font": STR, "font_size": STR,
         "from": STR, "reply_to": STR,
         "autonomy": {"type": "object", "properties": {
             "mode": {"type": "string", "enum": list(MODES)},
             "allowed_recipients": STRS, "daily_limit": {"type": "integer"}}},
         "smtp": {"type": "object", "properties": {
             "host": STR, "port": {"type": "integer"}, "user": STR,
             "security": {"type": "string", "enum": ["starttls", "ssl", "none"]}}}}}},
    {"name": "check_setup", "description": "Diagnose the setup: drafts folder, profile, permission level, SMTP.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "create_email_draft",
     "description": "Create an UNSENT email draft (.eml) with attachments, inline images and any font. "
                    "Opens in the default mail app so the user can review. Never sends.",
     "inputSchema": {"type": "object", "properties": {
         "to": STRS, "cc": STRS, "bcc": STRS, "subject": STR,
         "body": {"type": "string", "description": "Plain text body (also used as text/plain part)"},
         "html_body": {"type": "string", "description": "Optional inner HTML (<p>, <b>, <ul>, <a>, <table>, "
                       "<span style='font-family:...'>). Reference inline images as <img src='cid:img1'> "
                       "(numbered in the order of inline_images)."},
         "attachments": {"type": "array", "items": STR, "description": "Absolute file paths to attach"},
         "inline_images": {"type": "array", "items": STR,
                           "description": "Absolute image paths shown inside the mail body (cid:img1, cid:img2, ...)"},
         "font": {"type": "string", "description": "Any font name, default from profile or Calibri"},
         "font_size": {"type": "string", "description": "CSS size, e.g. 11pt"},
         "signature": {"type": "boolean", "description": "Append profile signature (default true)"},
         "from": STR, "reply_to": STR, "in_reply_to": {"type": "string", "description": "Message-ID being answered"},
         "open": {"type": "boolean", "description": "Open the draft in the mail app (default true)"}},
         "required": ["subject"]}},
    {"name": "send_email",
     "description": "Send a draft created by create_email_draft, according to the permission level. "
                    "draft_only: refused. ask_before_send: needs confirmed=true AFTER the user said yes in chat. "
                    "autonomous: sends without asking only to allow-listed recipients within the daily limit.",
     "inputSchema": {"type": "object", "properties": {
         "draft_path": {"type": "string", "description": "Path returned by create_email_draft"},
         "confirmed": {"type": "boolean", "description": "Set true ONLY after the user explicitly approved this exact mail in chat"}},
         "required": ["draft_path"]}},
    {"name": "list_attachments_preview",
     "description": "Check that files exist and report sizes against the ~25 MB limit.",
     "inputSchema": {"type": "object", "properties": {"attachments": STRS, "inline_images": STRS},
                     "required": ["attachments"]}},
]

HANDLERS = {"get_profile": get_profile, "set_profile": set_profile, "check_setup": check_setup,
            "create_email_draft": create, "send_email": send_draft, "list_attachments_preview": preview}


def handle(req):
    m, rid = req.get("method"), req.get("id")
    if m == "initialize":
        return {"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": req.get("params", {}).get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "mail-assistant", "version": VERSION}}}
    if m == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}
    if m == "tools/call":
        name = req["params"]["name"]
        args = req["params"].get("arguments") or {}
        try:
            text, err = HANDLERS[name](args)
        except Exception as e:
            text, err = "Error: %s" % e, True
        return {"jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": text}], "isError": err}}
    if rid is not None:
        return {"jsonrpc": "2.0", "id": rid, "result": {}}
    return None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(e)}}
        if resp:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
