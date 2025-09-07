"""
Rotas de autenticação Pusher
"""
from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from stella.api.models import AuthRequest
from stella.api.services.auth import AuthService

def create_auth_router() -> APIRouter:
    """
    Cria API router de autenticação com Pusher
    """
    router = APIRouter(prefix="/auth", tags=["Autenticação"])
    auth_service = AuthService()

    @router.post("/pusher")
    async def authenticate_pusher(request: AuthRequest = Depends(AuthRequest.as_form)):
        """
        Endpoint para autenticação de canal privado do Pusher
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
            
            return auth_data
            
        except HTTPException:
            raise  # Re-raise HTTP exceptions
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno na autenticação: {str(e)}"
            )
    
    return router
