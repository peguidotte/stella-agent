"""
Modelos Pydantic para requisições de entrada da API Stella
"""
from pydantic import BaseModel, Field
from typing import Optional

class SpeechData(BaseModel):
    text: str = Field(..., min_length=1, description="Texto transcrito do speech")
    userId: Optional[str] = Field(None, description="ID do usuário que fez a solicitação")

class SpeechRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão ativa")
    correlation_id: Optional[str] = Field(None, description="ID para rastreamento da requisição")
    data: SpeechData = Field(..., description="Dados do speech")

class FaceData(BaseModel):
    encoding: str = Field(..., min_length=1, description="Encoding base64 da imagem facial")
    userId: Optional[str] = Field(None, description="ID do usuário esperado")

class FaceRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão ativa")
    correlation_id: Optional[str] = Field(None, description="ID para rastreamento da requisição")
    data: FaceData = Field(..., description="Dados do reconhecimento facial")

class SessionEndRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão a ser encerrada")

class AuthRequest(BaseModel):
    channel_name: str = Field(..., description="Nome do canal Pusher para autenticação")
    socket_id: str = Field(..., description="ID do socket Pusher")
    session_id: str = Field(..., description="ID da sessão a ser encerrada")