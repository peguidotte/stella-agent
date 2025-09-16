from pydantic import BaseModel, Field

class SessionStartRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão a ser criada")

class SessionEndRequest(BaseModel):
    session_id: str = Field(..., description="ID da sessão a ser encerrada")
    
class SessionStartResponse(BaseModel):
    success: bool = Field(..., description="Indica se a sessão foi criada com sucesso")
    session_id: str = Field(..., description="ID da nova sessão criada")
    
class SessionEndResponse(BaseModel):
    success: bool = Field(..., description="Indica se a sessão foi encerrada com sucesso")
    session_id: str = Field(..., description="ID da sessão encerrada")