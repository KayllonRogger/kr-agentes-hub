import os
import json
import time
from datetime import datetime
import urllib.parse
from typing import List, Dict, Optional
from langchain_core.messages import SystemMessage, HumanMessage

from config import DADOS_EMPRESA, CONTAS_FUNCIONARIOS, eh_empresa_bloqueada, validar_cargo_icp_eletrico
from utils import get_llm, extrair_texto
from documentos_kr import compilar_documentos_institucionais
from servico_lusha import consultar_contato_lusha, consultar_empresa_lusha, enriquecer_lead_com_lusha
from servico_apollo import gerar_link_busca_apollo, consultar_empresa_apollo
from servico_rocketreach import (
    consultar_perfil_rocketreach,
    buscar_decisores_rocketreach,
    enriquecer_lead_com_rocketreach,
    verificar_status_rocketreach
)

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
                "cargo_alvo": "Gerente de Manutenção Elétrica e Automação",
                "departamento_alvo": "Coordenação de Manutenção Elétrica & Automação",
                "foco": "Alimentadores de moagem, seletividade de neutro e retrofits de relés"
            },
            {
                "nome": "Samarco Mineração - Complexos Ubu & Germano",
                "dominio": "samarco.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia e Manutenção Elétrica",
                "departamento_alvo": "Gerência de Engenharia e Manutenção Elétrica",
                "foco": "Reativação de subestações de alta tensão e parametrização de IEDs"
            },
            {
                "nome": "CSN Mineração - Casa de Pedra",
                "dominio": "csn.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "departamento_alvo": "Coordenação de Manutenção Elétrica",
                "foco": "Coordenação e seletividade no ETAP e proteção de alimentadores"
            },
            {
                "nome": "Kinross Brasil - Mina Morro do Ouro",
                "dominio": "kinross.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "departamento_alvo": "Gerência de Manutenção Elétrica",
                "foco": "Confiabilidade de subestações e mitigação de transitórios de partida"
            },
            {
                "nome": "Anglo American - Minas-Rio",
                "dominio": "angloamerican.com",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Coordenador de Engenharia Elétrica & Subestações",
                "departamento_alvo": "Coordenação de Engenharia Elétrica & Subestações",
                "foco": "Subestações de mineroduto e testes TAF/TAC em bancada"
            },
            {
                "nome": "Nexa Resources - Vazante / Juiz de Fora",
                "dominio": "nexaresources.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica e Automação",
                "departamento_alvo": "Gerência de Manutenção Elétrica e Automação",
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
                "departamento_alvo": "Coordenação de Manutenção Elétrica & Fornos a Arco",
                "foco": "Fornos elétricos a arco, lógicas GOOSE e relés SIPROTEC 5"
            },
            {
                "nome": "ArcelorMittal Tubarão / Monlevade",
                "dominio": "arcelormittal.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica e Automação",
                "departamento_alvo": "Gerência de Engenharia Elétrica e Automação",
                "foco": "Seletividade lógica, estudos de transitórios e cubículos de média tensão"
            },
            {
                "nome": "Usiminas - Usina de Ipatinga",
                "dominio": "usiminas.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "departamento_alvo": "Coordenação de Manutenção Elétrica",
                "foco": "Retrofit de cubículos e parametrização avançada de relés SEL"
            },
            {
                "nome": "Aperam South America - Timóteo",
                "dominio": "aperam.com",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Manutenção Elétrica",
                "departamento_alvo": "Gerência de Manutenção Elétrica",
                "foco": "Comissionamento TAC e ensaios com mala microprocessada calibrada RBC"
            },
            {
                "nome": "Albras - Alumínio Brasileiro",
                "dominio": "albras.net",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica & Subestações",
                "departamento_alvo": "Gerência de Engenharia Elétrica & Subestações",
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
                "departamento_alvo": "Gerência de Engenharia e Manutenção de Subestações",
                "foco": "Automação SAS / IEC 61850 e ensaios em relés de alta tensão"
            },
            {
                "nome": "Neoenergia - Parques Eólicos/Solares",
                "dominio": "neoenergia.com",
                "tensao": "230/34.5 kV",
                "cargo_alvo": "Coordenador de Comissionamento Elétrico",
                "departamento_alvo": "Coordenação de Comissionamento Elétrico",
                "foco": "Validação de bancada TAF/TAC e parametrização de proteção de interligação"
            },
            {
                "nome": "CPFL Renováveis",
                "dominio": "cpfl.com.br",
                "tensao": "138/34.5 kV",
                "cargo_alvo": "Gerente de Operação e Manutenção Elétrica",
                "departamento_alvo": "Gerência de Operação e Manutenção Elétrica",
                "foco": "Estudos de integração ao ONS e testes de seletividade"
            },
            {
                "nome": "Engie Brasil Energia",
                "dominio": "engie.com",
                "tensao": "230/138 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica & Proteção",
                "departamento_alvo": "Coordenação de Manutenção Elétrica & Proteção",
                "foco": "Ensaios secundários e relatórios técnicos com emissão de ART"
            },
            {
                "nome": "Atlas Renewable Energy",
                "dominio": "atlasrenewableenergy.com",
                "tensao": "230/34.5 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "departamento_alvo": "Gerência de Engenharia Elétrica",
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
                "departamento_alvo": "Gerência de Manutenção Elétrica e Automação",
                "foco": "Turbo-geradores industriais, lógica de ilhamento e estudos ETAP"
            },
            {
                "nome": "Klabin - Projeto Puma",
                "dominio": "klabin.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "departamento_alvo": "Gerência de Engenharia Elétrica",
                "foco": "Estabilidade de sistemas industriais e parametrização de IEDs"
            },
            {
                "nome": "Cenibra - Celulose Nipo-Brasileira",
                "dominio": "cenibra.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Manutenção Elétrica",
                "departamento_alvo": "Coordenação de Manutenção Elétrica",
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
                "departamento_alvo": "Gerência de Engenharia Elétrica e Comissionamento",
                "foco": "Subcontratação especialista em TAF/TAC e subestações turn-key"
            },
            {
                "nome": "Construtora Barbosa Mello (CBM)",
                "dominio": "cbm.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Coordenador de Comissionamento Elétrico",
                "departamento_alvo": "Coordenação de Comissionamento Elétrico",
                "foco": "Montagem eletromecânica e energização de plantas industriais"
            },
            {
                "nome": "MIP Engenharia",
                "dominio": "mip.com.br",
                "tensao": "138/13.8 kV",
                "cargo_alvo": "Gerente de Engenharia Elétrica",
                "departamento_alvo": "Gerência de Engenharia Elétrica",
                "foco": "Montagem eletromecânica industrial e testes de aceitação em campo"
            },
            {
                "nome": "Tenenge / Novonor",
                "dominio": "tenenge.com.br",
                "tensao": "230/13.8 kV",
                "cargo_alvo": "Gerente de Comissionamento Eletromecânico",
                "departamento_alvo": "Gerência de Comissionamento Eletromecânico",
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

    # 5. Apollo.io Search (B2B Lead Search)
    link_apollo = gerar_link_busca_apollo(nome_limpo, cargo)

    return {
        "lusha": link_lusha,
        "lusha_portal": "https://www.lusha.com/",
        "apollo": link_apollo,
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
Redigir uma abordagem B2B de alto valor para a área de GERENCIAMENTO ELÉTRICO e Sistemas de Potência da planta-alvo indicada.

DIRETRIZES DO E-MAIL:
1. Saudação Inicial Obrigatória:
   - Siga rigorosamente a DIRETRIZ DE SAUDAÇÃO indicada no contexto técnico.
   - NUNCA invente nomes de pessoas. Se o destinatário for uma liderança/coordenação departamental, dirija-se com o devido respeito técnico (ex: 'Prezada Coordenação de Manutenção Elétrica & Engenharia de Potência,').
2. Tom: De engenharia para engenharia. Extremamente respeitoso, sem bajulação, sem clichês de marketing genérico.
3. Parágrafo 1 - Contexto Técnico da Planta: Demonstre conhecimento sobre a operação da empresa-alvo (tensões, equipamentos críticos e os riscos operacionais como descoordenação de neutro, saturação de TCs ou janelas críticas de parada).
4. Parágrafo 2 - O Diferencial da KR Engenharia: Enfatize nossa metodologia de pré-validação em bancada (redução de até 40% de downtime) e cases de referência em grandes plantas (Baltic Power 400kV, Vale e Gerdau com Siemens SIPROTEC 5 e SEL).
5. Parágrafo 3 - Anexos & Chamada para Ação: Mencione que estamos anexando a Carta de Apresentação Institucional e o Portfólio de Serviços. Proponha uma conversa técnica rápida de 15 minutos na próxima semana.

REGRA CRÍTICA DE FECHAMENTO:
- Conclua a mensagem estritamente com a saudação: "Atenciosamente,".
- NUNCA adicione seu nome ("Lucas Campos"), cargo, empresa, telefone, CREA ou rodapé após "Atenciosamente,".
- Motivo: A assinatura visual corporativa completa com logomarca e dados de contato da KR Engenharia já é anexada automaticamente pelo sistema logo abaixo de "Atenciosamente,".

ESTRUTURA DA RESPOSTA:
ASSUNTO: [Linha de assunto direta e técnica]
CORPO:
[Texto completo do e-mail pronto para envio, iniciando pela saudação e encerrando exatamente com Atenciosamente,]
"""

def redigir_email_prospeccao(empresa_info: dict, especialidade_foco: str = "") -> Dict[str, str]:
    """Gera o assunto e corpo do e-mail hiperpersonalizado para a planta-alvo e liderança técnica."""
    nome_empresa = empresa_info.get("nome", "")
    dominio_emp = empresa_info.get("dominio", "")
    if eh_empresa_bloqueada(nome_empresa) or eh_empresa_bloqueada(dominio_emp):
        raise ValueError("O domínio sma-eng.com.br não deve ser prospectado como lead.")

    cargo_alvo = empresa_info.get("cargo_alvo", "Gerente de Manutenção Elétrica")
    decisor_nome = empresa_info.get("decisor_nome", "")
    decisor_cargo = empresa_info.get("decisor_cargo", cargo_alvo)
    tipo_lead = empresa_info.get("tipo_lead", "DEPARTAMENTAL_VERIFICADO")

    if tipo_lead == "NOMINAL_VERIFICADO" and decisor_nome and not any(termo in decisor_nome for termo in ["Coordenação", "Gerência", "Equipe"]):
        diretriz_saudacao = f"Inicie a mensagem OBRIGATORIAMENTE com a saudação nominal: 'Prezado {decisor_nome},'."
    else:
        diretriz_saudacao = f"Inicie a mensagem dirigindo-se à liderança técnica da planta: 'Prezada Coordenação de Manutenção Elétrica & Engenharia de Potência — {nome_empresa},'."

    contexto = f"""
EMPRESA-ALVO: {nome_empresa}
DOMÍNIO CORPORATIVO: {dominio_emp}
NÍVEL DE TENSÃO DA PLANTA: {empresa_info.get('tensao', 'Alta Tensão')}
DESTINATÁRIO TÉCNICO: {decisor_nome if decisor_nome else 'Coordenação de Manutenção Elétrica'}
CARGO / DEPARTAMENTO: {decisor_cargo}
DIRETRIZ DE SAUDAÇÃO: {diretriz_saudacao}
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
    assunto = f"KR Engenharia | Confiabilidade em Sistemas de Potência — {nome_empresa}"
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
# MOTOR DE RESOLUÇÃO E ENRIQUECIMENTO AUTÔNOMO (ROCKETREACH + APOLLO + LUSHA)
# =====================================================================

def resolver_decisor_autonomo(
    empresa_info: dict,
    linkedin_url: Optional[str] = None,
    nome_candidato: Optional[str] = None
) -> dict:
    """
    Resolve e enriquece os dados do decisor e da organização de forma 100% autônoma e segura:
    1. Apollo.io Organization Enrichment: telefone corporativo da sede, localização (cidade/estado), porte e setor.
    2. RocketReach API v2:
       - Se fornecido linkedin_url ou nome, consulta direta de contato via person/lookup.
       - Se for varredura autônoma (sem contato prévio), executa person/search filtrando por empresa e cargos elétricos.
       - Valida estritamente o cargo via validar_cargo_icp_eletrico() para descartar logística, produção e operadores.
    3. Lusha Person API: Fallback caso RocketReach não retorne ou esteja pendente de confirmação.
    4. Quando não houver decisor nominal verificado no ICP:
       Mapeia a Coordenação / Gerência de Manutenção Elétrica da planta com a central corporativa via Apollo.
    """
    nome_emp = empresa_info.get("nome", "")
    dominio_emp = empresa_info.get("dominio", "")
    cargo_alvo = empresa_info.get("cargo_alvo", "Gerente de Manutenção Elétrica")
    dep_alvo = empresa_info.get("departamento_alvo", "Coordenação de Manutenção Elétrica & Subestações")

    # 1. Apollo Organization Enrichment
    dados_apollo = None
    tel_apollo = ""
    cidade_apollo = ""
    estado_apollo = ""
    try:
        res_apollo = consultar_empresa_apollo(dominio_emp)
        if res_apollo.get("encontrado") and res_apollo.get("dados"):
            dados_apollo = res_apollo["dados"]
            tel_apollo = dados_apollo.get("telefone", "")
            cidade_apollo = dados_apollo.get("cidade", "")
            estado_apollo = dados_apollo.get("estado", "")
    except Exception as e:
        print(f"   ⚠️ [Apollo] Erro ao consultar {dominio_emp}: {e}")

    # 2. RocketReach Intelligence (Busca e Enriquecimento)
    dados_rr = None
    try:
        if linkedin_url or nome_candidato:
            res_rr = consultar_perfil_rocketreach(
                linkedin_url=linkedin_url if (linkedin_url and "linkedin.com/in/" in linkedin_url) else None,
                nome=nome_candidato,
                empresa=nome_emp
            )
            if res_rr.get("encontrado") and res_rr.get("dados"):
                cand_rr = res_rr["dados"]
                if validar_cargo_icp_eletrico(cand_rr.get("cargo", "")):
                    dados_rr = cand_rr
        else:
            # Varredura autônoma no RocketReach para a empresa
            res_busca_rr = buscar_decisores_rocketreach(
                empresa=nome_emp,
                cargos=[cargo_alvo, "Gerente de Manutenção Elétrica", "Coordenador de Manutenção Elétrica", "Engenheiro Eletricista"]
            )
            if res_busca_rr.get("encontrados"):
                melhor_cand = res_busca_rr["encontrados"][0]
                if melhor_cand.get("email_principal") or melhor_cand.get("telefones_formatados"):
                    dados_rr = melhor_cand
                elif melhor_cand.get("id") or melhor_cand.get("linkedin_url"):
                    lookup_rr = consultar_perfil_rocketreach(
                        person_id=melhor_cand.get("id"),
                        linkedin_url=melhor_cand.get("linkedin_url")
                    )
                    if lookup_rr.get("encontrado") and lookup_rr.get("dados"):
                        dados_rr = lookup_rr["dados"]
                    else:
                        dados_rr = melhor_cand
    except Exception as e:
        print(f"   ⚠️ [RocketReach] Erro na consulta de {nome_emp}: {e}")

    # 3. Lusha Person API Enrichment (Fallback)
    dados_lusha = None
    if not dados_rr and (linkedin_url or nome_candidato):
        try:
            partes_nome = (nome_candidato or "").replace("Eng.", "").strip().split()
            primeiro_nome = partes_nome[0] if partes_nome else None
            ultimo_nome = " ".join(partes_nome[1:]) if len(partes_nome) > 1 else None

            res_lusha = consultar_contato_lusha(
                linkedin_url=linkedin_url if (linkedin_url and "linkedin.com/in/" in linkedin_url) else None,
                primeiro_nome=primeiro_nome,
                ultimo_nome=ultimo_nome,
                dominio_empresa=dominio_emp
            )
            if res_lusha.get("encontrado") and res_lusha.get("dados"):
                candidato = res_lusha["dados"]
                cargo_candidato = candidato.get("cargo", "")
                if validar_cargo_icp_eletrico(cargo_candidato):
                    dados_lusha = candidato
                else:
                    print(f"   ⚠️ [ICP Rejeitado Lusha] Cargo '{cargo_candidato}' não pertence à gestão elétrica. Descartado.")
        except Exception as e:
            print(f"   ⚠️ [Lusha] Erro ao consultar contato: {e}")

    # 4. Consolidação dos campos
    origem_decisor = "APOLLO_DEPARTAMENTAL"
    dados_decisor = dados_rr or dados_lusha

    if dados_decisor:
        nome_final = dados_decisor.get("nome_completo", "")
        if nome_final and not nome_final.startswith("Eng."):
            nome_final = f"Eng. {nome_final}"
        cargo_final = dados_decisor.get("cargo", cargo_alvo)
        email_final = dados_decisor.get("email_principal", "")
        telefones_finais = list(dados_decisor.get("telefones_formatados", []))
        if tel_apollo and not any(tel_apollo in t for t in telefones_finais):
            telefones_finais.append(f"🏢 Sede/Central (Apollo): {tel_apollo}")
        linkedin_final = dados_decisor.get("linkedin_url", linkedin_url or "")
        tipo_lead = "NOMINAL_VERIFICADO"
        origem_decisor = "ROCKETREACH_VERIFICADO" if dados_rr else "LUSHA_VERIFICADO"
    else:
        # Canal Departamental Corporativo Oficial
        nome_final = dep_alvo
        cargo_final = cargo_alvo
        email_final = ""
        telefones_finais = [f"🏢 Central Corporativa (Apollo): {tel_apollo}"] if tel_apollo else []
        linkedin_final = ""
        tipo_lead = "DEPARTAMENTAL_VERIFICADO"
        origem_decisor = "APOLLO_DEPARTAMENTAL"

    cidade_final = cidade_apollo or (dados_decisor.get("cidade") if dados_decisor else "")
    estado_final = estado_apollo or (dados_decisor.get("estado") if dados_decisor else "")

    return {
        "contato_nome": nome_final,
        "cargo_real": cargo_final,
        "email_destinatario": email_final,
        "telefones_contato": telefones_finais,
        "linkedin_contato": linkedin_final,
        "cidade": cidade_final,
        "estado": estado_final,
        "tipo_lead": tipo_lead,
        "origem_decisor": origem_decisor,
        "rocketreach_enriquecido": bool(dados_rr),
        "lusha_enriquecido": bool(dados_lusha),
        "lusha_status": "ENRIQUECIDO" if dados_lusha else ("ENRIQUECIDO_RR" if dados_rr else "CANAL_CORPORATIVO"),
        "apollo_enriquecido": bool(dados_apollo),
        "dados_apollo": dados_apollo,
        "dados_rocketreach": dados_rr,
        "dados_lusha": dados_lusha
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

def empresa_ja_contatada(empresa: str, dominio: str = "", fila: Optional[List[Dict]] = None) -> Optional[Dict]:
    """
    Verifica se uma empresa já foi mapeada ou contatada no pipeline de prospecção da KR Engenharia,
    ou se pertence à lista de domínios restritos (ex: @sma-eng.com.br).
    Evita rigorosamente que o Lucas repita cold outreach para a mesma organização.
    Retorna o lead existente se encontrado, ou None se for uma empresa inédita.
    """
    if eh_empresa_bloqueada(empresa) or eh_empresa_bloqueada(dominio):
        return {
            "empresa": empresa,
            "dominio": dominio,
            "bloqueado_prospeccao_fria": True,
            "status": "Bloqueado",
            "motivo": "Domínio ou empresa bloqueada para prospecção"
        }

    if fila is None:
        fila = carregar_fila_campanhas()
    if not fila:
        return None

    empresa_norm = empresa.lower().split(" - ")[0].strip()
    dom_norm = (dominio or "").lower().replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()

    for lead in fila:
        # 1. Verifica domínio idêntico
        lead_dom = lead.get("dominio", "").lower().replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()
        if dom_norm and lead_dom and dom_norm == lead_dom:
            return lead

        # 2. Verifica nome da empresa
        lead_empresa = lead.get("empresa", "").lower().split(" - ")[0].strip()
        if empresa_norm and lead_empresa:
            if empresa_norm == lead_empresa or empresa_norm in lead_empresa or lead_empresa in empresa_norm:
                return lead

    return None

def executar_varredura_setor(
    chave_setor: str = "MINERACAO",
    especialidade_foco: str = "Estudos de Proteção no ETAP e Comissionamento TAF/TAC",
    limite: int = 3
) -> List[Dict]:
    """
    Executa a prospecção autônoma do Lucas focada na área de Gerenciamento Elétrico.
    Mapeia as empresas, resolve e enriquece contatos via Lusha e Apollo.io autonomamente,
    redige os e-mails personalizados nominalmente e anexa o portfólio oficial.
    Garante deduplicação estrita: nunca repete abordagem fria para quem já está no pipeline.
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
        dominio_emp = emp.get("dominio", "")

        # Ignora se pertencer ao domínio restrito sma-eng.com.br
        if eh_empresa_bloqueada(nome_emp) or eh_empresa_bloqueada(dominio_emp):
            print(f"   ℹ️ [Ignorado] {nome_emp} possui domínio restrito (@sma-eng.com.br). Não será adicionada como novo lead.")
            continue

        # Deduplicação: Nunca repete prospecção fria para empresas já no pipeline ou contatadas
        lead_existente = empresa_ja_contatada(nome_emp, dominio_emp, fila_atual + novos_leads)
        if lead_existente:
            st_exist = lead_existente.get("status", "NO_PIPELINE")
            resp_exist = lead_existente.get("responsavel_atual_nome", "Lucas Campos")
            print(f"   ℹ️ [Ignorado - Já Mapeado] {nome_emp} já consta no pipeline ({st_exist} com {resp_exist}). Prospecção inicial não será duplicada.")
            continue

        cargo_alvo = emp.get("cargo_alvo", "Gerente de Manutenção Elétrica")
        print(f"   🔍 Resolvendo decisor e contatos autônomos em: {nome_emp}...")

        # Resolução autônoma via Apollo + Lusha + Catálogo
        decisor_resolvido = resolver_decisor_autonomo(emp)

        # Atualiza dados da empresa para redação nominal
        emp_com_contato = dict(emp)
        emp_com_contato["decisor_nome"] = decisor_resolvido["contato_nome"]
        emp_com_contato["decisor_cargo"] = decisor_resolvido["cargo_real"]

        links = gerar_links_prospeccao(nome_emp, decisor_resolvido["cargo_real"])
        email_gerado = redigir_email_prospeccao(emp_com_contato, especialidade_foco)

        lead = {
            "id": f"LEAD-{int(time.time())}-{len(fila_atual) + len(novos_leads) + 1}",
            "setor": setor_dados["nome"],
            "empresa": nome_emp,
            "dominio": dominio_emp,
            "tensao": emp.get("tensao", ""),
            "cargo_alvo": cargo_alvo,
            "cargo_real": decisor_resolvido["cargo_real"],
            "contato_nome": decisor_resolvido["contato_nome"],
            "email_destinatario": decisor_resolvido["email_destinatario"],
            "telefones_contato": decisor_resolvido["telefones_contato"],
            "linkedin_contato": decisor_resolvido["linkedin_contato"],
            "cidade": decisor_resolvido["cidade"],
            "estado": decisor_resolvido["estado"],
            "link_lusha": links["lusha"],
            "link_apollo": links["apollo"],
            "link_linkedin": links["linkedin_direto"],
            "link_xray": links["google_xray"],
            "link_rocketreach": links["rocketreach"],
            "lusha_enriquecido": decisor_resolvido["lusha_enriquecido"],
            "lusha_status": decisor_resolvido["lusha_status"],
            "apollo_enriquecido": decisor_resolvido["apollo_enriquecido"],
            "rocketreach_enriquecido": decisor_resolvido.get("rocketreach_enriquecido", False),
            "tipo_lead": decisor_resolvido.get("tipo_lead", "DEPARTAMENTAL_VERIFICADO"),
            "origem_decisor": decisor_resolvido.get("origem_decisor", "APOLLO_DEPARTAMENTAL"),
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
    print(f"✅ [Lucas Campos] {len(novos_leads)} leads adicionados com e-mails e telefones verificados prontos para envio!")
    return novos_leads

def enriquecer_fila_autonomamente(forcar_redacao: bool = False) -> Dict[str, Any]:
    """
    Varre todos os leads na fila de campanhas e preenche autonomamente os campos
    de decisor, e-mail corporativo verificado, telefones (Lusha + Apollo) e personalização nominal.
    """
    fila = carregar_fila_campanhas()
    if not fila:
        return {"sucesso": True, "total": 0, "enriquecidos": 0, "mensagem": "Fila vazia."}

    enriquecidos_count = 0
    fila_atualizada = []

    # Mapa de consulta rápida no catálogo
    mapa_catalogo = {}
    for setor_key, s_data in CATALOGO_SETORES.items():
        for e in s_data["empresas"]:
            dom = e.get("dominio", "").lower().strip()
            if dom:
                mapa_catalogo[dom] = e
            nome_limpo = e.get("nome", "").split(" - ")[0].lower().strip()
            mapa_catalogo[nome_limpo] = e

    for lead in fila:
        # Segurança: bloqueia @sma-eng.com.br
        if eh_empresa_bloqueada(lead.get("dominio", "")) or eh_empresa_bloqueada(lead.get("empresa", "")):
            continue

        dom_lead = lead.get("dominio", "").lower().strip()
        nome_lead = lead.get("empresa", "").split(" - ")[0].lower().strip()

        emp_info = mapa_catalogo.get(dom_lead) or mapa_catalogo.get(nome_lead) or {
            "nome": lead.get("empresa", ""),
            "dominio": lead.get("dominio", ""),
            "tensao": lead.get("tensao", ""),
            "cargo_alvo": lead.get("cargo_alvo", "Gerente de Manutenção Elétrica"),
            "decisor_nome": lead.get("contato_nome", ""),
            "decisor_cargo": lead.get("cargo_real") or lead.get("cargo_alvo", ""),
            "decisor_email": lead.get("email_destinatario", ""),
            "decisor_telefone": lead.get("telefones_contato", [""])[0] if lead.get("telefones_contato") else "",
            "decisor_linkedin": lead.get("linkedin_contato", "")
        }

        decisor_resolvido = resolver_decisor_autonomo(emp_info)

        # Atualiza campos
        lead["contato_nome"] = decisor_resolvido["contato_nome"]
        lead["cargo_real"] = decisor_resolvido["cargo_real"]
        lead["email_destinatario"] = decisor_resolvido["email_destinatario"]
        lead["telefones_contato"] = decisor_resolvido["telefones_contato"]
        lead["linkedin_contato"] = decisor_resolvido["linkedin_contato"]
        lead["cidade"] = decisor_resolvido["cidade"]
        lead["estado"] = decisor_resolvido["estado"]
        lead["lusha_enriquecido"] = decisor_resolvido["lusha_enriquecido"]
        lead["lusha_status"] = decisor_resolvido["lusha_status"]
        lead["apollo_enriquecido"] = decisor_resolvido["apollo_enriquecido"]
        lead["rocketreach_enriquecido"] = decisor_resolvido.get("rocketreach_enriquecido", False)
        lead["origem_decisor"] = decisor_resolvido.get("origem_decisor", "APOLLO_DEPARTAMENTAL")
        lead["tipo_lead"] = decisor_resolvido.get("tipo_lead", "DEPARTAMENTAL_VERIFICADO")

        # Se o corpo atual tiver saudação genérica ("Prezado Gerente") ou forçado, regenera com nome
        corpo_atual = lead.get("corpo_email", "")
        if forcar_redacao or "Prezado Gerente" in corpo_atual or "Prezado Coordenador" in corpo_atual or not corpo_atual:
            emp_info_redacao = dict(emp_info)
            emp_info_redacao["decisor_nome"] = decisor_resolvido["contato_nome"]
            emp_info_redacao["decisor_cargo"] = decisor_resolvido["cargo_real"]
            novo_email = redigir_email_prospeccao(emp_info_redacao)
            lead["assunto"] = novo_email["assunto"]
            lead["corpo_email"] = novo_email["corpo"]

        enriquecidos_count += 1
        fila_atualizada.append(lead)

    salvar_fila_campanhas(fila_atualizada)
    return {
        "sucesso": True,
        "total": len(fila_atualizada),
        "enriquecidos": enriquecidos_count,
        "mensagem": f"{enriquecidos_count} lead(s) enriquecidos autonomamente com contatos RocketReach/Apollo/Lusha e e-mails nominais!"
    }

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
    nome_completo: Optional[str] = None,
    motor: str = "auto"
) -> Dict:
    """
    Localiza um lead específico na fila de campanhas e enriquece com as APIs RocketReach e Lusha,
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

    resultado = None

    # Tenta RocketReach primeiro se solicitado ou automático
    if motor in ["auto", "rocketreach"]:
        resultado_rr = enriquecer_lead_com_rocketreach(
            lead_alvo,
            linkedin_url=linkedin_url,
            nome_completo=nome_completo
        )
        if resultado_rr.get("encontrado"):
            salvar_fila_campanhas(fila)
            return resultado_rr
        elif motor == "rocketreach":
            return resultado_rr

    # Fallback para Lusha se motor for auto ou lusha
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

def calcular_dias_envio(data_envio_str: Optional[str]) -> int:
    """Calcula os dias corridos transcorridos desde a data de envio informada."""
    if not data_envio_str:
        return 0
    formatos = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y"
    ]
    for fmt in formatos:
        try:
            dt = datetime.strptime(str(data_envio_str).strip(), fmt)
            delta = datetime.now() - dt
            return max(0, delta.days)
        except Exception:
            continue
    return 0

def gerar_email_followup(lead: Dict, etapa: int = 1) -> Dict[str, str]:
    """
    Gera o e-mail de follow-up hiperpersonalizado e técnico para o lead de acordo com a etapa:
    - Etapa 1 (D+3 a D+5): Reforço de valor e confirmação de recebimento dos documentos técnicos.
    - Etapa 2 (D+7 a D+10): Estudo de caso de redução de downtime e convite direto para reunião de 15 min.
    - Etapa 3 (D+14+): Break-up cordial preservando relacionamento técnico futuro.
    """
    empresa = lead.get("empresa", "sua empresa")
    decisor = lead.get("contato_nome") or "Coordenação de Engenharia Elétrica"
    tensao = lead.get("tensao", "média e alta tensão")
    assunto_orig = lead.get("assunto", "Estudos de Proteção Elétrica e Comissionamento TAF/TAC")
    if not assunto_orig.lower().startswith("re:"):
        assunto_follow = f"Re: {assunto_orig}"
    else:
        assunto_follow = assunto_orig

    llm = get_llm()

    if etapa == 1:
        corpo_padrao = (
            f"Prezado(a) {decisor},\n\n"
            f"Escrevo para dar um breve retorno sobre a mensagem enviada há alguns dias a respeito da atuação da KR Engenharia em Estudos de Proteção Elétrica (ETAP) e Comissionamento TAF/TAC para as instalações de {tensao} da {empresa}.\n\n"
            f"Sabemos da intensidade da rotina de operação e manutenção nos sistemas de potência industrial. Gostaria apenas de confirmar se você conseguiu avaliar nossa Carta de Apresentação e o Portfólio de Serviços encaminhados anteriormente — em especial nossas atuações na pré-validação de relés em bancada e mitigação de descoordenação de neutro em plantas de grande porte como Vale, Gerdau e no projeto offshore Baltic Power 400 kV.\n\n"
            f"Caso faça sentido para o planejamento técnico da {empresa}, ficamos à disposição para um alinhamento rápido de 15 minutos.\n\n"
            f"Atenciosamente,"
        )
        prompt_etapa = (
            f"Redija um follow-up curto, elegante e extremamente profissional de engenharia (Follow-up 1: Confirmação de recebimento e reforço de valor).\n"
            f"Lead: {decisor}, Empresa: {empresa}, Tensão: {tensao}.\n"
            f"Mencione os anexos (Carta Institucional e Portfólio) e a redução de riscos de paradas não programadas.\n"
            f"Termine com 'Atenciosamente,' sem assinar o nome no final."
        )
    elif etapa == 2:
        assunto_follow = f"{assunto_follow} | Case Técnico: Redução de 40% em Downtime de Comissionamento"
        corpo_padrao = (
            f"Prezado(a) {decisor},\n\n"
            f"Nas interações recentes com coordenadores elétricos em plantas de {tensao}, um desafio comum que identificamos é o cumprimento dos cronogramas de paradas programadas sem comprometer a rigorosa validação das parametrizações de IEDs e lógicas IEC 61850.\n\n"
            f"Na KR Engenharia, aplicamos uma sistemática de ensaios secundários automatizados prévios com mala microprocessada calibrada RBC. Essa metodologia permitiu a clientes industriais reduzir em até 40% o tempo de intervenção em campo durante janelas críticas, eliminando retrabalhos em energizações.\n\n"
            f"Gostaria de verificar sua disponibilidade para uma conversa técnica de 15 minutos nesta semana ou na próxima. Terça ou quinta-feira pela manhã funcionaria para você?\n\n"
            f"Atenciosamente,"
        )
        prompt_etapa = (
            f"Redija um follow-up persuasivo e técnico (Follow-up 2: Estudo de Caso e proposta de reunião técnica de 15 min).\n"
            f"Lead: {decisor}, Empresa: {empresa}, Tensão: {tensao}.\n"
            f"Destaque o case de redução de 40% de downtime com ensaios automatizados de relés e sugira horários (terça ou quinta).\n"
            f"Termine com 'Atenciosamente,' sem assinar o nome no final."
        )
    else:
        assunto_follow = f"{assunto_follow} | Próximos passos e acervo técnico"
        corpo_padrao = (
            f"Prezado(a) {decisor},\n\n"
            f"Como não tivemos retorno às tentativas anteriores, imagino que as prioridades da equipe técnica da {empresa} estejam voltadas para outros projetos e paradas no momento.\n\n"
            f"Para não sobrecarregar sua caixa postal, encerro por aqui nossas tentativas ativas de contato. Nosso acervo técnico de estudos de coordenação/seletividade no ETAP e procedimentos de comissionamento TAF/TAC permanece à inteira disposição da sua equipe caso surja alguma demanda futura ou necessidade de suporte emergencial.\n\n"
            f"Desejo muito sucesso às operações da {empresa} e será um prazer restabelecer contato quando for o momento oportuno.\n\n"
            f"Atenciosamente,"
        )
        prompt_etapa = (
            f"Redija um e-mail de 'Break-up' cordial e técnico (Follow-up 3: Encerramento elegante de cadência).\n"
            f"Lead: {decisor}, Empresa: {empresa}.\n"
            f"Reconheça as prioridades da empresa, encerre o contato ativo sem pressão e deixe a porta aberta para o futuro com a KR Engenharia.\n"
            f"Termine com 'Atenciosamente,' sem assinar o nome no final."
        )

    if llm:
        try:
            msgs = [
                SystemMessage(content=(
                    "Você é Lucas Campos, SDR e Analista Comercial da KR Engenharia. "
                    "Seu tom é técnico, respeitoso, objetivo e de engenheiro para engenheiro. "
                    "Nunca invente nomes fictícios nem prometa o que a engenharia não faz. "
                    "Termine com 'Atenciosamente,' sem colocar o nome após."
                )),
                HumanMessage(content=prompt_etapa)
            ]
            resp = llm.invoke(msgs)
            corpo_llm = extrair_texto(resp).strip()
            if len(corpo_llm) > 100:
                corpo_padrao = corpo_llm
        except Exception as e:
            print(f"⚠️ Fallback para template padrão no follow-up {etapa}: {e}")

    return {
        "assunto": assunto_follow,
        "corpo": corpo_padrao
    }

def avancar_etapa_followup(lead_id: str, etapa_alvo: int) -> Dict:
    """
    Avança o lead para a próxima etapa de follow-up (1, 2 ou 3).
    Gera o novo e-mail e atualiza o status na fila de campanhas.
    """
    fila = carregar_fila_campanhas()
    lead = next((l for l in fila if l.get("id") == lead_id), None)
    if not lead:
        return {"sucesso": False, "mensagem": f"Lead {lead_id} não localizado."}

    if lead.get("bloqueado_prospeccao_fria"):
        custodia = lead.get("custodia_funcionario_nome", "Especialista")
        return {
            "sucesso": False,
            "mensagem": f"Lead está sob custódia de {custodia} ({lead.get('status')}). Follow-up frio bloqueado."
        }

    email_f = gerar_email_followup(lead, etapa=etapa_alvo)

    st_map = {
        1: "FOLLOW_UP_1_PENDENTE",
        2: "FOLLOW_UP_2_PENDENTE",
        3: "BREAK_UP_PENDENTE"
    }
    novo_status = st_map.get(etapa_alvo, f"FOLLOW_UP_{etapa_alvo}_PENDENTE")

    lead["etapa_followup"] = etapa_alvo
    lead["status"] = novo_status
    lead["assunto"] = email_f["assunto"]
    lead["corpo_email"] = email_f["corpo"]
    lead["data_geracao_followup"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    salvar_fila_campanhas(fila)
    return {
        "sucesso": True,
        "mensagem": f"Follow-up {etapa_alvo} gerado por Lucas Campos com sucesso!",
        "lead": lead
    }

def transferir_lead_para_especialista(
    lead_id: str,
    funcionario_id: str,
    motivo: str,
    observacoes: str = "",
    fechar_contrato: bool = False
) -> Dict:
    """
    Transfere a custódia do lead de Lucas Campos para um especialista técnico (Beatriz, Rafael, Carlos, etc.).
    Garante que Lucas NÃO repetirá contatos de prospecção fria.
    Cria uma tarefa oficial no Escritório Virtual (tarefas_empresa.json).
    """
    from empresa_kr import FUNCIONARIOS, atribuir_tarefa

    fila = carregar_fila_campanhas()
    lead = next((l for l in fila if l.get("id") == lead_id), None)
    if not lead:
        return {"sucesso": False, "mensagem": f"Lead {lead_id} não localizado."}

    funcionario_id = (funcionario_id or "").strip().upper()
    if funcionario_id not in FUNCIONARIOS:
        return {"sucesso": False, "mensagem": f"Especialista {funcionario_id} não cadastrado."}

    func_info = FUNCIONARIOS[funcionario_id]
    empresa = lead.get("empresa", "Empresa")
    decisor = lead.get("contato_nome", "Decisor")
    tensao = lead.get("tensao", "N/D")

    novo_status = "CONTRATO_FECHADO" if fechar_contrato else "RESPONDIDO_EM_NEGOCIACAO"
    lead["status"] = novo_status
    lead["bloqueado_prospeccao_fria"] = True
    lead["fechar_contrato"] = fechar_contrato
    lead["custodia_funcionario_id"] = funcionario_id
    lead["custodia_funcionario_nome"] = func_info["nome"]
    lead["custodia_funcionario_cargo"] = func_info["cargo"]
    lead["data_transferencia"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Histórico de transferências
    historico = lead.get("historico_transferencia", [])
    historico.append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "de": "LUCAS",
        "para": funcionario_id,
        "para_nome": func_info["nome"],
        "motivo": motivo,
        "fechar_contrato": fechar_contrato,
        "observacoes": observacoes
    })
    lead["historico_transferencia"] = historico

    # Gera tarefa no Escritório Virtual para o especialista
    rotulo = "CONTRATO FECHADO" if fechar_contrato else "RESPOSTA POSITIVA / NEGOCIAÇÃO"
    titulo_tarefa = f"[{rotulo}] Atendimento: {empresa} — {decisor}"

    instrucao = (
        f"🎯 PASSAGEM DE BASTÃO COMERCIAL (Lucas Campos ➔ {func_info['nome']})\n"
        f"Status: {rotulo}\n"
        f"Cliente: {empresa} (Tensão: {tensao})\n"
        f"Decisor: {decisor} ({lead.get('cargo_real') or lead.get('cargo_alvo', '')})\n"
        f"E-mail: {lead.get('email_destinatario', 'N/D')}\n"
        f"Telefones: {', '.join(lead.get('telefones_contato', [])) if lead.get('telefones_contato') else 'Central telefônica mapeada'}\n"
        f"Localização: {lead.get('cidade', '')} - {lead.get('estado', '')}\n\n"
        f"Motivo da Transferência: {motivo}\n"
        f"Observações / Alinhamento: {observacoes if observacoes else 'Sem observações adicionais.'}\n\n"
        f"📌 DIRETRIZES OPERACIONAIS PARA {func_info['nome'].upper()} ({func_info['cargo']}):\n"
    )

    if funcionario_id == "BEATRIZ":
        instrucao += (
            "1. Estruturação do DataBook As-Built e minutas de ART junto ao CREA-MG.\n"
            "2. Conduzir reunião formal de Onboarding com os gestores da planta.\n"
            "3. Estabelecer canal direto de Customer Success e marcos contratuais (30/90 dias)."
        )
    elif funcionario_id == "RAFAEL":
        instrucao += (
            "1. Obter diagramas unifilares completos e especificações de IEDs da planta.\n"
            "2. Configurar o modelo de simulação no ETAP (curto-circuito, fluxo de potência e seletividade ANSI 50/51/51N/51V).\n"
            "3. Elaborar parecer técnico e conduzir alinhamento com a equipe de engenharia do cliente."
        )
    elif funcionario_id == "CARLOS":
        instrucao += (
            "1. Planejar mobilização técnica para comissionamento TAF (em fábrica) ou TAC (em campo).\n"
            "2. Definir roteiro de ensaios secundários de relés com mala microprocessada calibrada RBC.\n"
            "3. Alinhar janelas de parada com a operação e conformidade com NR-10 e NR-35."
        )
    elif funcionario_id == "MARIANA":
        instrucao += (
            "1. Avaliar autorização para elaboração de Estudo de Caso institucional conjunto.\n"
            "2. Estruturar material técnico de autoridade preservando dados confidenciais do cliente."
        )
    else:
        instrucao += (
            "1. Conduzir atendimento técnico especializado e manter comunicação direta com o cliente."
        )

    tarefa = atribuir_tarefa(
        titulo=titulo_tarefa,
        funcionario_id=funcionario_id,
        instrucao=instrucao
    )
    lead["tarefa_id_escritorio"] = tarefa["id"]

    salvar_fila_campanhas(fila)
    return {
        "sucesso": True,
        "tarefa_id": tarefa["id"],
        "lead": lead,
        "mensagem": f"Lead transferido com sucesso para {func_info['nome']}! Tarefa #{tarefa['id']} registrada no Escritório Virtual."
    }

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

