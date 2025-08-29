import os, json, uuid, pika
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Carrega .env da raiz do repo
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def _get_params():
    amqp_url = os.environ.get('CLOUDAMQP_URL')
    if not amqp_url:
        raise RuntimeError("CLOUDAMQP_URL not found")
    params = pika.URLParameters(amqp_url)
    params.heartbeat = 600
    params.blocked_connection_timeout = 30
    params.socket_timeout = 15
    return params

def publish(routing_key: str, payload: dict, correlation_id: str, headers: dict | None = None) -> None:
    """
    Publica no exchange 'agent' (já existente) com IDs.

    :param routing_key: Routing key de destino (ex.: 'speech.response', 'face.response').
    :type routing_key: str
    :param payload: Conteúdo da mensagem (serializado em JSON).
    :type payload: dict
    :param correlation_id: ID para correlacionar a resposta ao request original.
    :type correlation_id: str
    :param headers: Cabeçalhos AMQP opcionais (ex.: {"client_id": "..."}).
    :type headers: dict | None
    :return: None. Lança exceção em caso de erro.
    :rtype: None
    """
    params = _get_params()
    connection = None
    try:
        connection = pika.BlockingConnection(params)
        ch = connection.channel()
        ch.exchange_declare(exchange='agent', passive=True)  # não altera o tipo no broker

        message_id = str(uuid.uuid4())
        props = pika.BasicProperties(
            content_type='application/json',
            delivery_mode=2,
            correlation_id=correlation_id,
            message_id=message_id,
            headers=headers or {}
        )
        body = json.dumps(payload, ensure_ascii=False)
        ch.basic_publish(exchange='agent', routing_key=routing_key, body=body, properties=props)
        logger.success(f"Published with rk={routing_key} corr={correlation_id} msg={message_id}")
    except Exception as e:
        logger.error(f"Error publishing message: {e}")
        raise
    finally:
        if connection:
            try:
                connection.close()
                logger.success(f"Connection closed successfully")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
                raise