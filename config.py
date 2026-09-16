import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Modelo de IA padrão (recomendado pela API oficial do Google Gemini)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

# Credenciais de acesso ao painel
APP_USUARIO = os.getenv("APP_USUARIO", "admin")
APP_SENHA = os.getenv("APP_SENHA", "kr2026")

# Verificação básica de chave de API
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("⚠️ [AVISO] GOOGLE_API_KEY não encontrada nas variáveis de ambiente. Verifique o arquivo .env.")

# Chaves de API das plataformas B2B de Prospecção
LUSHA_API_KEY = os.getenv("LUSHA_API_KEY", "")
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY", "")

# Lista de Restrição Institucional / Blacklist de Prospecção
# REGRA INVIOLÁVEL: A empresa SM&A NUNCA deve ser contactada para prospecção de clientes.
EMPRESAS_BLOQUEADAS_PROSPECCAO = [
    "SM&A", "SMA", "SM&A ENGENHARIA", "SM&A CONSULTORIA",
    "SMA ENGENHARIA", "SMA CONSULTORIA", "SMAENG",
    "SMA.ENG.BR", "SMAENGENHARIA.COM.BR"
]

def eh_empresa_bloqueada(texto: str) -> bool:
    """
    Verifica se um nome, razão social, domínio ou e-mail pertence à lista de restrição da KR (ex: SM&A).
    Garante que a SM&A jamais seja incluída em campanhas de prospecção ou receba e-mails outbound.
    """
    if not texto:
        return False
    import re
    txt_lower = texto.lower().strip()
    
    # Domínios ou e-mails bloqueados
    dominios_bloqueados = ["@sma.eng.br", "@smaengenharia.com.br", "sma.eng.br", "smaengenharia.com.br"]
    for dom in dominios_bloqueados:
        if dom in txt_lower:
            return True

    # Padrões com SM&A ou SMA como palavra isolada
    padrao = r"\b(sm&a|sma)\b"
    if re.search(padrao, txt_lower):
        return True

    # Normalizado sem pontuação ou espaços
    normalizado = re.sub(r"[^a-z0-9]", "", txt_lower)
    if "smeae" in normalizado or "smaeng" in normalizado or "smaconsult" in normalizado:
        return True

    return False

# Metadados institucionais centralizados da KR Engenharia
DADOS_EMPRESA = {
    "razao_social": "KR Consultoria e Soluções em Engenharia LTDA",
    "nome_fantasia": "KR Engenharia",
    "responsavel_tecnico": "Eng. Kayllon Rogger Nunes",
    "crea": "CREA-MG nº 141854962-2",
    "cidade": "Belo Horizonte - MG",
    "website": "www.krconsultoria.com.br",
    "email": "kayllon@krconsultoria.com.br",
    "especialidades": (
        "Sistemas de Potência (até 500 kV), Proteção e Seletividade (ETAP), "
        "Automação de Subestações (SAS / IEC 61850) e Comissionamento de Campo (TAF/TAC)"
    ),
    "posicionamento": (
        "Boutique Técnica em Sistemas de Potência, Proteção (ETAP), "
        "Automação de Subestações (SAS / IEC 61850) e Comissionamento (TAF/TAC)"
    )
}

# Configurações do servidor SMTP Titan
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.titan.email"),
    "port": int(os.getenv("SMTP_PORT", "465")),
    "port_tls": int(os.getenv("SMTP_PORT_TLS", "587")),
}

# Configurações do servidor IMAP Titan (Leitura de Caixa de Entrada)
IMAP_CONFIG = {
    "host": os.getenv("IMAP_HOST", "imap.titan.email"),
    "port": int(os.getenv("IMAP_PORT", "993")),
}

# Credenciais dos Funcionários Autônomos de IA
CONTAS_FUNCIONARIOS = {
    "LUCAS": {
        "email": os.getenv("EMAIL_LUCAS", "lucas.campos@krconsultoria.com.br"),
        "senha": os.getenv("SENHA_LUCAS", ""),
        "nome": "Lucas Campos",
        "cargo": "Analista de Inteligência Comercial (SDR)",
        "departamento": "Vendas & Prospecção"
    },
    "MARIANA": {
        "email": os.getenv("EMAIL_MARIANA", "mariana.esteves@krconsultoria.com.br"),
        "senha": os.getenv("SENHA_MARIANA", ""),
        "nome": "Mariana Esteves",
        "cargo": "Especialista em Marketing Técnico",
        "departamento": "Marketing"
    },
    "RAFAEL": {
        "email": os.getenv("EMAIL_RAFAEL", "rafael.gomes@krconsultoria.com.br"),
        "senha": os.getenv("SENHA_RAFAEL", ""),
        "nome": "Eng. Rafael Gomes",
        "cargo": "Especialista em Proteção e Estudos Elétricos",
        "departamento": "Engenharia de Proteção"
    },
    "CARLOS": {
        "email": os.getenv("EMAIL_CARLOS", "carlos.tenaglia@krconsultoria.com.br"),
        "senha": os.getenv("SENHA_CARLOS", ""),
        "nome": "Eng. Carlos Tenaglia",
        "cargo": "Coordenador de Comissionamento e Campo",
        "departamento": "Comissionamento & Campo"
    },
    "BEATRIZ": {
        "email": os.getenv("EMAIL_BEATRIZ", "beatriz.silveira@krconsultoria.com.br"),
        "senha": os.getenv("SENHA_BEATRIZ", ""),
        "nome": "Beatriz Silveira",
        "cargo": "Customer Success & Gestão Contratual",
        "departamento": "Sucesso do Cliente"
    }
}
