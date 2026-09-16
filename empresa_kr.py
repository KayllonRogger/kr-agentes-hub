import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

# Importa as inteligências especializadas de cada departamento
from grafo_agentes import (
    carregar_acervo_tecnico,
    agente_diagnostico,
    agente_operacoes,
    agente_comercial,
    EstadoProjeto
)
from agente_marketing import gerar_conteudo_linkedin
from agente_prospeccao import gerar_cadencia_prospeccao, gerar_link_busca_linkedin
from agente_inteligencia import analisar_especificacao_tecnica
from agente_pos_comissionamento import gerar_pacote_encerramento
from agente_backoffice import processar_conformidade_backoffice

ARQUIVO_TAREFAS = "tarefas_empresa.json"

# -------------------------------------------------------------
# DEFINIÇÃO DOS FUNCIONÁRIOS DA KR ENGENHARIA
# -------------------------------------------------------------
FUNCIONARIOS = {
    "LUCAS": {
        "nome": "Lucas Campos",
        "cargo": "Analista de Inteligência Comercial (SDR)",
        "especialidade": "Mapeamento de decisores em mineradoras/EPCistas e cadências de abordagem no LinkedIn.",
        "departamento": "Vendas & Prospecção"
    },
    "MARIANA": {
        "nome": "Mariana Esteves",
        "cargo": "Especialista em Marketing Técnico",
        "especialidade": "Produção de artigos técnicos e estudos de caso de autoridade para o LinkedIn B2B.",
        "departamento": "Marketing"
    },
    "RAFAEL": {
        "nome": "Eng. Rafael Gomes",
        "cargo": "Especialista em Proteção e Estudos Elétricos",
        "especialidade": "Análise de transitórios, funções ANSI (50/51, 51N, 51V) e modelagem no ETAP.",
        "departamento": "Engenharia de Proteção"
    },
    "CARLOS": {
        "nome": "Eng. Carlos Tenaglia",
        "cargo": "Coordenador de Comissionamento e Campo",
        "especialidade": "Planejamento executivo de TAF/TAC, ensaios com malas microprocessadas e NR-10/NR-35.",
        "departamento": "Comissionamento & Campo"
    },
    "BEATRIZ": {
        "nome": "Beatriz Silveira",
        "cargo": "Customer Success & Gestão Contratual",
        "especialidade": "Estruturação de DataBook As-Built, minutas de ART para o CREA-MG e retenção 30/90 dias.",
        "departamento": "Sucesso do Cliente"
    }
}

# -------------------------------------------------------------
# GERENCIAMENTO DE PERSISTÊNCIA DAS TAREFAS
# -------------------------------------------------------------
def carregar_tarefas() -> List[Dict]:
    if not os.path.exists(ARQUIVO_TAREFAS):
        return []
    try:
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_tarefas(tarefas: List[Dict]):
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(tarefas, f, indent=2, ensure_ascii=False)

def atribuir_tarefa(titulo: str, funcionario_id: str, instrucao: str) -> Dict:
    tarefas = carregar_tarefas()
    nova_tarefa = {
        "id": f"TASK-{int(time.time())}",
        "titulo": titulo,
        "funcionario_id": funcionario_id,
        "funcionario_nome": FUNCIONARIOS.get(funcionario_id, {}).get("nome", "Assistente"),
        "cargo": FUNCIONARIOS.get(funcionario_id, {}).get("cargo", ""),
        "instrucao": instrucao,
        "status": "PENDENTE",  # PENDENTE -> EM_EXECUCAO -> AGUARDANDO_APROVACAO -> CONCLUIDO
        "resultado": "",
        "data_criacao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "aprovado_por_diretor": False,
        "parecer_diretor": ""
    }
    tarefas.append(nova_tarefa)
    salvar_tarefas(tarefas)
    return nova_tarefa

# -------------------------------------------------------------
# EXECUÇÃO AUTÔNOMA DO FUNCIONÁRIO
# -------------------------------------------------------------
def executar_tarefa_funcionario(tarefa_id: str) -> Optional[Dict]:
    tarefas = carregar_tarefas()
    tarefa = next((t for t in tarefas if t["id"] == tarefa_id), None)
    if not tarefa:
        return None

    tarefa["status"] = "EM_EXECUCAO"
    salvar_tarefas(tarefas)

    fid = tarefa["funcionario_id"]
    instrucao = tarefa["instrucao"]
    resultado = ""

    print(f"\n⚙️ [{tarefa['funcionario_nome']}] Iniciando trabalho independente na tarefa '{tarefa['titulo']}'...")

    try:
        if fid == "LUCAS":
            # Lucas faz o mapeamento outbound e gera link do LinkedIn
            resultado = gerar_cadencia_prospeccao(instrucao)
            link = gerar_link_busca_linkedin(instrucao, "Gerente Manutenção Elétrica")
            resultado += f"\n\n---\n🔗 **Link de Busca Direta no LinkedIn Gerado:** [Abrir Decisores]({link})"

        elif fid == "MARIANA":
            # Mariana redige o artigo de autoridade técnica
            resultado = gerar_conteudo_linkedin(instrucao)

        elif fid == "RAFAEL":
            # Rafael realiza o diagnóstico técnico com base no acervo
            acervo = carregar_acervo_tecnico("acervo")
            estado_diag: EstadoProjeto = {
                "dados_cliente": instrucao,
                "base_conhecimento": acervo,
                "diagnostico_tecnico": "",
                "planejamento_operacional": "",
                "ajustes_do_engenheiro": "",
                "proposta_final": ""
            }
            res = agente_diagnostico(estado_diag)
            resultado = res["diagnostico_tecnico"]

        elif fid == "CARLOS":
            # Carlos planeja a estratégia de campo e ensaios
            acervo = carregar_acervo_tecnico("acervo")
            estado_campo: EstadoProjeto = {
                "dados_cliente": instrucao,
                "base_conhecimento": acervo,
                "diagnostico_tecnico": "Diagnóstico prévio aprovado pela engenharia.",
                "planejamento_operacional": "",
                "ajustes_do_engenheiro": "",
                "proposta_final": ""
            }
            res = agente_operacoes(estado_campo)
            resultado = res["planejamento_operacional"]

        elif fid == "BEATRIZ":
            # Beatriz organiza o DataBook e minuta de ART
            resultado = gerar_pacote_encerramento(instrucao)

        tarefa["resultado"] = resultado
        tarefa["status"] = "AGUARDANDO_APROVACAO"
        print(f"✅ [{tarefa['funcionario_nome']}] Tarefa concluída e colocada na Mesa do Diretor para aprovação!")

    except Exception as e:
        tarefa["status"] = "PENDENTE"
        tarefa["resultado"] = f"Erro na execução autônoma: {str(e)}"
        print(f"❌ Erro na execução de {tarefa['funcionario_nome']}: {e}")

    salvar_tarefas(tarefas)
    return tarefa

def aprovar_tarefa_diretor(tarefa_id: str, parecer: str = "Aprovado sem ressalvas.") -> bool:
    tarefas = carregar_tarefas()
    for t in tarefas:
        if t["id"] == tarefa_id:
            t["status"] = "CONCLUIDO"
            t["aprovado_por_diretor"] = True
            t["parecer_diretor"] = parecer
            salvar_tarefas(tarefas)
            return True
    return False

if __name__ == "__main__":
    print("="*60)
    print("🏢 SISTEMA DE FUNCIONÁRIOS AUTÔNOMOS - KR ENGENHARIA")
    print("="*60)
    
    # Exemplo: Atribui uma tarefa autônoma para a Mariana (Marketing)
    t = atribuir_tarefa(
        titulo="Redigir artigo sobre Seletividade Lógica IEC 61850",
        funcionario_id="MARIANA",
        instrucao="Abordar a mitigação de desligamentos em cascata utilizando mensagens GOOSE rápidas em subestações de 138kV."
    )
    print(f"📌 Nova tarefa criada: {t['id']} atribuída para {t['funcionario_nome']}")
    
    # Funcionário executa a tarefa sozinho
    executar_tarefa_funcionario(t["id"])
