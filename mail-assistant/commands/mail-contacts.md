---
description: "Show, add or change contacts (address, du/Sie, salutation)"
argument-hint: "[e.g. \"Mehdi mehdi@example.com du\" or \"Dr. Lisa Schmidt lisa@firma.de Frau Sie\" or a search word]"
---

Contacts: $ARGUMENTS

- Nothing given: `email_contacts` and show them as a short list.
- A search word only: `email_contacts` with `query`.
- New or changed data: `email_contact_set`. Read from the user's words: name, email, `address` du/sie (default sie), `gender` f/m when "Frau/Herr" is given, `title` (Dr., Prof.), optional fixed salutation or closing. Show the resulting salutation from the tool answer.
- Deleting only when the user clearly asks, with `email_contact_delete`.

Afterwards the contact can be used by name: `/mail Mehdi, ...`.
