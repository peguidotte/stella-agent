from __future__ import annotations

"""Orquestra o fluxo de interpretação de comandos falados da Stella."""

import asyncio
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from stella.agent.interpreter import (  # noqa: E402
    AbstractInterpreter,
    get_interpreter as build_interpreter,
)
from stella.agent.interpreter.factory import PublisherFn  # noqa: E402
from stella.config.settings import settings  # noqa: E402
from stella.messaging.publisher import publish  # noqa: E402
from stella.session import manager as session_manager  # noqa: E402
from stella.stock.factory import get_stock_provider  # noqa: E402


_INTERPRETER: Optional[AbstractInterpreter] = None
_PUBLISHER: PublisherFn = publish


def _build_error_response(reason: str) -> Dict[str, Any]:
    """Retorna um payload consistente para falhas internas."""
    return {
        "intention": "not_understood",
        "items": [],
        "response": "Houve um erro no processamento. Pode repetir sua solicitação?",
        "stella_analysis": "not_understood",
        "reason": reason,
    }


def _ensure_interpreter() -> AbstractInterpreter:
    """Garante uma instância única do interpretador configurado via factories."""
    global _INTERPRETER
    if _INTERPRETER is None:
        logger.info(
            "Inicializando interpretador | mock_gemini={} | mock_database={}",
            settings.mock_gemini,
            settings.mock_database,
        )
        stock_provider = get_stock_provider()
        _INTERPRETER = build_interpreter(stock_provider, _PUBLISHER)
    return _INTERPRETER


async def command_interpreter(command: str, session_id: str) -> Dict[str, Any]:
    """Encaminha o comando do usuário para o interpretador configurado."""
    try:
        interpreter = _ensure_interpreter()
    except Exception as exc:  # pragma: no cover - erro crítico de bootstrap
        logger.error(f"Falha ao inicializar interpretador: {exc}")
        return _build_error_response("bootstrap_failure")

    try:
        result = await interpreter.interpret(command, session_id)
        return result
    except Exception as exc:  # pragma: no cover - fallback resiliente
        logger.error(f"Erro ao interpretar comando (sessão {session_id}): {exc}")
        return _build_error_response("internal_error")


def end_session(session_id: str) -> bool:
    """Finaliza a sessão associada ao interpretador."""
    return session_manager.end_session(session_id)


def clear_sessions() -> None:
    """Remove todas as sessões em memória."""
    session_manager.clear_all()


def active_session_id() -> Optional[str]:
    """Retorna a sessão atualmente ativa, se houver."""
    return session_manager.active_session_id()


def refresh_interpreter() -> None:
    """Força a reinicialização do interpretador e de suas dependências."""
    global _INTERPRETER
    _INTERPRETER = None


__all__ = [
    "command_interpreter",
    "end_session",
    "clear_sessions",
    "active_session_id",
    "refresh_interpreter",
]


async def _interactive_cli() -> None:
    """Interface simples para testes manuais via terminal."""
    print("🤖 Stella Agent - Console de Testes do Speech Processor")
    print("Digite comandos em português. Use /help para listar atalhos.")

    session_id = _new_session_id()
    session_manager.switch_active_session(session_id)
    print(f"📝 Sessão inicial: {session_id}\n")
    managed_sessions: set[str] = set()

    while True:
        try:
            command = input(f"[{session_id}] Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Encerrando console de testes.")
            break

        if not command:
            continue

        if command.startswith("/"):
            if command == "/help":
                _print_help()
            elif command == "/new":
                if session_id in managed_sessions:
                    end_session(session_id)
                    managed_sessions.discard(session_id)
                session_id = _new_session_id()
                session_manager.switch_active_session(session_id)
                print(f"🆕 Nova sessão criada: {session_id}\n")
            elif command == "/clear":
                clear_sessions()
                managed_sessions.clear()
                session_id = _new_session_id()
                session_manager.switch_active_session(session_id)
                print("🧹 Todas as sessões foram limpas.")
                print(f"🆕 Sessão atual: {session_id}\n")
            elif command == "/session":
                current = active_session_id()
                print(f"📊 Sessão ativa no gerenciador: {current or 'nenhuma'}\n")
            elif command == "/refresh":
                refresh_interpreter()
                print("🔄 Interpretador será recriado na próxima chamada.\n")
            elif command == "/quit":
                print("👋 Até a próxima!")
                break
            else:
                print("❓ Comando não reconhecido. Use /help para ajuda.\n")
            continue

        print("🤖 Stella está processando...")
        response = await command_interpreter(command, session_id)
        managed_sessions.add(session_id)
        _print_response(response)
        print("-" * 60)

    if session_id in managed_sessions:
        end_session(session_id)


def _new_session_id() -> str:
    return uuid.uuid4().hex[:8]


def _print_help() -> None:
    print("\nComandos disponíveis:")
    print("  /help     - Mostra esta ajuda")
    print("  /new      - Cria uma nova sessão")
    print("  /clear    - Limpa todas as sessões em memória")
    print("  /session  - Mostra a sessão atualmente ativa")
    print("  /refresh  - Refaz a instanciação do interpretador")
    print("  /quit     - Encerra o console")
    print()


def _print_response(payload: Dict[str, Any]) -> None:
    print("📋 Interpretação da Stella:")
    print(f"  🎯 Intention: {payload.get('intention', 'N/A')}")
    print(f"  📦 Items: {payload.get('items', [])}")
    print(f"  💬 Response: {payload.get('response', 'N/A')}")
    print(f"  🔍 Analysis: {payload.get('stella_analysis', 'N/A')}")
    if payload.get("reason"):
        print(f"  💡 Reason: {payload['reason']}")
    print()


if __name__ == "__main__":
    asyncio.run(_interactive_cli())
