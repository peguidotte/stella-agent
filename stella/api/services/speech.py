"""
Serviço de processamento de voz e interação com IA
"""
import json
from loguru import logger
from typing import Dict, Any, Optional
from stella.api.models.responses import StandardResponse
from stella.agent.speech_processor import command_interpreter

class SpeechService:
    """Serviço responsável pelo processamento de voz e interação com IA"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
    
    def process_speech_input(self, session_id: str, text: str) -> StandardResponse:
        """
        Processa entrada de voz usando IA com contexto de sessão
        
        Args:
            session_id: ID da sessão do usuário
            text: Texto a ser processado
            
        Returns:
            StandardResponse com resultado do processamento
        """
        try:
            logger.info(f"🗣️ Processando fala para sessão {session_id}: {text[:50]}...")
            
            # Processa usando a IA com contexto de sessão
            ai_response = command_interpreter(text, session_id)
            
            # Envia resposta via WebSocket
            if ai_response:
                channel_name = f"private-session-{session_id}"
                self.websocket_manager.send_message(
                    channel_name,
                    "ai_response",
                    {
                        "message": ai_response,
                        "timestamp": self._get_current_timestamp(),
                        "session_id": session_id
                    }
                )
                logger.success(f"✅ Resposta enviada para sessão {session_id}")
            
            return StandardResponse(
                success=True,
                message="Fala processada e resposta enviada",
                data={"ai_response": ai_response}
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar fala: {e}")
            error_response = f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}"
            
            # Envia erro via WebSocket se possível
            try:
                channel_name = f"private-session-{session_id}"
                self.websocket_manager.send_message(
                    channel_name,
                    "ai_error",
                    {
                        "error": error_response,
                        "timestamp": self._get_current_timestamp(),
                        "session_id": session_id
                    }
                )
            except:
                pass  # Se falhar, pelo menos retorna erro via HTTP
            
            return StandardResponse(
                success=False,
                message="Erro ao processar fala",
                data={"error": str(e)}
            )
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
