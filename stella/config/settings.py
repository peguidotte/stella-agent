"""
Configurações do Sistema Stella

Gerencia todas as configurações da aplicação incluindo:
- PINs da unidade
- Timeouts e limites
- Configurações de hardware (câmera, microfone)
"""

import os
from typing import Dict, Any
import yaml
from pathlib import Path


class Settings:
    """Gerenciador de configurações do sistema"""
    
    def __init__(self, config_file: str = "stella_config.yaml"):
        """
        Inicializa as configurações
        
        Args:
            config_file: Arquivo de configuração YAML
        """
        self.config_file = Path(__file__).parent / config_file
        self._settings = self._load_default_settings()
        self._load_from_file()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Carrega configurações padrão"""
        return {
            # Configurações de autenticação (HU-01)
            "authentication": {
                "pin_length": 6,
                "max_pin_attempts": 3,
                "lockout_duration_minutes": 30,
                "require_name_confirmation": True
            },
            
            # Configurações de solicitação (HU-02)  
            "request": {
                "wake_word": "Stella",
                "confirmation_timeout_minutes": 10,
                "allow_concurrent_requests": False,
                "outlier_detection_enabled": True
            },
            
            # Configurações de validação (HU-03)
            "validation": {
                "max_face_id_attempts": 3,
                "face_id_confidence_threshold": 0.8,
                "allow_pin_fallback": True
            },
            
            # Configurações de hardware
            "hardware": {
                "camera_device_id": 0,
                "microphone_device_id": None,
                "speaker_device_id": None
            },
            
            # Configurações de sistema
            "system": {
                "unit_id": "UNIT_001",
                "log_level": "INFO",
                "data_retention_days": 30
            }
        }
    
    def _load_from_file(self):
        """Carrega configurações do arquivo YAML"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_settings = yaml.safe_load(f)
                    if file_settings:
                        self._merge_settings(file_settings)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
    
    def _merge_settings(self, new_settings: Dict[str, Any]):
        """Mescla novas configurações com as existentes"""
        def merge_dict(base: dict, update: dict):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self._settings, new_settings)
    
    def get(self, key_path: str, default=None):
        """
        Obtém uma configuração usando notação de ponto
        
        Args:
            key_path: Caminho da configuração (ex: 'authentication.pin_length')
            default: Valor padrão se não encontrado
            
        Returns:
            Valor da configuração
        """
        keys = key_path.split('.')
        value = self._settings
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Define uma configuração usando notação de ponto
        
        Args:
            key_path: Caminho da configuração
            value: Novo valor
        """
        keys = key_path.split('.')
        current = self._settings
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def save(self):
        """Salva as configurações atuais no arquivo"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self._settings, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    @property
    def unit_pin(self) -> str:
        """PIN atual da unidade (carregado do ambiente ou arquivo)"""
        # Primeiro tenta carregar do ambiente
        pin = os.getenv('STELLA_UNIT_PIN')
        if pin:
            return pin
        
        # Se não encontrar, usa um PIN padrão (deve ser alterado em produção)
        default_pin = self.get('authentication.default_pin', '123456')
        if not isinstance(default_pin, str):
            return '123456'  # Fallback to default if not a string
        return default_pin
    
    @unit_pin.setter
    def unit_pin(self, value: str):
        """Define um novo PIN para a unidade"""
        if len(value) != self.get('authentication.pin_length', 6):
            raise ValueError(f"PIN deve ter {self.get('authentication.pin_length')} dígitos")
        
        self.set('authentication.default_pin', value)
        self.save()
