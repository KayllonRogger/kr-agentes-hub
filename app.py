import os
import streamlit as st
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Credenciais configuradas no .env
USUARIO_CORRETO = os.getenv("APP_USUARIO", "admin")
SENHA_CORRETA = os.getenv("APP_SENHA", "kr2026")

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

# Localiza imagem do logo
caminho_logo = None
for p in ["assets/logo.png", "logo.png"]:
    if os.path.exists(p):
        caminho_logo = p
        break

# -------------------------------------------------------------
# CONTROLE DE ACESSO (LOGIN PRIVADO)
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col_vazia1, col_login, col_vazia2 = st.columns(3)
    with col_login:
        st.write("")
        st.write("")
        if caminho_logo:
            st.image(caminho_logo, width=160)
        st.markdown('<div class="main-title">KR ENGENHARIA</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Acesso Restrito ao Centro de IA</div>', unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário")
            senha_input = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Acessar Painel", type="primary")
            
            if btn_entrar:
                if usuario_input == USUARIO_CORRETO and senha_input == SENHA_CORRETA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# -------------------------------------------------------------
# PAINEL PRINCIPAL (APÓS LOGIN BEM-SUCEDIDO)
# -------------------------------------------------------------
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

# Cabeçalho da Aplicação
st.markdown('<div class="main-title">KR ENGENHARIA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centro Operacional Multi-Agente • Sistemas de Potência & Automação SAS</div>', unsafe_allow_html=True)

# Barra Lateral
with st.sidebar:
    if caminho_logo:
        st.image(caminho_logo, width=160)
    st.title("Painel de Controle")
    st.write(f"Conectado como: **{USUARIO_CORRETO}**")
    if st.button("Sair da Conta"):
        st.session_state.autenticado = False
        st.rerun()
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

# ABA 1: CÉREBRO CENTRAL (COM MEMÓRIA)
with tab_cerebro:
    st.subheader("Orquestrador Supervisor com Memória de Sessão")
    st.write("Converse com o Cérebro Central. Ele mantém o contexto das mensagens anteriores e roteia entre os departamentos.")
    
    if "mensagens_chat" not in st.session_state:
        st.session_state.mensagens_chat = []

    for m in st.session_state.mensagens_chat:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt_usuario := st.chat_input("Digite sua demanda técnica, pedido de post ou ajuste..."):
        st.session_state.mensagens_chat.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Cérebro Central consultando departamentos..."):
                config_sessao = {"configurable": {"thread_id": "sessao-web-kr"}}
                res = cerebro.invoke({
                    "entrada_usuario": prompt_usuario,
                    "categoria": "",
                    "historico_conversa": st.session_state.mensagens_chat,
                    "resposta_final": ""
                }, config=config_sessao)
                
                resp_texto = f"**[Departamento: {res['categoria']}]**\n\n" + res["resposta_final"]
                st.markdown(resp_texto)
                st.session_state.mensagens_chat.append({"role": "assistant", "content": resp_texto})

# ABA 2: PROPOSTAS E ENGENHARIA
with tab_propostas:
    st.subheader("Esteira de Diagnóstico e Propostas Comerciais")
    col1, col2 = st.columns(2)
    with col1:
        dados_cliente = st.text_area("Dados da Demanda / Relato do Cliente:", height=200, placeholder="Ex.: Subestação 230/13,8 kV, desligamentos na moagem, relés SEL-751 e SIPROTEC 5...")
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
                r_diag = agente_diagnostico(estado)
                estado["diagnostico_tecnico"] = r_diag["diagnostico_tecnico"]
                r_ops = agente_operacoes(estado)
                estado["planejamento_operacional"] = r_ops["planejamento_operacional"]
                r_com = agente_comercial(estado)
                
                os.makedirs("output", exist_ok=True)
                with open("output/proposta_gerada.md", "w", encoding="utf-8") as f:
                    f.write(r_com["proposta_final"])
                renderizar_proposta()
                
                st.success("Proposta Técnica Gerada!")
                st.markdown(r_com["proposta_final"])
                
                if os.path.exists("output/proposta_final.html"):
                    with open("output/proposta_final.html", "r", encoding="utf-8") as f_html:
                        st.download_button(
                            label="📄 Baixar Documento Executivo (A4 / PDF)",
                            data=f_html.read(),
                            file_name="Proposta_KR_Engenharia.html",
                            mime="text/html"
                        )

# ABA 3: MARKETING B2B
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

# ABA 4: PROSPECÇÃO OUTBOUND (COM BUSCA EM 1 CLIQUE)
with tab_prospeccao:
    st.subheader("Inteligência Comercial & Abordagem B2B no LinkedIn")
    st.write("Mapeie decisores em indústrias ou EPCistas e gere mensagens técnicas prontas com link de busca direta.")
    
    col_alvo1, col_alvo2 = st.columns(2)
    with col_alvo1:
        empresa_alvo = st.text_input("Empresa-Alvo / Planta Industrial:", placeholder="Ex: Mineração Vale - Carajás ou EPCista Andrade Gutierrez")
    with col_alvo2:
        servico_foco = st.text_input("Serviço em Foco:", placeholder="Ex: Estudos no ETAP, Comissionamento TAC ou Redes IEC 61850")
        
    cargo_busca = st.selectbox("Cargo do Decisor a Buscar no LinkedIn:", [
        "Gerente de Manutenção Elétrica",
        "Coordenador de Comissionamento",
        "Gerente de Engenharia",
        "Engenheiro Eletricista de Proteção",
        "Diretor de Operações"
    ])
    
    btn_gerar_cadencia = st.button("Gerar Abordagem e Link de Busca", type="primary")
    
    if btn_gerar_cadencia and empresa_alvo:
        with st.spinner("Mapeando decisores e estruturando abordagem..."):
            cadencia = gerar_cadencia_prospeccao(empresa_alvo, servico_foco)
            
            # Gera o link direto no LinkedIn
            import urllib.parse
            query_busca = urllib.parse.quote(f"{cargo_busca} {empresa_alvo}")
            link_linkedin = f"https://www.linkedin.com/search/results/people/?keywords={query_busca}"
            
            os.makedirs("output", exist_ok=True)
            with open("output/cadencia_prospeccao.md", "w", encoding="utf-8") as f:
                f.write(cadencia)
                
            st.success("Estratégia de Abordagem Concluída!")
            
            # Botão de Ação Direta com Link do LinkedIn
            st.link_button(
                label=f"🔗 Abrir Busca de {cargo_busca} na {empresa_alvo} no LinkedIn",
                url=link_linkedin
            )
            
            st.markdown(cadencia)

# ABA 5: AUDITORIA DE EDITAIS
with tab_edital:
    st.subheader("Auditor de Termos de Referência (TR) e Editais")
    texto_tr = st.text_area("Cole trechos do Termo de Referência ou Especificação Técnica do cliente:", height=200, placeholder="Ex.: O cliente exige laudo NR-10 de condutores em canaletas...")
    if st.button("Auditar Escopo e Gerar Lista de Desvios", type="primary"):
        if texto_tr:
            with st.spinner("Auditando conformidade contra o Acervo..."):
                analise = analisar_especificacao_tecnica(texto_tr)
                os.makedirs("output", exist_ok=True)
                with open("output/analise_edital.md", "w", encoding="utf-8") as f:
                    f.write(analise)
                st.success("Auditoria concluída!")
                st.markdown(analise)

# ABA 6: PÓS-COMISSIONAMENTO E ART
with tab_pos_obra:
    st.subheader("Sucesso do Cliente, DataBook As-Built e ART (CREA-MG)")
    dados_conclusao = st.text_area("Dados da Obra Recém-Concluída:", height=150, placeholder="Ex.: Cliente Mineração Vale, concluída parametrização de 6 relés SIPROTEC 5...")
    if st.button("Gerar Pacote de Encerramento e ART", type="primary"):
        if dados_conclusao:
            with st.spinner("Gerando índice de DataBook e minuta de ART..."):
                pacote = gerar_pacote_encerramento(dados_conclusao)
                os.makedirs("output", exist_ok=True)
                with open("output/plano_pos_comissionamento.md", "w", encoding="utf-8") as f:
                    f.write(pacote)
                st.success("Pacote de encerramento gerado!")
                st.markdown(pacote)

# ABA 7: BACKOFFICE E CONFORMIDADE HSE
with tab_backoffice:
    st.subheader("Habilitação de Campo (NR-10/NR-35), Metrologia RBC e Medições")
    dados_backoffice = st.text_area("Dados da Mobilização ou Faturamento:", height=150, placeholder="Ex.: Mobilização de 2 técnicos com mala Conprove e faturamento da 2ª parcela...")
    if st.button("Gerar Dossiê de Conformidade e Medição", type="primary"):
        if dados_backoffice:
            with st.spinner("Auditando documentação de segurança e faturamento..."):
                dossie = processar_conformidade_backoffice(dados_backoffice)
                os.makedirs("output", exist_ok=True)
                with open("output/conformidade_backoffice.md", "w", encoding="utf-8") as f:
                    f.write(dossie)
                st.success("Dossiê gerado com sucesso!")
                st.markdown(dossie)
