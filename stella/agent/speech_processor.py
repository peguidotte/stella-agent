import datetime
import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger
import sys
import time
from typing import Dict, Optional, Any
import asyncio
import httpx
from stella.messaging.publisher import publish

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

api_key = require_gemini_env()

genai.configure(api_key=api_key)

MODEL_ID = 'gemini-2.5-flash'
SYSTEM_INSTRUCTION = (
    "Você é Stella, uma assistente de almoxarifado dos laboratórios DASA. Sua função é ser "
    "objetiva e garantir a rapidez na retirada de itens, então fale de forma clara e direta." 
    "Caso o usuário peça para que você se apresente, na sua apresentação deixe claro o seu objetivo e que você é assistente de almoxarifado dos laboratórios DASA."
    "Sempre retorne JSON válido, sem exceções, e não adicione explicações fora do JSON. "
    "Analise o estoque antes de confirmar qualquer retirada. Se o estoque for atingir nível baixo ou crítico após a requisição do usuário, alerte o usuário. "
    "O JSON deve ter a seguinte estrutura e valores:"
    """
    {
        "intention": "string (um de: withdraw_request, withdraw_confirm, doubt, stock_query, not_understood, normal)",
        "items": "array (opcional, lista de: {'productName': 'nome_item', 'quantity': numero})",
        "response": "string (resposta natural e amigável para o usuário)",
        "stella_analysis": "string (um de: normal, low_stock_alert, critical_stock_alert, outlier_withdraw_request, ambiguous, not_understood, farewell, greeting)",
        "reason": "string (opcional, justificativa para a análise)"
    }
    """
    "Normalize nomes de itens (ex: 'seringa 10ml' para 'seringa_10ml')."
    "Antes de um withdraw confirm, peça a confirmação ao usuário. Exemplo de confirmação: 'Você confirma a retirada de x itens?'"
    "Depois da confirmação deixe claro ao usuário que você confirmou a retirada. Exemplo de resposta: 'Retirada de x itens confirmada. Obrigada!'"
    "Após uma withdraw confirm, SOMENTE EM CASO em que o usuário peça para cancelar a última requisição, instrua ele a falar com o gerente de estoque"
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
async def load_external_stock(base_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Busca estoque da API externa e retorna um dicionário indexado por nome normalizado.
    Estrutura da API externa (GET /products):
    [
      {
        "id": "string",
        "name": "string",
        "description": "string",
        "quantity": 0,
        "createdAt": "2025-09-24T04:12:55.092Z",
        "updatedAt": "2025-09-24T04:12:55.093Z",
        "categoryName": "string"
      }
    ]
    """
    # Permite configurar via variável de ambiente INVENTORY_API_URL
    base = (base_url or os.environ.get("INVENTORY_API_URL") or "http://localhost:8080").rstrip('/')
    url = base + "/products"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            items = resp.json() or []
            def _norm(s: str) -> str:
                s = (s or "").strip().lower()
                # normaliza espaços e separadores comuns
                for ch in [" ", ",", ".", ";", ":", "/", "\\"]:
                    s = s.replace(ch, "_")
                while "__" in s:
                    s = s.replace("__", "_")
                return s.strip("_")
            stock_map: Dict[str, Any] = {}
            for it in items:
                name = it.get("name") or ""
                norm = _norm(name)
                stock_map[norm] = {
                    "id": it.get("id"),
                    "name": name,
                    "description": it.get("description"),
                    "quantity": int(it.get("quantity", 0)),
                    "createdAt": it.get("createdAt"),
                    "updatedAt": it.get("updatedAt"),
                    "categoryName": it.get("categoryName"),
                }
            return stock_map
    except httpx.HTTPError as e:
        logger.error(f"Erro ao consultar estoque externo: {e}")
        return {}
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar estoque externo: {e}")
        return {}
    
    
async def publish_withdraw_confirm(session_id: str, items: list):
    """
    Publica confirmação de retirada no RabbitMQ de forma assíncrona
    """
    try:
        
        
        payload = {
            "itens": items,
            "withdrawBy": session_id 
        }
        
        logger.debug(f"Preparando para publicar confirmação de retirada | `{payload}`")
        
        await asyncio.to_thread(publish, 'stock', 'remove', payload)
        logger.success(f"📤 Confirmação de retirada publicada | Sessão: {session_id}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao publicar confirmação: {e}")

async def command_interpreter(comando: str, session_id: str):
    switch_active_session(session_id)
    sess = get_or_create_session(session_id)
    # Carrega estoque da API externa
    external_stock = await load_external_stock()
    
    # Formatar estoque de forma legível para a IA
    estoque_formatado = ""
    for norm_name, item in external_stock.items():
        quantidade_atual = item.get('quantity', 0)
        categoria = item.get('categoryName') or 'N/A'
        estoque_formatado += (
            f"\n• {norm_name}: {item.get('name')}\n"
            f"- Quantidade atual: {quantidade_atual} unidade(s)\n"
            f"- Categoria: {categoria}\n"
        )
    
    prompt = f"""
        Analise este comando: "{comando}"

        ESTOQUE ATUAL:
        {estoque_formatado}
        """
    
    try:
        # ✅ Usar asyncio.to_thread para operação síncrona do Gemini
        response = await asyncio.to_thread(sess.send_message, prompt)
        
        # Limpa a resposta
        clean_text = response.text.strip()
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:-3]
        elif clean_text.startswith('```'):
            clean_text = clean_text[3:-3]

        logger.debug(f"Resposta limpa do Gemini: {clean_text}")

        resultado = json.loads(clean_text)
        
        valid_intentions = ["withdraw_request", "withdraw_confirm", "doubt", "stock_query", "not_understood", "normal"]
        valid_analyses = ["normal", "low_stock_alert", "critical_stock_alert", "outlier_withdraw_request", "ambiguous", "not_understood", "greeting", "farewell"]
        
        if resultado.get("intention") not in valid_intentions:
            logger.warning(f"IA retornou intention inválida: {resultado.get('intention')}")
            resultado["intention"] = "not_understood"
            
        if resultado.get("stella_analysis") not in valid_analyses:
            logger.warning(f"IA retornou stella_analysis inválida: {resultado.get('stella_analysis')}")
            resultado["stella_analysis"] = "not_understood"
            
        # Pré-validação para pedidos de retirada: informa disponibilidade antes da confirmação
        if resultado.get("intention") == "withdraw_request":
            pedidos = resultado.get("items", [])
            if pedidos:
                def _norm(s: str) -> str:
                    s = (s or "").strip().lower()
                    for ch in [" ", ",", ".", ";", ":", "/", "\\"]:
                        s = s.replace(ch, "_")
                    while "__" in s:
                        s = s.replace("__", "_")
                    return s.strip("_")

                faltantes = []
                insuficientes = []
                disponiveis = []
                for it in pedidos:
                    name = it.get("productName") or ""
                    qty = int(it.get("quantity", 0))
                    norm = _norm(name)
                    stock_item = external_stock.get(norm)
                    if not stock_item:
                        faltantes.append(name)
                        continue
                    available = int(stock_item.get("quantity", 0))
                    if qty > available:
                        insuficientes.append({
                            "name": name,
                            "requested": qty,
                            "available": available
                        })
                    else:
                        disponiveis.append({
                            "name": name,
                            "requested": qty,
                            "available": available
                        })

                info_msgs = []
                if disponiveis:
                    info_msgs.append(
                        "Disponível: " + ", ".join([f"{d['name']} ({d['requested']}/{d['available']})" for d in disponiveis])
                    )
                if insuficientes:
                    info_msgs.append(
                        "Estoque insuficiente: " + ", ".join([f"{d['name']} (solicitado {d['requested']}, disponível {d['available']})" for d in insuficientes])
                    )
                if faltantes:
                    info_msgs.append("Não encontrado(s): " + ", ".join(faltantes))

                if info_msgs:
                    complemento = " | ".join(info_msgs)
                    resultado["stella_analysis"] = resultado.get("stella_analysis", "normal")
                    resultado["response"] = f"{resultado.get('response', '')} (Checagem de estoque: {complemento})".strip()

        if resultado.get("intention") == "withdraw_confirm":
            items_confirmados = resultado.get("items", [])
            if items_confirmados:
                # valida itens contra estoque externo
                def _norm(s: str) -> str:
                    s = (s or "").strip().lower()
                    for ch in [" ", ",", ".", ";", ":", "/", "\\"]:
                        s = s.replace(ch, "_")
                    while "__" in s:
                        s = s.replace("__", "_")
                    return s.strip("_")

                faltantes = []
                insuficientes = []
                for it in items_confirmados:
                    name = it.get("productName") or ""
                    qty = int(it.get("quantity", 0))
                    norm = _norm(name)
                    stock_item = external_stock.get(norm)
                    if not stock_item:
                        faltantes.append(name)
                        continue
                    if qty > int(stock_item.get("quantity", 0)):
                        insuficientes.append({
                            "name": name,
                            "requested": qty,
                            "available": int(stock_item.get("quantity", 0))
                        })

                if faltantes or insuficientes:
                    # Não publica e orienta usuário
                    msg_parts = []
                    if faltantes:
                        msg_parts.append(f"Itens não encontrados: {', '.join(faltantes)}")
                    if insuficientes:
                        det = ", ".join([f"{d['name']} (solicitado {d['requested']}, disponível {d['available']})" for d in insuficientes])
                        msg_parts.append(f"Itens com estoque insuficiente: {det}")
                    resultado["intention"] = "doubt"
                    resultado["stella_analysis"] = "ambiguous"
                    resultado["response"] = (
                        "Não consegui confirmar a retirada. " + "; ".join(msg_parts) + 
                        ". Deseja ajustar a quantidade ou escolher outro item?"
                    )
                else:
                    await publish_withdraw_confirm(session_id, items_confirmados)
                    logger.info(f"📤 Publicação de confirmação iniciada | Sessão: {session_id}")
        
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
    """
    Interface de teste interativo para o command_interpreter
    Permite testar comandos e verificar o contexto da sessão
    """
    import uuid
    
    print("🤖 Stella Agent - Teste do Speech Processor")
    print("=" * 50)
    print("Comandos disponíveis:")
    print("  /help     - Mostra esta ajuda")
    print("  /session  - Mostra informações da sessão atual")
    print("  /history  - Mostra histórico da conversa")
    print("  /clear    - Limpa histórico da sessão")
    print("  /new      - Cria nova sessão")
    print("  /quit     - Sai do teste")
    print()
    
    # Sessão de teste
    current_session_id = str(uuid.uuid4())[:8]
    print(f"📝 Sessão de teste criada: {current_session_id}")
    print()
    
    while True:
        try:
            # Prompt com sessão atual
            comando = input(f"[{current_session_id}] Você: ").strip()
            
            if not comando:
                continue
                
            # Comandos especiais
            if comando == "/quit":
                print("👋 Até logo!")
                break
                
            elif comando == "/help":
                print("\nComandos disponíveis:")
                print("  /help     - Mostra esta ajuda")
                print("  /session  - Mostra informações da sessão atual")
                print("  /history  - Mostra histórico da conversa")
                print("  /clear    - Limpa histórico da sessão")
                print("  /new      - Cria nova sessão")
                print("  /quit     - Sai do teste")
                print()
                continue
                
            elif comando == "/session":
                sess = get_or_create_session(current_session_id)
                print(f"📊 Sessão: {current_session_id}")
                print(f"📝 Mensagens na sessão: {len(sess.history) if hasattr(sess, 'history') else 'N/A'}")
                print(f"⏰ Último acesso: {_LAST_SEEN.get(current_session_id, 'N/A')}")
                print()
                continue
                
            elif comando == "/history":
                sess = get_or_create_session(current_session_id)
                if hasattr(sess, 'history') and sess.history:
                    print("📜 Histórico da conversa:")
                    for i, msg in enumerate(sess.history):
                        role = "👤 Você" if msg.role == "user" else "🤖 Stella"
                        content = msg.parts[0].text[:100] + "..." if len(msg.parts[0].text) > 100 else msg.parts[0].text
                        print(f"  {i+1}. {role}: {content}")
                else:
                    print("📜 Nenhum histórico ainda.")
                print()
                continue
                
            elif comando == "/clear":
                if end_session(current_session_id):
                    print(f"🗑️ Histórico da sessão {current_session_id} limpo.")
                    # Cria nova sessão
                    current_session_id = str(uuid.uuid4())[:8]
                    print(f"📝 Nova sessão criada: {current_session_id}")
                else:
                    print("❌ Erro ao limpar sessão.")
                print()
                continue
                
            elif comando == "/new":
                current_session_id = str(uuid.uuid4())[:8]
                print(f"📝 Nova sessão criada: {current_session_id}")
                print()
                continue
            
            # Processa comando normal
            print("🤖 Stella está pensando...")
            
            start_time = time.time()
            resultado = command_interpreter(comando, current_session_id)
            end_time = time.time()
            
            # Mostra resultado
            print(f"⚡ Tempo de resposta: {(end_time - start_time):.2f}s")
            print()
            
            print("📋 Análise da Stella:")
            print(f"  🎯 Intention: {resultado.get('intention', 'N/A')}")
            print(f"  📦 Items: {resultado.get('items', [])}")
            print(f"  💬 Response: {resultado.get('response', 'N/A')}")
            print(f"  🔍 Analysis: {resultado.get('stella_analysis', 'N/A')}")
            if resultado.get('reason'):
                print(f"  💡 Reason: {resultado.get('reason')}")
            print()
            
            # Mostra resposta da Stella
            print("🤖 Stella:", resultado.get('response', 'N/A'))
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n👋 Teste interrompido pelo usuário.")
            break
        except Exception as e:
            print(f"❌ Erro durante o teste: {e}")
            print("Tente novamente ou use /quit para sair.")
            print()
