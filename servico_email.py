import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional, List, Dict

from config import SMTP_CONFIG, CONTAS_FUNCIONARIOS, DADOS_EMPRESA

def gerar_assinatura_email(funcionario_info: dict) -> str:
    """Gera a assinatura técnica padrão em texto puro e HTML."""
    nome = funcionario_info.get("nome", "Especialista")
    cargo = funcionario_info.get("cargo", "Engenharia")
    email = funcionario_info.get("email", DADOS_EMPRESA["email"])
    
    assinatura_texto = f"""
--
{nome}
{cargo}
{DADOS_EMPRESA['razao_social']}
Contato: {email} | {DADOS_EMPRESA['website']}
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']})
"""
    return assinatura_texto

def testar_conexao_smtp(funcionario_id: str = "LUCAS") -> Dict[str, any]:
    """Testa a conexão e autenticação com o servidor SMTP Titan para um funcionário."""
    conta = CONTAS_FUNCIONARIOS.get(funcionario_id)
    if not conta or not conta.get("email") or not conta.get("senha"):
        return {
            "sucesso": False,
            "motivo": f"Credenciais não encontradas ou incompletas para o funcionário {funcionario_id}."
        }

    email = conta["email"]
    senha = conta["senha"]
    host = SMTP_CONFIG["host"]
    port_ssl = SMTP_CONFIG["port"]
    port_tls = SMTP_CONFIG["port_tls"]

    # Tentativa 1: SSL na porta 465
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port_ssl, context=context, timeout=12) as server:
            server.login(email, senha)
            return {
                "sucesso": True,
                "modo": "SSL (Porta 465)",
                "mensagem": f"Conexão SMTP autenticada com sucesso para {email}."
            }
    except Exception as err_ssl:
        msg_ssl = str(err_ssl)
        
        # Tentativa 2: STARTTLS na porta 587
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port_tls, timeout=12) as server:
                server.starttls(context=context)
                server.login(email, senha)
                return {
                    "sucesso": True,
                    "modo": "STARTTLS (Porta 587)",
                    "mensagem": f"Conexão SMTP autenticada com sucesso para {email}."
                }
        except Exception as err_tls:
            diagnostico = str(err_tls)
            dica = "Verifique se a caixa postal já foi criada no painel Titan e se o acesso SMTP/IMAP externo foi liberado."
            if "authentication failed" in diagnostico.lower() or "535" in diagnostico:
                dica = (
                    "Erro de autenticação no Titan. "
                    "1. Confirme se a conta já foi ativada acessando o webmail (https://mail.titan.email). "
                    "2. No painel de controle Titan/Hostinger, certifique-se de que o acesso a aplicativos externos (IMAP/SMTP) está habilitado para esta caixa postal."
                )

            return {
                "sucesso": False,
                "motivo": diagnostico,
                "dica": dica
            }

def enviar_email_funcionario(
    funcionario_id: str,
    destinatario: str,
    assunto: str,
    corpo_texto: str,
    corpo_html: Optional[str] = None,
    anexos: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Envia um e-mail a partir da caixa postal corporativa oficial de um funcionário de IA.
    """
    conta = CONTAS_FUNCIONARIOS.get(funcionario_id)
    if not conta:
        return {"sucesso": False, "erro": f"Funcionário '{funcionario_id}' não cadastrado."}
    
    remetente_email = conta["email"]
    remetente_senha = conta["senha"]
    remetente_nome = conta["nome"]

    if not remetente_email or not remetente_senha:
        return {
            "sucesso": False,
            "erro": f"E-mail ou senha ausentes para {remetente_nome} ({funcionario_id}). Verifique o .env."
        }

    # Monta a mensagem MIME
    msg = MIMEMultipart("mixed")
    msg["Subject"] = assunto
    msg["From"] = f"{remetente_nome} | {DADOS_EMPRESA['nome_fantasia']} <{remetente_email}>"
    msg["To"] = destinatario
    msg["Reply-To"] = remetente_email

    # Anexa o corpo com a assinatura corporativa
    assinatura = gerar_assinatura_email(conta)
    corpo_completo_texto = corpo_texto.strip() + "\n" + assinatura

    parte_conteudo = MIMEMultipart("alternative")
    parte_conteudo.attach(MIMEText(corpo_completo_texto, "plain", "utf-8"))

    if corpo_html:
        corpo_completo_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 11pt; color: #2d3748; line-height: 1.6;">
            {corpo_html}
            <br><br>
            <hr style="border: 0; border-top: 1px solid #e2e8f0;">
            <div style="font-size: 9pt; color: #718096;">
                <strong>{remetente_nome}</strong> — {conta.get('cargo')}<br>
                <strong>{DADOS_EMPRESA['razao_social']}</strong><br>
                {remetente_email} • <a href="https://{DADOS_EMPRESA['website']}">{DADOS_EMPRESA['website']}</a><br>
                Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']})
            </div>
        </div>
        """
        parte_conteudo.attach(MIMEText(corpo_completo_html, "html", "utf-8"))

    msg.attach(parte_conteudo)

    # Anexos opcionais (ex: PDF de portfólio ou proposta)
    if anexos:
        for caminho_anexo in anexos:
            if os.path.exists(caminho_anexo):
                nome_anexo = os.path.basename(caminho_anexo)
                try:
                    with open(caminho_anexo, "rb") as f:
                        part = MIMEApplication(f.read(), Name=nome_anexo)
                    part['Content-Disposition'] = f'attachment; filename="{nome_anexo}"'
                    msg.attach(part)
                except Exception as e:
                    print(f"⚠️ Erro ao anexar '{caminho_anexo}': {e}")

    # Envio via SMTP Titan
    host = SMTP_CONFIG["host"]
    port_ssl = SMTP_CONFIG["port"]
    port_tls = SMTP_CONFIG["port_tls"]

    # Tentativa com SSL (465)
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port_ssl, context=context, timeout=15) as server:
            server.login(remetente_email, remetente_senha)
            server.send_message(msg)
            return {
                "sucesso": True,
                "remetente": remetente_email,
                "destinatario": destinatario,
                "assunto": assunto,
                "mensagem": f"E-mail enviado com sucesso por {remetente_nome} para {destinatario}!"
            }
    except Exception as err_ssl:
        # Fallback com STARTTLS (587)
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port_tls, timeout=15) as server:
                server.starttls(context=context)
                server.login(remetente_email, remetente_senha)
                server.send_message(msg)
                return {
                    "sucesso": True,
                    "remetente": remetente_email,
                    "destinatario": destinatario,
                    "assunto": assunto,
                    "mensagem": f"E-mail enviado com sucesso por {remetente_nome} para {destinatario} (via porta 587)!"
                }
        except Exception as err_tls:
            return {
                "sucesso": False,
                "remetente": remetente_email,
                "destinatario": destinatario,
                "erro": f"Falha no envio via Titan SMTP: {err_tls} (SSL anterior: {err_ssl})"
            }

if __name__ == "__main__":
    print("==========================================================")
    print("📧 TESTE DO SERVIÇO DE E-MAIL TITAN - FUNCIONÁRIOS KR")
    print("==========================================================")
    
    for fid in CONTAS_FUNCIONARIOS:
        info = CONTAS_FUNCIONARIOS[fid]
        print(f"\n🔍 Testando conexão para {info['nome']} ({info['email']})...")
        res = testar_conexao_smtp(fid)
        if res["sucesso"]:
            print(f"✅ {res['mensagem']}")
        else:
            print(f"❌ Falha: {res['motivo']}")
            print(f"💡 Dica: {res['dica']}")
