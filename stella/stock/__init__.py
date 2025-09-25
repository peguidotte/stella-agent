"""Módulo de carregamento de estoque."""

from .base import AbstractStockProvider
from .factory import get_stock_provider

__all__ = ["AbstractStockProvider", "get_stock_provider"]
