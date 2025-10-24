from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional

from loguru import logger

from stella.config.settings import settings

__all__ = [
    "get_session",
    "end_session",
    "switch_active_session",
    "clear_all",
    "active_session_id",
]


_SESSIONS: Dict[str, Any] = {}
_LAST_SEEN: Dict[str, float] = {}
_ACTIVE_SESSION_ID: Optional[str] = None


def _session_ttl() -> int:
    return max(settings.session_ttl_seconds, 0)


def _gc_sessions(on_end: Optional[Callable[[Any], None]] = None) -> None:
    ttl = _session_ttl()
    if ttl <= 0:
        return

    now = time.time()
    expired = [sid for sid, ts in _LAST_SEEN.items() if now - ts > ttl]
    for sid in expired:
        session = _SESSIONS.pop(sid, None)
        _LAST_SEEN.pop(sid, None)
        if session and on_end:
            try:
                on_end(session)
            except Exception as exc:  # pragma: no cover - handler resiliente
                logger.warning(f"Erro ao finalizar sessão expirada {sid}: {exc}")
        logger.info(f"Sessão expirada e removida: {sid}")


def get_session(session_id: str, factory: Callable[[], Any], *, on_new: Optional[Callable[[Any], None]] = None) -> Any:
    """Recupera ou cria uma sessão usando o factory fornecido."""
    if not session_id:
        raise ValueError("session_id é obrigatório para manter contexto.")

    session = _SESSIONS.get(session_id)
    if session is None:
        session = factory()
        _SESSIONS[session_id] = session
        if on_new:
            try:
                on_new(session)
            except Exception as exc:  # pragma: no cover
                logger.warning(f"Erro no callback de nova sessão {session_id}: {exc}")
        logger.info(f"Sessão criada: {session_id}")

    _LAST_SEEN[session_id] = time.time()
    _gc_sessions()
    return session


def end_session(session_id: str, *, on_end: Optional[Callable[[Any], None]] = None) -> bool:
    """Finaliza e remove uma sessão."""
    session = _SESSIONS.pop(session_id, None)
    _LAST_SEEN.pop(session_id, None)
    if session is None:
        logger.warning(f"⚠️ Sessão não encontrada para encerrar: {session_id}")
        return False

    if on_end:
        try:
            on_end(session)
        except Exception as exc:  # pragma: no cover
            logger.warning(f"Erro ao finalizar sessão {session_id}: {exc}")

    logger.info(f"🗑️ Sessão encerrada: {session_id}")
    global _ACTIVE_SESSION_ID
    if _ACTIVE_SESSION_ID == session_id:
        _ACTIVE_SESSION_ID = None
    return True


def switch_active_session(session_id: str, *, on_end: Optional[Callable[[Any], None]] = None) -> None:
    """Garante sessão exclusiva: ao trocar, apaga histórico anterior."""
    global _ACTIVE_SESSION_ID
    if _ACTIVE_SESSION_ID and _ACTIVE_SESSION_ID != session_id:
        for sid in list(_SESSIONS.keys()):
            if sid != session_id:
                end_session(sid, on_end=on_end)
        logger.info(f"Alternando sessão ativa de {_ACTIVE_SESSION_ID} para {session_id}")
    _ACTIVE_SESSION_ID = session_id
    _LAST_SEEN[session_id] = time.time()


def clear_all(*, on_end: Optional[Callable[[Any], None]] = None) -> None:
    """Remove todas as sessões em memória."""
    for sid in list(_SESSIONS.keys()):
        end_session(sid, on_end=on_end)
    _SESSIONS.clear()
    _LAST_SEEN.clear()
    global _ACTIVE_SESSION_ID
    _ACTIVE_SESSION_ID = None


def active_session_id() -> Optional[str]:
    """Retorna a sessão atualmente ativa."""
    return _ACTIVE_SESSION_ID
