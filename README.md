# 🤖 Stella Agent - DASA Challenge

Assistente Inteligente para Gerenciamento de Almoxarifado com reconhecimento facial, comandos de voz e integração com sistemas de unidade.

## 📋 Visão Geral

O Stella Agent implementa três histórias de usuário principais:

- **HU-01**: Autenticação de usuário com Face ID e PIN
- **HU-02**: Solicitação de retirada de produtos por comando de voz  
- **HU-03**: Validação de retirada com confirmação de identidade

## 🏗️ Estrutura do Projeto

```
stella/
├── core/              # Lógica de fluxo principal
│   ├── __init__.py
│   └── session_manager.py
├── voice/             # Processamento de voz e comandos
│   ├── __init__.py
│   └── speech_processor.py
├── face_id/           # Reconhecimento facial
│   ├── __init__.py
│   └── face_recognizer.py
├── messaging/         # Comunicação com Sistema da Unidade
│   ├── __init__.py
│   └── unit_system_client.py
├── config/            # Configurações e armazenamento
│   ├── __init__.py
│   ├── settings.py
│   └── stella_config.yaml
└── main.py           # Ponto de entrada principal
```

## 🚀 Setup e Instalação

### Pré-requisitos

- Python 3.8+
- Câmera (para Face ID)
- Microfone (para comandos de voz)

### Instalação das Dependências (Implementar on demand)

```bash
pip install -r requirements.txt
```

### Configuração

1. Edite o arquivo `stella/config/stella_config.yaml` conforme necessário
2. Configure o PIN da unidade (padrão: 123456)
3. Ajuste configurações de hardware se necessário

## 🎮 Executando o Sistema

### Modo Produção
```bash
python stella/main.py
```

### Modo Demonstração (Recomendado para Teste)
```bash
python demo.py
```

## 🧪 Demonstração Interativa

O arquivo `demo.py` oferece uma demonstração completa dos fluxos:

1. **Demo HU-01**: Processo completo de autenticação
2. **Demo HU-02**: Solicitação de retirada de produtos
3. **Demo HU-03**: Validação de retirada com Face ID/PIN
4. **Fluxo Completo**: Sequência das 3 HUs
5. **Status do Sistema**: Informações do estado atual

### Exemplo de Uso da Demo

```bash
python demo.py
```

Siga o menu interativo:
- Digite comandos de voz simulados
- Teste diferentes cenários (PIN correto/incorreto, Face ID)
- Observe as notificações enviadas ao Sistema da Unidade

## 🔧 Configurações Principais

### Autenticação (HU-01)
- `authentication.pin_length`: Tamanho do PIN (padrão: 6)
- `authentication.max_pin_attempts`: Máximo de tentativas (padrão: 3)
- `authentication.lockout_duration_minutes`: Tempo de bloqueio (padrão: 30)

### Solicitação (HU-02)
- `request.wake_word`: Palavra de ativação (padrão: "Stella")
- `request.confirmation_timeout_minutes`: Timeout para confirmação (padrão: 10)

### Validação (HU-03)
- `validation.max_face_id_attempts`: Tentativas de Face ID (padrão: 3)
- `validation.face_id_confidence_threshold`: Limite de confiança (padrão: 0.8)

## 📡 Integração com Sistema da Unidade

O sistema envia notificações via fila (Redis) para o Sistema da Unidade:

### Tipos de Notificação
- `auth_success`: Autenticação bem-sucedida
- `auth_failure`: Falha na autenticação
- `auth_lockout`: Sistema bloqueado
- `withdrawal_request`: Solicitação de retirada
- `withdrawal_completed`: Retirada completada
- `validation_failure`: Falha na validação

### Exemplo de Payload
```json
{
  "event_type": "withdrawal_completed",
  "timestamp": "2025-07-14T10:30:00",
  "unit_id": "UNIT_001",
  "message_id": "uuid-here",
  "data": {
    "user_name": "João Silva",
    "withdrawn_items": {
      "Seringa 5ml": 10,
      "Luva M": 2
    },
    "validation_method": "face_id",
    "status": "completed"
  }
}
```

## 🤝 Contribuição

Este projeto faz parte do DASA Challenge. Para contribuir:

1. Mantenha a estrutura modular existente
2. Siga as especificações das HUs
3. Adicione testes quando implementar funcionalidades reais (não precisamos disso agora)
4. Documente mudanças significativas

## 📄 Licença

Este projeto é parte do DASA Challenge - FIAP 2025.