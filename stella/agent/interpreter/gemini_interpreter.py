from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional, cast

from loguru import logger

try:  # pragma: no cover - dependência opcional para ambientes sem Gemini
    import google.generativeai as genai  # type: ignore
except ImportError:  # pragma: no cover - a factory impedirá uso sem a lib
    genai = None

from stella.config.settings import settings
from stella.session import manager as session_manager
from stella.stock import AbstractStockProvider
from stella.utils import normalize_key

from .base import AbstractInterpreter, VALID_ANALYSES, VALID_INTENTIONS

SYSTEM_INSTRUCTION = (
    "Você é Stella, uma assistente de almoxarifado dos laboratórios DASA. Sua função é ser "
    "objetiva e garantir a rapidez na retirada de itens, então fale de forma clara e direta."
    "Caso o usuário peça para que você se apresente, na sua apresentação deixe claro o seu objetivo e que você é assistente de almoxarifado dos laboratórios DASA."
    "Sempre retorne JSON válido, sem exceções, e não adicione explicações fora do JSON. "
    "Analise o estoque antes de confirmar qualquer retirada. Se o estoque for atingir nível baixo ou crítico após a requisição do usuário, alerte o usuário. "
    "O JSON deve ter a seguinte estrutura e valores:"
    """
    {
        "intention": "string (um de: withdraw_request, withdraw_confirm, doubt, stock_query, not_understood, normal)",
        "items": "array (opcional, lista de: {'productName': 'nome_item', 'quantity': numero})",
        "response": "string (resposta natural e amigável para o usuário)",
        "stella_analysis": "string (um de: normal, low_stock_alert, critical_stock_alert, outlier_withdraw_request, ambiguous, not_understood, farewell, greeting)",
        "reason": "string (opcional, justificativa para a análise)"
    }
    """
    "Normalize nomes de itens (ex: 'seringa 10ml' para 'seringa_10ml')."
    "Antes de um withdraw confirm, peça a confirmação ao usuário. Exemplo de confirmação: 'Você confirma a retirada de x itens?'"
    "Depois da confirmação deixe claro ao usuário que você confirmou a retirada. Exemplo de resposta: 'Retirada de x itens confirmada. Obrigada!'"
    "Após uma withdraw confirm, SOMENTE EM CASO em que o usuário peça para cancelar a última requisição, instrua ele a falar com o gerente de estoque"
)


class GeminiInterpreter(AbstractInterpreter):
    """Interpretação usando o modelo Gemini."""

    def __init__(self, stock_provider: AbstractStockProvider, publisher: Callable[[str, str, Dict[str, Any]], bool]) -> None:
        if genai is None:
            raise RuntimeError("Biblioteca google-generativeai não encontrada. Instale-a ou habilite MOCK_GEMINI=true.")
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY ausente. Defina a variável de ambiente ou habilite o modo mock.")

        super().__init__(stock_provider)
        genai_mod = cast(Any, genai)
        genai_mod.configure(api_key=settings.gemini_api_key)
        self._model = genai_mod.GenerativeModel(
            settings.gemini_model_id,
            system_instruction=SYSTEM_INSTRUCTION,
        )
        self.publisher = publisher

    def _create_session(self):
        return self._model.start_chat(history=[])

    async def interpret(self, command: str, session_id: str) -> Dict[str, Any]:
        session_manager.switch_active_session(session_id)
        stock_map = await self.stock_provider.load_stock()

        session = session_manager.get_session(session_id, self._create_session)
        prompt = self._build_prompt(command, stock_map)

        try:
            response = await asyncio.to_thread(session.send_message, prompt)
        except Exception as exc:
            logger.error(f"Erro ao chamar Gemini (sessão {session_id}): {exc}")
            return self._error_response()

        clean_text = self._clean_response_text(response.text)
        logger.debug(f"Resposta limpa do Gemini: {clean_text}")

        try:
            payload = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            logger.error(f"Resposta inválida do Gemini: {exc} | texto: {clean_text}")
            return self._error_response()

        self._enforce_schema(payload)
        self._augment_with_stock(payload, stock_map)

        if payload.get("intention") == "withdraw_confirm":
            await self._handle_withdraw_confirm(session_id, payload, stock_map)

        logger.success(
            f"SessionID: {session_id} - Comando interpretado: {payload.get('intention', 'N/A')}"
        )
        return payload

    @staticmethod
    def _build_prompt(command: str, stock_map: Dict[str, Any]) -> str:
        estoque_formatado = ""
        for norm_name, item in stock_map.items():
            quantidade_atual = item.get('quantity', 0)
            categoria = item.get('categoryName') or 'N/A'
            estoque_formatado += (
                f"\n• {norm_name}: {item.get('name')}\n"
                f"- Quantidade atual: {quantidade_atual} unidade(s)\n"
                f"- Categoria: {categoria}\n"
            )
        return (
            f"Analise este comando: \"{command}\"\n\n"
            f"ESTOQUE ATUAL:\n{estoque_formatado}\n"
        )

    @staticmethod
    def _clean_response_text(text: str) -> str:
        clean = text.strip()
        if clean.startswith('```json'):
            return clean[7:-3]
        if clean.startswith('```'):
            return clean[3:-3]
        return clean

    @staticmethod
    def _error_response() -> Dict[str, Any]:
        return {
            "intention": "not_understood",
            "items": [],
            "response": "Houve um erro no processamento. Pode repetir sua solicitação?",
            "stella_analysis": "not_understood",
        }

    @staticmethod
    def _enforce_schema(payload: Dict[str, Any]) -> None:
        intention = payload.get("intention")
        if intention not in VALID_INTENTIONS:
            logger.warning(f"IA retornou intention inválida: {intention}")
            payload["intention"] = "not_understood"

        analysis = payload.get("stella_analysis")
        if analysis not in VALID_ANALYSES:
            logger.warning(f"IA retornou stella_analysis inválida: {analysis}")
            payload["stella_analysis"] = "not_understood"

        items = payload.get("items")
        if not isinstance(items, list):
            payload["items"] = []

    def _augment_with_stock(self, payload: Dict[str, Any], stock_map: Dict[str, Any]) -> None:
        if payload.get("intention") != "withdraw_request":
            return

        pedidos = payload.get("items", [])
        if not pedidos:
            return

        faltantes: List[str] = []
        insuficientes: List[Dict[str, Any]] = []
        disponiveis: List[Dict[str, Any]] = []

        for item in pedidos:
            name = item.get("productName") or ""
            qty = int(item.get("quantity", 0))
            norm = normalize_key(name)
            stock_item = stock_map.get(norm)
            if not stock_item:
                faltantes.append(name)
                continue
            available = int(stock_item.get("quantity", 0))
            if qty > available:
                insuficientes.append({
                    "name": name,
                    "requested": qty,
                    "available": available,
                })
            else:
                disponiveis.append({
                    "name": name,
                    "requested": qty,
                    "available": available,
                })

        info_msgs: List[str] = []
        if disponiveis:
            info_msgs.append(
                "Disponível: "
                + ", ".join([f"{d['name']} ({d['requested']}/{d['available']})" for d in disponiveis])
            )
        if insuficientes:
            info_msgs.append(
                "Estoque insuficiente: "
                + ", ".join(
                    [
                        f"{d['name']} (solicitado {d['requested']}, disponível {d['available']})"
                        for d in insuficientes
                    ]
                )
            )
        if faltantes:
            info_msgs.append("Não encontrado(s): " + ", ".join(faltantes))

        if info_msgs:
            complemento = " | ".join(info_msgs)
            payload["stella_analysis"] = payload.get("stella_analysis", "normal")
            payload["response"] = (
                f"{payload.get('response', '')} (Checagem de estoque: {complemento})"
            ).strip()

    async def _handle_withdraw_confirm(
        self,
        session_id: str,
        payload: Dict[str, Any],
        stock_map: Dict[str, Any],
    ) -> None:
        items_confirmados = payload.get("items", [])
        if not items_confirmados:
            return

        faltantes: List[str] = []
        insuficientes: List[Dict[str, Any]] = []

        for item in items_confirmados:
            name = item.get("productName") or ""
            qty = int(item.get("quantity", 0))
            norm = normalize_key(name)
            stock_item = stock_map.get(norm)
            if not stock_item:
                faltantes.append(name)
                continue
            available = int(stock_item.get("quantity", 0))
            if qty > available:
                insuficientes.append({
                    "name": name,
                    "requested": qty,
                    "available": available,
                })

        if faltantes or insuficientes:
            msg_parts: List[str] = []
            if faltantes:
                msg_parts.append(f"Itens não encontrados: {', '.join(faltantes)}")
            if insuficientes:
                det = ", ".join(
                    [
                        f"{d['name']} (solicitado {d['requested']}, disponível {d['available']})"
                        for d in insuficientes
                    ]
                )
                msg_parts.append(f"Itens com estoque insuficiente: {det}")
            payload["intention"] = "doubt"
            payload["stella_analysis"] = "ambiguous"
            payload["response"] = (
                "Não consegui confirmar a retirada. "
                + "; ".join(msg_parts)
                + ". Deseja ajustar a quantidade ou escolher outro item?"
            )
            return

        await self._publish_withdraw_confirm(session_id, items_confirmados)

    async def _publish_withdraw_confirm(self, session_id: str, items: List[Dict[str, Any]]) -> None:
        payload = {
            "itens": items,
            "withdrawBy": session_id,
        }
        try:
            logger.debug(f"Preparando para publicar confirmação de retirada | `{payload}`")
            await asyncio.to_thread(self.publisher, 'stock', 'remove', payload)
            logger.success(f"📤 Confirmação de retirada publicada | Sessão: {session_id}")
        except Exception as exc:
            logger.error(f"❌ Erro ao publicar confirmação: {exc}")


__all__ = ["GeminiInterpreter", "SYSTEM_INSTRUCTION"]
