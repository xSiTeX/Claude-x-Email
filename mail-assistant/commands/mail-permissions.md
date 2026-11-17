---
description: "Show or change what Claude may do with mail (draft only, ask before send, autonomous)"
argument-hint: "[draft_only | ask_before_send | autonomous] [allowed addresses/@domains] [daily limit]"
---

Permission level: $ARGUMENTS

Follow the `email-permissions` skill.
- Nothing given: call `email_profile_get` and explain the current level and the three options in a short table.
- A level given by the user here: set it with `email_permissions_set`. For `autonomous` an allow-list is required; if none was named, ask for it (suggest the user's own address) before setting.
- After a change run `email_setup_check` and say whether sending works (SMTP and password set).
