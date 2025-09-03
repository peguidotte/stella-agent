"""
Rotas de processamento de voz
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models.requests import SpeechRequest
from stella.api.models.responses import StandardResponse
from stella.api.services.speech import SpeechService

def create_speech_router(websocket_manager) -> APIRouter:
    """
    Cria router de processamento de voz com dependência do WebSocketManager
    
    Args:
        websocket_manager: Instância do WebSocketManager
        
    Returns:
        APIRouter configurado para processamento de voz
    """
    router = APIRouter(prefix="/speech", tags=["Processamento de Voz"])
    speech_service = SpeechService(websocket_manager)
    
    @router.post("/process", response_model=StandardResponse)
    async def process_speech(request: SpeechRequest):
        """
        Processa entrada de voz usando IA com contexto de sessão
        
        Args:
            request: Dados da solicitação (session_id, text)
            
        Returns:
            StandardResponse com resultado do processamento
        """
        try:
            logger.info(f"🗣️ Processando fala para sessão: {request.session_id}")
            
            # Valida entrada
            if not request.text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Texto não pode estar vazio"
                )
            
            if len(request.text) > 1000:  # Limite de segurança
                raise HTTPException(
                    status_code=400,
                    detail="Texto muito longo (máximo 1000 caracteres)"
                )
            
            # Processa a fala
            result = speech_service.process_speech_input(
                request.session_id,
                request.text
            )
            
            return result
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro no processamento de voz: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno no processamento: {str(e)}"
            )
    
    return router
