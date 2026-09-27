"""Exercise the real Tk window, including a stalled online request."""
import sys
import tempfile
import threading
import time
import tkinter as tk
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dictionary import App, LookupError


def wait(app, condition, timeout=3):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        app.update()
        if condition():
            return
        time.sleep(.005)
    raise AssertionError('UI condition timed out')


def labels(widget):
    result = []
    for child in widget.winfo_children():
        if isinstance(child, tk.Label):
            result.append(child.cget('text'))
        result.extend(labels(child))
    return result


with tempfile.TemporaryDirectory() as temp:
    with patch.dict('os.environ', {'LOCALAPPDATA': temp}):
        app = App()
        release = threading.Event()
        started = threading.Event()
        try:
            app.update()
            assert app.search.get() == '' and app.current == '' and not app.history
            assert not app.pending
            app.lookup('bright')
            wait(app, lambda: app.current == 'bright')
            original = app.service.lookup
            def delayed(word, online=False):
                if online:
                    started.set()
                    release.wait(5)
                    raise LookupError('Simulated service failure')
                return original(word)
            app.service.lookup = delayed
            app.fetch_online('bright')
            wait(app, started.is_set)
            before = time.perf_counter()
            app.lookup('peasant')
            wait(app, lambda: app.current == 'peasant')
            elapsed = time.perf_counter() - before
            assert any('农夫' in text for text in labels(app.body))
            assert 'ANTONYMS' not in labels(app.body)
            assert not any('No example' in text or 'No antonyms' in text or 'REMEMBER IT' in text for text in labels(app.body))
            assert elapsed < 1, elapsed
            app.toggle_saved()
            assert 'peasant' in app.saved
            app.lookup('need')
            wait(app, lambda: app.current == 'need')
            release.set()
            wait(app, lambda: all(f.done() for f in app.pending))
            assert app.current == 'need'
            app.lookup('run')
            wait(app, lambda: app.current == 'run')
            assert any(isinstance(w, tk.Button) and 'Show more meanings' in w.cget('text') for w in app.body.winfo_children())
            with patch.object(app.translator, 'translate', return_value='我正在学习英语。') as translator:
                for sentence in ('I am learning English.', 'I am learning English'):
                    app.lookup(sentence)
                    wait(app, lambda: app.status.cget('text').startswith('Google Translate'))
                    assert app.search.get() == sentence and app.current == ''
                    assert sentence not in app.saved and sentence not in app.history
                    outputs = [w for frame in app.body.winfo_children() for w in frame.winfo_children() if isinstance(w, tk.Text)]
                    assert any('我正在学习英语。' in w.get('1.0', 'end') for w in outputs)
                self_calls = translator.call_count
                app.lookup('look up')
                wait(app, lambda: app.current == 'look up')
                assert translator.call_count == self_calls
            print(f'UI passed: blank startup, sentence routing, concise sections, Chinese, saved words, pagination, search during stalled network ({elapsed * 1000:.0f} ms).')
        finally:
            release.set()
            app.close()
