"""Wordroom: a small, dependency-free desktop English dictionary."""
from __future__ import annotations

import json
import os
import queue
import re
import threading
import tkinter as tk
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
import copy
from offline_dictionary import OfflineDictionary
from translation import Translator, TranslationError, validate_text
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parent
BG, WHITE, INK, MUTED, ACCENT = '#f3f5f1', '#ffffff', '#203d34', '#6e7d75', '#23745d'


class LookupError(Exception):
    pass


def normalize(word):
    word = ' '.join(word.strip().lower().replace('’', "'").replace('–', '-').split())
    if not re.fullmatch(r"[a-z][a-z0-9 .&'\-]*", word) or len(word) > 100 or '..' in word:
        raise LookupError('Enter an English word or phrase. / 请输入英文单词或短语。')
    return word


class Dictionary:
    def __init__(self, data_dir=None):
        self.directory = Path(data_dir or os.environ.get('LOCALAPPDATA', ROOT)) / 'Wordroom'
        self.lock = threading.Lock()
        self.starter = json.loads((ROOT / 'starter.json').read_text(encoding='utf-8'))
        self.offline = OfflineDictionary()

    def lookup(self, word, online=False):
        word = normalize(word)
        local = self.offline.lookup(word)
        def translated(entries):
            entries = copy.deepcopy(entries)
            if local:
                entries[0]['translation'] = local[0].get('translation', '')
                if not entries[0].get('phonetic'):
                    entries[0]['phonetic'] = local[0].get('phonetic', '')
                entries[0]['translationSource'] = 'Chinese definitions: ECDICT (MIT)'
            return entries
        if not online and word in self.starter:
            return translated(self.starter[word]), 'Offline / 离线词典'
        path = self.directory / 'cache' / (word + '.json')
        try:
            cached = json.loads(path.read_text(encoding='utf-8'))
            if not online and isinstance(cached, list) and cached and all(isinstance(e, dict) and isinstance(e.get('meanings'), list) for e in cached):
                return translated(cached), 'Saved entry + offline Chinese / 本地缓存'
        except (OSError, ValueError):
            pass
        if not online:
            if local:
                return local, 'Offline / 离线词典 · ECDICT + WordNet'
            raise LookupError(f'“{word}” is not in the offline dictionary. Check the spelling, try a base form, or use Online lookup below. / 离线词库未收录，可尝试联网查询。')
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en/' + urllib.parse.quote(word)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Wordroom/1.0', 'Accept': 'application/json'})
            with urllib.request.urlopen(req, timeout=5) as response:
                entries = json.load(response)
            if not isinstance(entries, list) or not entries or any(not isinstance(e, dict) or not isinstance(e.get('meanings'), list) for e in entries):
                raise LookupError('The dictionary returned an unexpected response. Please try again.')
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise LookupError(f'No entry found for “{word}”. Check the spelling or try the base form.') from exc
            raise LookupError('Online details are unavailable. Offline searches still work. / 在线服务暂不可用，离线查词不受影响。') from exc
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise LookupError('Could not connect. Saved words and the offline starter dictionary are still available.') from exc
        try:
            with self.lock:
                path.parent.mkdir(parents=True, exist_ok=True)
                temp = path.with_suffix('.tmp')
                temp.write_text(json.dumps(entries, ensure_ascii=False), encoding='utf-8')
                temp.replace(path)
        except OSError:
            pass
        return translated(entries), 'Free Dictionary API + offline Chinese'


def meanings(entries):
    return [m for entry in entries for m in entry.get('meanings', [])]


def relations(meaning, kind):
    values = list(meaning.get(kind, []))
    for definition in meaning.get('definitions', []):
        values.extend(definition.get(kind, []))
    return list(dict.fromkeys(w.lower() for w in values if isinstance(w, str)))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Wordroom 1.2.1 • English–Chinese Dictionary')
        icon = ROOT / 'assets' / 'wordroom.ico'
        if icon.exists():
            self.iconbitmap(str(icon))
        self.geometry('1100x800')
        self.minsize(760, 560)
        self.configure(bg=BG)
        self.option_add('*Font', '{Segoe UI} 11')
        self.service = Dictionary()
        self.translator = Translator()
        self.events = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=6)
        self.online_executor = ThreadPoolExecutor(max_workers=2)
        self.pending = []
        self.generation = 0
        self.current = ''
        self.cards = {}
        self.history = []
        self.saved = self.read_saved()
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.build()
        self.bind('<Control-l>', lambda e: (self.search.focus_set(), self.search.selection_range(0, 'end')))
        self.after(70, self.poll)
        self.search.focus_set()

    def read_saved(self):
        try:
            data = json.loads((self.service.directory / 'saved.json').read_text(encoding='utf-8'))
            return [w for w in data if isinstance(w, str)] if isinstance(data, list) else []
        except (OSError, ValueError):
            return []

    def label(self, parent, text, size=11, color=INK, bold=False, bg=None, **kwargs):
        return tk.Label(parent, text=text, font=('Segoe UI', size, 'bold' if bold else 'normal'),
                        fg=color, bg=bg or parent.cget('bg'), anchor='w', justify='left', **kwargs)

    def button(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, relief='flat', bd=0,
                         bg=ACCENT if primary else '#e6ede7', fg=WHITE if primary else INK,
                         activebackground='#d0e2d5', padx=16, pady=9, cursor='hand2')

    def build(self):
        sidebar = tk.Frame(self, bg=INK, width=210)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        self.label(sidebar, 'wordroom.', 25, WHITE, True).pack(anchor='w', padx=22, pady=(30, 0))
        self.label(sidebar, 'A little word. A wider world.', 9, '#b9d0c4').pack(anchor='w', padx=22, pady=(5, 35))
        self.label(sidebar, 'YOUR COLLECTION', 9, '#b9d0c4', True).pack(anchor='w', padx=22)
        self.saved_list = tk.Listbox(sidebar, bg=INK, fg=WHITE, borderwidth=0, highlightthickness=0,
                                    selectbackground=ACCENT, activestyle='none', height=12)
        self.saved_list.pack(fill='x', padx=18, pady=12)
        self.saved_list.bind('<<ListboxSelect>>', self.open_saved)
        self.refresh_saved()
        self.label(sidebar, 'RECENT WORDS', 9, '#b9d0c4', True).pack(anchor='w', padx=22, pady=(20, 8))
        self.recent = tk.Frame(sidebar, bg=INK)
        self.recent.pack(fill='x', padx=18)
        self.label(sidebar, 'English ↔ 中文释义\n770,000+ offline entries\n\nCtrl + L to search', 10, '#b9d0c4').pack(side='bottom', anchor='w', padx=22, pady=25)
        main = tk.Frame(self, bg=BG)
        main.pack(side='left', fill='both', expand=True, padx=30, pady=25)
        self.label(main, 'ENGLISH–CHINESE DICTIONARY · 英汉词典', 10, ACCENT, True).pack(anchor='w')
        self.label(main, 'Make every word stick.', 26, INK, True).pack(anchor='w', pady=(8, 18))
        bar = tk.Frame(main, bg=WHITE, padx=8, pady=7)
        bar.pack(fill='x')
        self.search = tk.Entry(bar, relief='flat', font=('Segoe UI', 15), bg=WHITE, fg=INK)
        self.search.pack(side='left', fill='x', expand=True, padx=10)
        self.search.bind('<Return>', lambda e: self.lookup())
        self.button(bar, 'Look up  →', self.lookup, True).pack(side='right')
        self.button(bar, 'Translate', lambda: self.lookup(translate=True)).pack(side='right', padx=5)
        self.label(main, 'Words: offline · Sentences: online via Google Translate / 单词离线 · 句子联网翻译', 9, MUTED).pack(anchor='w', pady=(8, 0))
        self.status = self.label(main, 'Enter a word or sentence. / 请输入单词或句子。', 10, MUTED)
        self.status.pack(anchor='w', pady=10)
        container = tk.Frame(main, bg=BG)
        container.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.body = tk.Frame(self.canvas, bg=BG)
        self.window = self.canvas.create_window((0, 0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self.resize)
        self.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(-int(e.delta / 120), 'units'))

    def resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)
        self.wrap_labels(self.body, max(280, event.width - 55))

    def wrap_labels(self, widget, width):
        for child in widget.winfo_children():
            if isinstance(child, tk.Label):
                child.configure(wraplength=width)
            self.wrap_labels(child, width)

    def submit(self, generation, kind, key, word):
        def work():
            try:
                if generation != self.generation:
                    return
                if kind == 'translation':
                    result = self.translator.translate(word)
                else:
                    try:
                        result = self.service.lookup(word, online=kind == 'online')
                    except LookupError:
                        if kind == 'main' and len(word.split()) > 1:
                            self.events.put((generation, 'translate-needed', key, None, None))
                            return
                        raise
                self.events.put((generation, kind, key, result, None))
            except Exception as exc:
                self.events.put((generation, kind, key, None, str(exc)))
        self.pending = [future for future in self.pending if not future.done()]
        executor = self.online_executor if kind in ('online', 'translation') else self.executor
        self.pending.append(executor.submit(work))

    def fetch_online(self, word):
        self.status.configure(text='Loading optional online details… You can keep searching offline.', fg=MUTED)
        self.submit(self.generation, 'online', word, word)

    def lookup(self, word=None, translate=False):
        try:
            word = validate_text(word if word is not None else self.search.get())
            if not translate:
                try:
                    normalize(word)
                except LookupError:
                    translate = True
        except TranslationError as exc:
            self.status.configure(text=str(exc), fg='#a34335')
            return
        self.search.delete(0, 'end')
        self.search.insert(0, word)
        self.generation += 1
        self.current = ''
        for future in self.pending:
            future.cancel()
        self.pending = []
        self.clear()
        self.status.configure(text='Translating… / 翻译中…' if translate else 'Looking up… / 查询中…', fg=MUTED)
        self.submit(self.generation, 'translation' if translate else 'main', word, word)

    def clear(self):
        for child in self.body.winfo_children():
            child.destroy()
        self.cards = {}
        self.canvas.yview_moveto(0)

    def poll(self):
        try:
            while True:
                generation, kind, key, result, error = self.events.get_nowait()
                if generation != self.generation:
                    continue
                if kind == 'translate-needed':
                    self.status.configure(text='Translating… / 翻译中…', fg=MUTED)
                    self.submit(generation, 'translation', key, key)
                    continue
                if kind == 'translation':
                    if error:
                        self.clear()
                        self.status.configure(text=error, fg='#a34335')
                        self.button(self.body, 'Retry translation / 重试翻译', lambda w=key: self.lookup(w, translate=True)).pack(anchor='w', pady=12)
                    else:
                        self.render_translation(key, result)
                    continue
                if kind in ('main', 'online'):
                    if error:
                        if kind == 'online':
                            self.status.configure(text=error, fg='#a34335')
                            continue
                        self.clear()
                        self.label(self.body, 'Let’s try another word.', 21, bold=True).pack(anchor='w', pady=(25, 12))
                        self.label(self.body, error, color=MUTED, wraplength=550).pack(anchor='w')
                        self.button(self.body, 'Online lookup / 联网查询', lambda w=key: self.fetch_online(w)).pack(anchor='w', pady=15)
                        self.status.configure(text='No offline entry / 离线词库未找到', fg='#a34335')
                    else:
                        self.render(normalize(key), *result)
                elif key in self.cards:
                    self.render_relation(key, result, error)
        except queue.Empty:
            pass
        self.after(70, self.poll)

    def render_translation(self, original, translated):
        self.clear()
        self.current = ''
        self.status.configure(text='Google Translate · Machine translation / 机器翻译', fg=MUTED)
        for title, text, color in [('Original / 原文', original, WHITE), ('Translation / 译文', translated, '#e4efe5')]:
            frame = tk.Frame(self.body, bg=color, padx=18, pady=15)
            frame.pack(fill='x', pady=8, padx=(0, 5))
            self.label(frame, title, 10, ACCENT, True).pack(anchor='w')
            output = tk.Text(frame, height=min(10, max(2, len(text) // 55 + 2)), wrap='word',
                             bg=color, fg=INK, relief='flat', font=('Segoe UI', 14))
            output.insert('1.0', text)
            output.configure(state='disabled')
            output.pack(fill='x', pady=(8, 0))
        self.button(self.body, 'Copy translation / 复制译文', lambda: (self.clipboard_clear(), self.clipboard_append(translated))).pack(anchor='w', pady=8)

    def brief_label(self, parent, text, size=11, color=MUTED, maximum=180):
        text = text.strip()
        shortened = text[:maximum].rsplit(' ', 1)[0].rstrip(' ,;') + '…' if len(text) > maximum else text
        label = self.label(parent, shortened, size, color, wraplength=max(280, self.canvas.winfo_width() - 70))
        if shortened != text:
            label.configure(cursor='hand2')
            label.bind('<Button-1>', lambda e: label.configure(text=text if label.cget('text') == shortened else shortened))
        return label

    def render(self, word, entries, source, limit=3, related_limit=3):
        self.clear()
        self.current = word
        self.status.configure(text=source, fg=MUTED)
        top = tk.Frame(self.body, bg=BG)
        top.pack(fill='x', pady=(10, 8))
        self.label(top, word, 34, bold=True).pack(side='left')
        self.save_button = self.button(top, '✓ Saved' if word in self.saved else '+ Save word', self.toggle_saved)
        self.save_button.pack(side='right', padx=4)
        phonetic = next((e.get('phonetic') or next((p['text'] for p in e.get('phonetics', []) if p.get('text')), '') for e in entries), '')
        self.label(self.body, phonetic, 13, MUTED).pack(anchor='w')
        chinese = next((e.get('translation') for e in entries if e.get('translation')), '')
        if chinese:
            translation_card = tk.Frame(self.body, bg='#e4efe5', padx=18, pady=13)
            translation_card.pack(fill='x', pady=(14, 6), padx=(0, 5))
            self.label(translation_card, '中文释义', 11, ACCENT, True).pack(anchor='w')
            self.brief_label(translation_card, chinese, 13, INK).pack(anchor='w', fill='x', pady=(6, 0))
        if entries[0].get('baseForm'):
            self.label(self.body, 'Base form / 原形: ' + entries[0]['baseForm'], 11, MUTED).pack(anchor='w', pady=6)
        self.button(self.body, 'Online details (optional) / 补充在线释义', lambda: self.fetch_online(word)).pack(anchor='w', pady=6)
        all_meanings = []
        for meaning in meanings(entries):
            definitions = [d for d in meaning.get('definitions', []) if d.get('definition') and
                           d['definition'] != 'English explanation is not available in the offline source.']
            if definitions:
                all_meanings.append(dict(meaning, definitions=definitions))
        parts = list(dict.fromkeys(m.get('partOfSpeech', 'unknown') for m in all_meanings))
        if parts:
            self.label(self.body, 'PARTS OF SPEECH  /  ' + '  ·  '.join(parts), 10, ACCENT, True).pack(anchor='w', pady=(15, 8))
        for index, meaning in enumerate(all_meanings[:limit]):
            card = tk.Frame(self.body, bg=WHITE, padx=20, pady=18)
            card.pack(fill='x', pady=8, padx=(0, 5))
            pos = meaning.get('partOfSpeech', 'unknown')
            self.label(card, pos.upper(), 11, ACCENT, True).pack(anchor='w', pady=(0, 8))
            for number, definition in enumerate(meaning.get('definitions', []), 1):
                self.brief_label(card, f'{number:02d}  {definition.get("definition", "")}', 12, INK).pack(anchor='w', fill='x', pady=(5, 3))
                example = definition.get('example')
                if example:
                    self.brief_label(card, f'“{example.splitlines()[0]}”').pack(anchor='w', fill='x', padx=(25, 0), pady=(0, 8))
            for kind in ('synonyms', 'antonyms'):
                words = relations(meaning, kind)
                if not words:
                    continue
                self.label(card, kind.upper(), 9, ACCENT if kind == 'synonyms' else '#a06640', True).pack(anchor='w', pady=(12, 5))
                for related in words[:related_limit]:
                    key = (index, kind, related)
                    frame = tk.Frame(card, bg='#f5f7f3', padx=12, pady=9)
                    frame.pack(fill='x', pady=4)
                    link = self.label(frame, related + '  ↗', 12, ACCENT, True, cursor='hand2')
                    link.pack(anchor='w')
                    link.bind('<Button-1>', lambda e, w=related: self.lookup(w))
                    detail = self.label(frame, '', 10, MUTED, wraplength=600)
                    detail.pack(anchor='w', fill='x', pady=(5, 0))
                    hint = meaning.get('definitions', [{}])[0].get('definition', '') if kind == 'synonyms' else ''
                    self.cards[key] = (detail, pos, hint)
                    self.submit(self.generation, 'related', key, related)
                if len(words) > related_limit:
                    self.button(card, f'More {kind}…', lambda: self.render(word, entries, source, limit, 1000)).pack(anchor='w')
        if len(all_meanings) > limit:
            self.button(self.body, f'Show more meanings / 更多释义 ({len(all_meanings) - limit})',
                        lambda: self.render(word, entries, source, limit + 3, related_limit)).pack(anchor='w', pady=12)
        sources = list(dict.fromkeys(url for e in entries for url in e.get('sourceUrls', []) if url.startswith('https://')))
        for url in sources:
            link = self.label(self.body, 'Dictionary source ↗', 9, ACCENT, cursor='hand2')
            link.pack(anchor='w')
            link.bind('<Button-1>', lambda e, u=url: webbrowser.open(u))
        for entry in entries:
            license_info = entry.get('license', {})
            if license_info:
                self.label(self.body, 'License: ' + license_info.get('name', ''), 9, MUTED).pack(anchor='w')
                break
        if entries[0].get('translationSource'):
            self.label(self.body, entries[0]['translationSource'], 9, MUTED).pack(anchor='w')
        self.wrap_labels(self.body, max(280, self.canvas.winfo_width() - 55))
        self.history = [word] + [w for w in self.history if w != word]
        for child in self.recent.winfo_children():
            child.destroy()
        for recent in self.history[:6]:
            tk.Button(self.recent, text=recent, command=lambda w=recent: self.lookup(w), anchor='w',
                      bg=INK, fg='#dbe8df', relief='flat', cursor='hand2').pack(fill='x')

    def render_relation(self, key, result, error):
        label, pos, hint = self.cards[key]
        if error:
            label.pack_forget()
            return
        entries, _ = result
        candidates = meanings(entries)
        same_pos = [m for m in candidates if m.get('partOfSpeech') == pos]
        selected = (same_pos or candidates)
        if not selected:
            label.pack_forget()
            return
        meaning = next((m for m in selected if any(d.get('definition') == hint for d in m.get('definitions', []))), selected[0])
        definitions = meaning.get('definitions', [])
        definition = next((d for d in definitions if d.get('example')), definitions[0] if definitions else {})
        example = definition.get('example')
        chinese = next((e.get('translation') for e in entries if e.get('translation')), '')
        lines = [f'{meaning.get("partOfSpeech", "")} · {definition.get("definition", "")}']
        if chinese:
            lines.append(chinese.splitlines()[0])
        if example:
            lines.append(f'“{example.splitlines()[0]}”')
        full = '\n'.join(lines)
        shortened = '\n'.join(line[:177] + '…' if len(line) > 180 else line for line in lines)
        label.configure(text=shortened)
        if shortened != full:
            label.configure(cursor='hand2')
            label.bind('<Button-1>', lambda e: label.configure(text=full if label.cget('text') == shortened else shortened))

    def refresh_saved(self):
        self.saved_list.delete(0, 'end')
        for word in self.saved:
            self.saved_list.insert('end', word)

    def open_saved(self, event):
        selection = self.saved_list.curselection()
        if selection:
            self.lookup(self.saved_list.get(selection[0]))

    def toggle_saved(self):
        if not self.current:
            return
        updated = [w for w in self.saved if w != self.current] if self.current in self.saved else self.saved + [self.current]
        try:
            self.service.directory.mkdir(parents=True, exist_ok=True)
            path = self.service.directory / 'saved.json'
            temp = path.with_suffix('.tmp')
            temp.write_text(json.dumps(updated), encoding='utf-8')
            temp.replace(path)
        except OSError:
            self.status.configure(text='Could not save your collection. Check folder permissions.', fg='#a34335')
            return
        self.saved = updated
        self.refresh_saved()
        self.save_button.configure(text='✓ Saved' if self.current in self.saved else '+ Save word')

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.online_executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()


if __name__ == '__main__':
    App().mainloop()
