"""
Toto Library — Offline Dictionary & Search.

Loads the bundled toto_english_2col.jsonl lexicon for:
  - Full vocabulary loading for agent system prompts.
  - Offline word/phrase lookup without an API call.
"""

import re
import json
from pathlib import Path

from .config import DATA_JSONL


def _clean_toto(raw: str) -> str:
    """Strip Bengali script artifacts and normalise whitespace."""
    cleaned = re.sub(r"[\u0980-\u09ff]", "", raw).strip()
    cleaned = re.sub(r"\s+", " ", cleaned).strip(",;:()")
    return cleaned


# Cultural / pragmatic overrides that take priority over raw lexicon data
OVERRIDES = {
    "good morning": "Toisho hinwa? / Kani tirihe?",
    "hello": "Kani tirihe? / Kiba na?",
    "how are you": "Nane kiba? / Kani tirihe?",
    "what": "ha'di",
    "why": "ha'di",
    "who": "hata",
    "where": "toisho / hete",
    "when": "ha-tempu",
    "how": "hado",
    "do": "jowa",
    "make": "banai / leina",
    "stay": "gaow / tung",
    "outside": "barota",
    "inside": "gadu",
    "brother": "nobepa (elder) / mokoidangbepa (younger)",
    "elder brother": "nobepa",
    "younger brother": "mokoidangbepa",
    "sister": "nocima (elder) / mokoidangma (younger)",
    "elder sister": "nocima",
    "younger sister": "mokoidangma",
    "bright": "hahipajowa",
    "to worship": "jishang huiva",
    "to lend": "kiwa",
    "grater": "khoewa",
}


class Lexicon:
    """Offline Toto-English dictionary backed by the bundled JSONL file."""

    def __init__(self, jsonl_path: Path | str | None = None):
        self._path = Path(jsonl_path) if jsonl_path else DATA_JSONL
        self._entries: list[dict[str, str]] = []
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self._path.is_file():
            return
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                en = (obj.get("english") or "").strip()
                to = _clean_toto(obj.get("toto") or obj.get("toto_roman") or "")
                if en and to:
                    self._entries.append({"english": en, "toto": to})

    @property
    def entries(self) -> list[dict[str, str]]:
        self._load()
        return self._entries

    def __len__(self) -> int:
        return len(self.entries)

    def lookup(self, query: str) -> list[dict[str, str]]:
        """Search the lexicon for entries matching *query* (case-insensitive).

        Checks overrides first, then searches the JSONL data.

        Returns a list of ``{"english": ..., "toto": ...}`` dicts.
        """
        q = query.strip().lower()
        results: list[dict[str, str]] = []

        # Check overrides
        if q in OVERRIDES:
            results.append({"english": q, "toto": OVERRIDES[q]})

        # Search JSONL
        for entry in self.entries:
            if q in entry["english"].lower():
                results.append(entry)

        return results

    def build_vocab_prompt(self, max_entries: int = 1200) -> str:
        """Build a vocabulary block for use in an LLM system prompt.

        Override entries come first, followed by JSONL entries up to
        *max_entries* total.
        """
        lines = [f"{k} -> {v}" for k, v in OVERRIDES.items()]
        seen = set(OVERRIDES.keys())

        for entry in self.entries:
            en = entry["english"].lower()
            to = entry["toto"]
            if en in seen:
                continue
            if len(en) < 40 and "ha'di" not in to:
                seen.add(en)
                lines.append(f"{en} -> {to}")
            if len(lines) >= max_entries:
                break

        return "\n".join(lines)


# Module-level convenience instance
_default_lexicon: Lexicon | None = None


def get_lexicon() -> Lexicon:
    """Return the default Lexicon singleton."""
    global _default_lexicon
    if _default_lexicon is None:
        _default_lexicon = Lexicon()
    return _default_lexicon
