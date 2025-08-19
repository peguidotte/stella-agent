import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from difflib import get_close_matches  # Para fuzzy matching de itens

# Especifique o caminho absoluto para o .env (teste)
load_dotenv("stella/voice/GEMINI_API_KEY.env")
api_key = os.getenv("GEMINI_API_KEY")
print(f"Chave lida do .env: {api_key}")  # Depuração
if not api_key:
    raise ValueError("Chave GEMINI_API_KEY não encontrada no .env")
genai.configure(api_key=api_key)

# Etapa 1: Ler o JSON (mesmo que antes)
def ler_json(arquivo):
    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
            return data['comando'].lower()
    except FileNotFoundError:
        print(f"Arquivo {arquivo} não encontrado.")  # Mais detalhe
        return None  # Retorna None em vez de string para evitar processamento
    except KeyError:
        print("Formato de JSON inválido.")
        return None

# Etapa 2: Interpretar com Gemini API (gratuita com limites)
def interpretar_comando(comando):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Analise o comando de um sistema de almoxarifado: '{comando}'
    Identifique a intenção principal (ex.: retirar_item, cadastrar_item, cancelar_retirada, consultar_estoque, responder_duvida) e extraia:
    - quantidade (número, default 1 se não especificado),
    - item (nome do produto, corrigindo erros de transcrição se possível).
    Retorne em JSON: {{"intencao": "valor", "quantidade": numero, "item": "valor"}}.
    Se não entender, retorne {{"intencao": null, "quantidade": null, "item": null}}.
    """
    response = model.generate_content(prompt)
    print(f"Resposta bruta do Gemini: {response.text}")  # Depuração
    try:
        # Extrai o conteúdo entre ```json
        import re
        json_str = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
        if json_str:
            resultado = json.loads(json_str.group(1).strip())
        else:
            resultado = json.loads(response.text.strip('```json').strip('```'))
        return resultado['intencao'], resultado['quantidade'], resultado['item']
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        return None, None, None

# Etapa 3: Processar ação (mesmo que antes, com fuzzy para itens)
def processar_acao(intent, quantidade, item):
    # Aqui, carregue itens do DB para fuzzy
    itens_conhecidos = ["siringa", "agulha", "luva"]  # Exemplo; substitua por query ao DB
    if item:
        correcao = get_close_matches(item, itens_conhecidos, n=1, cutoff=0.7)
        if correcao:
            item = correcao[0]
    
    print(f"Ação: {intent}, Quantidade: {quantidade}, Item: {item}")
    return "Ação simulada (integre com DB aqui)."

# Fluxo principal
comando = ler_json('stella/voice/falas.json')
if comando:
    print(f"Comando simulado: {comando}")
    intent, quantidade, item = interpretar_comando(comando)
    if intent:
        resultado = processar_acao(intent, quantidade, item)
        print(resultado)
    else:
        print("Comando não entendido. Tente reformular.")
else:
    print("Nenhum comando válido para processar.")
