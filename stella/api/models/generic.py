from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BaseRequest(BaseModel):
    """Classe base para todas as requisições com campos comuns"""
    session_id: str = Field(..., description="ID da sessão ativa")
    correlation_id: Optional[str] = Field(None, description="ID para rastreamento")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da requisição")

class BaseResponse(BaseModel):
    """Classe base para todas as respostas com campos comuns"""
    session_id: str = Field(..., description="ID da sessão ativa")
    correlation_id: str = Field(..., description="ID para rastreamento")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
class APIBaseResponse(BaseModel):
    """
    Response padrão para endpoints que processam assincronamente
    e retornam resultado via WebSocket
    """
    status: str = Field(default="accepted", description="Status da requisição (accepted/error)")
    correlation_id: str = Field(..., description="ID para rastreamento da resposta no WebSocket")
    message: Optional[str] = Field(None, description="Mensagem adicional (opcional)")