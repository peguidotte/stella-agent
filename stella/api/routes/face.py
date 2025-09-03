"""
Rotas de reconhecimento facial
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models.requests import FaceRequest
from stella.api.models.responses import StandardResponse
from stella.api.services.face import FaceService

def create_face_router(websocket_manager) -> APIRouter:
    """
    Cria router de reconhecimento facial com dependência do WebSocketManager
    
    Args:
        websocket_manager: Instância do WebSocketManager
        
    Returns:
        APIRouter configurado para reconhecimento facial
    """
    router = APIRouter(prefix="/face", tags=["Reconhecimento Facial"])
    face_service = FaceService(websocket_manager)
    
    @router.post("/recognize", response_model=StandardResponse)
    async def recognize_face(request: FaceRequest):
        """
        Processa reconhecimento facial
        
        Args:
            request: Dados da solicitação (session_id, image_data)
            
        Returns:
            StandardResponse com resultado do reconhecimento
        """
        try:
            logger.info(f"👤 Processando reconhecimento facial para sessão: {request.session_id}")
            
            # Valida entrada
            if not request.image_data.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Dados da imagem não podem estar vazios"
                )
            
            # Valida formato base64 básico
            if not request.image_data.startswith(('data:image/', '/9j/', 'iVBOR')):
                raise HTTPException(
                    status_code=400,
                    detail="Formato de imagem inválido (esperado base64)"
                )
            
            # Processa o reconhecimento
            result = face_service.process_face_recognition(
                request.session_id,
                request.image_data
            )
            
            return result
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro no reconhecimento facial: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno no reconhecimento: {str(e)}"
            )
    
    return router
