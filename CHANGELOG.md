# Changelog

## 1.2.1 — sentence translation quality

- Replace MyMemory with Google Translate for whole-sentence translation.
- Improve the reported “heads spin” example and other tested idioms without hardcoded sentence replacements.
- Preserve all translated segments, punctuation and the original input.
- Handle malformed responses, network failures and rate limits without caching failures.
- Update provider attribution and privacy information; retain the session-only cache.
- Keep blank startup, concise dictionary results and saved collections unchanged.

The public translation endpoint can change or be unavailable. Translation is still
machine-generated and may be inaccurate; there is no guarantee for every idiom.

## 1.2.0 — sentence translation and concise results

- Open with a blank, focused search box and no automatic lookup.
- Translate English sentences into Chinese and Chinese text into English through MyMemory.
- Keep dictionary phrases offline when found; translate other multiword input automatically.
- Add an explicit Translate button, selectable translation text, and Copy translation.
- Keep sentence text only in a bounded session-memory cache, never saved-word files or disk caches.
- Show three meanings/related words initially, with more available on demand.
- Omit empty translations, examples, synonyms and antonyms, and remove repetitive advice.
- Shorten long explanations by default; click abbreviated text to expand it.
- Preserve saved collections and the existing installer identity.

Sentence translation needs internet access and is limited to 500 UTF-8 bytes per
request, plus the provider's usage quota. It is machine translation and may be inaccurate.

## 1.1.0 — first public release

- Bundle 770,611 ECDICT entries for offline English–Chinese lookup.
- Add 206,941 WordNet word/sense records with relationships and available examples.
- Display Chinese definitions for searched and related words.
- Resolve many inflected forms to their base words.
- Keep normal searches local; isolate explicitly requested online lookups from local workers.
- Display long entries in batches of eight meanings.
- Preserve saved collections across updates, using a separate user-data directory.
- Package a Windows 10/11 x64 installer with desktop and Start menu shortcuts.
- Add source-data checksums, build instructions, and third-party notices for distribution.

Known limitations: incomplete dictionary/example coverage; Chinese definitions are not
sentence translations; optional online service may fail; installer is unsigned.

## 1.0.0 — earlier local milestone (not a GitHub release)

- Original desktop dictionary, starter entries, online lookup, cache, and saved words.
