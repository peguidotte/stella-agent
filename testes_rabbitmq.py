#!/usr/bin/env python3
"""
Script para testar o funcionamento do MockRabbitMQ com o Stella Agent
"""

import os
import sys
import json
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stella.agent.mock_rabbitmq import mock_rabbitmq
from stella.agent.speech_processor import get_command, command_interpreter, process_action

def publish_test_commands():
    """Publica comandos de teste no tópico de comandos"""
    print("\n=== Publicando comandos de teste ===")
    
    test_commands = [
        {"comando": "preciso de 5 seringas de 10ml"},
        {"comando": "quanto tem de luva tamanho M no estoque?"},
        {"comando": "peguei 3 caixas de gaze estéril"},
        {"comando": "onde fica o termômetro digital?"},
        {"comando": "cancelar o último registro"}
    ]
    
    topic = "comandos_stella"
    mock_rabbitmq.create_topic(topic)
    
    for i, cmd in enumerate(test_commands, 1):
        result = mock_rabbitmq.publish(topic, cmd)
        if result:
            print(f"✅ [{i}] Comando publicado: {cmd['comando']}")
        else:
            print(f"❌ [{i}] Falha ao publicar: {cmd['comando']}")
    
    print(f"\nTotal de comandos no tópico: {mock_rabbitmq.get_topic_size(topic)}")

def process_commands():
    """Processa todos os comandos disponíveis"""
    print("\n=== Processando comandos ===")
    
    processed = 0
    while True:
        # Obtém o próximo comando
        comando = get_command()
        if not comando:
            print("Não há mais comandos disponíveis.")
            break
        
        print(f"\n[{processed+1}] Processando: \"{comando}\"")
        
        # Interpreta o comando com o Gemini
        resultado = command_interpreter(comando)
        
        if resultado:
            # Mostra a intenção detectada
            intencao = resultado.get('intencao', 'desconhecida')
            print(f"🧠 Intenção: {intencao}")
            
            # Processa a ação e obtém a confirmação
            confirmacao = process_action(resultado)
            print(f"💬 Resposta: {confirmacao}")
            
            processed += 1
        else:
            print("❌ Falha ao interpretar o comando")
    
    print(f"\nTotal de comandos processados: {processed}")

def view_responses():
    """Visualiza as respostas geradas"""
    print("\n=== Respostas geradas ===")
    
    topic = "respostas_stella"
    size = mock_rabbitmq.get_topic_size(topic)
    
    if size == 0:
        print("Nenhuma resposta disponível.")
        return
    
    print(f"Total de respostas: {size}\n")
    
    # Carrega todas as mensagens para visualização (sem consumir)
    messages = mock_rabbitmq._load_messages(topic)
    
    for i, msg in enumerate(messages, 1):
        content = msg.get('content', {})
        if isinstance(content, dict) and 'resposta' in content:
            resposta = content['resposta']
            intencao = resposta.get('intencao', 'N/A')
            confirmacao = resposta.get('confirmacao', 'N/A')
            
            print(f"[{i}] {intencao}: {confirmacao}")
            
            # Se houver itens, mostra-os também
            if 'itens' in resposta and resposta['itens']:
                print("   Itens:")
                for item in resposta['itens']:
                    print(f"   - {item}")
                    
            print()

def main():
    """Menu principal do script"""
    print("🚀 STELLA AGENT - TESTES RABBITMQ MOCK")
    print("=" * 50)
    
    while True:
        print("\nOpções:")
        print("1. Publicar comandos de teste")
        print("2. Processar comandos")
        print("3. Visualizar respostas")
        print("4. Limpar tópicos")
        print("5. Mostrar status dos tópicos")
        print("6. Sair")
        
        choice = input("\nEscolha uma opção (1-6): ").strip()
        
        if choice == '1':
            publish_test_commands()
        
        elif choice == '2':
            process_commands()
        
        elif choice == '3':
            view_responses()
        
        elif choice == '4':
            topic = input("Nome do tópico para limpar (comandos_stella/respostas_stella): ").strip()
            if topic:
                confirm = input(f"Tem certeza que deseja limpar o tópico '{topic}'? (s/n): ").strip().lower()
                if confirm == 's':
                    mock_rabbitmq.purge_topic(topic)
                    print(f"✅ Tópico '{topic}' limpo com sucesso")
                else:
                    print("Operação cancelada")
            else:
                print("Nome do tópico inválido")
        
        elif choice == '5':
            print("\n=== Status dos Tópicos ===")
            topics = mock_rabbitmq.list_topics()
            
            if not topics:
                print("Nenhum tópico encontrado.")
            else:
                for topic in topics:
                    size = mock_rabbitmq.get_topic_size(topic)
                    print(f"📂 {topic}: {size} mensagens")
        
        elif choice == '6':
            print("Saindo...")
            break
        
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    # Importa datetime somente aqui para evitar conflito no speech_processor.py
    from datetime import datetime
    main()
