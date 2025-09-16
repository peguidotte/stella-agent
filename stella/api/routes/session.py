"""
Rotas de gerenciamento de sessões
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models import SessionEndRequest, SessionStartRequest, SessionEndResponse, SessionStartResponse
from stella.api.services.session import SessionService

def create_session_router() -> APIRouter:
    """
    Cria API router de sessões
    """
    router = APIRouter(prefix="/session", tags=["Gerenciamento de Sessões"])
    session_service = SessionService()
    
    @router.post("/start", response_model=SessionStartResponse)
    async def start_session(request: SessionStartRequest):
        """
        Inicia uma nova sessão
        """
        try:
            logger.info("🚀 Solicitação para iniciar nova sessão")
            
            result = session_service.start_new_session(request)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sessão: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao iniciar sessão: {str(e)}"
            )
    
    @router.post("/end", response_model=SessionEndResponse)
    async def end_session(request: SessionEndRequest):
        """
        Finaliza uma sessão específica
        """
        try:
            logger.info(f"🔚 Solicitação para encerrar sessão: {request.session_id}")
            
            # Valida se session_id não está vazio
            if not request.session_id.strip():
                raise HTTPException(
                    status_code=400,
                    detail="ID da sessão não pode estar vazio"
                )
            
            result = session_service.end_session(request.session_id)
            
            return result
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar sessão: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao encerrar sessão: {str(e)}"
            )
            
    return router