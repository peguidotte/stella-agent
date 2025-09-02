"""
Módulo de WebSocket usando Pusher para comunicação em tempo real.
"""

import os
import uuid
import pusher
from datetime import datetime
from typing import Dict, Any, Callable
from dotenv import load_dotenv
from loguru import logger
from agent.speech_processor import command_interpreter

# Carrega .env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

class WebSocketManager:
    def __init__(self):
        # Configuração do Pusher
        self.pusher_client = pusher.Pusher(
            app_id=os.environ.get('PUSHER_APP_ID', '2044028'),
            key=os.environ.get('PUSHER_KEY', '6e145679d2e5714d4e58'),
            secret=os.environ.get('PUSHER_SECRET', '0edc812bb267bc12a911'),
            cluster=os.environ.get('PUSHER_CLUSTER', 'us2'),
            ssl=True
        )
        
        # Registra handlers para eventos
        self.event_handlers: Dict[str, Callable] = {
            'client-speech-input': self.handle_speech_input,
            'client-face-input': self.handle_face_input,
        }
        
        # Canal ÚNICO para cada Stella
        self.default_channel = 'private-agent-123'

    def handle_speech_input(self, data: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """
        Processa entrada de speech
        TODO: integrar com stella.agent.speech_processor
        """
        correlation_id = data.get('correlation_id', str(uuid.uuid4()))
        input_text = data.get('data', {}).get('text', 'sem texto')

        logger.info(f"Processando speech {correlation_id}")

        result = command_interpreter(input_text)
        
        # Responde no mesmo canal
        response_data = {
            "correlation_id": data.get('correlation_id', str(uuid.uuid4())),
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
        self.send_event(channel, 'server-speech-output', response_data, correlation_id)
        
        return result
        
    def handle_face_input(self, data: Dict[str, Any], channel: str) -> Dict[str, Any]:
        """
        Processa entrada de face recognition
        TODO: integrar com stella.face_id.face_recognizer
        """
        correlation_id = data.get('correlation_id', str(uuid.uuid4()))

        logger.info(f"Processando face {correlation_id}")

        # TODO: Substituir por processamento real
        # from stella.face_id.face_recognizer import process_face
        # result = process_face(data)
        
        # Mock processing
        user_id = data.get('data', {}).get('userId', 'unknown')
        result = {
            "user_identified": True,
            "user_id": "user_123",
            "user_name": "João Silva",
            "confidence": 0.87,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Responde no mesmo canal
        response_data = {
            "correlation_id": data.get('correlation_id', str(uuid.uuid4())),
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        
        self.send_event(channel, 'server-face-output', response_data, correlation_id)

        return result

    def send_event(self, channel: str, event: str, data: Dict[str, Any], correlation_id: str):
        """Envia evento via Pusher"""
        try:
            self.pusher_client.trigger(channel, event, data)
            logger.success(f"📤 Evento {event} enviado para {channel} com correlation_id {correlation_id}")
        except Exception as e:
            logger.error(f"❌ Erro enviando evento {event}: {e} | correlation_id {correlation_id}")
            raise
            
    def authenticate_channel(self, channel: str, socket_id: str) -> Dict[str, Any]:
        """Autentica canal privado do Pusher"""
        try:
            # Aqui você poderia validar o usuário, mas no teste a gente só libera:
            auth = self.pusher_client.authenticate(
                channel=channel,
                socket_id=socket_id
            )
            logger.info(f"🔐 Canal {channel} autenticado para socket {socket_id}")
            return auth
        except Exception as e:
            logger.error(f"❌ Erro autenticando canal {channel}: {e}")
            raise
            
    # Métodos utilitários para teste
    def test_send_speech_output(self, channel: str = None):
        """Envia evento de teste para speech"""
        channel = channel or self.default_channel
        test_data = {
            "correlation_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "data": {
                "response": "Esta é uma mensagem de teste do Stella Agent!",
                "intent": "test",
                "confidence": 1.0
            }
        }
        
        self.send_event(channel, 'server-speech-output', test_data)
        logger.info(f"🧪 Teste speech enviado para {channel}")
        
    def test_send_face_output(self, channel: str = None):
        """Envia evento de teste para face"""
        channel = channel or self.default_channel
        test_data = {
            "correlation_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "data": {
                "user_identified": True,
                "user_id": "test_user",
                "user_name": "Teste Silva",
                "confidence": 0.99
            }
        }
        
        self.send_event(channel, 'server-face-output', test_data)
        logger.info(f"🧪 Teste face enviado para {channel}")

