import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do .env
load_dotenv()

# Modelo de IA padrão (compatível com a API oficial do Google Gemini)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

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
