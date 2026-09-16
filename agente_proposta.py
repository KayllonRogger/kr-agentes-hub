import os
from langchain_core.messages import SystemMessage, HumanMessage
from config import DADOS_EMPRESA
from utils import get_llm, extrair_texto

SYSTEM_PROMPT = f"""Você é o Agente Técnico Especialista da {DADOS_EMPRESA['nome_fantasia']} ({DADOS_EMPRESA['razao_social']}).
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']}).
Especialidade: {DADOS_EMPRESA['especialidades']}.

Sua missão é analisar dados de um lead/cliente industrial e produzir:
1. Diagnóstico preliminar e enquadramento da severidade do problema.
2. Escopo técnico recomendado dividido em fases (Estudos em Laboratório -> TAF -> TAC em Campo -> DataBook As-Built + ART).
3. Matriz de riscos operacionais preliminar.
4. Relação de documentos e arquivos técnicos a solicitar (unifilares, arquivos CID/ICD, dados de placa).
"""

def executar_analise_piloto(dados_cliente: str) -> str:
    """Executa a análise técnica inicial de um lead industrial."""
    mensagens = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=dados_cliente)
    ]
    
    print("⏳ Processando análise técnica com rastreamento...\n")
    llm = get_llm(temperature=0.2)
    resposta = llm.invoke(mensagens)
    return extrair_texto(resposta)

if __name__ == "__main__":
    caso_exemplo = """
    Cliente: Mineração Vale do Aço
    Tensão: Subestação 13,8 kV / 230 kV
    Problema: Ocorrência de desligamentos em cascata no alimentador principal de moagem durante a partida de grandes motores. 
    Equipamentos: Relés SEL-751 e Siemens SIPROTEC 5.
    Necessidade: Estudo de coordenação/seletividade urgente e validação de parametrizações antes da próxima parada de manutenção de 24h.
    """
    
    resultado = executar_analise_piloto(caso_exemplo)
    print("=== RESULTADO DA PRÉ-PROPOSTA KR ENGENHARIA ===\n")
    print(resultado)
