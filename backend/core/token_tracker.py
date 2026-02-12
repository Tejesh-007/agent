"""Lightweight per-request token usage tracker.

Primary path : read AIMessage.usage_metadata (LangChain standard attribute)
Secondary path: BaseCallbackHandler.on_llm_end (callback fallback)
"""

import logging
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("token_tracker")


def _read_usage(obj) -> tuple[int, int, int]:
    """Extract (input, output, total) from a usage object or dict.

    Handles both:
      - LangChain standard keys: input_tokens, output_tokens, total_tokens
      - Gemini raw keys: prompt_token_count, candidates_token_count, total_token_count
      - OpenAI keys: prompt_tokens, completion_tokens
    """
    if obj is None:
        return 0, 0, 0

    # Support both dict-like and attribute access (UsageMetadata dataclass)
    def _get(key, default=0):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    # LangChain standard (works for Gemini via langchain-google-genai)
    inp = _get("input_tokens", 0)
    out = _get("output_tokens", 0)
    total = _get("total_tokens", 0)

    # Fallback: Gemini raw keys
    if inp == 0 and out == 0:
        inp = _get("prompt_token_count", 0)
        out = _get("candidates_token_count", 0)
        total = _get("total_token_count", 0)

    # Fallback: OpenAI keys
    if inp == 0 and out == 0:
        inp = _get("prompt_tokens", 0)
        out = _get("completion_tokens", 0)

    if total == 0:
        total = inp + out

    return inp, out, total


class TokenTracker(BaseCallbackHandler):
    """Accumulates token usage across multiple LLM calls within one request."""

    def __init__(self):
        super().__init__()
        self.total_input = 0
        self.total_output = 0

    # ----- primary: read directly from AIMessage -----

    def track_from_metadata(self, msg) -> None:
        """Extract token counts from the AIMessage.

        Checks msg.usage_metadata first (LangChain standard), then falls
        back to msg.response_metadata["usage_metadata"].
        """
        # 1) Top-level usage_metadata (LangChain >= 0.2 standard)
        usage = getattr(msg, "usage_metadata", None)

        # 2) Nested inside response_metadata
        if not usage:
            meta = getattr(msg, "response_metadata", {}) or {}
            usage = meta.get("usage_metadata")

        if not usage:
            return

        inp, out, total = _read_usage(usage)
        if inp == 0 and out == 0:
            return

        self.total_input += inp
        self.total_output += out
        logger.info(
            "[tokens] LLM call — input: %d, output: %d, total: %d",
            inp, out, total,
        )

    # ----- secondary: LangChain callback fallback -----

    def on_llm_end(self, response, **kwargs) -> None:
        """Fallback capture via callback handler."""
        llm_output = response.llm_output or {}
        usage = (
            llm_output.get("token_usage")
            or llm_output.get("usage_metadata")
            or {}
        )
        inp, out, _ = _read_usage(usage)
        if inp == 0 and out == 0:
            return

        self.total_input += inp
        self.total_output += out
        logger.info(
            "[tokens] LLM call (callback) — input: %d, output: %d",
            inp, out,
        )

    # ----- summary -----

    def summary(self) -> dict:
        return {
            "total_input_tokens": self.total_input,
            "total_output_tokens": self.total_output,
            "total_tokens": self.total_input + self.total_output,
        }
