import os
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA
from utils import get_llm, extrair_texto, salvar_markdown_saida

PROMPT_BACKOFFICE = f"""Você é o Especialista em Backoffice, Conformidade Regulatória (HSE) e Faturamento Técnico da {DADOS_EMPRESA['nome_fantasia']}.
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']}).

SUA MISSÃO:
Receber dados sobre mobilização de campo, instrumentos de teste ou faturamento de serviços da {DADOS_EMPRESA['nome_fantasia']} e estruturar o DOSSIÊ DE CONFORMIDADE E MEMÓRIA DE MEDIÇÃO.

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
   - Dados fiscais da {DADOS_EMPRESA['razao_social']} (ISSQN item 7.01 recolhido em {DADOS_EMPRESA['cidade']}).
"""

def processar_conformidade_backoffice(solicitacao_backoffice: str) -> str:
    """Gera dossiê de conformidade para mobilização de equipe e medição."""
    print("\n📋 [Agente de Backoffice] Auditando documentação de segurança, instrumentos e faturamento...")
    
    llm = get_llm(temperature=0.1)
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
    caminho_saida = salvar_markdown_saida("conformidade_backoffice.md", relatorio)
    
    print("\n" + "="*60)
    print(f"✅ DOSSIÊ DE CONFORMIDADE E MEDIÇÃO SALVO EM: {caminho_saida}")
    print("="*60 + "\n")
    print(relatorio)
