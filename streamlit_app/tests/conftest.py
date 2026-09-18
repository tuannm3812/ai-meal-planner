"""Put streamlit_app/ on sys.path so tests import modules the way the app does.

Streamlit inserts the main script's directory at sys.path[0] at runtime, which is
why app.py says `from api import request_json`. Replicating that here means the
tests exercise the real import mechanism rather than a test-only one. Adding
streamlit_app/__init__.py instead would make the app's own sibling imports
resolve differently from how Streamlit resolves them.
"""

import sys
from pathlib import Path

STREAMLIT_APP_DIR = Path(__file__).resolve().parents[1]

if str(STREAMLIT_APP_DIR) not in sys.path:
    sys.path.insert(0, str(STREAMLIT_APP_DIR))
