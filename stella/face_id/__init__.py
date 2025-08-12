"""
Face ID Module - Reconhecimento Facial

Este módulo gerencia:
- Captura de imagens da câmera
- Processamento e reconhecimento facial
- Cadastro de novos rostos (durante autenticação inicial)
- Validação de identidade para retiradas
"""

from .face_recognizer import FaceRecognizer

__all__ = ['FaceRecognizer']