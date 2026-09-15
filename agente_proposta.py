import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa o modelo Gemini configurado para rastrear no LangSmith
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.2,
)

# Prompt de Sistema estruturado para a KR Engenharia
SYSTEM_PROMPT = """Você é o Agente Técnico Especialista da KR Engenharia (KR Consultoria e Soluções em Engenharia LTDA).
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).
Especialidade: Sistemas de Potência (até 500 kV), Proteção e Seletividade (ETAP), Automação de Subestações (SAS / IEC 61850) e Comissionamento de Campo (TAF/TAC).

Sua missão é analisar dados de um lead/cliente industrial e produzir:
1. Diagnóstico preliminar e enquadramento da severidade do problema.
2. Escopo técnico recomendado dividido em fases (Estudos em Laboratório -> TAF -> TAC em Campo -> DataBook As-Built + ART).
3. Matriz de riscos operacionais preliminar.
4. Relação de documentos e arquivos técnicos a solicitar (unifilares, arquivos CID/ICD, dados de placa).
"""

def executar_analise_piloto(dados_cliente: str):
    mensagens = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=dados_cliente)
    ]
    
    print("⏳ Processando análise técnica com rastreamento no LangSmith...\n")
    resposta = llm.invoke(mensagens)
    # Garante a extração limpa do texto independentemente do formato de retorno
    if isinstance(resposta.content, list):
        return resposta.content[0].get('text', '')
    return resposta.content

if __name__ == "__main__":
    # Exemplo simulando dados recebidos de um cliente industrial
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
