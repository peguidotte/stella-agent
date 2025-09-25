from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from stella.stock import AbstractStockProvider


VALID_INTENTIONS = {
    "withdraw_request",
    "withdraw_confirm",
    "doubt",
    "stock_query",
    "not_understood",
    "normal",
}

VALID_ANALYSES = {
    "normal",
    "low_stock_alert",
    "critical_stock_alert",
    "outlier_withdraw_request",
    "ambiguous",
    "not_understood",
    "greeting",
    "farewell",
}


class AbstractInterpreter(ABC):
    """Contrato base para interpretação de comandos."""

    def __init__(self, stock_provider: AbstractStockProvider) -> None:
        self.stock_provider = stock_provider

    @abstractmethod
    async def interpret(self, command: str, session_id: str) -> Dict[str, Any]:
        """Processa o comando do usuário."""
        raise NotImplementedError


__all__ = ["AbstractInterpreter", "VALID_ANALYSES", "VALID_INTENTIONS"]
