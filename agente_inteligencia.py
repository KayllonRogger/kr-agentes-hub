import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from grafo_agentes import carregar_acervo_tecnico

# 1. Carrega configurações do .env
load_dotenv()

# 2. Inicializa o modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
)

def extrair_texto(resposta) -> str:
    if isinstance(resposta.content, list):
        return resposta.content[0].get('text', '')
    return str(resposta.content)

PROMPT_INTELIGENCIA = """Você é o Engenheiro Especialista em Inteligência Regulatória e Análise de Editais da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).

DIRETRIZES E LIMITES DE ESCOPO DA KR ENGENHARIA:
{acervo}

SUA MISSÃO:
Analisar criticamente o Termo de Referência (TR), especificação técnica ou solicitação de concorrência enviada pelo cliente e produzir uma ANÁLISE DE CONFORMIDADE E LISTA DE DESVIOS TÉCNICOS.

ESTRUTURA DA RESPOSTA:
1. RESUMO EXECUTIVO DA DEMANDA: Objeto do edital/TR, tensão da planta, principais equipamentos e prazos exigidos.
2. MATRIZ DE ADERÊNCIA E DESVIOS TÉCNICOS:
   - Itens Aceitos no Escopo Padrão da KR Engenharia.
   - Lista de Desvios e Exclusões Explícitas (o que deve constar na proposta como NÃO INCLUSO para evitar passivos ou retrabalho não remunerado).
3. EXIGÊNCIAS DE HABILITAÇÃO E SEGURANÇA:
   - Documentos de equipe necessários (NR-10 SEP, NR-35, ASO).
   - Instrumentos exigidos e certificados de calibração RBC (Omicron, Conprove, Doble).
4. RECOMENDAÇÃO ESTRATÉGICA AO DIRETOR TÉCNICO:
   - Parecer recomendando: Proposta com Escopo Fechado, Regime de Horas (Guarda-Chuva) ou Recusa Técnica justificada.
"""

def analisar_especificacao_tecnica(texto_especificacao: str) -> str:
    print("\n🔍 [Agente de Inteligência] Cruzando especificação do cliente com limites de escopo da KR...")
    acervo = carregar_acervo_tecnico("acervo")
    
    prompt = PROMPT_INTELIGENCIA.format(acervo=acervo)
    
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"ESPECIFICAÇÃO TÉCNICA / TERMO DE REFERÊNCIA DO CLIENTE:\n\n{texto_especificacao}")
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
    # Exemplo simulando um trecho de especificação técnica rigorosa de cliente
    exemplo_edital = """
    ESPECIFICAÇÃO TÉCNICA - EDITAL DE CONCORRÊNCIA PRIVADA
    OBJETO: Contratação de empresa especializada para modernização do Sistema de Proteção e Automação da SE Principal 138/13,8 kV.
    EXIGÊNCIAS DO CLIENTE:
    1. A CONTRATADA deverá realizar levantamento físico em campo de todos os condutores de força e controle de todas as canaletas da subestação, com emissão de laudo de conformidade total com a NR-10.
    2. Parametrização e testes de injeção secundária de 12 relés de proteção durante a operação normal da planta, sem interrupção de carga.
    3. Entrega de projetos executivos civis de bases de concreto para novos cubículos.
    4. Prazo de atendimento a comentários nos desenhos: 24 horas após envio pela fiscalização.
    5. A CONTRATADA deverá arcar integralmente com despesas de viagens, alimentação e hospedagem sem direito a reembolso.
    """

    print("==========================================================")
    print("🚀 AUDITOR TÉCNICO DE EDITAIS E TR - KR ENGENHARIA")
    print("==========================================================")
    
    relatorio = analisar_especificacao_tecnica(exemplo_edital)
    
    os.makedirs("output", exist_ok=True)
    caminho_saida = "output/analise_edital.md"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    print("\n" + "="*60)
    print(f"✅ ANÁLISE DE CONFORMIDADE E DESVIOS SALVA EM: {caminho_saida}")
    print("="*60 + "\n")
    print(relatorio)
