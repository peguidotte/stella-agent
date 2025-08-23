#!/usr/bin/env python3
"""
Teste simples para verificar se o MockRabbitMQ está funcionando
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stella.agent.mock_rabbitmq import mock_rabbitmq

def teste_simples():
    print("🧪 TESTE SIMPLES DO MOCK RABBITMQ")
    print("=" * 40)
    
    # Teste 1: Criar tópico
    print("\n1. Criando tópico...")
    topic = "teste_topic"
    result = mock_rabbitmq.create_topic(topic)
    print(f"   Resultado: {'✅ Sucesso' if result else '❌ Falha'}")
    
    # Teste 2: Publicar mensagem
    print("\n2. Publicando mensagem...")
    message = {"teste": "mensagem de teste", "numero": 123}
    result = mock_rabbitmq.publish(topic, message)
    print(f"   Resultado: {'✅ Sucesso' if result else '❌ Falha'}")
    
    # Teste 3: Verificar tamanho do tópico
    print("\n3. Verificando tamanho do tópico...")
    size = mock_rabbitmq.get_topic_size(topic)
    print(f"   Tamanho: {size} mensagens")
    
    # Teste 4: Consumir mensagem
    print("\n4. Consumindo mensagem...")
    consumed = mock_rabbitmq.consume(topic)
    if consumed:
        print(f"   ✅ Mensagem consumida: {consumed['content']}")
    else:
        print("   ❌ Nenhuma mensagem para consumir")
    
    # Teste 5: Verificar tamanho após consumo
    print("\n5. Verificando tamanho após consumo...")
    size = mock_rabbitmq.get_topic_size(topic)
    print(f"   Tamanho: {size} mensagens")
    
    # Teste 6: Listar tópicos
    print("\n6. Listando tópicos...")
    topics = mock_rabbitmq.list_topics()
    print(f"   Tópicos: {topics}")
    
    print("\n🎉 Teste concluído!")

if __name__ == "__main__":
    teste_simples()
