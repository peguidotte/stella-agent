# Configuração de Tópicos RabbitMQ
# Este arquivo permite configurar os tópicos utilizados pelo sistema

# Tópicos principais
USER_INPUT_TOPIC = "user_input"
AI_RESPONSE_TOPIC = "ai_response"

# Tópicos legados (compatibilidade)
COMANDOS_STELLA_TOPIC = "comandos_stella"
RESPOSTAS_STELLA_TOPIC = "respostas_stella"

# Tópicos específicos por funcionalidade
AUTHENTICATION_TOPIC = "stella_auth"
INVENTORY_REQUESTS_TOPIC = "inventory_requests"
INVENTORY_RESPONSES_TOPIC = "inventory_responses"
SYSTEM_NOTIFICATIONS_TOPIC = "system_notifications"

# Configurações de timeout
MESSAGE_TIMEOUT = 10.0  # segundos
CONVERSATION_CLEANUP_HOURS = 24  # horas para limpar conversas inativas

# Configurações de contexto
MAX_CONTEXT_MESSAGES = 10  # máximo de mensagens no contexto
MAX_CONVERSATIONS = 100  # máximo de conversas simultâneas

# Para produção com RabbitMQ real
RABBITMQ_CONFIG = {
    "host": "localhost",
    "port": 5672,
    "username": "guest",
    "password": "guest",
    "virtual_host": "/",
    "exchange": "stella_exchange",
    "routing_keys": {
        "user_input": "user.input",
        "ai_response": "ai.response",
        "notifications": "system.notifications"
    }
}
