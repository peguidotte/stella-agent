"""
Modelos Pydantic para validação de requests e responses da API Stella
"""

from stella.api.models.speech import (
    SpeechResponse,
    UserIntentions,
    StellaAnalysis,
    StellaSpeechResponse,
    SpeechRequest,
    SpeechDataRequest
)

from stella.api.models.face import (
    FaceAuthRequest,
    FaceAuthResponse,
    FaceCadResponse,
    FaceCadRequest
)

from stella.api.models.auth import (
    AuthRequest,
    AuthResponse
)

from stella.api.models.session import (
    SessionStartRequest,
    SessionStartResponse,
    SessionEndRequest,
    SessionEndResponse
)

from stella.api.models.generic import APIBaseResponse

__all__ = [
    # Speech models
    "SpeechRequest",
    "SpeechResponse",
    "StellaSpeechResponse",
    "StellaAnalysis",
    "UserIntentions",
    "SpeechDataRequest",

    # Face models
    "FaceAuthRequest",
    "FaceAuthResponse",
    "FaceCadRequest",
    "FaceCadResponse",
    
    # Auth models
    "AuthRequest",
    "AuthResponse",
    
    # Session models
    "SessionStartRequest",
    "SessionStartResponse",
    "SessionEndRequest",
    "SessionEndResponse"
    
    # Generic models
    "APIBaseResponse"
]