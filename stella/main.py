from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from datetime import datetime
import uuid
import os
from websocket.websocket_manager import WebSocketManager


app = FastAPI(title="Stella Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Instância global do agent
stella_socket = WebSocketManager()

@app.post("/pusher/auth")
async def pusher_auth(channel_name: str = Form(...), socket_id: str = Form(...)):
    """
    Autentica canais privados do Pusher
    Endpoint necessário para canais private-*
    """
    try:
        logger.info(f"🔐 Requisição de autenticação: canal={channel_name}, socket={socket_id}")
        
        # Aqui você poderia validar o usuário, mas no teste a gente só libera:
        auth = stella_socket.authenticate_channel(channel_name, socket_id)
        
        return JSONResponse(content=auth)
        
    except Exception as e:
        logger.error(f"❌ Erro na autenticação: {e}")
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/test/speech")
async def test_speech():
    """Endpoint para testar speech output"""
    stella_socket.test_send_speech_output()
    return {"status": "success", "message": "Test speech output sent"}

@app.get("/test/face")
async def test_face():
    """Endpoint para testar face output"""
    stella_socket.test_send_face_output()
    return {"status": "success", "message": "Test face output sent"}

@app.post("/api/speech")
async def api_speech(request: Request):
    """
    Recebe mensagem de speech via HTTP POST do front-end
    Processa e envia resposta via Pusher WebSocket
    """
    try:
        data = await request.json()
        correlation_id = data.get('correlation_id', str(uuid.uuid4()))
        
        logger.info(f"📥 Recebida mensagem speech via HTTP: {correlation_id}")
        
        # Processa usando o handler
        result = stella_socket.handle_speech_input(data, stella_socket.default_channel)
        
        return {
            "status": "success",
            "correlation_id": correlation_id,
            "message": "Speech processado e resposta enviada via Pusher",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro processando speech via HTTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/face")
async def api_face(request: Request):
    """
    Recebe mensagem de face recognition via HTTP POST do front-end
    Processa e envia resposta via Pusher WebSocket
    """
    try:
        data = await request.json()
        correlation_id = data.get('correlation_id', str(uuid.uuid4()))
        
        logger.info(f"📥 Recebida mensagem face via HTTP: {correlation_id}")
        
        # Processa usando o handler
        result = stella_socket.handle_face_input(data, stella_socket.default_channel)
        
        return {
            "status": "success",
            "correlation_id": correlation_id,
            "message": "Face processado e resposta enviada via Pusher",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro processando face via HTTP: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test/auth")
async def test_auth():
    """Testa autenticação com dados mock"""
    try:
        test_channel = "private-agent-123"
        test_socket_id = "123456.7890123"
        
        auth = stella_socket.authenticate_channel(test_channel, test_socket_id)
        
        return {
            "status": "success", 
            "message": "Autenticação testada com sucesso",
            "auth": auth,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro testando auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Status do servidor e endpoints disponíveis"""
    return {
        "service": "Stella Pusher HTTP + WebSocket Server",
        "status": "running",
        "pusher_cluster": os.environ.get('PUSHER_CLUSTER', 'us2'),
        "supported_events": list(stella_socket.event_handlers.keys()),
        "auth_endpoint": "/pusher/auth",
        "api_endpoints": {
            "speech": "POST /api/speech",
            "face": "POST /api/face",
            "test_speech": "GET /test/speech",
            "test_face": "GET /test/face",
            "test_auth": "GET /test/auth"
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Iniciando Stella...")
    logger.info("Auth endpoint: http://localhost:8000/pusher/auth")
    logger.info("API endpoints:")
    logger.info("   POST http://localhost:8000/api/speech")
    logger.info("   POST http://localhost:8000/api/face")
    logger.info("Test endpoints:")
    logger.info("   GET http://localhost:8000/test/speech")
    logger.info("   GET http://localhost:8000/test/face")
    logger.info("   GET http://localhost:8000/test/auth")
    logger.info("Fluxo: Front HTTP POST → Back processa → Pusher WebSocket → Front")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Servidor encerrado")