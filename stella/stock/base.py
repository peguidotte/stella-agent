from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractStockProvider(ABC):
    """Interface base para provedores de estoque."""

    @abstractmethod
    async def load_stock(self) -> Dict[str, Any]:
        """Retorna um dicionário de estoque indexado por chave normalizada."""
        raise NotImplementedError


__all__ = ["AbstractStockProvider"]
