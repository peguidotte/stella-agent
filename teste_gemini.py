#!/usr/bin/env python3
"""
Teste específico para o interpretador de comandos com Gemini
"""

import sys
import os

# Adiciona o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stella.agent.speech_processor import command_interpreter

def test_gemini_interpreter():
    """Testa a interpretação de comandos com o Gemini"""
    print("🧪 TESTE DO INTERPRETADOR GEMINI")
    print("=" * 50)
    
    test_commands = [
        "preciso de 5 seringas de 10ml",
        "quanto tem de luva no estoque?",
        "peguei 3 caixas de gaze estéril",
        "onde fica o termômetro digital?",
        "cancelar o último registro"
    ]
    
    for i, comando in enumerate(test_commands, 1):
        print(f"\n[{i}] Testando: '{comando}'")
        try:
            resultado = command_interpreter(comando)
            if resultado:
                intencao = resultado.get('intencao', 'N/A')
                confirmacao = resultado.get('confirmacao', 'N/A')
                print(f"   ✅ Intenção: {intencao}")
                print(f"   💬 Confirmação: {confirmacao}")
                
                if 'itens' in resultado and resultado['itens']:
                    print(f"   📦 Itens: {resultado['itens']}")
            else:
                print("   ❌ Falha na interpretação")
        except Exception as e:
            print(f"   💥 Erro: {e}")

if __name__ == "__main__":
    test_gemini_interpreter()
