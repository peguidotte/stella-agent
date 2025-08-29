import os
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

try:
    from stella.messaging.consumer import consume_multiple
    from stella.messaging.publisher import publish
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from stella.messaging.consumer import consume_multiple
    from stella.messaging.publisher import publish

# Carrega .env
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def start_worker():
    """
    Orquestrador:
    - Consome 'speech.input' e 'face.input'
    - Chama handlers específicos
    - Publica em 'speech.response' e 'face.response' com o mesmo correlation_id
    """
    def handle_speech_message(payload: dict | str, props):
        # TODO: integrar com stella.agent.speech_processor
        # from stella.agent.speech_processor import process_speech
        # resp = process_speech(payload)
        resp = {
            "response": "OK (speech)",
            "echo": payload,
            "processed_at": datetime.now().isoformat()
        }
        publish(
            routing_key='speech.response',
            payload=resp,
            correlation_id=getattr(props, 'correlation_id', None),
        )

    def handle_face_message(payload: dict | str, props):
        # TODO: integrar com stella.face_id.face_recognizer
        # from stella.face_id.face_recognizer import process_face
        # resp = process_face(payload)
        resp = {
            "response": "OK (face)",
            "echo": payload,
            "processed_at": datetime.now().isoformat()
        }
        publish(
            routing_key='face.response',
            payload=resp,
            correlation_id=getattr(props, 'correlation_id', None),
        )

    logger.info("Worker iniciado: speech.input + face.input → responses (via utilitário consumer)")
    
    consume_multiple(
        {
            'speech.input': handle_speech_message,
            'face.input': handle_face_message,
        },
        auto_ack=False
    )
    

if __name__ == "__main__":
    start_worker()