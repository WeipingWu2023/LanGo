import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from lango_ai import ServiceError, classify, load_key, lookup, save_key, validate_result


EXAMPLES = [{'en': f'An example {n}.', 'zh': f'例句{n}。'} for n in range(3)]
WORD = {'kind': 'word', 'headword': 'light', 'pronunciation': '/laɪt/',
        'senses': [{'part_of_speech': 'noun', 'definition_en': 'Visible electromagnetic radiation.',
                    'definition_zh': '光。', 'usage_note': '', 'examples': EXAMPLES,
                    'synonyms': [], 'antonyms': []}]}
TRANSLATION = {'kind': 'translation', 'original': '我听得一头雾水。',
               'translation': 'I was completely lost.', 'direction': 'zh_en', 'note': 'An idiom.'}


class DeepSeekTests(unittest.TestCase):
    def response(self, content):
        return io.BytesIO(json.dumps({'choices': [{'message': {'content': json.dumps(content, ensure_ascii=False)},
                                                   'finish_reason': 'stop'}]}).encode())

    def test_routes_word_english_and_chinese_sentences(self):
        self.assertEqual(classify('  LIGHT '), ('LIGHT', 'word'))
        self.assertEqual(classify('The light is on.'), ('The light is on.', 'en_zh'))
        self.assertEqual(classify('我听得一头雾水。'), ('我听得一头雾水。', 'zh_en'))

    def test_lango_ai_is_the_only_provider_and_prompt_preserves_text(self):
        samples = [('light', WORD), ('我听得一头雾水。', TRANSLATION)]
        for text, expected in samples:
            with self.subTest(text=text), patch('urllib.request.urlopen', return_value=self.response(expected)) as call:
                self.assertEqual(lookup(text, 'test-key'), expected)
                request = call.call_args.args[0]
                self.assertEqual(request.full_url, 'https://api.deepseek.com/chat/completions')
                self.assertEqual(request.get_header('Authorization'), 'Bearer test-key')
                payload = json.loads(request.data)
                self.assertEqual(payload['model'], 'deepseek-flash')
                self.assertIn(text, payload['messages'][1]['content'])

    def test_requires_complete_bilingual_examples(self):
        broken = json.loads(json.dumps(WORD))
        broken['senses'][0]['examples'] = EXAMPLES[:2]
        with self.assertRaisesRegex(ServiceError, 'examples'):
            validate_result(broken, 'word')

    def test_quota_failure_names_actual_provider_and_no_fallback(self):
        error = urllib.error.HTTPError('https://api.deepseek.com', 429, 'rate limit', {}, None)
        with patch('urllib.request.urlopen', side_effect=error) as call:
            with self.assertRaisesRegex(ServiceError, 'DeepSeek is busy'):
                lookup('light', 'test-key')
            call.assert_called_once()

    def test_encrypted_key_round_trip_and_missing_key(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'api-key.bin'
            with self.assertRaisesRegex(ServiceError, 'settings.json'):
                load_key(path)
            fake = 'sk-' + 'a' * 32
            try:
                save_key(path, fake)
            except OSError as error:
                self.skipTest(f'Windows DPAPI unavailable in this test environment: {error}')
            self.assertNotIn(fake.encode(), path.read_bytes())
            self.assertEqual(load_key(path), fake)

    def test_input_size_and_missing_translation(self):
        with self.assertRaises(ServiceError): classify('中' * 501)
        with self.assertRaises(ServiceError): validate_result({'kind': 'translation', 'translation': ''}, 'zh_en')


if __name__ == '__main__': unittest.main()
