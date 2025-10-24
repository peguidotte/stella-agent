# 🛠️ Guia de Desenvolvimento - Stella Agent

Este guia contém informações para desenvolvedores que desejam contribuir ou trabalhar no Stella Agent.

## 📋 Índice

- [Pré-requisitos](#-pré-requisitos)
- [Setup do Ambiente](#-setup-do-ambiente)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Padrões de Código](#-padrões-de-código)
- [Testes](#-testes)
- [Docker](#-docker)
- [Debugging](#-debugging)
- [CI/CD](#-cicd)

## 🔧 Pré-requisitos

- Python 3.11 ou superior
- Git
- Docker (opcional, para containerização)
- VS Code ou PyCharm (recomendado)

## 🚀 Setup do Ambiente

### Opção 1: Script Automático (Recomendado)

```bash
chmod +x setup.sh
./setup.sh
```

### Opção 2: Setup Manual

1. **Clone o repositório**
```bash
git clone https://github.com/peguidotte/stella-agent.git
cd stella-agent
```

2. **Crie ambiente virtual**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. **Instale dependências**
```bash
# Produção
pip install -r requirements.txt

# Desenvolvimento
pip install -r requirements-dev.txt
```

4. **Configure variáveis de ambiente**
```bash
cp .env.example .env
# Edite .env com suas credenciais
```

5. **Configure pre-commit hooks**
```bash
pre-commit install
```

## 📁 Estrutura do Projeto

```
stella-agent/
├── stella/                     # Código principal
│   ├── api/                    # API REST (FastAPI)
│   │   ├── models/            # Modelos Pydantic
│   │   ├── routes/            # Endpoints da API
│   │   └── services/          # Lógica de negócio
│   ├── agent/                 # Processamento de voz
│   ├── face_id/               # Reconhecimento facial
│   ├── messaging/             # RabbitMQ/AMQP
│   ├── websocket/             # WebSocket (Pusher)
│   ├── config/                # Configurações
│   └── data/                  # Dados (JSON)
├── tests/                     # Testes
│   ├── test_settings.py       # Testes unitários
│   └── test_api_integration.py # Testes de integração
├── docs/                      # Documentação adicional
├── main.py                    # Entry point
├── demo.py                    # Script de demonstração
└── requirements.txt           # Dependências
```

## 📝 Padrões de Código

### Python Style Guide

- **PEP 8**: Siga o guia de estilo do Python
- **Black**: Formatador automático (linha: 100 chars)
- **Type Hints**: Use sempre que possível
- **Docstrings**: Estilo Google para funções públicas

### Exemplo de Código

```python
from typing import Optional

def process_speech(text: str, session_id: str) -> dict:
    """
    Processa entrada de voz usando IA.
    
    Args:
        text: Texto transcrito da fala do usuário
        session_id: Identificador único da sessão
        
    Returns:
        Dicionário com a resposta processada
        
    Raises:
        ValueError: Se o texto estiver vazio
    """
    if not text:
        raise ValueError("Texto não pode estar vazio")
    
    # Processamento
    result = {"status": "success", "data": text}
    return result
```

### Commits Convencionais

Use o formato Conventional Commits:

```bash
feat: adiciona validação de PIN
fix: corrige bug no reconhecimento facial
docs: atualiza README com instruções de Docker
style: formata código com black
refactor: refatora serviço de speech
test: adiciona testes para settings
chore: atualiza dependências
```

## 🧪 Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=stella --cov-report=html

# Teste específico
pytest tests/test_settings.py

# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Excluir testes lentos
pytest -m "not slow"
```

### Escrever Testes

```python
import pytest
from stella.config.settings import Settings

@pytest.mark.unit
def test_settings_initialization():
    """Test that settings initialize correctly."""
    settings = Settings()
    assert settings.get('system.unit_id') == 'UNIT_001'
```

### Cobertura de Código

Mantenha cobertura > 80%. Visualize o relatório:

```bash
pytest --cov=stella --cov-report=html
open htmlcov/index.html
```

## 🐳 Docker

### Build e Run

```bash
# Build da imagem
docker build -t stella-agent:latest .

# Run container
docker run -p 8000:8000 --env-file .env stella-agent:latest

# Usando docker-compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

### Debug no Container

```bash
# Entrar no container
docker exec -it stella-agent bash

# Ver logs
docker logs stella-agent

# Reiniciar serviço
docker-compose restart stella-agent
```

## 🐛 Debugging

### VS Code

Configure `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### Logging

Configure níveis de log no `.env`:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Uso no código:

```python
from loguru import logger

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

## 🔄 CI/CD

### GitHub Actions

Workflows configurados:

1. **CI** (`.github/workflows/ci.yml`)
   - Linting (flake8)
   - Type checking (mypy)
   - Testes (pytest)
   - Cobertura de código

2. **Dependency Review** (`.github/workflows/dependency-review.yml`)
   - Scan de vulnerabilidades em PRs

### Pre-commit Hooks

Executados automaticamente antes do commit:

```bash
# Executar manualmente
pre-commit run --all-files

# Pular hooks (não recomendado)
git commit --no-verify
```

## 🔧 Comandos Úteis (Makefile)

```bash
make help           # Lista todos os comandos
make install        # Instala dependências
make install-dev    # Instala tudo (prod + dev)
make run            # Inicia servidor
make test           # Executa testes
make test-cov       # Testes com cobertura
make lint           # Linting (flake8)
make format         # Formata código (black)
make type-check     # Type checking (mypy)
make check          # Todos os checks
make clean          # Limpa arquivos temporários
make docker-build   # Build Docker image
make docker-up      # Inicia containers
make docker-down    # Para containers
```

## 📚 Recursos Adicionais

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pytest Docs](https://docs.pytest.org/)
- [Black Formatter](https://black.readthedocs.io/)
- [Pre-commit](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 💬 Suporte

- **Issues**: [GitHub Issues](https://github.com/peguidotte/stella-agent/issues)
- **Discussions**: Abra uma issue com tag `question`
- **Email**: Entre em contato com a equipe Stellar

---

**Happy Coding! 🚀**
