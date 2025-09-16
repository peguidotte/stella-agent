import json
import cv2
import numpy as np
import time
from datetime import datetime
from typing import Optional, List, Any, Tuple
from pathlib import Path
from deepface import DeepFace
from loguru import logger

class FaceRecognizer:
    """Gerenciador de reconhecimento facial"""
    
    def __init__(self):
        self.camera = None
        self.camera_index = 0  # Índice da câmera (0 para webcam padrão)
        self.camera_active = False
        self._mock_mode = False  # Para pular o reconhecimento facial
        self.faces_db_path = Path(__file__).parent / "faces_db.json"
        
        # Configurações do DeepFace
        self.model_name = "VGG-Face"
        self.threshold = 0.4  # Threshold padrão para VGG-Face
        self.distance_metric = "cosine"
        
        # Configurações de captura
        self.confidence_threshold = 0.6  # Limite de confiança para reconhecimento
        self.capture_timeout = 10  # Timeout para captura em segundos
        self.embeddings_per_user = 6  # Quantos embeddings capturar por usuário
        self.capture_interval = 2  # Segundos entre capturas
        
        # Carregar banco DEPOIS de definir model_name
        self.face_encodings = self._load_faces_database()
        
        logger.success(f"FaceRecognizer inicializado com modelo {self.model_name}")
    
    def _test_deepface(self):
        """Testa se o DeepFace está funcionando"""
        try:
            # Teste simples para verificar se DeepFace funciona
            test_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            embedding = DeepFace.represent(test_img, model_name=self.model_name, enforce_detection=False)
            logger.success("DeepFace funcionando corretamente")
            return True
        except Exception as e:
            logger.error(f"Erro no DeepFace: {e}")
            return False
    
    def _detect_face_in_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Detecta e extrai rosto do frame usando DeepFace
        
        Args:
            frame: Frame da câmera
            
        Returns:
            Rosto detectado ou None se não encontrou
        """
        try:
            # Usar DeepFace para extrair rostos
            faces = DeepFace.extract_faces(img_path=frame, enforce_detection=False, detector_backend='opencv')
            
            if not faces or len(faces) == 0:
                return None
            
            # Se múltiplos rostos, pegar o maior (mais próximo)
            if len(faces) > 1:
                logger.debug(f"Detectados {len(faces)} rostos, usando o maior")
                # Ordenar por tamanho (área da face)
                faces = sorted(faces, key=lambda x: x['face'].shape[0] * x['face'].shape[1], reverse=True)
            
            face = faces[0]['face']
            
            # Converter para uint8 se necessário
            if face.dtype != np.uint8:
                face = (face * 255).astype(np.uint8)
            
            return face
            
        except Exception as e:
            logger.debug(f"Erro ao detectar rosto: {e}")
            return None
    
    def _extract_embedding(self, face: np.ndarray) -> Optional[np.ndarray]:
        """
        Extrai embedding do rosto usando DeepFace
        
        Args:
            face: Imagem do rosto
            
        Returns:
            Embedding ou None se falha
        """
        try:
            # Usar DeepFace.represent para extrair embedding
            embedding = DeepFace.represent(
                img_path=face, 
                model_name=self.model_name,
                enforce_detection=False
            )
            
            # DeepFace.represent retorna uma lista, pegar o primeiro embedding
            if isinstance(embedding, list) and len(embedding) > 0:
                return np.array(embedding[0]['embedding'])
            else:
                return np.array(embedding['embedding'])
            
        except Exception as e:
            logger.error(f"Erro ao extrair embedding: {e}")
            return None
    
    async def initialize_camera(self) -> bool:
        """
        Initialize camera for face recognition.
        
        Returns:
            True if camera initialized successfully, False otherwise
        """
        if self._mock_mode:
            logger.info("🔍 Modo mock ativado, pulando inicialização da câmera.")
            return True
        
        try:
            logger.info(f"Inicializando câmera no índice {self.camera_index}...")
            self.camera = cv2.VideoCapture(self.camera_index)
            if self.camera is None or not self.camera.isOpened():
                logger.error("Não foi possível abrir a câmera.")
                self.camera_active = False
                if self.camera is not None:
                    self.camera.release()
                return False
            
            # Configurar resolução
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            self.camera_active = True
            logger.success("Câmera inicializada com sucesso!")
            return True
            
        except cv2.error as e:
            logger.error(f"Erro ao abrir câmera: {e}")
            self.camera_active = False
            return False
        except Exception as e:
            logger.error(f"Erro ao inicializar câmera: {e}")
            self.camera_active = False
            return False
    
    async def close_camera(self):
        """Closes the camera and windows, releasing resources."""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        cv2.destroyAllWindows()
        self.camera_active = False
        logger.info("Câmera fechada.")
    
    async def capture_frame(self) -> Optional[np.ndarray]:
        """
        Captura um frame da câmera
        
        Returns:
            Frame capturado ou None se falha
        """
        if not self.camera_active or self.camera is None:
            logger.warning("Câmera não está ativa")
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.warning("Falha ao capturar frame")
            return None
        
        return frame
    
    async def register_face(self, user_name: str) -> bool:
        """
        Register a new face for a user
        Parameters:
            user_name: Name of the user to register
        Returns:
            True if registration was successful, False otherwise
        """
        if not self.camera_active:
            logger.error("Câmera não está ativa")
            return False
        
        logger.info(f"🎯 Iniciando cadastro para usuário: {user_name}")
        embeddings = []
        
        # Janela para preview (debug)
        cv2.namedWindow('Cadastro - Posicione seu rosto', cv2.WINDOW_AUTOSIZE)
        
        try:
            for i in range(self.embeddings_per_user):
                logger.info(f"📸 Capturando embedding {i+1}/{self.embeddings_per_user}...")
                
                # Loop até detectar rosto
                face_detected = False
                start_time = time.time()
                
                while not face_detected:
                    frame = await self.capture_frame()
                    if frame is None:
                        continue
                    
                    # Mostrar preview
                    display_frame = frame.copy()
                    cv2.putText(display_frame, f"Captura {i+1}/{self.embeddings_per_user}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(display_frame, "Posicione seu rosto na camera", 
                              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Cadastro - Posicione seu rosto', display_frame)
                    
                    # Detectar rosto
                    face = self._detect_face_in_frame(frame)
                    if face is not None:
                        # Extrair embedding
                        embedding = self._extract_embedding(face)
                        if embedding is not None:
                            embeddings.append(embedding.tolist())
                            logger.success(f"✅ Embedding {i+1} capturado com sucesso!")
                            face_detected = True
                            
                            # Mostrar confirmação
                            cv2.putText(display_frame, f"Capturado! {i+1}/{self.embeddings_per_user}", 
                                      (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            cv2.imshow('Cadastro - Posicione seu rosto', display_frame)
                            cv2.waitKey(1000)  # Mostra por 1 segundo
                    else:
                        logger.debug("Nenhum rosto detectado, aguardando...")
                    
                    # Verificar timeout
                    if time.time() - start_time > 30:  # 30 segundos timeout por embedding
                        logger.error("Timeout ao aguardar detecção de rosto")
                        cv2.destroyAllWindows()
                        return False
                    
                    # ESC para cancelar
                    if cv2.waitKey(1) & 0xFF == 27:
                        logger.info("Cadastro cancelado pelo usuário")
                        cv2.destroyAllWindows()
                        return False
                
                # Aguardar intervalo entre capturas (exceto na última)
                if i < self.embeddings_per_user - 1:
                    logger.info(f"⏱️ Aguardando {self.capture_interval}s para próxima captura...")
                    time.sleep(self.capture_interval)
            
            # Salvar usuário no banco
            if len(embeddings) == self.embeddings_per_user:
                user_data = {
                    "embeddings": embeddings,
                    "registered_at": datetime.now().isoformat(),
                    "model_name": self.model_name,
                    "threshold": self.threshold
                }
                
                self.face_encodings["users"][user_name] = user_data
                
                if self._save_faces_database():
                    logger.success(f"🎉 Usuário {user_name} cadastrado com sucesso!")
                    cv2.destroyAllWindows()
                    return True
                else:
                    logger.error("Erro ao salvar banco de dados")
                    cv2.destroyAllWindows()
                    return False
            else:
                logger.error(f"Número insuficiente de embeddings: {len(embeddings)}")
                cv2.destroyAllWindows()
                return False
                
        except Exception as e:
            logger.error(f"Erro durante cadastro: {e}")
            cv2.destroyAllWindows()
            return False
    
    def _calculate_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calcula distância cosine entre dois embeddings
        
        Args:
            embedding1: Primeiro embedding
            embedding2: Segundo embedding
            
        Returns:
            Distância cosine (0 = idêntico, 1 = completamente diferente)
        """
        try:
            # Normalizar embeddings
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Calcular similaridade cosine
            cosine_similarity = np.dot(embedding1_norm, embedding2_norm)
            
            # Converter para distância (1 - similaridade)
            cosine_distance = 1 - cosine_similarity
            
            return cosine_distance
        except Exception as e:
            logger.error(f"Erro ao calcular distância: {e}")
            return 1.0  # Máxima distância em caso de erro
    
    def _find_best_match(self, current_embedding: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Encontra o melhor match para um embedding
        
        Args:
            current_embedding: Embedding atual para comparar
            
        Returns:
            (nome_usuario, distancia) ou (None, inf) se não encontrou match
        """
        best_match = None
        best_distance = float('inf')
        
        for user_name, user_data in self.face_encodings.get("users", {}).items():
            embeddings = user_data.get("embeddings", [])
            
            # Calcular média dos embeddings do usuário
            if embeddings:
                embeddings_array = np.array(embeddings)
                mean_embedding = np.mean(embeddings_array, axis=0)
                
                # Calcular distância
                distance = self._calculate_distance(current_embedding, mean_embedding)
                
                if distance < best_distance:
                    best_distance = distance
                    best_match = user_name
        
        return best_match, best_distance
    
    async def validate_face(self) -> Tuple[bool, str]:
        """
        Validates the face of the current user
            
        Returns:
            (True, username) if face is recognized, (False, "") otherwise
        """
        if not self.camera_active:
            logger.error("Câmera não está ativa")
            return False, ""
        
        logger.info("🔍 Iniciando validação facial...")
        
        # Janela para preview (debug)
        cv2.namedWindow('Validacao - Olhe para a camera', cv2.WINDOW_AUTOSIZE)
        
        max_attempts = 3
        
        try:
            for attempt in range(max_attempts):
                logger.info(f"🎯 Tentativa {attempt + 1}/{max_attempts}")
                
                # Loop até detectar rosto
                face_detected = False
                start_time = time.time()
                
                while not face_detected:
                    frame = await self.capture_frame()
                    if frame is None:
                        continue
                    
                    # Mostrar preview
                    display_frame = frame.copy()
                    cv2.putText(display_frame, f"Validacao - Tentativa {attempt + 1}/{max_attempts}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(display_frame, "Olhe para a camera", 
                              (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('Validacao - Olhe para a camera', display_frame)
                    
                    # Detectar rosto
                    face = self._detect_face_in_frame(frame)
                    if face is not None:
                        # Extrair embedding
                        embedding = self._extract_embedding(face)
                        if embedding is not None:
                            logger.info("Comparando com usuários cadastrados...")
                            
                            # Encontrar melhor match
                            best_match, distance = self._find_best_match(embedding)
                            
                            if best_match and distance < self.threshold:
                                logger.success(f"✅ Usuário identificado: {best_match} (distância: {distance:.4f})")
                                
                                # Atualizar último acesso
                                self.face_encodings["users"][best_match]["last_validated"] = datetime.now().isoformat()
                                self._save_faces_database()
                                
                                cv2.destroyAllWindows()
                                return True, best_match
                            else:
                                logger.warning(f"❌ Rosto não reconhecido (distância: {distance:.4f}, threshold: {self.threshold})")
                                face_detected = True  # Sair do loop de detecção
                    else:
                        logger.debug("Nenhum rosto detectado, aguardando...")
                    
                    # Verificar timeout
                    if time.time() - start_time > 10:  # 10 segundos timeout por tentativa
                        logger.warning("Timeout ao aguardar detecção de rosto nesta tentativa")
                        break
                    
                    # ESC para cancelar
                    if cv2.waitKey(1) & 0xFF == 27:
                        logger.info("Validação cancelada pelo usuário")
                        cv2.destroyAllWindows()
                        return False, ""
                
                # Aguardar um pouco entre tentativas
                if attempt < max_attempts - 1:
                    logger.info("⏱️ Aguardando 1s para próxima tentativa...")
                    time.sleep(1)
            
            logger.error("❌ Falha na validação após todas as tentativas")
            cv2.destroyAllWindows()
            return False, ""
            
        except Exception as e:
            logger.error(f"Erro durante validação: {e}")
            cv2.destroyAllWindows()
            return False, ""
    
    def is_face_registered(self, user_name: str) -> bool:
        """
        Verify if a user has a registered face
        
        Args:
            user_name: Name of the user
            
        Returns:
            True if user has a registered face, False otherwise
        """
        return user_name in self.face_encodings.get("users", {})

    def get_registered_users(self) -> List[str]:
        """
        Get a list of all users with registered faces
        
        Returns:
            List of user names with registered faces
        """
        return list(self.face_encodings.get("users", {}).keys())
    
    def remove_user_face(self, user_name: str) -> bool:
        """
        Remove a user's registered face
        
        Args:
            user_name: Name of the user
            
        Returns:
            True if removal was successful, False otherwise
        """
        if user_name in self.face_encodings.get("users", {}):
            del self.face_encodings["users"][user_name]
            if self._save_faces_database():
                logger.success(f"Usuário {user_name} removido com sucesso")
                return True
            else:
                logger.error("Erro ao salvar banco após remoção")
                return False
        else:
            logger.warning(f"Usuário {user_name} não encontrado")
            return False
    
    def _load_faces_database(self) -> dict:
        """Loads the face database from file"""
        try:
            if self.faces_db_path.exists():
                with open(self.faces_db_path, 'r') as f:
                    content = f.read().strip()
                    if not content:  # Arquivo vazio
                        logger.info("Arquivo de banco vazio, criando estrutura inicial")
                        return {"users": {}, "config": {"model_name": self.model_name}}
                    
                    data = json.loads(content)
                logger.success(f"Banco de dados carregado: {len(data.get('users', {}))} usuários")
                return data
            else:
                logger.info("Banco de dados não existe, criando novo")
                return {"users": {}, "config": {"model_name": self.model_name}}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}. Criando banco novo.")
            return {"users": {}, "config": {"model_name": self.model_name}}
        except Exception as e:
            logger.error(f"Erro ao carregar banco: {e}")
            return {"users": {}, "config": {"model_name": self.model_name}}
    
    def _save_faces_database(self) -> bool:
        """Saves the face database to file"""
        try:
            # Criar diretório se não existe
            self.faces_db_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.faces_db_path, 'w') as f:
                json.dump(self.face_encodings, f, indent=2)
            logger.success("Banco de dados salvo com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar banco: {e}")
            return False
    
    def set_confidence_threshold(self, threshold: float):
        """
        Define limite de confiança para reconhecimento
        
        Args:
            threshold: Valor entre 0 e 1
        """
        self.threshold = threshold
        logger.info(f"Threshold atualizado para: {threshold}")


if __name__ == "__main__":
    # Teste das funções
    async def test_face_recognizer():
        recognizer = FaceRecognizer()
        
        # Inicializar câmera
        if not await recognizer.initialize_camera():
            print("Erro ao inicializar câmera")
            return
        
        print("Comandos disponíveis:")
        print("- register <nome>: Cadastrar usuário")
        print("- validate: Validar usuário")
        print("- list: Listar usuários")
        print("- remove <nome>: Remover usuário")
        print("- quit: Sair")
        
        while True:
            command = input("\nDigite um comando: ").strip().lower()
            
            if command.startswith("register "):
                user_name = command.split(" ", 1)[1]
                success = await recognizer.register_face(user_name)
                print(f"Cadastro {'bem-sucedido' if success else 'falhou'}")
                
            elif command == "validate":
                success, user = await recognizer.validate_face()
                if success:
                    print(f"Usuário identificado: {user}")
                else:
                    print("Usuário não reconhecido")
                    
            elif command == "list":
                users = recognizer.get_registered_users()
                print(f"Usuários cadastrados: {users}")
                
            elif command.startswith("remove "):
                user_name = command.split(" ", 1)[1]
                success = recognizer.remove_user_face(user_name)
                print(f"Remoção {'bem-sucedida' if success else 'falhou'}")
                
            elif command == "quit":
                break
                
            else:
                print("Comando não reconhecido")
        
        await recognizer.close_camera()
    
    import asyncio
    asyncio.run(test_face_recognizer())