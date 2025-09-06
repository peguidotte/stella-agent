"""
Modelo Pydantic para endpoint "speech" da API
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from stella.api.models.generic import BaseRequest, BaseResponse

class UserIntentions(str, Enum):
    withdraw_request = "withdraw_request"
    withdraw_confirm = "withdraw_confirm"
    doubt = "doubt"
    stock_query = "stock_query"
    not_understood = "not_understood"
    error = "error"

class StellaAnalysis(str, Enum):
    normal = "normal"
    low_stock_alert = "low_stock_alert"
    critical_stock_alert = "critical_stock_alert"
    outlier_withdraw_request = "outlier_withdraw_request"
    ambiguous = "ambiguous"
    not_understood = "not_understood"
    safety_check = "safety_check"
    greeting = "greeting"
    farewell = "farewell"
    error = "error"

class StellaSpeechResponse(BaseModel):
    intention: UserIntentions = Field(..., description="Intenção interpretada do usuário")
    items: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Lista de itens (ex: [{'item':'seringa_10ml','quantidade':5}])"
    )
    response: str = Field(..., description="Resposta natural gerada pela Stella")
    stella_analysis: StellaAnalysis = Field(default="normal", description="Classificação interna para estilização no front")
    reason: Optional[str] = Field(
        default=None,
        description="Breve justificativa da análise (ex: 'quantidade 5x acima da média')."
    )

class SpeechResponse(BaseResponse):
    data: StellaSpeechResponse
    
class SpeechDataRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Texto transcrito do speech")
    userId: Optional[str] = Field(None, description="ID do usuário que fez a solicitação")

class SpeechRequest(BaseRequest):
    data: SpeechDataRequest = Field(..., description="Dados do speech")