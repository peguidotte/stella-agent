import sys
import uuid
from typing import Literal
from stella.messaging.publisher import publish  # usa o utilitário já criado

def send(kind: Literal["speech", "face"], text: str | None = None):
    correlation_id = str(uuid.uuid4())

    if kind == "speech":
        routing_key = "speech.input"
        payload = {"text": text or "preciso de 5 seringas de 10ml", "source": "manual_test"}
    else:
        routing_key = "face.input"
        payload = {"action": "validate", "user_id": text or "user_001", "source": "manual_test"}

    publish(routing_key=routing_key, payload=payload, correlation_id=correlation_id)
    print(f"Publicado em {routing_key} (correlation_id={correlation_id})")

if __name__ == "__main__":
    # Uso:
    #   python -m stella.messaging.send_input speech "mensagem opcional"
    #   python -m stella.messaging.send_input face "user_id opcional"
    kind = (sys.argv[1] if len(sys.argv) > 1 else "speech").lower()
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    if kind not in ("speech", "face"):
        print("Use: python -m stella.messaging.send_input [speech|face] [texto|user_id]")
        sys.exit(1)
    send(kind, arg)