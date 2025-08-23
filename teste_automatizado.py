#!/usr/bin/env python3
"""
Teste automatizado para o sistema Stella Agent
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stella.agent.mock_rabbitmq import mock_rabbitmq

def test_publish_commands():
    """Teste de publicação de comandos"""
    print("🧪 TESTANDO PUBLICAÇÃO DE COMANDOS")
    print("=" * 50)
    
    test_commands = [
        {"comando": "preciso de 5 seringas de 10ml"},
        {"comando": "quanto tem de luva tamanho M no estoque?"},
        {"comando": "peguei 3 caixas de gaze estéril"},
        {"comando": "onde fica o termômetro digital?"},
        {"comando": "cancelar o último registro"}
    ]
    
    topic = "comandos_stella"
    print(f"\n1. Criando tópico '{topic}'...")
    mock_rabbitmq.create_topic(topic)
    
    print(f"\n2. Publicando {len(test_commands)} comandos...")
    successful = 0
    failed = 0
    
    for i, cmd in enumerate(test_commands, 1):
        print(f"   Publicando comando {i}: {cmd['comando'][:50]}...")
        result = mock_rabbitmq.publish(topic, cmd)
        if result:
            successful += 1
            print(f"   ✅ Sucesso")
        else:
            failed += 1
            print(f"   ❌ Falha")
    
    print(f"\n3. Resultado:")
    print(f"   ✅ Sucessos: {successful}")
    print(f"   ❌ Falhas: {failed}")
    
    size = mock_rabbitmq.get_topic_size(topic)
    print(f"   📊 Total no tópico: {size} mensagens")
    
    return successful, failed

def test_consume_commands():
    """Teste de consumo de comandos"""
    print("\n🧪 TESTANDO CONSUMO DE COMANDOS")
    print("=" * 50)
    
    topic = "comandos_stella"
    consumed = 0
    
    print(f"\n1. Consumindo comandos do tópico '{topic}'...")
    
    while True:
        message = mock_rabbitmq.consume(topic)
        if not message:
            print("   Não há mais mensagens para consumir")
            break
        
        consumed += 1
        comando = message.get('content', {}).get('comando', 'N/A')
        print(f"   [{consumed}] Consumido: {comando[:50]}...")
    
    print(f"\n2. Resultado:")
    print(f"   📥 Total consumido: {consumed} mensagens")
    
    return consumed

def main():
    """Função principal do teste"""
    print("🚀 TESTE AUTOMATIZADO - STELLA AGENT MOCK RABBITMQ")
    print("=" * 60)
    
    try:
        # Teste de publicação
        successful, failed = test_publish_commands()
        
        # Teste de consumo
        consumed = test_consume_commands()
        
        # Resumo final
        print("\n🎯 RESUMO FINAL")
        print("=" * 30)
        print(f"✅ Comandos publicados: {successful}")
        print(f"❌ Falhas na publicação: {failed}")
        print(f"📥 Comandos consumidos: {consumed}")
        
        if successful > 0 and failed == 0 and consumed == successful:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return True
        else:
            print("\n⚠️  ALGUNS TESTES FALHARAM!")
            return False
            
    except Exception as e:
        print(f"\n💥 ERRO DURANTE O TESTE: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
