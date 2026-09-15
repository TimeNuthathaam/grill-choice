#!/usr/bin/env python3
"""Check the documented workflow without installing html-choice or using port 8767."""
import contextlib
import io
import json
import re
import runpy
import shutil
import tempfile
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request, urlopen


def main():
    skill = Path(__file__).resolve().parents[1]
    source = re.search(r"python3 - <<'PY'\n(.*?)\nPY", (skill / 'SKILL.md').read_text(), re.S).group(1)
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        shutil.copytree(skill, home / '.codex/skills/grill-choice', ignore=shutil.ignore_patterns('.git', '__pycache__'))
        pages = []
        with patch.object(Path, 'home', return_value=home), contextlib.redirect_stdout(io.StringIO()):
            for _ in range(2):
                page = {}
                exec(compile(source, 'SKILL.md example', 'exec'), page)
                pages.append(page)
        first, second = pages
        assert first['page_key'] != second['page_key']
        archive = first['archive']
        assert (archive / 'latest.html').read_text() == second['html']
        assert (archive / f"{first['page_key']}.html").read_text() == first['html']
        assert '__POINTS_JSON__' not in first['html']
        assert first['points'][0]['title'] in first['html']

        handler = runpy.run_path(str(skill / 'scripts/choice-server.py'))['Handler']
        with ThreadingHTTPServer(('127.0.0.1', 0), partial(handler, directory=str(archive))) as server:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f'http://127.0.0.1:{server.server_port}'
            state = {'responses': {'0': {'choice': 'comment', 'comment': 'ขอเริ่มเดือนหน้า'}}}
            try:
                with urlopen(base + '/' + first['page_key'] + '.html', timeout=5) as response:
                    assert response.read().decode() == first['html']
                with urlopen(base + '/', timeout=5) as response:
                    assert response.read().decode() == second['html']
                url = base + '/state?key=' + first['page_key']
                request = Request(url, data=json.dumps(state).encode(), headers={'Content-Type': 'application/json'})
                with urlopen(request, timeout=5) as response:
                    assert json.load(response)['ok']
                with urlopen(url, timeout=5) as response:
                    assert json.load(response) == state
                assert json.loads((archive / f"{first['page_key']}.state.json").read_text()) == state
                with urlopen(base + '/state?key=' + second['page_key'], timeout=5) as response:
                    assert json.load(response) == {'responses': {}}
            finally:
                server.shutdown()
                thread.join()
    print('PASS: standalone rendering, archived pages, saved comments, and separate page state')


if __name__ == '__main__':
    main()
