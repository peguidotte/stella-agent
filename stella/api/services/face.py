"""
Serviço de reconhecimento facial
"""

from datetime import datetime
from loguru import logger
from stella.api.models import FaceAuthResponse
from stella.api.models.face import FaceAuthRequest, FaceCadRequest, FaceCadResponse
from stella.face_id.face_recognizer import FaceRecognizer
from stella.websocket.websocket_manager import get_default_channel, send_event

class FaceService:
    """Serviço responsável pelo reconhecimento facial"""

    @staticmethod
    def process_face_recognition(request: FaceAuthRequest) -> FaceAuthResponse:
        """
        Processa reconhecimento facial
        
        Args:
            session_id: ID da sessão do usuário
            image_data: Dados da imagem em base64
            
        Returns:
            StandardResponse com resultado do reconhecimento
        """
        try:
            logger.info(f"👤 Processando reconhecimento facial para sessão {request.session_id}")

            # Processa reconhecimento facial
            recognition_result = FaceRecognizer.validate_face(request.encoding)

            # Envia resultado via WebSocket
            channel_name = get_default_channel()
            
            if recognition_result.get("success", False):
                user_info = recognition_result.get("user", {})
                logger.success(f"✅ Usuário reconhecido: {user_info.get('name', 'Desconhecido')}")

                send_event(
                    channel_name,
                    "face_recognition_success",
                    {
                        "user": user_info,
                        "timestamp": datetime.now(),
                        "session_id": request.session_id
                    }
                )
                
                return FaceAuthResponse(
                    success=True,
                    message="Usuário reconhecido com sucesso",
                    data={"user": user_info}
                )
            else:
                error_msg = recognition_result.get("message", "Usuário não reconhecido")
                logger.warning(f"⚠️ Reconhecimento falhou: {error_msg}")

                send_event(
                    channel_name,
                    "face_recognition_failed",
                    {
                        "error": error_msg,
                        "timestamp": datetime.now(),
                        "session_id": request.session_id
                    }
                )
                
                return FaceAuthResponse(
                    success=False,
                    message=error_msg,
                    data={"error": error_msg}
                )
            
        except Exception as e:
            logger.error(f"❌ Erro no reconhecimento facial: {e}")
            
            # Envia erro via WebSocket se possível
            try:
                channel_name
                send_event(
                    channel_name,
                    "face_recognition_error",
                    {
                        "error": str(e),
                        "timestamp": datetime.now(),
                        "session_id": request.session_id
                    }
                )
            except:
                pass
            
            return FaceAuthResponse(
                success=False,
                message="Erro no reconhecimento facial",
                data={"error": str(e)}
            )

    def register_new_face(request: FaceCadRequest) -> FaceCadResponse:
        return FaceCadResponse(
            session_id=request.session_id,
            correlation_id=request.correlation_id,
            timestamp=datetime.now(),
            success=True,
            message="Cadastro facial iniciado, resultado será enviado via WebSocket"
        )
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
