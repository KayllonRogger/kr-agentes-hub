import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

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

PROMPT_POS_COMISSIONAMENTO = """Você é o Especialista em Sucesso do Cliente, Garantia de Qualidade e Pós-Comissionamento da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).

SUA MISSÃO:
Receber os dados de uma obra, estudo ou comissionamento recém-finalizado e estruturar o pacote formal de encerramento técnico e retenção comercial da KR Engenharia.

ESTRUTURA DA RESPOSTA:
1. ESTRUTURAÇÃO DO DATABOOK AS-BUILT:
   - Índice formal de pastas e documentos definitivos para entrega à fiscalização do cliente (relatórios de injeção secundária, diagramas unifilares em DWG/PDF, arquivos de parametrização finais de relés SEL/Siemens/Schneider e certificados RBC de calibração das malas).
2. MINUTA DE REGISTRO DA ART (CREA-MG):
   - Descrição técnica recomendada para o preenchimento da ART perante o CREA-MG, delimitando com rigor a responsabilidade técnica do Eng. Kayllon sobre as atividades executadas.
3. PROTOCOLO DE CHECK-IN TÉCNICO (30 E 90 DIAS):
   - Mensagem de acompanhamento pós-energização para enviar ao Gerente de Manutenção do cliente.
   - Questionamento técnico sobre eventos de oscilografia, comportamento térmico dos transformadores/motores e proposta de avaliação de novas demandas para contratação de contrato guarda-chuva.
"""

def gerar_pacote_encerramento(dados_projeto: str) -> str:
    print("\n📦 [Agente de Sucesso do Cliente] Gerando DataBook, minuta de ART e protocolo pós-entrega...")
    
    resp = llm.invoke([
        SystemMessage(content=PROMPT_POS_COMISSIONAMENTO),
        HumanMessage(content=f"PROJETO CONCLUÍDO:\n{dados_projeto}")
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
    exemplo_conclusao = """
    Cliente: Siderúrgica Gerdau Aços Longos
    Serviço Executado: Revisão e parametrização das funções de proteção de sobrecorrente de neutro (51N) e inrush em transformadores de 13,8/0,48 kV da laminação.
    Equipamentos: Relés Siemens SIPROTEC 5 e Schneider Easergy P5.
    Status: Energização concluída com sucesso no último final de semana com acompanhamento da primeira partida.
    """

    print("==========================================================")
    print("🚀 GESTOR DE ENCERRAMENTO E PÓS-COMISSIONAMENTO - KR ENGENHARIA")
    print("==========================================================")
    
    pacote = gerar_pacote_encerramento(exemplo_conclusao)
    
    os.makedirs("output", exist_ok=True)
    caminho_saida = "output/plano_pos_comissionamento.md"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(pacote)
        
    print("\n" + "="*60)
    print(f"✅ PACOTE DE ENCERRAMENTO E ART SALVO EM: {caminho_saida}")
    print("="*60 + "\n")
    print(pacote)
