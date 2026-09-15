import os
import sys
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Carrega variáveis de ambiente
load_dotenv()

# 2. Inicializa o modelo otimizado para subagentes
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
)

def extrair_texto(resposta) -> str:
    if isinstance(resposta.content, list):
        return resposta.content[0].get('text', '')
    return str(resposta.content)

# 3. Prompt Especialista em Marketing Técnico B2B (Engenharia Elétrica de Potência)
PROMPT_SISTEMA_MARKETING = """Você é o Agente Especialista em Marketing de Conteúdo Técnico B2B da KR Engenharia.
Sua missão é posicionar a KR Engenharia e o Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2) como a principal referência nacional (Boutique de Engenharia) em:
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
    print(f"\n📢 [Agente de Marketing] Estruturando artigo técnico para o LinkedIn...")
    
    resposta = llm.invoke([
        SystemMessage(content=PROMPT_SISTEMA_MARKETING),
        HumanMessage(content=f"Tema ou Estudo de Caso a explorar:\n{tema_ou_case}")
    ])
    
    return extrair_texto(resposta)

if __name__ == "__main__":
    # Exemplo extraído do acervo real de projetos da KR Engenharia
    case_exemplo = """
    Projeto: Subestação GIS 230/400 kV - Geração Eólica Offshore (Transição de Redes)
    Problema de Engenharia: Validação de lógicas de intertravamento complexas e comissionamento de relés de proteção multimarcas (C264, RET670, SIPROTEC) com prazos críticos de janela de energização.
    Diferencial KR Engenharia: Pré-validação em laboratório das lógicas e arquivos de configuração antes do envio a campo, eliminando surpresas na energização final.
    """

    print("==========================================================")
    print("🚀 GERADOR DE AUTORIDADE TÉCNICA - KR ENGENHARIA")
    print("==========================================================")
    
    post_gerado = gerar_conteudo_linkedin(case_exemplo)
    
    # Salva o post gerado na pasta output/
    os.makedirs("output", exist_ok=True)
    caminho_saida = "output/post_linkedin.md"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(post_gerado)
        
    print("\n" + "="*60)
    print(f"✅ POST TÉCNICO GERADO COM SUCESSO EM: {caminho_saida}")
    print("="*60 + "\n")
    print(post_gerado)
