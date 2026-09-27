# Wordroom 1.2.0

Three improvements requested after the 1.1 milestone:

- **Blank startup:** the search box opens empty and focused, with no automatic “bright” lookup.
- **Sentence translation:** enter an English sentence for Chinese, or Chinese for English. Known dictionary phrases stay offline; other multiword input translates automatically. Use the new Translate button to force translation. Select or copy the result.
- **Concise results:** three meanings and related words initially; reveal more when needed. Empty examples, synonyms and antonyms are hidden. Repetitive advice is removed. Click abbreviated explanations to expand them.

## Install or update

Download **Wordroom-Setup-1.2.0-Windows-x64.exe** below. Run it to install or update
on Windows 10/11 x64 (Intel/AMD). Python and administrator rights are not required.
The desktop shortcut is retained and saved words remain in `%LOCALAPPDATA%\Wordroom`.
The 1.1.0 release remains available as the earlier completed milestone.

**Unsigned installer:** Windows may show an unknown-publisher/SmartScreen warning.
`SHA256SUMS.txt` contains the final installer's checksum. GitHub's Source code ZIP
is for developers, not an installer.

## Privacy and limitations

770,000+ dictionary entries, Chinese definitions and WordNet relationships remain
available offline. Sentence translation requires internet and sends submitted text
to MyMemory. Text is cached only in session memory and is not written to saved
words or disk caches. Avoid submitting confidential text. Translation is limited
to 500 UTF-8 bytes per request and the service's quota; results can be inaccurate.
No offline sentence-translation model is included. Missing dictionary content is
omitted, and an unlisted antonym does not prove that none exists.

## Verification

16 automated tests pass, plus the real-window regression check for blank startup,
sentence routing, Chinese display, hidden empty sections, saved words, pagination
and responsive local search during a stalled online request. A live sample sentence
was also translated through the public service.

Original code is MIT licensed. ECDICT, WordNet and runtime notices are included.
