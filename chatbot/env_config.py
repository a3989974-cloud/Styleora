import os
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent.parent / '.env'
_loaded = False


def load_env():
    global _loaded
    if _loaded:
        return
    _loaded = True
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_env(key, default=''):
    load_env()
    return os.environ.get(key, default)
