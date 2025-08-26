#!/usr/bin/env python3
"""
Script de inicialização para executar o Stella Agent com conversa contínua
Agora mantém contexto entre mensagens e simula comportamento assíncrono do RabbitMQ
"""

import sys
import os
from loguru import logger

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_legacy_mode():
    """Executa o modo legado (uma mensagem por vez)"""
    try:
        import speech_processor
        
        comando = speech_processor.get_command()
        if comando:
            print(f"Comando: {comando}\n")
            resultado = speech_processor.command_interpreter(comando)
            if resultado:
                resposta = speech_processor.process_action(resultado)
                print(f"Resposta: {resposta}")
            else:
                print("Comando não entendido. Tente reformular.")
        else:
            print("Nenhum comando válido para processar.")
            
    except Exception as e:
        logger.error(f"Erro ao iniciar Stella Agent (modo legado): {e}")
        raise

def run_conversation_mode():
    """Executa o novo modo de conversa contínua"""
    try:
        from conversation_manager import conversation_manager
        import time
        
        print("🤖 Iniciando Stella Agent em modo conversa contínua...")
        print("Para uma experiência interativa completa, use: python stella_chat.py")
        print("=" * 60)
        
        # Inicia o consumidor
        conversation_manager.start_consumer()
        
        # Verifica se há mensagens pendentes
        print("Verificando mensagens pendentes...")
        
        # Aguarda um pouco para processar mensagens
        time.sleep(2)
        
        # Consome respostas pendentes
        response_count = 0
        while True:
            response = conversation_manager.get_ai_response(timeout=1.0)
            if response:
                response_count += 1
                conv_id = response.get('conversation_id', 'unknown')
                ai_message = response.get('response', '')
                print(f"[{conv_id}] Stella: {ai_message[:100]}...")
            else:
                break
                
        if response_count == 0:
            print("Nenhuma mensagem pendente encontrada.")
            print("Para iniciar uma conversa:")
            print("1. Execute: python stella_chat.py (modo interativo)")
            print("2. Execute: python teste_conversa_continua.py (teste automático)")
        else:
            print(f"Processadas {response_count} mensagens pendentes.")
            
        conversation_manager.stop_consumer()
        
    except Exception as e:
        logger.error(f"Erro ao iniciar Stella Agent (modo conversa): {e}")
        raise

if __name__ == "__main__":
    print("Stella Agent - Escolha o modo de execução:")
    print("1. Modo Conversa Contínua (recomendado)")
    print("2. Modo Legado (uma mensagem por vez)")
    print("3. Chat Interativo")
    print("4. Teste Automático")
    
    choice = input("Opção (1-4, Enter para padrão=1): ").strip()
    
    if choice == "2":
        print("Executando em modo legado...")
        run_legacy_mode()
    elif choice == "3":
        print("Iniciando chat interativo...")
        os.system("python stella_inteligente.py")
    elif choice == "4":
        print("Iniciando teste automático...")
        os.system("python TestsMock_Rabbit/teste_conversa_continua.py")
    else:
        print("Executando em modo conversa contínua...")
        run_conversation_mode()
