"""
Configurações do Sistema Stella

Gerencia todas as configurações da aplicação incluindo:
- PINs da unidade
- Timeouts e limites
- Configurações de hardware (câmera, microfone)
"""

import os
from typing import Any, Dict, Optional
import yaml
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / '.env'
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:  # pragma: no cover - fallback quando .env não existe
    load_dotenv()


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
        self._load_env_settings()

    # --- Environment helpers -------------------------------------------------

    @staticmethod
    def _get_bool_env(name: str, default: bool = False) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "t", "yes", "y"}

    @staticmethod
    def _get_int_env(name: str, default: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _load_env_settings(self) -> None:
        """Carrega configurações provenientes de variáveis de ambiente."""
        self.mock_gemini: bool = self._get_bool_env('MOCK_GEMINI', False)
        self.mock_database: bool = self._get_bool_env('MOCK_DATABASE', False)
        self.inventory_api_url: str = os.getenv('INVENTORY_API_URL', 'http://localhost:8080')
        self.gemini_api_key: Optional[str] = os.getenv('GEMINI_API_KEY')
        self.gemini_model_id: str = os.getenv('GEMINI_MODEL_ID', 'gemini-2.5-flash')
        self.session_ttl_seconds: int = self._get_int_env('SESSION_TTL_SECONDS', 3 * 60)
        self.low_stock_threshold: int = self._get_int_env('STELLA_LOW_STOCK_THRESHOLD', 20)
        self.critical_stock_threshold: int = self._get_int_env('STELLA_CRITICAL_STOCK_THRESHOLD', 5)
        self.cloudamqp_url: Optional[str] = os.getenv('CLOUDAMQP_URL')
        self.pusher_app_id: Optional[str] = os.getenv('PUSHER_APP_ID')
        self.pusher_key: Optional[str] = os.getenv('PUSHER_KEY')
        self.pusher_secret: Optional[str] = os.getenv('PUSHER_SECRET')
        self.pusher_cluster: str = os.getenv('PUSHER_CLUSTER', 'us2')
        self.pusher_channel: str = os.getenv('STELLA_CHANNEL', 'private-agent-123')

    def pusher_credentials(self) -> Dict[str, Optional[str]]:
        """Retorna credenciais configuradas do Pusher."""
        return {
            'PUSHER_APP_ID': self.pusher_app_id,
            'PUSHER_KEY': self.pusher_key,
            'PUSHER_SECRET': self.pusher_secret,
            'PUSHER_CLUSTER': self.pusher_cluster,
        }

    def missing_pusher_credentials(self) -> list[str]:
        """Lista as variáveis obrigatórias do Pusher que não foram configuradas."""
        return [key for key, value in self.pusher_credentials().items() if not value]
    
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


settings = Settings()
