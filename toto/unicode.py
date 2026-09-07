"""
Toto Script (Unicode 14.0, U+1E290 - U+1E2BF) Transliteration Module.

Developed by Padma Shri Dhaniram Toto (2015), encoded into Unicode 14.0 (Sept 2021).
Font support: Google Fonts 'Noto Serif Toto'.

Functions
---------
roman_to_toto(text) -> str
    Convert Romanized Toto to native Toto script.
toto_to_roman(text) -> str
    Convert native Toto script back to Romanized form.
"""

import re

# -------------------------------------------------------------------------
# Unicode Block (U+1E290 – U+1E2AE)
# -------------------------------------------------------------------------

TOTO_UNICODE = {
    # Consonants (17)
    "pa": "\U0001E290", "p": "\U0001E290",
    "ba": "\U0001E291", "b": "\U0001E291",
    "ta": "\U0001E292", "t": "\U0001E292",
    "da": "\U0001E293", "d": "\U0001E293",
    "ka": "\U0001E294", "k": "\U0001E294",
    "ga": "\U0001E295", "g": "\U0001E295",
    "ma": "\U0001E296", "m": "\U0001E296",
    "na": "\U0001E297", "n": "\U0001E297",
    "nga": "\U0001E298", "ng": "\U0001E298", "\u014b": "\U0001E298",
    "sa": "\U0001E299", "s": "\U0001E299",
    "cha": "\U0001E29A", "ch": "\U0001E29A", "c": "\U0001E29A",
    "ya": "\U0001E29B", "y": "\U0001E29B",
    "wa": "\U0001E29C", "w": "\U0001E29C",
    "ja": "\U0001E29D", "j": "\U0001E29D",
    "ha": "\U0001E29E", "h": "\U0001E29E",
    "ra": "\U0001E29F", "r": "\U0001E29F",
    "la": "\U0001E2A0", "l": "\U0001E2A0",

    # Plain Vowels (8)
    "i": "\U0001E2A1",
    "iu": "\U0001E2A3", "\u0289": "\U0001E2A3",
    "u": "\U0001E2A5",
    "e": "\U0001E2A6",
    "eo": "\U0001E2A8", "\u0259": "\U0001E2A8", "\u0254": "\U0001E2A8",
    "o": "\U0001E2AA",
    "ae": "\U0001E2AB", "\u025b": "\U0001E2AB",
    "a": "\U0001E2AD",

    # Breathy Vowels (5)
    "ih": "\U0001E2A2",
    "iuh": "\U0001E2A4",
    "eh": "\U0001E2A7",
    "eoh": "\U0001E2A9",
    "aeh": "\U0001E2AC",

    # Tone Sign (1)
    "rising_tone": "\U0001E2AE",
}

# Reverse map (Unicode code point -> Romanized string)
UNICODE_TO_ROMAN = {
    "\U0001E290": "p",
    "\U0001E291": "b",
    "\U0001E292": "t",
    "\U0001E293": "d",
    "\U0001E294": "k",
    "\U0001E295": "g",
    "\U0001E296": "m",
    "\U0001E297": "n",
    "\U0001E298": "ng",
    "\U0001E299": "s",
    "\U0001E29A": "c",
    "\U0001E29B": "y",
    "\U0001E29C": "w",
    "\U0001E29D": "j",
    "\U0001E29E": "h",
    "\U0001E29F": "r",
    "\U0001E2A0": "l",
    "\U0001E2A1": "i",
    "\U0001E2A2": "ih",
    "\U0001E2A3": "iu",
    "\U0001E2A4": "iuh",
    "\U0001E2A5": "u",
    "\U0001E2A6": "e",
    "\U0001E2A7": "eh",
    "\U0001E2A8": "eo",
    "\U0001E2A9": "eoh",
    "\U0001E2AA": "o",
    "\U0001E2AB": "ae",
    "\U0001E2AC": "aeh",
    "\U0001E2AD": "a",
    "\U0001E2AE": "\u00b4",
}

# Tokenization regex — longest digraphs first for greedy matching
ROMAN_TOKEN_PATTERN = re.compile(
    r"(iuh|eoh|aeh|ih|eh|nga|ng|cha|ch|ae|eo|iu|"
    r"pa|ba|ta|da|ka|ga|ma|na|sa|ya|wa|ja|ha|ra|la|"
    r"[pbtdkgmnscywjhrliueoaɛɔəŋʉ])",
    re.IGNORECASE,
)

# Internal greedy lookup table (lowercase keys, ordered by length)
_LOOKUP = {
    # 3-char
    "iuh": "\U0001E2A4", "eoh": "\U0001E2A9", "aeh": "\U0001E2AC",
    # 2-char
    "ih": "\U0001E2A2", "eh": "\U0001E2A7",
    "ng": "\U0001E298", "\u014b": "\U0001E298",
    "ch": "\U0001E29A",
    "ae": "\U0001E2AB", "\u025b": "\U0001E2AB",
    "eo": "\U0001E2A8", "\u0259": "\U0001E2A8", "\u0254": "\U0001E2A8",
    "iu": "\U0001E2A3", "\u0289": "\U0001E2A3",
    # 1-char consonants
    "p": "\U0001E290", "b": "\U0001E291", "t": "\U0001E292", "d": "\U0001E293",
    "k": "\U0001E294", "g": "\U0001E295", "m": "\U0001E296", "n": "\U0001E297",
    "s": "\U0001E299", "c": "\U0001E29A", "y": "\U0001E29B", "w": "\U0001E29C",
    "j": "\U0001E29D", "h": "\U0001E29E", "r": "\U0001E29F", "l": "\U0001E2A0",
    # 1-char vowels
    "i": "\U0001E2A1", "u": "\U0001E2A5", "e": "\U0001E2A6",
    "o": "\U0001E2AA", "a": "\U0001E2AD",
}


def roman_to_toto(roman_text: str) -> str:
    """Transliterate Romanized Toto to native Toto Script (Unicode 14.0).

    The Toto script is an alphabet — letters are written linearly
    left-to-right. This function uses greedy longest-match tokenisation
    to handle multi-character digraphs correctly.

    Parameters
    ----------
    roman_text : str
        Romanized Toto string (e.g. ``"ka ti da-ro"``).

    Returns
    -------
    str
        Native Toto script string (e.g. ``"𞊔𞊭 𞊒𞊡 𞊓𞊭-𞊟𞊪"``).
    """
    if not roman_text:
        return ""

    result = []
    i = 0
    length = len(roman_text)

    while i < length:
        # Check 3-letter
        if i + 3 <= length and roman_text[i:i + 3].lower() in _LOOKUP:
            result.append(_LOOKUP[roman_text[i:i + 3].lower()])
            i += 3
        # Check 2-letter
        elif i + 2 <= length and roman_text[i:i + 2].lower() in _LOOKUP:
            result.append(_LOOKUP[roman_text[i:i + 2].lower()])
            i += 2
        # Check 1-letter
        elif roman_text[i].lower() in _LOOKUP:
            result.append(_LOOKUP[roman_text[i].lower()])
            i += 1
        else:
            # Preserve punctuation, spaces, hyphens, digits
            result.append(roman_text[i])
            i += 1

    return "".join(result)


def toto_to_roman(toto_script_text: str) -> str:
    """Convert native Toto script back to Romanized form.

    Parameters
    ----------
    toto_script_text : str
        Native Toto script string.

    Returns
    -------
    str
        Romanized representation.
    """
    if not toto_script_text:
        return ""

    result = []
    for char in toto_script_text:
        if char in UNICODE_TO_ROMAN:
            result.append(UNICODE_TO_ROMAN[char])
        else:
            result.append(char)
    return "".join(result)
