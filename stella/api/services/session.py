"""
Serviço de gerenciamento de sessões
"""
import uuid
from loguru import logger
from typing import Dict, Any, Optional
from stella.api.models.responses import StandardResponse, SessionStartResponse
from stella.core.session_manager import SessionManager

class SessionService:
    """Serviço responsável pelo gerenciamento de sessões de usuário"""
    
    def __init__(self, websocket_manager):
        self.websocket_manager = websocket_manager
        self.session_manager = SessionManager()
    
    def start_new_session(self) -> SessionStartResponse:
        """
        Inicia uma nova sessão de usuário
        
        Returns:
            SessionStartResponse com dados da nova sessão
        """
        try:
            # Gera ID único para a sessão
            session_id = str(uuid.uuid4())
            
            # Cria sessão no manager
            self.session_manager.create_session(session_id)
            
            logger.info(f"🚀 Nova sessão criada: {session_id}")
            
            return SessionStartResponse(
                success=True,
                message="Sessão iniciada com sucesso",
                data={
                    "session_id": session_id,
                    "channel_name": f"private-session-{session_id}",
                    "timestamp": self._get_current_timestamp()
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar sessão: {e}")
            return SessionStartResponse(
                success=False,
                message="Erro ao iniciar sessão",
                data={"error": str(e)}
            )
    
    def end_session(self, session_id: str) -> StandardResponse:
        """
        Finaliza uma sessão específica
        
        Args:
            session_id: ID da sessão a ser finalizada
            
        Returns:
            StandardResponse confirmando o encerramento
        """
        try:
            # Remove sessão do manager
            self.session_manager.remove_session(session_id)
            
            # Notifica via WebSocket sobre encerramento
            channel_name = f"private-session-{session_id}"
            self.websocket_manager.send_message(
                channel_name,
                "session_ended",
                {
                    "message": "Sessão encerrada",
                    "session_id": session_id,
                    "timestamp": self._get_current_timestamp()
                }
            )
            
            logger.info(f"🔚 Sessão encerrada: {session_id}")
            
            return StandardResponse(
                success=True,
                message="Sessão encerrada com sucesso",
                data={"session_id": session_id}
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar sessão {session_id}: {e}")
            return StandardResponse(
                success=False,
                message="Erro ao encerrar sessão",
                data={"error": str(e)}
            )
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna informações de uma sessão específica
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Dict com informações da sessão ou None se não encontrada
        """
        try:
            session_data = self.session_manager.get_session(session_id)
            if session_data:
                return {
                    "session_id": session_id,
                    "created_at": session_data.get("created_at"),
                    "last_activity": session_data.get("last_activity"),
                    "is_active": True
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações da sessão {session_id}: {e}")
            return None
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove sessões expiradas
        
        Returns:
            Número de sessões removidas
        """
        try:
            removed_count = self.session_manager.cleanup_expired_sessions()
            if removed_count > 0:
                logger.info(f"🧹 {removed_count} sessões expiradas removidas")
            return removed_count
            
        except Exception as e:
            logger.error(f"❌ Erro na limpeza de sessões: {e}")
            return 0
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual em formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
