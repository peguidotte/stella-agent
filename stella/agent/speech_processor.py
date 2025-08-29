import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

logger.info("Iniciando o carregamento da chave API do Gemini...")

# Tenta carregar do diretório atual e depois do diretório pai
env_paths = ["GEMINI_API_KEY.env", "../GEMINI_API_KEY.env", "../../GEMINI_API_KEY.env", ".env"]
api_key = None

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            logger.info(f"GEMINI_API_KEY carregada de: {env_path}")
            break

if not api_key:
    logger.error("GEMINI_API_KEY não encontrada.")
    logger.warning("Verifique se existe o arquivo 'GEMINI_API_KEY.env' no raiz do projeto.")
    logger.warning("Certifique-se de que a variável 'GEMINI_API_KEY' está definida no arquivo")
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please check that 'GEMINI_API_KEY.env' exists in the project root and contains the 'GEMINI_API_KEY' variable.")

logger.success("GEMINI_API_KEY carregada com sucesso.")
genai.configure(api_key=api_key)

def load_estoque_data():
    try:
        # Tenta diferentes caminhos para o arquivo de estoque
        estoque_paths = [
            'data/estoque_almoxarifado.json', 
            '../data/estoque_almoxarifado.json',
            '../../data/estoque_almoxarifado.json'
        ]
        
        for path in estoque_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        
        # Se não encontrou o arquivo, retorna dados de exemplo
        logger.warning("Arquivo de estoque não encontrado, usando dados de exemplo")
        return {"estoque": {}}
    except Exception as e:
        logger.error(f"Erro ao carregar dados do estoque: {e}")
        return {"estoque": {}}

def command_interpreter(comando):
    model = genai.GenerativeModel('gemini-1.5-flash')
    estoque_data = load_estoque_data()
    
    # 🔧 NOVA FORMA: Envia TODO o JSON do estoque
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
   Retorne: {{"intencao": "registrar_retirada", "itens": [{{"item": "nome_item", "quantidade": numero}}], "confirmacao": "Texto natural com avisos se necessário"}}

2. CONSULTA ESTOQUE: "quanto tem", "quantos", "estoque"  
   Retorne: {{"intencao": "consultar_estoque", "itens": [{{"item": "nome_item"}}], "confirmacao": "Texto natural com quantidade atual e localização"}}

3. CONSULTA LOCALIZAÇÃO: "onde está", "qual gaveta", "localização"
   Retorne: {{"intencao": "consultar_localizacao", "itens": [{{"item": "nome_item"}}], "confirmacao": "Texto natural com localização"}}

4. CANCELAR: "cancelar", "desistir"
   Retorne: {{"intencao": "cancelar_registro", "confirmacao": "Texto natural"}}

5. ALERTA ESTOQUE: quando detectar item em estado crítico/baixo
   Retorne: {{"intencao": "alerta_estoque", "confirmacao": "Texto natural com aviso"}}

6. NÃO ENTENDIDO: qualquer outra coisa
   Retorne: {{"intencao": "nao_entendido", "confirmacao": "Não entendi. Pode reformular?"}}

REGRAS IMPORTANTES:
- Normalize nomes (ex: "seringa 10ml" → "seringa_10ml")
- Retorne APENAS JSON válido
- Seja natural e amigável
- Em caso de ambiguidade, pergunte especificações (ex: qual tipo de seringa?)
- Se o item não existir no estoque, use intenção "nao_entendido"
- SEMPRE verifique se retirada deixará estoque em estado crítico/baixo
- Inclua avisos sobre localização quando relevante
- Para consultas, inclua quantidade atual e localização
- Detecte outliers (quantidades muito altas/baixas solicitadas)

EXEMPLOS DE RESPOSTAS COM CONTEXTO:
- Retirada normal: "Registrei 5 seringas de 10ml. Restam 45 unidades na gaveta B."
- Retirada com aviso: "⚠️ ATENÇÃO: Retirar 20 máscaras N95 deixará apenas 15 unidades (abaixo do mínimo de 30). Confirma?"
- Consulta: "Temos 150 seringas de 5ml disponíveis na gaveta B (estoque normal)."
- Crítico: "🔴 ALERTA: Agulhas 21G estão em estado CRÍTICO - apenas 5 unidades restantes!"

RESPONDA APENAS COM JSON:
"""
    
    # 🔍 PRINT DO PROMPT COMPLETO
    print("=" * 80)
    print("PROMPT ENVIADO PARA O GEMINI:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    try:
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt)
        logger.debug(f"Resposta bruta do Gemini: {response.text}")
        
        # Limpa a resposta
        clean_text = response.text.strip()
        if clean_text.startswith('```json'):
            clean_text = clean_text[7:-3]
        elif clean_text.startswith('```'):
            clean_text = clean_text[3:-3]
        
        resultado = json.loads(clean_text)
        logger.success(f"Comando interpretado com sucesso: {resultado.get('intencao', 'N/A')}")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao interpretar comando: {e}")
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

# =====================
# Chat integrado (StellaInteligente)
# =====================
class StellaInteligente:
    """Chat inteligente com Stella usando o Gemini (contexto mantido pela API)."""
    
    def __init__(self):
        self.user_name = "Usuário"
        self.pedidos_sessao = []  # Pedidos da sessão atual
        
        # Modelo Gemini com instrução de sistema e sessão de chat (histórico mantido pela API)
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            system_instruction=(
                "Você é Stella, assistente de almoxarifado hospitalar."
                " Mantenha conversa natural e contínua, use o contexto da sessão,"
                " seja objetiva, amigável e prestativa."
            ),
        )
        self.chat = self.model.start_chat(history=[])

    # -------- Deterministic estoque helpers --------
    def _get_estoque(self):
        try:
            data = load_estoque_data()
            return data.get('estoque', {})
        except Exception:
            return {}

    def _normalize_item(self, nome: str) -> str | None:
        t = (nome or '').lower().strip()
        t = t.replace('-', ' ').replace('_', ' ')
        # atalhos por palavras-chave
        if 'seringa' in t and ('10' in t or '10ml' in t or '10 ml' in t):
            return 'seringa_10ml'
        if 'seringa' in t and ('5' in t or '5ml' in t or '5 ml' in t):
            return 'seringa_5ml'
        if 'agulha' in t and '21' in t:
            return 'agulha_21g'
        if 'agulha' in t and '10' in t:
            return 'agulha_10g'
        if 'n95' in t or 'máscara' in t or 'mascara' in t:
            return 'mascara_n95'
        if 'luva' in t:
            return 'luva'
        if 'gaze' in t:
            return 'gaze'
        # tentativa direta
        key = t.replace(' ', '_')
        return key or None

    def _status_label(self, qtd: int | float, minimo: int | float, critico: int | float) -> str:
        try:
            if qtd <= critico:
                return '🔴 CRÍTICO'
            if qtd <= minimo:
                return '🟡 BAIXO'
            return '🟢 NORMAL'
        except Exception:
            return '🟢 NORMAL'

    def _responder_consulta_estoque(self, itens: list[dict]) -> str:
        estoque = self._get_estoque()
        respostas = []
        not_found = []
        for it in itens or []:
            nome = it.get('item') if isinstance(it, dict) else str(it)
            key = self._normalize_item(nome)
            dados = estoque.get(key or '')
            if not dados:
                not_found.append(nome)
                continue
            qtd = dados.get('quantidade_atual', 0)
            un = dados.get('unidade', 'unidade')
            loc = (dados.get('localizacao') or {}).get('gaveta', 'N/A')
            minimo = dados.get('quantidade_minima', 0)
            crit = dados.get('quantidade_critica', 0)
            status = self._status_label(qtd, minimo, crit)
            nome_full = dados.get('nome_completo', key)
            respostas.append(f"Temos {qtd} {un} de {nome_full} na gaveta {loc} ({status}).")
        if not_found:
            disponiveis = ', '.join(sorted(estoque.keys())) or '—'
            respostas.append(f"Itens não encontrados: {', '.join(not_found)}. Disponíveis: {disponiveis}.")
        return ' '.join(respostas) if respostas else 'Não encontrei esses itens no estoque.'

    def _responder_consulta_localizacao(self, itens: list[dict]) -> str:
        estoque = self._get_estoque()
        respostas = []
        not_found = []
        for it in itens or []:
            nome = it.get('item') if isinstance(it, dict) else str(it)
            key = self._normalize_item(nome)
            dados = estoque.get(key or '')
            if not dados:
                not_found.append(nome)
                continue
            loc = dados.get('localizacao', {}) or {}
            setor = loc.get('setor', '—')
            prat = loc.get('prateleira', '—')
            gav = loc.get('gaveta', '—')
            nome_full = dados.get('nome_completo', key)
            respostas.append(f"{nome_full} fica no Setor {setor}, Prateleira {prat}, Gaveta {gav}.")
        if not_found:
            disponiveis = ', '.join(sorted(estoque.keys())) or '—'
            respostas.append(f"Itens não encontrados: {', '.join(not_found)}. Disponíveis: {disponiveis}.")
        return ' '.join(respostas) if respostas else 'Não encontrei a localização solicitada.'

    # -------- Chat + roteamento de intenção --------
    def process_with_context(self, user_message: str) -> str:
        # 1) Tenta interpretar intenção primeiro (para evitar alucinações em consultas)
        try:
            resultado = command_interpreter(user_message)
            intencao = (resultado or {}).get('intencao')
            itens = (resultado or {}).get('itens', [])
            if intencao == 'consultar_estoque':
                return self._responder_consulta_estoque(itens)
            if intencao == 'consultar_localizacao':
                return self._responder_consulta_localizacao(itens)
            # Poderíamos tratar outras intenções aqui futuramente (registrar_retirada, etc.)
        except Exception as e:
            logger.debug(f"Falha na interpretação estruturada, usando chat: {e}")
        
        # 2) Fallback: conversa livre pelo chat do Gemini
        try:
            response = self.chat.send_message(user_message)
            resposta = (response.text or "").strip()
            if not resposta:
                resposta = self.generate_natural_response(user_message)
            return resposta
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return "Desculpe, tive um problema. Pode repetir sua mensagem?"

    def generate_natural_response(self, message: str) -> str:
        message_lower = message.lower()
        try:
            history_len = len(getattr(self.chat, 'history', []) or [])
        except Exception:
            history_len = 0
        
        if any(g in message_lower for g in ["olá", "oi", "ola", "hey", "e aí"]):
            return (f"Olá {self.user_name}! Sou a Stella, assistente do almoxarifado. Como posso ajudar você hoje?"
                    if history_len <= 1 else "Oi! Em que mais posso ajudar?")
        if any(w in message_lower for w in ["tudo bem", "como vai", "como está"]):
            return "Estou muito bem, obrigada! Pronta para ajudar com o almoxarifado. E você, como está?"
        if any(w in message_lower for w in ["nome", "quem é", "você é"]):
            return "Sou a Stella, sua assistente virtual do almoxarifado hospitalar. Estou aqui para ajudar com materiais e suprimentos!"
        if any(w in message_lower for w in ["pedido", "pedi", "solicitei", "último"]):
            if self.pedidos_sessao:
                return f"Você pediu: {', '.join(self.pedidos_sessao)}. Precisa de mais alguma coisa?"
            return "Ainda não vejo pedidos nesta conversa. O que você precisa?"
        if any(w in message_lower for w in ["obrigad", "valeu", "thanks"]):
            return "De nada! Foi um prazer ajudar. Se precisar de mais alguma coisa, estarei aqui!"
        return "Entendi! Como assistente do almoxarifado, posso ajudar com seringas, luvas, gazes e outros materiais. O que você precisa?"

    def show_history(self):
        print("\n" + "="*50)
        print("📝 HISTÓRICO DA CONVERSA")
        print("="*50)
        history = getattr(self.chat, 'history', []) or []
        for i, msg in enumerate(history, 1):
            try:
                role = getattr(msg, 'role', None) or (msg.get('role') if isinstance(msg, dict) else 'model')
            except Exception:
                role = 'model'
            role_name = self.user_name if role == 'user' else 'Stella'
            content_text = ''
            try:
                parts = getattr(msg, 'parts', None) or (msg.get('parts') if isinstance(msg, dict) else None)
                if parts is not None:
                    texts = []
                    for p in parts:
                        if hasattr(p, 'text'):
                            texts.append(p.text)
                        elif isinstance(p, dict) and 'text' in p:
                            texts.append(p['text'])
                        else:
                            texts.append(str(p))
                    content_text = ' '.join([t for t in texts if t])
                else:
                    content_text = str(getattr(msg, 'text', getattr(msg, 'content', '')))
            except Exception:
                content_text = ''
            content = (content_text[:100] + "...") if len(content_text) > 100 else content_text
            print(f"{i:2d}. {role_name}: {content}")
        print(f"\n💬 Total: {len(history)} mensagens")
        print("="*50)

    def show_pedidos(self):
        print("\n" + "="*30)
        print("📦 PEDIDOS DESTA SESSÃO")
        print("="*30)
        if self.pedidos_sessao:
            for i, pedido in enumerate(self.pedidos_sessao, 1):
                print(f"{i}. {pedido}")
        else:
            print("Nenhum pedido registrado ainda.")
        print("="*30)

    def start_chat(self):
        print("🧠 STELLA INTELIGENTE - GEMINI + CONTEXTO")
        print("=" * 50)
        self.user_name = input("Seu nome: ").strip() or "Usuário"
        print(f"\n✅ Olá {self.user_name}! Sistema inteligente ativo.")
        print("Digite 'sair' para encerrar, 'historico' para ver conversa\n")
        initial_message = (f"Olá {self.user_name}! Sou a Stella, sua assistente inteligente do almoxarifado. "
                           f"Como posso ajudar você hoje?")
        print(f"Stella: {initial_message}")
        try:
            while True:
                user_input = input(f"\n{self.user_name}: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['sair', 'exit', 'tchau']:
                    print("Stella: Até mais! Foi um prazer conversar com você! 👋")
                    break
                if user_input.lower() == 'historico':
                    self.show_history(); continue
                if user_input.lower() == 'pedidos':
                    self.show_pedidos(); continue
                print("🧠 Stella está processando...")
                ai_response = self.process_with_context(user_input)
                print(f"Stella: {ai_response}")
        except KeyboardInterrupt:
            print("\n\nTchau! 👋")
        except Exception as e:
            print(f"\n❌ Erro: {e}")

# Novo fluxo principal (RabbitMQ removido)
if __name__ == "__main__":
    # Fallback: inicia chat interativo integrado
    chat = StellaInteligente()
    chat.start_chat()
