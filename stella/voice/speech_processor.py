"""
Processador de Voz e Comandos

Gerencia:
- Detecção da palavra de ativação "Stella"
- Reconhecimento de fala para comandos
- Síntese de voz para respostas
- Processamento básico de linguagem natural
"""

import asyncio
import re
from typing import Optional, Dict, List
from enum import Enum


class VoiceCommand(Enum):
    """Tipos de comandos de voz reconhecidos"""
    WAKE_UP = "wake_up"  # "Stella"
    AUTHENTICATION = "authentication"  # "Autenticação" 
    WITHDRAWAL_REQUEST = "withdrawal_request"  # Solicitação de itens
    CONFIRMATION_YES = "yes"  # Confirmações positivas
    CONFIRMATION_NO = "no"  # Confirmações negativas
    PIN_INPUT = "pin_input"  # Entrada de PIN
    UNKNOWN = "unknown"


class SpeechProcessor:
    """Processador principal de voz e comandos"""
    
    def __init__(self):
        self.is_listening = False
        self.is_active = False  # True quando "Stella" foi detectada
        self._mock_mode = True  # Para desenvolvimento sem hardware real
        
        # Padrões de reconhecimento
        self.wake_patterns = [
            r"\bstella\b",
            r"\bestela\b"  # Variação comum de pronúncia
        ]
        
        self.auth_patterns = [
            r"\bautenticação\b",
            r"\bautentica\b",
            r"\bautenticar\b",
            r"\blogin\b"
        ]
        
        self.request_patterns = [
            r"\bpreciso\b.*\bde\b",
            r"\bquero\b.*",
            r"\bsolici[a-z]+\b",
            r"\bretirar\b",
            r"\bpegar\b"
        ]
        
        self.yes_patterns = [
            r"\bsim\b",
            r"\bconfirmo\b",
            r"\bokay?\b",
            r"\btá\b",
            r"\bperfeito\b"
        ]
        
        self.no_patterns = [
            r"\bnão\b",
            r"\bnao\b", 
            r"\bnegativo\b",
            r"\bcancela\b"
        ]
    
    async def start_listening(self):
        """Inicia o processamento de voz"""
        self.is_listening = True
        
        if self._mock_mode:
            print("🎤 Modo simulação: Processador de voz iniciado")
            print("💡 Dica: Digite comandos no console para simular entrada de voz")
        else:
            # TODO: Implementar inicialização real do microfone
            # import speech_recognition as sr
            # self.recognizer = sr.Recognizer()
            # self.microphone = sr.Microphone()
            pass
    
    async def stop_listening(self):
        """Para o processamento de voz"""
        self.is_listening = False
        self.is_active = False
        
        if self._mock_mode:
            print("🎤 Processador de voz parado")
    
    async def listen_for_wake_word(self) -> bool:
        """
        Escuta pela palavra de ativação "Stella"
        
        Returns:
            True se palavra de ativação foi detectada
        """
        if self._mock_mode:
            # Simula entrada de usuário no console
            print("\n🎧 Aguardando palavra de ativação 'Stella'...")
            print("Digite algo ou 'stella' para ativar:")
            
            # Em produção, isso seria um loop de escuta real
            await asyncio.sleep(0.1)
            return False
        else:
            # TODO: Implementar escuta real
            return False
    
    def process_voice_input(self, text: str) -> VoiceCommand:
        """
        Processa texto de entrada e classifica o comando
        
        Args:
            text: Texto reconhecido da fala
            
        Returns:
            Tipo de comando identificado
        """
        text_lower = text.lower().strip()
        
        # Verifica palavra de ativação
        if self._matches_patterns(text_lower, self.wake_patterns):
            self.is_active = True
            return VoiceCommand.WAKE_UP
        
        # Se não está ativo, ignora outros comandos
        if not self.is_active:
            return VoiceCommand.UNKNOWN
        
        # Verifica comando de autenticação
        if self._matches_patterns(text_lower, self.auth_patterns):
            return VoiceCommand.AUTHENTICATION
        
        # Verifica solicitação de retirada
        if self._matches_patterns(text_lower, self.request_patterns):
            return VoiceCommand.WITHDRAWAL_REQUEST
        
        # Verifica confirmações
        if self._matches_patterns(text_lower, self.yes_patterns):
            return VoiceCommand.CONFIRMATION_YES
        
        if self._matches_patterns(text_lower, self.no_patterns):
            return VoiceCommand.CONFIRMATION_NO
        
        # Verifica se é entrada de PIN (sequência de dígitos)
        if re.match(r'^[0-9\s]+$', text_lower):
            return VoiceCommand.PIN_INPUT
        
        return VoiceCommand.UNKNOWN
    
    def extract_withdrawal_items(self, text: str) -> Dict[str, int]:
        """
        Extrai itens solicitados de uma frase
        
        Args:
            text: Texto da solicitação
            
        Returns:
            Dicionário com itens e quantidades
        """
        items = {}
        text_lower = text.lower()
        
        # Padrões básicos de extração
        # Ex: "preciso de 10 seringas de 5ml"
        patterns = [
            r'(\d+)\s+([a-z\s]+?)(?:\s+de\s+(\d+(?:\.\d+)?)\s*([a-z]+))?',
            r'(\d+)\s+([a-z\s]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                try:
                    quantity = int(match.group(1))
                    item_name = match.group(2).strip()
                    
                    # Adiciona especificação se houver (ex: "5ml")
                    if len(match.groups()) > 3 and match.group(3):
                        spec = f"{match.group(3)}{match.group(4) or ''}"
                        item_name = f"{item_name} {spec}"
                    
                    # Normaliza o nome do item
                    item_name = self._normalize_item_name(item_name)
                    
                    if item_name:
                        items[item_name] = quantity
                        
                except (ValueError, IndexError):
                    continue
        
        return items
    
    def extract_pin_digits(self, text: str) -> Optional[str]:
        """
        Extrai dígitos de PIN de uma frase
        
        Args:
            text: Texto com possível PIN
            
        Returns:
            PIN como string ou None se não encontrado
        """
        # Remove espaços e mantém apenas dígitos
        digits = re.sub(r'[^\d]', '', text)
        
        # Verifica se tem o tamanho correto (6 dígitos por padrão)
        if len(digits) == 6:
            return digits
        
        return None
    
    async def speak(self, text: str):
        """
        Sintetiza fala para resposta
        
        Args:
            text: Texto a ser falado
        """
        if self._mock_mode:
            print(f"🔊 Stella diz: {text}")
        else:
            # TODO: Implementar síntese de voz real
            # import pyttsx3
            # engine = pyttsx3.init()
            # engine.say(text)
            # engine.runAndWait()
            pass
    
    def deactivate(self):
        """Desativa o modo de escuta ativa"""
        self.is_active = False
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Verifica se texto corresponde a algum dos padrões"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _normalize_item_name(self, name: str) -> str:
        """
        Normaliza nome de item para consistência
        
        Args:
            name: Nome bruto do item
            
        Returns:
            Nome normalizado
        """
        # Remove caracteres desnecessários
        name = re.sub(r'[^\w\s.-]', '', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        
        # Padronizações comuns
        substitutions = {
            'seringa': 'seringa',
            'seringas': 'seringa',
            'luva': 'luva',
            'luvas': 'luva',
            'mascara': 'máscara',
            'mascaras': 'máscara',
            'gaze': 'gaze',
            'gazes': 'gaze'
        }
        
        for old, new in substitutions.items():
            name = re.sub(rf'\b{old}\b', new, name, flags=re.IGNORECASE)
        
        return name.title()  # Capitaliza primeira letra de cada palavra
