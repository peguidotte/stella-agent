"""
Módulo de WebSocket usando Pusher para comunicação em tempo real com Front End.
Funções utilitárias para envio de eventos e autenticação.
"""

import os
import pusher
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
from loguru import logger
import sys

# Carrega variáveis de ambiente
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def require_pusher_env():
    """Garante que todas as variáveis do Pusher existam; encerra o processo se faltar algo."""
    required = ['PUSHER_APP_ID', 'PUSHER_KEY', 'PUSHER_SECRET', 'PUSHER_CLUSTER']
    missing = [k for k in required if not os.environ.get(k)]
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
    app_id=os.environ.get('PUSHER_APP_ID'),
    key=os.environ.get('PUSHER_KEY'),
    secret=os.environ.get('PUSHER_SECRET'),
    cluster=os.environ.get('PUSHER_CLUSTER'),
    ssl=True
)

# Canal padrão
DEFAULT_CHANNEL = os.environ.get('STELLA_CHANNEL', 'private-agent-123')
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