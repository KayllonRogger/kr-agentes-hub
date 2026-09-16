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
