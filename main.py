"""
Stella Agent - Sistema de Assistente Virtual com IA
Servidor principal FastAPI com arquitetura organizada
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from datetime import datetime

from stella.api.routes import (
    create_auth_router,
    create_speech_router,
    create_face_router,
    create_session_router
)
from stella.config.settings import settings

# Configuração da aplicação FastAPI
app = FastAPI(
    title="Stella Agent API",
    description="Sistema de Assistente Virtual com IA, reconhecimento facial e comunicação WebSocket. Para ter acesso as responses em chamadas que envolvem websocket, acesse o markdown 'AYNC_RESPONSES' na raiz do projeto.",
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

# Inclusão das rotas organizadas
app.include_router(create_auth_router())
app.include_router(create_speech_router())
app.include_router(create_face_router())
app.include_router(create_session_router())

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
        "pusher_cluster": settings.pusher_cluster,
        "endpoints": {
        "docs": "/docs",
            "auth": "/auth/pusher",
            "session_start": "/session/start",
            "session_end": "/session/end",
            "speech_process": "/speech/process",
            "face_recognize": "/face/recognize",
            "face_register": "/face/register"
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
    logger.info("   POST /session/end - Encerrar sessão")
    logger.info("   POST /speech/process - Processar fala")
    logger.info("   POST /face/recognize - Reconhecimento facial")
    logger.info("   POST /face/register - Cadastrar novo usuário facial")
    logger.info("   POST /auth/pusher - Autenticação Pusher")
    logger.info("")
    logger.info("🔄 Fluxo: HTTP POST → IA/Processamento → WebSocket Response")

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