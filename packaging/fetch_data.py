"""Download pinned public dictionary data, verifying SHA-256 before use."""
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parent.parent


def sha256(path):
    with path.open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()


def fetch():
    destination = ROOT / '.build-tools' / 'sources'
    destination.mkdir(parents=True, exist_ok=True)
    for source in json.loads((ROOT / 'data/sources.json').read_text(encoding='utf-8')):
        target = destination / source['file']
        if target.exists() and sha256(target) == source['sha256']:
            print('Verified:', source['name'])
            continue
        temporary = target.with_suffix(target.suffix + '.tmp')
        try:
            request = urllib.request.Request(source['url'], headers={'User-Agent': 'Wordroom-build/1.1'})
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open('wb') as output:
                shutil.copyfileobj(response, output)
            if sha256(temporary) != source['sha256']:
                raise RuntimeError(f"Checksum mismatch for {source['name']}; source was not accepted")
            temporary.replace(target)
            print('Downloaded and verified:', source['name'])
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    fetch()
