import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# 1. Carrega configurações do .env
load_dotenv()

# 2. Inicializa o modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
)

def extrair_texto(resposta) -> str:
    if isinstance(resposta.content, list):
        return resposta.content[0].get('text', '')
    return str(resposta.content)

PROMPT_PROSPECCAO = """Você é o Especialista em Inteligência Comercial e Prospecção B2B da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).
Posicionamento: Boutique Técnica de Engenharia em Sistemas de Potência, Proteção (ETAP), Automação de Subestações (SAS / IEC 61850) e Comissionamento (TAF/TAC).

SUA MISSÃO:
Criar uma estratégia de abordagem outbound altamente personalizada para uma empresa-alvo, falando a linguagem de engenheiro para engenheiro (zero clichês de vendas corporativas).

ESTRUTURA DA RESPOSTA:
1. MAPEAMENTO DO DECISOR: Cargo ideal a abordar na empresa (ex.: Gerente de Manutenção, Coordenador de Comissionamento, Gerente de Engenharia).
2. O GARGALO TÉCNICO: Qual a principal dor desse decisor que a KR Engenharia resolve (ex.: risco de estouro de janela de parada, falta de braço técnico para estudos no ETAP, erros de parametrização em campo).
3. CADÊNCIA DE CONTATO (3 ETAPAS):
   - Mensagem 1 (LinkedIn - Quebra-gelo Técnico): Apresentação focada em desafios técnicos comuns do segmento dele.
   - Mensagem 2 (E-mail - Prova Técnica): Citação de case real relevante da KR Engenharia (ex: projetos offshore de 400 kV ou retrofits industriais em 230 kV).
   - Mensagem 3 (Follow-up de Diagnóstico): Proposta de reunião rápida de 15 minutos para avaliar o diagrama unifilar ou a próxima janela de parada da planta.
"""

def gerar_cadencia_prospeccao(perfil_empresa: str) -> str:
    print(f"\n🎯 [Agente de Prospecção] Mapeando decisores e gerando cadência técnica...")
    
    resp = llm.invoke([
        SystemMessage(content=PROMPT_PROSPECCAO),
        HumanMessage(content=f"Empresa ou Segmento Alvo:\n{perfil_empresa}")
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
    exemplo_alvo = """
    Segmento: Grandes EPCistas e Integradores de Infraestrutura de Energia
    Alvo Típico: Empresas que executam obras de subestações de 138/230 kV para linhas de transmissão ou conexão de parques renováveis.
    Objetivo da Abordagem: Apresentar a KR Engenharia como braço técnico externo especialista para estudos de seletividade no ETAP e validação de redes IEC 61850 em fábrica (TAF).
    """

    print("==========================================================")
    print("🚀 GERADOR DE CADÊNCIA OUTBOUND B2B - KR ENGENHARIA")
    print("==========================================================")
    
    cadencia = gerar_cadencia_prospeccao(exemplo_alvo)
    
    os.makedirs("output", exist_ok=True)
    caminho_saida = "output/cadencia_prospeccao.md"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(cadencia)
        
    print("\n" + "="*60)
    print(f"✅ ESTRATÉGIA DE PROSPECÇÃO GERADA EM: {caminho_saida}")
    print("="*60 + "\n")
    print(cadencia)
