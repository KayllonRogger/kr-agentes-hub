import os
import time
import uuid
import urllib.parse
import streamlit as st

# Módulos centrais refatorados
from config import APP_USUARIO, APP_SENHA, DADOS_EMPRESA, CONTAS_FUNCIONARIOS
from utils import (
    carregar_acervo_tecnico,
    gerar_link_busca_linkedin,
    salvar_markdown_saida
)
from cerebro_kr import cerebro
from empresa_kr import (
    FUNCIONARIOS,
    carregar_tarefas,
    atribuir_tarefa,
    executar_tarefa_funcionario,
    aprovar_tarefa_diretor
)
from grafo_agentes import executar_pipeline_proposta
from agente_marketing import gerar_conteudo_linkedin
from agente_prospeccao import gerar_cadencia_prospeccao
from agente_inteligencia import analisar_especificacao_tecnica
from agente_pos_comissionamento import gerar_pacote_encerramento
from agente_backoffice import processar_conformidade_backoffice
from gerar_documento import renderizar_proposta
from servico_email import (
    enviar_email_funcionario,
    testar_conexao_smtp,
    gerar_assinatura_html,
    ler_caixa_entrada,
    analisar_intencao_resposta
)
from prospeccao_autonoma import (
    CATALOGO_SETORES,
    executar_varredura_setor,
    carregar_fila_campanhas,
    atualizar_lead_campanha,
    excluir_lead_campanha,
    limpar_fila_campanhas,
    gerar_links_prospeccao
)
from documentos_kr import compilar_documentos_institucionais

# Configuração da Página Web
st.set_page_config(
    page_title=f"{DADOS_EMPRESA['nome_fantasia']} - Centro de IA",
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
    .employee-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 12px;
    }
    .employee-name {
        color: #1a365d;
        font-weight: 700;
        font-size: 13pt;
    }
    .employee-role {
        color: #2b6cb0;
        font-size: 9.5pt;
        font-weight: 600;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Cache para acervo técnico
@st.cache_data(ttl=3600)
def carregar_acervo_cached() -> str:
    return carregar_acervo_tecnico("acervo")

# Localiza imagem do logo
caminho_logo = None
for p in ["assets/logo.png", "logo.png"]:
    if os.path.exists(p):
        caminho_logo = p
        break

# CONTROLE DE ACESSO (LOGIN)
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "session_id" not in st.session_state:
    st.session_state.session_id = f"sessao-{uuid.uuid4().hex[:8]}"

if not st.session_state.autenticado:
    col_vazia1, col_login, col_vazia2 = st.columns(3)
    with col_login:
        st.write("")
        st.write("")
        if caminho_logo:
            st.image(caminho_logo, width=160)
        st.markdown(f'<div class="main-title">{DADOS_EMPRESA["nome_fantasia"].upper()}</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Acesso Restrito ao Centro de IA</div>', unsafe_allow_html=True)
        
        with st.form("form_login"):
            usuario_input = st.text_input("Usuário")
            senha_input = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Acessar Painel", type="primary")
            
            if btn_entrar:
                if usuario_input == APP_USUARIO and senha_input == APP_SENHA:
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")
    st.stop()

# -------------------------------------------------------------
# PAINEL PRINCIPAL (LOGADO)
# -------------------------------------------------------------
st.markdown(f'<div class="main-title">{DADOS_EMPRESA["nome_fantasia"].upper()}</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centro Operacional Multi-Agente • Equipe Virtual de Especialistas</div>', unsafe_allow_html=True)

# Barra Lateral
with st.sidebar:
    if caminho_logo:
        st.image(caminho_logo, width=160)
    st.title("Diretor Técnico")
    st.write(DADOS_EMPRESA["responsavel_tecnico"])
    st.caption(DADOS_EMPRESA["crea"])
    st.caption(f"Sessão Ativa: `{st.session_state.session_id}`")
    if st.button("Sair da Conta"):
        st.session_state.autenticado = False
        st.session_state.session_id = f"sessao-{uuid.uuid4().hex[:8]}"
        st.rerun()
    st.divider()
    st.write("👥 **Equipe de Funcionários:**")
    for fid, f_info in FUNCIONARIOS.items():
        email_str = f_info.get("email", "")
        st.markdown(f"• **{f_info['nome']}**<br>&nbsp;&nbsp;<span style='color:#718096;font-size:8pt;'>{f_info['departamento']}</span><br>&nbsp;&nbsp;<code style='font-size:7.5pt;'>{email_str}</code>", unsafe_allow_html=True)
    st.divider()
    st.caption("LangGraph + Google Gemini + Titan SMTP")

# Definição das Abas
tab_equipe, tab_cerebro, tab_propostas, tab_marketing, tab_prospeccao, tab_inbox, tab_edital, tab_pos_obra, tab_backoffice = st.tabs([
    "🏢 Escritório da Equipe",
    "🧠 Cérebro Central",
    "⚡ Propostas Técnicas",
    "📢 Marketing B2B",
    "🎯 Prospecção Outbound",
    "📬 Caixa de Entrada",
    "🔍 Auditoria de Editais",
    "📦 Pós-Comissionamento",
    "📋 Backoffice & HSE"
])

# -------------------------------------------------------------
# ABA 1: ESCRITÓRIO VIRTUAL DA EQUIPE
# -------------------------------------------------------------
with tab_equipe:
    st.subheader("Quadro Operacional dos Funcionários Autônomos")
    st.write("Cada agente opera de forma independente em sua especialidade. As entregas finalizadas são enviadas para a sua aprovação.")
    
    tarefas_atuais = carregar_tarefas()
    pendentes_aprovacao = [t for t in tarefas_atuais if t.get("status") == "AGUARDANDO_APROVACAO"]
    em_execucao = [t for t in tarefas_atuais if t.get("status") in ["PENDENTE", "EM_EXECUCAO"]]
    concluidas = [t for t in tarefas_atuais if t.get("status") == "CONCLUIDO"]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Funcionários Ativos", len(FUNCIONARIOS))
    m2.metric("Tarefas em Andamento", len(em_execucao))
    m3.metric("Aguardando sua Aprovação", len(pendentes_aprovacao))
    m4.metric("Tarefas Concluídas", len(concluidas))
    
    st.divider()

    st.markdown("### 📥 Mesa do Diretor (Entregas Aguardando sua Aprovação)")
    if not pendentes_aprovacao:
        st.info("Nenhuma entrega pendente no momento. Seus funcionários estão aguardando novas diretrizes ou trabalhando nas tarefas.")
    else:
        for t in pendentes_aprovacao:
            with st.expander(f"🔔 {t.get('funcionario_nome')} finalizou: {t.get('titulo')} (Criado em {t.get('data_criacao')})", expanded=True):
                st.write(f"**Cargo:** {t.get('cargo')}")
                st.write(f"**Briefing inicial:** {t.get('instrucao')}")
                st.markdown("**Resultado Produzido pelo Funcionário:**")
                st.markdown(t.get("resultado", ""))
                
                c_aprov1, c_aprov2 = st.columns(2)
                with c_aprov1:
                    parecer = st.text_input(f"Observações do Diretor para {t['id']}:", value="Aprovado com rigor técnico.", key=f"obs_{t['id']}")
                with c_aprov2:
                    st.write("")
                    st.write("")
                    if st.button(f"✅ Aprovar Entrega de {t.get('funcionario_nome')}", key=f"btn_aprov_{t['id']}", type="primary"):
                        aprovar_tarefa_diretor(t["id"], parecer)
                        st.success(f"Entrega {t['id']} aprovada pelo {DADOS_EMPRESA['responsavel_tecnico']}!")
                        st.rerun()

    st.divider()

    st.markdown("### ➕ Delegar Tarefa para um Funcionário")
    col_del1, col_del2 = st.columns(2)
    
    with col_del1:
        opcoes_func = {fid: f"{info['nome']} — {info['cargo']}" for fid, info in FUNCIONARIOS.items()}
        func_escolhido = st.selectbox("Selecione o Funcionário:", list(opcoes_func.keys()), format_func=lambda x: opcoes_func[x])
        titulo_tarefa = st.text_input("Título da Tarefa:", placeholder="Ex: Prospecção da Mineradora Samarco ou Artigo sobre Curto-Circuito")
        
    with col_del2:
        instrucao_tarefa = st.text_area("Instruções Técnicas / Dados de Entrada:", height=100, placeholder="Descreva os dados do cliente, normas ou objetivo do trabalho...")
        
    if st.button("Atribuir e Executar Tarefa Autônoma", type="primary"):
        if titulo_tarefa and instrucao_tarefa:
            with st.spinner(f"Atribuindo e aguardando execução de {FUNCIONARIOS[func_escolhido]['nome']}..."):
                try:
                    nova_t = atribuir_tarefa(titulo_tarefa, func_escolhido, instrucao_tarefa)
                    executar_tarefa_funcionario(nova_t["id"])
                    st.success(f"Tarefa executada por {FUNCIONARIOS[func_escolhido]['nome']} e colocada na sua Mesa de Aprovação!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha na execução da tarefa: {e}")
        else:
            st.warning("Preencha o título e as instruções da tarefa.")

# -------------------------------------------------------------
# ABA 2: CÉREBRO CENTRAL (SUPERVISOR COM CHAT)
# -------------------------------------------------------------
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
                try:
                    config_sessao = {"configurable": {"thread_id": st.session_state.session_id}}
                    res = cerebro.invoke({
                        "entrada_usuario": prompt_usuario,
                        "categoria": "",
                        "historico_conversa": st.session_state.mensagens_chat,
                        "resposta_final": ""
                    }, config=config_sessao)
                    
                    categoria_resp = res.get("categoria", "GERAL")
                    resp_texto = f"**[Departamento: {categoria_resp}]**\n\n" + res.get("resposta_final", "")
                    st.markdown(resp_texto)
                    st.session_state.mensagens_chat.append({"role": "assistant", "content": resp_texto})
                except Exception as e:
                    erro_msg = f"❌ Erro ao consultar Cérebro Central: {e}"
                    st.error(erro_msg)
                    st.session_state.mensagens_chat.append({"role": "assistant", "content": erro_msg})

# -------------------------------------------------------------
# ABA 3: PROPOSTAS E ENGENHARIA
# -------------------------------------------------------------
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
                try:
                    estado_prop = executar_pipeline_proposta(dados_cliente, condicoes_comerciais)
                    renderizar_proposta()
                    
                    st.success("Proposta Técnica Gerada!")
                    st.markdown(estado_prop["proposta_final"])
                    
                    if os.path.exists("output/proposta_final.html"):
                        with open("output/proposta_final.html", "r", encoding="utf-8") as f_html:
                            st.download_button(
                                label="📄 Baixar Documento Executivo (A4 / PDF)",
                                data=f_html.read(),
                                file_name="Proposta_KR_Engenharia.html",
                                mime="text/html"
                            )
                except Exception as e:
                    st.error(f"Erro ao gerar proposta técnica: {e}")

# -------------------------------------------------------------
# ABA 4: MARKETING B2B
# -------------------------------------------------------------
with tab_marketing:
    st.subheader("Gerador de Artigos e Autoridade Técnica (LinkedIn)")
    tema_post = st.text_area("Tema técnico ou Estudo de Caso de obra passada:", height=150, placeholder="Ex.: Comissionamento de subestação GIS 230/400 kV offshore com validação prévia em bancada.")
    if st.button("Gerar Artigo Técnico para LinkedIn", type="primary"):
        if tema_post:
            with st.spinner("Mariana Esteves estruturando post..."):
                try:
                    post = gerar_conteudo_linkedin(tema_post)
                    salvar_markdown_saida("post_linkedin.md", post)
                    st.success("Artigo gerado com sucesso!")
                    st.markdown(post)
                except Exception as e:
                    st.error(f"Erro ao gerar artigo: {e}")

# -------------------------------------------------------------
# ABA 5: PROSPECÇÃO OUTBOUND
# -------------------------------------------------------------
with tab_prospeccao:
    st.subheader("🎯 Inteligência Comercial & Prospecção Outbound B2B")
    st.caption("Lucas Campos (SDR) — Mapeamento autônomo de decisores no LinkedIn, operadores booleanos (Google X-Ray) e disparos com portfólio oficial via Titan SMTP.")

    modo_prospeccao = st.radio(
        "Modo de Operação Comercial:",
        ["🤖 Motor de Campanhas Autônomas (Lucas SDR)", "🎯 Abordagem Pontual Sob Demanda"],
        horizontal=True,
        key="radio_modo_prospeccao"
    )

    if modo_prospeccao == "🤖 Motor de Campanhas Autônomas (Lucas SDR)":
        docs_institucionais = compilar_documentos_institucionais()
        fila_campanhas = carregar_fila_campanhas()
        total_leads = len(fila_campanhas)
        prontos_disparo = len([l for l in fila_campanhas if l.get("status") == "PRONTO_PARA_DISPARO"])
        enviados = len([l for l in fila_campanhas if l.get("status") == "ENVIADO"])
        setores_presentes = len(set(l.get("setor") for l in fila_campanhas if l.get("setor")))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Leads Mapeados", total_leads)
        m2.metric("Prontos para Disparo", prontos_disparo)
        m3.metric("Disparados Oficialmente", enviados)
        m4.metric("Setores em Foco", setores_presentes)

        st.divider()

        # Painel de Disparo de Nova Varredura
        with st.expander("🚀 Iniciar Nova Varredura Autônoma no Mercado", expanded=(total_leads == 0)):
            st.markdown("##### Parametrização da Varredura pelo Lucas Campos")
            col_v1, col_v2, col_v3 = st.columns([2, 2, 1])
            with col_v1:
                opcoes_setor = {k: f"{v['nome']} ({len(v['empresas'])} plantas mapeadas)" for k, v in CATALOGO_SETORES.items()}
                setor_escolhido = st.selectbox(
                    "Setor Industrial Alvo:",
                    list(opcoes_setor.keys()),
                    format_func=lambda x: opcoes_setor[x],
                    key="sel_setor_varredura"
                )
            with col_v2:
                foco_tecnico = st.text_input(
                    "Especialidade Foco:",
                    value="Estudos de Proteção no ETAP e Comissionamento TAF/TAC",
                    key="input_foco_varredura"
                )
            with col_v3:
                plantas_disponiveis = len(CATALOGO_SETORES[setor_escolhido]["empresas"])
                limite_varredura = st.number_input(
                    "Plantas por Ciclo:",
                    min_value=1,
                    max_value=plantas_disponiveis,
                    value=min(2, plantas_disponiveis),
                    key="num_plantas_varredura"
                )

            if st.button("🔎 Executar Varredura com Lucas Campos", type="primary", key="btn_exec_varredura"):
                nome_setor = CATALOGO_SETORES[setor_escolhido]["nome"]
                with st.spinner(f"Lucas Campos mapeando plantas em {nome_setor}, gerando dorks do LinkedIn e redigindo abordagens técnicas com anexos..."):
                    try:
                        novos = executar_varredura_setor(
                            chave_setor=setor_escolhido,
                            especialidade_foco=foco_tecnico,
                            limite=int(limite_varredura)
                        )
                        st.success(f"✅ {len(novos)} novas empresas do setor '{nome_setor}' mapeadas e adicionadas à fila de disparo!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro durante a varredura autônoma: {err}")

        # Seção de Documentos Institucionais Anexados
        with st.expander("📎 Documentos Oficiais Anexados aos E-mails (Portfólio Corporativo & Carta em PDF)"):
            st.caption("Estes documentos são automaticamente compilados em PDF e incluídos nos disparos de prospecção do Lucas Campos.")
            col_doc1, col_doc2 = st.columns(2)
            with col_doc1:
                st.markdown("**1. Carta de Apresentação Institucional (PDF com Marca d'Água)**")
                st.caption("Apresentação formal das disciplinas e metodologia com a logomarca KR como marca d'água de fundo.")
                try:
                    with open(docs_institucionais["carta_pdf"], "rb") as f:
                        conteudo_carta_pdf = f.read()
                    st.download_button(
                        label="📥 Baixar Carta de Apresentação (PDF)",
                        data=conteudo_carta_pdf,
                        file_name="Carta_Apresentacao_KR_Engenharia.pdf",
                        mime="application/pdf",
                        key="btn_down_carta_pdf"
                    )
                except Exception:
                    st.info("Documento sendo compilado...")
            with col_doc2:
                st.markdown("**2. Portfólio Corporativo Oficial (PDF 3 Páginas)**")
                st.caption("Documento completo de engenharia: disciplinas, instrumental RBC, cases reais e redução de downtime.")
                try:
                    with open(docs_institucionais["portfolio_pdf"], "rb") as f:
                        conteudo_port_pdf = f.read()
                    st.download_button(
                        label="📥 Baixar Portfólio Corporativo (PDF)",
                        data=conteudo_port_pdf,
                        file_name="Portfolio_Corporativo_KR_Engenharia.pdf",
                        mime="application/pdf",
                        key="btn_down_port_pdf"
                    )
                except Exception:
                    st.info("Documento sendo compilado...")

        st.divider()

        # Fila de Oportunidades
        col_hdr1, col_hdr2 = st.columns([3, 1])
        with col_hdr1:
            st.markdown("### 📋 Fila de Oportunidades & Disparos Oficiais")
        with col_hdr2:
            if total_leads > 0:
                if st.button("🗑️ Limpar Fila de Campanhas", key="btn_limpar_fila"):
                    limpar_fila_campanhas()
                    st.rerun()

        if total_leads == 0:
            st.info("Nenhuma oportunidade na fila no momento. Clique em 'Iniciar Nova Varredura Autônoma no Mercado' acima para começar.")
        else:
            for lead in fila_campanhas:
                lid = lead["id"]
                st_badge = "🟡 PRONTO PARA DISPARO" if lead.get("status") == "PRONTO_PARA_DISPARO" else ("🟢 ENVIADO" if lead.get("status") == "ENVIADO" else "🔴 ERRO")
                
                with st.expander(f"🏢 {lead.get('empresa')} — {lead.get('setor')} [{st_badge}]", expanded=(lead.get("status") == "PRONTO_PARA_DISPARO")):
                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown(f"**Tensão da Planta:** `{lead.get('tensao', 'N/D')}`")
                        st.markdown(f"**Cargo do Decisor Alvo:** `{lead.get('cargo_alvo', 'N/D')}`")
                    with c_info2:
                        st.markdown(f"**Domínio Corporativo:** `{lead.get('dominio', 'N/D')}`")
                        st.markdown(f"**Status Atual:** `{st_badge}`" + (f" ({lead.get('data_envio')})" if lead.get('data_envio') else ""))

                    st.markdown("#### 🔍 Engrenagens de Busca de Contatos Reais (Lusha & LinkedIn)")
                    st.info("💡 **Localização Precisa:** Clique em **Lusha** ou **LinkedIn** para localizar o e-mail corporativo direto e telefone do gestor elétrico. Cole o e-mail verificado no campo abaixo para habilitar o envio com portfólio.")

                    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
                    with col_g1:
                        st.link_button(
                            label="⚡ 1. Buscar no Lusha",
                            url=lead.get("link_lusha", f"https://www.google.com/search?q=site%3Alusha.com+{urllib.parse.quote(lead.get('empresa', ''))}"),
                            help="Busca no diretório Lusha por e-mails diretos e telefones de gestores da área elétrica."
                        )
                    with col_g2:
                        st.link_button(
                            label=f"🔗 2. LinkedIn Direct",
                            url=lead.get("link_linkedin", "#"),
                            help="Busca direta de pessoas logadas no LinkedIn com cargo de gerenciamento elétrico."
                        )
                    with col_g3:
                        st.link_button(
                            label="🔎 3. Google X-Ray",
                            url=lead.get("link_xray", "#"),
                            help="Operador booleano avançado para perfis indexados sem limite de busca."
                        )
                    with col_g4:
                        st.link_button(
                            label="🎯 4. RocketReach",
                            url=lead.get("link_rocketreach", f"https://www.google.com/search?q=site%3Arocketreach.co+{urllib.parse.quote(lead.get('empresa', ''))}"),
                            help="Consulta complementar para validação de contatos corporativos verificados."
                        )

                    st.markdown("#### ✉️ Proposta de E-mail Estruturada por Lucas Campos")
                    
                    email_dest_input = st.text_input(
                        "E-mail Verificado do Gestor Elétrico:",
                        value=lead.get("email_destinatario", ""),
                        placeholder="Cole aqui o e-mail real do gestor elétrico obtido no Lusha ou LinkedIn (ex: nome.sobrenome@empresa.com)",
                        key=f"dest_{lid}"
                    )
                    assunto_input = st.text_input(
                        "Linha de Assunto:",
                        value=lead.get("assunto", ""),
                        key=f"ass_{lid}"
                    )
                    corpo_input = st.text_area(
                        "Corpo da Mensagem (Hiperpersonalizado de Engenharia para Engenharia):",
                        value=lead.get("corpo_email", ""),
                        height=200,
                        key=f"corp_{lid}"
                    )
                    st.caption("ℹ️ O corpo do e-mail encerra em 'Atenciosamente,'. A assinatura corporativa oficial com logotipo da KR Engenharia e dados da empresa será anexada automaticamente como rodapé.")

                    st.markdown("📎 **Anexos que acompanharão o disparo:**")
                    for anexo in lead.get("anexos", []):
                        st.write(f"- `{os.path.basename(anexo)}`")

                    col_act1, col_act2, col_act3 = st.columns([2, 1, 1])
                    with col_act1:
                        if lead.get("status") != "ENVIADO":
                            if st.button("🚀 Disparar E-mail com Anexos (Titan SMTP)", key=f"btn_send_{lid}", type="primary"):
                                if not email_dest_input or "@" not in email_dest_input:
                                    st.warning("⚠️ Cole o e-mail verificado do gestor elétrico (obtido via Lusha ou LinkedIn) para prosseguir com o disparo.")
                                else:
                                    with st.spinner(f"Lucas Campos conectando à conta Titan e enviando para {email_dest_input}..."):
                                        res_envio = enviar_email_funcionario(
                                            funcionario_id="LUCAS",
                                            destinatario=email_dest_input,
                                            assunto=assunto_input,
                                            corpo_texto=corpo_input,
                                            anexos=lead.get("anexos", [])
                                        )
                                        if res_envio["sucesso"]:
                                            st.success(f"✅ {res_envio['mensagem']}")
                                            atualizar_lead_campanha(lid, {
                                                "status": "ENVIADO",
                                                "email_destinatario": email_dest_input,
                                                "assunto": assunto_input,
                                                "corpo_email": corpo_input,
                                                "data_envio": time.strftime("%d/%m/%Y %H:%M"),
                                                "resultado_envio": res_envio["mensagem"]
                                            })
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {res_envio['erro']}")
                                            atualizar_lead_campanha(lid, {
                                                "status": "ERRO",
                                                "resultado_envio": res_envio["erro"]
                                            })
                        else:
                            st.success(f"✅ E-mail enviado com sucesso em {lead.get('data_envio')} para `{lead.get('email_destinatario')}`!")
                            if st.button("🔄 Reenviar E-mail", key=f"btn_resend_{lid}"):
                                atualizar_lead_campanha(lid, {"status": "PRONTO_PARA_DISPARO"})
                                st.rerun()

                    with col_act2:
                        if st.button("💾 Salvar Alterações", key=f"btn_save_{lid}"):
                            atualizar_lead_campanha(lid, {
                                "email_destinatario": email_dest_input,
                                "assunto": assunto_input,
                                "corpo_email": corpo_input
                            })
                            st.success("Alterações salvas!")

                    with col_act3:
                        if st.button("❌ Remover Lead", key=f"btn_del_{lid}"):
                            excluir_lead_campanha(lid)
                            st.rerun()

                    with st.expander("👁️ Assinatura Institucional Oficial que acompanhará o e-mail"):
                        st.markdown(gerar_assinatura_html(CONTAS_FUNCIONARIOS["LUCAS"]), unsafe_allow_html=True)

    else:
        # Modo 2: Abordagem Pontual Sob Demanda
        st.subheader("Inteligência Comercial & Abordagem B2B no LinkedIn")
        col_alvo1, col_alvo2 = st.columns(2)
        with col_alvo1:
            empresa_alvo = st.text_input("Empresa-Alvo / Planta Industrial:", placeholder="Ex: Mineração Vale - Carajás ou EPCista Andrade Gutierrez")
        with col_alvo2:
            servico_foco = st.text_input("Serviço em Foco:", placeholder="Ex: Estudos no ETAP, Comissionamento TAC ou Redes IEC 61850")
            
        cargo_busca = st.selectbox("Cargo do Decisor na Área de Gerenciamento Elétrico:", [
            "Gerente de Manutenção Elétrica",
            "Gerente de Engenharia Elétrica",
            "Coordenador de Manutenção Elétrica",
            "Coordenador de Proteção e Comissionamento",
            "Supervisor de Manutenção Elétrica e Automação",
            "Gestor de Sistemas de Potência & Subestações"
        ])
        
        btn_gerar_cadencia = st.button("Gerar Abordagem e Links de Busca", type="primary")
        
        if btn_gerar_cadencia and empresa_alvo:
            with st.spinner("Lucas Campos mapeando decisores e estruturando abordagem..."):
                try:
                    cadencia = gerar_cadencia_prospeccao(empresa_alvo, servico_foco)
                    link_linkedin = gerar_link_busca_linkedin(empresa_alvo, cargo_busca)
                    query_lusha_pontual = urllib.parse.quote(f'site:lusha.com "{empresa_alvo}" ("{cargo_busca}" OR "Manutenção Elétrica")')
                    link_lusha_pontual = f"https://www.google.com/search?q={query_lusha_pontual}"
                    salvar_markdown_saida("cadencia_prospeccao.md", cadencia)
                    
                    st.session_state.cadencia_atual = cadencia
                    st.session_state.empresa_atual = empresa_alvo
                        
                    st.success("Estratégia de Abordagem Concluída!")
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.link_button(
                            label=f"⚡ Buscar no Lusha ({empresa_alvo})",
                            url=link_lusha_pontual,
                            help="Localize e-mails diretos e telefones de gestores da planta via Lusha."
                        )
                    with col_p2:
                        st.link_button(
                            label=f"🔗 Abrir Busca no LinkedIn Direct ({cargo_busca})",
                            url=link_linkedin
                        )
                    st.markdown(cadencia)
                except Exception as e:
                    st.error(f"Erro ao gerar prospecção: {e}")

        if "cadencia_atual" in st.session_state:
            st.divider()
            st.markdown("### 📧 Disparo Oficial de E-mail via Lucas Campos")
            st.caption("Envio autônomo diretamente da conta institucional `lucas.campos@krconsultoria.com.br` via Titan SMTP.")
            
            docs_institucionais = compilar_documentos_institucionais()
            anexar_documentos = st.checkbox("📎 Anexar Carta de Apresentação e Portfólio Oficial da KR", value=True, key="chk_anexar_pontual")

            col_email1, col_email2 = st.columns(2)
            with col_email1:
                destinatario_email = st.text_input("E-mail do Decisor/Cliente:", placeholder="ex: gerente.eletrica@mineradora.com.br", key="input_dest_email")
                assunto_padrao = f"KR Engenharia | Diagnóstico Técnico em {st.session_state.get('empresa_atual', 'Sistemas de Potência')}"
                assunto_email = st.text_input("Assunto do E-mail:", value=assunto_padrao, key="input_assunto_email")
                
            with col_email2:
                st.write("")
                st.write("")
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    btn_enviar_email = st.button("🚀 Disparar E-mail Oficial", type="primary", key="btn_enviar_lucas")
                with col_b2:
                    btn_testar_conexao = st.button("🔍 Testar Conexão Titan", key="btn_testar_titan")

            if btn_testar_conexao:
                with st.spinner("Testando autenticação de Lucas Campos no servidor Titan..."):
                    res_test = testar_conexao_smtp("LUCAS")
                    if res_test["sucesso"]:
                        st.success(f"✅ {res_test['mensagem']} ({res_test.get('modo', '')})")
                    else:
                        st.error(f"❌ {res_test['motivo']}")
                        if "dica" in res_test:
                            st.info(f"💡 {res_test['dica']}")

            if btn_enviar_email:
                if not destinatario_email or "@" not in destinatario_email:
                    st.warning("Por favor, informe um endereço de e-mail válido para o destinatário.")
                else:
                    anexos_envio = docs_institucionais["anexos_padrao"] if anexar_documentos else None
                    with st.spinner(f"Lucas Campos conectando à conta e disparando e-mail para {destinatario_email}..."):
                        res_envio = enviar_email_funcionario(
                            funcionario_id="LUCAS",
                            destinatario=destinatario_email,
                            assunto=assunto_email,
                            corpo_texto=st.session_state.cadencia_atual,
                            anexos=anexos_envio
                        )
                        if res_envio["sucesso"]:
                            st.success(f"✅ {res_envio['mensagem']}")
                        else:
                            st.error(f"❌ {res_envio['erro']}")
                            st.info("💡 Se o Titan recusar autenticação, certifique-se de que o acesso SMTP/IMAP está ativado no painel Titan ou acesse primeiro via webmail (https://mail.titan.email).")

            with st.expander("👁️ Ver Prévia da Assinatura Oficial do E-mail (com Logomarca KR)"):
                st.markdown(gerar_assinatura_html(CONTAS_FUNCIONARIOS["LUCAS"]), unsafe_allow_html=True)

# -------------------------------------------------------------
# ABA 6: CAIXA DE ENTRADA (TITAN IMAP)
# -------------------------------------------------------------
with tab_inbox:
    st.subheader("📬 Central de E-mails Recebidos & Triagem com IA")
    st.caption("Leitura das caixas de entrada dos funcionários em tempo real via Titan IMAP.")

    col_inbox_f, col_inbox_cfg = st.columns([2, 1])
    with col_inbox_f:
        opcoes_func_inbox = {fid: f"{info['nome']} ({info['email']})" for fid, info in CONTAS_FUNCIONARIOS.items()}
        func_inbox_sel = st.selectbox(
            "Selecione o Funcionário:",
            list(opcoes_func_inbox.keys()),
            format_func=lambda x: opcoes_func_inbox[x],
            key="sel_func_inbox"
        )
    with col_inbox_cfg:
        apenas_unseen = st.checkbox("Apenas e-mails não lidos", value=False, key="chk_unseen")
        btn_ler_inbox = st.button("🔄 Atualizar Caixa de Entrada", type="primary", key="btn_refresh_inbox")

    func_nome = CONTAS_FUNCIONARIOS[func_inbox_sel]["nome"]
    func_email = CONTAS_FUNCIONARIOS[func_inbox_sel]["email"]

    with st.spinner(f"Consultando caixa postal de {func_nome} via IMAP..."):
        dados_inbox = ler_caixa_entrada(func_inbox_sel, limite=10, apenas_nao_lidas=apenas_unseen)

    if not dados_inbox["sucesso"]:
        st.error(f"❌ Erro ao consultar a caixa postal: {dados_inbox['erro']}")
    else:
        total = dados_inbox["total_na_caixa"]
        mensagens = dados_inbox["mensagens"]
        st.info(f"📊 **Caixa Postal:** `{func_email}` • **Total de e-mails:** {total} • **Exibindo as {len(mensagens)} mensagens mais recentes**")

        if not mensagens:
            st.write("📭 Nenhum e-mail encontrado nesta caixa postal.")
        else:
            for i, msg in enumerate(mensagens):
                with st.expander(f"✉️ {msg['assunto']} — De: {msg['remetente']}", expanded=(i == 0)):
                    st.write(f"**De:** {msg['remetente']}")
                    st.write(f"**Data:** {msg['data']}")
                    st.write(f"**Assunto:** {msg['assunto']}")
                    st.divider()
                    st.markdown("**Conteúdo do E-mail:**")
                    st.text_area("Corpo:", value=msg['corpo'], height=160, key=f"txt_inbox_{func_inbox_sel}_{msg['id']}", disabled=True)
                    
                    if st.button(f"🧠 Analisar Intenção com IA (Mensagem #{msg['id']})", key=f"btn_analise_{func_inbox_sel}_{msg['id']}"):
                        with st.spinner("Analisando intenção e sugerindo resposta..."):
                            res_analise = analisar_intencao_resposta(msg['corpo'])
                            if res_analise["sucesso"]:
                                st.markdown("### 🎯 Parecer da Inteligência Comercial:")
                                st.markdown(res_analise["analise"])
                            else:
                                st.error(f"Erro ao analisar: {res_analise['erro']}")

# -------------------------------------------------------------
# ABA 7: AUDITORIA DE EDITAIS
# -------------------------------------------------------------
with tab_edital:
    st.subheader("Auditor de Termos de Referência (TR) e Editais")
    texto_tr = st.text_area("Cole trechos do Termo de Referência ou Especificação Técnica do cliente:", height=200, placeholder="Ex.: O cliente exige laudo NR-10 de condutores em canaletas...")
    if st.button("Auditar Escopo e Gerar Lista de Desvios", type="primary"):
        if texto_tr:
            with st.spinner("Auditando conformidade contra o Acervo..."):
                try:
                    analise = analisar_especificacao_tecnica(texto_tr)
                    salvar_markdown_saida("analise_edital.md", analise)
                    st.success("Auditoria concluída!")
                    st.markdown(analise)
                except Exception as e:
                    st.error(f"Erro na auditoria de edital: {e}")

# -------------------------------------------------------------
# ABA 7: PÓS-COMISSIONAMENTO E ART
# -------------------------------------------------------------
with tab_pos_obra:
    st.subheader("Sucesso do Cliente, DataBook As-Built e ART (CREA-MG)")
    dados_conclusao = st.text_area("Dados da Obra Recém-Concluída:", height=150, placeholder="Ex.: Cliente Mineração Vale, concluída parametrização de 6 relés SIPROTEC 5...")
    if st.button("Gerar Pacote de Encerramento e ART", type="primary"):
        if dados_conclusao:
            with st.spinner("Beatriz Silveira gerando índice de DataBook e minuta de ART..."):
                try:
                    pacote = gerar_pacote_encerramento(dados_conclusao)
                    salvar_markdown_saida("plano_pos_comissionamento.md", pacote)
                    st.success("Pacote de encerramento gerado!")
                    st.markdown(pacote)
                except Exception as e:
                    st.error(f"Erro ao gerar pacote de pós-obra: {e}")

# -------------------------------------------------------------
# ABA 8: BACKOFFICE E CONFORMIDADE HSE
# -------------------------------------------------------------
with tab_backoffice:
    st.subheader("Habilitação de Campo (NR-10/NR-35), Metrologia RBC e Medições")
    dados_backoffice = st.text_area("Dados da Mobilização ou Faturamento:", height=150, placeholder="Ex.: Mobilização de 2 técnicos com mala Conprove e faturamento da 2ª parcela...")
    if st.button("Gerar Dossiê de Conformidade e Medição", type="primary"):
        if dados_backoffice:
            with st.spinner("Auditando documentação de segurança e faturamento..."):
                try:
                    dossie = processar_conformidade_backoffice(dados_backoffice)
                    salvar_markdown_saida("conformidade_backoffice.md", dossie)
                    st.success("Dossiê gerado com sucesso!")
                    st.markdown(dossie)
                except Exception as e:
                    st.error(f"Erro ao gerar dossiê de backoffice: {e}")
