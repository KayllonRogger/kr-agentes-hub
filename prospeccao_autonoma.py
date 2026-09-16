import os
import json
import time
import urllib.parse
from typing import List, Dict, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from config import DADOS_EMPRESA, CONTAS_FUNCIONARIOS
from utils import get_llm, extrair_texto
from documentos_kr import compilar_documentos_institucionais

ARQUIVO_CAMPANHAS = "campanhas_prospeccao.json"

# =====================================================================
# ICP - CATÁLOGO DE MERCADO DE GRANDES PLANTAS INDUSTRIAIS
# =====================================================================
CATALOGO_SETORES = {
    "MINERACAO": {
        "nome": "Mineração & Beneficiamento",
        "empresas": [
            {"nome": "Vale S.A. - Complexo Carajás", "dominio": "vale.com", "tensao": "230/13.8 kV", "foco": "Alimentadores de moagem e retrofits"},
            {"nome": "Samarco Mineração - Ubu & Germano", "dominio": "samarco.com", "tensao": "138/13.8 kV", "foco": "Reativação de plantas e relés digitais"},
            {"nome": "CSN Mineração - Casa de Pedra", "dominio": "csn.com.br", "tensao": "138/13.8 kV", "foco": "Seletividade de neutro e estudos ETAP"},
            {"nome": "Kinross Brasil - Mina Morro do Ouro", "dominio": "kinross.com", "tensao": "138/13.8 kV", "foco": "Confiabilidade e transitórios de partida"},
            {"nome": "Anglo American - Minas-Rio", "dominio": "angloamerican.com", "tensao": "230/13.8 kV", "foco": "Subestações de mineroduto e TAF/TAC"},
            {"nome": "Nexa Resources - Vazante / Juiz de Fora", "dominio": "nexaresources.com", "tensao": "138/13.8 kV", "foco": "Manutenção especializada e IEC 61850"}
        ]
    },
    "SIDERURGIA": {
        "nome": "Siderurgia & Metalurgia",
        "empresas": [
            {"nome": "Gerdau Aços Longos - Usina Ouro Branco", "dominio": "gerdau.com.br", "tensao": "230/13.8 kV", "foco": "Fornos elétricos a arco e relés SIPROTEC 5"},
            {"nome": "ArcelorMittal Tubarão / Monlevade", "dominio": "arcelormittal.com.br", "tensao": "230/13.8 kV", "foco": "Seletividade lógica e transitórios"},
            {"nome": "Usiminas - Usina de Ipatinga", "dominio": "usiminas.com", "tensao": "138/13.8 kV", "foco": "Retrofit de cubículos e parametrização SEL"},
            {"nome": "Aperam South America - Timóteo", "dominio": "aperam.com", "tensao": "138/13.8 kV", "foco": "Ensaios com mala microprocessada"},
            {"nome": "Albras - Alumínio Brasileiro", "dominio": "albras.net", "tensao": "230/13.8 kV", "foco": "Sistemas retificadores e subestações industriais"}
        ]
    },
    "ENERGIA": {
        "nome": "Energia & Transmissão / Renováveis",
        "empresas": [
            {"nome": "Eletrobras Furnas", "dominio": "eletrobras.com", "tensao": "500/230 kV", "foco": "Subestações de grande porte e IEC 61850"},
            {"nome": "Neoenergia - Parques Eólicos/Solares", "dominio": "neoenergia.com", "tensao": "230/34.5 kV", "foco": "Comissionamento TAC e TAF em bancada"},
            {"nome": "CPFL Renováveis", "dominio": "cpfl.com.br", "tensao": "138/34.5 kV", "foco": "Estudos de integração e proteções de interligação"},
            {"nome": "Engie Brasil Energia", "dominio": "engie.com", "tensao": "230/138 kV", "foco": "Ensaios de campo e relatórios de comissionamento"},
            {"nome": "Atlas Renewable Energy", "dominio": "atlasrenewableenergy.com", "tensao": "230/34.5 kV", "foco": "Subestações coletoras fotovoltaicas"}
        ]
    },
    "CELULOSE": {
        "nome": "Papel & Celulose",
        "empresas": [
            {"nome": "Suzano S.A. - Unidade Mucuri / Aracruz", "dominio": "suzano.com.br", "tensao": "230/13.8 kV", "foco": "Turbo-geradores industriais e ilhamento"},
            {"nome": "Klabin - Projeto Puma", "dominio": "klabin.com.br", "tensao": "230/13.8 kV", "foco": "Estudos de estabilidade e parametrização"},
            {"nome": "Cenibra - Celulose Nipo-Brasileira", "dominio": "cenibra.com.br", "tensao": "138/13.8 kV", "foco": "Paradas gerais de manutenção e seletividade"}
        ]
    },
    "EPCISTAS": {
        "nome": "Grandes EPCistas & Montagem Eletromecânica",
        "empresas": [
            {"nome": "Andrade Gutierrez Engenharia", "dominio": "andradegutierrez.com.br", "tensao": "500/230 kV", "foco": "Subcontratação especialista em TAF/TAC"},
            {"nome": "Construtora Barbosa Mello (CBM)", "dominio": "cbm.com.br", "tensao": "138/13.8 kV", "foco": "Comissionamento em infraestrutura e mineração"},
            {"nome": "MIP Engenharia", "dominio": "mip.com.br", "tensao": "138/13.8 kV", "foco": "Montagem eletromecânica industrial"},
            {"nome": "Tenenge / Novonor", "dominio": "tenenge.com.br", "tensao": "230/13.8 kV", "foco": "Projetos EPC de alta tensão"}
        ]
    }
}

# =====================================================================
# ENGRENAGENS DE MERCADO PARA DESCOBERTA NO LINKEDIN
# =====================================================================

def gerar_links_prospeccao(empresa: str, cargo: str = "Gerente Manutenção Elétrica") -> Dict[str, str]:
    """
    Gera as duas principais engrenagens de busca de decisores do mercado:
    1. LinkedIn Direct Search: busca direta de pessoas logadas.
    2. Google X-Ray Search: operador booleano avançado que indexa perfis públicos sem travas.
    """
    query_linkedin = urllib.parse.quote(f"{cargo} {empresa}")
    link_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query_linkedin}"

    # Google X-Ray Dorking: site:linkedin.com/in/ "Empresa" "Cargo"
    query_xray = urllib.parse.quote(f'site:linkedin.com/in/ "{empresa}" "{cargo}"')
    link_xray = f"https://www.google.com/search?q={query_xray}"

    return {
        "linkedin_direto": link_linkedin,
        "google_xray": link_xray
    }

def deduzir_padroes_email(dominio: str, primeiro_nome: str = "Nome", ultimo_nome: str = "Sobrenome") -> List[str]:
    """Gera os 3 padrões de e-mail corporativo mais comuns do mercado B2B brasileiro."""
    p = primeiro_nome.lower().strip()
    u = ultimo_nome.lower().strip()
    d = dominio.lower().strip()

    return [
        f"{p}.{u}@{d}",
        f"{p[0]}{u}@{d}",
        f"{p}_{u}@{d}"
    ]

# =====================================================================
# GERADOR DE ABORDAGENS HIPERPERSONALIZADAS (LUCAS CAMPOS)
# =====================================================================

PROMPT_LUCAS_OUTBOUND = """Você é Lucas Campos, Especialista em Inteligência Comercial e SDR da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).
Posicionamento da Empresa: Boutique Técnica de Alta Especialização em Sistemas de Potência, Seletividade (ETAP), Automação SAS / IEC 61850 e Comissionamento de Campo (TAF/TAC).

SUA MISSÃO:
Redigir uma abordagem B2B de alto valor para o e-mail de um decisor industrial (Gerente de Manutenção Elétrica ou Coordenador de Comissionamento) da empresa-alvo indicada.

DIRETRIZES DO E-MAIL:
1. Tom: De engenharia para engenharia. Extremamente respeitoso, sem bajulação, sem clichês de marketing genérico.
2. Parágrafo 1 - Contexto Técnico da Planta: Demonstre conhecimento sobre a operação da empresa-alvo (tensões, equipamentos críticos e os riscos operacionais como descoordenação de neutro, saturação de TCs ou janelas críticas de parada).
3. Parágrafo 2 - O Diferencial da KR Engenharia: Enfatize nossa metodologia de pré-validação em bancada (redução de até 40% de downtime) e cases de referência em grandes plantas (Baltic Power 400kV, Vale e Gerdau com Siemens SIPROTEC 5 e SEL).
4. Parágrafo 3 - Anexos & Chamada para Ação: Mencione que estamos anexando a Carta de Apresentação Institucional e o Portfólio de Serviços. Proponha uma conversa técnica rápida de 15 minutos na próxima semana.

ESTRUTURA DA RESPOSTA:
ASSUNTO: [Linha de assunto direta e técnica]
CORPO:
[Texto completo do e-mail pronto para envio, sem tags ou placeholders genéricos]
"""

def redigir_email_prospeccao(empresa_info: dict, especialidade_foco: str = "") -> Dict[str, str]:
    """Gera o assunto e corpo do e-mail hiperpersonalizado para a planta-alvo."""
    contexto = f"""
EMPRESA-ALVO: {empresa_info['nome']}
DOMÍNIO CORPORATIVO: {empresa_info.get('dominio', '')}
NÍVEL DE TENSÃO DA PLANTA: {empresa_info.get('tensao', 'Alta Tensão')}
FOCO OPERACIONAL TÍPICO: {empresa_info.get('foco', 'Confiabilidade Elétrica')}
ESPECIALIDADE ESPECÍFICA: {especialidade_foco if especialidade_foco else 'Estudos de Seletividade no ETAP e Comissionamento TAF/TAC'}
"""
    llm = get_llm(temperature=0.3)
    resp = llm.invoke([
        SystemMessage(content=PROMPT_LUCAS_OUTBOUND),
        HumanMessage(content=contexto)
    ])
    texto = extrair_texto(resp)

    # Separa Assunto e Corpo
    assunto = f"KR Engenharia | Confiabilidade em Sistemas de Potência — {empresa_info['nome']}"
    corpo = texto

    linhas = texto.split("\n")
    for idx, l in enumerate(linhas):
        if l.strip().upper().startswith("ASSUNTO:"):
            assunto = l.replace("ASSUNTO:", "").replace("Assunto:", "").strip()
            corpo = "\n".join(linhas[idx+1:]).strip()
            if corpo.upper().startswith("CORPO:"):
                corpo = corpo[6:].strip()
            break

    return {
        "assunto": assunto,
        "corpo": corpo
    }

# =====================================================================
# MOTOR DE CAMPANHAS AUTÔNOMAS
# =====================================================================

def carregar_fila_campanhas() -> List[Dict]:
    """Carrega as campanhas salvas no disco."""
    if not os.path.exists(ARQUIVO_CAMPANHAS):
        return []
    try:
        with open(ARQUIVO_CAMPANHAS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def salvar_fila_campanhas(campanhas: List[Dict]):
    """Salva a fila de campanhas no disco."""
    with open(ARQUIVO_CAMPANHAS, "w", encoding="utf-8") as f:
        json.dump(campanhas, f, indent=2, ensure_ascii=False)

def executar_varredura_setor(
    chave_setor: str = "MINERACAO",
    especialidade_foco: str = "Estudos de Proteção no ETAP e Comissionamento TAF/TAC",
    limite: int = 3
) -> List[Dict]:
    """
    Executa a prospecção autônoma do Lucas para um setor industrial.
    Mapeia as empresas, gera os links do LinkedIn e Google X-Ray, redige os e-mails e anexa o portfólio.
    """
    setor_dados = CATALOGO_SETORES.get(chave_setor, CATALOGO_SETORES["MINERACAO"])
    empresas_alvo = setor_dados["empresas"][:limite]
    
    # Garante que os documentos institucionais estão compilados
    docs = compilar_documentos_institucionais()
    anexos_oficiais = docs["anexos_padrao"]

    fila_atual = carregar_fila_campanhas()
    novos_leads = []

    print(f"\n🚀 [Lucas Campos] Iniciando varredura autônoma no setor: {setor_dados['nome']}...")

    for emp in empresas_alvo:
        nome_emp = emp["nome"]
        cargo_alvo = "Gerente de Manutenção Elétrica"
        print(f"   🔍 Mapeando oportunidades em: {nome_emp}...")

        links = gerar_links_prospeccao(nome_emp, cargo_alvo)
        padroes = deduzir_padroes_email(emp.get("dominio", "empresa.com.br"), "Decisor", "Manutencao")
        email_gerado = redigir_email_prospeccao(emp, especialidade_foco)

        lead = {
            "id": f"LEAD-{int(time.time())}-{len(fila_atual) + len(novos_leads) + 1}",
            "setor": setor_dados["nome"],
            "empresa": nome_emp,
            "dominio": emp.get("dominio", ""),
            "tensao": emp.get("tensao", ""),
            "cargo_alvo": cargo_alvo,
            "link_linkedin": links["linkedin_direto"],
            "link_xray": links["google_xray"],
            "padroes_email": padroes,
            "email_destinatario": f"contato@{emp.get('dominio', 'empresa.com.br')}",
            "assunto": email_gerado["assunto"],
            "corpo_email": email_gerado["corpo"],
            "anexos": anexos_oficiais,
            "status": "PRONTO_PARA_DISPARO", # PRONTO_PARA_DISPARO -> ENVIADO -> ERRO
            "data_criacao": time.strftime("%d/%m/%Y %H:%M"),
            "data_envio": None,
            "resultado_envio": ""
        }
        novos_leads.append(lead)

    fila_atual.extend(novos_leads)
    salvar_fila_campanhas(fila_atual)
    print(f"✅ [Lucas Campos] {len(novos_leads)} leads mapeados e estruturados com portfólio anexo!")
    return novos_leads

def atualizar_lead_campanha(lead_id: str, updates: dict) -> bool:
    """Atualiza campos específicos de um lead na fila de campanhas."""
    fila = carregar_fila_campanhas()
    atualizado = False
    for l in fila:
        if l.get("id") == lead_id:
            l.update(updates)
            atualizado = True
            break
    if atualizado:
        salvar_fila_campanhas(fila)
    return atualizado

def excluir_lead_campanha(lead_id: str) -> bool:
    """Remove um lead específico da fila de campanhas."""
    fila = carregar_fila_campanhas()
    nova_fila = [l for l in fila if l.get("id") != lead_id]
    if len(nova_fila) != len(fila):
        salvar_fila_campanhas(nova_fila)
        return True
    return False

def limpar_fila_campanhas() -> bool:
    """Limpa toda a fila de campanhas salvas."""
    salvar_fila_campanhas([])
    return True

if __name__ == "__main__":
    print("="*60)
    print("🎯 TESTE DO MOTOR DE PROSPECÇÃO AUTÔNOMA (LUCAS CAMPOS)")
    print("="*60)
    
    leads = executar_varredura_setor("MINERACAO", limite=2)
    for l in leads:
        print(f"\n🏢 Empresa: {l['empresa']}")
        print(f"   Decisor Alvo: {l['cargo_alvo']}")
        print(f"   🔗 LinkedIn Direct: {l['link_linkedin']}")
        print(f"   🔎 Google X-Ray: {l['link_xray']}")
        print(f"   📄 Assunto: {l['assunto']}")
        print(f"   📎 Anexos: {l['anexos']}")

