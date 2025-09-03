import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger
import sys
import time
import threading
from typing import Dict, Optional, Any

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(dotenv_path=ENV_PATH)

def require_gemini_env() -> str:
    """Garante que a GEMINI_API_KEY exista; encerra o processo se faltar."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error(
            "GEMINI_API_KEY ausente. Defina no .env ({}) ou no ambiente e reinicie."
            .format(ENV_PATH)
        )
        sys.exit(1)
    logger.success("Variável de ambiente GEMINI_API_KEY carregada.")
    return api_key

# Fail fast e configuração do SDK
api_key = require_gemini_env()

genai.configure(api_key=api_key)

MODEL_ID = 'gemini-2.5-flash'
SYSTEM_INSTRUCTION = (
    "Você é Stella, assistente de almoxarifado hospitalar. Mantenha contexto por sessão. "
    "Seja objetiva, amigável e sempre retorne JSON válido conforme o esquema solicitado."
)
model = genai.GenerativeModel(MODEL_ID, system_instruction=SYSTEM_INSTRUCTION)

# Armazenamento simples em memória para sessões Gemini
_SESSIONS: Dict[str, Any] = {}  # Any porque ChatSession não está em genai.types
_LAST_SEEN: Dict[str, float] = {}
_SESSION_TTL_SECONDS = 3 * 60  # 3 minutos

def _gc_sessions():
    """Coleta sessões inativas (TTL)."""
    now = time.time()
    expired = [sid for sid, ts in _LAST_SEEN.items() if now - ts > _SESSION_TTL_SECONDS]
    for sid in expired:
        _SESSIONS.pop(sid, None)
        _LAST_SEEN.pop(sid, None)
        logger.info(f"Sessão expirada e removida: {sid}")

def get_or_create_session(session_id: str) -> Any:
    """Retorna ou cria uma ChatSession por session_id."""
    if not session_id:
        raise ValueError("session_id é obrigatório para manter contexto.")
    sess = _SESSIONS.get(session_id)
    if sess is None:
        sess = model.start_chat(history=[])
        _SESSIONS[session_id] = sess
        logger.info(f"Sessão criada: {session_id}")
    _LAST_SEEN[session_id] = time.time()
    _gc_sessions()
    return sess

def end_session(session_id: str):
    """Encerrar sessão explicitamente (opcional)."""
    _SESSIONS.pop(session_id, None)
    _LAST_SEEN.pop(session_id, None)
    logger.info(f"Sessão encerrada: {session_id}")

def load_estoque_data():
    try:
        # Caminho único e absoluto para o arquivo de estoque
        stock_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'data', 'stock.json')
        )

        if not os.path.exists(stock_path):
            logger.error(f"Arquivo de estoque não encontrado em: {stock_path}")
            return {"estoque": {}}

        with open(stock_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"Erro ao carregar dados do estoque: {e}")
        return {"estoque": {}}

def command_interpreter(comando: str, session_id: str):
    sess = get_or_create_session(session_id)
    estoque_data = load_estoque_data()
    model = genai.GenerativeModel('gemini-2.5-flash')
    estoque_data = load_estoque_data()
    
    estoque_completo = estoque_data.get('estoque', {})
    
    # Formatar estoque de forma legível para a IA
    estoque_formatado = ""
    for item_key, item_data in estoque_completo.items():
        nome_completo = item_data.get('nome_completo', item_key)
        quantidade_atual = item_data.get('quantidade_atual', 0)
        quantidade_minima = item_data.get('quantidade_minima', 0)
        quantidade_critica = item_data.get('quantidade_critica', 0)
        localizacao = item_data.get('localizacao', {})
        unidade = item_data.get('unidade', 'unidade')
        
        status = "🟢 NORMAL"
        if quantidade_atual <= quantidade_critica:
            status = "🔴 CRÍTICO"
        elif quantidade_atual <= quantidade_minima:
            status = "🟡 BAIXO"
        
        gaveta = localizacao.get('gaveta', 'N/A') if localizacao else 'N/A'
        
        estoque_formatado += f"""
        • {item_key}: {nome_completo}
        - Quantidade atual: {quantidade_atual} {unidade}
        - Mínimo: {quantidade_minima} | Crítico: {quantidade_critica}
        - Localização: Gaveta {gaveta}
        - Status: {status}
        """
    
    prompt = f"""
        Você é Stella, assistente de almoxarifado hospitalar. Analise este comando: "{comando}"

        ESTOQUE COMPLETO DISPONÍVEL:
        {estoque_formatado}

        CONTEXTO IMPORTANTE:
        - Última atualização: {estoque_data.get('ultima_atualizacao', 'N/A')}
        - Status 🔴 CRÍTICO = quantidade <= crítica
        - Status 🟡 BAIXO = quantidade <= mínima  
        - Status 🟢 NORMAL = quantidade > mínima

        IDENTIFIQUE A INTENÇÃO:

        1. RETIRADA DE ITEM: "preciso", "quero", "peguei", "retirar"
        Retorne: {{"intention": "registrar_retirada", "itens": [{{"item": "nome_item", "quantidade": numero}}], "response": "Texto natural com avisos se necessário"}}

        2. CONSULTA ESTOQUE: "quanto tem", "quantos", "estoque"  
        Retorne: {{"intention": "consultar_estoque", "itens": [{{"item": "nome_item", "quantidade": numero}}], "response": "Texto natural com quantidade atual e localização"}}

        3. CONSULTA LOCALIZAÇÃO: "onde está", "qual gaveta", "localização"
        Retorne: {{"intention": "consultar_localizacao", "itens": [{{"item": "nome_item"}}], "response": "Texto natural com localização"}}

        4. CANCELAR: "cancelar", "desistir"
        Retorne: {{"intention": "cancelar_retirada", "itens": [{{"item": "nome_item", "quantidade": numero}}], "response": "Texto natural"}}

        5. ALERTA ESTOQUE: quando detectar item em estado crítico/baixo
        Retorne: {{"intention": "alerta_estoque", "itens": [{{"item": "nome_item", "quantidade": numero}}], "response": "Texto natural com aviso"}}

        6. NÃO ENTENDIDO: qualquer outra coisa
        Retorne: {{"intention": "nao_entendido", "response": "Não entendi. Pode reformular?"}}

        7. CONFIRMAÇÃO: "confirmar", "sim", "claro"
        Retorne: {{"intention": "confirmar_retirada", "itens": [{{"item": "nome_item", "quantidade": numero}}], "response": "Texto natural com confirmação"}}

        REGRAS IMPORTANTES:
        - Normalize nomes (ex: "seringa 10ml" → "seringa_10ml")
        - Retorne APENAS JSON válido
        - Seja natural e amigável
        - Em caso de ambiguidade, pergunte especificações (ex: qual tipo de seringa?)
        - Se o item não existir no estoque, avise o usuário
        - SEMPRE verifique se retirada deixará estoque em estado crítico/baixo
        - Inclua avisos sobre localização se existir e for relevante
        - Para consultas, inclua quantidade atual e localização
        - Detecte outliers (quantidades muito altas/baixas solicitadas)
        - Confirmar retirada deve ser feita apenas quando você tiver certeza da quantidade e do item, e o usuário tiver confirmado a retirada. Depois disso, encerraremos a sessão e enviaremos a retirada.

        EXEMPLOS DE RESPOSTAS COM CONTEXTO:
        - Retirada normal: "Registrei 5 seringas de 10ml. Restam 45 unidades na gaveta B."
        - Retirada com aviso: "⚠️ ATENÇÃO: Retirar 20 máscaras N95 deixará apenas 15 unidades (abaixo do mínimo de 30). Confirma?"
        - Consulta: "Temos 150 seringas de 5ml disponíveis na gaveta B (estoque normal)."
        - Crítico: "🔴 ALERTA: Agulhas 21G estão em estado CRÍTICO - apenas 5 unidades restantes!"

        RESPONDA APENAS COM JSON:

        Contexto da conversa:
        {sess.history}
        """
    
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        
        # Limpa a resposta
        clean_text = response.text.strip()
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:-3]
        elif clean_text.startswith('```'):
            clean_text = clean_text[3:-3]

        logger.debug(f"Resposta limpa do Gemini: {clean_text}")

        resultado = json.loads(clean_text)
        logger.success(f"SessionID: {session_id} - Comando interpretado com sucesso: {resultado.get('intention', 'N/A')}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao interpretar (sessão {session_id}): {e}")
        return {
            "intention": "erro",
            "response": "Houve um erro no processamento. Pode repetir sua solicitação?"
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

if __name__ == "__main__":
    # Fallback: inicia chat interativo integrado
    pass
