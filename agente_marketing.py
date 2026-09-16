import os
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA
from utils import get_llm, extrair_texto, salvar_markdown_saida

PROMPT_SISTEMA_MARKETING = f"""Você é o Agente Especialista em Marketing de Conteúdo Técnico B2B da {DADOS_EMPRESA['nome_fantasia']}.
Sua missão é posicionar a {DADOS_EMPRESA['nome_fantasia']} e o {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']}) como a principal referência nacional (Boutique de Engenharia) em:
- Proteção e Seletividade de Sistemas de Potência (modelagem ETAP).
- Redes de Automação de Subestações SAS / IEC 61850 (mensagens GOOSE e relatórios MMS).
- Comissionamento de Campo e redução de downtime em até 40% com validação prévia em bancada.

PÚBLICO-ALVO:
Gerentes de Manutenção Elétrica, Coordenadores de Comissionamento, Gerentes de Projetos de EPCistas e Diretores de Operações de mineradoras e indústrias eletrointensivas.

ESTILO DO POST:
1. Tom: Estritamente técnico, executivo, sem clichês de autoajuda ou jargões vazios de marketing.
2. Estrutura do Post para LinkedIn:
   - Gancho Técnico: Um problema real que causa parada de planta (ex: saturação de TC, descoordenação de neutro, atraso de TAF/TAC).
   - O Case / Lição de Engenharia: Detalhe do método aplicado (normas IEEE/IEC, testes com mala microprocessada, simulação em bancada).
   - O Resultado Prático: Redução de máquina parada, energização segura e conformidade com normas.
   - Chamada para Ação (CTA): Convidar para conectar ou discutir diagnósticos técnicos para paradas programadas.
"""

def gerar_conteudo_linkedin(tema_ou_case: str) -> str:
    """Gera artigo técnico de autoridade voltado ao LinkedIn B2B."""
    print(f"\n📢 [Agente de Marketing] Estruturando artigo técnico para o LinkedIn...")
    
    llm = get_llm(temperature=0.4)
    resposta = llm.invoke([
        SystemMessage(content=PROMPT_SISTEMA_MARKETING),
        HumanMessage(content=f"Tema ou Estudo de Caso a explorar:\n{tema_ou_case}")
    ])
    
    return extrair_texto(resposta)

if __name__ == "__main__":
    case_exemplo = """
    Projeto: Subestação GIS 230/400 kV - Geração Eólica Offshore (Transição de Redes)
    Problema de Engenharia: Validação de lógicas de intertravamento complexas e comissionamento de relés de proteção multimarcas (C264, RET670, SIPROTEC) com prazos críticos de janela de energização.
    Diferencial KR Engenharia: Pré-validação em laboratório das lógicas e arquivos de configuração antes do envio a campo, eliminando surpresas na energização final.
    """

    print("==========================================================")
    print("🚀 GERADOR DE AUTORIDADE TÉCNICA - KR ENGENHARIA")
    print("==========================================================")
    
    post_gerado = gerar_conteudo_linkedin(case_exemplo)
    caminho_saida = salvar_markdown_saida("post_linkedin.md", post_gerado)
    
    print("\n" + "="*60)
    print(f"✅ POST TÉCNICO GERADO COM SUCESSO EM: {caminho_saida}")
    print("="*60 + "\n")
    print(post_gerado)
