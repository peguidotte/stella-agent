"""
Serviço de reconhecimento facial
"""
import json
from loguru import logger
from typing import Dict, Any, Optional
from stella.api.models.responses import StandardResponse
from stella.face_id.face_recognizer import FaceRecognizer

class FaceService:
    """Serviço responsável pelo reconhecimento facial"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
    
    def process_face_recognition(self, session_id: str, image_data: str) -> StandardResponse:
        """
        Processa reconhecimento facial
        
        Args:
            session_id: ID da sessão do usuário
            image_data: Dados da imagem em base64
            
        Returns:
            StandardResponse com resultado do reconhecimento
        """
        try:
            logger.info(f"👤 Processando reconhecimento facial para sessão {session_id}")
            
            # Processa reconhecimento facial
            recognition_result = FaceRecognizer.validate_face(image_data)
            
            # Envia resultado via WebSocket
            channel_name = f"private-session-{session_id}"
            
            if recognition_result.get("success", False):
                user_info = recognition_result.get("user", {})
                logger.success(f"✅ Usuário reconhecido: {user_info.get('name', 'Desconhecido')}")
                
                self.websocket_manager.send_message(
                    channel_name,
                    "face_recognition_success",
                    {
                        "user": user_info,
                        "timestamp": self._get_current_timestamp(),
                        "session_id": session_id
                    }
                )
                
                return StandardResponse(
                    success=True,
                    message="Usuário reconhecido com sucesso",
                    data={"user": user_info}
                )
            else:
                error_msg = recognition_result.get("message", "Usuário não reconhecido")
                logger.warning(f"⚠️ Reconhecimento falhou: {error_msg}")
                
                self.websocket_manager.send_message(
                    channel_name,
                    "face_recognition_failed",
                    {
                        "error": error_msg,
                        "timestamp": self._get_current_timestamp(),
                        "session_id": session_id
                    }
                )
                
                return StandardResponse(
                    success=False,
                    message=error_msg,
                    data={"error": error_msg}
                )
            
        except Exception as e:
            logger.error(f"❌ Erro no reconhecimento facial: {e}")
            
            # Envia erro via WebSocket se possível
            try:
                channel_name = f"private-session-{session_id}"
                self.websocket_manager.send_message(
                    channel_name,
                    "face_recognition_error",
                    {
                        "error": str(e),
                        "timestamp": self._get_current_timestamp(),
                        "session_id": session_id
                    }
                )
            except:
                pass
            
            return StandardResponse(
                success=False,
                message="Erro no reconhecimento facial",
                data={"error": str(e)}
            )
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
