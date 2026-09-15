import os
import sys
import glob
import time
from typing import TypedDict
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# 1. Carrega configurações do arquivo .env
load_dotenv()

# 2. Inicializa o modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
)

def extrair_texto(resposta) -> str:
    """Extrai texto limpo independentemente do formato de retorno da API."""
    if isinstance(resposta.content, list):
        return resposta.content[0].get('text', '')
    return str(resposta.content)

def carregar_acervo_tecnico(pasta_acervo: str = "acervo") -> str:
    """Lê todos os templates e normas da pasta acervo/."""
    if not os.path.exists(pasta_acervo):
        return ""
    
    conteudos = []
    arquivos = glob.glob(os.path.join(pasta_acervo, "*.md")) + glob.glob(os.path.join(pasta_acervo, "*.txt"))
    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        with open(caminho, "r", encoding="utf-8") as f:
            conteudos.append(f"=== REFERÊNCIA DO ACERVO: {nome_arquivo} ===\n{f.read().strip()}")
    
    return "\n\n".join(conteudos)

# 3. Estado compartilhado do fluxo
class EstadoProjeto(TypedDict):
    dados_cliente: str
    base_conhecimento: str
    diagnostico_tecnico: str
    planejamento_operacional: str
    ajustes_do_engenheiro: str
    proposta_final: str

# 4. Nós dos Agentes
def agente_diagnostico(estado: EstadoProjeto):
    print("\n⚡ [1/3 - Agente de Proteção] Analisando transitórios com base no Acervo...")
    prompt = f"""Você é o Engenheiro Especialista em Proteção da KR Engenharia.
Faça a análise técnica estrita do problema relatado utilizando as referências do Acervo Técnico:

REFERÊNCIAS TÉCNICAS:
{estado['base_conhecimento']}

SUA MISSÃO:
- Identificar funções ANSI e fenômenos elétricos envolvidos (inrush, saturação de TC, harmônicos, descoordenação).
- Citar expressamente as normas aplicáveis (ex: IEC 60909, IEEE 141, IEEE 399, IEEE 242, NBR 14039).
- Apontar os estudos necessários a rodar no software ETAP.
Retorne um parecer técnico objetivo para o diretor técnico."""

    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=estado["dados_cliente"])
    ])
    return {"diagnostico_tecnico": extrair_texto(resp)}

def agente_operacoes(estado: EstadoProjeto):
    print("🛠️ [2/3 - Agente de Campo] Estruturando estratégia de comissionamento e limites...")
    prompt = f"""Você é o Coordenador de Comissionamento e Campo da KR Engenharia.
Com base no diagnóstico técnico e nas premissas operacionais da empresa:

PREMISSAS DO ACERVO:
{estado['base_conhecimento']}

SUA MISSÃO:
- Definir o que é feito em laboratório (TAF / simulação prévia para mitigar risco).
- Planejar a intervenção em campo (TAC / injeção secundária com mala microprocessada).
- Destacar os limites operacionais (RDO diário, necessidade de acompanhamento pelo cliente, não rastreamento de cabos de força)."""

    contexto = f"Demanda:\n{estado['dados_cliente']}\n\nDiagnóstico Elétrico:\n{estado['diagnostico_tecnico']}"
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=contexto)
    ])
    return {"planejamento_operacional": extrair_texto(resp)}

def agente_comercial(estado: EstadoProjeto):
    print("📋 [3/3 - Agente Comercial] Consolidando proposta institucional com ART...")
    prompt = f"""Você é o Diretor Técnico da KR Engenharia (Eng. Kayllon Rogger Nunes - CREA-MG nº 141854962-2).
Consolide as análises em uma Proposta Técnica Comercial executiva de alto nível:

PADRÃO INSTITUCIONAL E CONTRATUAL DO ACERVO:
{estado['base_conhecimento']}

SUA MISSÃO:
- Cabeçalho formal da KR Consultoria e Soluções em Engenharia LTDA.
- Resumo do problema e metodologia focada na redução de downtime.
- Escopo detalhado por fases e entregáveis formais (DataBook As-Built e ART perante o CREA-MG).
- Cláusulas de blindagem contratual (prazo de 5 dias para comentários, 1 rodada de revisão inclusa, despesas reembolsáveis com BDI e validade da proposta).
- Incorpore fielmente as condições comerciais inseridas pelo Engenheiro no campo 'Ajustes do Engenheiro'."""

    contexto = f"""
DIAGNÓSTICO TÉCNICO:
{estado['diagnostico_tecnico']}

PLANEJAMENTO OPERACIONAL:
{estado['planejamento_operacional']}

DIRETRIZES DO ENGENHEIRO RESPONSÁVEL:
{estado['ajustes_do_engenheiro']}
"""
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=contexto)
    ])
    return {"proposta_final": extrair_texto(resp)}

# 5. Execução Principal com Pausas para o Plano Gratuito
if __name__ == "__main__":
    caminho_demanda = "demanda.txt"
    
    if not os.path.exists(caminho_demanda):
        print(f"❌ Arquivo '{caminho_demanda}' não encontrado.")
        sys.exit(1)
        
    with open(caminho_demanda, "r", encoding="utf-8") as f:
        dados_cliente = f.read().strip()
        
    if not dados_cliente:
        print(f"❌ O arquivo '{caminho_demanda}' está vazio.")
        sys.exit(1)

    # Carrega acervo
    acervo = carregar_acervo_tecnico("acervo")
    if acervo:
        print("📚 Acervo técnico institucional carregado com sucesso!")
    else:
        print("⚠️ Pasta 'acervo/' vazia ou ausente. Prosseguindo com diretrizes padrão.")

    print("==========================================================")
    print("🚀 PIPELINE MULTI-AGENTE KR ENGENHARIA (MODO GRATUITO)")
    print("==========================================================")
    
    estado_parcial = {
        "dados_cliente": dados_cliente,
        "base_conhecimento": acervo,
        "diagnostico_tecnico": "",
        "planejamento_operacional": "",
        "ajustes_do_engenheiro": "",
        "proposta_final": ""
    }
    
    # 1. Agente de Diagnóstico
    res_diag = agente_diagnostico(estado_parcial)
    estado_parcial["diagnostico_tecnico"] = res_diag["diagnostico_tecnico"]
    
    # Pausa de segurança de 15s para a cota gratuita
    print("\n⏳ Aguardando 15s para respeitar a cota de requisições da API gratuita...")
    time.sleep(15)

    # 2. Agente de Operações
    res_ops = agente_operacoes(estado_parcial)
    estado_parcial["planejamento_operacional"] = res_ops["planejamento_operacional"]
    
    # 3. Pausa Human-in-the-Loop para o Eng. Kayllon
    print("\n" + "-"*60)
    print("🔍 DIAGNÓSTICO E OPERAÇÕES CONCLUÍDOS!")
    print("-"*60)
    print("Insira abaixo observações comerciais/técnicas para a proposta")
    print("(Exemplo: 'Prazo de 3 semanas. Valor: R$ 26.500,00 com 50% na entrada'):")
    
    ajustes = input("\n👉 Suas diretrizes comerciais (ou Enter para padrão): ").strip()
    estado_parcial["ajustes_do_engenheiro"] = ajustes if ajustes else "Condições comerciais padrão da KR Engenharia."
    
    # Pausa de segurança de 15s antes do Comercial
    print("\n⏳ Aguardando 15s para a chamada final...")
    time.sleep(15)

    # 4. Agente Comercial
    res_comercial = agente_comercial(estado_parcial)
    estado_parcial["proposta_final"] = res_comercial["proposta_final"]
    
    # 5. Salva a proposta gerada em output/ e na raiz
    os.makedirs("output", exist_ok=True)
    arquivo_saida = "output/proposta_gerada.md"
    with open(arquivo_saida, "w", encoding="utf-8") as f:
        f.write(estado_parcial["proposta_final"])
        
    print("\n" + "="*60)
    print(f"✅ SUCESSO! Proposta final salva em: {arquivo_saida}")
    print("👉 Para gerar o documento executivo em HTML/PDF, execute:")
    print("   python gerar_documento.py")
    print("="*60)
