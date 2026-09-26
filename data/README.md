# Offline dictionary: build locally, do not commit

`dictionary.db` is generated and ignored by Git. The Windows installer includes
it, so people installing Wordroom do not need these build steps.

For source development, use Python 3.12 and run from the repository root:

```powershell
python packaging/fetch_data.py
python packaging/build_dictionary.py
```

The first command downloads the fixed revisions in `sources.json` into the
ignored `.build-tools/sources/` folder. Each file must match its recorded SHA-256
fingerprint before it is accepted. Already verified files are reused. A mismatch
stops the build; do not bypass it or replace the expected hash without reviewing
the source change.

The second command verifies the sources again and builds an indexed SQLite
database with 770,611 ECDICT entries, 206,941 WordNet word/sense records, and
62,101 form-to-base aliases. These are overlapping record counts, not a sum of
unique words. SQLite indexes make normal lookups local and fast.

Sources: ECDICT supplies Chinese and available English definitions; WordNet 3.0
supplies English senses, examples where provided, and lexical relationships.
See the root THIRD_PARTY_NOTICES.md and packaging/licenses/ for their separate
licenses. A separately distributed database must include those notices too.

No personal saved words or lookup cache is used to build this database. Nothing
under `%LOCALAPPDATA%\Wordroom` is an input to the build.
