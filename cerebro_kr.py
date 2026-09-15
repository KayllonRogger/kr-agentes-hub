import os
import sys
from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Importa todos os departamentos especializados
from grafo_agentes import (
    carregar_acervo_tecnico,
    agente_diagnostico,
    agente_operacoes,
    agente_comercial,
    EstadoProjeto
)
from agente_marketing import gerar_conteudo_linkedin
from agente_prospeccao import gerar_cadencia_prospeccao
from agente_inteligencia import analisar_especificacao_tecnica
from agente_pos_comissionamento import gerar_pacote_encerramento
from agente_backoffice import processar_conformidade_backoffice
from gerar_documento import renderizar_proposta

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

# 3. Estado do Cérebro Central com Histórico de Memória
class EstadoCerebro(TypedDict):
    entrada_usuario: str
    categoria: str
    historico_conversa: list[dict]
    resposta_final: str

# 4. Nó Supervisor com Memória Contextual
def supervisor_triagem(estado: EstadoCerebro):
    print("\n🧠 [Cérebro Central] Analisando mensagem considerando o histórico recente...")
    
    # Monta resumo do histórico recente para contextualizar follow-ups
    historico_texto = ""
    for msg in estado.get("historico_conversa", [])[-4:]:
        papel = "Usuário" if msg["role"] == "user" else "Assistente"
        historico_texto += f"{papel}: {msg['content'][:200]}...\n"

    prompt = f"""Você é o Cérebro Central de Operações da KR Engenharia.
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

# 5. Nós dos Departamentos

def departamento_propostas(estado: EstadoCerebro):
    print("\n🏢 -> Ativando DEPARTAMENTO DE ENGENHARIA E PROPOSTAS...")
    acervo = carregar_acervo_tecnico("acervo")
    estado_projeto: EstadoProjeto = {
        "dados_cliente": estado["entrada_usuario"],
        "base_conhecimento": acervo,
        "diagnostico_tecnico": "",
        "planejamento_operacional": "",
        "ajustes_do_engenheiro": "Condições comerciais padrão da KR Engenharia com ART inclusa.",
        "proposta_final": ""
    }
    r_diag = agente_diagnostico(estado_projeto)
    estado_projeto["diagnostico_tecnico"] = r_diag["diagnostico_tecnico"]
    r_ops = agente_operacoes(estado_projeto)
    estado_projeto["planejamento_operacional"] = r_ops["planejamento_operacional"]
    r_com = agente_comercial(estado_projeto)
    
    os.makedirs("output", exist_ok=True)
    with open("output/proposta_gerada.md", "w", encoding="utf-8") as f:
        f.write(r_com["proposta_final"])
        
    renderizar_proposta()
    return {"resposta_final": "Proposta Técnica e Documento Executivo gerados com sucesso na pasta 'output/'."}

def departamento_marketing(estado: EstadoCerebro):
    print("\n📢 -> Ativando DEPARTAMENTO DE MARKETING...")
    post = gerar_conteudo_linkedin(estado["entrada_usuario"])
    os.makedirs("output", exist_ok=True)
    with open("output/post_linkedin.md", "w", encoding="utf-8") as f:
        f.write(post)
    return {"resposta_final": f"Artigo para o LinkedIn salvo em 'output/post_linkedin.md'.\n\nResumo:\n{post[:300]}..."}

def departamento_prospeccao(estado: EstadoCerebro):
    print("\n🎯 -> Ativando DEPARTAMENTO DE PROSPECÇÃO B2B...")
    cadencia = gerar_cadencia_prospeccao(estado["entrada_usuario"])
    os.makedirs("output", exist_ok=True)
    with open("output/cadencia_prospeccao.md", "w", encoding="utf-8") as f:
        f.write(cadencia)
    return {"resposta_final": f"Plano de abordagem salvo em 'output/cadencia_prospeccao.md'.\n\nResumo:\n{cadencia[:300]}..."}

def departamento_edital(estado: EstadoCerebro):
    print("\n🔍 -> Ativando DEPARTAMENTO DE AUDITORIA DE EDITAIS...")
    relatorio = analisar_especificacao_tecnica(estado["entrada_usuario"])
    os.makedirs("output", exist_ok=True)
    with open("output/analise_edital.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
    return {"resposta_final": f"Auditoria salva em 'output/analise_edital.md'.\n\nResumo:\n{relatorio[:300]}..."}

def departamento_pos_obra(estado: EstadoCerebro):
    print("\n📦 -> Ativando DEPARTAMENTO DE SUCESSO DO CLIENTE...")
    pacote = gerar_pacote_encerramento(estado["entrada_usuario"])
    os.makedirs("output", exist_ok=True)
    with open("output/plano_pos_comissionamento.md", "w", encoding="utf-8") as f:
        f.write(pacote)
    return {"resposta_final": f"DataBook e ART salvos em 'output/plano_pos_comissionamento.md'.\n\nResumo:\n{pacote[:300]}..."}

def departamento_backoffice(estado: EstadoCerebro):
    print("\n📋 -> Ativando DEPARTAMENTO DE BACKOFFICE E CONFORMIDADE...")
    relatorio = processar_conformidade_backoffice(estado["entrada_usuario"])
    os.makedirs("output", exist_ok=True)
    with open("output/conformidade_backoffice.md", "w", encoding="utf-8") as f:
        f.write(relatorio)
    return {"resposta_final": f"Dossiê salvo em 'output/conformidade_backoffice.md'.\n\nResumo:\n{relatorio[:300]}..."}

def departamento_consulta(estado: EstadoCerebro):
    print("\n💡 -> Ativando CONSULTORIA TÉCNICA DIRETA...")
    prompt = """Você é o Consultor Técnico Especialista da KR Engenharia.
Responda com base no rigor normativo (IEEE, IEC 61850, ABNT) e considere o histórico anterior se for uma continuação de pergunta."""
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=estado["entrada_usuario"])
    ])
    return {"resposta_final": extrair_texto(resp)}

# 6. Grafo com Checkpointer de Memória (MemorySaver)
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
    return rotas.get(estado["categoria"], "depto_consulta")

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

# 7. Execução Interativa no Terminal com Memória Contínua
if __name__ == "__main__":
    print("="*60)
    print("🧠 CÉREBRO CENTRAL KR ENGENHARIA (COM MEMÓRIA DE SESSÃO)")
    print("="*60)
    print("O sistema agora mantém o contexto da conversa ativa.")
    print("(Digite 'sair' para encerrar)\n")

    # Configuração da sessão ativa de memória
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
