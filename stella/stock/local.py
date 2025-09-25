from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from .base import AbstractStockProvider
from stella.utils import normalize_key


class LocalStockProvider(AbstractStockProvider):
    """Carrega estoque a partir de um arquivo JSON local."""

    def __init__(self, stock_file: Path | None = None) -> None:
        self.stock_file = stock_file or Path(__file__).parent / "stock.json"

    def _load_sync(self) -> Dict[str, Any]:
        if not self.stock_file.exists():
            logger.error(f"Arquivo de estoque não encontrado em: {self.stock_file}")
            return {}

        try:
            with open(self.stock_file, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
        except Exception as exc:  # pragma: no cover - leitura resiliente
            logger.error(f"Erro ao carregar dados do estoque local: {exc}")
            return {}

        estoque = payload.get("estoque", {}) or {}
        updated_at = payload.get("ultima_atualizacao")
        stock_map: Dict[str, Any] = {}

        for raw_key, item in estoque.items():
            name = item.get("nome_completo") or raw_key
            norm_key = normalize_key(name)
            stock_map[norm_key] = {
                "id": raw_key,
                "name": name,
                "description": item.get("descricao") or name,
                "quantity": int(item.get("quantidade_atual", 0)),
                "createdAt": updated_at,
                "updatedAt": updated_at,
                "categoryName": item.get("categoria"),
                "metadata": item,
            }

        return stock_map

    async def load_stock(self) -> Dict[str, Any]:
        return await asyncio.to_thread(self._load_sync)


__all__ = ["LocalStockProvider"]
