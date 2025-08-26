#!/usr/bin/env python3
"""
Adaptador para migração transparente do MockRabbitMQ para RabbitMQ real
Permite alternar entre mock e real sem alterar código existente
"""

import os
from loguru import logger


class RabbitMQAdapter:
    """
    Adaptador que permite usar tanto Mock quanto RabbitMQ real
    com a mesma interface
    """
    
    def __init__(self, use_real=None, **kwargs):
        """
        Inicializa o adaptador
        
        Args:
            use_real: Se None, detecta automaticamente. Se True/False, força modo específico
            **kwargs: Parâmetros para RabbitMQ real
        """
        self.client = None
        self.is_real = False
        
        # Detecta automaticamente se não especificado
        if use_real is None:
            use_real = self._detect_rabbitmq_available()
        
        self._initialize_client(use_real, **kwargs)
    
    def _detect_rabbitmq_available(self):
        """
        Detecta se RabbitMQ real está disponível
        
        Returns:
            True se RabbitMQ real disponível
        """
        try:
            import pika
            
            # Tenta conectar rapidamente
            credentials = pika.PlainCredentials('guest', 'guest')
            parameters = pika.ConnectionParameters(
                host='localhost',
                port=5672,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=0.5,
                socket_timeout=2
            )
            
            connection = pika.BlockingConnection(parameters)
            connection.close()
            
            logger.info("✅ RabbitMQ real detectado e disponível")
            return True
            
            logger.warning(f"🔌 RabbitMQ real não disponível ({type(e).__name__}: {e}) - usando mock")
            return False
    
    def _initialize_client(self, use_real, **kwargs):
        """
        Inicializa o cliente apropriado
        
        Args:
            use_real: Se deve usar RabbitMQ real
            **kwargs: Parâmetros para RabbitMQ real
        """
        if use_real:
            try:
                from stella.messaging.rabbitmq_real import RealRabbitMQ
                self.client = RealRabbitMQ(**kwargs)
                self.is_real = True
                logger.success("🐰 Usando RabbitMQ REAL")
                
            except Exception as e:
                logger.error(f"❌ Falha ao inicializar RabbitMQ real: {e}")
                logger.info("🔄 Fallback para MockRabbitMQ")
                self._initialize_mock()
        else:
            self._initialize_mock()
    
    def _initialize_mock(self):
        """Inicializa MockRabbitMQ"""
        try:
            from stella.agent.mock_rabbitmq import MockRabbitMQ
            self.client = MockRabbitMQ()
            self.is_real = False
            logger.info("🎭 Usando MockRabbitMQ")
            
        except Exception as e:
            logger.error(f"❌ Falha ao inicializar MockRabbitMQ: {e}")
            raise
    
    # Interface unificada - delega para o cliente ativo
    def create_topic(self, topic):
        """Cria tópico/queue"""
        return self.client.create_topic(topic)
    
    def publish(self, topic, message):
        """Publica mensagem"""
        return self.client.publish(topic, message)
    
    def consume(self, topic):
        """Consome mensagem"""
        return self.client.consume(topic)
    
    def get_topic_size(self, topic):
        """Retorna tamanho do tópico"""
        return self.client.get_topic_size(topic)
    
    def purge_topic(self, topic):
        """Limpa tópico"""
        return self.client.purge_topic(topic)
    
    def list_topics(self):
        """Lista tópicos"""
        return self.client.list_topics()
    
    def start_consumer(self, topic, callback=None):
        """Inicia consumer (se disponível)"""
        if hasattr(self.client, 'start_consumer') and callable(getattr(self.client, 'start_consumer')):
            return self.client.start_consumer(topic, callback)
        else:
            logger.warning(f"start_consumer não implementado para {type(self.client).__name__}")
            return False
    
    def stop_consumer(self, topic):
        """Para consumer (se disponível)"""
        if hasattr(self.client, 'stop_consumer') and callable(getattr(self.client, 'stop_consumer')):
            return self.client.stop_consumer(topic)
        else:
            logger.warning(f"stop_consumer não implementado para {type(self.client).__name__}")
            return False
    
    def close(self):
        """Fecha conexão"""
        if hasattr(self.client, 'close') and callable(getattr(self.client, 'close')):
            return self.client.close()
    
    def get_status(self):
        """Retorna status do cliente"""
        return {
            'type': 'RealRabbitMQ' if self.is_real else 'MockRabbitMQ',
            'real': self.is_real,
            'client': type(self.client).__name__
        }


# Instância global
_global_rabbitmq = None

def get_rabbitmq(force_real=None, **kwargs):
    """
    Obtém instância global do adaptador RabbitMQ
    
    Args:
        force_real: Se especificado, força modo real (True) ou mock (False)
        **kwargs: Parâmetros para RabbitMQ real
        
    Returns:
        Instância do adaptador RabbitMQ
    """
    global _global_rabbitmq
    
    if _global_rabbitmq is None:
        _global_rabbitmq = RabbitMQAdapter(use_real=force_real, **kwargs)
    
    return _global_rabbitmq

def reset_rabbitmq():
    """Reset da instância global (útil para testes)"""
    global _global_rabbitmq
    if _global_rabbitmq:
        _global_rabbitmq.close()
        _global_rabbitmq = None


# Backward compatibility - mantém interface igual ao mock_rabbitmq.py
def create_rabbitmq_instance():
    """
    Cria instância compatível com uso existente
    
    Returns:
        Instância do cliente RabbitMQ
    """
    return get_rabbitmq()


# Para compatibilidade total com código existente
rabbitmq = get_rabbitmq()

if __name__ == "__main__":
    # Teste básico
    print("🧪 Testando RabbitMQ Adapter")
    
    adapter = RabbitMQAdapter()
    status = adapter.get_status()
    
    print(f"Status: {status}")
    print(f"Tipo: {status['type']}")
    
    # Teste básico de operações
    topic = "test_topic"
    
    print(f"\n📝 Testando operações no tópico: {topic}")
    
    # Cria tópico
    adapter.create_topic(topic)
    print(f"Tamanho inicial: {adapter.get_topic_size(topic)}")
    
    # Publica mensagem
    adapter.publish(topic, {"teste": "mensagem de teste"})
    print(f"Após publicar: {adapter.get_topic_size(topic)}")
    
    # Consome mensagem
    message = adapter.consume(topic)
    print(f"Mensagem consumida: {message}")
    print(f"Tamanho final: {adapter.get_topic_size(topic)}")
    
    adapter.close()
    print("✅ Teste concluído")
