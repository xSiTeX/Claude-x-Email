#!/usr/bin/env python3
"""Build Claude Desktop packages into dist/:
  dist/mail-assistant.mcpb      one-click extension (Settings > Extensions > Install)
  dist/skills/<name>.zip        skills for Settings > Capabilities > Skills (claude.ai / Desktop)
Run: python desktop/build.py
"""
import os, zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST = os.path.join(ROOT, "dist")
PLUGIN = os.path.join(ROOT, "mail-assistant")


def zipdir(zf, folder, arc_prefix):
    for base, _, files in os.walk(folder):
        for fn in files:
            full = os.path.join(base, fn)
            zf.write(full, os.path.join(arc_prefix, os.path.relpath(full, folder)).replace("\\", "/"))


os.makedirs(os.path.join(DIST, "skills"), exist_ok=True)
with zipfile.ZipFile(os.path.join(DIST, "mail-assistant.mcpb"), "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(ROOT, "desktop", "manifest.json"), "manifest.json")
    z.write(os.path.join(PLUGIN, "server", "server.py"), "server/server.py")

skills = os.path.join(PLUGIN, "skills")
for name in sorted(os.listdir(skills)):
    with zipfile.ZipFile(os.path.join(DIST, "skills", name + ".zip"), "w", zipfile.ZIP_DEFLATED) as z:
        zipdir(z, os.path.join(skills, name), name)
print("built:", ", ".join(sorted(os.listdir(DIST))), "+ skills/")
