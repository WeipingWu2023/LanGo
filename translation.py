"""Explicit sentence translation through MyMemory; no text is saved to disk."""
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request


class TranslationError(Exception):
    pass


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
        pair = 'zh-CN|en' if re.search(r'[\u3400-\u9fff]', text) else 'en|zh-CN'
        url = 'https://api.mymemory.translated.net/get?' + urllib.parse.urlencode({'q': text, 'langpair': pair})
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Wordroom/1.2.0'})
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.load(response)
            if not isinstance(data, dict):
                raise ValueError('Invalid response')
            if data.get('quotaFinished') or str(data.get('responseStatus')) == '429':
                raise TranslationError('Translation limit reached. Try later. / 翻译额度已用完，请稍后重试。')
            result = data.get('responseData', {}).get('translatedText')
            if str(data.get('responseStatus')) != '200' or not isinstance(result, str) or not result.strip():
                raise ValueError('No translation')
            result = html.unescape(result).strip()
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, AttributeError) as exc:
            raise TranslationError('Translation unavailable. Check your connection and retry. / 翻译暂不可用，请检查网络后重试。') from exc
        if len(self.cache) >= 50:
            self.cache.pop(next(iter(self.cache)))
        self.cache[text] = result
        return result
