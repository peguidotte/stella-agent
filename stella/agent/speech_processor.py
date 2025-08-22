import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

logger.info("Iniciando o carregamento da chave API do Gemini...")
load_dotenv("GEMINI_API_KEY.env")
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    logger.error("GEMINI_API_KEY não encontrada.")
    logger.warning("Verifique se existe o arquivo 'GEMINI_API_KEY.env' no raiz do projeto.")
    logger.warning("Certifique-se de que a variável 'GEMINI_API_KEY' está definida no arquivo")
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check that 'GEMINI_API_KEY.env' exists in the project root and contains the 'GEMINI_API_KEY' variable.")
logger.success("GEMINI_API_KEY carregada com sucesso.")
genai.configure(api_key=api_key)

def read_json(arquivo):
    try:
        with open(arquivo, 'r') as f:
            data = json.load(f)
        if 'comando' not in data:
            logger.error(f"Arquivo {arquivo} não contém a chave 'comando'.")
            return None
        return data['comando'].lower()
    except FileNotFoundError:
        logger.error(f"Arquivo {arquivo} não encontrado.")
        return None
    except KeyError:
        logger.error("Formato de JSON inválido.")
        return None

def load_estoque_data():
    try:
        with open('data/estoque_almoxarifado.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Arquivo de estoque não encontrado")
        return {"estoque": {}}

def command_interpreter(comando):
    model = genai.GenerativeModel('gemini-1.5-flash')
    estoque_data = load_estoque_data()
    
    # Cria contexto de estoque para a IA
    contexto_estoque = ""
    for item_key, item_info in estoque_data.get('estoque', {}).items():
        contexto_estoque += f"""
{item_key}: 
- Disponível: {item_info['quantidade_atual']} {item_info['unidade']}
- Mínimo: {item_info['quantidade_minima']}
- Crítico: {item_info['quantidade_critica']}
- Outlier máx: {item_info['outlier_maximo']}
- Localização: Setor {item_info['localizacao']['setor']}, Prateleira {item_info['localizacao']['prateleira']}
"""
    
    prompt = f"""
    Você é a Stella, uma assistente de registro de almoxarifado hospitalar. Analise o comando: '{comando}'

    ESTOQUE ATUAL:
    {contexto_estoque}

    CONTEXTO: Estoquistas vêm ao almoxarifado, pegam itens e informam você sobre a retirada. Seu papel é registrar essas movimentações no sistema.

    IDENTIFIQUE A INTENÇÃO e extraia informações estruturadas:

    ## 1. REGISTRO DE RETIRADA DE ITEM(S)
    Palavras-chave: "preciso", "quero", "retirar", "pegar", "buscar", "tirei", "peguei"
    - Verifique se há estoque suficiente
    - Se quantidade solicitada > outlier_maximo, marque como "outlier": true
    - Se estoque < quantidade_critica após retirada, marque como "alerta_critico": true
    - Se múltiplos itens, liste todos
    - Normalize nomes (ex: "seringa 5ml" → "seringa_5ml")

    Retorne APENAS:
    ```json
    {{
    "intencao": "registrar_retirada",
    "itens": [
        {{
            "item": "nome_normalizado", 
            "quantidade": numero, 
            "especificacao": "detalhes_opcionais",
            "estoque_atual": numero,
            "estoque_apos_retirada": numero,
            "outlier": boolean,
            "nivel_alerta": enum(0, 1, 2)  # 0: Normal, 1: Atenção, 2: Crítico,
            "localizacao": "Setor X, Prateleira Y" #OPCIONAL, APENAS SE HOUVER A INFORMAÇÃO
        }}
    ],
    "confirmacao": "Sua frase natural de confirmação"
    }}
    ```

    ## 2. CANCELAR REGISTRO
    Palavras-chave: "cancelar", "desistir", "não quero mais", "errei"
    ```json
    {{
    "intencao": "cancelar_registro",
    "itens": [
        {{"item": "nome_normalizado", "quantidade": numero}}
    ],
    "confirmacao": "Entendi, vou cancelar o registro da retirada. Confirma?"
    }}
    ```

    ## 3. CONSULTAR ESTOQUE
    Palavras-chave: "quanto tem", "quantos", "estoque", "disponível", "sobrou"
    ```json
    {{
    "intencao": "consultar_estoque",
    "itens": [
        {{
            "item": "nome_normalizado",
            "quantidade_atual": numero,
            "quantidade_minima": numero,
            "nivel_alerta": enum(0, 1, 2),  # 0: Normal, 1: Atenção, 2: Crítico
            "localizacao": "Setor X, Prateleira Y" #OPCIONAL, APENAS SE HOUVER A INFORMAÇÃO
        }}
    ],
    "confirmacao": "Temos [quantidade] [item] disponíveis. Localização: [setor/prateleira]"
    }}
    ```

    ## 4. DÚVIDAS SOBRE ALMOXARIFADO
    Responda apenas sobre: localização de itens, procedimentos, equipamentos médicos
    ```json
    {{
    "intencao": "responder_duvida",
    "duvida": "pergunta_original",
    "resposta": "sua_resposta_breve",
    "confirmacao": "Consegui esclarecer? Precisa de mais alguma informação?"
    }}
    ```

    ## 5. COMANDO UNCLEAR OU FORA DO ESCOPO
    ```json
    {{
    "intencao": "nao_entendido",
    "confirmacao": "Não consegui entender. Você está informando uma retirada? Ex: 'Peguei 5 seringas de 10ml'"
    }}
    ```

    REGRAS:
    - SEMPRE retorne JSON válido
    - Normalize itens médicos para padrão consistente
    - Se comando ambíguo, peça esclarecimento
    - Ignore conversas não relacionadas ao almoxarifado
    - Para múltiplos itens, processe cada um separadamente no array
    - As frases de confirmação são APENAS EXEMPLOS - crie frases naturais e conversacionais
    - Use tom profissional mas amigável, como uma assistente de registro eficiente
    - Foque em CONFIRMAR a retirada para depois registrar no sistema
    - Varie as confirmações para soar natural

    FORMATO DE SAÍDA: Apenas o JSON, sem markdown ou explicações adicionais.
    """
    response = model.generate_content(prompt)
    logger.debug(f"Resposta bruta do Gemini: {response.text}")  # Depuração
    try:
        # Extrai o conteúdo entre ```json
        import re
        json_str = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
        if json_str:
            resultado = json.loads(json_str.group(1).strip())
        else:
            # Remove markdown se existir
            clean_text = response.text.strip()
            if clean_text.startswith('```json'):
                clean_text = clean_text[7:-3]
            elif clean_text.startswith('```'):
                clean_text = clean_text[3:-3]
            resultado = json.loads(clean_text)
        
        # Retorna o resultado completo ao invés de campos específicos
        return resultado
        
    except Exception as e:
        print(f"Erro ao parsear JSON: {e}")
        return {
            "intencao": "nao_entendido",
            "confirmacao": "Houve um erro no processamento. Pode repetir sua solicitação?"
        }

def process_action(resultado):
    if not resultado:
        return "Comando não reconhecido."
    
    intencao = resultado.get('intencao')
    itens = resultado.get('itens', [])
    confirmacao = resultado.get('confirmacao', '')
    
    print(f"Intenção identificada: {intencao}")
    if itens:
        print(f"Itens processados: {itens}")
    
    # Aqui você implementará a lógica específica:
    if intencao == 'registrar_retirada':
        # TODO: Validar estoque, verificar outliers, preparar log para o sistema
        pass
    elif intencao == 'consultar_estoque':
        # TODO: Consultar banco de dados de estoque
        pass
    elif intencao == 'cancelar_registro':
        # TODO: Cancelar registro pendente
        pass
    
    return confirmacao

comando = read_json('stella/agent/falas.json')
if comando:
    print(f"Comando: {comando}\n")
    resultado = command_interpreter(comando)
    if resultado:
        resposta = process_action(resultado)
    else:
        print("Comando não entendido. Tente reformular.")
else:
    print("Nenhum comando válido para processar.")
