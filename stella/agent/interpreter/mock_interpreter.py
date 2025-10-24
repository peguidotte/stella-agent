from __future__ import annotations

from typing import Any, Dict, List

from stella.config.settings import settings
from stella.session import manager as session_manager
from stella.stock import AbstractStockProvider
from stella.utils import normalize_key
from loguru import logger

from .base import AbstractInterpreter
from .utils import extract_quantity


class MockInterpreter(AbstractInterpreter):
    """Interpretação local sem chamadas ao Gemini."""

    def __init__(self, stock_provider: AbstractStockProvider) -> None:
        super().__init__(stock_provider)

    async def interpret(self, command: str, session_id: str) -> Dict[str, Any]:
        session_manager.get_session(session_id, lambda: {"mode": "mock"})
        session_manager.switch_active_session(session_id)
        stock_map = await self.stock_provider.load_stock()
        normalized_command = normalize_key(command)
        lower_command = command.lower()

        detected_items: List[Dict[str, Any]] = []
        for norm_key, data in stock_map.items():
            name = data.get("name") or norm_key
            aliases_norm = {norm_key, normalize_key(name)}
            metadata = data.get("metadata") or {}
            if isinstance(metadata, dict):
                raw_key = metadata.get("nome") or metadata.get("chave") or metadata.get("id")
                if raw_key:
                    aliases_norm.add(normalize_key(str(raw_key)))
            if any(alias and alias in normalized_command for alias in aliases_norm):
                quantity = extract_quantity(lower_command, [name.lower(), norm_key.replace('_', ' ')])
                detected_items.append({
                    "productName": name,
                    "quantity": quantity,
                })

        intention = "normal"
        if any(keyword in lower_command for keyword in ["retirar", "retire", "pegar", "separar", "buscar"]):
            intention = "withdraw_request"
        if "confirm" in lower_command or "confirmar" in lower_command:
            intention = "withdraw_confirm" if detected_items else "doubt"
        elif any(keyword in lower_command for keyword in ["estoque", "quantidade", "tem", "disponível"]):
            intention = "stock_query"

        stella_analysis = "normal"
        response = "Modo mock ativo."

        if intention == "withdraw_request":
            if detected_items:
                resumo = ", ".join([f"{item['quantity']}x {item['productName']}" for item in detected_items])
                response = f"Posso separar {resumo}. Confirme se estiver tudo certo."
            else:
                response = "Quais itens você deseja retirar?"
        elif intention == "withdraw_confirm":
            if detected_items:
                resumo = ", ".join([f"{item['quantity']}x {item['productName']}" for item in detected_items])
                response = f"Retirada de {resumo} confirmada (simulação)."
            else:
                response = "Não encontrei itens para confirmar. Pode repetir?"
                stella_analysis = "ambiguous"
                intention = "doubt"
        elif intention == "stock_query":
            if detected_items:
                detalhes = []
                for item in detected_items:
                    norm_key = normalize_key(item["productName"])
                    estoque_item = stock_map.get(norm_key, {})
                    quantidade = estoque_item.get("quantity", "desconhecida")
                    detalhes.append(f"{item['productName']}: {quantidade} unidade(s) disponíveis")
                response = "Estoque simulado:\n" + "\n".join(detalhes)
            else:
                response = "Os itens simulados estão com disponibilidade normal."
        else:
            response = "Modo mock ativo. Posso simular retiradas ou consultas de estoque."

        for item in detected_items:
            estoque_item = stock_map.get(normalize_key(item["productName"]), {})
            quantidade = int(estoque_item.get("quantity", 0))
            if quantidade <= settings.critical_stock_threshold:
                stella_analysis = "critical_stock_alert"
            elif quantidade <= settings.low_stock_threshold and stella_analysis == "normal":
                stella_analysis = "low_stock_alert"

        logger.info(f"[MockInterpreter] Session: {session_id} | Command: {command} | Intention: {intention} | Items: {detected_items} | Analysis: {stella_analysis}")

        return {
            "intention": intention,
            "items": detected_items if intention in {"withdraw_request", "withdraw_confirm", "doubt"} else [],
            "response": response,
            "stella_analysis": stella_analysis,
            "reason": "Simulação local de interpretação de comandos.",
        }


__all__ = ["MockInterpreter"]
