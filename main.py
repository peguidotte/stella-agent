"""
Stella Agent - Sistema de Assistente Virtual com IA
Servidor principal FastAPI com arquitetura organizada
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import os
from datetime import datetime

# Importações dos componentes da API
from stella.websocket.websocket_manager import WebSocketManager
from stella.api.routes import (
    create_auth_router,
    create_speech_router,
    create_face_router,
    create_session_router
)

# Configuração da aplicação FastAPI
app = FastAPI(
    title="Stella Agent API",
    description="Sistema de Assistente Virtual com IA, reconhecimento facial e comunicação WebSocket",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Inicialização do WebSocket Manager
websocket_manager = WebSocketManager()

# Inclusão das rotas organizadas
app.include_router(create_auth_router(websocket_manager))
app.include_router(create_speech_router(websocket_manager))
app.include_router(create_face_router(websocket_manager))
app.include_router(create_session_router(websocket_manager))

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint principal com informações do sistema
    
    Returns:
        Dict com status e informações da API
    """
    return {
        "service": "Stella Agent API",
        "status": "running",
        "version": "1.0.0",
        "description": "Sistema de Assistente Virtual com IA",
        "features": {
            "pusher_websocket": "Comunicação em tempo real",
            "gemini_ai": "Processamento de linguagem natural",
            "face_recognition": "Reconhecimento facial",
            "session_management": "Gerenciamento de sessões com contexto"
        },
        "pusher_cluster": os.getenv('PUSHER_CLUSTER', 'us2'),
        "endpoints": {
            "docs": "/docs",
            "health": "/session/health",
            "auth": "/auth/pusher",
            "session_start": "/session/start",
            "session_end": "/session/end",
            "speech_process": "/speech/process",
            "face_recognize": "/face/recognize"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando Stella Agent...")
    logger.info("📚 Documentação da API: http://localhost:8000/docs")
    logger.info("🔍 Redoc: http://localhost:8000/redoc")
    logger.info("💻 Endpoints principais:")
    logger.info("   POST /session/start - Iniciar nova sessão")
    logger.info("   POST /speech/process - Processar fala")
    logger.info("   POST /face/recognize - Reconhecimento facial")
    logger.info("   POST /auth/pusher - Autenticação Pusher")
    logger.info("   GET /session/health - Status da API")
    logger.info("")
    logger.info("🔄 Fluxo: HTTP POST → IA/Processamento → WebSocket Response")
    logger.info("📡 WebSocket: Pusher channels para comunicação em tempo real")

    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("🛑 Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
    finally:
        logger.info("👋 Stella Agent finalizado")