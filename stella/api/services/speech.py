"""
Serviço de processamento de voz e interação com IA
"""
import asyncio
from datetime import datetime
from loguru import logger
from pydantic import ValidationError
from stella.api.models import SpeechRequest, SpeechResponse, StellaSpeechResponse
from stella.agent.speech_processor import command_interpreter
from stella.websocket.websocket_manager import send_event, get_default_channel

class SpeechService:
    """Serviço responsável pelo processamento de voz e interação com IA"""
    
    @staticmethod
    async def process_speech_async(request: SpeechRequest):
        """
        Processa entrada de voz assincronamente e envia via WebSocket
        """
        try:
            logger.info(f"🗣️ Processando async | Sessão: {request.session_id} | Corr: {request.correlation_id}")

            ai_response = await command_interpreter(
                request.data.text,
                request.session_id
            )
            
            if ai_response:
                
                try:
                    speech_response = SpeechResponse(
                        session_id=request.session_id,
                        correlation_id=request.correlation_id,
                        timestamp=datetime.now(),
                        data=ai_response 
                    )
                    
                    send_event(
                        channel=get_default_channel(),
                        event="server-speech-output",
                        data=speech_response.model_dump()
                    )
                    
                    logger.success(f"✅ Resposta validada e enviada | Sessão: {request.session_id}")
                    
                except ValidationError as ve:
                    logger.error(f"❌ Erro de validação na resposta: {ve}")
                    await SpeechService._send_validation_error(request.session_id, request.correlation_id, ve)

            else:
                logger.warning(f"⚠️ IA retornou resposta vazia")
                await SpeechService._send_empty_response(request.session_id, request.correlation_id)

        except Exception as e:
            logger.error(f"❌ Erro no processamento: {e}")
            await SpeechService._send_processing_error(request.session_id, request.correlation_id, e)

    @staticmethod
    async def _send_validation_error(session_id: str, correlation_id: str, validation_error: ValidationError):
        """Envia erro de validação via WebSocket"""
        try:
            error_response = SpeechResponse(
                session_id=session_id,
                correlation_id=correlation_id,
                timestamp=datetime.now(),
                data=StellaSpeechResponse(
                    intention="error",
                    response="Desculpe, houve um erro na validação da resposta.",
                    stella_analysis="error",
                    reason=f"Validation error: {str(validation_error)}"
                )
            )
            
            send_event(
                channel=get_default_channel(),
                event="server-speech-output",
                data=error_response.model_dump()
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar validation error: {e}")
    
    @staticmethod
    async def _send_empty_response(session_id: str, correlation_id: str):
        """Envia resposta para IA vazia"""
        try:
            empty_response = SpeechResponse(
                session_id=session_id,
                correlation_id=correlation_id,
                timestamp=datetime.now(),
                data=StellaSpeechResponse(
                    intention="error",
                    response="Desculpe, não consegui processar sua solicitação.",
                    stella_analysis="error",
                    reason="IA retornou resposta vazia"
                )
            )

            send_event(
                channel=get_default_channel(),
                event="server-speech-output",
                data=empty_response.model_dump()
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar empty response: {e}")
    
    @staticmethod
    async def _send_processing_error(session_id: str, correlation_id: str, error: Exception):
        """Envia erro de processamento via WebSocket"""
        try:
            error_response = SpeechResponse(
                session_id=session_id,
                correlation_id=correlation_id,
                timestamp=datetime.now(),
                data=StellaSpeechResponse(
                    intention="error",
                    response="Desculpe, ocorreu um erro interno. Tente novamente.",
                    stella_analysis="error",
                    reason=f"Processing error: {str(error)}"
                )
            )

            send_event(
                channel=get_default_channel(),
                event="server-speech-error",
                data=error_response.model_dump()
            )
        except Exception as e:
            logger.error(f"❌ Erro ao enviar processing error: {e}")