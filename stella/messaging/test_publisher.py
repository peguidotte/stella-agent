import sys
import os
from datetime import datetime
from loguru import logger

# Adiciona o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from publisher import publish

def main():
    """
    Teste do publisher enviando mensagem para exchange 'stock' com routing key 'remove'
    """
    logger.info("🚀 Iniciando teste do publisher...")
    
    # Configurar exchange e routing key
    exchange = "stock"
    routing_key = "remove"
    
    # Payload de exemplo para remoção de stock
    payload = {
        "itens": [
            {
                "productName": "Heroina",
                "quantity": 5,
            },
            {
                "productName": "Maconha",
                "quantity": 989,
            }
        ],
        "withdrawBy": "Miguel"
    }
    
    try:
        logger.info(f"📦 Preparando para enviar payload:")
        logger.info(f"   Exchange: {exchange}")
        logger.info(f"   Routing Key: {routing_key}")
        logger.info(f"   Payload: {payload}")
        
        # Publicar mensagem
        success = publish(exchange=exchange, routing_key=routing_key, payload=payload)
        
        if success:
            logger.success("🎉 Mensagem enviada com sucesso!")
        else:
            logger.error("❌ Falha ao enviar mensagem")
            
    except Exception as e:
        logger.error(f"💥 Erro durante o teste: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🧪 TESTE DO PUBLISHER RABBITMQ")
    logger.info("=" * 50)
    
    # Executar teste
    result = main()
    
    if result:
        logger.success("✅ Teste concluído com sucesso!")
    else:
        logger.error("❌ Teste falhou!")
        sys.exit(1)
    
    logger.info("=" * 50)