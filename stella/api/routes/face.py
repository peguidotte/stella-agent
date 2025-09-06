"""
Rotas de reconhecimento facial
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models import FaceAuthRequest, FaceCadRequest, FaceAuthResponse, FaceCadResponse, APIBaseResponse
from stella.api.services.face import FaceService
import asyncio

def create_face_router() -> APIRouter:
    """
    Cria API router de reconhecimento facial 
    """
    router = APIRouter(prefix="/face", tags=["Reconhecimento Facial"])

    @router.post("/recognize", response_model=APIBaseResponse)
    async def recognize_face(request: FaceAuthRequest):
        """
        Processa reconhecimento facial
        
        Args:
            request: Dados da solicitação (session_id, image_data)
            
        Returns:
            FaceAuthResponse com resultado do reconhecimento
        """
        try:
            logger.info(f"👤 Processando reconhecimento facial para sessão: {request.session_id}")

            asyncio.create_task(FaceService.process_face_recognition(
                request
            ))

            return APIBaseResponse(
                status="accepted",
                correlation_id=request.correlation_id,
                message="Processamento de reconhecimento facial iniciado, resultado será enviado via WebSocket"
            )
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro no reconhecimento facial: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno no reconhecimento: {str(e)}"
            )

    @router.post("/register", response_model=APIBaseResponse)
    async def register_face(request: FaceCadRequest):
        """
        Cadastra um novo usuário via reconhecimento facial
        
        Args:
            request: Dados da solicitação (name, image_data)
            
        Returns:
            FaceCadResponse com resultado do cadastro
        """
        try:
            logger.info(f"🆕 Cadastrando novo usuário: {request.name}")
            
            # Processa o cadastro facial
            asyncio.create_task(FaceService.register_new_face(
                request
            ))

            return APIBaseResponse(
                status="accepted",
                correlation_id=request.correlation_id,
                message="Processamento de cadastro facial iniciado, resultado será enviado via WebSocket"
            )
            
        except HTTPException:
            raise
    
    return router
