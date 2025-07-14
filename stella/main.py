"""
Stella Agent - Ponto de Entrada Principal

Sistema de IA para gerenciamento de almoxarifado com:
- Autenticação por Face ID e PIN (HU-01)
- Solicitação de retirada de produtos por voz (HU-02) 
- Validação de retirada com confirmação de identidade (HU-03)
"""

import asyncio
import logging
from loguru import logger

from stella.core.session_manager import SessionManager
from stella.voice.speech_processor import SpeechProcessor
from stella.face_id.face_recognizer import FaceRecognizer
from stella.messaging.unit_system_client import UnitSystemClient
from stella.config.settings import Settings


class StellaAgent:
    """
    Classe principal do agente Stella
    Gerencia o ciclo de vida da aplicação e coordena os módulos
    """
    
    def __init__(self):
        """Inicializa o agente Stella com todos os módulos necessários"""
        logger.info("Inicializando Stella Agent...")
        
        # Carrega configurações
        self.settings = Settings()
        
        # Inicializa módulos
        self.session_manager = SessionManager()
        self.speech_processor = SpeechProcessor()
        self.face_recognizer = FaceRecognizer()
        self.unit_system_client = UnitSystemClient()
        
        # Estado da aplicação
        self.is_running = False
        self.current_session = None
        
        logger.info("Stella Agent inicializado com sucesso")
    
    async def start(self):
        """Inicia o agente Stella"""
        logger.info("Iniciando Stella Agent...")
        self.is_running = True
        
        try:
            # Inicia os serviços necessários
            await self._initialize_services()
            
            # Loop principal da aplicação
            await self._main_loop()
            
        except KeyboardInterrupt:
            logger.info("Recebido sinal de interrupção")
        except Exception as e:
            logger.error(f"Erro durante execução: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Para o agente Stella de forma limpa"""
        logger.info("Parando Stella Agent...")
        self.is_running = False
        
        # Cleanup dos recursos
        await self._cleanup_services()
        
        logger.info("Stella Agent parado")
    
    async def _initialize_services(self):
        """Inicializa todos os serviços necessários"""
        logger.info("Inicializando serviços...")
        
        # TODO: Implementar inicialização dos serviços
        # - Configurar reconhecimento de voz
        # - Inicializar câmera para Face ID  
        # - Conectar com sistema de mensageria
        # - Carregar configurações da unidade
        
        pass
    
    async def _cleanup_services(self):
        """Limpa recursos dos serviços"""
        logger.info("Limpando recursos...")
        
        # TODO: Implementar cleanup
        # - Fechar conexões de rede
        # - Liberar recursos de câmera/áudio
        # - Salvar estado se necessário
        
        pass
    
    async def _main_loop(self):
        """Loop principal da aplicação"""
        logger.info("Entrando no loop principal...")
        
        while self.is_running:
            try:
                # TODO: Implementar lógica principal
                # 1. Escutar pela palavra-chave "Stella"
                # 2. Processar comandos de voz
                # 3. Gerenciar fluxos das HUs (autenticação, solicitação, validação)
                # 4. Enviar notificações ao Sistema da Unidade
                
                # Por enquanto, apenas aguarda
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(1)


async def main():
    """Função principal de entrada"""
    # Configurar logging
    logger.add("stella.log", rotation="1 day", retention="30 days")
    logger.info("=== Iniciando Stella Agent ===")
    
    # Criar e iniciar o agente
    stella = StellaAgent()
    await stella.start()


if __name__ == "__main__":
    # Executar o agente
    asyncio.run(main())
