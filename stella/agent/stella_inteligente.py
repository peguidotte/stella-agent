"""
Stella Chat Inteligente - Usando Gemini Real
Integra o command_interpreter do speech_processor com conversa contínua
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Configura ambiente
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Importa as funções já configuradas do speech_processor
from speech_processor import command_interpreter, load_estoque_data
from loguru import logger

# Configura logger
logger.remove()
logger.add(sys.stderr, level="INFO")

class StellaInteligente:
    """Chat inteligente com Stella usando o Gemini do speech_processor"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_name = "Usuário"
        self.pedidos_sessao = []  # Pedidos da sessão atual
        
    def add_to_history(self, role, message):
        """Adiciona mensagem ao histórico"""
        self.conversation_history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
    def process_with_context(self, user_message):
        """Processa mensagem mantendo contexto"""
        try:
            # Adiciona ao histórico
            self.add_to_history("user", user_message)
            
            # Cria comando contextualizado
            context_info = ""
            
            # Se há histórico, adiciona contexto
            if len(self.conversation_history) > 1:
                recent_messages = []
                for msg in self.conversation_history[-6:]:  # Últimas 6 mensagens
                    role_name = self.user_name if msg["role"] == "user" else "Stella"
                    recent_messages.append(f"{role_name}: {msg['content']}")
                
                context_info = f"\n\nCONTEXTO DA CONVERSA:\n" + "\n".join(recent_messages)
            
            # Se há pedidos na sessão, adiciona
            if self.pedidos_sessao:
                context_info += f"\n\nPEDIDOS DESTA SESSÃO:\n" + "\n".join(self.pedidos_sessao)
            
            # Comando completo para o interpretador
            comando_completo = f"""
USUÁRIO: {user_message}

INSTRUÇÕES PARA STELLA:
- Mantenha uma conversa natural e contínua
- Use o contexto anterior para entender referências
- Seja amigável e prestativa
- Se for cumprimento, responda adequadamente
- Se perguntar sobre pedidos anteriores, consulte o contexto
- Se for sobre materiais, forneça informações detalhadas
{context_info}

Responda de forma conversacional e natural:
"""
            
            # Usa o interpretador do speech_processor
            resultado = command_interpreter(comando_completo)
            
            if resultado and isinstance(resultado, dict):
                resposta = resultado.get('confirmacao', 'Posso ajudar com mais alguma coisa?')
                
                # Se foi um pedido, adiciona à lista
                if resultado.get('intencao') == 'registrar_retirada':
                    itens = resultado.get('itens', [])
                    for item in itens:
                        if isinstance(item, dict):
                            pedido = f"{item.get('quantidade', '')} {item.get('item', '')}"
                            self.pedidos_sessao.append(pedido)
                        else:
                            self.pedidos_sessao.append(str(item))
                        
            else:
                # Fallback para resposta natural
                resposta = self.generate_natural_response(user_message)
            
            # Adiciona resposta ao histórico
            self.add_to_history("assistant", resposta)
            
            logger.success(f"Processado comando para {self.user_name}")
            return resposta
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            error_response = "Desculpe, tive um problema. Pode repetir sua mensagem?"
            self.add_to_history("assistant", error_response)
            return error_response
    
    def generate_natural_response(self, message):
        """Gera resposta natural baseada na mensagem"""
        message_lower = message.lower()
        
        # Detecção de intenções
        if any(greeting in message_lower for greeting in ["olá", "oi", "ola", "hey", "e aí"]):
            if len(self.conversation_history) <= 2:
                return f"Olá {self.user_name}! Sou a Stella, assistente do almoxarifado. Como posso ajudar você hoje?"
            else:
                return "Oi! Em que mais posso ajudar?"
                
        elif any(word in message_lower for word in ["tudo bem", "como vai", "como está"]):
            return "Estou muito bem, obrigada! Pronta para ajudar com o almoxarifado. E você, como está?"
            
        elif any(word in message_lower for word in ["nome", "quem é", "você é"]):
            return "Sou a Stella, sua assistente virtual do almoxarifado hospitalar. Estou aqui para ajudar com materiais e suprimentos!"
            
        elif any(word in message_lower for word in ["pedido", "pedi", "solicitei", "último"]):
            if self.pedidos_sessao:
                return f"Você pediu: {', '.join(self.pedidos_sessao)}. Precisa de mais alguma coisa?"
            else:
                return "Ainda não vejo pedidos nesta conversa. O que você precisa?"
                
        elif any(word in message_lower for word in ["obrigad", "valeu", "thanks"]):
            return "De nada! Foi um prazer ajudar. Se precisar de mais alguma coisa, estarei aqui!"
            
        else:
            return "Entendi! Como assistente do almoxarifado, posso ajudar com seringas, luvas, gazes e outros materiais. O que você precisa?"
    
    def start_chat(self):
        """Inicia o chat inteligente"""
        print("🧠 STELLA INTELIGENTE - GEMINI + CONTEXTO")
        print("=" * 50)
        
        # Configuração
        self.user_name = input("Seu nome: ").strip() or "Usuário"
        print(f"\n✅ Olá {self.user_name}! Sistema inteligente ativo.")
        print("Digite 'sair' para encerrar, 'historico' para ver conversa\n")
        
        # Mensagem inicial
        initial_message = f"Olá {self.user_name}! Sou a Stella, sua assistente inteligente do almoxarifado. Como posso ajudar você hoje?"
        print(f"Stella: {initial_message}")
        self.add_to_history("assistant", initial_message)
        
        try:
            while True:
                # Input do usuário
                user_input = input(f"\n{self.user_name}: ").strip()
                
                if not user_input:
                    continue
                    
                # Comandos especiais
                if user_input.lower() in ['sair', 'exit', 'tchau']:
                    print("Stella: Até mais! Foi um prazer conversar com você! 👋")
                    break
                elif user_input.lower() == 'historico':
                    self.show_history()
                    continue
                elif user_input.lower() == 'pedidos':
                    self.show_pedidos()
                    continue
                
                # Processa com IA
                print("🧠 Stella está processando...")
                ai_response = self.process_with_context(user_input)
                print(f"Stella: {ai_response}")
                
        except KeyboardInterrupt:
            print("\n\nTchau! 👋")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            
    def show_history(self):
        """Mostra histórico da conversa"""
        print("\n" + "="*50)
        print("📝 HISTÓRICO DA CONVERSA")
        print("="*50)
        
        for i, msg in enumerate(self.conversation_history, 1):
            role_name = self.user_name if msg['role'] == 'user' else 'Stella'
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            print(f"{i:2d}. {role_name}: {content}")
            
        print(f"\n💬 Total: {len(self.conversation_history)} mensagens")
        print("="*50)
        
    def show_pedidos(self):
        """Mostra pedidos da sessão"""
        print("\n" + "="*30)
        print("📦 PEDIDOS DESTA SESSÃO")
        print("="*30)
        
        if self.pedidos_sessao:
            for i, pedido in enumerate(self.pedidos_sessao, 1):
                print(f"{i}. {pedido}")
        else:
            print("Nenhum pedido registrado ainda.")
            
        print("="*30)


def main():
    """Função principal"""
    try:
        chat = StellaInteligente()
        chat.start_chat()
    except Exception as e:
        print(f"Erro ao iniciar: {e}")
        print("Verifique se o arquivo GEMINI_API_KEY.env existe e está configurado.")


if __name__ == "__main__":
    main()
