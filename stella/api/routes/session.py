"""
Rotas de gerenciamento de sessões
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models.requests import SessionEndRequest
from stella.api.models.responses import StandardResponse, SessionStartResponse, HealthResponse
from stella.api.services.session import SessionService

def create_session_router(websocket_manager) -> APIRouter:
    """
    Cria router de sessões com dependência do WebSocketManager
    
    Args:
        websocket_manager: Instância do WebSocketManager
        
    Returns:
        APIRouter configurado para gerenciamento de sessões
    """
    router = APIRouter(prefix="/session", tags=["Gerenciamento de Sessões"])
    session_service = SessionService(websocket_manager)
    
    @router.post("/start", response_model=SessionStartResponse)
    async def start_session():
        """
        Inicia uma nova sessão de usuário
        
        Returns:
            SessionStartResponse com dados da nova sessão
        """
        try:
            logger.info("🚀 Solicitação para iniciar nova sessão")
            
            result = session_service.start_new_session()
            
            if result.success:
                logger.success(f"✅ Sessão criada: {result.data.get('session_id')}")
            else:
                logger.error(f"❌ Falha ao criar sessão: {result.message}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sessão: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao iniciar sessão: {str(e)}"
            )
    
    @router.post("/end", response_model=StandardResponse)
    async def end_session(request: SessionEndRequest):
        """
        Finaliza uma sessão específica
        
        Args:
            request: Dados da solicitação (session_id)
            
        Returns:
            StandardResponse confirmando o encerramento
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
    
    @router.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Endpoint de verificação de saúde da API
        
        Returns:
            HealthResponse com status da API
        """
        try:
            # Faz limpeza de sessões expiradas como parte do health check
            cleaned_count = session_service.cleanup_expired_sessions()
            
            return HealthResponse(
                success=True,
                message="API funcionando normalmente",
                data={
                    "status": "healthy",
                    "expired_sessions_cleaned": cleaned_count,
                    "timestamp": session_service._get_current_timestamp()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no health check: {e}")
            return HealthResponse(
                success=False,
                message="Problemas detectados na API",
                data={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": session_service._get_current_timestamp()
                }
            )
    
    return router
