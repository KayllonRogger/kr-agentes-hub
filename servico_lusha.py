import os
import requests
from typing import Dict, Optional, List, Any
from config import LUSHA_API_KEY

LUSHA_API_BASE = "https://api.lusha.com/v2"
LUSHA_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_lusha_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Retorna os cabeçalhos HTTP necessários para autenticação e bypass de restrições de User-Agent."""
    key = (api_key or LUSHA_API_KEY or "").strip()
    return {
        "api_key": key,
        "User-Agent": LUSHA_USER_AGENT,
        "Accept": "application/json"
    }

def consultar_contato_lusha(
    linkedin_url: Optional[str] = None,
    primeiro_nome: Optional[str] = None,
    ultimo_nome: Optional[str] = None,
    dominio_empresa: Optional[str] = None,
    email: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Consulta a API v2 da Lusha para obter e-mails corporativos diretos, telefones e cargos reais de decisores.
    Aceita busca por:
      1. linkedinUrl (ex: 'https://www.linkedin.com/in/usuario')
      2. firstName + lastName + companyDomain (ex: 'Carlos', 'Silva', 'vale.com')
      3. email corporativo/pessoal
    """
    key = (api_key or LUSHA_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Chave LUSHA_API_KEY não configurada no ambiente (.env).",
            "dados": None,
            "erro": "MISSING_API_KEY"
        }

    params = {}
    if linkedin_url and "linkedin.com" in linkedin_url.lower():
        # Limpa parâmetros de tracking (ex: ?originalSubdomain=br)
        url_limpa = linkedin_url.split("?")[0].strip()
        params["linkedinUrl"] = url_limpa
    elif primeiro_nome and ultimo_nome and dominio_empresa:
        # Lusha v2 exige companyDomain (não company nem domain)
        dom_limpo = dominio_empresa.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()
        params["firstName"] = primeiro_nome.strip()
        params["lastName"] = ultimo_nome.strip()
        params["companyDomain"] = dom_limpo
    elif email and "@" in email:
        params["email"] = email.strip()
    else:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Parâmetros insuficientes para consulta no Lusha. Forneça o Link do LinkedIn ou Nome + Sobrenome + Domínio da Empresa.",
            "dados": None,
            "erro": "INVALID_PARAMS"
        }

    try:
        url = f"{LUSHA_API_BASE}/person"
        headers = get_lusha_headers(key)
        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 401 or resp.status_code == 403:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Erro de autenticação Lusha API (HTTP {resp.status_code}). Verifique a chave configurada.",
                "dados": None,
                "erro": "AUTH_ERROR"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Falha na consulta à Lusha API (HTTP {resp.status_code}): {resp.text[:200]}",
                "dados": None,
                "erro": f"HTTP_{resp.status_code}"
            }

        resultado_raw = resp.json()
        contact_root = resultado_raw.get("contact", {})
        erro_lusha = contact_root.get("error")
        is_credit_charged = contact_root.get("isCreditCharged", False)

        if erro_lusha:
            nome_erro = erro_lusha.get("name", "EMPTY_DATA")
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": f"Contato não localizado na base do Lusha ({nome_erro}).",
                "credito_cobrado": is_credit_charged,
                "dados": None,
                "erro": nome_erro
            }

        data = contact_root.get("data")
        if not data:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": "Nenhum dado retornado para este perfil no Lusha.",
                "credito_cobrado": is_credit_charged,
                "dados": None,
                "erro": "NO_DATA"
            }

        # Extrai Nome
        primeiro = data.get("firstName", "")
        ultimo = data.get("lastName", "")
        nome_completo = data.get("fullName") or f"{primeiro} {ultimo}".strip()

        # Extrai Cargo
        job_title_obj = data.get("jobTitle", {})
        if isinstance(job_title_obj, dict):
            cargo = job_title_obj.get("title", "")
            departamentos = job_title_obj.get("departments", [])
            senioridade = job_title_obj.get("seniority", "")
        else:
            cargo = str(job_title_obj)
            departamentos = []
            senioridade = ""

        # Extrai Empresa
        company_obj = data.get("company", {})
        empresa_nome = company_obj.get("name", "") if isinstance(company_obj, dict) else ""
        empresa_dominios = company_obj.get("domains", {}) if isinstance(company_obj, dict) else {}
        empresa_dominio = empresa_dominios.get("email") or empresa_dominios.get("homepage", "")

        # Extrai E-mails (Corporativos vs Pessoais)
        emails_trabalho = []
        emails_pessoais = []
        emails_todos = []
        lista_emails_raw = data.get("emailAddresses", [])

        for item in lista_emails_raw:
            if isinstance(item, dict):
                em = item.get("email", "").strip()
                tipo = item.get("emailType", "work")
                status = item.get("status", "")
                if em:
                    emails_todos.append(em)
                    if tipo == "work":
                        emails_trabalho.append(em)
                    else:
                        emails_pessoais.append(em)
            elif isinstance(item, str) and item.strip():
                emails_todos.append(item.strip())
                emails_trabalho.append(item.strip())

        # Extrai Telefones (Móveis e Diretos)
        telefones = []
        telefones_formatados = []
        lista_tel_raw = data.get("phoneNumbers", [])

        for item in lista_tel_raw:
            if isinstance(item, dict):
                num = item.get("number", "").strip()
                tipo = item.get("phoneType", "direct")
                do_not_call = item.get("doNotCall", False)
                if num:
                    telefones.append({
                        "numero": num,
                        "tipo": tipo,
                        "do_not_call": do_not_call
                    })
                    tipo_fmt = "📱 Móvel" if tipo == "mobile" else "📞 Direto"
                    telefones_formatados.append(f"{tipo_fmt}: {num}")
            elif isinstance(item, str) and item.strip():
                telefones.append({"numero": item.strip(), "tipo": "phone", "do_not_call": False})
                telefones_formatados.append(f"📞 {item.strip()}")

        # Extrai Localização
        loc_obj = data.get("location", {})
        cidade = loc_obj.get("city", "") if isinstance(loc_obj, dict) else ""
        estado = loc_obj.get("state", "") if isinstance(loc_obj, dict) else ""
        pais = loc_obj.get("country", "") if isinstance(loc_obj, dict) else ""

        # Social
        social_obj = data.get("socialLinks", {})
        linkedin_retornado = social_obj.get("linkedin", "") if isinstance(social_obj, dict) else ""

        # E-mail Principal Selecionado (Prioriza trabalho corporativo verificado)
        email_principal = emails_trabalho[0] if emails_trabalho else (emails_todos[0] if emails_todos else "")

        dados_formatados = {
            "nome_completo": nome_completo,
            "primeiro_nome": primeiro,
            "ultimo_nome": ultimo,
            "cargo": cargo,
            "departamentos": departamentos,
            "senioridade": senioridade,
            "empresa": empresa_nome,
            "dominio_empresa": empresa_dominio,
            "email_principal": email_principal,
            "emails_trabalho": emails_trabalho,
            "emails_pessoais": emails_pessoais,
            "emails_todos": emails_todos,
            "telefones": telefones,
            "telefones_formatados": telefones_formatados,
            "cidade": cidade,
            "estado": estado,
            "pais": pais,
            "linkedin_url": linkedin_retornado or linkedin_url or "",
            "raw": data
        }

        msg_sucesso = f"Contato '{nome_completo}' localizado com sucesso!"
        if email_principal:
            msg_sucesso += f" E-mail verificado: {email_principal}"
        if telefones_formatados:
            msg_sucesso += f" ({len(telefones_formatados)} telefone(s) disponível(is))"

        return {
            "sucesso": True,
            "encontrado": True,
            "mensagem": msg_sucesso,
            "credito_cobrado": is_credit_charged,
            "dados": dados_formatados,
            "erro": None
        }

    except requests.RequestException as exc:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro de conexão com Lusha API: {str(exc)}",
            "dados": None,
            "erro": "CONNECTION_ERROR"
        }
    except Exception as ex:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro inesperado ao processar dados da Lusha: {str(ex)}",
            "dados": None,
            "erro": "UNEXPECTED_ERROR"
        }

def consultar_empresa_lusha(dominio: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Consulta a API v2 da Lusha para obter dados cadastrais e inteligência de uma empresa pelo seu domínio.
    """
    key = (api_key or LUSHA_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Chave LUSHA_API_KEY não configurada no ambiente (.env).",
            "dados": None
        }

    dom_limpo = dominio.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()
    if not dom_limpo:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Domínio inválido fornecido.",
            "dados": None
        }

    try:
        url = f"{LUSHA_API_BASE}/company"
        params = {"domain": dom_limpo}
        headers = get_lusha_headers(key)
        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Falha na consulta da empresa (HTTP {resp.status_code})",
                "dados": None
            }

        res_json = resp.json()
        data = res_json.get("data")
        if not data:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": f"Empresa com domínio '{dom_limpo}' não localizada no Lusha.",
                "dados": None
            }

        return {
            "sucesso": True,
            "encontrado": True,
            "mensagem": f"Empresa '{data.get('name')}' localizada com sucesso no Lusha!",
            "dados": {
                "nome": data.get("name", ""),
                "dominio": data.get("domain", dom_limpo),
                "dominio_email": data.get("emailDomain", ""),
                "descricao": data.get("description", ""),
                "setor_principal": data.get("mainIndustry", ""),
                "sub_setor": data.get("subIndustry", ""),
                "funcionarios": data.get("employees", ""),
                "website": data.get("website", ""),
                "linkedin_empresa": data.get("social", {}).get("linkedin", {}).get("url", "") if isinstance(data.get("social"), dict) else "",
                "logo_url": data.get("logoUrl", ""),
                "raw": data
            }
        }
    except Exception as exc:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro ao consultar empresa no Lusha: {str(exc)}",
            "dados": None
        }

def enriquecer_lead_com_lusha(
    lead: Dict[str, Any],
    linkedin_url: Optional[str] = None,
    nome_completo: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Enriquece um lead da fila de prospecção da KR Engenharia com contatos verificados pela Lusha API.
    Atualiza automaticamente o e-mail corporativo verificado e telefones, eliminando deduções.
    """
    primeiro_nome = None
    ultimo_nome = None

    if nome_completo and not linkedin_url:
        partes = nome_completo.strip().split()
        if len(partes) >= 2:
            primeiro_nome = partes[0]
            ultimo_nome = " ".join(partes[1:])
        elif len(partes) == 1:
            primeiro_nome = partes[0]
            ultimo_nome = "Silva"

    resultado = consultar_contato_lusha(
        linkedin_url=linkedin_url,
        primeiro_nome=primeiro_nome,
        ultimo_nome=ultimo_nome,
        dominio_empresa=lead.get("dominio"),
        api_key=api_key
    )

    if resultado.get("encontrado") and resultado.get("dados"):
        dados = resultado["dados"]
        email_encontrado = dados.get("email_principal")
        telefones = dados.get("telefones_formatados", [])

        lead["contato_nome"] = dados.get("nome_completo") or lead.get("contato_nome", "")
        if dados.get("cargo"):
            lead["cargo_real"] = dados.get("cargo")
        if email_encontrado:
            lead["email_destinatario"] = email_encontrado
        if telefones:
            lead["telefones_contato"] = telefones
        if dados.get("linkedin_url"):
            lead["linkedin_contato"] = dados.get("linkedin_url")

        lead["lusha_enriquecido"] = True
        lead["lusha_status"] = "ENRIQUECIDO"
        lead["lusha_info"] = {
            "emails_encontrados": dados.get("emails_todos", []),
            "emails_trabalho": dados.get("emails_trabalho", []),
            "telefones": telefones,
            "cidade": dados.get("cidade", ""),
            "estado": dados.get("estado", "")
        }

    return {
        "sucesso": resultado.get("sucesso", False),
        "encontrado": resultado.get("encontrado", False),
        "mensagem": resultado.get("mensagem", ""),
        "lead": lead,
        "dados_lusha": resultado.get("dados")
    }

