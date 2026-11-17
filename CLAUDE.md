# Claude x Email

If the user wants the Mail Assistant **set up or installed**, follow [INSTALL.md](INSTALL.md) step by step (Path A; you can run commands here).

If the user wants to **develop** the plugin:
- Server: `mail-assistant/server/server.py` (Python stdlib only, MCP over stdio). Tests: `python -m unittest discover -s tests`.
- Commands: `mail-assistant/commands/*.md`. These are also served as MCP prompts for Claude Desktop.
- Skills: `mail-assistant/skills/`. User guide (German): `mail-assistant/ANLEITUNG.md`, served by the `email_help` tool.
- After changes, rebuild `dist/` with `python desktop/build.py`. Keep the version in sync in `mail-assistant/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `desktop/manifest.json` and `VERSION` in server.py.
- Release: push a tag `v<version>`, and CI publishes the `.mcpb` and skill zips.
