# Guia de instalação de dependências do projeto

## Python e venv

1. **Baixe Python 3.11.9:** [Download Python 3.11.9](https://www.python.org/downloads/release/python-3119/)
   - No Windows: baixe `python-3.11.9-amd64.exe`
   - ✅ Marque **"Add Python to PATH"** durante a instalação

2. **Verifique a instalação:**
```bash
py -3.11 --version
```
Deve mostrar `Python 3.11.9`

3. **Crie ambiente virtual:**
```bash
py -3.11 -m venv venv
```

4. **Ative o ambiente virtual:**
```bash
.\venv\Scripts\activate
```

Deve aparecer `(venv)` no prompt.

5. **Verifique a versão no ambiente:**
```bash
python --version
```
Deve mostrar `Python 3.11.9`

6. **Atualize o pip para garantir:**
```bash
python -m pip install --upgrade pip
```

## Instalação das Dependências

1. **GARANTA** que você está no ambiente virtual (venv) antes de instalar as dependências.

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Verificação final**

```bash
pip list
```

Deve mostrar algo assim:
- ✅ `mediapipe` (0.10.21)
- ✅ `opencv-contrib-python` (4.11.0.86)
- ✅ `numpy` (1.26.4)
- ✅ `python-dotenv` - Variáveis de ambiente
- ✅ `pyyaml` - Configuração YAML
- ✅ `loguru` - Sistema de logging
- ✅ `matplotlib` (3.10.5) - Gráficos
- ✅ `pillow` (11.3.0) - Imagens
- ✅ `protobuf` (4.25.8) - Modelos ML

## Adicionar novas dependências

1. Garante que sua dependência adicionada não quebrou nenhuma funcionalidade existente.
2. Adicione a nova dependência no arquivo `requirements.txt`.
3. Execute testes para verificar se tudo está funcionando corretamente.

Caso sua nova dependência não seja compatível com as versões existentes, você pode precisar ajustar as versões no `requirements.txt` ou resolver conflitos de dependência, dê preferência a não alterar versões de pacotes já instalados, tente resolver conflitos alterando a sua própria dependência.

## Configuração da Chave API do Gemini

O agente Stella utiliza a API do Google Gemini para processamento de linguagem natural. Para obter sua chave gratuita, siga os passos abaixo:

### 1. Obter a Chave API do Gemini

1. **Acesse o Google AI Studio:**
   - Vá para: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

2. **Faça login com sua Conta Google**
   - Use qualquer conta Google (Gmail, workspace, etc.)

3. **Crie uma nova API Key:**
   - Clique em **"Create API Key"** (Criar chave de API)
   - Selecione **"Create API key in new project"** se for sua primeira vez
   - Ou escolha um projeto existente se já tiver um

4. **Copie a chave gerada:**
   - A chave aparecerá no formato: `AIzaSyC...` (cerca de 39 caracteres)
   - ⚠️ **IMPORTANTE:** Copie imediatamente e guarde em local seguro
   - Por segurança, a chave completa só é mostrada uma vez

### 2. Configurar a Chave no Projeto

1. **Crie o arquivo de ambiente:**
   - Na **raiz do projeto** `stella-agent/`, crie um arquivo chamado `GEMINI_API_KEY.env`

2. **Adicione sua chave no arquivo:**
   ```env
   GEMINI_API_KEY=AIzaSyC...SuaChaveAqui
   ```
   - Substitua `AIzaSyC...SuaChaveAqui` pela sua chave real
   - **Não** coloque aspas ou espaços extras

3. **Estrutura final do projeto:**
   ```
   stella-agent/
   ├── GEMINI_API_KEY.env  ← Arquivo criado
   ├── requirements.txt
   ├── README.md
   ├── stella/
   └── ...
   ```

### 3. Verificar a Configuração

1. **Execute o agente para testar:**
   ```bash
   python stella/agent/speech_processor.py
   ```

2. **Mensagens esperadas:**
   - ✅ `GEMINI_API_KEY carregada com sucesso.`
   - Se der erro, verifique se:
     - O arquivo está na raiz do projeto
     - A chave está correta (sem espaços/aspas extras)
     - Você tem internet ativa

### 4. Limites do Plano Gratuito

- **15 requisições por minuto**
- **1.500 requisições por dia**
- **1 milhão de tokens por dia**

Para uso normal do agente Stella, esses limites são mais que suficientes.

### 5. Troubleshooting

**Erro: "GEMINI_API_KEY não encontrada"**
- Verifique se o arquivo `GEMINI_API_KEY.env` está na raiz do projeto
- Confirme se o nome da variável está exatamente como: `GEMINI_API_KEY=`

**Erro: "API Key inválida"**
- Verifique se copiou a chave completa
- Teste criando uma nova chave no Google AI Studio

**Erro: "Quota exceeded"**
- Você excedeu o limite gratuito
- Aguarde o reset (24h) ou considere upgrade para plano pago
