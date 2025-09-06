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
ACTIVE_SESSION_ID: Optional[str] = None  # sessão ativa exclusiva

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

def end_session(session_id: str) -> bool:
    """
    Encerra uma sessão específica do Gemini
    
    Args:
        session_id: ID da sessão para encerrar
        
    Returns:
        True se sessão foi encontrada e removida
    """
    global _SESSIONS, _LAST_SEEN
    
    if session_id in _SESSIONS:
        del _SESSIONS[session_id]
        if session_id in _LAST_SEEN:
            del _LAST_SEEN[session_id]
        logger.info(f"🗑️ Sessão Gemini encerrada: {session_id}")
        return True
    
    logger.warning(f"⚠️ Sessão não encontrada para encerrar: {session_id}")
    return False

def switch_active_session(session_id: str):
    """Garante sessão exclusiva: ao trocar de session_id, apaga histórico anterior."""
    global ACTIVE_SESSION_ID
    if ACTIVE_SESSION_ID and ACTIVE_SESSION_ID != session_id:
        for sid in list(_SESSIONS.keys()):
            if sid != session_id:
                end_session(sid)
        logger.info(f"Alternando sessão ativa de {ACTIVE_SESSION_ID} para {session_id}")
    ACTIVE_SESSION_ID = session_id

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
    switch_active_session(session_id)
    sess = get_or_create_session(session_id)
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

        RESPONDA EXATAMENTE COM ESTE FORMATO JSON:
        {{
            "intention": "ESCOLHA_UM_VALOR_VÁLIDO",
            "items": [{{"item": "nome_item", "quantidade": numero}}],
            "response": "resposta natural e amigável da Stella",
            "stella_analysis": "ESCOLHA_UM_VALOR_VÁLIDO",
            "reason": "justificativa opcional"
        }}

        VALORES VÁLIDOS PARA "intention":
        - "withdraw_request" = usuário quer retirar item
        - "withdraw_confirm" = usuário confirmou retirada 
        - "doubt" = usuário tem dúvida/pergunta
        - "stock_query" = usuário quer consultar estoque
        - "not_understood" = não entendi o comando

        VALORES VÁLIDOS PARA "stella_analysis":
        - "normal" = operação normal
        - "low_stock_alert" = estoque baixo (quantidade <= mínima)
        - "critical_stock_alert" = estoque crítico (quantidade <= crítica)
        - "outlier_withdraw_request" = quantidade solicitada muito alta/baixa
        - "ambiguous" = comando ambíguo, precisa esclarecimento
        - "not_understood" = não consegui entender

        REGRAS IMPORTANTES:
        - Use APENAS os valores listados acima
        - Normalize nomes (ex: "seringa 10ml" → "seringa_10ml")
        - Retorne APENAS JSON válido
        - Seja natural e amigável
        - Verifique se retirada deixará estoque crítico/baixo
        - Para ambiguidade, use intention="doubt" e stella_analysis="ambiguous"

        EXEMPLOS CORRETOS:
        
        Comando: "Preciso de 5 seringas"
        {{
            "intention": "withdraw_request",
            "items": [{{"item": "seringa_10ml", "quantidade": 5}}],
            "response": "Você quer 5 seringas de 10ml ou 5ml? Temos ambas disponíveis.",
            "stella_analysis": "ambiguous",
            "reason": "Tipo de seringa não especificado"
        }}

        Comando: "Confirmo 5 seringas 10ml"
        {{
            "intention": "withdraw_confirm", 
            "items": [{{"item": "seringa_10ml", "quantidade": 5}}],
            "response": "Registrei a retirada de 5 seringas de 10ml. Restam 45 unidades na gaveta B.",
            "stella_analysis": "normal"
        }}

        Comando: "Quanto tem de máscaras?"
        {{
            "intention": "stock_query",
            "items": [{{"item": "mascara_n95", "quantidade": 0}}],
            "response": "Temos 25 máscaras N95 disponíveis na gaveta A (estoque baixo - mínimo é 30).",
            "stella_analysis": "low_stock_alert"
        }}

        Comando: "blablabla"
        {{
            "intention": "not_understood",
            "items": [],
            "response": "Desculpe, não entendi. Você pode repetir ou perguntar sobre retiradas ou consultas de estoque?",
            "stella_analysis": "not_understood"
        }}

        CONTEXTO DA CONVERSA:
        {sess.history}

        RESPONDA APENAS COM JSON VÁLIDO:
        """
    
    try:
        response = sess.send_message(prompt)
        
        # Limpa a resposta
        clean_text = response.text.strip()
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:-3]
        elif clean_text.startswith('```'):
            clean_text = clean_text[3:-3]

        logger.debug(f"Resposta limpa do Gemini: {clean_text}")

        resultado = json.loads(clean_text)
        
        # ✅ VALIDAÇÃO ADICIONAL DOS ENUMS
        valid_intentions = ["withdraw_request", "withdraw_confirm", "doubt", "stock_query", "not_understood"]
        valid_analyses = ["normal", "low_stock_alert", "critical_stock_alert", "outlier_withdraw_request", "ambiguous", "not_understood"]
        
        if resultado.get("intention") not in valid_intentions:
            logger.warning(f"IA retornou intention inválida: {resultado.get('intention')}")
            resultado["intention"] = "not_understood"
            
        if resultado.get("stella_analysis") not in valid_analyses:
            logger.warning(f"IA retornou stella_analysis inválida: {resultado.get('stella_analysis')}")
            resultado["stella_analysis"] = "not_understood"
        
        logger.success(f"SessionID: {session_id} - Comando interpretado: {resultado.get('intention', 'N/A')}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao interpretar (sessão {session_id}): {e}")
        return {
            "intention": "not_understood",
            "items": [],
            "response": "Houve um erro no processamento. Pode repetir sua solicitação?",
            "stella_analysis": "not_understood"
        }

if __name__ == "__main__":
    # Fallback: inicia chat interativo integrado
    pass
