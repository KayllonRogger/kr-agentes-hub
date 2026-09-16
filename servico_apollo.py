import os
import urllib.parse
import requests
from typing import Dict, Optional, List, Any
from config import APOLLO_API_KEY, eh_empresa_bloqueada

APOLLO_API_BASE = "https://api.apollo.io/v1"

def get_apollo_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Retorna os cabeçalhos padrão para a API Apollo.io."""
    key = (api_key or APOLLO_API_KEY or "").strip()
    return {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "x-api-key": key
    }

def gerar_link_busca_apollo(empresa: str, cargo: str = "Gerente de Manutenção Elétrica") -> str:
    """Gera link de busca profunda no Apollo Prospector para localização de decisores."""
    nome_limpo = empresa.split(" - ")[0].strip()
    query = urllib.parse.quote(f'site:apollo.io/people "{nome_limpo}" ("{cargo}" OR "Manutenção Elétrica")')
    return f"https://www.google.com/search?q={query}"

def consultar_empresa_apollo(dominio: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Enriquece dados cadastrais, tecnologias e inteligência de mercado de uma empresa via Apollo.io.
    """
    if eh_empresa_bloqueada(dominio):
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Consulta bloqueada: O domínio sma-eng.com.br não deve ser prospectado.",
            "dados": None,
            "erro": "BLOCKED_DOMAIN"
        }

    key = (api_key or APOLLO_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Chave APOLLO_API_KEY não configurada no ambiente (.env).",
            "dados": None,
            "erro": "MISSING_API_KEY"
        }

    dom_limpo = dominio.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()
    if not dom_limpo:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Domínio da empresa inválido.",
            "dados": None,
            "erro": "INVALID_DOMAIN"
        }

    try:
        url = f"{APOLLO_API_BASE}/organizations/enrich"
        headers = get_apollo_headers(key)
        params = {"domain": dom_limpo}
        resp = requests.get(url, params=params, headers=headers, timeout=15)

        if resp.status_code == 401 or resp.status_code == 403:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Erro de autorização Apollo.io (HTTP {resp.status_code}): {resp.text[:150]}",
                "dados": None,
                "erro": "AUTH_ERROR"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Falha na consulta Apollo.io (HTTP {resp.status_code})",
                "dados": None,
                "erro": f"HTTP_{resp.status_code}"
            }

        res_json = resp.json()
        org = res_json.get("organization")
        if not org:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": f"Nenhuma organização encontrada para o domínio '{dom_limpo}' no Apollo.io.",
                "dados": None,
                "erro": "NOT_FOUND"
            }

        dados_formatados = {
            "nome": org.get("name", ""),
            "dominio": dom_limpo,
            "website_url": org.get("website_url", ""),
            "linkedin_url": org.get("linkedin_url", ""),
            "twitter_url": org.get("twitter_url", ""),
            "facebook_url": org.get("facebook_url", ""),
            "funcionarios_estimados": org.get("estimated_num_employees"),
            "setor": org.get("industry", ""),
            "industrias": org.get("industries", []),
            "palavras_chave": org.get("keywords", [])[:10],
            "telefone": org.get("phone", ""),
            "cidade": org.get("city", ""),
            "estado": org.get("state", ""),
            "pais": org.get("country", ""),
            "raw": org
        }

        return {
            "sucesso": True,
            "encontrado": True,
            "mensagem": f"Empresa '{dados_formatados['nome']}' enriquecida com sucesso pelo Apollo.io!",
            "dados": dados_formatados,
            "erro": None
        }

    except Exception as exc:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro na conexão com Apollo.io: {str(exc)}",
            "dados": None,
            "erro": "CONNECTION_ERROR"
        }

def consultar_contato_apollo(
    primeiro_nome: Optional[str] = None,
    ultimo_nome: Optional[str] = None,
    dominio: Optional[str] = None,
    linkedin_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Tenta localizar contato pelo endpoint People Match da Apollo.io.
    Caso a conta seja do plano gratuito, orienta sobre o uso do plano ou sugere o Lusha.
    """
    if dominio and eh_empresa_bloqueada(dominio):
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Consulta bloqueada: O domínio sma-eng.com.br não deve ser prospectado.",
            "dados": None,
            "erro": "BLOCKED_DOMAIN"
        }

    key = (api_key or APOLLO_API_KEY or "").strip()
    if not key:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": "Chave APOLLO_API_KEY não configurada no ambiente (.env).",
            "dados": None,
            "erro": "MISSING_API_KEY"
        }

    payload = {"api_key": key}
    if linkedin_url:
        payload["linkedin_url"] = linkedin_url
    if primeiro_nome:
        payload["first_name"] = primeiro_nome
    if ultimo_nome:
        payload["last_name"] = ultimo_nome
    if dominio:
        payload["domain"] = dominio.replace("http://", "").replace("https://", "").replace("www.", "").split("/")[0].strip()

    try:
        url = f"{APOLLO_API_BASE}/people/match"
        headers = get_apollo_headers(key)
        resp = requests.post(url, json=payload, headers=headers, timeout=15)

        if resp.status_code == 403 and "API_INACCESSIBLE" in resp.text:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": "A API de People Search/Match da Apollo.io requer plano pago ativo. Utilize o enriquecimento pelo Lusha API que já está operacional com créditos.",
                "dados": None,
                "erro": "TIER_RESTRICTION"
            }

        if resp.status_code != 200:
            return {
                "sucesso": False,
                "encontrado": False,
                "mensagem": f"Erro Apollo People Match (HTTP {resp.status_code}): {resp.text[:150]}",
                "dados": None,
                "erro": f"HTTP_{resp.status_code}"
            }

        res_json = resp.json()
        person = res_json.get("person")
        if not person:
            return {
                "sucesso": True,
                "encontrado": False,
                "mensagem": "Pessoa não localizada na base Apollo.io.",
                "dados": None,
                "erro": "NOT_FOUND"
            }

        return {
            "sucesso": True,
            "encontrado": True,
            "mensagem": f"Contato '{person.get('name')}' localizado no Apollo.io!",
            "dados": {
                "nome_completo": person.get("name", ""),
                "cargo": person.get("title", ""),
                "email_principal": person.get("email", ""),
                "linkedin_url": person.get("linkedin_url", ""),
                "empresa": person.get("organization", {}).get("name", ""),
                "telefones_formatados": [f"📞 {person.get('phone_number')}"] if person.get("phone_number") else [],
                "raw": person
            },
            "erro": None
        }
    except Exception as exc:
        return {
            "sucesso": False,
            "encontrado": False,
            "mensagem": f"Erro de conexão com Apollo.io: {str(exc)}",
            "dados": None,
            "erro": "CONNECTION_ERROR"
        }

