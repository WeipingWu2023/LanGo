import io
import json
import unittest
import urllib.error
import urllib.parse
from unittest.mock import patch
from translation import Translator, TranslationError, validate_text


class TranslationTests(unittest.TestCase):
    def response(self, **kwargs):
        data = {'responseStatus': 200, 'responseData': {'translatedText': '我正在学习英语。'}}
        data.update(kwargs)
        return io.BytesIO(json.dumps(data).encode())

    def test_sentence_case_punctuation_and_session_cache(self):
        service = Translator()
        text = 'I am learning English. Are you?'
        with patch('urllib.request.urlopen', return_value=self.response()) as request:
            self.assertEqual(service.translate(text), '我正在学习英语。')
            self.assertEqual(service.translate(text), '我正在学习英语。')
            request.assert_called_once()
            query = urllib.parse.parse_qs(urllib.parse.urlsplit(request.call_args.args[0].full_url).query)
            self.assertEqual(query, {'q': [text], 'langpair': ['en|zh-CN']})

    def test_chinese_to_english_direction(self):
        with patch('urllib.request.urlopen', return_value=self.response()) as request:
            Translator().translate('你好吗？')
            self.assertIn('zh-CN%7Cen', request.call_args.args[0].full_url)

    def test_limit_measures_utf8_bytes(self):
        self.assertEqual(validate_text(' a '), 'a')
        for text in ('', 'a' * 501, '中' * 167):
            with self.assertRaises(TranslationError):
                validate_text(text)

    def test_quota_error_not_rendered_as_translation(self):
        with patch('urllib.request.urlopen', return_value=self.response(quotaFinished=True)):
            with self.assertRaisesRegex(TranslationError, 'limit reached'):
                Translator().translate('Hello there')

    def test_invalid_response_not_cached(self):
        service = Translator()
        with patch('urllib.request.urlopen', return_value=self.response(responseData=None)):
            with self.assertRaises(TranslationError):
                service.translate('Hello there')
        self.assertEqual(service.cache, {})

    def test_network_failure(self):
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('offline')):
            with self.assertRaisesRegex(TranslationError, 'connection'):
                Translator().translate('Hello there')


if __name__ == '__main__':
    unittest.main()
