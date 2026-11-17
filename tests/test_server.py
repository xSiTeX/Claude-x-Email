import os, sys, tempfile, json, unittest, base64
from unittest import mock
from email import policy
from email.parser import BytesParser

TMP = tempfile.mkdtemp()
os.environ["EMAIL_DRAFT_DIR"] = os.path.join(TMP, "drafts")
os.environ["MAIL_STATE_DIR"] = os.path.join(TMP, "state")
os.environ["MAIL_PROFILE"] = os.path.join(TMP, "state", "profile.json")
os.environ.pop("MAIL_SMTP_PASSWORD", None)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mail-assistant", "server"))
import server  # noqa: E402

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")


def call(_tool, **args):
    return server.HANDLERS[_tool](args)


def write(path, data, mode="w"):
    with open(path, mode) as f:
        f.write(data)


def parse(path):
    with open(path, "rb") as f:
        return BytesParser(policy=policy.default).parse(f)


def path_of(text):
    return text.split("\n")[0].split(": ", 1)[1]


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt = os.path.join(TMP, "a.txt")
        cls.png = os.path.join(TMP, "p.png")
        write(cls.txt, "hello")
        write(cls.png, PNG, "wb")

    def setUp(self):
        if os.path.exists(server.PROFILE_PATH):
            os.remove(server.PROFILE_PATH)

    def draft(self, **kw):
        args = dict(to=["x@example.com"], subject="Hi", body="Hallo\n\nWelt", attachments=[self.txt], open=False)
        args.update(kw)
        text, err = call("email_draft", **args)
        self.assertFalse(err, text)
        return path_of(text)


class LayoutTests(Base):
    def test_din5008_full_layout(self):
        call("email_profile_set", name="Max Muster", language="de",
             signature="Muster GmbH\nTelefon +49 30 1234567")
        text, err = call("email_check", subject="Betreff: Rechnung 2026-114.", salutation="Sehr geehrte Frau Müller",
                         body="Anbei  erhalten Sie die Rechnung.\n\n\n\n   Bei Fragen melden Sie sich gerne.",
                         attachments=[self.txt])
        self.assertFalse(err)
        path = self.draft(subject="Betreff: Rechnung 2026-114.", salutation="Sehr geehrte Frau Müller",
                          body="Anbei  erhalten Sie die Rechnung.\n\n\n\n   Bei Fragen melden Sie sich gerne.")
        msg = parse(path)
        self.assertEqual(msg["Subject"], "Rechnung 2026-114")
        self.assertEqual(msg.get_body(("plain",)).get_content(),
                         "Sehr geehrte Frau Müller,\n\n"
                         "anbei erhalten Sie die Rechnung.\n\n"
                         "Bei Fragen melden Sie sich gerne.\n\n"
                         "Freundliche Grüße\n\n"
                         "Max Muster\n\n"
                         "-- \nMuster GmbH\nTelefon +49 30 1234567\n")
        self.assertIn("Rechnung 2026-114", text)

    def test_closing_written_into_body_is_relaid(self):
        call("email_profile_set", language="de")
        text, _ = call("email_check", subject="x", salutation="Hallo Max,",
                       body="Ich komme morgen.\nViele Grüße,\nAnna\nTeamleitung")
        self.assertIn(" 3 | ich komme morgen.\n 4 | \n 5 | Viele Grüße\n 6 | \n 7 | Anna\n 8 | Teamleitung", text)

    def test_salutation_inside_body_gets_blank_line(self):
        text, _ = call("email_check", subject="x", language="de", body="Hallo Max,\nwie besprochen das Angebot.")
        self.assertIn(" 1 | Hallo Max,\n 2 | \n 3 | wie besprochen", text)

    def test_english_layout(self):
        call("email_profile_set", name="Max Muster", language="en")
        text, _ = call("email_check", subject="Offer", salutation="Dear Ms Miller", body="please find the offer below.")
        self.assertIn("Dear Ms Miller,\n 2 | \n 3 | Please find", text)
        self.assertIn("Kind regards,\n 6 | Max Muster", text)

    def test_legacy_signature_is_split(self):
        call("email_profile_set", signature="Freundliche Grüße, Max Muster\nMuster GmbH", language="de")
        p = json.load(open(server.PROFILE_PATH, encoding="utf-8"))
        self.assertEqual((p["closing"], p["name"], p["signature"]), ("Freundliche Grüße", "Max Muster", "Muster GmbH"))

    def test_html_body_gets_norm_spacing(self):
        call("email_profile_set", language="de", name="Max")
        path = self.draft(salutation="Hallo Anna,",
                          html_body="<p>im Anhang die Liste:</p><p></p><ul><li>eins</li></ul><p>Danke</p>")
        h = parse(path).get_body(("html",)).get_content()
        self.assertEqual(h.count("&nbsp;</p>"), 5)  # salutation|p|ul|p|closing|name
        self.assertNotIn("<p>", h)
        self.assertIn('<ul style="margin-top:0;margin-bottom:0;', h)

    def test_warnings(self):
        text, _ = call("email_check", subject="A" * 70, language="de", salutation="Hallo,",
                       body="anbei die Datei. Ruf an: 030/123456")
        self.assertIn("no file is attached", text)
        self.assertIn("Ruf an: 030 123456", text)  # fixed to DIN 5008
        self.assertIn("70 characters", text)
        text, _ = call("email_check", subject="x", salutation="Hallo,", body="text", attachments=[self.txt])
        self.assertIn("Attachment not mentioned", text)

    def test_check_writes_nothing_and_checks_drafts(self):
        before = os.listdir(server.OUT_DIR) if os.path.isdir(server.OUT_DIR) else []
        call("email_check", subject="x", body="y")
        after = os.listdir(server.OUT_DIR) if os.path.isdir(server.OUT_DIR) else []
        self.assertEqual(before, after)
        path = self.draft(salutation="Hallo Max,", body="im Anhang die Datei.")
        text, err = call("email_check", draft_path=path)
        self.assertFalse(err)
        self.assertIn("Norm check: no issues.", text)
        listing, _ = call("email_list_drafts")
        self.assertIn(path, listing)


class DraftTests(Base):
    def test_attachment_inline_image_and_calibri(self):
        msg = parse(self.draft(inline_images=[self.png]))
        names = [p.get_filename() for p in msg.walk()]
        self.assertIn("a.txt", names)
        self.assertIn("p.png", names)
        body = msg.get_body(("html",)).get_content()
        self.assertIn("'Calibri', Carlito", body)
        self.assertIn("cid:img1", body)
        self.assertEqual(msg["X-Unsent"], "1")

    def test_other_font(self):
        body = parse(self.draft(font="Cambria", font_size="12pt")).get_body(("html",)).get_content()
        self.assertIn("'Cambria', Caladea", body)
        self.assertIn("font-size:12pt", body)

    def test_missing_file(self):
        _, err = call("email_draft", subject="x", attachments=["/nope.pdf"], open=False)
        self.assertTrue(err)

    def test_old_tool_names_still_work(self):
        text, err = call("create_email_draft", to=["x@example.com"], subject="Hi", body="x", open=False)
        self.assertFalse(err, text)
        _, err = call("get_profile")
        self.assertFalse(err)


class PermissionTests(Base):
    def test_draft_only_refuses_send(self):
        text, err = call("email_send", draft_path=self.draft(), confirmed=True)
        self.assertTrue(err)
        self.assertIn("disabled", text)

    def test_send_only_from_drafts_folder(self):
        call("email_permissions_set", mode="ask_before_send")
        _, err = call("email_send", draft_path=self.txt, confirmed=True)
        self.assertTrue(err)

    def test_bad_mode_and_no_password_stored(self):
        _, err = call("email_permissions_set", mode="yolo")
        self.assertTrue(err)
        call("email_profile_set", smtp={"host": "smtp.test", "user": "u@test", "password": "secret"})
        self.assertNotIn("secret", open(server.PROFILE_PATH).read())

    def test_ask_and_autonomous_flow(self):
        sent = []
        fake = mock.MagicMock()
        fake.__enter__.return_value = fake
        fake.send_message.side_effect = lambda m: sent.append(m)
        with mock.patch.dict(os.environ, {"MAIL_SMTP_PASSWORD": "pw"}), \
                mock.patch("smtplib.SMTP", return_value=fake), \
                mock.patch.object(server, "sent_today", lambda: len(sent)):
            call("email_profile_set", smtp={"host": "smtp.test", "user": "me@test", "port": 587})
            call("email_permissions_set", mode="ask_before_send", allowed_recipients=["@example.com"], daily_limit=5)
            path = self.draft()
            text, err = call("email_send", draft_path=path)
            self.assertTrue(err)
            self.assertIn("CONFIRMATION REQUIRED", text)
            self.assertIn("a.txt", text)
            self.assertEqual(sent, [])
            text, err = call("email_send", draft_path=path, confirmed=True)
            self.assertFalse(err, text)
            self.assertEqual(len(sent), 1)
            self.assertNotIn("X-Unsent", sent[0])

            call("email_permissions_set", mode="autonomous")
            text, err = call("email_send", draft_path=self.draft())
            self.assertFalse(err, text)
            self.assertEqual(len(sent), 2)

            text, _ = call("email_draft", to=["other@elsewhere.org"], subject="Hi", body="x", open=False)
            text, err = call("email_send", draft_path=path_of(text))
            self.assertTrue(err)
            self.assertIn("allow-list", text)

            call("email_permissions_set", daily_limit=2)
            text, _ = call("email_send", draft_path=self.draft())
            self.assertIn("limit", text)


class NormTests(Base):
    def test_default_is_din5008_and_calibri(self):
        text, _ = call("email_check", subject="x", body="Hallo Mehdi, Ich komme morgen.")
        self.assertIn("Layout: DIN 5008", text)
        self.assertIn(" 3 | ich komme morgen.", text)
        self.assertIn("Freundliche Grüße", text)
        html = parse(self.draft()).get_body(("html",)).get_content()
        self.assertIn("font-family:'Calibri'", html)
        self.assertIn("font-size:11pt", html)

    def test_dates_times_amounts_phone(self):
        call("email_profile_set", signature="Telefon 030/123456", language="de")
        text, _ = call("email_check", subject="x", salutation="Hallo Mehdi,",
                       body="am 7.3.2026 um 9.30 Uhr, Preis 250€ bzw. € 1.250,00, 10% Rabatt, +49 (0)30 555.")
        self.assertIn("am 07.03.2026 um 9:30 Uhr, Preis 250 € bzw. 1.250,00 €, 10 % Rabatt, +49 30 555.", text)
        self.assertIn("Telefon 030 123456", text)
        call("email_profile_set", signature="")

    def test_english_text_keeps_numbers(self):
        text, _ = call("email_check", subject="x", body="Hi John, thanks for the update, see you on 7.3.2026.")
        self.assertIn("international", text)
        self.assertIn(" 1 | Hi John,\n 2 | \n 3 | Thanks for the update, see you on 7.3.2026.", text)

    def test_html_numbers_leave_css_alone(self):
        path = self.draft(salutation="Hallo,", html_body='<p style="width:100%">10% am 1.2.2026</p>')
        h = parse(path).get_body(("html",)).get_content()
        self.assertIn("width:100%", h)
        self.assertIn("10 % am 01.02.2026", h)


class ProtocolTests(unittest.TestCase):
    def test_initialize_has_instructions_and_prompts(self):
        r = server.handle({"method": "initialize", "id": 1, "params": {}})["result"]
        self.assertIn("DIN 5008", r["instructions"])
        self.assertIn("prompts", r["capabilities"])
        prompts = server.handle({"method": "prompts/list", "id": 2})["result"]["prompts"]
        names = [p["name"] for p in prompts]
        for n in ("mail", "mail-reply", "mail-check", "mail-send", "mail-profile", "mail-permissions",
                  "mail-setup", "mail-help"):
            self.assertIn(n, names)
        got = server.handle({"method": "prompts/get", "id": 3,
                             "params": {"name": "mail", "arguments": {"anfrage": "an Mehdi wegen Freitag"}}})
        self.assertIn("an Mehdi wegen Freitag", got["result"]["messages"][0]["content"]["text"])

    def test_help(self):
        text, err = call("email_help")
        self.assertFalse(err)
        self.assertIn("Rechtestufen", text)
        text, _ = call("email_help", topic="daten")
        self.assertIn("profile.json", text)

    def test_tools_list_and_unknown_tool(self):
        names = [t["name"] for t in server.handle({"method": "tools/list", "id": 1})["result"]["tools"]]
        self.assertTrue(all(n.startswith("email_") for n in names))
        self.assertEqual(len(names), 10)
        r = server.handle({"method": "tools/call", "id": 2, "params": {"name": "nope"}})
        self.assertIn("error", r)


if __name__ == "__main__":
    unittest.main()
