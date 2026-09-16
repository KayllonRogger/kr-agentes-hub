import os
import json
import time
import urllib.parse
from typing import List, Dict, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from config import DADOS_EMPRESA, CONTAS_FUNCIONARIOS
from utils import get_llm, extrair_texto
from documentos_kr import compilar_documentos_institucionais
from servico_lusha import consultar_contato_lusha, consultar_empresa_lusha, enriquecer_lead_com_lusha

ARQUIVO_CAMPANHAS = "campanhas_prospeccao.json"

# =====================================================================
# ICP - CATÁLOGO DE MERCADO DE GRANDES PLANTAS INDUSTRIAIS
# =====================================================================
# =====================================================================
# ICP - CATÁLOGO DE MERCADO DE GRANDES PLANTAS INDUSTRIAIS
# Foco estrito: Área de Gerenciamento Elétrico & Sistemas de Potência
# =====================================================================
CATALOGO_SETORES = {
    "MINERACAO": {
        "nome": "Mineração & Beneficiamento",
        "empresas": [
            {
                "nome": "Vale S.A. - Complexo Carajás",
                "dominio": "vale.com",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "foco": "Alimentadores de moagem, seletividade de neutro e retrofits de relés"
            },
            {
                "nome": "Samarco Mineração - Complexos Ubu & Germano",
                "dominio": "samarco.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia e Manutenção Elétrica",
                "foco": "Reativação de subestações de alta tensão e parametrização de IEDs"
            },
            {
                "nome": "CSN Mineração - Casa de Pedra",
                "dominio": "csn.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "foco": "Coordenação e seletividade no ETAP e proteção de alimentadores"
            },
            {
                "nome": "Kinross Brasil - Mina Morro do Ouro",
                "dominio": "kinross.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "foco": "Confiabilidade de subestações e mitigação de transitórios de partida"
            },
            {
                "nome": "Anglo American - Minas-Rio",
                "dominio": "angloamerican.com",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Coordenador de Engenharia Elétrica & Subestações",
                "foco": "Subestações de mineroduto e testes TAF/TAC em bancada"
            },
            {
                "nome": "Nexa Resources - Vazante / Juiz de Fora",
                "dominio": "nexaresources.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica e Automação",
                "foco": "Ensaios secundários e automação IEC 61850"
            }
        ]
    },
    "SIDERURGIA": {
        "nome": "Siderurgia & Metalurgia",
        "empresas": [
            {
                "nome": "Gerdau Aços Longos - Usina Ouro Branco",
                "dominio": "gerdau.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "foco": "Fornos elétricos a arco, lógicas GOOSE e relés SIPROTEC 5"
            },
            {
                "nome": "ArcelorMittal Tubarão / Monlevade",
                "dominio": "arcelormittal.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica e Automação",
                "foco": "Seletividade lógica, estudos de transitórios e cubículos de média tensão"
            },
            {
                "nome": "Usiminas - Usina de Ipatinga",
                "dominio": "usiminas.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "foco": "Retrofit de cubículos e parametrização avançada de relés SEL"
            },
            {
                "nome": "Aperam South America - Timóteo",
                "dominio": "aperam.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "foco": "Comissionamento TAC e ensaios com mala microprocessada calibrada RBC"
            },
            {
                "nome": "Albras - Alumínio Brasileiro",
                "dominio": "albras.net",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica & Subestações",
                "foco": "Sistemas retificadores de grande porte e proteção de subestações"
            }
        ]
    },
    "ENERGIA": {
        "nome": "Energia & Transmissão / Renováveis",
        "empresas": [
            {
                "nome": "Eletrobras Furnas",
                "dominio": "eletrobras.com",
                "tensao": "500/230 kV",
                "cargo_alvo": "Gerente de Engenharia e Manutenção de Subestações",
                "foco": "Automação SAS / IEC 61850 e ensaios em relés de alta tensão"
            },
            {
                "nome": "Neoenergia - Parques Eólicos/Solares",
                "dominio": "neoenergia.com",
                "tensao": "230/34.5 kV",
                "cargo_alvo": "Coordenador de Comissionamento Elétrico",
                "foco": "Validação de bancada TAF/TAC e parametrização de proteção de interligação"
            },
            {
                "nome": "CPFL Renováveis",
                "dominio": "cpfl.com.br",
                "tensao": "138/34.5 kV",
                "cargo_alvo": "Gerente de Operação e Manutenção Elétrica",
                "foco": "Estudos de integração ao ONS e testes de seletividade"
            },
            {
                "nome": "Engie Brasil Energia",
                "dominio": "engie.com",
                "tensao": "230/138 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica & Proteção",
                "foco": "Ensaios secundários e relatórios técnicos com emissão de ART"
            },
            {
                "nome": "Atlas Renewable Energy",
                "dominio": "atlasrenewableenergy.com",
                "tensao": "230/34.5 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "foco": "Subestações coletoras fotovoltaicas e parametrização multimarca"
            }
        ]
    },
    "CELULOSE": {
        "nome": "Papel & Celulose",
        "empresas": [
            {
                "nome": "Suzano S.A. - Unidade Mucuri / Aracruz",
                "dominio": "suzano.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica e Automação",
                "foco": "Turbo-geradores industriais, lógica de ilhamento e estudos ETAP"
            },
            {
                "nome": "Klabin - Projeto Puma",
                "dominio": "klabin.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "foco": "Estabilidade de sistemas industriais e parametrização de IEDs"
            },
            {
                "nome": "Cenibra - Celulose Nipo-Brasileira",
                "dominio": "cenibra.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "foco": "Janelas críticas de parada geral de manutenção e testes de relés"
            }
        ]
    },
    "EPCISTAS": {
        "nome": "Grandes EPCistas & Montagem Eletromecânica",
        "empresas": [
            {
                "nome": "Andrade Gutierrez Engenharia",
                "dominio": "andradegutierrez.com.br",
                "tensao": "500/230 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica e Comissionamento",
                "foco": "Subcontratação especialista em TAF/TAC e subestações turn-key"
            },
            {
                "nome": "Construtora Barbosa Mello (CBM)",
                "dominio": "cbm.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Comissionamento Elétrico",
                "foco": "Montagem eletromecânica e energização de plantas industriais"
            },
            {
                "nome": "MIP Engenharia",
                "dominio": "mip.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "foco": "Montagem eletromecânica industrial e testes de aceitação em campo"
            },
            {
                "nome": "Tenenge / Novonor",
                "dominio": "tenenge.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Comissionamento Eletromecânico",
                "foco": "Projetos EPC de alta tensão e comissionamento especializado"
            }
        ]
    }
}

# =====================================================================
# ENGRENAGENS DE MERCADO PARA DESCOBERTA DE CONTATOS REAIS (LUSHA + LINKEDIN)
# =====================================================================

def gerar_links_prospeccao(empresa: str, cargo: str = "Gerente de Manutenção Elétrica") -> Dict[str, str]:
    """
    Gera engrenagens de busca de alta precisão para localização de contatos reais:
    1. Lusha B2B Prospector: Busca no diretório Lusha por e-mails e telefones diretos do gestor elétrico.
    2. LinkedIn Direct Search: Busca de pessoas logadas focada estritamente na gestão elétrica.
    3. Google X-Ray Search: Operador booleano avançado (dork) que indexa perfis públicos sem travas.
    4. RocketReach Search: Consulta complementar de contatos corporativos verificados.
    """
    nome_limpo = empresa.split(" - ")[0].strip()

    # 1. Lusha Prospecting Search (e-mails diretos e telefones de decisores de gestão elétrica)
    query_lusha = urllib.parse.quote(f'site:lusha.com "{nome_limpo}" ("{cargo}" OR "Manutenção Elétrica" OR "Engenharia Elétrica" OR "Electrical Manager")')
    link_lusha = f"https://www.google.com/search?q={query_lusha}"

    # 2. LinkedIn Direct Search (gestão elétrica na empresa)
    query_linkedin = urllib.parse.quote(f'("{cargo}") "{nome_limpo}"')
    link_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query_linkedin}"

    # 3. Google X-Ray Search (LinkedIn Dorking)
    query_xray = urllib.parse.quote(f'site:linkedin.com/in/ ("{cargo}" OR "Gerente de Engenharia Elétrica" OR "Coordenador de Manutenção Elétrica") "{nome_limpo}"')
    link_xray = f"https://www.google.com/search?q={query_xray}"

    # 4. RocketReach Search
    query_rr = urllib.parse.quote(f'site:rocketreach.co "{nome_limpo}" ("{cargo}" OR "Manutenção Elétrica" OR "Engenharia Elétrica")')
    link_rr = f"https://www.google.com/search?q={query_rr}"

    return {
        "lusha": link_lusha,
        "lusha_portal": "https://www.lusha.com/",
        "linkedin_direto": link_linkedin,
        "google_xray": link_xray,
        "rocketreach": link_rr
    }

def remover_texto_pos_fechamento(texto: str) -> str:
    """
    Remove rigorosamente qualquer assinatura textual ou dados repetidos após a saudação
    (ex: 'Atenciosamente,', 'Cordialmente,'), uma vez que a assinatura corporativa oficial
    com a logomarca da KR Engenharia e os dados institucionais é anexada automaticamente.
    """
    fechamentos = [
        "atenciosamente,", "atenciosamente",
        "cordialmente,", "cordialmente",
        "respeitosamente,", "respeitosamente",
        "um abraço,", "abraços,"
    ]
    linhas = texto.strip().split("\n")
    linhas_filtradas = []
    for linha in linhas:
        linhas_filtradas.append(linha)
        if linha.strip().lower() in fechamentos:
            break
    return "\n".join(linhas_filtradas).strip()

# =====================================================================
# GERADOR DE ABORDAGENS HIPERPERSONALIZADAS (LUCAS CAMPOS)
# =====================================================================

PROMPT_LUCAS_OUTBOUND = """Você é Lucas Campos, Especialista em Inteligência Comercial e SDR da KR Engenharia.
Responsável Técnico: Eng. Kayllon Rogger Nunes (CREA-MG nº 141854962-2).
Posicionamento da Empresa: Boutique Técnica de Alta Especialização em Sistemas de Potência, Seletividade (ETAP), Automação SAS / IEC 61850 e Comissionamento de Campo (TAF/TAC).

SUA MISSÃO:
Redigir uma abordagem B2B de alto valor para o e-mail de um decisor técnico exclusivo da área de GERENCIAMENTO ELÉTRICO (Gerente de Manutenção Elétrica, Gerente de Engenharia Elétrica ou Coordenador de Comissionamento Elétrico) da empresa-alvo indicada.

DIRETRIZES DO E-MAIL:
1. Tom: De engenharia para engenharia. Extremamente respeitoso, sem bajulação, sem clichês de marketing genérico.
2. Parágrafo 1 - Contexto Técnico da Planta: Demonstre conhecimento sobre a operação da empresa-alvo (tensões, equipamentos críticos e os riscos operacionais como descoordenação de neutro, saturação de TCs ou janelas críticas de parada).
3. Parágrafo 2 - O Diferencial da KR Engenharia: Enfatize nossa metodologia de pré-validação em bancada (redução de até 40% de downtime) e cases de referência em grandes plantas (Baltic Power 400kV, Vale e Gerdau com Siemens SIPROTEC 5 e SEL).
4. Parágrafo 3 - Anexos & Chamada para Ação: Mencione que estamos anexando a Carta de Apresentação Institucional e o Portfólio de Serviços. Proponha uma conversa técnica rápida de 15 minutos na próxima semana.

REGRA CRÍTICA DE FECHAMENTO:
- Conclua a mensagem estritamente com a saudação: "Atenciosamente,".
- NUNCA adicione seu nome ("Lucas Campos"), cargo, empresa, telefone, CREA ou rodapé após "Atenciosamente,".
- Motivo: A assinatura visual corporativa completa com logomarca e dados de contato da KR Engenharia já é anexada automaticamente pelo sistema logo abaixo de "Atenciosamente,".

ESTRUTURA DA RESPOSTA:
ASSUNTO: [Linha de assunto direta e técnica]
CORPO:
[Texto completo do e-mail pronto para envio, encerrando exatamente com Atenciosamente,]
"""

def redigir_email_prospeccao(empresa_info: dict, especialidade_foco: str = "") -> Dict[str, str]:
    """Gera o assunto e corpo do e-mail hiperpersonalizado para a planta-alvo."""
    cargo_alvo = empresa_info.get("cargo_alvo", "Gerente de Manutenção Elétrica")
    contexto = f"""
EMPRESA-ALVO: {empresa_info['nome']}
DOMÍNIO CORPORATIVO: {empresa_info.get('dominio', '')}
NÍVEL DE TENSÃO DA PLANTA: {empresa_info.get('tensao', 'Alta Tensão')}
CARGO DO DECISOR ELÉTRICO: {cargo_alvo}
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

    # Garante que o corpo encerre estritamente na saudação Atenciosamente, sem duplicação
    corpo = remover_texto_pos_fechamento(corpo)

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
    Executa a prospecção autônoma do Lucas focada na área de Gerenciamento Elétrico.
    Mapeia as empresas, gera os links do Lusha, LinkedIn e Google X-Ray, redige os e-mails e anexa o portfólio.
    """
    setor_dados = CATALOGO_SETORES.get(chave_setor, CATALOGO_SETORES["MINERACAO"])
    empresas_alvo = setor_dados["empresas"][:limite]
    
    # Garante que os documentos institucionais estão compilados
    docs = compilar_documentos_institucionais()
    anexos_oficiais = docs["anexos_padrao"]

    fila_atual = carregar_fila_campanhas()
    novos_leads = []

    print(f"\n🚀 [Lucas Campos] Iniciando varredura no setor: {setor_dados['nome']} (Foco: Gerenciamento Elétrico)...")

    for emp in empresas_alvo:
        nome_emp = emp["nome"]
        cargo_alvo = emp.get("cargo_alvo", "Gerente de Manutenção Elétrica")
        print(f"   🔍 Mapeando oportunidades em: {nome_emp} (Decisor: {cargo_alvo})...")

        links = gerar_links_prospeccao(nome_emp, cargo_alvo)
        email_gerado = redigir_email_prospeccao(emp, especialidade_foco)

        lead = {
            "id": f"LEAD-{int(time.time())}-{len(fila_atual) + len(novos_leads) + 1}",
            "setor": setor_dados["nome"],
            "empresa": nome_emp,
            "dominio": emp.get("dominio", ""),
            "tensao": emp.get("tensao", ""),
            "cargo_alvo": cargo_alvo,
            "link_lusha": links["lusha"],
            "link_linkedin": links["linkedin_direto"],
            "link_xray": links["google_xray"],
            "link_rocketreach": links["rocketreach"],
            "email_destinatario": "",  # Preenchido via enriquecimento Lusha ou busca de contatos
            "contato_nome": "",
            "cargo_real": "",
            "telefones_contato": [],
            "linkedin_contato": "",
            "lusha_enriquecido": False,
            "lusha_status": "PENDENTE",
            "assunto": email_gerado["assunto"],
            "corpo_email": email_gerado["corpo"],
            "anexos": anexos_oficiais,
            "status": "PRONTO_PARA_DISPARO",
            "data_criacao": time.strftime("%d/%m/%Y %H:%M"),
            "data_envio": None,
            "resultado_envio": ""
        }
        novos_leads.append(lead)

    fila_atual.extend(novos_leads)
    salvar_fila_campanhas(fila_atual)
    print(f"✅ [Lucas Campos] {len(novos_leads)} leads mapeados com engrenagens Lusha/LinkedIn e portfólio anexo!")
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

def enriquecer_lead_por_id(
    lead_id: str,
    linkedin_url: Optional[str] = None,
    nome_completo: Optional[str] = None
) -> Dict:
    """
    Localiza um lead específico na fila de campanhas e enriquece com a API Lusha,
    salvando e-mail corporativo verificado e telefones sem deduções especulativas.
    """
    fila = carregar_fila_campanhas()
    lead_alvo = None
    for l in fila:
        if l.get("id") == lead_id:
            lead_alvo = l
            break
    if not lead_alvo:
        return {"sucesso": False, "encontrado": False, "mensagem": f"Lead {lead_id} não localizado na fila."}

    resultado = enriquecer_lead_com_lusha(
        lead_alvo,
        linkedin_url=linkedin_url,
        nome_completo=nome_completo
    )

    if resultado.get("encontrado"):
        salvar_fila_campanhas(fila)

    return resultado

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

