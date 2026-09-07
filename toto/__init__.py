"""
toto — A Python library for the Toto language.

Toto is a critically endangered Sino-Tibetan language spoken in
Totopara, Alipurduar, West Bengal, India. This library provides:

  - LLM-powered English-to-Toto translation with morphemic analysis
  - Toto Unicode 14.0 script transliteration
  - An offline dictionary of ~7,000 verified entries
  - A web interface for interactive translation

Quick Start
-----------
>>> from toto import totoagent
>>> result = totoagent.translate("I will drink water")
>>> print(result)          # romanized Toto
>>> print(result.script)   # native Toto script

>>> from toto import roman_to_toto, toto_to_roman
>>> roman_to_toto("ka ti da-ro")
'𞊔𞊭 𞊒𞊡 𞊓𞊭-𞊟𞊪'

>>> from toto import webagent
>>> webagent.run(port=5001)
"""

__version__ = "0.2.0"

# -- Unicode transliteration (no dependencies, always available) ----------
from .unicode import roman_to_toto, toto_to_roman

# -- Configuration --------------------------------------------------------
from .config import configure

# -- Exceptions -----------------------------------------------------------
from .exceptions import TotoError, MissingApiKeyError, ModelConnectionError, TranslationError

# -- Lexicon (offline dictionary) -----------------------------------------
from .lexicon import Lexicon, get_lexicon

# -- Translation bridge (Bengali <-> English) -----------------------------
from .translator import bengali_to_english, english_to_bengali, translate_google

# -- Translation agent (lazy singleton) -----------------------------------
from .agent import TotoAgent, TranslationResult


class _LazyAgent:
    """Proxy that defers TotoAgent creation until first use.

    This avoids triggering .env loading and API key checks at import time.
    """

    def __init__(self):
        self._agent = None

    def _ensure(self):
        if self._agent is None:
            self._agent = TotoAgent()

    def translate(self, text: str, lang: str = "en") -> TranslationResult:
        """Translate English text into Toto.

        See :meth:`TotoAgent.translate` for full documentation.
        """
        self._ensure()
        return self._agent.translate(text, lang=lang)

    def __repr__(self):
        return "totoagent (default TotoAgent instance)"


class _LazyWebAgent:
    """Proxy that defers WebAgent creation until first use."""

    def __init__(self):
        self._web = None

    def _ensure(self):
        if self._web is None:
            from .web import WebAgent
            self._web = WebAgent()

    def run(self, host: str = "127.0.0.1", port: int = 5001, debug: bool = False):
        """Start the Toto web translation interface.

        See :meth:`WebAgent.run` for full documentation.
        """
        self._ensure()
        self._web.run(host=host, port=port, debug=debug)

    def get_app(self):
        """Return the Flask app (for WSGI deployment)."""
        self._ensure()
        return self._web.get_app()

    def test_client(self):
        """Return a Flask test client."""
        self._ensure()
        return self._web.test_client()

    def __repr__(self):
        return "webagent (default WebAgent instance)"


# Module-level convenience singletons
totoagent = _LazyAgent()
webagent = _LazyWebAgent()


def get_documents() -> list[str]:
    """Return file paths to the bundled linguistic documentation PDFs."""
    from .config import DOCS_DIR
    if not DOCS_DIR.is_dir():
        return []
    return sorted(str(p) for p in DOCS_DIR.glob("*.pdf"))


__all__ = [
    # Core API
    "totoagent",
    "webagent",
    "configure",
    "roman_to_toto",
    "toto_to_roman",
    "bengali_to_english",
    "english_to_bengali",
    "translate_google",
    # Classes
    "TotoAgent",
    "TranslationResult",
    "Lexicon",
    "get_lexicon",
    "get_documents",
    # Exceptions
    "TotoError",
    "MissingApiKeyError",
    "ModelConnectionError",
    "TranslationError",
    # Metadata
    "__version__",
]
