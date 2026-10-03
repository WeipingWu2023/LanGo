"""LanGo desktop interface; DeepSeek supplies every result."""
import json
import os
import queue
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tkinter import ttk

from lango_ai import ServiceError, classify, load_key, lookup

ROOT = Path(__file__).resolve().parent
NAVY, BLUE, GOLD, PAPER, WHITE, INK, MUTED = '#101b35', '#2457c6', '#f2b84b', '#f6f8fd', '#ffffff', '#172747', '#52627d'


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('LanGo 1.3 · The word detective')
        icon = ROOT / 'assets' / 'lango.ico'
        if icon.exists(): self.iconbitmap(str(icon))
        self.geometry('1120x820')
        self.minsize(760, 560)
        self.configure(bg=PAPER)
        # Tk delegates text rasterisation to Windows; Segoe UI Variable and a
        # modest scaling factor keep glyphs smooth on high-DPI displays.
        self.tk.call('tk', 'scaling', 1.25)
        self.option_add('*Font', '{Segoe UI Variable Text} 11')
        local = Path(os.environ.get('LOCALAPPDATA', ROOT))
        self.directory = local / 'LanGo'
        legacy = local / 'Wordroom' / 'saved.json'
        if not (self.directory / 'saved.json').exists() and legacy.exists():
            self.directory.mkdir(parents=True, exist_ok=True)
            (self.directory / 'saved.json').write_bytes(legacy.read_bytes())
        self.events, self.executor, self.generation = queue.Queue(), ThreadPoolExecutor(max_workers=2), 0
        self.current, self.current_result, self.history = '', None, []
        self.saved_results = self.read_saved_results()
        self.saved = self.read_saved()
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.build()
        self.bind('<Control-l>', lambda e: (self.search.focus_set(), self.search.selection_range(0, 'end')))
        self.after(80, self.poll)
        self.search.focus_set()

    def read_saved(self):
        try:
            value = json.loads((self.directory / 'saved.json').read_text(encoding='utf-8'))
            return [w for w in value if isinstance(w, str)] if isinstance(value, list) else []
        except (OSError, ValueError): return []

    def read_saved_results(self):
        try:
            value = json.loads((self.directory / 'saved_results.json').read_text(encoding='utf-8'))
            return value if isinstance(value, dict) else {}
        except (OSError, ValueError): return {}

    def label(self, parent, value, size=11, color=INK, bold=False, **kw):
        return tk.Label(parent, text=value, font=('Segoe UI Variable Text', size, 'bold' if bold else 'normal'),
                        bg=parent.cget('bg'), fg=color, anchor='w', justify='left', **kw)

    def button(self, parent, value, command, primary=False):
        return tk.Button(parent, text=value, command=command, relief='flat', bd=0,
                         bg=BLUE if primary else '#e4ebfb', fg=WHITE if primary else INK,
                         activebackground='#bad0ff', padx=15, pady=9, cursor='hand2')

    def build(self):
        side = tk.Frame(self, bg=NAVY, width=225)
        side.pack(side='left', fill='y')
        side.pack_propagate(False)
        self.label(side, 'LANGO', 22, WHITE, True).pack(anchor='w', padx=22, pady=(28, 3))
        self.label(side, 'THE WORD DETECTIVE  ✦', 10, GOLD, True).pack(anchor='w', padx=22, pady=(0, 15))
        art = ROOT / 'assets' / 'detective.png'
        if art.exists():
            # The asset is pre-scaled with Lanczos during the build; PhotoImage
            # must display it at 1:1 to preserve anti-aliased edges.
            self.detective_art = tk.PhotoImage(file=str(art))
            tk.Label(side, image=self.detective_art, bg=NAVY).pack(anchor='center', pady=(0, 18))
        self.label(side, 'YOUR CASE FILES', 9, '#92b1ec', True).pack(anchor='w', padx=22)
        self.saved_list = tk.Listbox(side, bg=NAVY, fg=WHITE, borderwidth=0,
                                    highlightthickness=0, selectbackground=BLUE, activestyle='none', height=10)
        self.saved_list.pack(fill='x', padx=18, pady=8)
        self.saved_list.bind('<<ListboxSelect>>', self.open_saved)
        self.refresh_saved()
        self.button(side, 'Delete selected  ×', self.delete_saved).pack(fill='x', padx=18, pady=(0, 10))
        self.label(side, 'RECENT CLUES', 9, '#92b1ec', True).pack(anchor='w', padx=22, pady=(13, 5))
        self.recent = tk.Frame(side, bg=NAVY)
        self.recent.pack(fill='x', padx=18)
        self.label(side, 'DETECTIVE MODE  ·  ONLINE', 9, GOLD, True).pack(side='bottom', anchor='w', padx=22, pady=24)
        main = tk.Frame(self, bg=PAPER)
        main.pack(side='left', fill='both', expand=True, padx=26, pady=22)
        self.label(main, 'ENGLISH LEARNING · 中英双向翻译', 10, BLUE, True).pack(anchor='w')
        self.label(main, 'Every word has a story.', 25, INK, True).pack(anchor='w', pady=(6, 3))
        self.label(main, 'Investigate a word. Decode a sentence. Keep the clues that stick.', 11, MUTED).pack(anchor='w', pady=(0, 16))
        bar = tk.Frame(main, bg=WHITE, padx=8, pady=7, highlightbackground='#c7d7f6', highlightthickness=1)
        bar.pack(fill='x')
        self.search = tk.Entry(bar, relief='flat', font=('Segoe UI Variable Text', 15), bg=WHITE, fg=INK)
        self.search.pack(side='left', fill='x', expand=True, padx=10)
        self.search.bind('<Return>', lambda e: self.search_now())
        self.search.bind('<KeyRelease>', self.on_search_changed)
        self.clear_button = self.button(bar, 'Clear ×', self.clear_search)
        self.clear_button.pack(side='right', padx=(0, 6))
        self.investigate_button = self.button(bar, 'Investigate  →', self.search_now, True)
        self.investigate_button.pack(side='right')
        self.status = self.label(main, 'Enter an English word, an English sentence, or Chinese text.', 10, MUTED)
        self.status.pack(anchor='w', pady=11)
        frame = tk.Frame(main, bg=PAPER)
        frame.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(frame, bg=PAPER, highlightthickness=0)
        scroll = ttk.Scrollbar(frame, orient='vertical', command=self.canvas.yview)
        scroll.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        self.canvas.configure(yscrollcommand=scroll.set)
        self.body = tk.Frame(self.canvas, bg=PAPER)
        self.window = self.canvas.create_window((0, 0), window=self.body, anchor='nw')
        self.body.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', self.resize)
        self.bind_all('<MouseWheel>', lambda e: self.canvas.yview_scroll(-int(e.delta / 120), 'units'))
        card = self.card()
        self.field(card, '✦  YOUR NEXT CLUE', 10, BLUE, True)
        self.field(card, 'Start with a word or a sentence.', 18, INK, True)
        self.field(card, 'DeepSeek explains senses in English, shows Chinese meanings, and pairs examples with translations. Chinese input becomes natural English.', 11, MUTED)

    def resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)
        def wrap(widget):
            for child in widget.winfo_children():
                if isinstance(child, tk.Label):
                    child.configure(wraplength=max(350, event.width - 100))
                wrap(child)
        wrap(self.body)

    def card(self, background=WHITE):
        frame = tk.Frame(self.body, bg=background, padx=20, pady=18,
                         highlightbackground='#dbe4f5', highlightthickness=1)
        frame.pack(fill='x', pady=8, padx=(0, 4))
        return frame

    def field(self, parent, text, size=11, color=INK, bold=False, pad=(0, 5)):
        if text:
            self.label(parent, text, size, color, bold,
                       wraplength=max(350, self.canvas.winfo_width() - 100)).pack(anchor='w', fill='x', pady=pad)

    def clear(self):
        for child in self.body.winfo_children(): child.destroy()
        self.canvas.yview_moveto(0)

    def on_search_changed(self, _event=None):
        if not self.search.get().strip():
            self.cancel_search()

    def clear_search(self):
        self.search.delete(0, 'end')
        self.cancel_search()

    def cancel_search(self):
        self.generation += 1
        self.current = ''
        self.current_result = None
        self.clear()
        self.investigate_button.configure(text='Investigate  →', command=self.search_now)
        self.status.configure(text='Search cancelled. Enter a new word or sentence.', fg=MUTED)

    def search_now(self, text=None):
        text = text if text is not None else self.search.get()
        try:
            text, _ = classify(text)
            key = load_key(self.directory / 'settings.json')
        except ServiceError as exc:
            self.status.configure(text=str(exc), fg='#b84439')
            return
        self.search.delete(0, 'end')
        self.search.insert(0, text)
        self.generation += 1
        generation = self.generation
        self.current = ''
        self.current_result = None
        self.clear()
        self.investigate_button.configure(text='Cancel  ×', command=self.cancel_search)
        self.status.configure(text='DeepSeek is investigating… / 正在分析…', fg=BLUE)
        def work():
            try: self.events.put((generation, text, lookup(text, key), None))
            except Exception as exc: self.events.put((generation, text, None, str(exc)))
        self.executor.submit(work)

    def poll(self):
        try:
            while True:
                generation, text, result, error = self.events.get_nowait()
                if generation != self.generation: continue
                self.clear()
                self.investigate_button.configure(text='Investigate  →', command=self.search_now)
                if error:
                    self.status.configure(text=error, fg='#b84439')
                    self.button(self.body, 'Try again / 重试', lambda t=text: self.search_now(t)).pack(anchor='w', pady=10)
                elif result['kind'] == 'word': self.render_word(text, result)
                else: self.render_translation(text, result)
        except queue.Empty: pass
        self.after(80, self.poll)

    def render_word(self, text, result):
        self.current = text.lower()
        self.current_result = result
        self.status.configure(text='DeepSeek · English learning dossier / 英语学习档案', fg=MUTED)
        head = self.card(NAVY)
        self.field(head, result.get('headword') or text, 29, WHITE, True)
        self.field(head, result.get('pronunciation', ''), 12, GOLD)
        self.save_button = self.button(head, '✓ Saved' if self.current in self.saved else '+ Save word', self.toggle_saved)
        self.save_button.pack(anchor='w', pady=(8, 0))
        for number, sense in enumerate(result['senses'], 1):
            card = self.card()
            self.field(card, f'CASE {number:02d}  ·  {sense.get("part_of_speech", "meaning").upper()}', 10, BLUE, True)
            self.field(card, sense['definition_en'], 12, INK, True, (7, 7))
            self.field(card, sense.get('definition_zh', ''), 11, MUTED)
            self.field(card, sense.get('usage_note', ''), 10, BLUE)
            for index, example in enumerate(sense.get('examples', []), 1):
                if isinstance(example, dict):
                    self.field(card, f'{index}.  {example.get("en", "")}', 11, INK, False, (9, 2))
                    self.field(card, f'     {example.get("zh", "")}', 10, MUTED)
            for label, key in [('Similar clues', 'synonyms'), ('Opposites', 'antonyms')]:
                words = sense.get(key, [])
                if isinstance(words, list) and words:
                    self.field(card, label.upper() + '  ·  ' + '  /  '.join(str(w) for w in words), 10, BLUE)
        self.history = [self.current] + [w for w in self.history if w != self.current]
        for child in self.recent.winfo_children(): child.destroy()
        for word in self.history[:5]:
            tk.Button(self.recent, text=word, command=lambda w=word: self.search_now(w),
                      bg=NAVY, fg=WHITE, anchor='w', relief='flat', cursor='hand2').pack(fill='x')

    def render_translation(self, text, result):
        self.status.configure(text='DeepSeek · Context-aware translation / 语境翻译', fg=MUTED)
        original = self.card()
        self.field(original, 'ORIGINAL / 原文', 10, BLUE, True)
        self.field(original, text, 15)
        output = self.card('#e9f0ff')
        self.field(output, 'TRANSLATION / 译文', 10, BLUE, True)
        self.field(output, result['translation'], 16)
        self.field(output, result.get('note', ''), 10, MUTED, False, (10, 0))
        self.button(self.body, 'Copy translation / 复制译文', lambda: (
            self.clipboard_clear(), self.clipboard_append(result['translation']))).pack(anchor='w', pady=8)

    def refresh_saved(self):
        self.saved_list.delete(0, 'end')
        for word in self.saved: self.saved_list.insert('end', word)

    def open_saved(self, event):
        selected = self.saved_list.curselection()
        if not selected: return
        word = self.saved_list.get(selected[0])
        cached = self.saved_results.get(word.lower())
        if cached:
            self.generation += 1
            self.search.delete(0, 'end')
            self.search.insert(0, word)
            self.current = ''
            self.current_result = None
            self.clear()
            self.render_word(word, cached)
        else:
            self.search_now(word)

    def delete_saved(self):
        selected = self.saved_list.curselection()
        if not selected:
            return
        word = self.saved_list.get(selected[0])
        self.saved = [item for item in self.saved if item != word]
        self.saved_results.pop(word.lower(), None)
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            saved_tmp = self.directory / 'saved.tmp'
            saved_tmp.write_text(json.dumps(self.saved, ensure_ascii=False), encoding='utf-8')
            saved_tmp.replace(self.directory / 'saved.json')
            result_tmp = self.directory / 'saved_results.tmp'
            result_tmp.write_text(json.dumps(self.saved_results, ensure_ascii=False), encoding='utf-8')
            result_tmp.replace(self.directory / 'saved_results.json')
        except OSError:
            self.status.configure(text='Could not update your collection. / 无法更新生词。', fg='#b84439')
            return
        if self.search.get().strip().lower() == word.lower() or self.current == word.lower():
            self.cancel_search()
            self.search.delete(0, 'end')
        self.refresh_saved()
        self.status.configure(text=f'Removed {word} from your case files. / 已删除 {word}。', fg=MUTED)

    def toggle_saved(self):
        if not self.current: return
        removing = self.current in self.saved
        updated = [w for w in self.saved if w != self.current] if removing else self.saved + [self.current]
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            temporary = self.directory / 'saved.tmp'
            temporary.write_text(json.dumps(updated, ensure_ascii=False), encoding='utf-8')
            temporary.replace(self.directory / 'saved.json')
            if removing:
                self.saved_results.pop(self.current, None)
            elif self.current_result:
                self.saved_results[self.current] = self.current_result
            result_tmp = self.directory / 'saved_results.tmp'
            result_tmp.write_text(json.dumps(self.saved_results, ensure_ascii=False), encoding='utf-8')
            result_tmp.replace(self.directory / 'saved_results.json')
        except OSError:
            self.status.configure(text='Could not save your collection. / 无法保存生词。', fg='#b84439')
            return
        self.saved = updated
        self.refresh_saved()
        self.save_button.configure(text='✓ Saved' if self.current in self.saved else '+ Save word')

    def close(self):
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()


if __name__ == '__main__': App().mainloop()
