"""
Gerenciador de Sessões do Stella

Controla o estado das sessões de usuário e fluxos das HUs:
- HU-01: Autenticação de usuário
- HU-02: Solicitação de retirada 
- HU-03: Validação de retirada
"""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass


class SessionState(Enum):
    """Estados possíveis de uma sessão"""
    IDLE = "idle"
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    REQUESTING_WITHDRAWAL = "requesting_withdrawal"
    VALIDATING_WITHDRAWAL = "validating_withdrawal"
    LOCKED = "locked"


@dataclass
class WithdrawalRequest:
    """Representa uma solicitação de retirada"""
    items: Dict[str, int]  # {produto: quantidade}
    user_name: str
    timestamp: datetime
    confirmed: bool = False


@dataclass
class UserSession:
    """Sessão de usuário ativa"""
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    face_encoding: Optional[Any] = None  # Encoding facial do usuário
    state: SessionState = SessionState.IDLE
    pin_attempts: int = 0
    face_id_attempts: int = 0
    created_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    withdrawal_request: Optional[WithdrawalRequest] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()


class SessionManager:
    """Gerenciador de sessões e estado da aplicação"""
    
    def __init__(self):
        self.current_session: Optional[UserSession] = None
        self.is_locked = False
        self.lock_until: Optional[datetime] = None
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Inicia o gerenciador de sessões"""
        # Inicia task de limpeza periódica
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def stop(self):
        """Para o gerenciador de sessões"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    def create_session(self) -> UserSession:
        """
        Cria uma nova sessão de usuário
        
        Returns:
            Nova sessão criada
        """
        if self.is_system_locked():
            raise ValueError("Sistema está bloqueado para autenticação")
        
        self.current_session = UserSession()
        return self.current_session
    
    def get_current_session(self) -> Optional[UserSession]:
        """Retorna a sessão atual, se existir"""
        return self.current_session
    
    def update_session_activity(self):
        """Atualiza timestamp da última atividade da sessão"""
        if self.current_session:
            self.current_session.last_activity = datetime.now()
    
    def set_session_state(self, state: SessionState):
        """
        Define o estado da sessão atual
        
        Args:
            state: Novo estado da sessão
        """
        if self.current_session:
            self.current_session.state = state
            self.update_session_activity()
    
    def authenticate_user(self, user_name: str, face_encoding: Any = None) -> bool:
        """
        Autentica um usuário na sessão atual
        
        Args:
            user_name: Nome do usuário
            face_encoding: Encoding facial (opcional)
            
        Returns:
            True se autenticação foi bem-sucedida
        """
        if not self.current_session:
            return False
        
        self.current_session.user_name = user_name
        self.current_session.face_encoding = face_encoding
        self.current_session.state = SessionState.AUTHENTICATED
        self.update_session_activity()
        
        return True
    
    def increment_pin_attempts(self) -> int:
        """
        Incrementa tentativas de PIN
        
        Returns:
            Número atual de tentativas
        """
        if self.current_session:
            self.current_session.pin_attempts += 1
            return self.current_session.pin_attempts
        return 0
    
    def increment_face_id_attempts(self) -> int:
        """
        Incrementa tentativas de Face ID
        
        Returns:
            Número atual de tentativas
        """
        if self.current_session:
            self.current_session.face_id_attempts += 1
            return self.current_session.face_id_attempts
        return 0
    
    def create_withdrawal_request(self, items: Dict[str, int]) -> bool:
        """
        Cria uma nova solicitação de retirada
        
        Args:
            items: Dicionário de itens {produto: quantidade}
            
        Returns:
            True se solicitação foi criada
        """
        if not self.current_session or self.current_session.state != SessionState.AUTHENTICATED:
            return False
        
        if self.current_session.withdrawal_request:
            # Já existe uma solicitação ativa
            return False
        
        self.current_session.withdrawal_request = WithdrawalRequest(
            items=items,
            user_name=self.current_session.user_name or "Unknown",
            timestamp=datetime.now()
        )
        
        self.set_session_state(SessionState.REQUESTING_WITHDRAWAL)
        return True
    
    def confirm_withdrawal_request(self) -> bool:
        """
        Confirma a solicitação de retirada atual
        
        Returns:
            True se confirmação foi bem-sucedida
        """
        if (not self.current_session or 
            not self.current_session.withdrawal_request or
            self.current_session.state != SessionState.REQUESTING_WITHDRAWAL):
            return False
        
        self.current_session.withdrawal_request.confirmed = True
        self.set_session_state(SessionState.VALIDATING_WITHDRAWAL)
        return True
    
    def complete_withdrawal(self) -> bool:
        """
        Completa a retirada após validação
        
        Returns:
            True se retirada foi completada
        """
        if (not self.current_session or 
            not self.current_session.withdrawal_request or
            self.current_session.state != SessionState.VALIDATING_WITHDRAWAL):
            return False
        
        # Limpa a solicitação e volta para autenticado
        self.current_session.withdrawal_request = None
        self.set_session_state(SessionState.AUTHENTICATED)
        return True
    
    def lock_system(self, duration_minutes: int = 30):
        """
        Bloqueia o sistema por um período
        
        Args:
            duration_minutes: Duração do bloqueio em minutos
        """
        self.is_locked = True
        self.lock_until = datetime.now() + timedelta(minutes=duration_minutes)
        
        # Encerra sessão atual se existir
        if self.current_session:
            self.current_session.state = SessionState.LOCKED
    
    def unlock_system(self):
        """Desbloqueia o sistema manualmente"""
        self.is_locked = False
        self.lock_until = None
    
    def is_system_locked(self) -> bool:
        """
        Verifica se o sistema está bloqueado
        
        Returns:
            True se sistema está bloqueado
        """
        if not self.is_locked:
            return False
        
        if self.lock_until and datetime.now() >= self.lock_until:
            # Bloqueio expirou
            self.unlock_system()
            return False
        
        return True
    
    def end_session(self):
        """Encerra a sessão atual"""
        self.current_session = None
    
    async def _periodic_cleanup(self):
        """Task de limpeza periódica"""
        while True:
            try:
                await asyncio.sleep(60)  # Verifica a cada minuto
                
                # Verifica se o bloqueio expirou
                if self.is_system_locked():
                    continue
                
                # Verifica timeout de sessão (ex: 30 minutos de inatividade)
                if self.current_session and self.current_session.last_activity:
                    inactive_time = datetime.now() - self.current_session.last_activity
                    if inactive_time > timedelta(minutes=30):
                        self.end_session()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Erro na limpeza periódica: {e}")
