import os
import markdown

def renderizar_proposta():
    # 1. Localiza a proposta gerada em markdown
    if os.path.exists("output/proposta_gerada.md"):
        caminho_md = "output/proposta_gerada.md"
    elif os.path.exists("proposta_gerada.md"):
        caminho_md = "proposta_gerada.md"
    else:
        print("❌ Arquivo 'proposta_gerada.md' não encontrado.")
        print("👉 Execute primeiro: python grafo_agentes.py")
        return

    os.makedirs("output", exist_ok=True)

    with open(caminho_md, "r", encoding="utf-8") as f:
        texto_md = f.read()

    # Converte Markdown para HTML com tabelas
    conteudo_html = markdown.markdown(texto_md, extensions=['tables', 'fenced_code'])

    # 2. Carrega o CSS externo de templates/styles.css se existir
    css_estilos = ""
    if os.path.exists("templates/styles.css"):
        with open("templates/styles.css", "r", encoding="utf-8") as f:
            css_estilos = f.read()

    # 3. Verifica imagens do logo (em assets/ ou raiz)
    caminho_logo = None
    for p in ["assets/logo.png", "logo.png"]:
        if os.path.exists(p):
            caminho_logo = p
            break

    if caminho_logo:
        # Caminho relativo a partir da pasta output/
        src_logo = f"../{caminho_logo}"
        bloco_logo = f'<img src="{src_logo}" alt="KR Engenharia" class="logo-header">'
        bloco_watermark = f'<img src="{src_logo}" alt="" class="watermark-img">'
    else:
        bloco_logo = ''
        bloco_watermark = '<div class="watermark-text">KR ENGENHARIA</div>'

    # 4. Estrutura do documento com CSS injetado
    documento_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Proposta Técnica Comercial - KR Engenharia</title>
    <style>
        {css_estilos}
    </style>
</head>
<body>
    <!-- MARCA D'ÁGUA -->
    {bloco_watermark}

    <!-- BARRA NÃO IMPRESSA -->
    <div class="no-print" style="background: #edf2f7; padding: 12px; margin-bottom: 20px; border-radius: 6px; text-align: center;">
        <span style="font-size: 10pt; color: #4a5568;">Visualização Executiva A4 Pronta. </span>
        <button onclick="window.print()" style="background: #2b6cb0; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; font-weight: bold;">Salvar em PDF / Imprimir</button>
    </div>

    <!-- CABEÇALHO OFICIAL -->
    <div class="header-kr">
        <div class="header-left">
            {bloco_logo}
            <div>
                <h1>KR ENGENHARIA</h1>
                <div class="sub">Consultoria Técnica Especialista • SAS & Proteção de Sistemas de Potência</div>
            </div>
        </div>
        <div class="doc-meta">
            <strong>Responsável Técnico:</strong> Eng. Kayllon Rogger Nunes<br>
            <strong>CREA-MG:</strong> nº 141854962-2<br>
            Belo Horizonte - MG
        </div>
    </div>

    <!-- CONTEÚDO DA PROPOSTA -->
    <div class="content">
        {conteudo_html}
    </div>

    <!-- RODAPÉ -->
    <div class="footer-kr">
        KR Consultoria e Soluções em Engenharia LTDA • www.krconsultoria.com.br • kayllon@krconsultoria.com.br
    </div>
</body>
</html>
"""

    caminho_saida = "output/proposta_final.html"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(documento_html)

    print("\n" + "="*60)
    print(f"✅ DOCUMENTO EXECUTIVO GERADO COM SUCESSO EM: {caminho_saida}")
    if caminho_logo:
        print(f"📌 Logomarca '{caminho_logo}' aplicada no cabeçalho e marca d'água.")
    print("Abra o arquivo no navegador e clique em 'Salvar em PDF' (ou aperte Ctrl + P).")
    print("="*60 + "\n")

if __name__ == "__main__":
    renderizar_proposta()
