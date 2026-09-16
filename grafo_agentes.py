import os
import sys
import time
from typing import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA
from utils import (
    get_llm,
    extrair_texto,
    carregar_acervo_tecnico,
    salvar_markdown_saida
)

# Estado compartilhado do fluxo de propostas técnicas
class EstadoProjeto(TypedDict):
    dados_cliente: str
    base_conhecimento: str
    diagnostico_tecnico: str
    planejamento_operacional: str
    ajustes_do_engenheiro: str
    proposta_final: str

# Nós dos Agentes
def agente_diagnostico(estado: EstadoProjeto) -> dict:
    print("\n⚡ [1/3 - Agente de Proteção] Analisando transitórios com base no Acervo...")
    prompt = f"""Você é o Engenheiro Especialista em Proteção da {DADOS_EMPRESA['nome_fantasia']}.
Faça a análise técnica estrita do problema relatado utilizando as referências do Acervo Técnico:

REFERÊNCIAS TÉCNICAS:
{estado['base_conhecimento']}

SUA MISSÃO:
- Identificar funções ANSI e fenômenos elétricos envolvidos (inrush, saturação de TC, harmônicos, descoordenação).
- Citar expressamente as normas aplicáveis (ex: IEC 60909, IEEE 141, IEEE 399, IEEE 242, NBR 14039).
- Apontar os estudos necessários a rodar no software ETAP.
Retorne um parecer técnico objetivo para o diretor técnico."""

    llm = get_llm(temperature=0.1)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=estado["dados_cliente"])
    ])
    return {"diagnostico_tecnico": extrair_texto(resp)}

def agente_operacoes(estado: EstadoProjeto) -> dict:
    print("🛠️ [2/3 - Agente de Campo] Estruturando estratégia de comissionamento e limites...")
    prompt = f"""Você é o Coordenador de Comissionamento e Campo da {DADOS_EMPRESA['nome_fantasia']}.
Com base no diagnóstico técnico e nas premissas operacionais da empresa:

PREMISSAS DO ACERVO:
{estado['base_conhecimento']}

SUA MISSÃO:
- Definir o que é feito em laboratório (TAF / simulação prévia para mitigar risco).
- Planejar a intervenção em campo (TAC / injeção secundária com mala microprocessada).
- Destacar os limites operacionais (RDO diário, necessidade de acompanhamento pelo cliente, não rastreamento de cabos de força)."""

    contexto = f"Demanda:\n{estado['dados_cliente']}\n\nDiagnóstico Elétrico:\n{estado['diagnostico_tecnico']}"
    llm = get_llm(temperature=0.2)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=contexto)
    ])
    return {"planejamento_operacional": extrair_texto(resp)}

def agente_comercial(estado: EstadoProjeto) -> dict:
    print("📋 [3/3 - Agente Comercial] Consolidando proposta institucional com ART...")
    prompt = f"""Você é o Diretor Técnico da {DADOS_EMPRESA['nome_fantasia']} ({DADOS_EMPRESA['responsavel_tecnico']} - {DADOS_EMPRESA['crea']}).
Consolide as análises em uma Proposta Técnica Comercial executiva de alto nível:

PADRÃO INSTITUCIONAL E CONTRATUAL DO ACERVO:
{estado['base_conhecimento']}

SUA MISSÃO:
- Cabeçalho formal da {DADOS_EMPRESA['razao_social']}.
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
    llm = get_llm(temperature=0.2)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=contexto)
    ])
    return {"proposta_final": extrair_texto(resp)}

def executar_pipeline_proposta(dados_cliente: str, ajustes_comerciais: str = "") -> dict:
    """Executa a esteira sequencial completa dos 3 agentes para gerar a proposta."""
    acervo = carregar_acervo_tecnico("acervo")
    estado: EstadoProjeto = {
        "dados_cliente": dados_cliente,
        "base_conhecimento": acervo,
        "diagnostico_tecnico": "",
        "planejamento_operacional": "",
        "ajustes_do_engenheiro": ajustes_comerciais or f"Condições comerciais padrão da {DADOS_EMPRESA['nome_fantasia']} com ART inclusa.",
        "proposta_final": ""
    }
    
    r_diag = agente_diagnostico(estado)
    estado["diagnostico_tecnico"] = r_diag["diagnostico_tecnico"]
    
    r_ops = agente_operacoes(estado)
    estado["planejamento_operacional"] = r_ops["planejamento_operacional"]
    
    r_com = agente_comercial(estado)
    estado["proposta_final"] = r_com["proposta_final"]
    
    salvar_markdown_saida("proposta_gerada.md", estado["proposta_final"])
    return estado

if __name__ == "__main__":
    caminho_demanda = "demanda.txt"
    
    if not os.path.exists(caminho_demanda):
        print(f"❌ Arquivo '{caminho_demanda}' não encontrado.")
        sys.exit(1)
        
    with open(caminho_demanda, "r", encoding="utf-8") as f:
        demanda = f.read().strip()
        
    if not demanda:
        print(f"❌ O arquivo '{caminho_demanda}' está vazio.")
        sys.exit(1)

    print("==========================================================")
    print("🚀 PIPELINE MULTI-AGENTE KR ENGENHARIA")
    print("==========================================================")
    
    resultado = executar_pipeline_proposta(demanda)
    print("\n" + "="*60)
    print("✅ SUCESSO! Proposta final salva em: output/proposta_gerada.md")
    print("👉 Para gerar o documento executivo em HTML/PDF, execute: python gerar_documento.py")
    print("="*60)
