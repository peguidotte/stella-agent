import os
import json
import uuid
import pika
from datetime import datetime
from dotenv import load_dotenv

# Carrega .env da raiz do repo
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

AMQP_URL = os.environ.get('CLOUDAMQP_URL')
if not AMQP_URL:
    raise RuntimeError("CLOUDAMQP_URL não encontrada no .env")

params = pika.URLParameters(AMQP_URL)
params.heartbeat = 600
params.blocked_connection_timeout = 30
params.socket_timeout = 15

connection = pika.BlockingConnection(params)
channel = connection.channel()

# Garante que o exchange existe (topic, durável)
EXCHANGE = 'agent'
ROUTING_KEY = 'speech.response'
channel.exchange_declare(exchange=EXCHANGE, passive=True)

# Mensagem simples (JSON)
payload = {
    "response": "Pedido 1 registrado com sucesso.",
    "intent": "register_withdrawal",
    "metadata": {"source": "demo", "ts": datetime.now().isoformat()}
}

message_id = str(uuid.uuid4())
correlation_id = message_id  # para MVP, use o mesmo; em request/reply, copie do request

channel.basic_publish(
    exchange=EXCHANGE,
    routing_key=ROUTING_KEY,
    body=json.dumps(payload, ensure_ascii=False),
    properties=pika.BasicProperties(
        delivery_mode=2,  # persistente
        content_type='application/json',
        message_id=message_id,
        correlation_id=correlation_id
    )
)

print("Publicado em agent/speech.response")
connection.close()