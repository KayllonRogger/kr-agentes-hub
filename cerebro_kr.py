import os
import sys
from typing import TypedDict, Literal
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from config import DADOS_EMPRESA
from utils import get_llm, extrair_texto, salvar_markdown_saida
from grafo_agentes import executar_pipeline_proposta
from agente_marketing import gerar_conteudo_linkedin
from agente_prospeccao import gerar_cadencia_prospeccao
from agente_inteligencia import analisar_especificacao_tecnica
from agente_pos_comissionamento import gerar_pacote_encerramento
from agente_backoffice import processar_conformidade_backoffice
from gerar_documento import renderizar_proposta

# 1. Estado do Cérebro Central com Histórico de Memória
class EstadoCerebro(TypedDict):
    entrada_usuario: str
    categoria: str
    historico_conversa: list[dict]
    resposta_final: str

# 2. Nó Supervisor com Memória Contextual
def supervisor_triagem(estado: EstadoCerebro) -> dict:
    print("\n🧠 [Cérebro Central] Analisando mensagem considerando o histórico recente...")
    
    historico_texto = ""
    for msg in estado.get("historico_conversa", [])[-4:]:
        papel = "Usuário" if msg.get("role") == "user" else "Assistente"
        historico_texto += f"{papel}: {msg.get('content', '')[:200]}...\n"

    prompt = f"""Você é o Cérebro Central de Operações da {DADOS_EMPRESA['nome_fantasia']}.
Considere o histórico da conversa recente (se houver) para entender continuações e ajustes:

HISTÓRICO RECENTE:
{historico_texto if historico_texto else "Início da conversa."}

Classifique a solicitação do usuário em exatamente UMA das sete categorias abaixo:
1. PROPOSTA: Demandas de estudos elétricos, falhas em subestações ou elaboração/ajuste de propostas técnicas.
2. MARKETING: Criação ou resumo de artigos e posts para o LinkedIn.
3. PROSPECCAO: Estratégias de abordagem comercial e cadências para EPCistas/indústrias.
4. EDITAL: Análise de especificações técnicas, TRs e lista de desvios.
5. POS_OBRA: DataBook As-Built, ART CREA-MG e protocolos pós-energização.
6. BACKOFFICE: Liberação de equipe (NRs/ASO), calibração RBC de instrumentos e medições.
7. CONSULTA: Dúvidas gerais sobre normas ou engenharia elétrica.

Responda APENAS com a palavra da categoria (PROPOSTA, MARKETING, PROSPECCAO, EDITAL, POS_OBRA, BACKOFFICE ou CONSULTA)."""

    llm = get_llm(temperature=0.0)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=estado["entrada_usuario"])
    ])
    
    categoria = extrair_texto(resp).strip().upper()
    categorias_validas = ["PROPOSTA", "MARKETING", "PROSPECCAO", "EDITAL", "POS_OBRA", "BACKOFFICE", "CONSULTA"]
    if categoria not in categorias_validas:
        categoria = "CONSULTA"
        
    print(f"🎯 [Roteador] Intenção identificada: Departamento de **{categoria}**")
    return {"categoria": categoria}

# 3. Nós dos Departamentos
def departamento_propostas(estado: EstadoCerebro) -> dict:
    print("\n🏢 -> Ativando DEPARTAMENTO DE ENGENHARIA E PROPOSTAS...")
    resultado = executar_pipeline_proposta(estado["entrada_usuario"])
    renderizar_proposta()
    return {"resposta_final": f"Proposta Técnica e Documento Executivo gerados com sucesso na pasta 'output/'.\n\nResumo Técnico:\n{resultado['diagnostico_tecnico'][:350]}..."}

def departamento_marketing(estado: EstadoCerebro) -> dict:
    print("\n📢 -> Ativando DEPARTAMENTO DE MARKETING...")
    post = gerar_conteudo_linkedin(estado["entrada_usuario"])
    salvar_markdown_saida("post_linkedin.md", post)
    return {"resposta_final": f"Artigo para o LinkedIn salvo em 'output/post_linkedin.md'.\n\n{post}"}

def departamento_prospeccao(estado: EstadoCerebro) -> dict:
    print("\n🎯 -> Ativando DEPARTAMENTO DE PROSPECÇÃO B2B...")
    cadencia = gerar_cadencia_prospeccao(estado["entrada_usuario"])
    salvar_markdown_saida("cadencia_prospeccao.md", cadencia)
    return {"resposta_final": f"Plano de abordagem salvo em 'output/cadencia_prospeccao.md'.\n\n{cadencia}"}

def departamento_edital(estado: EstadoCerebro) -> dict:
    print("\n🔍 -> Ativando DEPARTAMENTO DE AUDITORIA DE EDITAIS...")
    relatorio = analisar_especificacao_tecnica(estado["entrada_usuario"])
    salvar_markdown_saida("analise_edital.md", relatorio)
    return {"resposta_final": f"Auditoria salva em 'output/analise_edital.md'.\n\n{relatorio}"}

def departamento_pos_obra(estado: EstadoCerebro) -> dict:
    print("\n📦 -> Ativando DEPARTAMENTO DE SUCESSO DO CLIENTE...")
    pacote = gerar_pacote_encerramento(estado["entrada_usuario"])
    salvar_markdown_saida("plano_pos_comissionamento.md", pacote)
    return {"resposta_final": f"DataBook e ART salvos em 'output/plano_pos_comissionamento.md'.\n\n{pacote}"}

def departamento_backoffice(estado: EstadoCerebro) -> dict:
    print("\n📋 -> Ativando DEPARTAMENTO DE BACKOFFICE E CONFORMIDADE...")
    relatorio = processar_conformidade_backoffice(estado["entrada_usuario"])
    salvar_markdown_saida("conformidade_backoffice.md", relatorio)
    return {"resposta_final": f"Dossiê salvo em 'output/conformidade_backoffice.md'.\n\n{relatorio}"}

def departamento_consulta(estado: EstadoCerebro) -> dict:
    print("\n💡 -> Ativando CONSULTORIA TÉCNICA DIRETA...")
    prompt = f"""Você é o Consultor Técnico Especialista da {DADOS_EMPRESA['nome_fantasia']}.
Responda com base no rigor normativo (IEEE, IEC 61850, ABNT, ONS) e considere o histórico anterior se for uma continuação de pergunta."""
    llm = get_llm(temperature=0.2)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=estado["entrada_usuario"])
    ])
    return {"resposta_final": extrair_texto(resp)}

# 4. Grafo de Roteamento com Memória
def escolher_caminho(estado: EstadoCerebro) -> Literal[
    "depto_propostas", "depto_marketing", "depto_prospeccao", 
    "depto_edital", "depto_pos_obra", "depto_backoffice", "depto_consulta"
]:
    rotas = {
        "PROPOSTA": "depto_propostas",
        "MARKETING": "depto_marketing",
        "PROSPECCAO": "depto_prospeccao",
        "EDITAL": "depto_edital",
        "POS_OBRA": "depto_pos_obra",
        "BACKOFFICE": "depto_backoffice",
    }
    return rotas.get(estado.get("categoria", ""), "depto_consulta")

workflow = StateGraph(EstadoCerebro)

workflow.add_node("supervisor", supervisor_triagem)
workflow.add_node("depto_propostas", departamento_propostas)
workflow.add_node("depto_marketing", departamento_marketing)
workflow.add_node("depto_prospeccao", departamento_prospeccao)
workflow.add_node("depto_edital", departamento_edital)
workflow.add_node("depto_pos_obra", departamento_pos_obra)
workflow.add_node("depto_backoffice", departamento_backoffice)
workflow.add_node("depto_consulta", departamento_consulta)

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", escolher_caminho)
workflow.add_edge("depto_propostas", END)
workflow.add_edge("depto_marketing", END)
workflow.add_edge("depto_prospeccao", END)
workflow.add_edge("depto_edital", END)
workflow.add_edge("depto_pos_obra", END)
workflow.add_edge("depto_backoffice", END)
workflow.add_edge("depto_consulta", END)

# Compila o grafo anexando a memória persistente
memoria = MemorySaver()
cerebro = workflow.compile(checkpointer=memoria)

if __name__ == "__main__":
    print("="*60)
    print(f"🧠 CÉREBRO CENTRAL {DADOS_EMPRESA['nome_fantasia'].upper()} (COM MEMÓRIA DE SESSÃO)")
    print("="*60)
    print("O sistema agora mantém o contexto da conversa ativa.")
    print("(Digite 'sair' para encerrar)\n")

    config_sessao = {"configurable": {"thread_id": "sessao-kr-diretor"}}
    historico = []

    while True:
        comando = input("\n👉 O que você precisa hoje? ").strip()
        if not comando:
            continue
        if comando.lower() in ["sair", "exit", "quit"]:
            print("Encerrando a sessão do Cérebro Central. Até logo!")
            break

        historico.append({"role": "user", "content": comando})
        
        resultado = cerebro.invoke({
            "entrada_usuario": comando,
            "categoria": "",
            "historico_conversa": historico,
            "resposta_final": ""
        }, config=config_sessao)
        
        resposta = resultado["resposta_final"]
        historico.append({"role": "assistant", "content": resposta})
        
        print("\n" + "="*60)
        print("RESPOSTA DO CÉREBRO CENTRAL:")
        print("="*60)
        print(resposta)
