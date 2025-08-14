import json
import cv2
import numpy as np
from typing import Optional, List, Any
from pathlib import Path
import mediapipe as mp


class FaceRecognizer:
    """Gerenciador de reconhecimento facial"""
    
    def __init__(self):
        self.camera = None
        self.camera_active = False
        self._mock_mode = True  # Para pular o reconhecimento facial
        self.faces_db_path = Path(__file__).parent / "faces_db.json"
        self.face_encodings = self._load_faces_database()
        
        # Configurações
        self.confidence_threshold = 0.6  # Limite de confiança para reconhecimento
        self.capture_timeout = 10  # Timeout para captura em segundos
    
    async def initialize_camera(self) -> bool:
        """
        Inicializa a câmera para captura
        
        Returns:
            True se câmera foi inicializada com sucesso
        """
        return False
    
    async def close_camera(self):
        """Fecha a câmera"""
        pass
    
    async def capture_and_register_face(self, user_name: str) -> Optional[Any]:
        """
        Captura e registra uma nova face no sistema
        
        Args:
            user_name: Nome do usuário para registro
            
        Returns:
            Face encoding se sucesso, None se falha
        """
        pass
    
    async def validate_face(self, user_name: str) -> bool:
        """
        Valida identidade comparando rosto atual com rosto registrado
        
        Args:
            user_name: Nome do usuário para validação
            
        Returns:
            True se validação foi bem-sucedida
        """
        return False
    
    def is_face_registered(self, user_name: str) -> bool:
        """
        Verifica se usuário tem rosto registrado
        
        Args:
            user_name: Nome do usuário
            
        Returns:
            True se tem rosto registrado
        """
        return False

    def get_registered_users(self) -> List[str]:
        """
        Retorna lista de usuários com rosto registrado
        
        Returns:
            Lista de nomes de usuários
        """
        return []
    
    def remove_user_face(self, user_name: str) -> bool:
        """
        Remove o rosto registrado de um usuário
        
        Args:
            user_name: Nome do usuário
            
        Returns:
            True se removido com sucesso
        """
        return False
    
    def _load_faces_database(self) -> dict:
        """Carrega banco de dados de rostos do arquivo"""
        return {}
    
    def _save_faces_database(self):
        """Salva banco de dados de rostos no arquivo"""
        pass
    
    async def capture_frame(self) -> Optional[Any]:
        """
        Captura um frame da câmera
        
        Returns:
            Frame capturado ou None se falha
        """
        pass
    
    def set_confidence_threshold(self, threshold: float):
        """
        Define limite de confiança para reconhecimento
        
        Args:
            threshold: Valor entre 0 e 1
        """
        pass


def test():
    """
    Função de teste simples para verificar instalação e câmera
    """
    print("🔍 TESTE DO SISTEMA STELLA AGENT")
    print("=" * 40)
    
    # 1. Testar imports
    try:
        print("📦 Testando imports...")
        print(f"✅ OpenCV: {cv2.__version__}")
        print(f"✅ MediaPipe: {mp.__version__}")
        print(f"✅ NumPy: {np.__version__}")
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False
    
    # 2. Testar conexão com câmera
    try:
        print("\n📷 Testando câmera...")
        camera = cv2.VideoCapture(0)
        
        if not camera.isOpened():
            print("❌ Não foi possível abrir a câmera")
            return False
        
        print("✅ Câmera conectada com sucesso!")
        
        # Capturar um frame de teste
        ret, frame = camera.read()
        if ret:
            height, width = frame.shape[:2]
            print(f"✅ Frame capturado: {width}x{height}")
        else:
            print("❌ Não foi possível capturar frame")
            camera.release()
            return False
        
        # Mostrar preview da câmera
        print("\n🎥 Mostrando preview da câmera...")
        print("Pressione ESC para fechar")
        
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            
            # Adicionar texto no frame
            cv2.putText(frame, "STELLA AGENT - Teste de Camera", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame, "Pressione ESC para sair", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Teste da Camera - STELLA AGENT', frame)
            
            # ESC para sair
            if cv2.waitKey(1) & 0xFF == 27:
                break
        
        # Limpar recursos
        camera.release()
        cv2.destroyAllWindows()
        
        print("✅ Teste da câmera concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar câmera: {e}")
        try:
            camera.release()
            cv2.destroyAllWindows()
        except:
            pass
        return False


if __name__ == "__main__":
    # Executar teste quando o arquivo for chamado diretamente
    test()