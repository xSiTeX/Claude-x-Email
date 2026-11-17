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


def call(name, **args):
    return server.HANDLERS[name](args)


class MailTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.txt = os.path.join(TMP, "a.txt")
        cls.png = os.path.join(TMP, "p.png")
        open(cls.txt, "w").write("hello")
        open(cls.png, "wb").write(PNG)

    def draft(self, **kw):
        text, err = call("create_email_draft", to=["x@example.com"], subject="Hi", body="Hallo\n\nWelt",
                         attachments=[self.txt], open=False, **kw)
        self.assertFalse(err, text)
        return text.split("\n")[0].split(": ", 1)[1]

    def parse(self, path):
        with open(path, "rb") as f:
            return BytesParser(policy=policy.default).parse(f)

    def test_draft_has_attachment_inline_image_and_calibri(self):
        path = self.draft(inline_images=[self.png])
        msg = self.parse(path)
        names = [p.get_filename() for p in msg.walk()]
        self.assertIn("a.txt", names)
        self.assertIn("p.png", names)
        body = msg.get_body(("html",)).get_content()
        self.assertIn("Calibri", body)
        self.assertIn("cid:img1", body)
        self.assertEqual(msg["X-Unsent"], "1")

    def test_other_font(self):
        path = self.draft(font="Cambria", font_size="12pt")
        body = self.parse(path).get_body(("html",)).get_content()
        self.assertIn("'Cambria', Caladea", body)
        self.assertIn("12pt", body)

    def test_missing_file_and_signature(self):
        text, err = call("create_email_draft", subject="x", attachments=["/nope.pdf"], open=False)
        self.assertTrue(err)
        call("set_profile", signature="Gruss\nMax")
        self.assertIn("Gruss", self.parse(self.draft()).get_body(("plain",)).get_content())
        call("set_profile", signature="")

    def test_draft_only_refuses_send(self):
        call("set_profile", autonomy={"mode": "draft_only"})
        text, err = call("send_email", draft_path=self.draft(), confirmed=True)
        self.assertTrue(err)
        self.assertIn("disabled", text)

    def test_send_only_from_drafts_folder(self):
        text, err = call("send_email", draft_path=self.txt, confirmed=True)
        self.assertTrue(err)

    def test_set_profile_rejects_bad_mode_and_stores_no_password(self):
        _, err = call("set_profile", autonomy={"mode": "yolo"})
        self.assertTrue(err)
        call("set_profile", smtp={"host": "smtp.test", "user": "u@test", "password": "secret"})
        self.assertNotIn("secret", open(os.environ["MAIL_PROFILE"]).read())

    def test_ask_and_autonomous_flow(self):
        sent = []
        fake = mock.MagicMock()
        fake.__enter__.return_value = fake
        fake.send_message.side_effect = lambda m: sent.append(m)
        with mock.patch.dict(os.environ, {"MAIL_SMTP_PASSWORD": "pw"}), \
                mock.patch("smtplib.SMTP", return_value=fake):
            call("set_profile", smtp={"host": "smtp.test", "user": "me@test", "port": 587},
                 autonomy={"mode": "ask_before_send", "allowed_recipients": ["@example.com"], "daily_limit": 5})
            path = self.draft()
            text, err = call("send_email", draft_path=path)
            self.assertTrue(err)
            self.assertIn("CONFIRMATION REQUIRED", text)
            self.assertEqual(sent, [])
            text, err = call("send_email", draft_path=path, confirmed=True)
            self.assertFalse(err, text)
            self.assertEqual(len(sent), 1)
            self.assertNotIn("X-Unsent", sent[0])

            call("set_profile", autonomy={"mode": "autonomous"})
            text, err = call("send_email", draft_path=self.draft())  # allow-listed domain
            self.assertFalse(err, text)
            self.assertEqual(len(sent), 2)

            text, err = call("create_email_draft", to=["other@elsewhere.org"], subject="Hi", body="x", open=False)
            text, err = call("send_email", draft_path=text.split("\n")[0].split(": ", 1)[1])
            self.assertTrue(err)  # not allow-listed -> needs confirmation
            self.assertIn("allow-list", text)

            call("set_profile", autonomy={"daily_limit": 2})
            text, err = call("send_email", draft_path=self.draft())
            self.assertIn("limit", text)
        call("set_profile", autonomy={"mode": "draft_only"})


if __name__ == "__main__":
    unittest.main()
