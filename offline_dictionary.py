"""Indexed local dictionary. A separate SQLite connection is used per lookup."""
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POS = {'n': 'noun', 'v': 'verb', 'vt': 'verb', 'vi': 'verb', 'a': 'adjective',
       'adj': 'adjective', 's': 'adjective', 'r': 'adverb', 'adv': 'adverb',
       'prep': 'preposition', 'pron': 'pronoun', 'conj': 'conjunction',
       'interj': 'interjection', 'int': 'interjection', 'num': 'numeral', 'art': 'article', 'det': 'determiner'}


class OfflineDictionary:
    def __init__(self, path=None):
        self.path = Path(path or ROOT / 'data/dictionary.db')

    def lookup(self, word):
        if not self.path.exists():
            return None
        db = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)
        db.row_factory = sqlite3.Row
        try:
            row = db.execute('SELECT * FROM entries WHERE word=?', (word,)).fetchone()
            senses = db.execute('SELECT * FROM senses WHERE word=? ORDER BY pos,rank', (word,)).fetchall()
            lemma = word
            if not senses:
                for alias in db.execute('SELECT word FROM aliases WHERE form=? ORDER BY word', (word,)):
                    base = alias['word']
                    base_senses = db.execute('SELECT * FROM senses WHERE word=? ORDER BY pos,rank', (base,)).fetchall()
                    base_row = db.execute('SELECT * FROM entries WHERE word=?', (base,)).fetchone()
                    if base_senses or base_row:
                        lemma, senses = base, base_senses
                        if not row:
                            row = base_row
                        break
            if not row and not senses:
                return None
            chinese = row['chinese'] if row else ''
            entry = {'word': word, 'phonetic': row['phonetic'] if row else '', 'translation': chinese,
                     'meanings': [], 'sourceUrls': ['https://github.com/skywind3000/ECDICT', 'https://wordnet.princeton.edu/'],
                     'license': {'name': 'ECDICT: MIT · WordNet 3.0 (licenses included)'}}
            if lemma != word:
                entry['baseForm'] = lemma
            for sense in senses:
                entry['meanings'].append({'partOfSpeech': sense['pos'], 'definitions': [{
                    'definition': sense['definition'], 'example': sense['example'],
                }], 'synonyms': json.loads(sense['synonyms']), 'antonyms': json.loads(sense['antonyms'])})
            if not senses and row:
                for line in row['english'].splitlines():
                    match = re.match(r'^([a-z]+)\.\s*(.*)', line)
                    tag, definition = (match[1], match[2]) if match else ('', line)
                    if definition.strip():
                        entry['meanings'].append({'partOfSpeech': POS.get(tag, tag or 'unspecified'),
                                                  'definitions': [{'definition': definition}]})
                if not entry['meanings']:
                    tags = re.findall(r'(?m)^([a-z]+)\.', chinese)
                    for tag in dict.fromkeys(tags or ['']):
                        entry['meanings'].append({'partOfSpeech': POS.get(tag, tag or 'unspecified'),
                                                  'definitions': [{'definition': 'English explanation is not available in the offline source.'}]})
            return [entry]
        finally:
            db.close()
