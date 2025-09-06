"""
Serviço de gerenciamento de sessões
"""
import uuid
from loguru import logger
from stella.api.models import SessionEndRequest, SessionEndResponse, SessionStartResponse, SessionStartRequest
from stella.agent.speech_processor import end_session as end_speech_session

class SessionService:
    """Serviço responsável pelo gerenciamento de sessões de usuário"""
    
    @staticmethod
    def start_new_session(request: SessionStartRequest) -> SessionStartResponse:
        """
        Inicia uma nova sessão de usuário
        
        Returns:
            SessionStartResponse com dados da nova sessão
        """
        try:
            if not request.session_id:
                session_id = str(uuid.uuid4())
            else:
                session_id = request.session_id
                
            logger.info(f"🚀 Nova sessão criada: {session_id}")
            
            return SessionStartResponse(
                success=True,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar sessão: {e}")
            return SessionStartResponse(
                success=False,
                session_id=session_id,
            )

    def end_session(request: SessionEndRequest) -> SessionEndResponse:
        """
        Finaliza uma sessão específica
        
        Args:
            session_id: ID da sessão a ser finalizada
            
        Returns:
            SessionEndRequest confirmando o encerramento
        """
        try:
            session_id = request.session_id
            
            session_ended = end_speech_session(session_id)
            
            if session_ended:
                logger.info(f"🔚 Sessão encerrada: {session_id}")
                message = "Sessão encerrada com sucesso. Até logo!"
            else:
                logger.warning(f"⚠️ Sessão não encontrada: {session_id}")
                message = "Sessão não encontrada, mas processamento finalizado."

            return SessionEndResponse(
                success=True,
                session_id=session_id
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar sessão {session_id}: {e}")
            return SessionEndResponse(
                success=False,
                session_id=session_id
            )
