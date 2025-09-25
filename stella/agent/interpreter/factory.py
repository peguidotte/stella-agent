from __future__ import annotations

from typing import Any, Callable, Dict

from stella.config.settings import settings
from stella.stock import AbstractStockProvider

from .base import AbstractInterpreter
from .gemini_interpreter import GeminiInterpreter
from .mock_interpreter import MockInterpreter

PublisherFn = Callable[[str, str, Dict[str, Any]], bool]


def get_interpreter(stock_provider: AbstractStockProvider, publisher: PublisherFn) -> AbstractInterpreter:
    if settings.mock_gemini:
        return MockInterpreter(stock_provider)
    return GeminiInterpreter(stock_provider, publisher)


__all__ = ["get_interpreter", "PublisherFn"]
