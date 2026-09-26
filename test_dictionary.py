import json
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from dictionary import Dictionary, LookupError, meanings, normalize, relations


class DictionaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.service = Dictionary(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_offline_parts_and_every_related_word_has_examples(self):
        entries, _ = self.service.lookup(' LIGHT ')
        self.assertEqual({m['partOfSpeech'] for m in meanings(entries)}, {'noun', 'verb', 'adjective', 'adverb'})
        for entries in self.service.starter.values():
            for meaning in meanings(entries):
                for kind in ('synonyms', 'antonyms'):
                    for word in relations(meaning, kind):
                        related, _ = self.service.lookup(word)
                        self.assertTrue(all(d.get('example') for m in meanings(related) for d in m['definitions']))

    def test_rejects_paths_and_empty_input(self):
        for word in ('', '../hello', 'a/b', 'a\\b', '123'):
            with self.assertRaises(LookupError):
                normalize(word)

    def test_cached_entry_works_without_network(self):
        cache = self.service.directory / 'cache' / 'test.json'
        cache.parent.mkdir(parents=True)
        cache.write_text(json.dumps([{'word': 'test', 'meanings': []}]))
        with patch('urllib.request.urlopen', side_effect=AssertionError('Network must not be used')):
            entries, source = self.service.lookup('test')
        self.assertEqual(entries[0]['word'], 'test')
        self.assertIn('Saved entry', source)
        self.assertTrue(entries[0]['translation'])

    def test_network_failure_is_actionable(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
            with self.assertRaisesRegex(LookupError, 'Could not connect'):
                self.service.lookup('unavailable', online=True)

    def test_not_found(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.HTTPError('url', 404, 'missing', {}, None)):
            with self.assertRaisesRegex(LookupError, 'No entry found'):
                self.service.lookup('nonexistentword', online=True)

    def test_peasant_and_common_words_work_without_network(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('No network allowed')):
            for word in ('peasant', 'need', 'dictionary', 'computer', 'serendipity', 'run', 'beautiful', 'look up'):
                entries, _ = self.service.lookup(word)
                self.assertTrue(entries[0]['translation'], word)
                self.assertTrue(meanings(entries), word)
            self.assertIn('农夫', self.service.lookup('peasant')[0][0]['translation'])

    def test_inflected_words_and_normalization(self):
        self.assertEqual(normalize('  LOOK   UP  '), 'look up')
        self.assertEqual(normalize('don’t'), "don't")
        entries, _ = self.service.lookup('peasants')
        self.assertEqual(entries[0]['baseForm'], 'peasant')
        self.assertTrue(meanings(entries))

    def test_offline_miss_is_instant_and_does_not_attempt_network(self):
        with patch('urllib.request.urlopen', side_effect=AssertionError('No network allowed')):
            with self.assertRaisesRegex(LookupError, 'not in the offline dictionary'):
                self.service.lookup('zzzxqnonexistentword')

    def test_wordnet_senses_relations_and_examples(self):
        entries, _ = self.service.lookup('happy')
        self.assertTrue(any('unhappy' in relations(m, 'antonyms') for m in meanings(entries)))
        self.assertTrue(any(d.get('example') for m in meanings(entries) for d in m['definitions']))

    def test_corrupt_cache_falls_back_to_offline(self):
        cache = self.service.directory / 'cache' / 'peasant.json'
        cache.parent.mkdir(parents=True)
        cache.write_text('{broken')
        self.assertIn('农夫', self.service.lookup('peasant')[0][0]['translation'])


if __name__ == '__main__':
    unittest.main()
