"""
Módulo de WebSocket usando Pusher para comunicação em tempo real com Front End.
"""

import os
import pusher
from datetime import datetime
from typing import Dict, Any, Callable
from dotenv import load_dotenv
from loguru import logger
from stella.agent.speech_processor import command_interpreter
import sys

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
    logger.success("Variáveis do PUSHER carregadas.")

require_pusher_env()

class WebSocketManager:
    def __init__(self):
        # Configuração do Pusher
        self.pusher_client = pusher.Pusher(
            app_id=os.environ.get('PUSHER_APP_ID'),
            key=os.environ.get('PUSHER_KEY'),
            secret=os.environ.get('PUSHER_SECRET'),
            cluster=os.environ.get('PUSHER_CLUSTER'),
            ssl=True
        )
        
        # Registra handlers para eventos
        self.event_handlers: Dict[str, Callable] = {
            'client-speech-input': self.handle_speech_input,
            'client-face-input': self.handle_face_input,
        }
        
        # Canal ÚNICO por dispositivo
        self.default_channel = os.environ.get('STELLA_CHANNEL', 'private-agent-123')
        logger.info(f"Canal único configurado: {self.default_channel}")

    def handle_speech_input(self, data: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """
        Processa entrada de speech
        TODO: integrar com stella.agent.speech_processor
        """
        session_id = data.get('session_id')
        correlation_id = data.get('correlation_id', 'NO-CORRELATION-ID')
        input_text = data.get('data', {}).get('text', 'sem texto')

        if not session_id:
            logger.error(f"Session ID ausente | correlation_id {correlation_id}")
            return {
                "error": "session_id ausente"
            }
        if not input_text:
            logger.error(f"Input text ausente | correlation_id {correlation_id}")
            return {
                "error": "text ausente"
            }

        logger.info(f"Processando speech {correlation_id} na sessão {session_id}")

        result = command_interpreter(input_text, session_id)
        
        response_data = {
            "session_id": session_id,
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
        self.send_event(channel, 'server-speech-output', response_data)
        
        return result
        
    def handle_face_input(self, data: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """
        Processa entrada de face recognition
        TODO: integrar com stella.face_id.face_recognizer
        """
        session_id = data.get('session_id')
        correlation_id = data.get('correlation_id', 'NO-CORRELATION-ID')
        if not session_id:
            logger.error(f"Session ID ausente | correlation_id {correlation_id}")
            return {
                "error": "session_id ausente"
            }

        logger.info(f"Processando face {correlation_id}")

        # TODO: Substituir por processamento real
        # from stella.face_id.face_recognizer import process_face
        # result = process_face(data)
        
        result = {
            "user_identified": True,
            "user_id": "user_123",
            "user_name": "João Silva",
            "confidence": 0.87,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Responde no mesmo canal
        response_data = {
            "correlation_id": correlation_id,
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
        self.send_event(channel, 'server-face-output', response_data, correlation_id)

        return result

    def send_event(self, channel: str, event: str, data: Dict[str, Any], correlation_id: str):
        """Envia evento via Pusher"""
        try:
            self.pusher_client.trigger(channel, event, data)
            logger.success(f"Evento {event} enviado para {channel} com correlation_id {correlation_id}")
        except Exception as e:
            logger.error(f"Erro enviando evento {event}: {e} | correlation_id {correlation_id}")
            raise
            
    def authenticate_channel(self, channel: str, socket_id: str) -> Dict[str, Any]:
        """Autentica canal privado do Pusher"""
        try:
            # Aqui você poderia validar o usuário, mas no teste a gente só libera:
            auth = self.pusher_client.authenticate(
                channel=channel,
                socket_id=socket_id
            )
            logger.info(f"Canal {channel} autenticado para socket {socket_id}")
            return auth
        except Exception as e:
            logger.error(f"Erro autenticando canal {channel}: {e}")
            raise
