import os
import shutil
from typing import Dict, List
from PIL import Image

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm

from config import DADOS_EMPRESA

PASTA_DOCUMENTOS = "documentos"
ARQUIVO_LOGO = "assets/logo.png"
ARQUIVO_LOGO_HEADER = "assets/logo_header.png"
ARQUIVO_WATERMARK = "assets/watermark.png"

# Paleta de Cores Corporativas KR Engenharia
COR_NAVY = colors.HexColor("#0f3d64")
COR_AMBER = colors.HexColor("#c26510")
COR_TEXTO = colors.HexColor("#1e293b")
COR_MUTED = colors.HexColor("#64748b")
COR_LINHA = colors.HexColor("#e2e8f0")
COR_FUNDO = colors.HexColor("#f8fafc")
COR_AZUL_CLARO = colors.HexColor("#e0f2fe")

def garantir_recursos_graficos():
    """Gera versões otimizadas da marca d'água e logo de cabeçalho."""
    os.makedirs("assets", exist_ok=True)
    if os.path.exists(ARQUIVO_LOGO):
        # 1. Marca d'água otimizada com 8% de opacidade
        if not os.path.exists(ARQUIVO_WATERMARK):
            im = Image.open(ARQUIVO_LOGO).convert("RGBA")
            im_wm = im.resize((600, 523), Image.Resampling.LANCZOS)
            alpha = im_wm.split()[3]
            alpha = alpha.point(lambda p: int(p * 0.08))
            im_wm.putalpha(alpha)
            im_wm.save(ARQUIVO_WATERMARK, "PNG", optimize=True)

        # 2. Logo para o cabeçalho
        if not os.path.exists(ARQUIVO_LOGO_HEADER):
            im = Image.open(ARQUIVO_LOGO)
            im_hdr = im.resize((200, 175), Image.Resampling.LANCZOS)
            im_hdr.save(ARQUIVO_LOGO_HEADER, "PNG", optimize=True)

def desenhar_decoracao_pagina(canvas_obj, doc, tipo_documento: str = "portfolio"):
    """Desenha a marca d'água de fundo, o cabeçalho oficial e o rodapé da página."""
    width, height = A4
    canvas_obj.saveState()

    garantir_recursos_graficos()

    # 1. Marca d'água no centro da página
    if os.path.exists(ARQUIVO_WATERMARK):
        wm_w = 340
        wm_h = 296
        wm_x = (width - wm_w) / 2 + 30
        wm_y = (height - wm_h) / 2 - 20
        canvas_obj.drawImage(ARQUIVO_WATERMARK, wm_x, wm_y, width=wm_w, height=wm_h, mask="auto")

    # 2. Cabeçalho Corporativo Superior Direito
    logo_hdr = ARQUIVO_LOGO_HEADER if os.path.exists(ARQUIVO_LOGO_HEADER) else ARQUIVO_LOGO
    if os.path.exists(logo_hdr):
        canvas_obj.drawImage(logo_hdr, width - 54 - 36, height - 52, width=36, height=31, mask="auto")

    canvas_obj.setFont("Helvetica-Bold", 10)
    canvas_obj.setFillColor(COR_NAVY)
    canvas_obj.drawRightString(width - 54 - 42, height - 36, "KR ENGENHARIA")

    canvas_obj.setFont("Helvetica-Bold", 7.5)
    canvas_obj.setFillColor(COR_AMBER)
    if tipo_documento == "portfolio":
        canvas_obj.drawRightString(width - 54 - 42, height - 46, "ELÉTRICA, AUTOMAÇÃO & SAS")
    else:
        canvas_obj.drawRightString(width - 54 - 42, height - 46, "SISTEMAS DE POTÊNCIA & PROTEÇÃO")

    # Linha divisória do cabeçalho
    canvas_obj.setStrokeColor(COR_LINHA)
    canvas_obj.setLineWidth(0.75)
    canvas_obj.line(54, height - 58, width - 54, height - 58)

    # 3. Rodapé
    canvas_obj.line(54, 45, width - 54, 45)
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(COR_MUTED)
    canvas_obj.drawString(54, 32, "KR Engenharia • www.krconsultoria.com.br • Belo Horizonte, MG")

    # Número da página
    canvas_obj.setFont("Helvetica-Bold", 9)
    canvas_obj.setFillColor(COR_NAVY)
    canvas_obj.drawRightString(width - 54, 32, str(canvas_obj.getPageNumber()))

    canvas_obj.restoreState()

# =====================================================================
# 1. GERADOR DO PORTFÓLIO CORPORATIVO OFICIAL EM PDF (3 PÁGINAS)
# =====================================================================

def gerar_portfolio_corporativo_pdf(caminho_saida: str) -> str:
    """
    Gera o Portfólio Corporativo Oficial da KR Engenharia em PDF,
    reproduzindo fidedignamente o documento oficial de 3 páginas.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=68,
        bottomMargin=58
    )

    styles = getSampleStyleSheet()

    # Estilos customizados
    s_titulo = ParagraphStyle(
        "KR_Titulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COR_NAVY,
        spaceAfter=4
    )

    s_subtitulo = ParagraphStyle(
        "KR_Subtitulo",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=COR_NAVY,
        spaceAfter=4
    )

    s_tagline = ParagraphStyle(
        "KR_Tagline",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=COR_MUTED,
        spaceAfter=14
    )

    s_secao = ParagraphStyle(
        "KR_Secao",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=COR_NAVY,
        spaceBefore=10,
        spaceAfter=6
    )

    s_subsecao = ParagraphStyle(
        "KR_Subsecao",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=COR_AMBER,
        spaceBefore=6,
        spaceAfter=4
    )

    s_corpo = ParagraphStyle(
        "KR_Corpo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.2,
        leading=13.5,
        textColor=COR_TEXTO,
        spaceAfter=6
    )

    s_bullet = ParagraphStyle(
        "KR_Bullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.0,
        textColor=COR_TEXTO,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    s_num_item = ParagraphStyle(
        "KR_NumItem",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.2,
        textColor=COR_TEXTO,
        leftIndent=14,
        firstLineIndent=-14,
        spaceAfter=6
    )

    story = []

    # -------------------------------------------------------------
    # PÁGINA 1
    # -------------------------------------------------------------
    story.append(Paragraph("KR ENGENHARIA", s_titulo))
    story.append(Paragraph("Portfólio Corporativo de Engenharia Elétrica e Sistemas de Automação de Subestações (SAS)", s_subtitulo))
    story.append(Paragraph("Belo Horizonte, MG | Estudos Elétricos, Proteção, Comissionamento e Redes IEC 61850", s_tagline))

    story.append(Paragraph("1. Apresentação Institucional e Modelo de Atuação", s_secao))
    story.append(Paragraph(
        "Sob a direção técnica do Eng. Kayllon Rogger Nunes, a KR Engenharia posiciona-se no mercado como uma "
        "\"Consultoria Técnica Especialista (Boutique de Engenharia)\". Nosso modelo de negócio foca no atendimento e condução "
        "direta pelo especialista sênior responsável técnico, o que garante rigor normativo, agilidade, zero ruído de comunicação e "
        "responsabilidade direta pela execução de cada projeto.",
        s_corpo
    ))
    story.append(Paragraph(
        "A empresa possui histórico comprovado em projetos de alta tensão no Brasil, com forte atuação em Minas Gerais, Pará e Ceará, "
        "além de consolidada experiência em operações internacionais de infraestrutura crítica na Polônia e nos Estados Unidos.",
        s_corpo
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("2. Áreas de Expertise", s_secao))

    story.append(Paragraph("2.1. Estudos Elétricos e Proteção", s_subsecao))
    story.append(Paragraph("• Modelagem rigorosa de sistemas elétricos (curto-circuito, fluxo de potência, coordenação e seletividade) utilizando o software ETAP.", s_bullet))
    story.append(Paragraph("• Desenvolvimento de esquemas críticos de Rejeição de Carga (Load Shedding) para garantir a estabilidade de geradores industriais.", s_bullet))
    story.append(Paragraph("• Estruturação de diagramas lógicos funcionais avançados para documentação técnica de alta precisão.", s_bullet))

    story.append(Paragraph("2.2. Automação de Subestações (SAS)", s_subsecao))
    story.append(Paragraph("• Desenho de arquiteturas de redes baseadas na norma IEC 61850 (GOOSE e MMS) e protocolo DNP 3.0.", s_bullet))
    story.append(Paragraph("• Parametrização avançada de IEDs multimarcas e controladores de bay (BCUs), com mapeamento e integração total a sistemas SCADA e supervisórios industriais.", s_bullet))

    story.append(Paragraph("2.3. Comissionamento e Campo", s_subsecao))
    story.append(Paragraph("• Execução de Testes de Aceitação em Fábrica (TAF) e em Campo (TAC) com rigor normativo.", s_bullet))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # PÁGINA 2
    # -------------------------------------------------------------
    story.append(Paragraph("• Inspeção física e comissionamento de cubículos de média e alta tensão e validação de intertravamentos.", s_bullet))
    story.append(Paragraph("• Injeção secundária de relés com malas microprocessadas e emissão de DataBook As-Built com recolhimento de ART.", s_bullet))

    story.append(Spacer(1, 6))
    story.append(Paragraph("3. Tecnologias, Normas e Instrumental Dominados", s_secao))

    # Tabela de Tecnologias e Instrumental
    dados_tabela = [
        [
            Paragraph("<b>Categoria</b>", ParagraphStyle("TH", parent=s_corpo, textColor=colors.white, fontName="Helvetica-Bold", fontSize=9)),
            Paragraph("<b>Domínio Técnico</b>", ParagraphStyle("TH", parent=s_corpo, textColor=colors.white, fontName="Helvetica-Bold", fontSize=9)),
            Paragraph("<b>Instrumental e Observações</b>", ParagraphStyle("TH", parent=s_corpo, textColor=colors.white, fontName="Helvetica-Bold", fontSize=9))
        ],
        [
            Paragraph("<b>Softwares</b>", s_corpo),
            Paragraph("ETAP, AutoCAD", s_corpo),
            Paragraph("Modelagem, projeto e diagramação lógica.", s_corpo)
        ],
        [
            Paragraph("<b>Protocolos</b>", s_corpo),
            Paragraph("IEC 61850 (Ed. 1 e 2), DNP 3.0, Modbus TCP/RTU", s_corpo),
            Paragraph("Integração e arquitetura de redes SAS.", s_corpo)
        ],
        [
            Paragraph("<b>Hardware (IEDs)</b>", s_corpo),
            Paragraph("SEL, Siemens, Schneider, ABB, SYMAP, GE", s_corpo),
            Paragraph("Parametrização avançada multimarcas.", s_corpo)
        ],
        [
            Paragraph("<b>Instrumental</b>", s_corpo),
            Paragraph("Malas de injeção (Omicron, Doble, Conprove), Megômetros, Microhmímetros", s_corpo),
            Paragraph("Certificado RBC vigente mobilizado conforme demanda.", s_corpo)
        ]
    ]

    tabela = Table(dados_tabela, colWidths=[95, 175, 217])
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COR_NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, COR_LINHA),
    ]))
    story.append(tabela)

    story.append(Spacer(1, 6))
    story.append(Paragraph("4. Casos Reais de Destaque e Histórico de Projetos", s_secao))
    story.append(Paragraph("• <b>Baltic Power (Polônia):</b> Comissionamento de proteção e controle (RET670, C264) para subestações GIS de 230/400 kV em offshore wind.", s_bullet))
    story.append(Paragraph("• <b>NavShip (EUA):</b> Comissionamento de geração e propulsão com rede em anel e relés SYMAP para suporte eólico offshore.", s_bullet))
    story.append(Paragraph("• <b>Vale S.A. (Brasil):</b> Retrofit de proteção GE para SEL em subestação 230/13,8 kV e validação de paralelismo de transformadores.", s_bullet))
    story.append(Paragraph("• <b>Gerdau Aços Longos (Brasil):</b> Expansão de laminação, parametrização SIPROTEC 5, integração WinCC e ensaios em transformadores de 345 kV.", s_bullet))

    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Metodologia de Trabalho Exclusiva (Foco em Redução de Downtime)", s_secao))
    story.append(Paragraph(
        "<b>1. Avaliação Preliminar e Engenharia Básica:</b> Imersão imediata no projeto do cliente, realizando levantamento de dados precisos em campo ou via documentação existente para modelagem inicial sólida.",
        s_num_item
    ))

    story.append(PageBreak())

    # -------------------------------------------------------------
    # PÁGINA 3
    # -------------------------------------------------------------
    story.append(Paragraph(
        "<b>2. Desenvolvimento e Parametrização em Laboratório:</b> Simulação intensa para validação prévia, reduzindo em até 40% o tempo de máquina parada no site do cliente.",
        s_num_item
    ))
    story.append(Paragraph(
        "<b>3. Validação e TAF:</b> Realização de testes de plataforma intensivos para atestar a sintonia e o correto funcionamento dos arquivos de configuração e das lógicas de automação antes de qualquer intervenção a campo.",
        s_num_item
    ))
    story.append(Paragraph(
        "<b>4. Comissionamento Integrado (TAC):</b> Mobilização ágil e altamente eficiente da equipe de engenharia habilitada e certificada para execução técnica no site da obra, unindo agilidade de campo e segurança de procedimentos.",
        s_num_item
    ))
    story.append(Paragraph(
        "<b>5. Entrega e Documentação Definitiva:</b> Disponibilização de um DataBook minucioso e completo, cobrindo todos os relatórios de injeção e teste, parametrizações finais extraídas dos equipamentos e diagramas esquemáticos totalmente atualizados (As-Built).",
        s_num_item
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("6. Dados Institucionais e Contato", s_secao))
    story.append(Paragraph("A KR Engenharia está estruturada para atender plantas industriais, EPCistas e concessionárias com máxima excelência técnica.", s_corpo))

    story.append(Spacer(1, 12))

    # Caixa institucional com dados do diretor e selo digital
    dados_contato_html = f"""<b>KR ENGENHARIA</b><br/>
<font color="#64748b">Razão Social: {DADOS_EMPRESA['razao_social']}</font><br/><br/>
<b>{DADOS_EMPRESA['responsavel_tecnico']} | Diretor Técnico</b><br/>
Engenheiro Eletricista | {DADOS_EMPRESA['crea']}<br/><br/>
<b>E-mail:</b> {DADOS_EMPRESA['email']}<br/>
<b>Website:</b> {DADOS_EMPRESA['website']}<br/>
<b>Localização:</b> {DADOS_EMPRESA['cidade']}
"""

    selo_digital_html = """<font size="7.5" color="#475569">
<b>KR CONSULTORIA E SERVICOS DE ENGENHARIA LTDA</b><br/>
CNPJ: 68.797.626/0001-04<br/>
<i>Assinado de forma digital por KR CONSULTORIA E SERVICOS DE ENGENHARIA LTDA</i><br/>
Certificação & Rigor Normativo CREA-MG<br/>
</font>
"""

    tabela_assinatura = Table([
        [
            Paragraph(dados_contato_html, ParagraphStyle("P_Cont", parent=s_corpo, fontSize=9.0, leading=13)),
            Paragraph(selo_digital_html, ParagraphStyle("P_Selo", parent=s_corpo, fontSize=7.5, leading=11))
        ]
    ], colWidths=[290, 197])

    tabela_assinatura.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BACKGROUND', (0, 0), (0, 0), COR_FUNDO),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#f1f5f9")),
        ('BOX', (0, 0), (0, 0), 0.5, COR_LINHA),
        ('BOX', (1, 0), (1, 0), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(tabela_assinatura)

    # Constrói o PDF com callbacks de cabeçalho, rodapé e marca d'água
    doc.build(
        story,
        onFirstPage=lambda c, d: desenhar_decoracao_pagina(c, d, "portfolio"),
        onLaterPages=lambda c, d: desenhar_decoracao_pagina(c, d, "portfolio")
    )

    return caminho_saida

# =====================================================================
# 2. GERADOR DA CARTA DE APRESENTAÇÃO EXECUTIVA EM PDF (COM MARCA D'ÁGUA)
# =====================================================================

def gerar_carta_apresentacao_pdf(caminho_saida: str) -> str:
    """
    Gera a Carta de Apresentação Executiva em PDF oficial da KR Engenharia,
    contendo a logomarca oficial em marca d'água translúcida no fundo.
    """
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    doc = SimpleDocTemplate(
        caminho_saida,
        pagesize=A4,
        leftMargin=54,
        rightMargin=54,
        topMargin=68,
        bottomMargin=58
    )

    styles = getSampleStyleSheet()

    s_badge = ParagraphStyle(
        "C_Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COR_NAVY,
        spaceAfter=10
    )

    s_destinatario = ParagraphStyle(
        "C_Dest",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=15,
        textColor=COR_NAVY,
        spaceAfter=8
    )

    s_corpo = ParagraphStyle(
        "C_Corpo",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.0,
        textColor=COR_TEXTO,
        spaceAfter=6
    )

    s_highlight = ParagraphStyle(
        "C_Highlight",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.8,
        leading=12.5,
        textColor=COR_NAVY
    )

    s_secao = ParagraphStyle(
        "C_Secao",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=COR_NAVY,
        spaceBefore=8,
        spaceAfter=4
    )

    s_bullet = ParagraphStyle(
        "C_Bullet",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.6,
        leading=12.2,
        textColor=COR_TEXTO,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    story = []

    story.append(Paragraph("<b>APRESENTAÇÃO INSTITUCIONAL & TÉCNICA</b>", s_badge))
    story.append(Paragraph("À Gerência de Manutenção Elétrica, Engenharia e Comissionamento", s_destinatario))
    story.append(Paragraph("Prezados Senhores,", s_corpo))

    story.append(Paragraph(
        f"Apresentamos a <b>{DADOS_EMPRESA['razao_social']}</b>, empresa de engenharia consultiva altamente especializada "
        "em estudos elétricos avançados, automação de subestações e intervenções técnicas de campo em plantas industriais "
        "eletrointensivas e sistemas de transmissão de alta tensão.",
        s_corpo
    ))

    # Box de Destaque - Diferencial de Redução de Downtime
    box_texto = (
        "<b>Diferencial Operacional KR Engenharia:</b><br/>"
        "Nossa metodologia proprietária fundamenta-se na <b>pré-validação em bancada de simulação</b> de todas as lógicas, "
        "mensagens GOOSE e parametrizações de IEDs antes da mobilização a campo, proporcionando <b>redução de até 40% no tempo de parada de planta (downtime)</b> "
        "e assegurando energizações seguras, sem atuações indevidas."
    )
    tabela_box = Table([[Paragraph(box_texto, s_highlight)]], colWidths=[487])
    tabela_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LINELEFT', (0, 0), (0, 0), 3.5, COR_NAVY),
        ('BOX', (0, 0), (-1, -1), 0.5, COR_LINHA),
    ]))
    story.append(tabela_box)
    story.append(Spacer(1, 4))

    story.append(Paragraph("1. Disciplinas e Capacidades Técnicas", s_secao))
    story.append(Paragraph(
        "• <b>Estudos Elétricos de Proteção e Seletividade (Software ETAP):</b> Modelagem completa de curto-circuito, coordenação de sobrecorrente (50/51, 51N, 51V), direcional (67/67N), diferencial de transformador (87T) e barras (87B), com mitigação de disparos indevidos na partida de grandes motores.",
        s_bullet
    ))
    story.append(Paragraph(
        "• <b>Automação de Subestações (SAS / IEC 61850):</b> Parametrização e validação de intertravamentos lógicos via GOOSE e integração SCADA via MMS.",
        s_bullet
    ))
    story.append(Paragraph(
        "• <b>Comissionamento de Campo (TAF / TAC):</b> Injeção secundária em relés de proteção multimarcas (Siemens SIPROTEC 5, SEL, Schneider e ABB) com malas de ensaio microprocessadas e calibração RBC.",
        s_bullet
    ))
    story.append(Paragraph(
        "• <b>Equipamentos Primários:</b> Inspeção e ensaios especializados em transformadores de força, disjuntores e transformadores para instrumentos (TCs e TPs).",
        s_bullet
    ))

    story.append(Paragraph("2. Experiência de Campo e Casos de Referência", s_secao))
    story.append(Paragraph(
        "• <b>Geração Eólica Offshore (Baltic Power 400 kV):</b> Comissionamento e validação de sistemas de controle e proteção de subestações GIS de alta tensão.",
        s_bullet
    ))
    story.append(Paragraph(
        "• <b>Grandes Mineradoras e Siderúrgicas Nacionais:</b> Atuação em retrofits complexos e comissionamento em plantas da Vale S.A. e Gerdau Aços Longos com janelas operacionais restritas.",
        s_bullet
    ))

    story.append(Paragraph("3. Rigor Técnico, ART e Conformidade Normativa", s_secao))
    story.append(Paragraph(
        "Todos os serviços prestados contam com <b>emissão formal de ART perante o CREA-MG</b> e entrega do <b>DataBook As-Built</b> completo com relatórios rastreáveis de teste e parametrizações definitivas.",
        s_corpo
    ))
    story.append(Paragraph(
        "Colocamo-nos à disposição para agendar uma conversa técnica de 15 minutos ou analisar preliminarmente o diagrama unifilar de sua planta.",
        s_corpo
    ))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Atenciosamente,", s_corpo))
    story.append(Paragraph(
        f"<b>{DADOS_EMPRESA['responsavel_tecnico']}</b><br/>"
        f"Diretor Técnico • {DADOS_EMPRESA['crea']}<br/>"
        f"<b>{DADOS_EMPRESA['razao_social']}</b>",
        ParagraphStyle("Ass", parent=s_corpo, fontName="Helvetica", fontSize=9.0, leading=13)
    ))

    doc.build(
        story,
        onFirstPage=lambda c, d: desenhar_decoracao_pagina(c, d, "carta"),
        onLaterPages=lambda c, d: desenhar_decoracao_pagina(c, d, "carta")
    )

    return caminho_saida

# =====================================================================
# 3. VERSÃO HTML DA CARTA DE APRESENTAÇÃO (COM MARCA D'ÁGUA CSS)
# =====================================================================

def gerar_carta_apresentacao_html() -> str:
    """Gera a versão HTML da Carta de Apresentação com marca d'água em CSS para pré-visualização web."""
    logo_url = "https://krconsultoria.com.br/Image/tn_logomarca.jpg"

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Carta de Apresentação Institucional - {DADOS_EMPRESA['nome_fantasia']}</title>
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            color: #1e293b;
            line-height: 1.6;
            margin: 0;
            padding: 40px;
            background-color: #f8fafc;
        }}
        .document-container {{
            max-width: 800px;
            margin: 0 auto;
            background: #ffffff;
            padding: 50px;
            border-radius: 8px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-top: 6px solid #0f3d64;
            position: relative;
            overflow: hidden;
        }}
        .document-container::before {{
            content: "";
            position: absolute;
            top: 50%;
            left: 55%;
            transform: translate(-50%, -50%);
            width: 380px;
            height: 380px;
            background-image: url('{logo_url}');
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            opacity: 0.07;
            pointer-events: none;
            z-index: 0;
        }}
        .content-relative {{
            position: relative;
            z-index: 1;
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 18px;
            margin-bottom: 25px;
        }}
        .header-title h1 {{
            color: #0f3d64;
            font-size: 20pt;
            margin: 0;
            font-weight: 800;
        }}
        .header-title .sub {{
            color: #c26510;
            font-size: 9.5pt;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
        }}
        .logo-img {{
            width: 70px;
            height: 70px;
            border-radius: 4px;
        }}
        .section-title {{
            color: #0f3d64;
            font-size: 12pt;
            font-weight: bold;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .badge {{
            background: #e0f2fe;
            color: #0369a1;
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 9pt;
            display: inline-block;
            margin-bottom: 10px;
        }}
        .highlight-box {{
            background: #f1f5f9;
            border-left: 4px solid #0f3d64;
            padding: 14px;
            margin: 18px 0;
            border-radius: 0 6px 6px 0;
            font-size: 9.5pt;
        }}
        .footer {{
            margin-top: 35px;
            border-top: 1px solid #e2e8f0;
            padding-top: 18px;
            font-size: 9pt;
            color: #64748b;
            text-align: center;
        }}
        ul {{
            padding-left: 18px;
        }}
        li {{
            margin-bottom: 6px;
            font-size: 9.5pt;
        }}
    </style>
</head>
<body>
    <div class="document-container">
        <div class="content-relative">
            <div class="header">
                <div class="header-title">
                    <h1>{DADOS_EMPRESA['nome_fantasia'].upper()}</h1>
                    <div class="sub">Boutique de Engenharia em Sistemas de Potência & Proteção</div>
                </div>
                <img src="{logo_url}" alt="KR Engenharia Logo" class="logo-img">
            </div>

            <div class="badge">APRESENTAÇÃO INSTITUCIONAL & TÉCNICA</div>
            <p><strong>À Gerência de Manutenção Elétrica, Engenharia e Comissionamento</strong></p>

            <p>Prezados Senhores,</p>

            <p>Apresentamos a <strong>{DADOS_EMPRESA['razao_social']}</strong>, empresa especializada na prestação de serviços de engenharia consultiva, estudos elétricos avançados e intervenções de campo em subestações de alta tensão e plantas industriais eletrointensivas.</p>

            <div class="highlight-box">
                <strong>Diferencial Operacional KR Engenharia:</strong><br>
                Nossa metodologia fundamenta-se na <strong>pré-validação em bancada de simulação</strong> de todas as lógicas e parametrizações antes da mobilização a campo, proporcionando <strong>redução de até 40% no tempo de parada de planta (downtime)</strong> e garantindo energizações seguras e sem surpresas.
            </div>

            <div class="section-title">1. DISCIPLINAS E CAPACIDADES TÉCNICAS</div>
            <ul>
                <li><strong>Estudos Elétricos de Proteção e Seletividade (Software ETAP):</strong> Modelagem completa de curto-circuito, coordenação de sobrecorrente (50/51, 51N, 51V), direcional (67/67N), diferencial de transformador (87T) e barras (87B), mitigando atuações indevidas na partida de grandes motores.</li>
                <li><strong>Automação de Subestações (SAS / IEC 61850):</strong> Parametrização e validação de intertravamentos via mensagens GOOSE e integração SCADA via relatórios MMS.</li>
                <li><strong>Comissionamento de Campo (TAF / TAC):</strong> Testes de injeção secundária em relés multimarcas (Siemens SIPROTEC 5, SEL, Schneider e ABB) com malas calibradas RBC.</li>
                <li><strong>Ensaios em Equipamentos Primários:</strong> Transformadores de força, disjuntores e transformadores para instrumentos (TCs e TPs).</li>
            </ul>

            <div class="section-title">2. EXPERIÊNCIA DE CAMPO E CASOS DE REFERÊNCIA</div>
            <ul>
                <li><strong>Geração Eólica Offshore (Baltic Power 400 kV):</strong> Validação de sistemas de controle e proteção de subestações GIS em alta tensão.</li>
                <li><strong>Grandes Mineradoras e Siderúrgicas Nacionais:</strong> Atuação em retrofits complexos e comissionamento em plantas da Vale S.A. e Gerdau Aços Longos com janelas restritas de parada.</li>
            </ul>

            <div class="section-title">3. RIGOR TÉCNICO E CONFORMIDADE</div>
            <p>Todos os projetos contam com emissão formal de <strong>ART perante o CREA-MG</strong> e entrega do <strong>DataBook As-Built</strong> completo com relatórios de ensaio e parametrizações finais.</p>

            <p>Colocamo-nos à inteira disposição para agendar uma reunião técnica de 15 minutos ou analisar preliminarmente o diagrama unifilar de sua planta.</p>

            <br>
            <p>Atenciosamente,</p>
            <p>
                <strong>{DADOS_EMPRESA['responsavel_tecnico']}</strong><br>
                Diretor Técnico • {DADOS_EMPRESA['crea']}<br>
                {DADOS_EMPRESA['razao_social']}
            </p>

            <div class="footer">
                {DADOS_EMPRESA['razao_social']} • {DADOS_EMPRESA['website']} • {DADOS_EMPRESA['email']}<br>
                Contato Executivo: +55 (31) 99566-6963 • {DADOS_EMPRESA['cidade']}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html

# =====================================================================
# 4. COMPILADOR UNIFICADO DE DOCUMENTOS OFICIAIS (PDFS DE ENVIO)
# =====================================================================

def compilar_documentos_institucionais(pasta_destino: str = PASTA_DOCUMENTOS) -> Dict[str, any]:
    """
    Compila os documentos oficiais da KR Engenharia em formato PDF
    prontos para envio em anexo nas mensagens de prospecção do Lucas.
    """
    os.makedirs(pasta_destino, exist_ok=True)
    garantir_recursos_graficos()

    # 1. Portfólio Corporativo Oficial em PDF
    caminho_portfolio_pdf = os.path.join(pasta_destino, "Portfolio_Corporativo_KR_Engenharia.pdf")
    gerar_portfolio_corporativo_pdf(caminho_portfolio_pdf)

    # Cria também link/cópia com o nome padronizado para compatibilidade
    caminho_portfolio_compat = os.path.join(pasta_destino, "Portfolio_Tecnico_KR_Engenharia.pdf")
    shutil.copyfile(caminho_portfolio_pdf, caminho_portfolio_compat)

    # 2. Carta de Apresentação Institucional em PDF (com Marca d'Água)
    caminho_carta_pdf = os.path.join(pasta_destino, "Carta_Apresentacao_KR_Engenharia.pdf")
    gerar_carta_apresentacao_pdf(caminho_carta_pdf)

    # 3. Carta de Apresentação em HTML (para visualização web)
    caminho_carta_html = os.path.join(pasta_destino, "Carta_Apresentacao_KR_Engenharia.html")
    with open(caminho_carta_html, "w", encoding="utf-8") as f:
        f.write(gerar_carta_apresentacao_html())

    return {
        "carta_pdf": caminho_carta_pdf,
        "carta_html": caminho_carta_html,
        "portfolio_pdf": caminho_portfolio_pdf,
        "anexos_padrao": [caminho_carta_pdf, caminho_portfolio_pdf]
    }

if __name__ == "__main__":
    print("Compilando documentos oficiais em PDF com marca d'água...")
    docs = compilar_documentos_institucionais()
    print(f"✅ Portfólio Corporativo gerado (PDF): {docs['portfolio_pdf']}")
    print(f"✅ Carta de Apresentação gerada (PDF): {docs['carta_pdf']}")
    print(f"✅ Anexos Oficiais de Envio: {docs['anexos_padrao']}")
