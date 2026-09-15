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

PROMPT_BACKOFFICE = """Você é o Especialista em Backoffice, Conformidade Regulatória (HSE) e Faturamento Técnico da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).

SUA MISSÃO:
Receber dados sobre mobilização de campo, instrumentos de teste ou faturamento de serviços da KR Engenharia e estruturar o DOSSIÊ DE CONFORMIDADE E MEMÓRIA DE MEDIÇÃO.

ESTRUTURA DA RESPOSTA:
1. DOSSIÊ DE HABILITAÇÃO DE CAMPO (NRs e SST):
   - Checklist de documentação obrigatória para liberação de entrada na planta (ASO com aptidão para SEP e Altura, certificados de NR-10 Básico, NR-10 SEP e NR-35 vigentes).
   - Relação de EPIs obrigatórios com CA válido (vestimenta contra arco elétrico Categoria II/IV, calçado de segurança dielétrico e óculos com proteção UV).
2. PLANILHA DE CONTROLE METROLÓGICO (RBC/INMETRO):
   - Relação dos instrumentos alocados (mala microprocessada Omicron/Conprove, megômetro 10kV, microhmímetro 100A).
   - Requisitos de validade do certificado de calibração rastreável à RBC (padrão de até 18 meses).
3. MEMÓRIA DE CÁLCULO E BOLETIM DE MEDIÇÃO DE SERVIÇOS (BMS):
   - Estruturação do faturamento por marco de entrega ou horas trabalhadas (HN, HE com adicionais de 50%/100% conforme CLT).
   - Prestação de contas de despesas reembolsáveis via nota de débito acrescida da taxa de administração/BDI de 15%.
   - Dados fiscais da KR Consultoria e Soluções em Engenharia LTDA (ISSQN item 7.01 recolhido em Belo Horizonte/MG).
"""

def processar_conformidade_backoffice(solicitacao_backoffice: str) -> str:
    print("\n📋 [Agente de Backoffice] Auditando documentação de segurança, instrumentos e faturamento...")
    
    resp = llm.invoke([
        SystemMessage(content=PROMPT_BACKOFFICE),
        HumanMessage(content=f"DADOS DA OPERAÇÃO / MEDIÇÃO:\n{solicitacao_backoffice}")
    ])
    
    return extrair_texto(resp)

if __name__ == "__main__":
    exemplo_mobilizacao = """
    Cliente: Mina de Ferro - Vale S.A.
    Demanda: Mobilização de 2 especialistas de comissionamento da KR Engenharia para testes de injeção secundária em 6 painéis de 13,8 kV no próximo final de semana.
    Instrumentos Utilizados: 1 Mala de Testes Microprocessada Conprove CE-6006 e 1 Megômetro Digital 10kV.
    Faturamento: Liberação da 2ª parcela contratual (40% referente à conclusão dos ensaios de campo) + reembolso de R$ 3.850,00 de despesas de viagem (hospedagem, combustível e alimentação).
    """

    print("==========================================================")
    print("🚀 GESTÃO DE CONFORMIDADE E BACKOFFICE - KR ENGENHARIA")
    print("==========================================================")
    
    relatorio = processar_conformidade_backoffice(exemplo_mobilizacao)
    
    os.makedirs("output", exist_ok=True)
    caminho_saida = "output/conformidade_backoffice.md"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(relatorio)
        
    print("\n" + "="*60)
    print(f"✅ DOSSIÊ DE CONFORMIDADE E MEDIÇÃO SALVO EM: {caminho_saida}")
    print("="*60 + "\n")
    print(relatorio)
