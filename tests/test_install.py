import os, sys, tempfile, unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import install  # noqa: E402


class ShortcutTests(unittest.TestCase):
    def test_create_keep_foreign_and_remove(self):
        home = tempfile.mkdtemp()
        cmd_dir = os.path.join(home, ".claude", "commands")
        os.makedirs(cmd_dir)
        with open(os.path.join(cmd_dir, "mail-send.md"), "w", encoding="utf-8") as f:
            f.write("my own command")
        real = os.path.expanduser
        with mock.patch("os.path.expanduser", lambda p: home if p == "~" else real(p)):
            install.install_shortcuts(False)
            with open(os.path.join(cmd_dir, "mail.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("mail-assistant:mail", text)
            self.assertIn("argument-hint:", text)
            self.assertIn(install.SHORTCUT_MARK, text)
            with open(os.path.join(cmd_dir, "mail-send.md"), encoding="utf-8") as f:
                self.assertEqual(f.read(), "my own command")  # foreign file untouched
            install.install_shortcuts(False, remove=True)
            self.assertFalse(os.path.exists(os.path.join(cmd_dir, "mail.md")))
            self.assertTrue(os.path.exists(os.path.join(cmd_dir, "mail-send.md")))


if __name__ == "__main__":
    unittest.main()
