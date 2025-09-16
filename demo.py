"""
Script de Demonstração do Stella Agent

Simula interações básicas com o sistema para testar os fluxos das HUs:
- HU-01: Autenticação de usuário
- HU-02: Solicitação de retirada de produto  
- HU-03: Validação de retirada de produto
"""

import asyncio
import sys
from pathlib import Path

# Adiciona o diretório stella ao path para importações
sys.path.insert(0, str(Path(__file__).parent))

from stella.core.session_manager import SessionManager, SessionState
from stella.agent.speech_processor import SpeechProcessor, VoiceCommand
from stella.face_id.face_recognizer import FaceRecognizer
from stella.messaging.unit_system_client import UnitSystemClient
from stella.config.settings import Settings


class StellaDemo:
    """Demonstração interativa do Stella Agent"""
    
    def __init__(self):
        print("🤖 Inicializando Stella Agent Demo...")
        self.settings = Settings()
        self.session_manager = SessionManager()
        self.speech_processor = SpeechProcessor()
        self.face_recognizer = FaceRecognizer()
        self.unit_system_client = UnitSystemClient()
    
    async def start_demo(self):
        """Inicia a demonstração interativa"""
        print("\n" + "="*60)
        print("🌟 STELLA AGENT - DEMONSTRAÇÃO INTERATIVA")
        print("="*60)
        print("\nEste demo simula os fluxos das Histórias de Usuário:")
        print("📋 HU-01: Autenticação de usuário")
        print("📦 HU-02: Solicitação de retirada de produto")
        print("✅ HU-03: Validação de retirada de produto")
        print("\n" + "-"*60)
        
        # Inicializa serviços
        await self._initialize_services()
        
        # Menu principal
        while True:
            choice = await self._show_main_menu()
            
            if choice == "1":
                await self._demo_authentication()
            elif choice == "2":
                await self._demo_withdrawal_request()
            elif choice == "3":
                await self._demo_withdrawal_validation()
            elif choice == "4":
                await self._demo_full_flow()
            elif choice == "5":
                await self._show_system_status()
            elif choice == "0":
                print("\n👋 Encerrando demonstração...")
                break
            else:
                print("❌ Opção inválida!")
            
            input("\n⏸️  Pressione Enter para continuar...")
    
    async def _initialize_services(self):
        """Inicializa os serviços necessários"""
        print("\n🔧 Inicializando serviços...")
        
        await self.session_manager.start()
        await self.speech_processor.start_listening()
        await self.face_recognizer.initialize_camera()
        await self.unit_system_client.connect()
        
        print("✅ Todos os serviços inicializados!")
    
    async def _show_main_menu(self):
        """Mostra o menu principal e retorna a escolha"""
        print("\n" + "="*40)
        print("🎯 MENU PRINCIPAL")
        print("="*40)
        print("1. 🔐 Demo HU-01: Autenticação")
        print("2. 📦 Demo HU-02: Solicitação de Retirada")
        print("3. ✅ Demo HU-03: Validação de Retirada")
        print("4. 🔄 Demo Fluxo Completo")
        print("5. 📊 Status do Sistema")
        print("0. 🚪 Sair")
        print("-"*40)
        
        return input("Escolha uma opção: ").strip()
    
    async def _demo_authentication(self):
        """Demonstra o fluxo de autenticação (HU-01)"""
        print("\n" + "🔐 DEMO: AUTENTICAÇÃO DE USUÁRIO (HU-01)")
        print("-"*50)
        
        # Simula ativação por voz
        print("\n1️⃣ Simulando comando de voz: 'Stella, autenticação'")
        await self.speech_processor.speak("Olá! Vou ajudá-lo com a autenticação.")
        
        # Cria nova sessão
        session = self.session_manager.create_session()
        self.session_manager.set_session_state(SessionState.AUTHENTICATING)
        
        # Solicita PIN
        print("\n2️⃣ Solicitando PIN da unidade...")
        await self.speech_processor.speak("Por favor, informe o PIN da unidade.")
        
        pin = input("Digite o PIN (6 dígitos) ou 'voz:123456' para simular voz: ").strip()
        
        if pin.startswith("voz:"):
            pin = pin[4:]
            print(f"🎤 Reconhecimento de voz: '{pin}'")
        
        # Confirma PIN
        await self.speech_processor.speak(f"Você confirma esse PIN: {pin}?")
        confirmation = input("Confirma? (s/n): ").strip().lower()
        
        if confirmation != 's':
            print("❌ PIN não confirmado. Reiniciando processo...")
            return
        
        # Valida PIN
        correct_pin = self.settings.unit_pin
        attempts = self.session_manager.increment_pin_attempts()
        
        if pin == correct_pin:
            print("✅ PIN válido!")
            await self.speech_processor.speak("PIN válido. Agora vou associar sua identidade facial.")
            
            # Solicita nome
            user_name = input("\nDigite seu nome: ").strip()
            
            # Registra Face ID
            print(f"\n3️⃣ Registrando Face ID para {user_name}...")
            face_encoding = await self.face_recognizer.capture_and_register_face(user_name)
            
            if face_encoding:
                # Autentica usuário
                self.session_manager.authenticate_user(user_name, face_encoding)
                await self.speech_processor.speak(f"Autenticação concluída com sucesso! Bem-vindo, {user_name}.")
                
                # Notifica Sistema da Unidade
                await self.unit_system_client.send_auth_success(user_name, pin)
                
                print(f"🎉 Usuário {user_name} autenticado com sucesso!")
            else:
                print("❌ Falha no registro facial")
        else:
            print(f"❌ PIN inválido! Tentativa {attempts}/3")
            await self.speech_processor.speak(f"PIN inválido, você possui mais {3-attempts} tentativas")
            
            if attempts >= 3:
                print("🔒 Máximo de tentativas atingido. Sistema bloqueado!")
                self.session_manager.lock_system(30)
                await self.unit_system_client.send_auth_lockout(30)
            
            await self.unit_system_client.send_auth_failure(attempts, "invalid_pin")
    
    async def _demo_withdrawal_request(self):
        """Demonstra solicitação de retirada (HU-02)"""
        print("\n" + "📦 DEMO: SOLICITAÇÃO DE RETIRADA (HU-02)")
        print("-"*50)
        
        session = self.session_manager.get_current_session()
        if not session or session.state != SessionState.AUTHENTICATED:
            print("❌ Usuário deve estar autenticado primeiro!")
            return
        
        print(f"\n👤 Usuário autenticado: {session.user_name}")
        
        # Simula ativação
        print("\n1️⃣ Simulando comando: 'Stella'")
        await self.speech_processor.speak("Sim, estou ouvindo. O que você precisa?")
        
        # Solicita itens
        print("\n2️⃣ Processando solicitação...")
        request_text = input("Digite sua solicitação (ex: 'preciso de 10 seringas de 5ml'): ")
        
        command = self.speech_processor.process_voice_input(request_text)
        
        if command == VoiceCommand.WITHDRAWAL_REQUEST:
            items = self.speech_processor.extract_withdrawal_items(request_text)
            
            if items:
                print(f"\n📋 Itens identificados: {items}")
                
                # Verifica estoque
                print("\n3️⃣ Verificando disponibilidade no estoque...")
                stock_status = await self.unit_system_client.check_stock_availability(items)
                
                # Detecta outliers
                outliers = await self.unit_system_client.detect_outliers(items)
                
                # Mostra resumo
                print("\n📊 Resumo da solicitação:")
                for item, qty in items.items():
                    print(f"   • {item}: {qty} unidades")
                
                if outliers:
                    print("\n⚠️ Quantidades atípicas detectadas:")
                    for item, data in outliers.items():
                        print(f"   • {item}: {data['requested']} (média: {data['historical_average']})")
                
                # Confirma solicitação
                await self.speech_processor.speak("Confirma esses itens para retirada?")
                confirmation = input("\nDeseja confirmar essa retirada? (s/n): ").strip().lower()
                
                if confirmation == 's':
                    # Cria solicitação
                    if self.session_manager.create_withdrawal_request(items):
                        self.session_manager.confirm_withdrawal_request()
                        await self.unit_system_client.send_withdrawal_request(
                            session.user_name or "Unknown", items, outliers
                        )
                        print("✅ Solicitação confirmada! Prosseguindo para validação...")
                    else:
                        print("❌ Erro ao criar solicitação")
                else:
                    print("❌ Solicitação cancelada pelo usuário")
            else:
                print("❌ Não foi possível identificar itens na solicitação")
        else:
            print("❌ Comando não reconhecido como solicitação de retirada")
    
    async def _demo_withdrawal_validation(self):
        """Demonstra validação de retirada (HU-03)"""
        print("\n" + "✅ DEMO: VALIDAÇÃO DE RETIRADA (HU-03)")
        print("-"*50)
        
        session = self.session_manager.get_current_session()
        if not session or session.state != SessionState.VALIDATING_WITHDRAWAL:
            print("❌ Deve haver uma solicitação de retirada ativa!")
            return
        
        if not session.withdrawal_request:
            print("❌ Nenhuma solicitação encontrada!")
            return
        
        print(f"\n👤 Usuário: {session.user_name}")
        print(f"📦 Itens para retirada: {session.withdrawal_request.items}")
        
        # Validação por Face ID
        print("\n1️⃣ Iniciando validação por Face ID...")
        await self.speech_processor.speak("Por favor, posicione seu rosto para validação.")
        
        if not session.user_name:
            print("❌ Nome do usuário não encontrado na sessão!")
            return
        
        for attempt in range(1, 4):
            print(f"\nTentativa {attempt}/3 de reconhecimento facial...")
            input("Pressione Enter para simular captura facial...")
            
            success = await self.face_recognizer.validate_face(session.user_name)
            
            if success:
                print("✅ Identidade validada com sucesso!")
                await self.speech_processor.speak("Identidade confirmada. Retirada autorizada!")
                
                # Completa retirada
                self.session_manager.complete_withdrawal()
                await self.unit_system_client.send_withdrawal_completed(
                    session.user_name,
                    session.withdrawal_request.items,
                    "face_id"
                )
                
                print("🎉 Retirada completada com sucesso!")
                return
            else:
                self.session_manager.increment_face_id_attempts()
                
                if attempt < 3:
                    await self.speech_processor.speak("Não consegui reconhecer. Tente novamente.")
                else:
                    await self.speech_processor.speak(
                        "Última tentativa de reconhecimento facial. Posicione-se corretamente."
                    )
        
        # Fallback para PIN
        print("\n2️⃣ Face ID falhou. Oferecendo fallback para PIN...")
        await self.speech_processor.speak(
            "Não conseguimos reconhecer seu rosto. Deseja inserir o PIN manual?"
        )
        
        use_pin = input("Deseja usar PIN como alternativa? (s/n): ").strip().lower()
        
        if use_pin == 's':
            pin = input("Digite o PIN: ").strip()
            
            if pin == self.settings.unit_pin:
                print("✅ PIN válido! Retirada autorizada.")
                await self.speech_processor.speak("PIN confirmado. Retirada autorizada!")
                
                self.session_manager.complete_withdrawal()
                await self.unit_system_client.send_withdrawal_completed(
                    session.user_name,
                    session.withdrawal_request.items,
                    "pin_fallback"
                )
                
                print("🎉 Retirada completada com PIN!")
            else:
                print("❌ PIN inválido! Validação falhou.")
                await self.unit_system_client.send_validation_failure(
                    session.user_name,
                    session.withdrawal_request.items,
                    "invalid_pin_fallback"
                )
        else:
            print("❌ Validação cancelada pelo usuário")
            await self.unit_system_client.send_validation_failure(
                session.user_name,
                session.withdrawal_request.items,
                "user_cancelled"
            )
    
    async def _demo_full_flow(self):
        """Demonstra o fluxo completo das 3 HUs"""
        print("\n" + "🔄 DEMO: FLUXO COMPLETO")
        print("-"*50)
        print("Executando sequência: HU-01 → HU-02 → HU-03")
        
        await self._demo_authentication()
        
        session = self.session_manager.get_current_session()
        if session and session.state == SessionState.AUTHENTICATED:
            await self._demo_withdrawal_request()
            
            if session.state == SessionState.VALIDATING_WITHDRAWAL:
                await self._demo_withdrawal_validation()
    
    async def _show_system_status(self):
        """Mostra status atual do sistema"""
        print("\n" + "📊 STATUS DO SISTEMA")
        print("-"*40)
        
        session = self.session_manager.get_current_session()
        
        print(f"🔒 Sistema bloqueado: {'Sim' if self.session_manager.is_system_locked() else 'Não'}")
        print(f"👤 Sessão ativa: {'Sim' if session else 'Não'}")
        
        if session:
            print(f"   • Usuário: {session.user_name or 'N/A'}")
            print(f"   • Estado: {session.state.value}")
            print(f"   • Tentativas PIN: {session.pin_attempts}")
            print(f"   • Tentativas Face ID: {session.face_id_attempts}")
            
            if session.withdrawal_request:
                print(f"   • Solicitação ativa: {session.withdrawal_request.items}")
        
        print(f"📷 Câmera ativa: {'Sim' if self.face_recognizer.camera_active else 'Não'}")
        print(f"🎤 Escuta ativa: {'Sim' if self.speech_processor.is_listening else 'Não'}")
        print(f"📡 Conectado ao sistema: {'Sim' if self.unit_system_client.is_connected else 'Não'}")
        
        # Usuários registrados
        users = self.face_recognizer.get_registered_users()
        print(f"👥 Usuários registrados: {len(users)}")
        for user in users:
            print(f"   • {user}")


async def main():
    """Função principal da demonstração"""
    demo = StellaDemo()
    try:
        await demo.start_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
    finally:
        print("\n🔧 Limpando recursos...")
        # Cleanup seria feito aqui


if __name__ == "__main__":
    print("🚀 Iniciando Stella Agent Demo...")
    asyncio.run(main())
