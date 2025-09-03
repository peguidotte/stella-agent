"""
Modelos Pydantic para respostas da API Stella
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class StandardResponse(BaseModel):
    status: str = Field(..., description="Status da operação")
    correlation_id: str = Field(..., description="ID de rastreamento")
    message: str = Field(..., description="Mensagem descritiva")
    timestamp: str = Field(..., description="Timestamp da resposta")
    session_id: Optional[str] = Field(None, description="ID da sessão")

class SessionStartResponse(BaseModel):
    session_id: str = Field(..., description="ID da nova sessão")
    channel: str = Field(..., description="Canal Pusher para esta sessão")
    status: str = Field(..., description="Status da sessão")
    timestamp: str = Field(..., description="Timestamp de criação")

class SessionEndResponse(BaseModel):
    status: str = Field(..., description="Status da operação")
    session_id: str = Field(..., description="ID da sessão encerrada")
    timestamp: str = Field(..., description="Timestamp do encerramento")

class AuthResponse(BaseModel):
    auth: str = Field(..., description="Token de autenticação Pusher")
    channel_data: Optional[Dict[str, Any]] = Field(None, description="Dados do canal")

class HealthResponse(BaseModel):
    service: str = Field(..., description="Nome do serviço")
    status: str = Field(..., description="Status do servidor")
    pusher_cluster: str = Field(..., description="Cluster Pusher configurado")
    supported_events: list = Field(..., description="Eventos suportados")
    auth_endpoint: str = Field(..., description="Endpoint de autenticação")
    api_endpoints: Dict[str, str] = Field(..., description="Endpoints disponíveis")
    timestamp: str = Field(..., description="Timestamp da resposta")
    timestamp: datetime = Field(..., description="Timestamp do encerramento")