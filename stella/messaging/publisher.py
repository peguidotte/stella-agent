import os
import json
import uuid
import pika
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# Carrega .env da raiz do repo
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def get_rabbitmq_connection():
    """
    Cria e retorna uma conexão RabbitMQ com tratamento de erros.
    
    Returns:
        pika.BlockingConnection: Conexão ativa
        
    Raises:
        RuntimeError: Se CLOUDAMQP_URL não estiver configurada ou conexão falhar
    """
    amqp_url = os.environ.get('CLOUDAMQP_URL')
    if not amqp_url:
        logger.error("❌ CLOUDAMQP_URL não encontrada no .env")
        raise RuntimeError("CLOUDAMQP_URL não encontrada no .env")
    
    try:
        params = pika.URLParameters(amqp_url)
        params.heartbeat = 600
        params.blocked_connection_timeout = 30
        params.socket_timeout = 15
        
        connection = pika.BlockingConnection(params)
        logger.success("✅ Conexão RabbitMQ estabelecida")
        return connection
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao RabbitMQ: {e}")
        raise

def publish(exchange: str, routing_key: str, payload: dict) -> bool:
    """
    Publica mensagem JSON no exchange e routing_key especificados.
    
    Args:
        exchange: Nome do exchange
        routing_key: Routing key
        payload: Dados a publicar (serão convertidos para JSON)
        
    Returns:
        bool: True se publicação foi bem-sucedida
        
    Raises:
        Exception: Se houver erro na publicação
    """
    connection = None
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Garante que o exchange existe
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)
        
        # Publica a mensagem
        message_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())
        
        channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=json.dumps(payload, ensure_ascii=False),
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistente
                content_type='application/json',
                message_id=message_id,
                correlation_id=correlation_id,
                timestamp=int(datetime.now().timestamp())
            )
        )
        
        logger.success(f"📤 Mensagem publicada | Exchange: {exchange} | Key: {routing_key} | ID: {message_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao publicar mensagem: {e}")
        raise
    finally:
        if connection and not connection.is_closed:
            try:
                connection.close()
                logger.debug("🔌 Conexão RabbitMQ fechada")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao fechar conexão: {e}")