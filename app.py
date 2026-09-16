import os
import uuid
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
    st.subheader("Inteligência Comercial & Abordagem B2B no LinkedIn")
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
        with st.spinner("Lucas Campos mapeando decisores e estruturando abordagem..."):
            try:
                cadencia = gerar_cadencia_prospeccao(empresa_alvo, servico_foco)
                link_linkedin = gerar_link_busca_linkedin(empresa_alvo, cargo_busca)
                salvar_markdown_saida("cadencia_prospeccao.md", cadencia)
                
                st.session_state.cadencia_atual = cadencia
                st.session_state.empresa_atual = empresa_alvo
                    
                st.success("Estratégia de Abordagem Concluída!")
                st.link_button(
                    label=f"🔗 Abrir Busca de {cargo_busca} na {empresa_alvo} no LinkedIn",
                    url=link_linkedin
                )
                st.markdown(cadencia)
            except Exception as e:
                st.error(f"Erro ao gerar prospecção: {e}")

    if "cadencia_atual" in st.session_state:
        st.divider()
        st.markdown("### 📧 Disparo Oficial de E-mail via Lucas Campos")
        st.caption("Envio autônomo diretamente da conta institucional `lucas.campos@krconsultoria.com.br` via Titan SMTP.")
        
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
                with st.spinner(f"Lucas Campos conectando à conta e disparando e-mail para {destinatario_email}..."):
                    res_envio = enviar_email_funcionario(
                        funcionario_id="LUCAS",
                        destinatario=destinatario_email,
                        assunto=assunto_email,
                        corpo_texto=st.session_state.cadencia_atual
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
