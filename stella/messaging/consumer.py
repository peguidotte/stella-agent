import os
import json
import pika
from typing import Callable, Dict
from dotenv import load_dotenv

# Carrega .env da raiz do repo
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def _get_params():
    amqp_url = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672/%2f')
    params = pika.URLParameters(amqp_url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 30
    params.socket_timeout = 15
    return params

def consume(queue_name: str, on_message: Callable, auto_ack: bool = False, stop_after_one: bool = False):
    """
    Consume from an existing queue (already bound on the broker).

    :param str queue_name: Queue name (e.g., 'speech.response').
    :param on_message: Callback function called as on_message(payload, properties).
    :param bool auto_ack: If True, automatic ack (less safe). Default False (manual ack after callback).
    :param bool stop_after_one: If True, stop after 1 message (useful for tests).

    Note:
      - Decodes body as JSON when possible; otherwise, as a string.
      - properties (pika.BasicProperties) contains correlation_id, message_id, and headers.
    """
    params = _get_params()
    connection = pika.BlockingConnection(params)
    ch = connection.channel()
    ch.queue_declare(queue=queue_name, passive=True)

    def _cb(ch_, method, properties, body):
        try:
            try:
                msg = json.loads(body.decode('utf-8'))
            except Exception:
                msg = body.decode('utf-8', errors='ignore')
            on_message(msg, properties)
            if not auto_ack:
                ch_.basic_ack(delivery_tag=method.delivery_tag)
        finally:
            if stop_after_one:
                ch_.stop_consuming()

    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=queue_name, on_message_callback=_cb, auto_ack=auto_ack)

    try:
        ch.start_consuming()
    finally:
        try:
            ch.stop_consuming()
        except Exception:
            pass
        connection.close()

def consume_multiple(queue_handlers: Dict[str, Callable], auto_ack: bool = False):
    """
    Consome simultaneamente de múltiplas filas em uma única conexão/canal.

    Args:
      queue_handlers: Mapeamento { 'nome_da_fila': handler }, onde handler(payload, properties) processa a mensagem.
      auto_ack: Se True, ack automático. Padrão False (ack após sucesso do handler).

    Comportamento:
      - Abre uma conexão e registra um consumer por fila do dict.
      - Ack automático se auto_ack=True; caso False, ack após handler sem erro.
      - Em caso de exceção no handler, NACK com requeue=True.
    """
    params = _get_params()
    connection = pika.BlockingConnection(params)
    ch = connection.channel()
    ch.basic_qos(prefetch_count=1)

    for queue_name, handler in queue_handlers.items():
        ch.queue_declare(queue=queue_name, passive=True)

        def _make_cb(fn: Callable):
            def _cb(ch_, method, properties, body):
                try:
                    try:
                        msg = json.loads(body.decode('utf-8'))
                    except Exception:
                        msg = body.decode('utf-8', errors='ignore')
                    fn(msg, properties)
                    if not auto_ack:
                        ch_.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:
                    # Reencaminha para reprocessamento
                    ch_.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            return _cb

        ch.basic_consume(queue=queue_name, on_message_callback=_make_cb(handler), auto_ack=auto_ack)

    try:
        ch.start_consuming()
    finally:
        try:
            ch.stop_consuming()
        except Exception:
            pass
        connection.close()