"""Whole-sentence Google Translate requests; no text is saved to disk.

This public web endpoint is not the supported Google Cloud Translation API.
It needs no embedded credentials, but availability and response format may change.
"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request


class TranslationError(Exception):
    pass


def parse_translation(data):
    """Read every translated segment, rejecting incomplete/malformed responses."""
    if not isinstance(data, list) or not data or not isinstance(data[0], list) or not data[0]:
        raise ValueError('Invalid translation response')
    parts = []
    for segment in data[0]:
        if not isinstance(segment, list) or not segment or not isinstance(segment[0], str) or not segment[0].strip():
            raise ValueError('Invalid translation segment')
        parts.append(segment[0])
    return ''.join(parts).strip()


def validate_text(text):
    text = text.strip()
    if not text:
        raise TranslationError('Enter a word or sentence. / 请输入单词或句子。')
    if len(text.encode('utf-8')) > 500:
        raise TranslationError('Please use a shorter sentence (maximum 500 UTF-8 bytes). / 请缩短句子。')
    return text


class Translator:
    def __init__(self):
        self.cache = {}

    def translate(self, text):
        text = validate_text(text)
        if text in self.cache:
            return self.cache[text]
        source, target = ('zh-CN', 'en') if re.search(r'[\u3400-\u9fff]', text) else ('en', 'zh-CN')
        # Send the complete input so the service can interpret idioms in context.
        # Do not rewrite individual words or substitute hardcoded translations.
        url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({
            'client': 'gtx', 'sl': source, 'tl': target, 'dt': 't', 'q': text})
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Wordroom/1.2.1'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.load(response)
            result = parse_translation(data)
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                raise TranslationError('Translation limit reached. Try later. / 翻译额度已用完，请稍后重试。')
            raise TranslationError('Google Translate unavailable. Please retry later. / 谷歌翻译暂不可用，请稍后重试。') from exc
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, AttributeError) as exc:
            raise TranslationError('Translation unavailable. Check your connection and retry. / 翻译暂不可用，请检查网络后重试。') from exc
        if len(self.cache) >= 50:
            self.cache.pop(next(iter(self.cache)))
        self.cache[text] = result
        return result
