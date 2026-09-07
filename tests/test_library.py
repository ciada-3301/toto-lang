"""
Tests for the toto library.

Run with:  python -m pytest tests/ -v
Or:        python tests/test_library.py
"""

import os
import sys
import json
import unittest

# Ensure the package is importable from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestImports(unittest.TestCase):
    """Verify all public exports are importable."""

    def test_import_package(self):
        import toto
        self.assertTrue(hasattr(toto, "__version__"))

    def test_import_totoagent(self):
        from toto import totoagent
        self.assertIsNotNone(totoagent)

    def test_import_webagent(self):
        from toto import webagent
        self.assertIsNotNone(webagent)

    def test_import_unicode_functions(self):
        from toto import roman_to_toto, toto_to_roman
        self.assertTrue(callable(roman_to_toto))
        self.assertTrue(callable(toto_to_roman))

    def test_import_configure(self):
        from toto import configure
        self.assertTrue(callable(configure))

    def test_import_exceptions(self):
        from toto import MissingApiKeyError, ModelConnectionError, TranslationError, TotoError
        self.assertTrue(issubclass(MissingApiKeyError, TotoError))
        self.assertTrue(issubclass(ModelConnectionError, TotoError))
        self.assertTrue(issubclass(TranslationError, TotoError))

    def test_import_classes(self):
        from toto import TotoAgent, TranslationResult, Lexicon
        self.assertIsNotNone(TotoAgent)
        self.assertIsNotNone(TranslationResult)
        self.assertIsNotNone(Lexicon)


class TestUnicode(unittest.TestCase):
    """Test the Toto Unicode 14.0 transliteration module."""

    def test_roman_to_toto_basic(self):
        from toto import roman_to_toto
        result = roman_to_toto("ka")
        self.assertEqual(result, "\U0001E294\U0001E2AD")

    def test_roman_to_toto_phrase(self):
        from toto import roman_to_toto
        result = roman_to_toto("ka ti da-ro")
        self.assertIn("\U0001E294", result)  # k
        self.assertIn("\U0001E2AD", result)  # a
        self.assertIn("-", result)           # hyphen preserved

    def test_roman_to_toto_empty(self):
        from toto import roman_to_toto
        self.assertEqual(roman_to_toto(""), "")
        self.assertEqual(roman_to_toto(None), "")

    def test_toto_to_roman_basic(self):
        from toto import toto_to_roman
        # k + a
        result = toto_to_roman("\U0001E294\U0001E2AD")
        self.assertEqual(result, "ka")

    def test_roundtrip(self):
        from toto import roman_to_toto, toto_to_roman
        original = "nobepa"
        script = roman_to_toto(original)
        back = toto_to_roman(script)
        self.assertEqual(back, original)

    def test_digraphs(self):
        from toto import roman_to_toto
        # "ng" should map to single code point U+1E298
        result = roman_to_toto("ng")
        self.assertEqual(result, "\U0001E298")

    def test_punctuation_preserved(self):
        from toto import roman_to_toto
        result = roman_to_toto("ka? ti!")
        self.assertIn("?", result)
        self.assertIn("!", result)

    def test_spaces_preserved(self):
        from toto import roman_to_toto
        result = roman_to_toto("ka ti")
        self.assertIn(" ", result)


class TestTranslationResult(unittest.TestCase):
    """Test TranslationResult dataclass."""

    def test_str_returns_roman(self):
        from toto import TranslationResult
        r = TranslationResult(roman="akuko barota", script="test", gloss="g", notes="n")
        self.assertEqual(str(r), "akuko barota")

    def test_bool_true(self):
        from toto import TranslationResult
        r = TranslationResult(roman="test")
        self.assertTrue(r)

    def test_bool_false(self):
        from toto import TranslationResult
        r = TranslationResult()
        self.assertFalse(r)

    def test_to_dict(self):
        from toto import TranslationResult
        r = TranslationResult(
            english="I drink water",
            bengali="আমি জল খাই",
            roman="ka",
            script="s",
            gloss="g",
            notes="n",
            reasoning="r",
        )
        d = r.to_dict()
        self.assertEqual(d["english"], "I drink water")
        self.assertEqual(d["bengali"], "আমি জল খাই")
        self.assertEqual(d["roman"], "ka")
        self.assertEqual(d["script"], "s")
        self.assertEqual(d["gloss"], "g")
        self.assertEqual(d["notes"], "n")
        self.assertEqual(d["reasoning"], "r")

    def test_to_json(self):
        from toto import TranslationResult
        r = TranslationResult(english="water", bengali="জল", roman="ka", script="s", gloss="g", notes="n")
        j = r.to_json()
        parsed = json.loads(j)
        self.assertEqual(parsed["english"], "water")
        self.assertEqual(parsed["bengali"], "জল")
        self.assertEqual(parsed["roman"], "ka")


class TestLexicon(unittest.TestCase):
    """Test the offline dictionary."""

    def test_lexicon_loads(self):
        from toto import get_lexicon
        lex = get_lexicon()
        self.assertGreater(len(lex), 0)

    def test_lookup_returns_results(self):
        from toto import get_lexicon
        lex = get_lexicon()
        results = lex.lookup("water")
        self.assertIsInstance(results, list)
        # "water" should exist in the lexicon
        self.assertGreater(len(results), 0)

    def test_lookup_override(self):
        from toto import get_lexicon
        lex = get_lexicon()
        results = lex.lookup("good morning")
        self.assertTrue(any("Toisho" in r["toto"] for r in results))

    def test_vocab_prompt(self):
        from toto import get_lexicon
        lex = get_lexicon()
        prompt = lex.build_vocab_prompt(max_entries=10)
        self.assertIn("->", prompt)


class TestExceptions(unittest.TestCase):
    """Test exception classes."""

    def test_missing_api_key_message(self):
        from toto import MissingApiKeyError
        e = MissingApiKeyError()
        self.assertIn(".env", str(e))
        self.assertIn("TOTO_API_KEY", str(e))

    def test_model_connection_error(self):
        from toto import ModelConnectionError
        e = ModelConnectionError("https://example.com/v1")
        self.assertIn("example.com", str(e))

    def test_translation_error(self):
        from toto import TranslationError
        e = TranslationError(reason="test failure", raw_content="raw")
        self.assertIn("test failure", str(e))
        self.assertEqual(e.raw_content, "raw")


class TestConfig(unittest.TestCase):
    """Test configuration module."""

    def test_configure_api_key(self):
        from toto import configure
        from toto.config import get_api_key
        configure(api_key="test-key-12345")
        self.assertEqual(get_api_key(), "test-key-12345")

    def test_configure_api_key_var(self):
        from toto import configure
        from toto.config import get_api_key
        import os
        os.environ["CUSTOM_TRANSLATE_KEY"] = "custom-secret-999"
        configure(api_key_var="CUSTOM_TRANSLATE_KEY")
        self.assertEqual(get_api_key(), "custom-secret-999")

    def test_case_insensitive_toto_api(self):
        from toto import configure
        from toto.config import get_api_key, _config
        import os
        _config["api_key"] = ""
        os.environ["toto_api"] = "hf_token_sample_123"
        configure(api_key_var=None)
        self.assertEqual(get_api_key(), "hf_token_sample_123")

    def test_configure_base_url(self):
        from toto import configure
        from toto.config import get_base_url
        configure(base_url="https://custom.endpoint/v1")
        self.assertEqual(get_base_url(), "https://custom.endpoint/v1")

    def test_configure_model(self):
        from toto import configure
        from toto.config import get_model
        configure(model="custom-model")
        self.assertEqual(get_model(), "custom-model")


class TestGetDocuments(unittest.TestCase):
    """Test bundled document access."""

    def test_returns_pdf_paths(self):
        import toto
        docs = toto.get_documents()
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        for path in docs:
            self.assertTrue(path.endswith(".pdf"))


class TestMissingApiKeyRaisesOnTranslate(unittest.TestCase):
    """Verify that translation fails gracefully without an API key."""

    def test_no_key_raises(self):
        from toto import TotoAgent, MissingApiKeyError
        # Clear any configured key
        from toto.config import _config
        old_key = _config["api_key"]
        _config["api_key"] = ""
        try:
            agent = TotoAgent(api_key="")
            with self.assertRaises(MissingApiKeyError):
                agent.translate("test")
        finally:
            _config["api_key"] = old_key


class TestTranslator(unittest.TestCase):
    """Test Google Translate bridge between Bengali and English."""

    def test_bengali_to_english(self):
        from toto import bengali_to_english
        res = bengali_to_english("জল")
        self.assertIsInstance(res, str)
        self.assertIn("water", res.lower())

    def test_english_to_bengali(self):
        from toto import english_to_bengali
        res = english_to_bengali("water")
        self.assertIsInstance(res, str)
        self.assertTrue(len(res) > 0)


class TestWebAgent(unittest.TestCase):
    """Test webagent test client."""

    def test_web_index(self):
        import toto
        client = toto.webagent.test_client()
        res = client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Translation Agent", res.data)

    def test_web_translate_empty_input(self):
        import toto
        client = toto.webagent.test_client()
        res = client.post("/api/translate", json={"text": ""})
        self.assertEqual(res.status_code, 400)


if __name__ == "__main__":
    unittest.main()
