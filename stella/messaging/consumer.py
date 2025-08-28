import os
import json
import pika
from dotenv import load_dotenv

# Carrega .env da raiz do repo
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

AMQP_URL = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
params = pika.URLParameters(AMQP_URL)
params.heartbeat = 600
params.blocked_connection_timeout = 30
params.socket_timeout = 15

connection = pika.BlockingConnection(params)
channel = connection.channel()

EXCHANGE = 'agent'           # já existe no broker
QUEUE_NAME = 'speech.input'  # fila existente ligada ao exchange 'agent'

# Garante que a fila existe sem alterar propriedades
channel.queue_declare(queue=QUEUE_NAME, passive=True)

def callback(ch, method, properties, body):
    try:
        msg = json.loads(body.decode('utf-8'))
    except Exception:
        msg = body.decode('utf-8', errors='ignore')
    print(f" [x] Received from {EXCHANGE}/{QUEUE_NAME}: {msg}")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print(f" [*] Waiting for messages in queue '{QUEUE_NAME}' (exchange '{EXCHANGE}')...")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    pass
finally:
    try:
        channel.stop_consuming()
    except Exception:
        pass
    connection.close()
