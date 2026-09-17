import os
import requests
import urllib.parse
from typing import Dict, Optional, List, Any
from config import ROCKETREACH_API_KEY, eh_empresa_bloqueada, validar_cargo_icp_eletrico

ROCKETREACH_API_BASE = "https://api.rocketreach.co/api/v2"

# Termos prioritários de busca no RocketReach para a área de gerenciamento elétrico
CARGOS_PADRAO_ROCKETREACH = [
    "Gerente de Manutenção Elétrica",
    "Coordenador de Manutenção Elétrica",
    "Gerente de Engenharia Elétrica",
    "Coordenador de Engenharia Elétrica",
    "Engenheiro Eletricista",
    "Gerente de Subestações",
    "Especialista em Proteção e Automação"
]

def get_rocketreach_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Retorna cabeçalhos HTTP autenticados para a RocketReach API v2."""
    key = (api_key or ROCKETREACH_API_KEY or "").strip()
    return {
        "Api-Key": key,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "KREngenharia-LucasCampos/2.0"
    }

def verificar_status_rocketreach(api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Verifica a autenticação e o status da conta RocketReach.
    Identifica especificamente se a conta está ativa ou se o e-mail de ativação ainda está pendente de confirmação.
    """
    key = (api_key or ROCKETREACH_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "ativo": False,
            "verificado": False,
            "pendente_email": False,
            "mensagem": "Chave ROCKETREACH_API_KEY não configurada no ambiente (.env).",
            "erro": "MISSING_API_KEY"
        }

    try:
        url = f"{ROCKETREACH_API_BASE}/account"
        headers = get_rocketreach_headers(key)
        resp = requests.get(url, headers=headers, timeout=12)

        if resp.status_code == 401:
            texto_erro = resp.text.lower()
            if "verify your email" in texto_erro:
                return {
                    "sucesso": False,
                    "ativo": False,
                    "verificado": False,
                    "pendente_email": True,
                    "mensagem": (
                        "Conta RocketReach reconhecida, mas aguardando confirmação de e-mail. "
                        "Por favor, acerte a validação clicando no link enviado para a sua caixa de entrada da RocketReach."
                    ),
                    "erro": "EMAIL_VERIFICATION_PENDING"
                }
            return {
                "sucesso": False,
                "ativo": False,
                "verificado": False,
                "pendente_email": False,
                "mensagem": f"Chave RocketReach inválida ou não autorizada (HTTP 401): {resp.text[:150]}",
                "erro": "INVALID_KEY"
            }

        if resp.status_code == 200:
            dados = resp.json()
            creditos = dados.get("credits", {})
            return {
                "sucesso": True,
                "ativo": True,
                "verificado": True,
                "pendente_email": False,
                "creditos": creditos,
                "mensagem": "RocketReach API v2 autenticada e pronta para buscas!",
                "dados": dados,
                "erro": None
            }

        return {
            "sucesso": False,
            "ativo": False,
            "verificado": False,
            "pendente_email": False,
            "mensagem": f"Retorno inesperado da RocketReach (HTTP {resp.status_code}): {resp.text[:150]}",
            "erro": f"HTTP_{resp.status_code}"
        }

    except requests.RequestException as exc:
        return {
            "sucesso": False,
            "ativo": False,
            "verificado": False,
            "pendente_email": False,
            "mensagem": f"Erro de conexão com a API RocketReach: {str(exc)}",
            "erro": "CONNECTION_ERROR"
        }

def formatar_perfil_rocketreach(raw_person: dict) -> Dict[str, Any]:
    """Formata o perfil retornado pela RocketReach para a estrutura padrão da KR Engenharia."""
    nome = raw_person.get("name", "")
    cargo = raw_person.get("current_title") or raw_person.get("title") or ""
    empresa = raw_person.get("current_employer") or raw_person.get("employer") or ""
    linkedin_url = raw_person.get("linkedin_url", "")
    cidade = raw_person.get("city", "")
    estado = raw_person.get("region") or raw_person.get("state") or ""
    pais = raw_person.get("country_code") or raw_person.get("country") or ""

    # E-mails (separa corporativos e pessoais com validação SMTP)
    emails_raw = raw_person.get("emails", [])
    emails_trabalho = []
    emails_pessoais = []
    emails_todos = []

    for item in emails_raw:
        if isinstance(item, dict):
            em = item.get("email", "").strip()
            tipo = item.get("type", "work")
            smtp = item.get("smtp_valid", "")
            if em:
                emails_todos.append(em)
                if tipo == "work" or smtp == "valid":
                    emails_trabalho.append(em)
                else:
                    emails_pessoais.append(em)
        elif isinstance(item, str) and item.strip():
            emails_todos.append(item.strip())
            emails_trabalho.append(item.strip())

    # Telefones (móvel, direto, corporativo)
    telefones_raw = raw_person.get("phones", [])
    telefones = []
    telefones_formatados = []

    for item in telefones_raw:
        if isinstance(item, dict):
            num = item.get("number", "").strip()
            tipo = item.get("type", "direct")
            if num:
                telefones.append({"numero": num, "tipo": tipo})
                prefixo = "📱 Celular/Móvel" if tipo == "mobile" else ("📞 Direto" if tipo == "direct" else "🏢 Escritório")
                telefones_formatados.append(f"{prefixo}: {num}")
        elif isinstance(item, str) and item.strip():
            telefones.append({"numero": item.strip(), "tipo": "phone"})
            telefones_formatados.append(f"📞 {item.strip()}")

    email_principal = emails_trabalho[0] if emails_trabalho else (emails_todos[0] if emails_todos else "")

    return {
        "id": raw_person.get("id"),
        "nome_completo": nome,
        "cargo": cargo,
        "empresa": empresa,
        "email_principal": email_principal,
        "emails_trabalho": emails_trabalho,
        "emails_pessoais": emails_pessoais,
        "emails_todos": emails_todos,
        "telefones": telefones,
        "telefones_formatados": telefones_formatados,
        "cidade": cidade,
        "estado": estado,
        "pais": pais,
        "linkedin_url": linkedin_url,
        "raw": raw_person
    }

def consultar_perfil_rocketreach(
    linkedin_url: Optional[str] = None,
    nome: Optional[str] = None,
    empresa: Optional[str] = None,
    person_id: Optional[int] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consulta o perfil completo de um decisor pelo endpoint person/lookup da RocketReach API v2.
    Permite busca por linkedin_url, person_id ou nome + empresa.
    Aplica filtro rigoroso de ICP elétrico no cargo retornado.
    """
    if empresa and eh_empresa_bloqueada(empresa):
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Consulta bloqueada: O domínio sma-eng.com.br não deve ser prospectado.",
            "dados": None,
            "erro": "BLOCKED_DOMAIN"
        }

    key = (api_key or ROCKETREACH_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Chave ROCKETREACH_API_KEY não configurada no ambiente (.env).",
            "dados": None,
            "erro": "MISSING_API_KEY"
        }

    params: Dict[str, Any] = {}
    if person_id:
        params["id"] = person_id
    elif linkedin_url and "linkedin.com" in linkedin_url.lower():
        url_limpa = linkedin_url.split("?")[0].strip()
        params["linkedin_url"] = url_limpa
    elif nome and empresa:
        params["name"] = nome.replace("Eng.", "").strip()
        params["current_employer"] = empresa.split(" - ")[0].strip()
    else:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Parâmetros insuficientes: forneça LinkedIn URL, ID do RocketReach ou Nome + Empresa.",
            "dados": None,
            "erro": "INVALID_PARAMS"
        }

    try:
        url = f"{ROCKETREACH_API_BASE}/person/lookup"
        headers = get_rocketreach_headers(key)
        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 401:
            texto_erro = resp.text.lower()
            if "verify your email" in texto_erro:
                return {
                    "sucesso": False,
                    "encontrado": False,
                    "mensagem": "A conta RocketReach precisa ter o e-mail confirmado para liberar o uso da API.",
                    "dados": None,
                    "erro": "EMAIL_VERIFICATION_PENDING"
                }
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Erro de autenticação RocketReach (HTTP 401): {resp.text[:150]}",
                "dados": None,
                "erro": "AUTH_ERROR"
            }

        if resp.status_code == 404:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": "Perfil não localizado no RocketReach.",
                "dados": None,
                "erro": "NOT_FOUND"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Falha na consulta RocketReach (HTTP {resp.status_code}): {resp.text[:150]}",
                "dados": None,
                "erro": f"HTTP_{resp.status_code}"
            }

        raw_person = resp.json()
        dados_formatados = formatar_perfil_rocketreach(raw_person)
        cargo = dados_formatados.get("cargo", "")

        # Filtro estrito de ICP elétrico
        if cargo and not validar_cargo_icp_eletrico(cargo):
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": (
                    f"⚠️ Perfil de '{dados_formatados.get('nome_completo')}' descartado: Cargo '{cargo}' "
                    "não pertence à área de Gerenciamento Elétrico / Sistemas de Potência."
                ),
                "dados": None,
                "erro": "ICP_DISQUALIFIED"
            }

        msg = f"Perfil '{dados_formatados['nome_completo']}' localizado no RocketReach!"
        if dados_formatados["email_principal"]:
            msg += f" E-mail verificado: {dados_formatados['email_principal']}"
        if dados_formatados["telefones_formatados"]:
            msg += f" ({len(dados_formatados['telefones_formatados'])} telefone(s))"

        return {
            "sucesso": True,
            "encontrado": True,
            "mensagem": msg,
            "dados": dados_formatados,
            "erro": None
        }

    except Exception as exc:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro na conexão com RocketReach: {str(exc)}",
            "dados": None,
            "erro": "CONNECTION_ERROR"
        }

def buscar_decisores_rocketreach(
    empresa: str,
    cargos: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Busca de decisores elétricos na empresa via RocketReach API v2 person/search.
    Filtra estritamente os perfis retornados através de validar_cargo_icp_eletrico().
    """
    if eh_empresa_bloqueada(empresa):
        return {
            "sucesso": False,
            "encontrados": [],
            "mensagem": "Busca bloqueada: O domínio sma-eng.com.br não deve ser prospectado.",
            "erro": "BLOCKED_DOMAIN"
        }

    key = (api_key or ROCKETREACH_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrados": [],
            "mensagem": "Chave ROCKETREACH_API_KEY não configurada no ambiente (.env).",
            "erro": "MISSING_API_KEY"
        }

    empresa_limpa = empresa.split(" - ")[0].strip()
    cargos_busca = cargos or CARGOS_PADRAO_ROCKETREACH

    payload = {
        "query": {
            "current_employer": [empresa_limpa],
            "title": cargos_busca
        },
        "page_size": 5
    }

    try:
        url = f"{ROCKETREACH_API_BASE}/person/search"
        headers = get_rocketreach_headers(key)
        resp = requests.post(url, json=payload, headers=headers, timeout=15)

        if resp.status_code == 401:
            texto_erro = resp.text.lower()
            if "verify your email" in texto_erro:
                return {
                    "sucesso": False,
                    "encontrados": [],
                    "mensagem": "A conta RocketReach precisa ter o e-mail confirmado para liberar o uso da API.",
                    "erro": "EMAIL_VERIFICATION_PENDING"
                }
            return {
                "sucesso": False,
                "encontrados": [],
                "mensagem": f"Erro de autenticação RocketReach (HTTP 401): {resp.text[:150]}",
                "erro": "AUTH_ERROR"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrados": [],
                "mensagem": f"Falha na busca RocketReach (HTTP {resp.status_code}): {resp.text[:150]}",
                "erro": f"HTTP_{resp.status_code}"
            }

        res_json = resp.json()
        pessoas_raw = res_json.get("people", [])
        aprovados_icp = []

        for p in pessoas_raw:
            cargo = p.get("current_title") or p.get("title") or ""
            if validar_cargo_icp_eletrico(cargo):
                aprovados_icp.append(formatar_perfil_rocketreach(p))

        if not aprovados_icp:
            return {
                "sucesso": True,
                "encontrados": [],
                "total_bruto": len(pessoas_raw),
                "mensagem": f"Nenhum perfil da área elétrica aprovado no ICP para '{empresa_limpa}' no RocketReach.",
                "erro": "NO_ICP_MATCH"
            }

        return {
            "sucesso": True,
            "encontrados": aprovados_icp,
            "total_bruto": len(pessoas_raw),
            "mensagem": f"{len(aprovados_icp)} decisor(es) de gestão elétrica localizados no RocketReach!",
            "erro": None
        }

    except Exception as exc:
        return {
            "sucesso": False,
            "encontrados": [],
            "mensagem": f"Erro ao buscar decisores no RocketReach: {str(exc)}",
            "erro": "CONNECTION_ERROR"
        }

def enriquecer_lead_com_rocketreach(
    lead: Dict[str, Any],
    linkedin_url: Optional[str] = None,
    nome_completo: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enriquece um lead da fila de oportunidades da KR Engenharia via RocketReach API.
    Aplica filtro estrito de ICP elétrico para evitar perfis inadequados.
    """
    empresa = lead.get("empresa", "")
    resultado = consultar_perfil_rocketreach(
        linkedin_url=linkedin_url or lead.get("linkedin_contato"),
        nome=nome_completo or lead.get("contato_nome"),
        empresa=empresa,
        api_key=api_key
    )

    if resultado.get("encontrado") and resultado.get("dados"):
        dados = resultado["dados"]
        email = dados.get("email_principal")
        telefones = dados.get("telefones_formatados", [])

        lead["contato_nome"] = dados.get("nome_completo") or lead.get("contato_nome", "")
        if dados.get("cargo"):
            lead["cargo_real"] = dados.get("cargo")
        if email:
            lead["email_destinatario"] = email
        if telefones:
            lead["telefones_contato"] = telefones
        if dados.get("linkedin_url"):
            lead["linkedin_contato"] = dados.get("linkedin_url")
        if dados.get("cidade"):
            lead["cidade"] = dados.get("cidade")
        if dados.get("estado"):
            lead["estado"] = dados.get("estado")

        lead["rocketreach_enriquecido"] = True
        lead["tipo_lead"] = "NOMINAL_VERIFICADO"

    return {
        "sucesso": resultado.get("sucesso", False),
        "encontrado": resultado.get("encontrado", False),
        "mensagem": resultado.get("mensagem", ""),
        "erro": resultado.get("erro"),
        "lead": lead,
        "dados_rocketreach": resultado.get("dados")
    }

