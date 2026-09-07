"""
Toto Library — Exception Classes.

All exceptions include actionable guidance so users know exactly
what went wrong and how to fix it.
"""


class TotoError(Exception):
    """Base exception for all toto library errors."""
    pass


class MissingApiKeyError(TotoError):
    """Raised when no API key is found in environment or configuration.

    Includes step-by-step instructions for setting up credentials.
    """

    DEFAULT_MESSAGE = (
        "No API key found. The toto library requires an API key to call the "
        "translation model.\n\n"
        "How to fix this:\n"
        "  1. Create a .env file in your project root (next to your script).\n"
        "  2. Add one of these variables:\n\n"
        "       TOTO_API_KEY=your-key-here\n"
        "       OLLAMA_API_KEY=your-key-here\n"
        "       HF_TOKEN=your-key-here\n\n"
        "  3. Or configure programmatically before translating:\n\n"
        "       import toto\n"
        "       toto.configure(api_key='your-key-here')\n\n"
        "The default endpoint is Ollama Cloud (https://ollama.com/v1) using\n"
        "the nemotron-3-super:cloud model.  You can also use any\n"
        "OpenAI-compatible endpoint by setting TOTO_BASE_URL and TOTO_MODEL\n"
        "in your .env, or via toto.configure(base_url=..., model=...)."
    )

    def __init__(self, message: str | None = None):
        super().__init__(message or self.DEFAULT_MESSAGE)


class ModelConnectionError(TotoError):
    """Raised when the library cannot reach the translation API endpoint.

    Provides troubleshooting steps for connectivity issues.
    """

    def __init__(self, endpoint: str, original_error: Exception | None = None):
        detail = f" ({original_error})" if original_error else ""
        message = (
            f"Could not connect to the translation endpoint: {endpoint}{detail}\n\n"
            "Troubleshooting:\n"
            "  1. Check that your API key is valid and not expired.\n"
            "  2. Verify the endpoint URL is correct.\n"
            "  3. Check your network connection and any proxy/firewall settings.\n"
            "  4. If using a local model, make sure the server is running.\n\n"
            "Current endpoint can be changed via:\n"
            "  toto.configure(base_url='http://your-endpoint/v1')"
        )
        super().__init__(message)
        self.endpoint = endpoint
        self.original_error = original_error


class TranslationError(TotoError):
    """Raised when the model returns an unusable response.

    Includes the raw content for debugging.
    """

    def __init__(self, reason: str, raw_content: str = "", raw_reasoning: str = ""):
        message = (
            f"Translation failed: {reason}\n\n"
            "This usually means the model's response could not be parsed into\n"
            "the expected JSON format. Possible causes:\n"
            "  - The model exhausted its token budget on reasoning.\n"
            "  - The input text was too long or ambiguous.\n"
            "  - A temporary API issue.\n\n"
            "Try again, or simplify the input sentence."
        )
        super().__init__(message)
        self.reason = reason
        self.raw_content = raw_content
        self.raw_reasoning = raw_reasoning
