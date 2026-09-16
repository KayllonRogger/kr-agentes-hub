import os
import smtplib
import ssl
import imaplib
import email
from email.header import decode_header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional, List, Dict

from config import SMTP_CONFIG, IMAP_CONFIG, CONTAS_FUNCIONARIOS, DADOS_EMPRESA

def gerar_assinatura_html(funcionario_info: dict) -> str:
    """Gera a assinatura corporativa oficial em HTML com a logomarca da KR Engenharia."""
    nome = funcionario_info.get("nome", DADOS_EMPRESA["responsavel_tecnico"])
    cargo = funcionario_info.get("cargo", "Engenharia")
    email_conta = funcionario_info.get("email", DADOS_EMPRESA["email"])
    telefone_exibicao = "+55 (31) 99566-6963"
    telefone_link = "+5531995666963"
    site_url = "https://krconsultoria.com.br"
    logo_url = "https://krconsultoria.com.br/Image/tn_logomarca.jpg"

    if "Kayllon" in nome or cargo == "Diretor Técnico":
        subtitulo_cargo = f"Diretor T&eacute;cnico | {DADOS_EMPRESA['crea']}"
    else:
        subtitulo_cargo = f"{cargo} | KR Engenharia"

    assinatura_html = f"""
<br><br>
<table cellpadding="0" cellspacing="0" border="0" style="font-family: Arial, Helvetica, sans-serif; font-size: 13px; line-height: 1.4; color: rgb(30, 41, 59); border-collapse: collapse; width: 100%; app-region: no-drag !important;" width="100%">
	<tbody valign="middle" style="app-region: no-drag !important;">
		<tr valign="inherit" style="app-region: no-drag !important;">
			<td valign="middle" align="center" style="width: 75px; min-width: 75px; max-width: 75px; padding: 0px 28px 0px 0px; vertical-align: middle; text-align: center; line-height: 0; app-region: no-drag !important;">
				<a href="{site_url}" target="_blank" style="text-decoration: none; display: block; width: 75px; height: 75px; app-region: no-drag !important;"><img src="{logo_url}" alt="KR Engenharia Logo" width="75" height="75" style="display: block; width: 75px; height: 75px; min-width: 75px; min-height: 75px; max-width: 75px; max-height: 75px; border: 0px; outline: none; text-decoration: none; margin: 0px; padding: 0px; app-region: no-drag !important;" data-clarity-loaded="13l56i6"></a></td>
			<td valign="middle" style="width: 2px; min-width: 2px; border-left: 2px solid rgb(15, 61, 100); padding: 0px 0px 0px 20px; vertical-align: middle; app-region: no-drag !important;">

				<table cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse; width: 100%; app-region: no-drag !important;" width="100%">
					<tbody valign="middle" style="app-region: no-drag !important;">
						<tr valign="inherit" style="app-region: no-drag !important;">
							<td style="padding-bottom: 2px; white-space: nowrap; app-region: no-drag !important;" valign="inherit"><span style="font-size: 16px; font-weight: bold; color: rgb(15, 23, 42); letter-spacing: -0.2px; app-region: no-drag !important;">{nome}</span></td>
						</tr>
						<tr valign="inherit" style="app-region: no-drag !important;">
							<td style="padding-bottom: 8px; white-space: nowrap; app-region: no-drag !important;" valign="inherit"><span style="font-size: 13px; font-weight: 600; color: rgb(15, 61, 100); app-region: no-drag !important;">{subtitulo_cargo}</span></td>
						</tr>
						<tr valign="inherit" style="border-top: 1px solid rgb(226, 232, 240); padding-top: 8px; padding-bottom: 5px; white-space: nowrap; app-region: no-drag !important;">
							<td style="border-top: 1px solid rgb(226, 232, 240); padding-top: 8px; padding-bottom: 5px; white-space: nowrap; app-region: no-drag !important;" valign="inherit"><span style="font-size: 12px; font-weight: bold; color: rgb(30, 41, 59); app-region: no-drag !important;">KR Engenharia</span> <span style="font-size: 12px; color: rgb(100, 116, 139); app-region: no-drag !important;">&nbsp;&mdash; Consultoria e Solu&ccedil;&otilde;es em Engenharia LTDA</span></td>
						</tr>
						<tr valign="inherit" style="app-region: no-drag !important;">
							<td style="font-size: 12px; color: rgb(51, 65, 85); line-height: 1.5; white-space: nowrap; app-region: no-drag !important;" valign="inherit"><span style="white-space: nowrap; app-region: no-drag !important;"><strong style="color: rgb(15, 61, 100); app-region: no-drag !important;">T:</strong> <a href="tel:{telefone_link}" style="color: rgb(51, 65, 85); text-decoration: none; app-region: no-drag !important;">{telefone_exibicao}</a></span> <span style="color: rgb(203, 213, 225); margin: 0px 8px; app-region: no-drag !important;">|</span> <span style="white-space: nowrap; app-region: no-drag !important;"><strong style="color: rgb(15, 61, 100); app-region: no-drag !important;">E:</strong> <a href="mailto:{email_conta}" style="color: rgb(15, 61, 100); text-decoration: none; font-weight: 500; app-region: no-drag !important;">{email_conta}</a></span> <span style="color: rgb(203, 213, 225); margin: 0px 8px; app-region: no-drag !important;">|</span>&nbsp;
								<br style="app-region: no-drag !important;"><span style="white-space: nowrap; app-region: no-drag !important;"><strong style="color: rgb(15, 61, 100); app-region: no-drag !important;">W:</strong> <a href="{site_url}" target="_blank" style="color: rgb(15, 61, 100); text-decoration: none; font-weight: 500; app-region: no-drag !important;">krconsultoria.com.br</a></span></td>
						</tr>
					</tbody>
				</table>
			</td>
		</tr>
	</tbody>
</table>
"""
    return assinatura_html.strip()

def gerar_assinatura_texto(funcionario_info: dict) -> str:
    """Gera a assinatura técnica padrão em texto puro (fallback)."""
    nome = funcionario_info.get("nome", DADOS_EMPRESA["responsavel_tecnico"])
    cargo = funcionario_info.get("cargo", "Engenharia")
    email_conta = funcionario_info.get("email", DADOS_EMPRESA["email"])
    
    return f"""
--
{nome}
{cargo}
{DADOS_EMPRESA['razao_social']}
T: +55 (31) 99566-6963 | E: {email_conta} | W: {DADOS_EMPRESA['website']}
Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']})
""".strip()

def testar_conexao_smtp(funcionario_id: str = "LUCAS") -> Dict[str, any]:
    """Testa a conexão e autenticação com o servidor SMTP Titan para um funcionário."""
    conta = CONTAS_FUNCIONARIOS.get(funcionario_id)
    if not conta or not conta.get("email") or not conta.get("senha"):
        return {
            "sucesso": False,
            "motivo": f"Credenciais não encontradas ou incompletas para o funcionário {funcionario_id}."
        }

    email_user = conta["email"]
    senha = conta["senha"]
    host = SMTP_CONFIG["host"]
    port_ssl = SMTP_CONFIG["port"]
    port_tls = SMTP_CONFIG["port_tls"]

    # Tentativa 1: SSL na porta 465
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port_ssl, context=context, timeout=12) as server:
            server.login(email_user, senha)
            return {
                "sucesso": True,
                "modo": "SSL (Porta 465)",
                "mensagem": f"Conexão SMTP autenticada com sucesso para {email_user}."
            }
    except Exception as err_ssl:
        msg_ssl = str(err_ssl)
        
        # Tentativa 2: STARTTLS na porta 587
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(host, port_tls, timeout=12) as server:
                server.starttls(context=context)
                server.login(email_user, senha)
                return {
                    "sucesso": True,
                    "modo": "STARTTLS (Porta 587)",
                    "mensagem": f"Conexão SMTP autenticada com sucesso para {email_user}."
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

def formatar_corpo_html(texto_conteudo: str) -> str:
    """Converte quebras de linha e texto simples em parágrafos e quebras HTML formatadas."""
    linhas = texto_conteudo.strip().split("\n")
    paragrafos = []
    bloco_atual = []

    for linha in linhas:
        l = linha.strip()
        if not l:
            if bloco_atual:
                paragrafos.append("<p style='margin: 0 0 12px 0;'>" + "<br>".join(bloco_atual) + "</p>")
                bloco_atual = []
        else:
            bloco_atual.append(l)

    if bloco_atual:
        paragrafos.append("<p style='margin: 0 0 12px 0;'>" + "<br>".join(bloco_atual) + "</p>")

    return "\n".join(paragrafos)

def enviar_email_funcionario(
    funcionario_id: str,
    destinatario: str,
    assunto: str,
    corpo_texto: str,
    corpo_html: Optional[str] = None,
    anexos: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Envia um e-mail a partir da caixa postal corporativa oficial de um funcionário de IA,
    incluindo a assinatura oficial com logomarca e dados da KR Engenharia.
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

    # Gera assinaturas oficiais
    assinatura_txt = gerar_assinatura_texto(conta)
    assinatura_htm = gerar_assinatura_html(conta)

    corpo_completo_texto = corpo_texto.strip() + "\n\n" + assinatura_txt

    if corpo_html:
        conteudo_html = corpo_html
    else:
        conteudo_html = formatar_corpo_html(corpo_texto)

    corpo_completo_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, Helvetica, sans-serif; font-size: 13px; color: #1e293b; line-height: 1.5; margin: 0; padding: 10px;">
    <div style="margin-bottom: 25px;">
        {conteudo_html}
    </div>
    {assinatura_htm}
</body>
</html>
"""

    parte_conteudo = MIMEMultipart("alternative")
    parte_conteudo.attach(MIMEText(corpo_completo_texto, "plain", "utf-8"))
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

# =====================================================================
# LEITURA DE CAIXA DE ENTRADA VIA IMAP TITAN
# =====================================================================

def decodificar_cabecalho(cabecalho: str) -> str:
    """Decodifica cabeçalhos RFC 2047 com caracteres especiais (acentos, UTF-8)."""
    if not cabecalho:
        return ""
    pedacos = decode_header(cabecalho)
    texto_total = []
    for parte, codificacao in pedacos:
        if isinstance(parte, bytes):
            texto_total.append(parte.decode(codificacao or "utf-8", errors="replace"))
        else:
            texto_total.append(str(parte))
    return "".join(texto_total)

def extrair_corpo_email(msg) -> str:
    """Extrai texto limpo de uma mensagem recebida (texto puro ou HTML formatado)."""
    corpo = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    corpo = payload.decode(charset, errors="replace")
                    break
            elif content_type == "text/html" and not corpo and "attachment" not in content_disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    corpo = payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            corpo = payload.decode(charset, errors="replace")
    return corpo.strip()

def ler_caixa_entrada(
    funcionario_id: str = "LUCAS",
    limite: int = 5,
    apenas_nao_lidas: bool = False
) -> Dict[str, any]:
    """
    Conecta via IMAP SSL ao servidor Titan e lê as mensagens recebidas na caixa postal do funcionário.
    """
    conta = CONTAS_FUNCIONARIOS.get(funcionario_id)
    if not conta:
        return {"sucesso": False, "erro": f"Funcionário '{funcionario_id}' não cadastrado."}

    email_user = conta["email"]
    senha = conta["senha"]
    host = IMAP_CONFIG["host"]
    port = IMAP_CONFIG["port"]

    if not email_user or not senha:
        return {"sucesso": False, "erro": f"Credenciais ausentes para {email_user}."}

    mensagens_lidas = []

    try:
        context = ssl.create_default_context()
        with imaplib.IMAP4_SSL(host, port, ssl_context=context, timeout=15) as client:
            # Tenta autenticação com SASL PLAIN (suporta caracteres especiais e aspas com segurança)
            try:
                def auth_plain(response):
                    return f"\0{email_user}\0{senha}".encode("utf-8")
                client.authenticate("PLAIN", auth_plain)
            except Exception:
                # Fallback para login padrão
                client.login(email_user, senha)

            client.select("INBOX")

            criterio = "UNSEEN" if apenas_nao_lidas else "ALL"
            status, dados = client.search(None, criterio)
            
            if status != "OK":
                return {"sucesso": False, "erro": "Falha ao buscar mensagens na INBOX."}

            msg_ids = dados[0].split()
            total_mensagens = len(msg_ids)

            # Pega as mensagens mais recentes
            ids_recentes = msg_ids[-limite:] if limite else msg_ids
            ids_recentes.reverse()

            for m_id in ids_recentes:
                status_fetch, dados_fetch = client.fetch(m_id, "(RFC822)")
                if status_fetch != "OK":
                    continue

                for resposta in dados_fetch:
                    if isinstance(resposta, tuple):
                        msg = email.message_from_bytes(resposta[1])
                        
                        remetente = decodificar_cabecalho(msg.get("From", ""))
                        assunto = decodificar_cabecalho(msg.get("Subject", ""))
                        data_envio = msg.get("Date", "")
                        corpo = extrair_corpo_email(msg)

                        mensagens_lidas.append({
                            "id": m_id.decode() if isinstance(m_id, bytes) else str(m_id),
                            "remetente": remetente,
                            "assunto": assunto,
                            "data": data_envio,
                            "corpo": corpo,
                            "trecho": corpo[:250] + ("..." if len(corpo) > 250 else "")
                        })

            return {
                "sucesso": True,
                "funcionario": conta["nome"],
                "email": email_user,
                "total_na_caixa": total_mensagens,
                "mensagens": mensagens_lidas
            }

    except Exception as e:
        return {
            "sucesso": False,
            "funcionario": conta["nome"],
            "email": email_user,
            "erro": f"Falha ao conectar via IMAP: {str(e)}"
        }

def analisar_intencao_resposta(corpo_email: str) -> Dict[str, any]:
    """Analisa o e-mail de um lead/cliente usando IA e classifica a intenção comercial."""
    from utils import get_llm, extrair_texto
    from langchain_core.messages import SystemMessage, HumanMessage

    prompt = """Você é o Analista de Inteligência Comercial da KR Engenharia.
Analise a resposta recebida de um lead ou cliente por e-mail e classifique-a:

CLASSIFICAÇÃO OBRIGATÓRIA (escolha exatamente uma):
- INTERESSE: O cliente demonstrou interesse nos serviços ou quer saber mais.
- AGENDAMENTO: O cliente solicitou uma reunião, conversa ou visita técnica.
- DUVIDA_TECNICA: O cliente fez perguntas sobre normas (IEEE, IEC), estudos no ETAP ou metodologias.
- RECUSA: O cliente informou que não tem interesse ou pediu para descadastrar.
- INFORMATIVO: E-mail de boas-vindas, confirmação automática ou newsletter.
- OUTRO: Qualquer outro assunto.

ESTRUTURA DA RESPOSTA:
1. INTENÇÃO: [Categoria em maiúsculo]
2. RESUMO: [Resumo objetivo em 1 parágrafo da mensagem do cliente]
3. AÇÃO RECOMENDADA: [Qual deve ser o próximo passo comercial ou técnico da KR Engenharia]
4. SUGESTÃO DE RESPOSTA: [Rascunho de resposta técnica e cordial pronto para envio]
"""
    try:
        llm = get_llm(temperature=0.1)
        resp = llm.invoke([
            SystemMessage(content=prompt),
            HumanMessage(content=f"MENSAGEM RECEBIDA DO CLIENTE:\n\n{corpo_email}")
        ])
        return {"sucesso": True, "analise": extrair_texto(resp)}
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}

if __name__ == "__main__":
    print("==========================================================")
    print("📧 PREVIEW DA ASSINATURA OFICIAL KR ENGENHARIA")
    print("==========================================================")
    for fid in CONTAS_FUNCIONARIOS:
        info = CONTAS_FUNCIONARIOS[fid]
        print(f"\n--- {info['nome']} ({fid}) ---")
        print(gerar_assinatura_texto(info))
