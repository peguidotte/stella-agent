from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from loguru import logger

from .base import AbstractStockProvider
from stella.config.settings import settings
from stella.utils import normalize_key


class RemoteStockProvider(AbstractStockProvider):
    """Consulta estoque em serviço HTTP externo."""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0) -> None:
        self.base_url = (base_url or settings.inventory_api_url).rstrip('/')
        self.timeout = timeout

    async def load_stock(self) -> Dict[str, Any]:
        url = f"{self.base_url}/products"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                items = response.json() or []
        except httpx.HTTPError as exc:
            logger.error(f"Erro ao consultar estoque externo ({url}): {exc}")
            return {}
        except Exception as exc:  # pragma: no cover - cobertura resiliente
            logger.error(f"Erro inesperado ao consultar estoque externo: {exc}")
            return {}

        stock_map: Dict[str, Any] = {}
        for item in items:
            name = item.get("name") or ""
            norm_key = normalize_key(name)
            stock_map[norm_key] = {
                "id": item.get("id"),
                "name": name,
                "description": item.get("description"),
                "quantity": int(item.get("quantity", 0)),
                "createdAt": item.get("createdAt"),
                "updatedAt": item.get("updatedAt"),
                "categoryName": item.get("categoryName"),
                "metadata": item,
            }

        return stock_map


__all__ = ["RemoteStockProvider"]
