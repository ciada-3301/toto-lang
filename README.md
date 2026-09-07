# toto

A Python library for the Toto language — a critically endangered Sino-Tibetan language spoken in Totopara, Alipurduar, West Bengal, India.

Provides LLM-powered English-to-Toto translation with morphemic analysis, Unicode 14.0 script transliteration, an offline dictionary of ~7,000 verified entries, and a local web interface.

---

## Installation

```bash
pip install -e .
```

Or install dependencies separately:

```bash
pip install openai>=1.0 flask>=3.0
```

---

## Setup

The library needs an API key for the translation model. By default it uses [Ollama Cloud](https://ollama.com) with the `nemotron-3-super:cloud` model.

### 1. Create a `.env` file

Create a `.env` file **in your project root** (the directory where your script runs):

```
TOTO_API_KEY=your-api-key-here
```

The library also recognises these variable names (checked in order):

| Variable | Source |
|---|---|
| `TOTO_API_KEY` | Recommended |
| `TOTO_API` | Alternative |
| `OLLAMA_API_KEY` | Ollama Cloud |
| `HF_TOKEN` | HuggingFace |

### 2. Or configure programmatically

```python
import toto

toto.configure(api_key="your-key-here")
# Or load from a specific .env file:
toto.configure(env_path="/path/to/your/.env")
# Or override the endpoint entirely:
toto.configure(
    api_key="your-key",
    base_url="https://your-endpoint/v1",
    model="your-model-name"
)
```

### Optional: Custom endpoint

Set these in your `.env` to override defaults:

```
TOTO_BASE_URL=https://your-endpoint/v1
TOTO_MODEL=your-model-name
```

---

## Usage

### Translate from English or Bengali

The library supports both English and Bengali inputs. When Bengali is provided, it is automatically bridged to English via Google Translate and then translated into Toto by the linguistic agent:

```python
from toto import totoagent

# 1. Translate from English (returns both Toto and Bengali)
result = totoagent.translate("They should not stay outside", lang="en")

print(result)            # Romanized Toto: akuko barota gaow-dinga
print(result.script)     # Native Toto script (Unicode 14.0): 𞊭𞊔𞊥𞊔𞊪 𞊑𞊭𞊟𞊪𞊒𞊭 𞊕𞊭𞊪𞊜-𞊓𞊡𞊘𞊭
print(result.roman)      # akuko barota gaow-dinga
print(result.bengali)    # তাদের বাইরে থাকা উচিত নয়
print(result.gloss)      # Interlinear morpheme breakdown
print(result.notes)      # Grammatical synthesis explanation
print(result.reasoning)  # Full chain-of-thought reasoning trace

# 2. Translate from Bengali directly
bn_result = totoagent.translate("তারা বাইরে থাকা উচিত নয়", lang="bn")
print(bn_result.english) # They should not be outside
print(bn_result.script)  # 𞊭𞊔𞊥𞊔𞊪 𞊑𞊭𞊟𞊪𞊒𞊭 𞊕𞊭𞊪𞊜-𞊓𞊡𞊘𞊭
print(bn_result.roman)   # akuko barota gaow-dinga
```

### Serialise results

```python
result.to_dict()   # -> dict with 'english', 'bengali', 'roman', 'script', 'gloss', 'notes', 'reasoning'
result.to_json()   # -> JSON string
```

### Unicode transliteration (no API key needed)

```python
from toto import roman_to_toto, toto_to_roman

script = roman_to_toto("ka ti da-ro")
print(script)  # 𞊔𞊭 𞊒𞊡 𞊓𞊭-𞊟𞊪

roman = toto_to_roman(script)
print(roman)   # ka ti da-ro
```

### Offline dictionary lookup (no API key needed)

```python
from toto import get_lexicon

lex = get_lexicon()
results = lex.lookup("water")
for entry in results:
    print(f"{entry['english']} -> {entry['toto']}")
```

### Web interface

```python
from toto import webagent

webagent.run(port=5001)
# Open http://127.0.0.1:5001 in your browser
```

### Access bundled documentation

```python
import toto

docs = toto.get_documents()
for path in docs:
    print(path)
# -> .../Guha_et_al_2025_Morphological_Analysis_Toto.pdf
# -> .../Toby_Anderson_2017_Toto_English_Dictionary.pdf
```

### Create a dedicated agent instance

```python
from toto import TotoAgent

agent = TotoAgent(
    api_key="your-key",
    base_url="https://ollama.com/v1",
    model="nemotron-3-super:cloud"
)
result = agent.translate("Good morning")
```

---

## Error Handling

The library raises descriptive exceptions with actionable guidance:

```python
from toto import totoagent, MissingApiKeyError, ModelConnectionError, TranslationError

try:
    result = totoagent.translate("Hello")
except MissingApiKeyError:
    print("No API key found — check your .env file")
except ModelConnectionError:
    print("Cannot reach the translation API")
except TranslationError as e:
    print(f"Translation failed: {e}")
    print(f"Raw content: {e.raw_content}")
```

---

## Project Structure

```
toto-python/
├── pyproject.toml
├── setup.py
├── README.md
├── requirements.txt
├── toto/
│   ├── __init__.py          # Public API
│   ├── config.py            # .env auto-discovery
│   ├── exceptions.py        # Exception classes
│   ├── agent.py             # TotoAgent + TranslationResult
│   ├── unicode.py           # Script transliteration
│   ├── lexicon.py           # Offline dictionary
│   ├── web.py               # Web interface
│   ├── resources/
│   │   ├── data/            # Bundled JSONL lexicon
│   │   ├── grammar/         # Grammar specification
│   │   └── docs/            # Research PDFs
│   ├── templates/           # HTML templates
│   └── static/              # CSS & JS
└── tests/
    └── test_library.py
```

---

## References

- Toby Anderson, *Toto–English Dictionary*, Totopara Community, 2017.
- Guha et al., *Morphological Analysis of Toto*, Adamas University, 2025.
- Unicode 14.0 Toto Block (U+1E290 – U+1E2BF), September 2021.
- Script created by Padma Shri Dhaniram Toto, 2015.

---

## License

MIT
