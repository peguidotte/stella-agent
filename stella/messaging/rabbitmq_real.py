#!/usr/bin/env python3
"""
Implementação real do RabbitMQ para substituir o mock
Migração do MockRabbitMQ para RabbitMQ real usando pika
"""

import pika
import json
import time
import threading
from datetime import datetime
from loguru import logger
from typing import Optional, Dict, Any, Callable


class RealRabbitMQ:
    """
    Implementação real do RabbitMQ usando pika
    Interface compatível com MockRabbitMQ para migração transparente
    """
    
    def __init__(self, host='localhost', port=5672, username='guest', password='guest', virtual_host='/'):
        """
        Inicializa conexão com RabbitMQ real
        
        Args:
            host: Servidor RabbitMQ
            port: Porta do servidor
            username: Usuário
            password: Senha
            virtual_host: Virtual host
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        
        self.connection = None
        self.channel = None
        self.consumers = {}  # Para tracking de consumers ativos
        
        self._connect()
        logger.info(f"RealRabbitMQ inicializado em: {host}:{port}")
    
    def _connect(self):
        """Estabelece conexão com RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300,
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Configuração de QoS
            self.channel.basic_qos(prefetch_count=1)
            
            logger.success(f"Conectado ao RabbitMQ: {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao RabbitMQ: {e}")
            raise
    
    def _ensure_connection(self):
        """Garante que a conexão está ativa"""
        try:
            if not self.connection or self.connection.is_closed:
                logger.warning("Conexão perdida, reconectando...")
                self._connect()
        except Exception as e:
            logger.error(f"Erro ao verificar conexão: {e}")
            self._connect()
    
    def create_topic(self, topic: str) -> bool:
        """
        Cria um exchange/queue (equivalente ao tópico do mock)
        
        Args:
            topic: Nome do tópico/queue
            
        Returns:
            True se criado com sucesso
        """
        try:
            self._ensure_connection()
            
            # Declara queue durável
            self.channel.queue_declare(
                queue=topic,
                durable=True,  # Persiste restarts do servidor
                exclusive=False,
                auto_delete=False
            )
            
            logger.info(f"Queue '{topic}' criada/verificada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar queue {topic}: {e}")
            return False
    
    def publish(self, topic: str, message: Any) -> bool:
        """
        Publica mensagem na queue
        
        Args:
            topic: Nome da queue
            message: Mensagem a ser publicada
            
        Returns:
            True se publicado com sucesso
        """
        try:
            self._ensure_connection()
            
            # Garante que a queue existe
            self.create_topic(topic)
            
            # Serializa mensagem
            if isinstance(message, (dict, list)):
                message_body = json.dumps(message, ensure_ascii=False)
            else:
                message_body = str(message)
            
            # Publica com persistência
            self.channel.basic_publish(
                exchange='',  # Default exchange
                routing_key=topic,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensagem persistente
                    timestamp=int(time.time()),
                    content_type='application/json'
                )
            )
            
            logger.success(f"Mensagem publicada na queue '{topic}'")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem na queue {topic}: {e}")
            return False
    
    def consume(self, topic: str) -> Optional[Dict[str, Any]]:
        """
        Consome uma mensagem da queue (equivalente ao mock)
        
        Args:
            topic: Nome da queue
            
        Returns:
            Mensagem consumida ou None se vazia
        """
        try:
            self._ensure_connection()
            
            # Garante que a queue existe
            self.create_topic(topic)
            
            # Consome uma mensagem
            method_frame, header_frame, body = self.channel.basic_get(
                queue=topic,
                auto_ack=True  # Auto-acknowledgment para simplicidade
            )
            
            if method_frame:
                # Processa mensagem
                try:
                    content = json.loads(body.decode('utf-8'))
                except json.JSONDecodeError:
                    content = body.decode('utf-8')
                
                message = {
                    'id': str(method_frame.delivery_tag),
                    'timestamp': datetime.now().isoformat(),
                    'content': content
                }
                
                logger.success(f"Mensagem consumida da queue '{topic}': {method_frame.delivery_tag}")
                return message
            
            else:
                logger.debug(f"Queue '{topic}' está vazia")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao consumir mensagem da queue {topic}: {e}")
            return None
    
    def start_consumer(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Inicia consumer contínuo (para conversas em tempo real)
        
        Args:
            topic: Nome da queue
            callback: Função para processar mensagens recebidas
        """
        try:
            self._ensure_connection()
            self.create_topic(topic)
            
            def wrapper(ch, method, properties, body):
                try:
                    # Processa mensagem
                    try:
                        content = json.loads(body.decode('utf-8'))
                    except json.JSONDecodeError:
                        content = body.decode('utf-8')
                    
                    message = {
                        'id': str(method.delivery_tag),
                        'timestamp': datetime.now().isoformat(),
                        'content': content
                    }
                    
                    # Chama callback
                    callback(message)
                    
                    # Acknowledge
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    
                except Exception as e:
                    logger.error(f"Erro no consumer callback: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            
            # Configura consumer
            self.channel.basic_consume(
                queue=topic,
                on_message_callback=wrapper
            )
            
            # Armazena referência
            self.consumers[topic] = True
            
            logger.info(f"Consumer iniciado para queue '{topic}'")
            
            # Inicia consumo em thread separada
            def consume_thread():
                try:
                    while self.consumers.get(topic, False):
                        self.connection.process_data_events(time_limit=1)
                        time.sleep(0.1)
                except Exception as e:
                    logger.error(f"Erro no consumer thread: {e}")
            
            threading.Thread(target=consume_thread, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Erro ao iniciar consumer para {topic}: {e}")
    
    def stop_consumer(self, topic: str):
        """Para consumer específico"""
        if topic in self.consumers:
            self.consumers[topic] = False
            logger.info(f"Consumer parado para queue '{topic}'")
    
    def get_topic_size(self, topic: str) -> int:
        """
        Retorna número de mensagens na queue
        
        Args:
            topic: Nome da queue
            
        Returns:
            Número de mensagens
        """
        try:
            self._ensure_connection()
            
            method = self.channel.queue_declare(
                queue=topic,
                durable=True,
                passive=True  # Apenas verifica, não cria
            )
            
            return method.method.message_count
            
        except Exception as e:
            logger.error(f"Erro ao obter tamanho da queue {topic}: {e}")
            return 0
    
    def purge_topic(self, topic: str) -> bool:
        """
        Remove todas as mensagens da queue
        
        Args:
            topic: Nome da queue
            
        Returns:
            True se limpo com sucesso
        """
        try:
            self._ensure_connection()
            
            self.channel.queue_purge(queue=topic)
            logger.info(f"Queue '{topic}' foi limpa")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao limpar queue {topic}: {e}")
            return False
    
    def list_topics(self) -> list:
        """
        Lista todas as queues (aproximação para compatibilidade)
        No RabbitMQ real isso requer API management
        """
        logger.warning("list_topics() não implementado para RabbitMQ real - requer RabbitMQ Management API")
        return []
    
    def close(self):
        """Fecha conexão"""
        try:
            # Para todos os consumers
            for topic in list(self.consumers.keys()):
                self.stop_consumer(topic)
            
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("Conexão RabbitMQ fechada")
                
        except Exception as e:
            logger.error(f"Erro ao fechar conexão: {e}")
    
    def __del__(self):
        """Destructor para garantir limpeza"""
        self.close()


# Factory function para migração transparente
def create_rabbitmq_client(use_real=False, **kwargs):
    """
    Factory para criar cliente RabbitMQ (mock ou real)
    
    Args:
        use_real: Se True, usa RabbitMQ real, senão usa mock
        **kwargs: Parâmetros para RabbitMQ real
        
    Returns:
        Instância do cliente RabbitMQ
    """
    if use_real:
        return RealRabbitMQ(**kwargs)
    else:
        from stella.agent.mock_rabbitmq import MockRabbitMQ
        return MockRabbitMQ()


# Configuração global
RABBITMQ_CONFIG = {
    'host': 'localhost',
    'port': 5672,
    'username': 'guest',
    'password': 'guest',
    'virtual_host': '/'
}

# Instância global (inicialmente mock, pode ser mudada)
rabbitmq_client = None

def get_rabbitmq_client(force_real=False):
    """
    Obtém cliente RabbitMQ global
    
    Args:
        force_real: Força uso do RabbitMQ real
        
    Returns:
        Cliente RabbitMQ ativo
    """
    global rabbitmq_client
    
    if rabbitmq_client is None:
        # Verifica se RabbitMQ real está disponível
        use_real = force_real or _check_rabbitmq_available()
        rabbitmq_client = create_rabbitmq_client(use_real=use_real, **RABBITMQ_CONFIG)
    
    return rabbitmq_client

def _check_rabbitmq_available():
    """
    Verifica se RabbitMQ real está disponível
    
    Returns:
        True se disponível
    """
    try:
        import pika
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters(
            host='localhost',
            port=5672,
            credentials=credentials,
            connection_attempts=1,
            retry_delay=1
        )
        
        connection = pika.BlockingConnection(parameters)
        connection.close()
        return True
        
    except Exception:
        return False
