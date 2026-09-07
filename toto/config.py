"""
Toto Library — Configuration & Environment Loader.

Discovery order for API keys:
  1. TOTO_API_KEY  or  TOTO_API
  2. OLLAMA_API_KEY
  3. HF_TOKEN

The .env file is auto-discovered by walking upward from os.getcwd().
Users can override any setting via toto.configure(...).
"""

import os
import sys
import inspect
from pathlib import Path

# ---------------------------------------------------------------------------
# Internal state (mutable via configure())
# ---------------------------------------------------------------------------

_config = {
    "api_key": "",
    "base_url": "https://ollama.com/v1",
    "model": "nemotron-3-super:cloud",
    "_env_loaded": False,
}

# ---------------------------------------------------------------------------
# .env parser (zero dependencies)
# ---------------------------------------------------------------------------

def _parse_env_file(filepath: Path) -> dict[str, str]:
    """Read a .env file and return key-value pairs.

    Handles inline comments and quoted values.
    Does NOT overwrite existing os.environ entries.
    """
    pairs: dict[str, str] = {}
    if not filepath.is_file():
        return pairs

    with open(filepath, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            # Strip inline comments (but not inside quotes)
            if "#" in val:
                val = val.split("#", 1)[0]
            val = val.strip().strip("'\"")
            if key:
                pairs[key] = val
    return pairs


def _discover_env_file() -> Path | None:
    """Find a .env file by checking script directories, caller frames, and cwd."""
    search_roots: list[Path] = []

    # 1. Directory of the running script (sys.argv[0] and __main__)
    if sys.argv and sys.argv[0]:
        try:
            arg_p = Path(sys.argv[0]).resolve()
            search_roots.append(arg_p.parent if arg_p.is_file() else arg_p)
        except Exception:
            pass

    try:
        import __main__
        if hasattr(__main__, "__file__") and __main__.__file__:
            main_p = Path(__main__.__file__).resolve()
            search_roots.append(main_p.parent)
    except Exception:
        pass

    # 2. Caller frames from inspect.stack
    try:
        for frame_info in inspect.stack():
            fn = frame_info.filename
            if fn and not fn.startswith("<") and "site-packages" not in fn and "toto" not in fn:
                p = Path(fn).resolve()
                if p.is_file():
                    search_roots.append(p.parent)
    except Exception:
        pass

    # 3. Current working directory
    try:
        search_roots.append(Path(os.getcwd()).resolve())
    except Exception:
        pass

    # Deduplicate while preserving priority order
    seen = set()
    unique_roots = []
    for root in search_roots:
        if root not in seen:
            seen.add(root)
            unique_roots.append(root)

    # First pass: direct .env file in candidate roots
    for root in unique_roots:
        candidate = root / ".env"
        if candidate.is_file():
            return candidate

    # Second pass: check immediate subdirectories (e.g. test_env/.env)
    for root in unique_roots:
        try:
            for sub in root.iterdir():
                if sub.is_dir() and not sub.name.startswith("."):
                    candidate = sub / ".env"
                    if candidate.is_file():
                        return candidate
        except Exception:
            pass

    # Third pass: walk upward from each root
    for root in unique_roots:
        current = root
        for _ in range(20):
            candidate = current / ".env"
            if candidate.is_file():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent

    return None


# Recognised key names (checked in order, case-insensitive)
DEFAULT_KEY_NAMES = [
    "TOTO_API_KEY",
    "TOTO_API",
    "toto_api_key",
    "toto_api",
    "OLLAMA_API_KEY",
    "ollama_api_key",
    "HF_TOKEN",
    "hf_token",
]


def _find_env_key(var_name: str | None = None) -> str:
    """Find an API key from environment variables."""
    if var_name:
        val = os.environ.get(var_name, "").strip()
        if val:
            return val
        # Case-insensitive check
        for k, v in os.environ.items():
            if k.lower() == var_name.lower() and v.strip():
                return v.strip()

    for candidate in DEFAULT_KEY_NAMES:
        val = os.environ.get(candidate, "").strip()
        if val:
            return val
        for k, v in os.environ.items():
            if k.lower() == candidate.lower() and v.strip():
                return v.strip()

    return ""


def _load_env_if_needed() -> None:
    """Load .env and resolve configuration."""
    # If API key is already resolved, don't redo discovery
    if _config.get("api_key"):
        return

    env_file = _discover_env_file()
    if env_file:
        pairs = _parse_env_file(env_file)
        # Inject into os.environ (don't overwrite existing)
        for k, v in pairs.items():
            if k not in os.environ:
                os.environ[k] = v

    # Resolve API key from environment in priority order
    key = _find_env_key(_config.get("api_key_var"))
    if key:
        _config["api_key"] = key
        _config["_env_loaded"] = True

    # Resolve optional overrides from environment
    for env_var, config_key in [
        ("TOTO_BASE_URL", "base_url"),
        ("OLLAMA_BASE_URL", "base_url"),
        ("TOTO_MODEL", "model"),
        ("OLLAMA_MODEL", "model"),
    ]:
        val = os.environ.get(env_var, "").strip()
        if not val:
            for k, v in os.environ.items():
                if k.lower() == env_var.lower() and v.strip():
                    val = v.strip()
                    break
        if val:
            _config[config_key] = val


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def configure(
    *,
    env_path: str | None = None,
    api_key: str | None = None,
    api_key_var: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> None:
    """Override library configuration programmatically.

    Parameters
    ----------
    env_path : str, optional
        Absolute or relative path to a custom .env file to load.
    api_key : str, optional
        API key value directly for the translation endpoint.
    api_key_var : str, optional
        Custom environment variable name to read the API key from
        (e.g., ``'CUSTOM_TOTO_KEY'``).
    base_url : str, optional
        Base URL of the OpenAI-compatible API endpoint.
    model : str, optional
        Model name to use for translations.
    """
    if api_key_var is not None:
        _config["api_key_var"] = api_key_var

    if env_path:
        pairs = _parse_env_file(Path(env_path))
        for k, v in pairs.items():
            os.environ[k] = v
        # Re-resolve API key after loading custom env
        key = _find_env_key(_config.get("api_key_var"))
        if key:
            _config["api_key"] = key

    if api_key is not None:
        _config["api_key"] = api_key
    else:
        key = _find_env_key(_config.get("api_key_var"))
        if key:
            _config["api_key"] = key

    if base_url is not None:
        _config["base_url"] = base_url
    if model is not None:
        _config["model"] = model
    _config["_env_loaded"] = True


def get_api_key() -> str:
    _load_env_if_needed()
    return _config["api_key"]


def get_base_url() -> str:
    _load_env_if_needed()
    return _config["base_url"]


def get_model() -> str:
    _load_env_if_needed()
    return _config["model"]


# ---------------------------------------------------------------------------
# Resource paths
# ---------------------------------------------------------------------------

PACKAGE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = PACKAGE_DIR / "resources"
DATA_JSONL = RESOURCES_DIR / "data" / "toto_english_2col.jsonl"
GRAMMAR_SPEC = RESOURCES_DIR / "grammar" / "toto_grammar_spec.md"
DOCS_DIR = RESOURCES_DIR / "docs"
TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"
