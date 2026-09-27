import io
import json
import unittest
import urllib.error
import urllib.parse
from unittest.mock import patch
from translation import Translator, TranslationError, validate_text, parse_translation


class TranslationTests(unittest.TestCase):
    def response(self):
        return io.BytesIO(json.dumps([[['我正在学习英语。', 'I am learning English.']], None, 'en']).encode())

    def test_sentence_case_punctuation_and_session_cache(self):
        service = Translator()
        text = 'I am learning English. Are you?'
        with patch('urllib.request.urlopen', return_value=self.response()) as request:
            self.assertEqual(service.translate(text), '我正在学习英语。')
            self.assertEqual(service.translate(text), '我正在学习英语。')
            request.assert_called_once()
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.call_args.args[0].full_url).query)
            self.assertEqual(query, {'q': [text], 'sl': ['en'], 'tl': ['zh-CN'], 'client': ['gtx'], 'dt': ['t']})

    def test_chinese_to_english_direction(self):
        with patch('urllib.request.urlopen', return_value=self.response()) as request:
            Translator().translate('你好吗？')
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.call_args.args[0].full_url).query)
            self.assertEqual(query['sl'], ['zh-CN'])
            self.assertEqual(query['tl'], ['en'])

    def test_limit_measures_utf8_bytes(self):
        self.assertEqual(validate_text(' a '), 'a')
        for text in ('', 'a' * 501, '中' * 167):
            with self.assertRaises(TranslationError):
                validate_text(text)

    def test_quota_error_not_rendered_as_translation(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.HTTPError('https://translate.googleapis.com', 429, 'limit', {}, None)):
            with self.assertRaisesRegex(TranslationError, 'limit reached'):
                Translator().translate('Hello there')

    def test_invalid_response_not_cached(self):
        service = Translator()
        with patch('urllib.request.urlopen', return_value=io.BytesIO(b'null')):
            with self.assertRaises(TranslationError):
                service.translate('Hello there')
        self.assertEqual(service.cache, {})

    def test_all_segments_preserved(self):
        self.assertEqual(parse_translation([[['第一句。 ', 'One.'], ['第二句。', 'Two.']], None]), '第一句。 第二句。')

    def test_malformed_segments_are_rejected(self):
        for data in (None, {}, [], [None], [[]], [[None]], [[[None]]], [[['']]], [[['valid'], [42]]]):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_translation(data)

    def test_idioms_sent_intact_without_rewriting(self):
        samples = [
            "understands astrophysics at a level that would make most people's heads spin",
            'The complexity made my head spin.',
            'The Earth spins on its axis.',
            "Let's break the ice.",
        ]
        for text in samples:
            with self.subTest(text=text), patch('urllib.request.urlopen', return_value=self.response()) as request:
                Translator().translate(text)
                query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.call_args.args[0].full_url).query)
                self.assertEqual(query['q'], [text])

    def test_http_failure_does_not_fall_back_or_cache(self):
        service = Translator()
        error = urllib.error.HTTPError('https://translate.googleapis.com', 503, 'unavailable', {}, None)
        with patch('urllib.request.urlopen', side_effect=error) as request:
            with self.assertRaises(TranslationError):
                service.translate('Hello there')
            request.assert_called_once()
        self.assertEqual(service.cache, {})
        with patch('urllib.request.urlopen', return_value=self.response()):
            self.assertEqual(service.translate('Hello there'), '我正在学习英语。')

    def test_session_cache_is_bounded(self):
        service = Translator()
        with patch('urllib.request.urlopen', side_effect=lambda *a, **k: self.response()):
            for index in range(51):
                service.translate(f'Sentence {index}')
        self.assertEqual(len(service.cache), 50)
        self.assertNotIn('Sentence 0', service.cache)

    def test_network_failure(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
            with self.assertRaisesRegex(TranslationError, 'connection'):
                Translator().translate('Hello there')


if __name__ == '__main__':
    unittest.main()
