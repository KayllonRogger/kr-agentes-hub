import os
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA, eh_empresa_bloqueada
from utils import get_llm, extrair_texto, gerar_link_busca_linkedin, salvar_markdown_saida

PROMPT_PROSPECCAO_1CLIQUE = f"""Você é o Especialista em Inteligência Comercial e Prospecção B2B da {DADOS_EMPRESA['nome_fantasia']}.
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']}).
Posicionamento: {DADOS_EMPRESA['posicionamento']}.

SUA MISSÃO:
Receber o nome de uma empresa-alvo e a especialidade desejada, e estruturar uma abordagem técnica de alto impacto pronta para envio no LinkedIn.

ESTRUTURA OBRIGATÓRIA DA RESPOSTA:
1. DECISOR RECOMENDADO:
   - Cargo ideal exato (ex: Gerente de Manutenção Elétrica, Coordenador de Comissionamento ou Gerente de Engenharia).

2. NOTA DE CONEXÃO NO LINKEDIN (MÁXIMO 280 CARACTERES):
   - Mensagem ultracurta para o convite de conexão (limite de 300 caracteres do LinkedIn). Direta, sem bajulação, focada em conexão técnica entre especialistas.

3. MENSAGEM PRINCIPAL DE ABORDAGEM (INMAIL OU E-MAIL CORPORATIVO):
   - Parágrafo 1: O gargalo operacional comum (ex: desligamentos indevidos por descoordenação, validação de intertravamentos GOOSE, prazos críticos de parada).
   - Parágrafo 2: O diferencial da KR Engenharia (pré-validação em bancada para redução de downtime em até 40% e vivência em projetos de grande porte como Baltic Power 400kV e retrofits na Vale/Gerdau).
   - Parágrafo 3: Proposta de conversa rápida de 15 minutos ou envio do diagrama unifilar para diagnóstico preliminar.
"""

def gerar_cadencia_prospeccao(perfil_empresa: str, especialidade: str = "") -> str:
    """Gera plano de abordagem de prospecção B2B personalizado."""
    if eh_empresa_bloqueada(perfil_empresa):
        return (
            "ℹ️ **[DOMÍNIO RESTRITO]**\n\n"
            "O domínio **sma-eng.com.br** está configurado para não ser prospectado como lead pelo Lucas."
        )

    print(f"\n🎯 [Agente de Prospecção] Mapeando abordagem para {perfil_empresa}...")
    
    contexto = f"EMPRESA-ALVO: {perfil_empresa}\n"
    if especialidade:
        contexto += f"SERVIÇO / DISCIPLINA EM FOCO: {especialidade}\n"
        
    llm = get_llm(temperature=0.3)
    resp = llm.invoke([
        SystemMessage(content=PROMPT_PROSPECCAO_1CLIQUE),
        HumanMessage(content=contexto)
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
    empresa = "Gerdau Aços Longos - Usina Ouro Branco"
    servico = "Estudos de Coordenação no ETAP e Parametrização de Relés SIPROTEC 5"
    
    print("==========================================================")
    print("🚀 PROSPECÇÃO B2B 1-CLIQUE - KR ENGENHARIA")
    print("==========================================================")
    
    resultado = gerar_cadencia_prospeccao(empresa, servico)
    link = gerar_link_busca_linkedin("Gerdau", "Gerente Manutenção Elétrica")
    salvar_markdown_saida("cadencia_prospeccao.md", resultado)
    
    print(resultado)
    print(f"\n🔗 Link de Busca Direto: {link}")
