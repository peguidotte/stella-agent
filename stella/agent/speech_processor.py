import json
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from loguru import logger

# Corrigindo a importação - mudando de relativa para absoluta
try:
    from stella.agent.mock_rabbitmq import mock_rabbitmq
except ImportError:
    # Fallback para importação direta quando executado como script
    try:
        from mock_rabbitmq import mock_rabbitmq
        logger.info("Mock RabbitMQ importado localmente")
    except ImportError:
        logger.error("Não foi possível importar mock_rabbitmq")
        mock_rabbitmq = None

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

# Funções de fallback removidas - usando apenas RabbitMQ
# def get_command_from_api(endpoint="comand"): - REMOVIDA
# def read_json(arquivo): - REMOVIDA

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
    
    # Cria contexto de estoque simplificado
    itens_disponiveis = list(estoque_data.get('estoque', {}).keys())
    
    prompt = f"""
Você é Stella, assistente de almoxarifado hospitalar. Analise este comando: "{comando}"

ITENS DISPONÍVEIS NO ESTOQUE:
{', '.join(itens_disponiveis)}

IDENTIFIQUE A INTENÇÃO:

1. RETIRADA DE ITEM: "preciso", "quero", "peguei", "retirar"
   Retorne: {{"intencao": "registrar_retirada", "itens": [{{"item": "nome_item", "quantidade": numero}}], "confirmacao": "Texto natural"}}

2. CONSULTA ESTOQUE: "quanto tem", "quantos", "estoque"  
   Retorne: {{"intencao": "consultar_estoque", "itens": [{{"item": "nome_item"}}], "confirmacao": "Texto natural"}}

3. CANCELAR: "cancelar", "desistir"
   Retorne: {{"intencao": "cancelar_registro", "confirmacao": "Texto natural"}}

4. DÚVIDAS: perguntas sobre localização
   Retorne: {{"intencao": "responder_duvida", "confirmacao": "Texto natural"}}

5. NÃO ENTENDIDO: qualquer outra coisa
   Retorne: {{"intencao": "nao_entendido", "confirmacao": "Não entendi. Pode reformular?"}}

IMPORTANTE:
- Normalize nomes (ex: "seringa 10ml" → "seringa_10ml")
- Retorne APENAS JSON válido
- Seja natural e amigável
- Se o item não existir no estoque, use intenção "nao_entendido"

RESPONDA APENAS COM JSON:
"""
    
    try:
        response = model.generate_content(prompt)
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

def get_command_from_rabbitmq(topic="comandos_stella"):
    """
    Busca comandos do tópico RabbitMQ (mock)
    
    Args:
        topic: Nome do tópico para consumir mensagens
        
    Returns:
        Comando processado ou None em caso de falha
    """
    try:
        logger.info(f"Buscando comando do tópico RabbitMQ: {topic}")
        
        # Consome mensagem do tópico
        message = mock_rabbitmq.consume(topic)
        
        if message:
            # Extrai o conteúdo da mensagem
            content = message.get('content', {})
            logger.success(f"Comando recebido do RabbitMQ: {content}")
            
            # Tenta extrair o comando do conteúdo
            if isinstance(content, dict) and 'comando' in content:
                return content['comando'].lower()
            elif isinstance(content, str):
                return content.lower()
            else:
                logger.error("Formato de mensagem não reconhecido")
                return None
        else:
            logger.info(f"Nenhuma mensagem disponível no tópico {topic}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao acessar RabbitMQ: {e}")
        return None

def publish_response_to_rabbitmq(response, topic="respostas_stella"):
    """
    Publica resposta no tópico RabbitMQ (mock)
    
    Args:
        response: Resposta a ser publicada
        topic: Nome do tópico para publicar
        
    Returns:
        True se publicado com sucesso, False caso contrário
    """
    try:
        logger.info(f"Publicando resposta no tópico RabbitMQ: {topic}")
        
        # Formata resposta para publicação
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "resposta": response
        }
        
        # Publica no tópico
        result = mock_rabbitmq.publish(topic, response_data)
        
        if result:
            logger.success(f"Resposta publicada com sucesso no tópico {topic}")
        else:
            logger.error(f"Falha ao publicar resposta no tópico {topic}")
            
        return result
        
    except Exception as e:
        logger.error(f"Erro ao publicar resposta no RabbitMQ: {e}")
        return False

def process_action(resultado):
    if not resultado:
        return "Comando não reconhecido."
    
    intencao = resultado.get('intencao')
    itens = resultado.get('itens', [])
    confirmacao = resultado.get('confirmacao', '')
    
    print(f"Intenção identificada: {intencao}")
    if itens:
        print(f"Itens processados: {itens}")
    
    # Publica a resposta no RabbitMQ
    publish_response_to_rabbitmq(resultado)
    
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

# Simplificando para usar APENAS RabbitMQ
def get_command():
    """Obtém comando APENAS do RabbitMQ mock - sem fallbacks"""
    
    # Tenta obter o comando do RabbitMQ
    comando = get_command_from_rabbitmq()
    if comando:
        logger.info("Comando obtido via RabbitMQ")
        return comando
    else:
        logger.debug("Nenhum comando disponível no RabbitMQ")
        return None

# Novo fluxo principal
if __name__ == "__main__":
    comando = get_command()
    if comando:
        print(f"Comando: {comando}\n")
        resultado = command_interpreter(comando)
        if resultado:
            resposta = process_action(resultado)
        else:
            print("Comando não entendido. Tente reformular.")
    else:
        print("Nenhum comando válido para processar.")
