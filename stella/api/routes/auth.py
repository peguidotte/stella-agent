"""
Rotas de autenticação Pusher
"""
from fastapi import APIRouter, HTTPException
from loguru import logger
from stella.api.models.requests import AuthRequest
from stella.api.models.responses import AuthResponse
from stella.api.services.auth import AuthService

def create_auth_router(websocket_manager) -> APIRouter:
    """
    Cria router de autenticação com dependência do WebSocketManager
    
    Args:
        websocket_manager: Instância do WebSocketManager
        
    Returns:
        APIRouter configurado para autenticação
    """
    router = APIRouter(prefix="/auth", tags=["Autenticação"])
    auth_service = AuthService(websocket_manager)
    
    @router.post("/pusher", response_model=AuthResponse)
    async def authenticate_pusher(request: AuthRequest):
        """
        Endpoint para autenticação de canais privados do Pusher
        
        Args:
            request: Dados de autenticação (channel_name, socket_id)
            
        Returns:
            AuthResponse com dados de autenticação ou erro
        """
        try:
            logger.info(f"🔐 Solicitação de autenticação para canal: {request.channel_name}")
            
            # Valida formato do canal
            if not request.channel_name.startswith("private-"):
                raise HTTPException(
                    status_code=400,
                    detail="Canal deve ser privado (começar com 'private-')"
                )
            
            # Autentica o canal
            auth_data = auth_service.authenticate_pusher_channel(
                request.channel_name,
                request.socket_id
            )
            
            return AuthResponse(
                success=True,
                message="Canal autenticado com sucesso",
                data=auth_data
            )
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno na autenticação: {str(e)}"
            )
    
    return router
