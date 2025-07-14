# 🧠 Projeto Stella – Assistente de Estoque com IA Local

## 📌 Visão Geral

A **Stella** é uma assistente de voz com IA, desenvolvida em **Python**, que será instalada localmente em almoxarifados físicos. Ela ajuda **estoquistas** a registrar retiradas de materiais, validar essas retiradas com **reconhecimento facial**, conferir estoque e enviar notificações.

> A Stella é **vinculada a uma unidade** via ID único, e se comunica com o sistema da unidade (web) por filas ou mensagens.

---

## 🎯 Objetivos principais da Stella:

1. Ser ativada por comando de voz: **“Stella”**
2. Escutar comandos simples de retirada: _"Preciso de 5 seringas de 10ml"_
3. Validar retirada com **Face ID**
4. Conferir o estoque atual (recebido por mensagens)
5. Verificar inconsistências (outliers, falta de estoque, etc)
6. Notificar o **Sistema da Unidade** via mensageria (RabbitMQ, Kafka, ou similar)

---

## 💡 Tecnologias sugeridas:

- **Python 3.10+**
- Reconhecimento de voz: `speech_recognition` + `pyaudio` ou `vosk`
- Face ID (local): `opencv` + `face_recognition`
- Mensageria: `pika` (RabbitMQ) ou `kafka-python` (Kafka)
- Armazenamento local leve: `TinyDB`, `sqlite3` ou arquivos JSON
- Assistente inicial via API (ex: OpenAI, Gemini) – apenas para testes

---

## 🧪 Setup inicial (para Copilot ajudar)

1. Criar estrutura de pasta padrão:
   - `/core` – lógica principal
   - `/voice` – ativação e escuta
   - `/face_id` – validação facial
   - `/messaging` – integração com sistema de unidade
   - `/config` – arquivos de configuração locais

2. Configurar ativação por palavra-chave **“Stella”** (via microfone)
3. Esperar comando de retirada e estruturar como JSON
4. Validar via Face ID
5. Enviar confirmação ou erro via fila (ex: para tópico `stella.retiradas`)

---

## 🔒 Observação

- O ideal é que **a Stella funcione offline**, mas neste início aceitaremos testes com dependência de APIs (OpenAI, Gemini, etc).
- Caso não haja conexão, a Stella deve continuar operando com fallback local.

---

## 🚀 Missão do Copilot

- Criar a estrutura base do projeto em Python
- Criar um listener de voz por comando "Stella"
- Criar um protótipo simples de reconhecimento facial
- Simular envio de mensagem JSON para outro sistema via fila

---

Com isso o Copilot já entende o projeto e começa a sugerir código em cima da estrutura certa. Se quiser depois, posso montar o `README.md` todo já formatado ou até gerar os arquivos base. Só pedir.
