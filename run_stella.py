#!/usr/bin/env python3
"""
Script de inicialização para executar o Stella Agent corretamente
"""

import sys
import os
from loguru import logger

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa e executa o módulo speech_processor
try:
    from stella.agent import speech_processor
    
    # Executa o fluxo principal
    if __name__ == "__main__":
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
    logger.error(f"Erro ao iniciar Stella Agent: {e}")
    raise
