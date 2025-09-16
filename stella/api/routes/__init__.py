"""
Pacote de rotas da API Stella
"""
from stella.api.routes.auth import create_auth_router
from stella.api.routes.speech import create_speech_router
from stella.api.routes.face import create_face_router
from stella.api.routes.session import create_session_router

__all__ = [
    "create_auth_router",
    "create_speech_router", 
    "create_face_router",
    "create_session_router"
]