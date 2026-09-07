"""
Toto Library — Web Interface Agent.

Wraps the Flask-based agentic translation interface in a clean
``webagent.run()`` API for quick local deployment.
"""

from pathlib import Path

from .config import TEMPLATES_DIR, STATIC_DIR, get_model, get_base_url


class WebAgent:
    """Serves the Toto Agentic Translation web interface.

    Examples
    --------
    >>> from toto import webagent
    >>> webagent.run(port=5001)
    """

    def __init__(self):
        self._app = None

    def _create_app(self):
        """Build the Flask application (lazy)."""
        try:
            from flask import Flask, render_template, request, jsonify
        except ImportError as exc:
            raise ImportError(
                "The 'flask' package is required for the web interface. "
                "Install it with:  pip install flask>=3.0"
            ) from exc

        from .agent import TotoAgent
        from .unicode import roman_to_toto

        app = Flask(
            __name__,
            template_folder=str(TEMPLATES_DIR),
            static_folder=str(STATIC_DIR),
        )

        agent_instance = None

        def get_agent():
            nonlocal agent_instance
            if agent_instance is None:
                agent_instance = TotoAgent()
            return agent_instance

        @app.route("/")
        def index():
            return render_template("index.html", model_name=get_model())

        @app.route("/api/translate", methods=["POST"])
        def api_translate():
            data = request.get_json() or {}
            text = (data.get("text") or "").strip()
            lang = (data.get("lang") or "en").strip().lower()
            if not text:
                return jsonify({"error": "No input text provided"}), 400

            try:
                current_agent = get_agent()
                result = current_agent.translate(text, lang=lang)
                return jsonify({
                    "english": result.english,
                    "bengali": result.bengali,
                    "toto": result.roman,
                    "toto_script": result.script,
                    "literal_gloss": result.gloss,
                    "notes": result.notes,
                    "reasoning": result.reasoning,
                })
            except Exception as e:
                return jsonify({
                    "error": str(e),
                    "english": "",
                    "bengali": "",
                    "toto": "",
                    "toto_script": "",
                    "literal_gloss": "",
                    "notes": f"Translation error: {e}",
                    "reasoning": "",
                }), 500

        return app

    def get_app(self):
        """Return the Flask app instance (creates it if needed)."""
        if self._app is None:
            self._app = self._create_app()
        return self._app

    def test_client(self):
        """Return a Flask test client for automated testing."""
        return self.get_app().test_client()

    def run(self, host: str = "127.0.0.1", port: int = 5001, debug: bool = False):
        """Start the web interface server.

        Parameters
        ----------
        host : str
            Bind address. Default ``"127.0.0.1"`` (localhost only).
        port : int
            Port number. Default ``5001``.
        debug : bool
            Enable Flask debug mode. Default ``False``.
        """
        app = self.get_app()
        print(f"\n* Toto Agent Web Interface running at http://{host}:{port}")
        app.run(host=host, port=port, debug=debug)
