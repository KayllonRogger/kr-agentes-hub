import os
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA
from utils import get_llm, extrair_texto, salvar_markdown_saida, carregar_acervo_tecnico

PROMPT_INTELIGENCIA = f"""Você é o Engenheiro Especialista em Inteligência Regulatória e Análise de Editais da {DADOS_EMPRESA['nome_fantasia']}.
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']}).

DIRETRIZES E LIMITES DE ESCOPO DA {DADOS_EMPRESA['nome_fantasia'].upper()}:
{{acervo}}

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
    """Cruza o edital/TR do cliente com as diretrizes e limites de escopo do acervo técnico."""
    print("\n🔍 [Agente de Inteligência] Cruzando especificação do cliente com limites de escopo da KR...")
    acervo = carregar_acervo_tecnico("acervo")
    prompt = PROMPT_INTELIGENCIA.format(acervo=acervo)
    
    llm = get_llm(temperature=0.1)
    resp = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"ESPECIFICAÇÃO TÉCNICA / TERMO DE REFERÊNCIA DO CLIENTE:\n\n{texto_especificacao}")
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
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
    caminho_saida = salvar_markdown_saida("analise_edital.md", relatorio)
    
    print("\n" + "="*60)
    print(f"✅ ANÁLISE DE CONFORMIDADE E DESVIOS SALVA EM: {caminho_saida}")
    print("="*60 + "\n")
    print(relatorio)
