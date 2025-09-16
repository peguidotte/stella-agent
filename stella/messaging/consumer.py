import os
import json
import signal
import sys
import pika
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

def process_message(ch, method, properties, body):
    """
    Callback para processar mensagens recebidas.
    
    Args:
        ch: Canal
        method: Método de entrega
        properties: Propriedades da mensagem
        body: Corpo da mensagem
    """
    try:
        # Tenta parsear como JSON
        try:
            message = json.loads(body.decode('utf-8'))
            logger.info(f"📨 Mensagem JSON recebida: {message}")
        except json.JSONDecodeError:
            # Se não for JSON, trata como string
            message = body.decode('utf-8', errors='ignore')
            logger.info(f"📨 Mensagem texto recebida: {message}")
        
        # Aqui, adicionar lógica de processamento

        # Confirma o processamento da mensagem
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(f"✅ Mensagem processada | Tag: {method.delivery_tag}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao processar mensagem: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer(exchange: str, queue_name: str):
    """
    Inicia o consumer RabbitMQ.
    
    Args:
        exchange: Nome do exchange
        queue_name: Nome da fila
    """
    connection = None
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Garante que a fila existe
        channel.queue_declare(queue=queue_name, durable=True)
        channel.queue_bind(exchange=exchange, queue=queue_name, routing_key='#')
        channel.basic_qos(prefetch_count=1)
        
        channel.basic_consume(
            queue=queue_name, 
            on_message_callback=process_message, 
            auto_ack=False
        )
        
        logger.info(f"🎧 Consumer iniciado | Exchange: {exchange} | Queue: {queue_name}")
        
        channel.start_consuming()
        
    except KeyboardInterrupt:
        logger.info("🛑 Consumer interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro no consumer: {e}")
    finally:
        if connection and not connection.is_closed:
            try:
                connection.close()
                logger.debug("🔌 Conexão RabbitMQ fechada")
            except Exception as e:
                logger.warning(f"⚠️ Erro ao fechar conexão: {e}")

def main():
    """Função principal para executar o consumer."""
    try:
        start_consumer()
    except Exception as e:
        logger.error(f"❌ Falha ao iniciar consumer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()