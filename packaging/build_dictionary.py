"""Compile ECDICT and WordNet 3.0 into an indexed, read-only offline database.

Inputs: .build-tools/sources/ecdict.csv and wordnet.zip (unmodified upstream data).
Output contains adapted records; upstream licenses are shipped with the installer.
"""
import csv
import json
import re
import sqlite3
import zipfile
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POS = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}


def clean(word):
    return re.sub(r'\((?:a|p|ip)\)$', '', word).replace('_', ' ').lower()


def build():
    for source in json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8')):
        with (ROOT / '.build-tools/sources' / source['file']).open('rb') as file:
            if hashlib.file_digest(file, 'sha256').hexdigest() != source['sha256']:
                raise RuntimeError(f"Unexpected source data for {source['name']}; run packaging/fetch_data.py")
    target = ROOT / 'data' / 'dictionary.tmp.db'
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        target.unlink()
    db = sqlite3.connect(target)
    db.executescript('''
        CREATE TABLE entries(word TEXT PRIMARY KEY, phonetic TEXT, english TEXT, chinese TEXT) WITHOUT ROWID;
        CREATE TABLE aliases(form TEXT, word TEXT, PRIMARY KEY(form,word)) WITHOUT ROWID;
        CREATE TABLE senses(word TEXT, pos TEXT, rank INTEGER, definition TEXT, example TEXT, synonyms TEXT, antonyms TEXT);
        CREATE INDEX sense_word ON senses(word);
    ''')
    with (ROOT / '.build-tools/sources/ecdict.csv').open(encoding='utf-8', newline='') as file:
        for row in csv.DictReader(file):
            word = row['word'].strip().lower()
            db.execute('INSERT OR IGNORE INTO entries VALUES (?,?,?,?)',
                       (word, row['phonetic'], row['definition'].replace('\\n', '\n'), row['translation'].replace('\\n', '\n')))
            for item in row['exchange'].split('/'):
                if ':' not in item:
                    continue
                kind, forms = item.split(':', 1)
                for form in forms.split(','):
                    if kind in ('p', 'd', 'i', '3', 's', 'r', 't') and form and form != word:
                        db.execute('INSERT OR IGNORE INTO aliases VALUES (?,?)', (form.lower(), word))
                    elif kind == '0' and form != word:
                        db.execute('INSERT OR IGNORE INTO aliases VALUES (?,?)', (word, form.lower()))
    synsets = {}
    with zipfile.ZipFile(ROOT / '.build-tools/sources/wordnet.zip') as archive:
        (ROOT / 'packaging/licenses/WordNet.txt').write_bytes(archive.read('wordnet/LICENSE'))
        for category in ('noun', 'verb', 'adj', 'adv'):
            for line in archive.read('wordnet/data.' + category).decode().splitlines():
                if not line or not line[0].isdigit():
                    continue
                metadata, gloss = line.split('|', 1)
                tokens = metadata.split()
                offset, pos, count = tokens[0], tokens[2], int(tokens[3], 16)
                words = [clean(tokens[4 + 2 * i]) for i in range(count)]
                cursor = 4 + 2 * count
                pointer_count = int(tokens[cursor])
                pointers = [tokens[cursor + 1 + i * 4:cursor + 5 + i * 4] for i in range(pointer_count)]
                examples = re.findall(r'"([^\"]+)"', gloss)
                definition = re.sub(r'"[^\"]+"', '', gloss).strip(' ;')
                synsets[(pos.replace('s', 'a'), offset)] = (pos, words, definition, '\n'.join(examples), pointers)
            for line in archive.read('wordnet/' + category + '.exc').decode().splitlines():
                form, *bases = line.split()
                for base in bases:
                    db.execute('INSERT OR IGNORE INTO aliases VALUES (?,?)', (clean(form), clean(base)))
        for category in ('noun', 'verb', 'adj', 'adv'):
            for line in archive.read('wordnet/index.' + category).decode().splitlines():
                if not line or line.startswith(' '):
                    continue
                tokens = line.split()
                word, pos, count = clean(tokens[0]), tokens[1], int(tokens[2])
                for rank, offset in enumerate(tokens[-count:]):
                    actual_pos, words, definition, examples, pointers = synsets[(pos, offset)]
                    antonyms = []
                    for symbol, target_offset, target_pos, indexes in pointers:
                        if symbol != '!':
                            continue
                        source_index, target_index = int(indexes[:2], 16), int(indexes[2:], 16)
                        if source_index and words[source_index - 1] != word:
                            continue
                        target_words = synsets[(target_pos.replace('s', 'a'), target_offset)][1]
                        antonyms.extend([target_words[target_index - 1]] if target_index else target_words)
                    db.execute('INSERT INTO senses VALUES (?,?,?,?,?,?,?)',
                               (word, POS[actual_pos], rank, definition, examples,
                                json.dumps([w for w in words if w != word]), json.dumps(list(dict.fromkeys(antonyms)))))
    db.commit()
    counts = {table: db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in ('entries', 'senses', 'aliases')}
    db.execute('VACUUM')
    db.close()
    target.replace(ROOT / 'data/dictionary.db')
    print(counts)


if __name__ == '__main__':
    build()
