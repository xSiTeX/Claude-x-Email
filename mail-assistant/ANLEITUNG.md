# Mail Assistant – Anleitung

Der Mail Assistant bringt Claude bei, E-Mails richtig zu schreiben: nach DIN 5008, in Calibri, mit Anhängen und Bildern. Er funktioniert in **Claude Code** und in der **Claude Desktop-App**.

## Überblick: was das Plugin kann

1. **Norm-Layout:** Jede Mail wird nach DIN 5008 aufgebaut, mit genau einer Leerzeile zwischen Anrede, Absätzen, Grußformel, Name und Signatur.
2. **Daten nach Norm:** Datum, Uhrzeit, Geldbeträge, Prozentangaben und Telefonnummern werden automatisch ins DIN-Format gebracht.
3. **Schrift:** Standard ist Calibri 11 pt in Schwarz. Jede andere Schrift geht auch.
4. **Anhänge und Bilder:** Dateien werden angehängt, Bilder können mitten im Text stehen. Dateien findet Claude auch ohne Pfad („die letzte Rechnung“).
5. **Kontakte und Vorlagen:** „/mail Mehdi, …“ reicht, Adresse und Du/Sie kommen aus den Kontakten. Wiederkehrende Mails gibt es als Vorlage.
6. **Entwürfe:** Die Mail öffnet sich als ungesendeter Entwurf in Outlook, Thunderbird oder Apple Mail, auf Wunsch direkt im klassischen Outlook. Du prüfst sie und drückst selbst auf Senden.
7. **Rechtestufen:** Standardmäßig sendet Claude nie selbst. Du kannst das schrittweise freigeben.

## Installation

**Am einfachsten:** Schick Claude den Link https://github.com/xSiTeX/Claude-x-Email und schreib „Richte mir das ein“. Claude folgt dann der Anleitung `INSTALL.md` im Repo. Es prüft und installiert bei Bedarf Python, richtet Claude Code und die Desktop-App ein und legt dein Profil an. Du musst nur ein paar Fragen beantworten und in der Desktop-App einmal auf „Installieren“ klicken.

Selbst einrichten: Python installieren, das Repo herunterladen und darin `python install.py` ausführen (`python install.py --help` zeigt alle Optionen, `python install.py --check` prüft nur).

Voraussetzung: **Python 3** ist installiert. Prüfen im Terminal mit `python --version`.

### Claude Code

Im Claude-Code-Chat eingeben:

```
/plugin marketplace add xSiTeX/Claude-x-Email
/plugin install mail-assistant@mail-tools
```

Danach eine neue Sitzung starten. Updates holst du mit `/plugin marketplace update mail-tools`.

### Claude Desktop-App

1. Die Datei `mail-assistant.mcpb` von der Release-Seite herunterladen: https://github.com/xSiTeX/Claude-x-Email/releases (neueste Version oben). Alternativ liegt sie im Repo unter `dist/`.
2. Doppelklick darauf (oder in der App unter *Einstellungen → Erweiterungen* installieren) und *Installieren* klicken.
3. Die Felder für SMTP leer lassen, solange du nur Entwürfe willst.
4. Optional: die ZIP-Dateien aus `dist/skills/` unter *Einstellungen → Fähigkeiten → Skills* hochladen. Nötig ist das nicht, die wichtigsten Regeln bringt die Erweiterung selbst mit.

## Befehle

| Befehl | Was er macht |
|---|---|
| `/mail <Wunsch> [Dateien]` | Neue Mail als Entwurf schreiben |
| `/mail-reply <Mail>` | Auf eine erhaltene Mail antworten |
| `/mail-check [Text oder Entwurf]` | Text oder Entwurf nach DIN 5008 prüfen und korrigieren |
| `/mail-send [Entwurf]` | Einen Entwurf senden (je nach Rechtestufe) |
| `/mail-profile [Werte]` | Name, Grußformel, Signatur, Logo, Sprache, Schrift, Outlook festlegen |
| `/mail-contacts [Daten]` | Kontakte mit Adresse, Du/Sie und Anrede verwalten |
| `/mail-templates [Name]` | Vorlagen für wiederkehrende Mails nutzen oder anlegen |
| `/mail-permissions [Stufe]` | Rechtestufe anzeigen oder ändern |
| `/mail-setup` | Einrichtung prüfen und alle Befehle zeigen |
| `/mail-help [Thema]` | Diese Anleitung erklären lassen |

**In Claude Code** tippst du die Befehle direkt ein.

**In der Desktop-App** gibt es keine Slash-Befehle. Die gleichen Befehle stellt die Erweiterung dort als **Prompts** bereit. Du findest sie je nach App-Version über das Plus- bzw. Anhang-Menü im Eingabefeld unter „Mail Assistant“. Noch einfacher: Schreib normal, zum Beispiel „Schreib Mehdi, dass das Treffen am Freitag um 14 Uhr ist“. Claude nutzt die Werkzeuge dann von selbst.

## Erste Schritte

1. **Profil anlegen** (einmalig):
   `/mail-profile Name Max Muster, Grußformel Freundliche Grüße, Signatur "Muster GmbH, Musterstraße 1, 12345 Berlin, Telefon +49 30 1234567", Sprache Deutsch, Schrift Calibri 11pt`
2. **Erste Mail:**
   `/mail Herr Schmidt, die Rechnung für Oktober ist im Anhang, C:\Users\max\Documents\rechnung.pdf`
3. Der Entwurf öffnet sich im Mailprogramm. Prüfen, Empfänger ergänzen falls nötig, selbst senden.
4. Wenn etwas nicht klappt: `/mail-setup`.

## So wird eine Mail aufgebaut (DIN 5008)

```
Sehr geehrte Frau Müller,             ← Anrede mit Komma
                                      ← 1 Leerzeile
vielen Dank für Ihre Anfrage. …       ← Text beginnt klein (außer Nomen und „Sie/Ihr“)
                                      ← 1 Leerzeile zwischen Absätzen
Im Anhang finden Sie das Angebot.     ← Anhänge immer im Text erwähnen
                                      ← 1 Leerzeile
Freundliche Grüße                     ← Grußformel OHNE Komma
                                      ← 1 Leerzeile
Max Muster                            ← Name
                                      ← 1 Leerzeile
--                                    ← Trennlinie zur Signatur (nur in der Textversion)
Muster GmbH                           ← Signatur: Firma, Adresse, Telefon, Web
Telefon +49 30 1234567
```

Weitere Regeln:
- Alles linksbündig, keine Einrückungen, kein Blocksatz.
- Immer genau eine Leerzeile zwischen den Blöcken, nie zwei.
- Betreff kurz und konkret, ohne das Wort „Betreff:“ und ohne Punkt am Ende.
- Aufzählungen bekommen eine Leerzeile davor und danach.

**Wichtig:** Claude übergibt Anrede, Text und Grußformel getrennt an den Server. Der Server setzt das Layout selbst zusammen. Deshalb stimmen die Abstände immer, auch wenn Claude sich vertippt.

Englische Mails bekommen das internationale Format: „Dear Ms Miller,“, Text mit großem Anfangsbuchstaben, „Kind regards,“ mit dem Namen direkt darunter. Ob Deutsch oder Englisch, entscheidet das Profil (Sprache). Ohne Angabe gilt Deutsch, außer der Text ist eindeutig englisch.

## Was automatisch korrigiert wird

| Vorher | Nachher | Regel |
|---|---|---|
| Anrede ohne Komma | `Sehr geehrte Frau Müller,` | Komma nach der Anrede |
| `Hallo Max, ich …` in einer Zeile | Anrede, Leerzeile, Text | Leerzeile nach der Anrede |
| `Ich melde mich …` nach der Anrede | `ich melde mich …` | Kleinschreibung nach „Anrede,“ |
| `Freundliche Grüße,` | `Freundliche Grüße` | kein Komma nach der Grußformel |
| Grußformel und Name ohne Abstand | Grußformel, Leerzeile, Name | DIN 5008 |
| mehrere Leerzeilen, Einrückungen, doppelte Leerzeichen | eine Leerzeile, linksbündig | DIN 5008 |
| `Betreff: Angebot.` | `Angebot` | Betreff ohne „Betreff:“ und Punkt |
| `7.3.2026` | `07.03.2026` | Datum zweistellig |
| `9.30 Uhr`, `14:30Uhr` | `9:30 Uhr`, `14:30 Uhr` | Uhrzeit mit Doppelpunkt |
| `250€`, `€ 1.250,00` | `250 €`, `1.250,00 €` | Betrag, Leerzeichen, Währung dahinter |
| `10%` | `10 %` | Leerzeichen vor Prozent |
| `030/123456`, `+49 (0)30 …`, `0049 30 …` | `030 123456`, `+49 30 …` | Telefonnummer nach DIN 5008 |

Diese Korrekturen gelten auch für die Signatur aus dem Profil. Datum, Uhrzeit, Beträge und Telefonnummern werden nur bei deutschen Mails angepasst.

## Was nur als Hinweis kommt

Claude zeigt diese Punkte unter „Please check“ und sagt sie dir:
- Ein Anhang ist dabei, wird im Text aber nicht erwähnt, oder umgekehrt.
- Der Betreff ist länger als etwa 60 Zeichen oder komplett in Großbuchstaben.
- Viele Wörter in Großbuchstaben, „!!“ oder „??“.
- Sehr lange Absätze (über etwa 700 Zeichen).
- Schriftgröße außerhalb von 10 bis 12 pt.
- Ungültige E-Mail-Adressen oder kein Empfänger.

## Schriften

- Standard: **Calibri 11 pt, schwarz**. Das entspricht dem Outlook-Standard und der Empfehlung der Norm (10 bis 12 pt, gut lesbare Schrift).
- Eine andere Schrift im Profil: `/mail-profile Schrift Arial 10pt`. Nur für eine Mail: „… in Cambria 12pt“.
- Jede Schrift funktioniert per Namen. Der Server hängt passende Ersatzschriften an (zum Beispiel Calibri → Carlito → Segoe UI → Arial), damit die Mail auch beim Empfänger ordentlich aussieht, wenn er die Schrift nicht hat.
- Die Schrift steht in jedem einzelnen Absatz. So behält auch Outlook sie bei.
- Fett, Listen, Links, Tabellen oder mehrere Schriften in einer Mail sind möglich. Sag es Claude einfach („die Termine als Liste, den Betrag fett“).

## Anhänge und Bilder

- **Anhänge:** Gib den vollständigen Pfad an, zum Beispiel `C:\Users\max\Documents\angebot.pdf`. Mehrere Dateien gehen auch.
- **Bilder im Text:** „… und zeig logo.png in der Mail“. Das Bild steht dann im Text statt im Anhang.
- **Grenze:** Zusammen etwa 25 MB. Bei größeren Dateien besser einen Freigabe-Link schicken.
- Claude hängt nur Dateien an, die du genannt hast.

## Profil

Das Profil speichert, was in jeder Mail gleich ist:

| Feld | Beispiel | Bedeutung |
|---|---|---|
| Name | Max Muster | steht unter der Grußformel |
| Grußformel | Freundliche Grüße | Standard-Grußformel (pro Mail änderbar) |
| Signatur | Muster GmbH, Adresse, Telefon, Web | Kontaktblock unter dem Namen |
| Sprache | Deutsch | DIN 5008 (Deutsch) oder international (Englisch) |
| Ton | freundlich, direkt | wie Claude formuliert |
| Schrift | Calibri 11pt | Standardschrift |
| Absender | max@muster.de | From-Adresse |

Anzeigen mit `/mail-profile`, ändern mit `/mail-profile <Werte>`. Die Antwort zeigt dir sofort, wie der Schluss deiner Mails aussieht.

Wer früher „Freundliche Grüße, Max Muster“ komplett in die Signatur geschrieben hat: Das Plugin trennt das automatisch in Grußformel, Name und Signatur.

### Signatur mit Logo

- `/mail-profile Logo C:\Users\max\Pictures\logo.png, Logobreite 150` setzt ein Logo unter die Signatur (Breite in Pixeln, Standard 150).
- Für eine formatierte Signatur (fett, Farbe, Link) kann Claude zusätzlich eine HTML-Signatur speichern („Mach den Firmennamen in der Signatur fett“). Die Textversion der Mail bekommt weiter die einfache Signatur.
- Fehlt die Logodatei später, kommt ein Hinweis, die Mail wird trotzdem erstellt.

## Kontakte

Kontakte sparen Tipparbeit und sorgen für die richtige Anrede.

```
/mail-contacts Mehdi mehdi@example.com du
/mail-contacts Dr. Lisa Schmidt lisa@firma.de Frau Sie
```

Danach reicht der Name: `/mail Mehdi, Treffen Freitag 14 Uhr`. Der Server setzt dann automatisch:
- die Adresse (`Mehdi <mehdi@example.com>`),
- die Anrede: „Hallo Mehdi,“ bei Du, „Sehr geehrte Frau Dr. Schmidt,“ bei Sie,
- die Grußformel: „Viele Grüße“ bei Du, sonst die aus deinem Profil,
- die Sprache, falls beim Kontakt eine eingetragen ist.

Gespeichert werden: Name, E-Mail, Du/Sie, Frau/Herr, Titel, Vor- und Nachname, Sprache, eine feste Anrede oder Grußformel (falls gewünscht) und eine Notiz. Ein unbekannter Name führt zu einer Rückfrage, Claude rät nie eine Adresse.

**Anrede-Prüfung:** Passt die Anrede nicht zum Kontakt, kommt ein Hinweis, zum Beispiel:
- „Sehr geehrter Herr Schmidt“ an eine als Frau gespeicherte Person,
- „Sehr geehrter Herr …“ an jemanden, den du duzt, oder „Hallo Lisa“ an jemanden, den du siezt,
- eine Anrede mit einem ganz anderen Namen („Hallo Anna“ an Mehdi).

„Sehr geehrte Herr“ bzw. „Sehr geehrter Frau“ wird automatisch grammatisch korrigiert.

## Vorlagen

Für Mails, die immer gleich aufgebaut sind. Eingebaut sind:

| Vorlage | Felder |
|---|---|
| `rechnung` | nummer, datum, betrag, frist |
| `termin` | datum, uhrzeit, ort |
| `absage` | thema, anlass, grund |
| `nachfassen` | datum, thema, frist |
| `angebot` | nummer, thema, frist |

Beispiel: `/mail-templates rechnung an Lisa, Nummer 2026-114 vom 01.10.2026, 250 €, zahlbar bis 15.11.2026, Datei C:\…\rechnung.pdf`

Eigene Vorlagen: „Speichere eine Vorlage 'lieferung': Betreff 'Lieferung {{auftrag}}', Text 'Ihre Bestellung {{auftrag}} wird am {{datum}} geliefert.'“ Platzhalter stehen in doppelten geschweiften Klammern. Die eingebauten Vorlagen sind in der Sie-Form; bei Du-Kontakten schreibt Claude den Text passend um.

## Dateien finden

Du musst keine Pfade tippen. „Häng die letzte Rechnung an“ oder „das PDF vom Angebot Müller“ reicht. Claude sucht dann in Downloads, Dokumente, Desktop, Bilder und OneDrive nach Dateinamen mit diesen Wörtern (neueste zuerst), zeigt dir die Treffer und hängt erst an, wenn du bestätigt hast, welche Datei es sein soll. Gesucht wird nur im Dateinamen, nicht im Inhalt.

## Entwürfe direkt in Outlook

Mit `/mail-profile Entwürfe in Outlook` (Profilfeld `draft_target: outlook`) legt Claude jeden Entwurf direkt im **Entwürfe-Ordner von Outlook** an und öffnet ihn dort, mit Anhängen, Bildern und Schrift. Zusätzlich bleibt die .eml-Datei als Kopie im Entwürfe-Ordner des Plugins.

Wichtig:
- Das geht nur mit dem **klassischen Outlook** unter Windows (Outlook aus Microsoft 365/Office). Das **neue Outlook** („Outlook for Windows“, das blaue Symbol mit „New“) hat keine Schnittstelle dafür. Dann öffnet sich automatisch die .eml-Datei und Claude sagt dir das.
- Beim ersten Mal kann Outlook eine Sicherheitsabfrage zeigen („Ein Programm versucht …“). Erlauben, wenn du es selbst ausgelöst hast.

## Rechtestufen

| Stufe | Was Claude darf |
|---|---|
| `draft_only` (Standard) | Nur Entwürfe erstellen. Senden ist gesperrt. Du sendest selbst. |
| `ask_before_send` | Claude zeigt dir Empfänger, Betreff, Text und Anhänge und sendet erst nach deinem ausdrücklichen „Ja“. |
| `autonomous` | Claude sendet ohne Nachfrage, aber nur an Adressen oder Domains auf deiner Erlaubnisliste und nur bis zum Tageslimit. Alles andere fragt wieder nach. |

Beispiele:
- `/mail-permissions ask_before_send`
- `/mail-permissions autonomous max@muster.de @muster.de Limit 5`
- `/mail-permissions draft_only` (zurück zum sicheren Standard)

Sicherheitsregeln, die im Code stecken:
- Nur du änderst die Stufe. Eine Mail, Datei oder Webseite kann das nicht.
- Gesendet werden nur Entwürfe aus dem Entwürfe-Ordner des Plugins.
- Ein „Ja“ gilt nur für genau diese eine Mail.
- Das Passwort wird nie im Profil gespeichert.
- Claude Code fragt zusätzlich bei jedem Sendeversuch um Erlaubnis, solange du das nicht abgeschaltet hast.

## Senden einrichten

Nur nötig, wenn Claude selbst senden soll.

1. **App-Passwort erstellen** beim Mailanbieter:
   - Gmail: Google-Konto → Sicherheit → App-Passwörter (Bestätigung in zwei Schritten muss an sein).
   - Outlook.com: Microsoft-Konto → Sicherheit → Erweiterte Sicherheitsoptionen → App-Passwörter.
2. **Passwort hinterlegen**, aber nie im Chat eintippen:
   - Claude Code: Umgebungsvariable `MAIL_SMTP_PASSWORD` setzen, zum Beispiel unter Windows mit `setx MAIL_SMTP_PASSWORD "dein-app-passwort"` und danach das Terminal neu öffnen.
   - Desktop-App: in den Einstellungen der Erweiterung im Feld „App-Passwort“.
3. **Server eintragen:** „Richte SMTP ein: smtp.gmail.com, Port 587, Benutzer max@gmail.com“ (Outlook.com: `smtp-mail.outlook.com`, Port 587).
4. **Stufe wählen:** `/mail-permissions ask_before_send`.
5. **Prüfen:** `/mail-setup` muss „password set: True“ zeigen.

## Wo deine Daten liegen

Alles bleibt auf deinem Rechner. Nichts geht an einen fremden Server, außer du sendest eine Mail über deinen eigenen Mailanbieter.

| Was | Wo |
|---|---|
| Entwürfe (.eml) | `Dokumente\ClaudeEmailDrafts` |
| Profil | `%USERPROFILE%\.claude-mail\profile.json` |
| Kontakte | `%USERPROFILE%\.claude-mail\contacts.json` |
| eigene Vorlagen | `%USERPROFILE%\.claude-mail\templates.json` |
| Versandprotokoll | `%USERPROFILE%\.claude-mail\sent.log` |
| Passwort | nur in der Umgebungsvariable bzw. in den Desktop-Einstellungen, nie in einer Datei des Plugins |

Claude Code und die Desktop-App nutzen auf demselben PC **dieselben Dateien**. Ein Profil, das du in Claude Code anlegst, gilt also auch in der Desktop-App und umgekehrt. Entwürfe kannst du jederzeit im Ordner löschen.

Andere Orte lassen sich mit den Umgebungsvariablen `EMAIL_DRAFT_DIR`, `MAIL_STATE_DIR` und `MAIL_PROFILE` festlegen.

## Fehlerbehebung

| Problem | Lösung |
|---|---|
| Befehl `/mail` unbekannt | Plugin nicht installiert oder Sitzung nicht neu gestartet. Siehe Installation. In der Desktop-App gibt es keine Slash-Befehle, dort normal schreiben oder die Prompts nutzen. |
| Werkzeuge fehlen / Server startet nicht | `python --version` prüfen. Python 3 muss im PATH sein. |
| Entwurf öffnet sich nicht | Für `.eml`-Dateien ist kein Mailprogramm eingestellt. Datei aus `Dokumente\ClaudeEmailDrafts` per Rechtsklick → Öffnen mit → Outlook öffnen. |
| Schrift sieht anders aus | Der Empfänger hat die Schrift nicht installiert; dann greift die Ersatzschrift. Webmail (Gmail im Browser) zeigt manchmal eine eigene Schrift. |
| „Sending is disabled“ | Stufe ist `draft_only`. Mit `/mail-permissions` ändern. |
| „SMTP is not configured“ | App-Passwort, Server und Benutzer fehlen. Siehe „Senden einrichten“. |
| „CONFIRMATION REQUIRED“ | Normal: Claude muss dich vor dem Senden fragen. |
| Anmeldung beim Senden schlägt fehl | App-Passwort statt normalem Passwort verwenden; Port 587 mit starttls. |
| „Unknown contact“ | Den Namen gibt es nicht in den Kontakten. Mit `/mail-contacts` anlegen oder die Adresse angeben. |
| „Classic Outlook is not available“ | Nur das neue Outlook ist installiert. `/mail-profile Entwürfe als Datei` stellt zurück; die .eml-Datei funktioniert weiter. |

## Grenzen

- Entwürfe sind `.eml`-Dateien. Direkt im Postfach landen sie nur mit dem klassischen Outlook (siehe „Entwürfe direkt in Outlook“).
- Die Dateisuche durchsucht nur Dateinamen in den üblichen Ordnern, nicht den Inhalt.
- Das Plugin liest keine Posteingänge. Um auf eine Mail zu antworten, füge sie in den Chat ein.
- Senden geht über SMTP mit App-Passwort, nicht über eine Google- oder Microsoft-Anmeldung (OAuth).
- Wie die Schrift aussieht, hängt am Ende vom Mailprogramm des Empfängers ab.
- Wörter, die nach der Anrede kleingeschrieben werden müssen, erkennt der Server nur für häufige Fälle (ich, wir, vielen Dank, anbei …). Bei Nomen bleibt der große Anfangsbuchstabe absichtlich.
