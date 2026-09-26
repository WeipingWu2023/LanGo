# Wordroom 1.1.0

The first public release of Wordroom, a local English–Chinese dictionary for
Windows 10/11 on 64-bit Intel/AMD computers.

## Download and install

Download **Wordroom-Setup-1.1.0-Windows-x64.exe** from the assets below and run it.
No Python installation, API key, or administrator rights are required. Setup
creates desktop and Start menu shortcuts. The automatic “Source code” ZIP is
for developers and is not the Windows installer.

**The installer is unsigned.** Windows may display an unknown-publisher or
SmartScreen warning. This release is not code-signed.

## Features

- 770,000+ offline English–Chinese dictionary entries from ECDICT.
- Fast indexed local search without waiting for an internet service.
- Chinese definitions for searched words and related words where available.
- WordNet English senses, synonyms, antonyms, and available examples.
- Many inflected forms resolve to their base word.
- Saved words remain in `%LOCALAPPDATA%\Wordroom`; updating preserves them.
- Optional online details run separately from local searches.
- Long entries show eight meanings initially, with a button for more.

## Known limitations

Coverage is not exhaustive. Some entries lack Chinese definitions, examples, or
relationships. Chinese headword definitions do not translate each English
sentence. Related-word explanations can occasionally refer to another sense.
Online details depend on an external service. No automatic spelling correction
or automatic updating is included. ARM, 32-bit Windows, macOS and Linux are not
supported release targets.

## Verification and attribution

Automated dictionary tests and the real Tk window test cover offline lookup,
Chinese display, saved words, pagination and searching during a stalled online
request. See README.md for reproducible build/test instructions.

`SHA256SUMS.txt` contains the SHA-256 fingerprint of the final installer.
In PowerShell, run `Get-FileHash .\Wordroom-Setup-1.1.0-Windows-x64.exe -Algorithm SHA256`
and compare the result to the checksum file.

Wordroom code is MIT licensed. ECDICT and WordNet retain their own licenses and
attribution; full notices are included in the installer and source repository.
