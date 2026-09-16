import os
from config import DADOS_EMPRESA

PASTA_DOCUMENTOS = "documentos"

def gerar_carta_apresentacao_html() -> str:
    """Gera a Carta de Apresentação Executiva oficial da KR Engenharia em formato A4 responsivo."""
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
        }}
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header-title h1 {{
            color: #0f3d64;
            font-size: 22pt;
            margin: 0;
            font-weight: 800;
        }}
        .header-title .sub {{
            color: #64748b;
            font-size: 10pt;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        .logo-img {{
            width: 75px;
            height: 75px;
            border-radius: 4px;
        }}
        .section-title {{
            color: #0f3d64;
            font-size: 13pt;
            font-weight: bold;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 4px;
            margin-top: 25px;
            margin-bottom: 12px;
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
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 6px 6px 0;
        }}
        .footer {{
            margin-top: 40px;
            border-top: 1px solid #e2e8f0;
            padding-top: 20px;
            font-size: 9.5pt;
            color: #64748b;
            text-align: center;
        }}
        ul {{
            padding-left: 20px;
        }}
        li {{
            margin-bottom: 8px;
        }}
        @media print {{
            body {{ background: #fff; padding: 0; }}
            .document-container {{ box-shadow: none; padding: 20px; max-width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="document-container">
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
            Nossa metodologia proprietária baseia-se na <strong>pré-validação em bancada de simulação</strong> de todas as lógicas e parametrizações antes da ida a campo, proporcionando <strong>redução de até 40% no tempo de parada de planta (downtime)</strong> e garantindo energizações seguras e sem surpresas.
        </div>

        <div class="section-title">1. DISCIPLINAS E CAPACIDADES TÉCNICAS</div>
        <ul>
            <li><strong>Estudos Elétricos de Proteção e Seletividade (Software ETAP):</strong> Modelagem completa de transitórios, coordenação de sobrecorrente (50/51, 51N, 51V), direcional (67/67N), diferencial de transformador (87T) e barras (87B), mitigando atuações indevidas em partida de grandes motores.</li>
            <li><strong>Automação de Subestações (SAS / IEC 61850):</strong> Parametrização e validação de lógicas de intertravamento via mensagens GOOSE ultrarrápidas e integração SCADA via relatórios MMS.</li>
            <li><strong>Comissionamento de Campo (TAF / TAC):</strong> Testes de injeção secundária em relés de proteção multimarcas (Siemens SIPROTEC 5, SEL, Schneider e ABB) utilizando malas de teste microprocessadas rastreáveis à RBC.</li>
            <li><strong>Inspeções e Ensaios em Equipamentos Primários:</strong> Transformadores de força, disjuntores e transformadores para instrumentos (TCs e TPs).</li>
        </ul>

        <div class="section-title">2. EXPERIÊNCIA DE CAMPO E CASES DE REFERÊNCIA</div>
        <ul>
            <li><strong>Geração Eólica Offshore (Baltic Power 400 kV):</strong> Vivência internacional na validação de sistemas de controle e proteção de subestações GIS em alta tensão.</li>
            <li><strong>Grandes Mineradoras e Siderúrgicas Nacionais:</strong> Atuação em retrofits complexos e comissionamento em plantas da Vale e Gerdau Aços Longos com janelas operacionais restritas.</li>
        </ul>

        <div class="section-title">3. RIGOR TÉCNICO E CONFORMIDADE</div>
        <p>Todos os projetos contam com emissão formal de <strong>ART perante o CREA-MG</strong> e entrega do <strong>DataBook As-Built</strong> completo com relatórios de ensaio e arquivos finais parametrizados.</p>

        <p>Colocamo-nos à inteira disposição para agendar uma reunião técnica de 15 minutos ou analisar preliminarmente o diagrama unifilar de vossa planta para identificar oportunidades de blindagem operacional.</p>

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
</body>
</html>
"""
    return html

def gerar_portfolio_resumido_texto() -> str:
    """Gera versão em texto estruturado do portfólio para anexos de e-mail rápidos."""
    return f"""==========================================================
KR ENGENHARIA — PORTFÓLIO TÉCNICO RESUMIDO
Boutique de Engenharia em Sistemas de Potência & Proteção
==========================================================

Responsável Técnico: {DADOS_EMPRESA['responsavel_tecnico']} ({DADOS_EMPRESA['crea']})
Website: {DADOS_EMPRESA['website']} | Contato: {DADOS_EMPRESA['email']}
Telefone: +55 (31) 99566-6963 | Belo Horizonte - MG

1. ESPECIALIDADES:
- Estudos de Proteção e Seletividade no software ETAP (Coordenação ANSI 50/51, 51N, 51V, 67, 87T).
- Automação de Subestações SAS / IEC 61850 (mensagens GOOSE e relatórios MMS).
- Comissionamento de Campo (TAF/TAC) com malas microprocessadas calibradas RBC.
- Parametrização multimarcas: Siemens SIPROTEC 5, SEL, Schneider e ABB.

2. DIFERENCIAL KR ENGENHARIA:
- Pré-validação em laboratório/bancada com redução de até 40% de downtime em paradas industriais.
- 100% dos serviços com ART perante o CREA-MG e entrega de DataBook As-Built.

3. CASOS DE REFERÊNCIA:
- Baltic Power 400 kV (Subestação Offshore GIS).
- Retrofits e comissionamento em plantas de grande porte da Vale e Gerdau.
=========================================================="""

def compilar_documentos_institucionais(pasta_destino: str = PASTA_DOCUMENTOS) -> dict:
    """Gera e salva os documentos institucionais prontos para envio em anexo."""
    os.makedirs(pasta_destino, exist_ok=True)
    
    # 1. Carta de Apresentação HTML
    caminho_carta_html = os.path.join(pasta_destino, "Carta_Apresentacao_KR_Engenharia.html")
    with open(caminho_carta_html, "w", encoding="utf-8") as f:
        f.write(gerar_carta_apresentacao_html())

    # 2. Portfólio Resumido TXT
    caminho_portfolio_txt = os.path.join(pasta_destino, "Portfolio_Tecnico_KR_Engenharia.txt")
    with open(caminho_portfolio_txt, "w", encoding="utf-8") as f:
        f.write(gerar_portfolio_resumido_texto())

    return {
        "carta_html": caminho_carta_html,
        "portfolio_txt": caminho_portfolio_txt,
        "anexos_padrao": [caminho_carta_html, caminho_portfolio_txt]
    }

if __name__ == "__main__":
    print("Compilando documentos oficiais da KR Engenharia...")
    docs = compilar_documentos_institucionais()
    print(f"✅ Carta de Apresentação gerada: {docs['carta_html']}")
    print(f"✅ Portfólio gerado: {docs['portfolio_txt']}")

