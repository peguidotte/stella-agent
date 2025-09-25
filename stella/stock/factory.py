from __future__ import annotations

from functools import lru_cache

from .base import AbstractStockProvider
from .local import LocalStockProvider
from .remote import RemoteStockProvider
from stella.config.settings import settings


@lru_cache(maxsize=1)
def get_stock_provider() -> AbstractStockProvider:
    """Retorna o provedor de estoque apropriado para a configuração atual."""
    if settings.mock_database:
        return LocalStockProvider()
    return RemoteStockProvider()


__all__ = ["get_stock_provider"]
