# 📡 Guia de Respostas Assíncronas via WebSocket - Stella Agent

Este documento descreve todas as respostas assíncronas enviadas via WebSocket pela Stella Agent API. Endpoints que processam dados via IA (speech) ou reconhecimento facial retornam confirmação HTTP imediata e resultado final via WebSocket.

## 🔄 Fluxo de Comunicação

```
1. Frontend → POST /endpoint → Backend
2. Backend → HTTP Response (50ms) → Frontend  
3. Backend → Processamento assíncrono (1-3s)
4. Backend → WebSocket Event → Frontend
```

## 📋 Índice

- [🗣️ Speech Processing](#-speech-processing)
- [📸 Face Recognition](#-face-recognition)
- [🔧 Configuração WebSocket](#-configuração-websocket)
- [📝 Exemplos de Implementação](#-exemplos-de-implementação)

---

## 🗣️ Speech Processing

### Endpoint: `POST /speech/process`

#### HTTP Response Imediata
```json
{
  "status": "accepted",
  "correlation_id": "uuid-correlation-id",
  "message": "Speech sendo processado pela Stella"
}
```

### WebSocket Events

#### ✅ Sucesso: `server-speech-output`

```json
{
    "session_id": "abc-123-session",
    "correlation_id": "xyz-789-correlation",
    "timestamp": "2025-09-07T10:30:45.123Z",
    "data": {
      "intention": "withdraw_request",
      "items": [
        {
          "item": "seringa_10ml",
          "quantidade": 5
        }
      ],
      "response": "Registrei a retirada de 5 seringas de 10ml. Restam 45 unidades na gaveta B.",
      "stella_analysis": "normal",
      "reason": null
    }
}
```

### Valores dos Enums

#### UserIntentions
| Valor | Descrição | Exemplo |
|-------|-----------|---------|
| `withdraw_request` | Solicitação de retirada | "Preciso de 5 seringas" |
| `withdraw_confirm` | Confirmação de retirada | "Confirmo a retirada" |
| `doubt` | Dúvida ou pergunta | "Como funciona o estoque?" |
| `stock_query` | Consulta de estoque | "Quantas máscaras temos?" |
| `not_understood` | Comando não compreendido | "blablabla" |

#### StellaAnalysis
| Valor | Descrição | UI Sugerida |
|-------|-----------|-------------|
| `normal` | Operação normal | Verde, ícone ✅ |
| `low_stock_alert` | Estoque baixo | Amarelo, ícone ⚠️ |
| `critical_stock_alert` | Estoque crítico | Vermelho, ícone 🔴 |
| `outlier_withdraw_request` | Quantidade muito alta/baixa | Laranja, ícone ⚡ |
| `ambiguous` | Comando ambíguo | Azul, ícone ❓ |
| `not_understood` | Não compreendido | Cinza, ícone ❌ |
| `safety_check` | Verificação de segurança | Roxo, ícone 🛡️ |
| `greeting` | Saudação | Verde claro, ícone 👋 |
| `farewell` | Despedida | Verde claro, ícone 👋 |

---

## 📸 Face Recognition

### Endpoint: `POST /face/recognize`

#### HTTP Response Imediata
```json
{
  "status": "accepted",
  "correlation_id": "uuid-correlation-id",
  "message": "Reconhecimento facial em processamento"
}
```

### WebSocket Events

#### ✅ Sucesso: `server-face-recognition-output`

```json
{
    "session_id": "abc-123-session",
    "correlation_id": "xyz-789-correlation",
    "timestamp": "2025-09-07T10:30:45.123Z",
    "user_exists": true,
    "user_id": "1"
}
```

---

### Endpoint: `POST /face/register`

#### HTTP Response Imediata
```json
{
  "status": "accepted",
  "correlation_id": "uuid-correlation-id",
  "message": "Cadastro de João Silva em processamento"
}
```

### WebSocket Events

#### ✅ Sucesso: `server-face-registration-output`

```json
{
    "session_id": "abc-123-session",
    "correlation_id": "xyz-789-correlation",
    "timestamp": "2025-09-07T10:30:45.123Z",
    "success": true,
    "message": "Usuário João Silva cadastrado com sucesso!"
}
```

---

## 🔧 Configuração WebSocket

### Conexão Pusher

```javascript
// Configuração do cliente Pusher
const pusher = new Pusher('pusher-key', {
  cluster: 'us2',
  encrypted: true,
  auth: {
    headers: {
      'Authorization': 'Bearer your-token'
    }
  }
});

// Subscrever canal
const channel = pusher.subscribe('private-agent-123');
```

### Eventos a Escutar

```javascript
// Speech Events
channel.bind('server-speech-output', handleSpeechSuccess);
channel.bind('server-speech-error', handleSpeechError);

// Face Recognition Events
channel.bind('server-face-recognition-success', handleFaceSuccess);
channel.bind('server-face-recognition-failure', handleFaceFailure);
channel.bind('server-face-recognition-error', handleFaceError);

// Face Registration Events
channel.bind('server-face-registration-success', handleRegisterSuccess);
channel.bind('server-face-registration-error', handleRegisterError);
```