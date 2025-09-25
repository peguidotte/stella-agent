"""Integração com Pusher para comunicação em tempo real do Stella Agent."""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pusher
from loguru import logger

from stella.config.settings import settings

ENV_PATH = Path(__file__).resolve().parents[2] / '.env'


def require_pusher_env() -> None:
    """Valida se as credenciais obrigatórias do Pusher estão configuradas."""
    missing = settings.missing_pusher_credentials()
    if missing:
        logger.error(
            "Variáveis de ambiente do Pusher ausentes: {}. "
            "Defina-as no .env ({}) e reinicie."
            .format(", ".join(missing), ENV_PATH)
        )
        sys.exit(1)
    logger.success("✅ Variáveis do PUSHER carregadas.")

# Valida configurações na importação
require_pusher_env()

# Cliente Pusher global (singleton)
_pusher_client = pusher.Pusher(
    app_id=settings.pusher_app_id,
    key=settings.pusher_key,
    secret=settings.pusher_secret,
    cluster=settings.pusher_cluster,
    ssl=True,
)

# Canal padrão
DEFAULT_CHANNEL = settings.pusher_channel
logger.info(f"📡 Canal padrão configurado: {DEFAULT_CHANNEL}")

def send_event(channel: str, event: str, data: Dict[str, Any]) -> None:
    """
    Envia evento via Pusher
    
    Args:
        channel: Canal do Pusher
        event: Nome do evento
        data: Dados a enviar
    """
    try:
        serializable_data = _convert_datetime_to_string(data)
        _pusher_client.trigger(channel, event, serializable_data)
        correlation_info = f" | Corr: {data.get('correlation_id', 'NO-CORRELATION-ID')}"
        logger.success(f"📡 Evento {event} enviado para {channel}{correlation_info}")
    except Exception as e:
        correlation_info = f" | Corr: {data.get('correlation_id', 'NO-CORRELATION-ID')}"
        logger.error(f"❌ Erro enviando evento {event}: {e}{correlation_info}")
        raise
    
def _convert_datetime_to_string(data: Any) -> Any:
    """Converte datetime objects para string recursivamente"""
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: _convert_datetime_to_string(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_datetime_to_string(item) for item in data]
    else:
        return data

def authenticate_channel(channel: str, socket_id: str) -> Dict[str, Any]:
    """
    Autentica canal privado do Pusher
    
    Args:
        channel: Nome do canal
        socket_id: ID do socket do cliente
        
    Returns:
        Dados de autenticação do Pusher
    """
    try:
        auth = _pusher_client.authenticate(
            channel=channel,
            socket_id=socket_id
        )
        logger.info(f"🔐 Canal {channel} autenticado para socket {socket_id}")
        return auth
    except Exception as e:
        logger.error(f"❌ Erro autenticando canal {channel}: {e}")
        raise

def get_default_channel() -> str:
    """Retorna o canal padrão configurado"""
    return DEFAULT_CHANNEL