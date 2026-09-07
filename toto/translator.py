"""
Toto Library — Google Translate Bridge for Bengali & English.

Enables English <-> Bengali translation with zero required API keys using
the standard Google Translate endpoint, with deep-translator as fallback.
"""

import json
import urllib.parse
import urllib.request
import logging

logger = logging.getLogger(__name__)


def translate_google(text: str, source: str = "auto", target: str = "en") -> str:
    """Translate text between languages using Google Translate.

    Parameters
    ----------
    text : str
        The input text to translate.
    source : str
        Source language ISO-639 code (e.g. 'en', 'bn', or 'auto').
    target : str
        Target language ISO-639 code (e.g. 'en', 'bn').

    Returns
    -------
    str
        The translated string.
    """
    if not text or not text.strip():
        return ""

    text = text.strip()

    # Primary method: Google GTX single-query endpoint (zero extra dependencies)
    try:
        encoded_query = urllib.parse.quote(text)
        url = (
            f"https://translate.googleapis.com/translate_a/single?"
            f"client=gtx&sl={source}&tl={target}&dt=t&q={encoded_query}"
        )
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            if payload and isinstance(payload, list) and len(payload) > 0:
                translated_chunks = [
                    item[0] for item in payload[0] if item and isinstance(item, list) and item[0]
                ]
                result = "".join(translated_chunks).strip()
                if result:
                    return result
    except Exception as exc:
        logger.debug("Google GTX endpoint failed: %s. Trying fallback.", exc)

    # Secondary fallback: deep-translator (if installed)
    try:
        from deep_translator import GoogleTranslator

        src = "auto" if source == "auto" else source
        return GoogleTranslator(source=src, target=target).translate(text)
    except Exception as exc:
        logger.debug("deep-translator fallback failed: %s", exc)

    # If all translation attempts fail, return original text as safe fallback
    return text


def bengali_to_english(text: str) -> str:
    """Translate Bengali text into English."""
    return translate_google(text, source="bn", target="en")


def english_to_bengali(text: str) -> str:
    """Translate English text into Bengali."""
    return translate_google(text, source="en", target="bn")
