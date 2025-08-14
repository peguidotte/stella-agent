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