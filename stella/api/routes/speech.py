"""
Rotas de processamento de voz
"""

import asyncio
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models import SpeechRequest, SpeechResponse, APIBaseResponse
from stella.api.services.speech import SpeechService

def create_speech_router() -> APIRouter:
    """
    Cria API router de processamento de voz
    """
    router = APIRouter(prefix="/speech", tags=["Processamento de Voz"])
    
    @router.post("/process", response_model=APIBaseResponse)
    async def process_speech(request: SpeechRequest):
        """
        Processa entrada de voz usando IA com contexto de sessão, assíncronamente envia resultado via WebSocket e retorna confirmação imediata
        
        Args:
            request: Dados da Request
            
        Returns:
            APIBaseResponse com resultado do processamento
        """

        try:
            logger.info(f"🗣️ Processando fala para sessão: {request.session_id}")
            
            # Valida entrada
            if not request.data.text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Texto não pode estar vazio"
                )
            
            if len(request.data.text) > 250:
                raise HTTPException(
                    status_code=400,
                    detail="Texto muito longo (máximo 250 caracteres)"
                )
            
            asyncio.create_task(SpeechService.process_speech_async(request))

            return APIBaseResponse(
                status="accepted",
                correlation_id=request.correlation_id,
                message="Processamento de voz iniciado, resultado será enviado via WebSocket"
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de voz: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno no processamento: {str(e)}"
            )
    
    return router
