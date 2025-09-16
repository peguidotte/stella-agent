"""
Serviço de autenticação Pusher para a API Stella
"""
from loguru import logger
from typing import Dict, Any
from stella.api.models import APIBaseResponse
from stella.websocket.websocket_manager import authenticate_channel

class AuthService:
    """Serviço responsável pela autenticação de canais Pusher"""
    
    @staticmethod
    def authenticate_pusher_channel(channel_name: str, socket_id: str) -> Dict[str, Any]:
        """
        Autentica canal privado do Pusher
        
        Args:
            channel_name: Nome do canal para autenticação
            socket_id: ID do socket Pusher
            
        Returns:
            Dict com dados de utenticação
        """
        try:
            logger.info(f"🔐 Autenticando canal: {channel_name} para socket: {socket_id}")
            
            # Aqui você poderia validar o usuário, mas no teste liberamos
            auth_data = authenticate_channel(channel_name, socket_id)

            logger.success(f"✅ Canal {channel_name} autenticado com sucesso")
            return auth_data
            
        except Exception as e:
            logger.error(f"❌ Erro na autenticação do canal {channel_name}: {e}")
            raise
