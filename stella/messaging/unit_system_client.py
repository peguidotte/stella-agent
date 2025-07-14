"""
Cliente de Comunicação com Sistema da Unidade

Gerencia:
- Envio de notificações para o Sistema da Unidade
- Recebimento de configurações e comandos
- Payloads conforme especificado nas HUs
- Comunicação via fila (Redis/RabbitMQ)
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class NotificationType(Enum):
    """Tipos de notificação para o Sistema da Unidade"""
    # HU-01: Autenticação
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_LOCKOUT = "auth_lockout"
    
    # HU-02: Solicitação de retirada
    WITHDRAWAL_REQUEST = "withdrawal_request"
    WITHDRAWAL_TIMEOUT = "withdrawal_timeout"
    WITHDRAWAL_CANCELLED = "withdrawal_cancelled"
    
    # HU-03: Validação de retirada
    WITHDRAWAL_COMPLETED = "withdrawal_completed"
    VALIDATION_FAILURE = "validation_failure"


class UnitSystemClient:
    """Cliente para comunicação com Sistema da Unidade"""
    
    def __init__(self):
        self._mock_mode = True  # Para desenvolvimento sem infraestrutura real
        self.unit_id = "UNIT_001"  # Configurável
        self.is_connected = False
        
        # Configurações de conexão
        self.queue_name = "stella_notifications"
        self.redis_host = "localhost"
        self.redis_port = 6379
    
    async def connect(self) -> bool:
        """
        Conecta com o sistema de mensageria
        
        Returns:
            True se conectado com sucesso
        """
        if self._mock_mode:
            print("📡 Modo simulação: Conectado ao Sistema da Unidade")
            self.is_connected = True
            return True
        else:
            try:
                # TODO: Implementar conexão real com Redis/RabbitMQ
                # import redis.asyncio as redis
                # self.redis_client = redis.Redis(
                #     host=self.redis_host,
                #     port=self.redis_port,
                #     decode_responses=True
                # )
                # await self.redis_client.ping()
                # self.is_connected = True
                # return True
                return False
            except Exception as e:
                print(f"Erro ao conectar com sistema de mensageria: {e}")
                return False
    
    async def disconnect(self):
        """Desconecta do sistema de mensageria"""
        if self._mock_mode:
            print("📡 Desconectado do Sistema da Unidade")
        else:
            # TODO: Implementar desconexão real
            # if hasattr(self, 'redis_client'):
            #     await self.redis_client.close()
            pass
        
        self.is_connected = False
    
    async def send_auth_success(self, user_name: str, pin: str) -> bool:
        """
        Envia notificação de autenticação bem-sucedida (HU-01)
        
        Args:
            user_name: Nome do usuário autenticado
            pin: PIN utilizado
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.AUTH_SUCCESS.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "user_name": user_name,
                "pin": pin,
                "auth_method": "face_id_and_pin"
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_auth_failure(self, attempts: int, reason: str) -> bool:
        """
        Envia notificação de falha na autenticação (HU-01)
        
        Args:
            attempts: Número de tentativas realizadas
            reason: Motivo da falha
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.AUTH_FAILURE.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "attempts": attempts,
                "reason": reason,
                "max_attempts_reached": attempts >= 3
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_auth_lockout(self, duration_minutes: int) -> bool:
        """
        Envia notificação de bloqueio por tentativas excessivas (HU-01)
        
        Args:
            duration_minutes: Duração do bloqueio em minutos
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.AUTH_LOCKOUT.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "lockout_duration_minutes": duration_minutes,
                "locked_until": (datetime.now().timestamp() + duration_minutes * 60),
                "message": f"Sistema bloqueado por {duration_minutes} minutos devido a tentativas excessivas"
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_withdrawal_request(self, user_name: str, items: Dict[str, int], 
                                    outliers: Optional[Dict[str, Any]] = None) -> bool:
        """
        Envia solicitação de retirada (HU-02)
        
        Args:
            user_name: Nome do usuário
            items: Dicionário de itens solicitados
            outliers: Itens com quantidades atípicas detectadas
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.WITHDRAWAL_REQUEST.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "user_name": user_name,
                "requested_items": items,
                "outliers_detected": outliers or {},
                "status": "pending_confirmation"
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_withdrawal_timeout(self, user_name: str, items: Dict[str, int]) -> bool:
        """
        Envia notificação de timeout da solicitação (HU-02)
        
        Args:
            user_name: Nome do usuário
            items: Itens da solicitação que expirou
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.WITHDRAWAL_TIMEOUT.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "user_name": user_name,
                "requested_items": items,
                "timeout_reason": "no_confirmation_within_time_limit",
                "timeout_minutes": 10
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_withdrawal_completed(self, user_name: str, items: Dict[str, int], 
                                      validation_method: str) -> bool:
        """
        Envia confirmação de retirada completada (HU-03)
        
        Args:
            user_name: Nome do usuário
            items: Itens retirados
            validation_method: Método de validação usado
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.WITHDRAWAL_COMPLETED.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "user_name": user_name,
                "withdrawn_items": items,
                "validation_method": validation_method,
                "status": "completed"
            }
        }
        
        return await self._send_notification(payload)
    
    async def send_validation_failure(self, user_name: str, items: Dict[str, int], 
                                    reason: str) -> bool:
        """
        Envia falha na validação de retirada (HU-03)
        
        Args:
            user_name: Nome do usuário
            items: Itens da tentativa de retirada
            reason: Motivo da falha
            
        Returns:
            True se enviado com sucesso
        """
        payload = {
            "event_type": NotificationType.VALIDATION_FAILURE.value,
            "timestamp": datetime.now().isoformat(),
            "unit_id": self.unit_id,
            "data": {
                "user_name": user_name,
                "requested_items": items,
                "failure_reason": reason,
                "status": "validation_failed"
            }
        }
        
        return await self._send_notification(payload)
    
    async def _send_notification(self, payload: Dict[str, Any]) -> bool:
        """
        Envia uma notificação para o Sistema da Unidade
        
        Args:
            payload: Dados da notificação
            
        Returns:
            True se enviado com sucesso
        """
        if not self.is_connected:
            await self.connect()
        
        try:
            # Adiciona ID único à mensagem
            payload["message_id"] = str(uuid.uuid4())
            
            if self._mock_mode:
                print(f"📤 Enviando notificação: {payload['event_type']}")
                print(f"   Dados: {json.dumps(payload['data'], indent=2, ensure_ascii=False)}")
                return True
            else:
                # TODO: Implementar envio real
                # message = json.dumps(payload)
                # await self.redis_client.lpush(self.queue_name, message)
                # return True
                return False
                
        except Exception as e:
            print(f"Erro ao enviar notificação: {e}")
            return False
    
    async def check_stock_availability(self, items: Dict[str, int]) -> Dict[str, Any]:
        """
        Verifica disponibilidade de itens no estoque (HU-02)
        
        Args:
            items: Itens a verificar
            
        Returns:
            Dicionário com status de disponibilidade
        """
        if self._mock_mode:
            print(f"📦 Verificando estoque para: {items}")
            
            # Simula verificação de estoque
            result = {
                "available": {},
                "insufficient": {},
                "unavailable": []
            }
            
            for item, quantity in items.items():
                # Simula diferentes cenários
                import random
                stock_level = random.randint(0, 50)
                
                if stock_level == 0:
                    result["unavailable"].append(item)
                elif stock_level < quantity:
                    result["insufficient"][item] = {
                        "requested": quantity,
                        "available": stock_level
                    }
                else:
                    result["available"][item] = {
                        "requested": quantity,
                        "available": stock_level
                    }
            
            print(f"   Resultado: {result}")
            return result
        else:
            # TODO: Implementar consulta real ao Sistema da Unidade
            return {"available": items, "insufficient": {}, "unavailable": []}
    
    async def detect_outliers(self, items: Dict[str, int]) -> Dict[str, Any]:
        """
        Detecta quantidades atípicas baseado em histórico (HU-02)
        
        Args:
            items: Itens a analisar
            
        Returns:
            Dicionário com outliers detectados
        """
        if self._mock_mode:
            print(f"🔍 Analisando padrões para: {items}")
            
            # Simula detecção de outliers
            outliers = {}
            
            for item, quantity in items.items():
                # Simula média histórica e detecção
                import random
                historical_avg = random.randint(1, 10)
                
                if quantity > historical_avg * 3:  # 3x a média = outlier
                    outliers[item] = {
                        "requested": quantity,
                        "historical_average": historical_avg,
                        "outlier_factor": round(quantity / historical_avg, 1),
                        "alert_level": "high" if quantity > historical_avg * 5 else "medium"
                    }
            
            if outliers:
                print(f"   ⚠️ Outliers detectados: {outliers}")
            else:
                print("   ✅ Quantidades dentro do padrão normal")
            
            return outliers
        else:
            # TODO: Implementar análise real de padrões
            return {}
    
    def set_unit_id(self, unit_id: str):
        """Define o ID da unidade"""
        self.unit_id = unit_id
