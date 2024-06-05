"""Callback Handler that prints to std out."""

from __future__ import annotations

from typing import Any, Optional

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.utils import print_text


class StdOutCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, color: Optional[str] = None) -> None:
        self.color = color

    def on_text(
        self,
        text: str,
        color: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Run when agent ends."""
        verbose = kwargs.get("verbose")
        if verbose:
            print_text(text, color=color or self.color)
