"""Check LanGo's real Tk window without reading the user's saved words."""
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lango_app import App
from test_lango_ai import WORD, TRANSLATION


def wait(app, condition, seconds=3):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.update()
        if condition(): return
        time.sleep(.01)
    raise AssertionError('Window did not update')


with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'LOCALAPPDATA': folder}):
    app = App()
    try:
        app.update()
        assert app.search.get() == '' and app.current == '' and not app.saved
        with patch.dict('os.environ', {'DEEPSEEK_API_KEY': 'sk-' + 'a' * 32}):
            with patch('lango_app.lookup', side_effect=[WORD, TRANSLATION]) as service:
                app.search_now('light')
                wait(app, lambda: app.current == 'light')
                assert any('Visible electromagnetic radiation.' in w.cget('text')
                       for card in app.body.winfo_children() for w in card.winfo_children()
                       if hasattr(w, 'cget') and w.winfo_class() == 'Label')
                app.toggle_saved()
                assert 'light' in app.saved
                app.saved_list.selection_set(0)
                app.open_saved(None)
                assert app.current == 'light' and service.call_count == 1
                app.clear_search()
                assert app.search.get() == '' and app.current == '' and not app.body.winfo_children()
                app.search_now('我听得一头雾水。')
                wait(app, lambda: app.status.cget('text').startswith('DeepSeek · Context'))
                assert app.current == '' and '我听得一头雾水。' not in app.saved
                app.search.delete(0, 'end')
                app.on_search_changed()
                assert app.current == '' and 'cancelled' in app.status.cget('text').lower()
                assert service.call_count == 2
        print('UI passed: blank start, cached saved word, clear control, cancellation, Chinese-to-English, one provider.')
    finally:
        app.close()
