"""
Toto Library — Agentic Translation Engine.

Houses TotoAgent (the LLM-backed translator) and TranslationResult
(the structured output with .roman, .script, .gloss, .notes, .reasoning).
"""

import json
import re
from dataclasses import dataclass, field

from .config import get_api_key, get_base_url, get_model
from .exceptions import MissingApiKeyError, ModelConnectionError, TranslationError
from .unicode import roman_to_toto
from .lexicon import get_lexicon
from .translator import bengali_to_english, english_to_bengali


# -------------------------------------------------------------------------
# Grammar specification (embedded for zero-file-dependency operation)
# -------------------------------------------------------------------------

TOTO_GRAMMAR_SPEC = """
# TOTO (TIBETO-BURMAN) GRAMMAR AND MORPHOLOGY SPECIFICATION

## 1. Word Order & Syntactic Typology
- Default Word Order: SOV (Subject - Object - Verb).
- Temporal & Locative Adverbs typically precede the Object: [Subject] [Time] [Location-LOC] [Object-ACC] [Verb-ASPECT-TENSE].
- Adjectives typically precede or follow the head noun with agreement.
- Postpositional language (uses case suffixes rather than prepositions).

## 2. Pronominal System
- 1SG ('I'): ka | Possessive ('my'): kung / kako | Objective ('me'): kahing / ka-hing
- 2SG ('you'): nati | Possessive ('your'): nako / natbihko | Objective ('you'): natihing
- 3SG ('he/she/it'): ako (he) / aku (she) / akwa | Possessive ('his/her'): akoko / akuko | Objective ('him/her'): akohing / akuhing
- 1PL ('we'): kiko / kibi | Possessive ('our'): kibiko / yangko | Objective ('us'): kikohing
- 3PL ('they'): akuko / abih | Possessive ('their'): akukoko / abihko | Objective ('them'): akukohing

## 3. Case System (Nominal Suffixes)
- Nominative: -null (unmarked).
- Accusative (Direct Object): -he / -hing / -hi (often omitted in inanimate direct objects).
- Dative (Indirect Object / 'to'): -hing / -ta (e.g. ram kahing book pica-na = Ram gave a book to me).
- Locative ('at', 'in', 'to'): -ta / -sho (e.g. iskul-ta = at/to school, sha-ta = at home, bazar-ta = to market).
- Instrumental ('with', 'by'): -sho / -sha (e.g. kolom-sho = with pen, teipum-sha = on foot/by walking).
- Ablative ('from'): -sho (e.g. shinge-sho = from tree, dal-sho = from branch, toi-sho = from a height).
- Genitive ('of', possessive): -ko / -koh (e.g. Sita-ko bajero = Sita's friend).
- Definite Marker: -ha (e.g. iga-ha = the book, minki-ha = the cat).
- Plural Marker: -bi (e.g. ceng-bi = children, pika-bi = cows, tebil-bi = tables).

## 4. Tense and Aspect Morphemes
- Present Tense: -na or -mi (e.g. ha-na / ha-mi = goes/walks, coi-na = buys, ca-na = eats).
- Past Tense: -mi or -na (e.g. ha-mi = went, pica-mi = gave, ca-mi = ate).
- Future Tense: -ro (e.g. ha-ro = will go, ca-ro = will eat, kelai-ro = will play).
- Progressive / Continuous: -dang-na / -ding-na (Present) | -dang-mi (Past).
  Example: ka neha hapung-ko ama ca-ding-na = 'I am now eating breakfast'.
- Perfect Aspect: -pate-na (Present Perfect) | -pate-mi (Past Perfect) | -pu-ro (Future Perfect).
  Example: ka iga parai-pate-na = 'I have read the book'.

## 5. Mood and Auxiliaries
- Imperative: Bare verb stem or suffix -ko (e.g. kelai = 'play!', ti da = 'drink water!', ama ca = 'eat!').
- Negative Auxiliary ('should not'): -dinga (e.g. ako nong-dinga = 'he should not see').
- Strict Prohibition ('must not'): -majo (e.g. ka coi-majo = 'I must not buy').
- Copula / Existence: mi / ha (e.g. ka kiba mi = 'I am fine', kako ming X mi = 'My name is X').
- Habitual / Subjunctive: -ko (e.g. ka phutbal kelai-na ico tim-ta kelai-ko = 'If I had played football, I would join a team').

## 7. Critical Cultural & Pragmatic Overrides (MANDATORY)
- "good morning": MUST be translated situationally as "Toisho hinwa?" ("Where are you going?") or "Kani tirihe?" ("Are you well?"). DO NOT translate as "ha'di", because "ha'di" means "what/why" in Toto!
- "hello" / "greetings": "Kani tirihe?" / "Kiba na?" (DO NOT use "gadu pira", which is an idiom meaning "come inside and sit").
- "how are you": "Nane kiba?" / "Kani tirihe?"
- "i am fine" / "i am well": "Ka kiba mi" / "Ka tiri mi"
- "brother": "nobepa" (elder brother) / "mokoidangbepa" (younger brother).
- "sister": "nocima" (elder sister) / "mokoidangma" (younger sister).
- "important": "mahatvapurna" or "liba".
- "to worship": "jishang huiva".
- "to lend": "kiwa".
- "grater": "khoewa".
- "bright": "hahipajowa".
"""


def _build_system_prompt() -> str:
    """Assemble the full system prompt with grammar + vocabulary."""
    lexicon = get_lexicon()
    vocab_text = lexicon.build_vocab_prompt(1200)

    return f"""You are the Master Linguist & Translator for the Toto language (critically endangered Sino-Tibetan language of Totopara, West Bengal, India).

You translate English text into authentic, grammatically correct Romanized Toto.
You operate with access to the complete codified grammar and vocabulary of the language.

{TOTO_GRAMMAR_SPEC}

# CORE LEXICON (ENGLISH -> ROMANIZED TOTO)
The following verified lexicon entries are ground truth. You MUST use these exact lexical roots:
{vocab_text}

# TRANSLATION INSTRUCTIONS:
1. Analyze the English input's grammatical roles (Subject, Tense/Aspect, Negation, Object, Location, Direct/Indirect).
2. Retrieve the exact Toto roots from the Core Lexicon. NEVER invent fake words or guess arbitrary English phonemes.
3. Apply Toto agglutinative morphology (-bi for plural, -ta for location, -ro for future, -dang-na for progressive, -dinga for should not).
4. Assemble into SOV order.
5. After your internal linguistic reasoning, you MUST close the thinking block with </think> and output strictly a valid JSON object:
```json
{{
  "toto": "final Romanized Toto translation string",
  "literal_gloss": "word-by-word morpheme breakdown",
  "notes": "brief explanation of grammatical and morphological choices"
}}
```
"""


# -------------------------------------------------------------------------
# JSON extractor — bulletproof, searches both content and reasoning
# -------------------------------------------------------------------------

def _extract_json_payload(content: str, reasoning: str = "") -> dict:
    """Extract the translation JSON from model output.

    Searches both message.content and message.reasoning (for reasoning
    models like Nemotron that may embed results in the thinking trace).
    """
    for text in [content, reasoning]:
        if not text:
            continue

        # 1. Direct JSON parse
        try:
            res = json.loads(text.strip())
            if isinstance(res, dict) and res.get("toto"):
                return res
        except Exception:
            pass

        # 2. Find JSON blocks containing "toto"
        matches = list(re.finditer(r"\{[\s\S]*?\}", text))
        for m in reversed(matches):
            chunk = m.group(0)
            if '"toto"' in chunk:
                try:
                    res = json.loads(chunk)
                    if isinstance(res, dict) and res.get("toto"):
                        val = res.get("toto", "").strip()
                        if val and not val.startswith("We need") and not val.startswith("In SOV"):
                            return res
                except Exception:
                    pass

        # 3. Key-value regex extraction as fallback
        toto_match = re.search(r'"toto"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
        if toto_match:
            val = toto_match.group(1).replace('\\"', '"').replace("\\n", " ").strip()
            if val and not val.startswith("We need"):
                gloss_match = re.search(r'"literal_gloss"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
                notes_match = re.search(r'"notes"\s*:\s*"([^"\\]*(?:\\.[^"\\]*)*)"', text)
                return {
                    "toto": val,
                    "literal_gloss": gloss_match.group(1) if gloss_match else "",
                    "notes": notes_match.group(1) if notes_match else "",
                }

    return {}


# -------------------------------------------------------------------------
# TranslationResult
# -------------------------------------------------------------------------

@dataclass
class TranslationResult:
    """Structured result from a Toto translation.

    Attributes
    ----------
    english : str
        English translation/source text.
    bengali : str
        Bengali translation/source text.
    roman : str
        Romanized Toto translation.
    script : str
        Native Toto script (Unicode 14.0).
    gloss : str
        Interlinear morpheme breakdown.
    notes : str
        Grammatical synthesis notes.
    reasoning : str
        Model chain-of-thought reasoning trace.
    """

    english: str = ""
    bengali: str = ""
    roman: str = ""
    script: str = ""
    gloss: str = ""
    notes: str = ""
    reasoning: str = ""

    def __str__(self) -> str:
        """Return the Romanized translation by default."""
        return self.roman

    def __repr__(self) -> str:
        return (
            f"TranslationResult(roman={self.roman!r}, script={self.script!r}, "
            f"english={self.english!r}, bengali={self.bengali!r})"
        )

    def __bool__(self) -> bool:
        return bool(self.roman)

    def to_dict(self) -> dict:
        """Serialise to a plain dictionary."""
        return {
            "english": self.english,
            "bengali": self.bengali,
            "roman": self.roman,
            "script": self.script,
            "gloss": self.gloss,
            "notes": self.notes,
            "reasoning": self.reasoning,
        }

    def to_json(self, **kwargs) -> str:
        """Serialise to a JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False, **kwargs)


# -------------------------------------------------------------------------
# TotoAgent
# -------------------------------------------------------------------------

class TotoAgent:
    """LLM-backed English-to-Toto translation agent.

    Uses an OpenAI-compatible API endpoint with in-context learning
    from the full Toto grammar specification and curated lexicon.

    Examples
    --------
    >>> from toto import totoagent
    >>> result = totoagent.translate("I will drink water")
    >>> print(result)          # romanized
    >>> print(result.script)   # native script
    >>> print(result.gloss)    # morpheme breakdown
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self._api_key = api_key or get_api_key()
        self._base_url = base_url or get_base_url()
        self._model = model or get_model()
        self._client = None
        self._system_prompt: str | None = None

    def _get_client(self):
        """Lazy-initialise the OpenAI client."""
        if self._client is not None:
            return self._client

        if not self._api_key:
            raise MissingApiKeyError()

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The 'openai' package is required for translation. "
                "Install it with:  pip install openai>=1.0"
            ) from exc

        self._client = OpenAI(
            base_url=self._base_url,
            api_key=self._api_key,
        )
        return self._client

    def _get_system_prompt(self) -> str:
        if self._system_prompt is None:
            self._system_prompt = _build_system_prompt()
        return self._system_prompt

    def translate(self, text: str, lang: str = "en") -> TranslationResult:
        """Translate text (English or Bengali) into authentic Toto.

        Parameters
        ----------
        text : str
            The input sentence or phrase in English or Bengali.
        lang : str, optional
            Source language code: ``"en"`` (default) or ``"bn"`` (Bengali).

        Returns
        -------
        TranslationResult
            Structured result containing ``.english``, ``.bengali``, ``.roman``,
            ``.script``, ``.gloss``, ``.notes``, and ``.reasoning``.

        Raises
        ------
        MissingApiKeyError
            If no API key is configured.
        ModelConnectionError
            If the API endpoint is unreachable.
        TranslationError
            If the model response cannot be parsed.
        """
        if not text or not text.strip():
            return TranslationResult()

        clean_text = text.strip()
        lang_code = (lang or "en").strip().lower()

        # Resolve English and Bengali representations
        if lang_code in ("bn", "bengali", "bangla"):
            bengali_text = clean_text
            english_text = bengali_to_english(bengali_text)
        else:
            english_text = clean_text
            bengali_text = english_to_bengali(english_text)

        client = self._get_client()

        user_prompt = (
            f'Translate this English text into authentic Romanized Toto:\n'
            f'"{english_text}"\n\n'
            f'After your internal thinking, conclude with </think> and output strictly a valid JSON object with keys:\n'
            f'- "toto": (string)\n'
            f'- "literal_gloss": (string)\n'
            f'- "notes": (string)'
        )

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=8192,
                response_format={"type": "json_object"},
            )
        except Exception as exc:
            exc_str = str(exc).lower()
            if "connection" in exc_str or "timeout" in exc_str or "refused" in exc_str:
                raise ModelConnectionError(self._base_url, exc) from exc
            raise TranslationError(
                reason=f"API request failed: {exc}",
                raw_content="",
                raw_reasoning="",
            ) from exc

        choice = response.choices[0]
        content = (choice.message.content or "").strip()
        reasoning = getattr(choice.message, "reasoning", "") or ""

        payload = _extract_json_payload(content, reasoning)
        if not payload or not payload.get("toto"):
            raise TranslationError(
                reason="Could not extract translation from model response.",
                raw_content=content,
                raw_reasoning=reasoning[:500],
            )

        roman = payload["toto"]
        script = ""
        if not roman.startswith("["):
            try:
                script = roman_to_toto(roman)
            except Exception:
                script = roman

        return TranslationResult(
            english=english_text,
            bengali=bengali_text,
            roman=roman,
            script=script,
            gloss=payload.get("literal_gloss", ""),
            notes=payload.get("notes", ""),
            reasoning=reasoning.strip(),
        )


# -------------------------------------------------------------------------
# Module-level convenience instance (lazy)
# -------------------------------------------------------------------------

_default_agent: TotoAgent | None = None


def _get_default_agent() -> TotoAgent:
    global _default_agent
    if _default_agent is None:
        _default_agent = TotoAgent()
    return _default_agent
