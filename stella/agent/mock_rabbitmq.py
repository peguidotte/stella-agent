import json
import os
import time
from datetime import datetime
import threading
from loguru import logger

class MockRabbitMQ:
    """
    Mock RabbitMQ implementação que simula tópicos usando arquivos JSON.
    """
    
    def __init__(self, topics_dir="rabbit_topics"):
        """
        Inicializa o mock RabbitMQ
        
        Args:
            topics_dir: Diretório onde serão armazenados os arquivos dos tópicos
        """
        self.topics_dir = topics_dir
        self.topics = {}
        self.locks = {}
        self._ensure_topics_dir()
        logger.info(f"MockRabbitMQ inicializado em: {self.topics_dir}")
    
    def _ensure_topics_dir(self):
        """Garante que o diretório de tópicos existe"""
        if not os.path.exists(self.topics_dir):
            os.makedirs(self.topics_dir)
            logger.info(f"Diretório de tópicos criado: {self.topics_dir}")
    
    def _get_topic_file(self, topic):
        """Retorna o caminho do arquivo do tópico"""
        return os.path.join(self.topics_dir, f"{topic}.json")
    
    def _get_lock(self, topic):
        """Obtém ou cria um lock para o tópico (thread-safe)"""
        if topic not in self.locks:
            self.locks[topic] = threading.Lock()
        return self.locks[topic]
    
    def _load_messages(self, topic):
        """Carrega mensagens do tópico do arquivo JSON"""
        topic_file = self._get_topic_file(topic)
        
        if not os.path.exists(topic_file):
            return []
        
        try:
            with open(topic_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('messages', [])
        except Exception as e:
            logger.error(f"Erro ao carregar tópico {topic}: {e}")
            return []
    
    def _save_messages(self, topic, messages):
        """Salva mensagens do tópico no arquivo JSON"""
        topic_file = self._get_topic_file(topic)
        
        data = {
            "topic": topic,
            "updated_at": datetime.now().isoformat(),
            "message_count": len(messages),
            "messages": messages
        }
        
        try:
            with open(topic_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro ao salvar tópico {topic}: {e}")
    
    def create_topic(self, topic):
        """
        Cria um novo tópico se não existir
        
        Args:
            topic: Nome do tópico
            
        Returns:
            True se o tópico foi criado/já existe
        """
        lock = self._get_lock(topic)
        with lock:
            if topic not in self.topics:
                self.topics[topic] = {
                    'created_at': datetime.now().isoformat(),
                    'message_count': 0
                }
                
                # Cria arquivo se não existir
                if not os.path.exists(self._get_topic_file(topic)):
                    self._save_messages(topic, [])
                
                logger.info(f"Tópico '{topic}' criado com sucesso")
            else:
                logger.debug(f"Tópico '{topic}' já existe")
            
            return True
    
    def publish(self, topic, message):
        """
        Publica uma mensagem no tópico
        
        Args:
            topic: Nome do tópico
            message: Mensagem a ser publicada
            
        Returns:
            True se a mensagem foi publicada com sucesso
        """
        try:
            # Garante que o tópico existe ANTES de adquirir o lock
            self.create_topic(topic)
            
            lock = self._get_lock(topic)
            with lock:
                # Carrega mensagens existentes
                messages = self._load_messages(topic)
                
                # Cria nova mensagem
                new_message = {
                    'id': str(int(time.time() * 1000)),  # timestamp como ID
                    'timestamp': datetime.now().isoformat(),
                    'content': message
                }
                
                # Adiciona ao tópico
                messages.append(new_message)
                
                # Salva no arquivo
                self._save_messages(topic, messages)
                
                logger.success(f"Mensagem publicada no tópico '{topic}': {new_message['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao publicar mensagem no tópico {topic}: {e}")
            return False
    
    def consume(self, topic):
        """
        Consome a mensagem mais antiga do tópico (FIFO)
        
        Args:
            topic: Nome do tópico
            
        Returns:
            Mensagem consumida ou None se tópico vazio
        """
        try:
            lock = self._get_lock(topic)
            with lock:
                # Carrega mensagens do tópico
                messages = self._load_messages(topic)
                
                if not messages:
                    logger.debug(f"Tópico '{topic}' está vazio")
                    return None
                
                # Remove a mensagem mais antiga (FIFO)
                message = messages.pop(0)
                
                # Salva tópico atualizado
                self._save_messages(topic, messages)
                
                logger.success(f"Mensagem consumida do tópico '{topic}': {message['id']}")
                return message
                
        except Exception as e:
            logger.error(f"Erro ao consumir mensagem do tópico {topic}: {e}")
            return None
    
    def list_topics(self):
        """Lista todos os tópicos disponíveis"""
        topics = []
        
        if os.path.exists(self.topics_dir):
            for filename in os.listdir(self.topics_dir):
                if filename.endswith('.json'):
                    topics.append(filename[:-5])  # Remove .json
        
        return topics
    
    def get_topic_size(self, topic):
        """Retorna o número de mensagens no tópico"""
        messages = self._load_messages(topic)
        return len(messages)
    
    def purge_topic(self, topic):
        """
        Remove todas as mensagens de um tópico
        
        Args:
            topic: Nome do tópico
            
        Returns:
            True se o tópico foi limpo com sucesso
        """
        try:
            lock = self._get_lock(topic)
            with lock:
                self._save_messages(topic, [])
                logger.info(f"Tópico '{topic}' foi limpo")
                return True
        except Exception as e:
            logger.error(f"Erro ao limpar tópico {topic}: {e}")
            return False

# Instância global para uso em toda a aplicação
mock_rabbitmq = MockRabbitMQ()
