#!/usr/bin/env python3
"""
Teste completo automatizado do sistema Stella Agent
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stella.agent.mock_rabbitmq import mock_rabbitmq
from stella.agent.speech_processor import get_command, command_interpreter, process_action

def test_complete_flow():
    """Testa o fluxo completo: Publicar → Processar → Visualizar"""
    print("🚀 TESTE COMPLETO DO FLUXO STELLA AGENT")
    print("=" * 60)
    
    # 1. Limpa tópicos
    print("\n1. 🧹 Limpando tópicos...")
    mock_rabbitmq.purge_topic("comandos_stella")
    mock_rabbitmq.purge_topic("respostas_stella")
    
    # 2. Publica comandos de teste
    print("\n2. 📤 Publicando comandos de teste...")
    test_commands = [
        {"comando": "preciso de 5 seringas de 10ml"},
        {"comando": "quanto tem de luva no estoque?"},
        {"comando": "peguei 3 caixas de gaze estéril"}
    ]
    
    topic = "comandos_stella"
    mock_rabbitmq.create_topic(topic)
    
    for i, cmd in enumerate(test_commands, 1):
        result = mock_rabbitmq.publish(topic, cmd)
        if result:
            print(f"   ✅ [{i}] Publicado: {cmd['comando']}")
        else:
            print(f"   ❌ [{i}] Falha: {cmd['comando']}")
    
    size = mock_rabbitmq.get_topic_size(topic)
    print(f"   📊 Total no tópico: {size} mensagens")
    
    # 3. Processa comandos
    print("\n3. 🔄 Processando comandos...")
    processed = 0
    max_iterations = 5  # Evita loop infinito
    
    for iteration in range(max_iterations):
        comando = get_command()
        if not comando:
            print(f"   ℹ️  Não há mais comandos após {processed} processamentos")
            break
        
        print(f"   [{processed+1}] Processando: \"{comando}\"")
        
        resultado = command_interpreter(comando)
        if resultado:
            intencao = resultado.get('intencao', 'desconhecida')
            print(f"      🧠 Intenção: {intencao}")
            
            confirmacao = process_action(resultado)
            print(f"      💬 Resposta: {confirmacao}")
            
            processed += 1
        else:
            print("      ❌ Falha ao interpretar")
            break
    
    print(f"   📈 Total processado: {processed} comandos")
    
    # 4. Visualiza respostas
    print("\n4. 👁️  Visualizando respostas...")
    response_topic = "respostas_stella"
    response_size = mock_rabbitmq.get_topic_size(response_topic)
    
    if response_size == 0:
        print("   ⚠️  Nenhuma resposta gerada")
    else:
        print(f"   📊 Total de respostas: {response_size}")
        messages = mock_rabbitmq._load_messages(response_topic)
        
        for i, msg in enumerate(messages, 1):
            content = msg.get('content', {})
            if isinstance(content, dict) and 'resposta' in content:
                resposta = content['resposta']
                intencao = resposta.get('intencao', 'N/A')
                confirmacao = resposta.get('confirmacao', 'N/A')[:50] + "..."
                print(f"      [{i}] {intencao}: {confirmacao}")
    
    # 5. Resultado final
    print(f"\n5. 🎯 Resultado Final:")
    commands_remaining = mock_rabbitmq.get_topic_size("comandos_stella")
    responses_generated = mock_rabbitmq.get_topic_size("respostas_stella")
    
    print(f"   📤 Comandos restantes: {commands_remaining}")
    print(f"   📥 Respostas geradas: {responses_generated}")
    print(f"   🔄 Comandos processados: {processed}")
    
    if processed > 0 and responses_generated > 0 and commands_remaining == 0:
        print("\n🎉 TESTE COMPLETO PASSOU COM SUCESSO!")
        return True
    else:
        print("\n⚠️  TESTE TEVE PROBLEMAS!")
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
