import io
import re
import requests
import pandas as pd
import streamlit as st

# =========================================
# CONFIGURAÇÃO BASE DA PÁGINA
# =========================================
st.set_page_config(
    page_title="WS Transportes | Envio WhatsApp",
    layout="wide",
)

# =========================================
# CSS COMPLETO (com remoção total da barra superior do Streamlit)
# =========================================
st.markdown(
    """
    <style>
    /* ============================================= */
    /* REMOÇÃO COMPLETA DA BARRA PRETA SUPERIOR DO STREAMLIT */
    /* ============================================= */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    /* Remove o espaço vazio que ficava acima do conteúdo */
    .css-1d391kg, .css-1v0mbtd, .css-1wrcr25, .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    /* Garante que o primeiro elemento suba até o topo */
    .main > div:first-child {
        padding-top: 0 !important;
    }

    /* ===== Layout base ===== */
    body {
        background-color: #05060A;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 900px;
        margin: 0 auto;
    }

    .main {
        padding-top: 0;
    }

    /* (tentativa extra, não atrapalha nada) */
    .block-container > div[data-testid="stTextInput"] {
        display: none !important;
    }

    /* ===== Login card menor e MAIS PRA CIMA pra cobrir a barra ===== */
    .login-card {
        max-width: 620px;
        margin: -2.3rem auto 1rem auto;  /* top negativo cobre qualquer resquício */
        background: #14151B;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 14px 32px rgba(0,0,0,0.5);
        border: 1px solid #262733;
    }
    .login-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: .3rem;
    }
    .login-subtitle {
        color: #c7c7d2;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .ws-color {
        color: #FFFFFF;
    }
    .error-box {
        background:#3b1515;
        border-radius:12px;
        border:1px solid #ff6961;
        padding:0.8rem 1rem;
        margin-top:0.8rem;
        color:#ffdede;
        font-size:0.9rem;
    }
    .success-box {
        background:#12351c;
        border-radius:12px;
        border:1px solid #32cd72;
        padding:0.8rem 1rem;
        margin-top:0.8rem;
        color:#d0ffe1;
        font-size:0.9rem;
    }
    .login-logo img {
        border-radius: 18px;
        max-width: 210px;
        margin: 0 auto;
        display: block;
    }
    .btn-entrar button {
        background:#ff4b4b !important;
        color:white !important;
        border-radius:999px !important;
        font-weight:600 !important;
        height:2.4rem;
        border:none;
        font-size:0.92rem;
    }
    .btn-entrar button:hover {
        filter:brightness(1.05);
    }

    /* ===== Header do app principal ===== */
    .app-header {
        display:flex;
        align-items:flex-start;
        justify-content:space-between;
        gap:1rem;
        margin-bottom:1rem;
    }
    .app-title-main {
        font-size:1.9rem;
        font-weight:700;
        color:#FFFFFF;
        margin-bottom:0.2rem;
    }
    .app-title-main span {
        color:#FFFFFF;
    }
    .app-subtitle {
        color:#c7c7d2;
        font-size:0.93rem;
        margin-bottom: 0;
    }

    /* ===== Badge da sessão ===== */
    .app-badge {
        align-self:flex-start;
        padding:0.4rem 1rem;
        border-radius:999px;
        border:1px solid #343542;
        background:#181924;
        color:#e3e3f0;
        display:flex;
        flex-direction:row;
        align-items:center;
        gap:0.5rem;
        white-space:nowrap;
        font-size:0.82rem;
    }
    .app-badge span {
        font-size:0.8rem;
        opacity:0.9;
    }
    .app-badge code {
        background:rgba(0,0,0,0.35);
        padding:0.15rem 0.7rem;
        border-radius:999px;
        font-size:0.84rem;
        color:#F9A826;
        font-family:monospace;
    }

    /* ===== Pílulas de passos ===== */
    .pill-steps {
        display:flex;
        gap:0.4rem;
        flex-wrap:wrap;
        margin-bottom:0.6rem;
    }
    .pill {
        font-size:0.78rem;
        padding:0.2rem 0.6rem;
        border-radius:999px;
        border:1px solid #333446;
        color:#c9c9db;
        background:#171822;
    }
    .pill span {
        color:#F9A826;
        font-weight:600;
        margin-right:0.2rem;
    }

    /* DataFrame */
    .stDataFrame {
        border-radius:12px;
        overflow:hidden;
        border:1px solid #262733;
    }

    /* Barra de progresso */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #F9A826, #ff4b4b);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0d0e13;
        border-right: 1px solid #262733;
    }
    .sidebar-exit button {
        border-radius:999px !important;
        border:1px solid #ff4b4b !important;
        color:#ffb3b3 !important;
        background:transparent !important;
        font-weight:500 !important;
    }

    /* Log de envios */
    .log-box {
        background:#101118;
        border-radius:12px;
        border:1px solid #262733;
        padding:0.6rem 0.8rem;
        font-size:0.86rem;
        color:#d6d6e5;
        min-height:2.5rem;
        margin-bottom: 0.5rem;
    }

    .stContainer { margin-bottom: 0.5rem; }
    .stMarkdown { margin-bottom: 0.5rem; }
    .stButton { margin-bottom: 0.5rem; }
    .stEmpty { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================
# ESTADO GLOBAL
# =========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "api_session" not in st.session_state:
    st.session_state.api_session = ""
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = ""
if "api_token" not in st.session_state:
    st.session_state.api_token = ""

# =========================================
# FUNÇÕES DE BACKEND
# =========================================
def normalizar_numero(raw: str) -> str:
    s = "".join(ch for ch in str(raw) if ch.isdigit())
    if not s:
        raise ValueError("Telefone vazio")
    if not s.startswith("55"):
        s = "55" + s
    return s

def montar_mensagem(nome, nf, integracao, vendedor):
    return (
        "Confirmação para entrega!\n\n"
        f"Olá, sou Rharianne da transportadora *WS TRANSPORTES*. "
        f"Estou falando com *{nome}*?\n\n"
        "Estou entrando em contato para confirmar se este número está ativo "
        "e se o endereço de destino está correto para seguirmos com a rota de entrega do seu pedido!\n\n"
        f"NF-e: {nf}\n"
        f"Integração (Pedido): {integracao}\n"
        f"Vendedor(a): {vendedor}\n\n"
        "Para facilitar a entrega, poderia me informar um ponto de referência próximo ao endereço?"
    )

def testar_conexao(session: str, base_url: str, token: str):
    url_base = base_url.rstrip("/")
    url = f"{url_base}/api/{session}/check-connection-session"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.exceptions.ConnectionError as e:
        msg = (
            "Não consegui falar com o servidor WPPConnect.\n\n"
            "• Confira se o `npm start` está rodando na pasta do wppconnect-server.\n"
            "• Confira se a *API Base URL* está correta (host e porta)."
        )
        return False, msg, str(e)
    except Exception as e:
        return False, "Erro inesperado ao tentar conectar na API.", str(e)

    if resp.status_code in (401, 403):
        return (
            False,
            "Token inválido ou não autorizado.\n\n"
            "• Gere um novo token no Swagger (endpoint `generate-token`).\n"
            "• Cole o token completo aqui em *Token (Bearer)*.",
            f"HTTP {resp.status_code}: {resp.text}",
        )

    if resp.status_code >= 500:
        return (
            False,
            "O servidor WPPConnect retornou erro interno (5xx).\n"
            "Tenta novamente em alguns segundos ou reinicia o `npm start`.",
            f"HTTP {resp.status_code}: {resp.text}",
        )

    try:
        data = resp.json()
    except Exception:
        return False, "Resposta inesperada da API.", resp.text

    if not data.get("status"):
        return (
            False,
            "Consegui falar com o servidor, mas a sessão não está conectada ao WhatsApp.\n\n"
            "• Verifique no Swagger se a sessão está *Connected*.\n"
            "• Se precisar, apague o token, gere outro e pareie novamente.",
            str(data),
        )

    return True, "Conexão com WPPConnect realizada com sucesso. Sessão conectada", str(data)

def enviar_mensagem_ws(base_url, session, token, phone, texto):
    url_base = base_url.rstrip("/")
    url = f"{url_base}/api/{session}/send-message"
    payload = {
        "phone": phone,
        "isGroup": False,
        "isNewsletter": False,
        "isLid": False,
        "message": texto,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=20)
        data = r.json()
    except Exception as e:
        return False, {"error": str(e)}

    if r.status_code >= 400:
        return False, data

    msg_text = str(data)
    if "não existe" in msg_text.lower():
        return False, data

    status = data.get("status")
    if status in (True, "success"):
        return True, data

    return False, data

# =========================================
# TELA 1 – LOGIN / CONFIG DA API
# =========================================
def tela_login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    col_logo, col_form = st.columns([1, 2])

    with col_logo:
        try:
            st.image("ws_logo.png", use_container_width=True)
        except Exception:
            pass

    with col_form:
        st.markdown(
            '<div class="login-title">Login WPPConnect – '
            '<span class="ws-color">WS Transportes</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-subtitle">'
            "Conecte o painel ao servidor WPPConnect antes de realizar os envios. "
            "Garanta que o serviço esteja rodando com <code>npm start</code> na máquina configurada."
            "</div>",
            unsafe_allow_html=True,
        )

        session = st.text_input(
            "Session",
            value=st.session_state.api_session or "NERDWHATS_AMERICA",
            help="Nome da sessão configurada no wppconnect-server.",
        )
        base_url = st.text_input(
            "API Base URL",
            value=st.session_state.api_base_url or "http://localhost:21465",
            help="Endereço onde o wppconnect-server está rodando.",
        )
        token = st.text_input(
            "Token (Bearer)",
            type="password",
            value=st.session_state.api_token or "",
            help="Token gerado no Swagger (endpoint generate-token).",
        )

        erro_msg = st.session_state.get("login_error_msg")
        erro_det = st.session_state.get("login_error_detail")
        ok_msg = st.session_state.get("login_ok_msg")

        col_btn = st.container()
        with col_btn:
            st.markdown('<div class="btn-entrar">', unsafe_allow_html=True)
            entrar = st.button("Entrar", use_container_width=True, type="primary")
            st.markdown("</div>", unsafe_allow_html=True)

        if entrar:
            st.session_state.login_error_msg = None
            st.session_state.login_error_detail = None
            st.session_state.login_ok_msg = None

            with st.spinner("Testando conexão com WPPConnect..."):
                ok, msg_amigavel, detalhe = testar_conexao(session, base_url, token)

            if ok:
                st.session_state.logged_in = True
                st.session_state.api_session = session
                st.session_state.api_base_url = base_url
                st.session_state.api_token = token
                st.session_state.login_ok_msg = msg_amigavel
                st.rerun()
            else:
                st.session_state.logged_in = False
                st.session_state.api_session = session
                st.session_state.api_base_url = base_url
                st.session_state.api_token = token
                st.session_state.login_error_msg = msg_amigavel
                st.session_state.login_error_detail = detalhe

        if erro_msg:
            msg_html = erro_msg.replace("\n", "<br/>")
            det_html = (erro_det or "").replace("\n", "<br/>")
            st.markdown(
                f"""
                <div class="error-box">
                    <b>Não consegui conectar na API do WPPConnect.</b><br/><br/>
                    {msg_html}<br/><br/>
                    <small><b>Detalhe técnico:</b> {det_html}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif ok_msg:
            ok_html = ok_msg.replace("\n", "<br/>")
            st.markdown(
                f"""
                <div class="success-box">
                {ok_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================
# TELA 2 – APP PRINCIPAL (ENVIO)
# =========================================
def tela_envio():
    # --- Sidebar ---
    st.sidebar.title("Configuração da API")
    st.sidebar.text_input("Session", value=st.session_state.api_session, disabled=True)
    st.sidebar.text_input("API Base URL", value=st.session_state.api_base_url, disabled=True)
    st.sidebar.text_input("Token (Bearer)", value=st.session_state.api_token, type="password", disabled=True)

    st.sidebar.markdown('<div class="sidebar-exit">', unsafe_allow_html=True)
    if st.sidebar.button("Sair / Trocar conexão"):
        st.session_state.logged_in = False
        st.session_state.login_ok_msg = None
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # --- Header principal ---
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <div class="app-title-main">Envio WhatsApp <span>WS Transportes</span></div>
                <div class="app-subtitle">
                    Automatize a confirmação de entregas a partir de uma planilha Excel, com status de envio por cliente.
                </div>
            </div>
            <div class="app-badge">
                <span>Sessão conectada:</span>
                <code>{st.session_state.api_session}</code>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="pill-steps">
            <div class="pill"><span>1.</span>Importar base de clientes</div>
            <div class="pill"><span>2.</span>Conferir pré-visualização</div>
            <div class="pill"><span>3.</span>Disparar mensagens e baixar relatório</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ===== Base de contatos =====
    st.markdown("### Base de contatos")
    st.markdown(
        "Utilize uma planilha com as colunas: "
        "`NOME / RAZÃO SOCIAL`, `TELEFONE`, `INTEGRACAO`, `Nº`, `VENDEDOR`, `DATA ENTREGA`, `OptOut`."
    )

    arquivo = st.file_uploader("Selecione a planilha Excel", type=["xlsx", "xls"])

    if arquivo is None:
        st.info("Faça o upload de uma planilha para começar.")
        return

    try:
        df = pd.read_excel(arquivo)
    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
        return

    st.subheader("Pré-visualização dos dados")
    st.dataframe(df.head(), use_container_width=True)

    # ===== Configurações de envio =====
    st.markdown("### Configurações de envio")
    col1, col2 = st.columns([1, 1])
    with col1:
        inicio = st.button("Iniciar envio", type="primary", use_container_width=True)
    with col2:
        so_teste = st.checkbox("Modo teste (não chamar API)", value=False)

    if not inicio:
        return

    # --- Processamento / envio ---
    COL_NOME = "NOME / RAZÃO SOCIAL"
    COL_NUMERO = "TELEFONE"
    COL_INTEGRACAO = "INTEGRACAO"
    COL_NF = "Nº"
    COL_VENDEDOR = "VENDEDOR"
    COL_OPTOUT = "OptOut"

    faltando = [c for c in [COL_NOME, COL_NUMERO, COL_INTEGRACAO, COL_NF, COL_VENDEDOR] if c not in df.columns]
    if faltando:
        st.error(f"As colunas obrigatórias não foram encontradas na planilha: {', '.join(faltando)}")
        return

    resultados = []
    total = len(df)
    enviados = 0
    falhas = 0

    st.markdown("### Progresso dos envios")
    barra = st.progress(0)
    log_container = st.empty()

    for i, row in df.iterrows():
        nome = str(row[COL_NOME]).strip()
        tel_raw = row[COL_NUMERO]
        integracao = str(row[COL_INTEGRACAO]).strip()
        nf = str(row[COL_NF]).strip()
        vendedor = str(row[COL_VENDEDOR]).strip()
        optout = str(row.get(COL_OPTOUT, "")).strip().lower()

        status_envio = "OK"
        detalhe = ""

        if optout in ("sim", "s", "1", "true"):
            status_envio = "Pulado (OptOut)"
            detalhe = "Cliente marcado para não receber mensagem."
        else:
            try:
                phone = normalizar_numero(tel_raw)
            except Exception as e:
                status_envio = "Falha"
                detalhe = f"Telefone inválido: {e}"
                falhas += 1
            else:
                msg = montar_mensagem(nome, nf, integracao, vendedor)

                if so_teste:
                    status_envio = "Simulado"
                    detalhe = "Modo teste: API não foi chamada."
                else:
                    ok, resp = enviar_mensagem_ws(
                        st.session_state.api_base_url,
                        st.session_state.api_session,
                        st.session_state.api_token,
                        phone,
                        msg,
                    )
                    if ok:
                        status_envio = "Enviado"
                        enviados += 1
                    else:
                        status_envio = "Falha"
                        detalhe = str(resp)
                        falhas += 1

        resultados.append(
            {
                "Nome": nome,
                "Telefone": str(tel_raw),
                "NF": nf,
                "Integracao": integracao,
                "Vendedor": vendedor,
                "Status": status_envio,
                "Detalhe": detalhe,
            }
        )

        barra.progress(int((i + 1) / total * 100))
        log_container.markdown(
            f'<div class="log-box">Enviando para <b>{nome}</b> ({tel_raw})...<br/>Status: <b>{status_envio}</b></div>',
            unsafe_allow_html=True,
        )

    st.success(f"Envio finalizado! Enviados: {enviados} | Falhas: {falhas}")

    # ===== Relatório final =====
    st.markdown("### Relatório de envios")
    st.markdown(
        "Visualize o status por cliente e baixe o relatório em Excel para registrar o disparo."
    )

    df_result = pd.DataFrame(resultados)
    st.dataframe(df_result, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_result.to_excel(writer, index=False, sheet_name="Envios")

    st.download_button(
        "Baixar relatório em Excel",
        data=buffer.getvalue(),
        file_name="relatorio_envio_whatsapp.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

# =========================================
# FLUXO PRINCIPAL
# =========================================
if not st.session_state.logged_in:
    tela_login()
else:
    tela_envio()