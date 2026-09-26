# Third-party notices

Wordroom's original application code, original starter entries and book icon are
licensed under the root MIT LICENSE. That license does not replace the terms of
third-party datasets or runtime components. Full notices are under
`packaging/licenses/` in source and `licenses/` in the installed application.

## Dictionary data

**ECDICT** — https://github.com/skywind3000/ECDICT

Copyright (c) 2025 Linwei. Distributed by the upstream project under MIT;
see `ECDICT.txt`. Wordroom converts selected CSV fields to SQLite, lowercases
headwords and builds inflection aliases. The upstream text is not authored by
Wordroom. The source revision and SHA-256 are recorded in `data/sources.json`.

**WordNet 3.0** — https://wordnet.princeton.edu/

WordNet 3.0 Copyright 2006 by Princeton University. All rights reserved.
See `WordNet.txt` for the complete license and disclaimer. Wordroom converts
the data/index/exception files to indexed SQLite sense and relationship records.
The unmodified WordNet archive is obtained from the NLTK data repository;
NLTK application code is not bundled. WordNet's name and source are acknowledged
for attribution only; no endorsement of Wordroom is claimed.

Citation: George A. Miller (1995). WordNet: A Lexical Database for English.
Communications of the ACM 38(11), 39–41.

The database combines these separately licensed sources; it is not relicensed
as a whole under Wordroom's MIT license. Redistributors must retain both notices,
including when distributing a database separately from the installer.

## Windows runtime and packaging

| Component | Notice / licensing information |
| --- | --- |
| CPython 3.12.10 and included standard-library components | `Python.txt`: PSF license, historical licenses, bzip2, libffi and other bundled notices; includes Microsoft Distributable Code conditions |
| Tcl 8.6.15 / Tk 8.6.15 | `Tcl.txt`, `Tk.txt`: retain the original copyright notices and disclaimers |
| OpenSSL 3.0.16 | `OpenSSL.txt`: Apache License 2.0; copyright notices retained in the unmodified binaries |
| zlib 1.3.1 | `zlib.txt`: zlib license |
| Expat 2.7.1 | `Expat.txt`: MIT license |
| liblzma from XZ Utils 5.2.5 | `XZ.txt`: liblzma source is public domain; standalone XZ command-line tools are not bundled |
| SQLite 3.49.1 | Public domain: https://www.sqlite.org/copyright.html |
| PyInstaller 6.22.3 bootloader and runtime hooks | `PyInstaller.txt`: GPL with bootloader exception; runtime hooks/utilities use Apache 2.0. Copyright (c) 2013–2023, PyInstaller Development Team, for the included Tcl/Tk hook; other included hooks retain their source copyright headers. |
| Inno Setup 6.7.3 | `InnoSetup.txt`: original compiler/setup copyright notices retained |

These notices describe the reference Windows release build. Preserve the
version-specific notices if rebuilding with a different runtime or compiler.
Build-only dependencies (such as Pillow) are installed separately and their
code is not included in the Wordroom application bundle.

## Optional online dictionary

https://dictionaryapi.dev/ is queried only when the user requests online details.
Online entries and their associated source/license metadata are cached in the
user's local data directory. Those caches are not included in this repository or
installer. The application displays the supplied attribution. Retain the entry's
own license and source metadata if redistributing online content separately.
