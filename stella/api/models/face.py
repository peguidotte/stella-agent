"""
Modelo Pydantic para endpoint "speech" da API
"""
from pydantic import Field, field_validator, model_validator
from typing import Optional
import base64
from stella.api.models.generic import BaseRequest, BaseResponse

class FaceAuthRequest(BaseRequest):
    encoding: str = Field(..., min_length=1, description="Encoding base64 da imagem facial")
    attempt: int = Field(..., ge=1, le=10, description="Número da tentativa (1-10)")

    @field_validator("attempt")
    @classmethod
    def validate_attempt(cls, v):
        if v is None:
            raise ValueError("O campo 'attempt' é obrigatório.")
        if v < 1:
            raise ValueError("O campo 'attempt' deve ser no mínimo 1.")
        if v > 10:
            raise ValueError("O campo 'attempt' deve ser no máximo 10.")
        return v

class FaceAuthResponse(BaseResponse):
    user_exists: bool = Field(..., description="Indica se o usuário existe")
    user_id: Optional[str] = Field(None, description="ID do usuário (enviado apenas se user_exists=True)")

    @model_validator(mode='after')
    def validate_user_consistency(self):
        if self.user_exists and not self.user_id:
            raise ValueError("user_id é obrigatório quando user_exists=True.")
        if not self.user_exists and self.user_id is not None:
            raise ValueError("user_id não deve ser enviado quando user_exists=False.")
        return self

class FaceCadRequest(BaseRequest):
    encoding: str = Field(..., min_length=1, description="Encoding base64 da imagem facial")
    user_name: str = Field(..., description="Nome do usuário")
    pin: int = Field(..., description="PIN númerico que deve bater com PIN configurado na STELLA")
    
    @field_validator("encoding")
    @classmethod
    def validate_encoding(cls, v):
        try:
            if ',' in v:
                v = v.split(',')[1]
            
            decoded = base64.b64decode(v, validate=True)
            
            if len(decoded) < 100:
                raise ValueError("Imagem muito pequena.")
            if len(decoded) > 5 * 1024 * 1024:
                raise ValueError("Imagem muito grande (máx 5MB).")
                
            return v
        except Exception:
            raise ValueError("Encoding base64 inválido.")
        
class FaceCadResponse(BaseResponse):
    success: bool = Field(..., description="Indica se o cadastro foi bem-sucedido")
    message: Optional[str] = Field(None, description="Mensagem adicional sobre o cadastro")
    