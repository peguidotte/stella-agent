"""Gerenciamento de sessões do Stella."""

from .manager import (
    active_session_id,
    clear_all,
    end_session,
    get_session,
    switch_active_session,
)

__all__ = [
    "active_session_id",
    "clear_all",
    "end_session",
    "get_session",
    "switch_active_session",
]
