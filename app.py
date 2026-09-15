import os
import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa as funções de cada departamento
from cerebro_kr import cerebro
from grafo_agentes import (
    carregar_acervo_tecnico,
    agente_diagnostico,
    agente_operacoes,
    agente_comercial,
    EstadoProjeto
)
from agente_marketing import gerar_conteudo_linkedin
from agente_prospeccao import gerar_cadencia_prospeccao
from agente_inteligencia import analisar_especificacao_tecnica
from agente_pos_comissionamento import gerar_pacote_encerramento
from agente_backoffice import processar_conformidade_backoffice
from gerar_documento import renderizar_proposta

# Configuração da Página Web
st.set_page_config(
    page_title="KR Engenharia - Centro de IA",
    page_icon="⚡",
    layout="wide"
)

# Estilização visual corporativa
st.markdown("""
<style>
    .main-title {
        color: #1a365d;
        font-size: 26pt;
        font-weight: 700;
        margin-bottom: 2px;
    }
    .sub-title {
        color: #718096;
        font-size: 11pt;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho da Aplicação
st.markdown('<div class="main-title">KR ENGENHARIA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centro Operacional Multi-Agente • Sistemas de Potência & Automação SAS</div>', unsafe_allow_html=True)

# Localiza imagem do logo
caminho_logo = None
for p in ["assets/logo.png", "logo.png"]:
    if os.path.exists(p):
        caminho_logo = p
        break

# Barra Lateral
with st.sidebar:
    if caminho_logo:
        st.image(caminho_logo, width=180)
    st.title("Painel de Controle")
    st.write("**Responsável Técnico:**")
    st.write("Eng. Kayllon Rogger Nunes")
    st.caption("CREA-MG nº 141854962-2")
    st.divider()
    st.write("📚 **Base de Conhecimento:**")
    acervo_itens = os.listdir("acervo") if os.path.exists("acervo") else []
    for item in acervo_itens:
        st.caption(f"• {item}")
    st.divider()
    st.caption("LangGraph + Google Gemini 3.5 + LangSmith")

# Definição das Abas dos 7 Departamentos
tab_cerebro, tab_propostas, tab_marketing, tab_prospeccao, tab_edital, tab_pos_obra, tab_backoffice = st.tabs([
    "🧠 Cérebro Central",
    "⚡ Propostas Técnicas",
    "📢 Marketing B2B",
    "🎯 Prospecção Outbound",
    "🔍 Auditoria de Editais",
    "📦 Pós-Comissionamento",
    "📋 Backoffice & HSE"
])

# -------------------------------------------------------------
# ABA 1: CÉREBRO CENTRAL (SUPERVISOR)
# -------------------------------------------------------------
with tab_cerebro:
    st.subheader("Orquestrador Supervisor Geral")
    st.write("Digite qualquer solicitação ou cole um texto. O Cérebro Central identificará o departamento responsável e executará a ação.")
    
    comando = st.text_area("O que você precisa hoje?", placeholder="Ex: 'Cliente Gerdau relatou atuação indevida de 51N nos transformadores de 13,8kV da laminação.'", height=120)
    
    if st.button("Executar pelo Cérebro Central", type="primary"):
        if comando:
            with st.spinner("Processando via LangGraph..."):
                res = cerebro.invoke({
                    "entrada_usuario": comando,
                    "categoria": "",
                    "resposta_final": ""
                })
                st.success(f"Departamento Ativado: **{res['categoria']}**")
                st.markdown(res["resposta_final"])
        else:
            st.warning("Por favor, digite uma solicitação.")

# -------------------------------------------------------------
# ABA 2: PROPOSTAS E ENGENHARIA
# -------------------------------------------------------------
with tab_propostas:
    st.subheader("Esteira de Diagnóstico e Propostas Comerciais")
    col1, col2 = st.columns(2)
    
    with col1:
        dados_cliente = st.text_area("Dados da Demanda / Relato do Cliente:", height=200, placeholder="Ex.: Subestação 230/13,8 kV, desligamentos em cascata na moagem, relés SEL-751 e SIPROTEC 5...")
        condicoes_comerciais = st.text_input("Diretrizes Comerciais (Prazo, Valor e Pagamento):", placeholder="Ex.: Prazo de 3 semanas. Valor de R$ 26.500,00 com 50% de entrada.")
        
        btn_gerar_proposta = st.button("Gerar Proposta Completa", type="primary")
        
    with col2:
        if btn_gerar_proposta and dados_cliente:
            with st.spinner("Executando Agentes de Proteção, Campo e Comercial..."):
                acervo = carregar_acervo_tecnico("acervo")
                estado: EstadoProjeto = {
                    "dados_cliente": dados_cliente,
                    "base_conhecimento": acervo,
                    "diagnostico_tecnico": "",
                    "planejamento_operacional": "",
                    "ajustes_do_engenheiro": condicoes_comerciais if condicoes_comerciais else "Condições comerciais padrão da KR Engenharia com ART inclusa.",
                    "proposta_final": ""
                }
                
                # Executa pipeline
                r_diag = agente_diagnostico(estado)
                estado["diagnostico_tecnico"] = r_diag["diagnostico_tecnico"]
                r_ops = agente_operacoes(estado)
                estado["planejamento_operacional"] = r_ops["planejamento_operacional"]
                r_com = agente_comercial(estado)
                
                # Grava saídas
                os.makedirs("output", exist_ok=True)
                with open("output/proposta_gerada.md", "w", encoding="utf-8") as f:
                    f.write(r_com["proposta_final"])
                renderizar_proposta()
                
                st.success("Proposta Técnica e Documento Executivo Gerados!")
                st.markdown(r_com["proposta_final"])
                
                # Download do HTML Executivo
                if os.path.exists("output/proposta_final.html"):
                    with open("output/proposta_final.html", "r", encoding="utf-8") as f_html:
                        st.download_button(
                            label="📄 Baixar Documento Executivo (A4 / PDF)",
                            data=f_html.read(),
                            file_name="Proposta_KR_Engenharia.html",
                            mime="text/html"
                        )

# -------------------------------------------------------------
# ABA 3: MARKETING B2B
# -------------------------------------------------------------
with tab_marketing:
    st.subheader("Gerador de Artigos e Autoridade Técnica (LinkedIn)")
    tema_post = st.text_area("Tema técnico ou Estudo de Caso de obra passada:", height=150, placeholder="Ex.: Comissionamento de subestação GIS 230/400 kV offshore com validação prévia em bancada.")
    
    if st.button("Gerar Artigo Técnico para LinkedIn", type="primary"):
        if tema_post:
            with st.spinner("Agente de Marketing estruturando post..."):
                post = gerar_conteudo_linkedin(tema_post)
                os.makedirs("output", exist_ok=True)
                with open("output/post_linkedin.md", "w", encoding="utf-8") as f:
                    f.write(post)
                st.success("Artigo gerado com sucesso!")
                st.markdown(post)
        else:
            st.warning("Insira um tema técnico.")

# -------------------------------------------------------------
# ABA 4: PROSPECÇÃO OUTBOUND
# -------------------------------------------------------------
with tab_prospeccao:
    st.subheader("Inteligência Comercial & Abordagem B2B")
    perfil_prospeccao = st.text_area("Perfil da Empresa-Alvo ou Segmento Industrial:", height=150, placeholder="Ex.: Grandes EPCistas de subestações de 138/230 kV para parques solares.")
    
    if st.button("Gerar Mapeamento e Cadência de 3 Etapas", type="primary"):
        if perfil_prospeccao:
            with st.spinner("Mapeando decisores e gerando mensagens..."):
                cadencia = gerar_cadencia_prospeccao(perfil_prospeccao)
                os.makedirs("output", exist_ok=True)
                with open("output/cadencia_prospeccao.md", "w", encoding="utf-8") as f:
                    f.write(cadencia)
                st.success("Estratégia outbound gerada!")
                st.markdown(cadencia)
        else:
            st.warning("Insira o perfil da empresa-alvo.")

# -------------------------------------------------------------
# ABA 5: AUDITORIA DE EDITAIS
# -------------------------------------------------------------
with tab_edital:
    st.subheader("Auditor de Termos de Referência (TR) e Editais")
    texto_tr = st.text_area("Cole trechos do Termo de Referência ou Especificação Técnica do cliente:", height=200, placeholder="Ex.: O cliente exige laudo NR-10 de condutores em canaletas e prazo de 24h para revisão...")
    
    if st.button("Auditar Escopo e Gerar Lista de Desvios", type="primary"):
        if texto_tr:
            with st.spinner("Auditando conformidade contra o Acervo da KR Engenharia..."):
                analise = analisar_especificacao_tecnica(texto_tr)
                os.makedirs("output", exist_ok=True)
                with open("output/analise_edital.md", "w", encoding="utf-8") as f:
                    f.write(analise)
                st.success("Auditoria concluída com sucesso!")
                st.markdown(analise)
        else:
            st.warning("Insira o texto da especificação técnica.")

# -------------------------------------------------------------
# ABA 6: PÓS-COMISSIONAMENTO E ART
# -------------------------------------------------------------
with tab_pos_obra:
    st.subheader("Sucesso do Cliente, DataBook As-Built e ART (CREA-MG)")
    dados_conclusao = st.text_area("Dados da Obra / Comissionamento Recém-Concluído:", height=150, placeholder="Ex.: Cliente Mineração Vale, concluída parametrização de 6 relés SIPROTEC 5 com acompanhamento da primeira energização.")
    
    if st.button("Gerar Pacote de Encerramento e ART", type="primary"):
        if dados_conclusao:
            with st.spinner("Gerando índice de DataBook, minuta de ART e follow-up..."):
                pacote = gerar_pacote_encerramento(dados_conclusao)
                os.makedirs("output", exist_ok=True)
                with open("output/plano_pos_comissionamento.md", "w", encoding="utf-8") as f:
                    f.write(pacote)
                st.success("Pacote de encerramento gerado!")
                st.markdown(pacote)
        else:
            st.warning("Insira os dados da obra concluída.")

# -------------------------------------------------------------
# ABA 7: BACKOFFICE E CONFORMIDADE HSE
# -------------------------------------------------------------
with tab_backoffice:
    st.subheader("Habilitação de Campo (NR-10/NR-35), Metrologia RBC e Medições")
    dados_backoffice = st.text_area("Dados da Mobilização ou Faturamento:", height=150, placeholder="Ex.: Mobilização de 2 técnicos para comissionamento em campo com mala Conprove e solicitação de faturamento da 2ª parcela...")
    
    if st.button("Gerar Dossiê de Conformidade e Medição", type="primary"):
        if dados_backoffice:
            with st.spinner("Auditando documentação de segurança e faturamento..."):
                dossie = processar_conformidade_backoffice(dados_backoffice)
                os.makedirs("output", exist_ok=True)
                with open("output/conformidade_backoffice.md", "w", encoding="utf-8") as f:
                    f.write(dossie)
                st.success("Dossiê gerado com sucesso!")
                st.markdown(dossie)
        else:
            st.warning("Insira os dados da mobilização ou medição.")
