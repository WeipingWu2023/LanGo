# Wordroom 1.2.1

Sentence translation now uses Google Translate instead of MyMemory. In live checks,
the reported astrophysics sentence was translated as “对天体物理学的理解足以让大多数人头晕目眩”,
instead of describing people's heads physically rotating. Other checks included
“break the ice”, “under the weather”, a literal rotation sentence, and Chinese-to-English.
These are observed examples, not a guarantee of perfect translation.

- Whole sentences are translated together; no hardcoded sentence replacements.
- Multiple response segments are preserved; errors are not cached as translations.
- Blank startup, concise results, 770,611 offline entries, Chinese definitions,
  WordNet relationships and optional online dictionary details remain available.
- Saved words remain in their separate local folder and are preserved on upgrade.

## Install

Download `Wordroom-Setup-1.2.1-Windows-x64.exe` and run it to update Wordroom.
Windows 10/11 x64 (Intel/AMD). The installer is unsigned and Windows may show an
unknown-publisher/SmartScreen warning. Verify it against `SHA256SUMS.txt`.

## Privacy and limitations

Sentence translation sends submitted text to Google Translate and needs internet.
The public web endpoint is not the supported Google Cloud API and may change,
be rate-limited or be unavailable on your network. There is no automatic MyMemory
fallback. Input remains limited to 500 UTF-8 bytes; translations may still be
inaccurate. Wordroom keeps sentence translations only in session memory, never
in saved-word files. Offline word lookup continues to work without internet.
