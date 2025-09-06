"""
Modelos Pydantic para endpoints "auth" da API Stella
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from fastapi import Form

class AuthRequest(BaseModel):
    channel_name: str = Field(..., description="Nome do canal Pusher para autenticação")
    socket_id: str = Field(..., description="ID do socket Pusher")

    @classmethod
    def as_form(
        cls,
        channel_name: str = Form(...),
        socket_id: str = Form(...),
        session_id: str = Form(...)
    ):
        return cls(
            channel_name=channel_name,
            socket_id=socket_id,
            session_id=session_id
        )

class AuthResponse(BaseModel):
    success: bool = Field(..., description="Indica se a autenticação foi bem-sucedida")
    message: Optional[str] = Field(..., description="Mensagem descritiva")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")