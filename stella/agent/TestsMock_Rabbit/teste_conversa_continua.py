"""
Teste Rápido da Conversa Contínua com Stella
Demonstra o funcionamento do sistema de conversa com contexto
"""

import sys
import time
from pathlib import Path

# Adiciona o diretório stella ao path
sys.path.insert(0, str(Path(__file__).parent))

from stella.agent.conversation_manager import conversation_manager
from loguru import logger

def test_continuous_conversation():
    """Testa uma conversa contínua simulada"""
    print("=" * 60)
    print("🧪 TESTE DE CONVERSA CONTÍNUA COM STELLA")
    print("=" * 60)
    
    # Inicia o consumidor da IA
    conversation_manager.start_consumer()
    
    # Simulação de conversa
    conversation_id = "test_session"
    user_name = "Dr. Silva"
    
    messages = [
        "Olá Stella, como você está?",
        "Preciso de algumas seringas para o setor de emergência",
        "Quero 10 seringas de 5ml e 5 seringas de 10ml",
        "E também preciso de luvas, você tem tamanho médio?",
        "Perfeito! Pode registrar a retirada de 2 caixas de luvas médias também?",
        "Obrigado! Ah, você pode me lembrar o que eu pedi hoje?",
        "Certo, agora preciso cancelar as seringas de 5ml",
        "Muito obrigado pela ajuda!"
    ]
    
    print(f"👤 Usuário: {user_name}")
    print(f"🆔 Sessão: {conversation_id}")
    print("-" * 60)
    
    try:
        for i, message in enumerate(messages, 1):
            print(f"\n[{i}/{len(messages)}] 👤 {user_name}: {message}")
            
            # Envia mensagem
            success = conversation_manager.send_user_message(message, conversation_id, user_name)
            
            if success:
                print("🤖 Stella está processando...")
                
                # Aguarda resposta
                response = conversation_manager.get_ai_response(timeout=15.0)
                
                if response:
                    ai_message = response.get('response', 'Erro na resposta')
                    print(f"🤖 Stella: {ai_message}")
                else:
                    print("❌ Timeout na resposta da IA")
                    
                # Pausa entre mensagens
                time.sleep(1)
            else:
                print("❌ Erro ao enviar mensagem")
                
        # Mostra histórico final
        print("\n" + "=" * 60)
        print("📝 HISTÓRICO FINAL DA CONVERSA")
        print("=" * 60)
        
        history = conversation_manager.get_conversation_history(conversation_id)
        if history:
            for msg in history['messages']:
                role = "👤 Usuário" if msg['role'] == 'user' else "🤖 Stella"
                print(f"{role}: {msg['content'][:100]}...")
                
        print(f"\n💬 Total de mensagens na conversa: {len(history['messages']) if history else 0}")
        
    except Exception as e:
        logger.error(f"Erro durante o teste: {e}")
        
    finally:
        # Para o consumidor
        conversation_manager.stop_consumer()
        print("\n🏁 Teste finalizado!")


def test_multiple_conversations():
    """Testa múltiplas conversas simultâneas"""
    print("=" * 60)
    print("🧪 TESTE DE MÚLTIPLAS CONVERSAS")
    print("=" * 60)
    
    conversation_manager.start_consumer()
    
    try:
        # Conversa 1
        conversation_manager.send_user_message("Olá, sou da enfermaria", "conv_1", "Enfermeira Ana")
        time.sleep(0.5)
        
        # Conversa 2  
        conversation_manager.send_user_message("Oi, sou do centro cirúrgico", "conv_2", "Dr. João")
        time.sleep(0.5)
        
        # Continua conversa 1
        conversation_manager.send_user_message("Preciso de termômetros", "conv_1", "Enfermeira Ana")
        time.sleep(0.5)
        
        # Continua conversa 2
        conversation_manager.send_user_message("Preciso de instrumentos cirúrgicos", "conv_2", "Dr. João")
        
        # Aguarda respostas
        print("⏳ Aguardando respostas...")
        time.sleep(5)
        
        # Consome respostas
        for i in range(4):
            response = conversation_manager.get_ai_response(timeout=2.0)
            if response:
                conv_id = response.get('conversation_id', 'unknown')
                user = response.get('user_name', 'unknown')
                message = response.get('response', '')[:100]
                print(f"📧 [{conv_id}] {user}: {message}...")
                
        # Lista conversas
        print("\n📊 CONVERSAS ATIVAS:")
        conversations = conversation_manager.list_conversations()
        for conv in conversations:
            print(f"- {conv['conversation_id']}: {conv['user_name']} ({conv['message_count']} msgs)")
            
    finally:
        conversation_manager.stop_consumer()
        print("\n🏁 Teste de múltiplas conversas finalizado!")


if __name__ == "__main__":
    print("Escolha o teste:")
    print("1. Conversa contínua simples")
    print("2. Múltiplas conversas")
    print("3. Ambos")
    
    choice = input("Opção (1-3): ").strip()
    
    if choice == "1":
        test_continuous_conversation()
    elif choice == "2":
        test_multiple_conversations()
    elif choice == "3":
        test_continuous_conversation()
        print("\n" + "="*60 + "\n")
        test_multiple_conversations()
    else:
        print("Opção inválida. Executando teste simples...")
        test_continuous_conversation()
