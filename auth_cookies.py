import os
import time
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import streamlit as st
from config import APP_USUARIO, APP_SENHA

# Nome padrão do cookie de sessão da KR Engenharia
NOME_COOKIE_AUTH = "kr_auth_session"

# Tempo limite de inatividade: 30 minutos (1800 segundos)
TIMEOUT_INATIVIDADE_SEGUNDOS = 30 * 60

# Chave secreta derivada para assinatura criptográfica segura
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", f"{APP_USUARIO}-{APP_SENHA}-kr-engenharia-2026")
SALT = "kr-auth-cookie-salt"

def get_serializer() -> URLSafeTimedSerializer:
    """Retorna o serializador criptográfico com assinatura baseada em tempo."""
    return URLSafeTimedSerializer(SECRET_KEY, salt=SALT)

def gerar_token_auth(usuario: str, session_id: str) -> str:
    """
    Gera um token assinado criptograficamente contendo os dados da sessão
    e o timestamp exato da última atividade do usuário.
    """
    s = get_serializer()
    dados = {
        "usuario": usuario,
        "session_id": session_id,
        "last_activity": time.time()
    }
    return s.dumps(dados)

def validar_token_auth(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Valida a autenticidade e o tempo de expiração do token.
    Retorna os dados da sessão se for válido e tiver menos de 30 minutos de inatividade.
    Retorna None se for inválido, adulterado ou se tiver mais de 30 minutos sem interação.
    """
    if not token or not isinstance(token, str):
        return None

    # Limpa possíveis aspas residuais do cookie
    token_limpo = token.strip().strip('"').strip("'")
    if not token_limpo:
        return None

    s = get_serializer()
    try:
        dados = s.loads(token_limpo, max_age=TIMEOUT_INATIVIDADE_SEGUNDOS)
        if not isinstance(dados, dict):
            return None

        last_activity = dados.get("last_activity", 0)
        tempo_decorrido = time.time() - last_activity

        # Validação estrita de inatividade (máximo 30 minutos)
        if tempo_decorrido > TIMEOUT_INATIVIDADE_SEGUNDOS:
            return None

        # Validação do usuário cadastrado
        if dados.get("usuario") != APP_USUARIO:
            return None

        return dados

    except (SignatureExpired, BadSignature, Exception):
        return None

def obter_token_cookie(cookie_controller=None) -> Optional[str]:
    """
    Tenta obter o token do cookie através de múltiplas camadas:
    1. st.context.cookies (nativo do Streamlit 1.63 - captura imediata na requisição HTTP no F5)
    2. cookie_controller.get (componente client-side, se disponível)
    """
    # Camada 1: Leitura direta dos headers da requisição HTTP (essencial para F5)
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            token_nativo = st.context.cookies.get(NOME_COOKIE_AUTH)
            if token_nativo:
                return str(token_nativo)
    except Exception:
        pass

    # Camada 2: Leitura via componente controller (se injetado)
    if cookie_controller is not None:
        try:
            token_ctrl = cookie_controller.get(NOME_COOKIE_AUTH)
            if token_ctrl:
                return str(token_ctrl)
        except Exception:
            pass

    return None

def gravar_cookie_auth(usuario: str, session_id: str, cookie_controller=None, reload_after: bool = False) -> str:
    """
    Grava o cookie de sessão com expiração de 30 minutos (1800 segundos) e salva no localStorage.
    Utiliza st.html com unsafe_allow_javascript=True diretamente no DOM da janela principal,
    garantindo que o cookie fique armazenado para o domínio da aplicação e seja enviado
    em toda requisição HTTP (inclusive no F5).
    Se reload_after=True, o navegador recarrega imediatamente após gravar, entrando autenticado.
    """
    token = gerar_token_auth(usuario, session_id)

    # 1. Grava no controller se disponível (camada complementar)
    if cookie_controller is not None:
        try:
            cookie_controller.set(
                name=NOME_COOKIE_AUTH,
                value=token,
                path="/",
                max_age=TIMEOUT_INATIVIDADE_SEGUNDOS,
                same_site="lax"
            )
        except Exception:
            pass

    # 2. Injeção direta de JavaScript no DOM superior (window.document)
    reload_js = "window.location.reload();" if reload_after else ""
    script_html = f"""
    <div style="display:none;" id="kr-cookie-setter">
      <script>
        (function() {{
          try {{
            var valor = "{token}";
            var maxAge = {TIMEOUT_INATIVIDADE_SEGUNDOS};
            var cookieStr = "{NOME_COOKIE_AUTH}=" + encodeURIComponent(valor) + "; max-age=" + maxAge + "; path=/; SameSite=Lax";
            document.cookie = cookieStr;
            try {{
              localStorage.setItem("{NOME_COOKIE_AUTH}", valor);
              sessionStorage.removeItem("kr_logged_out");
            }} catch(errLS) {{}}
            {reload_js}
          }} catch(e) {{
            {reload_js}
          }}
        }})();
      </script>
    </div>
    """
    try:
        st.html(script_html, unsafe_allow_javascript=True)
    except Exception as e:
        print(f"⚠️ Erro ao injetar script de cookie: {e}")

    return token

def remover_cookie_auth(cookie_controller=None, reload_after: bool = False):
    """
    Remove o cookie de autenticação do navegador (logout explícito ou expiração).
    Define max-age=0, limpa localStorage, sinaliza logout voluntário e recarrega na raiz limpa se reload_after=True.
    """
    if cookie_controller is not None:
        try:
            cookie_controller.remove(NOME_COOKIE_AUTH, path="/")
        except Exception:
            pass

    reload_js = "window.location.href = window.location.origin + window.location.pathname;" if reload_after else ""
    script_html = f"""
    <div style="display:none;" id="kr-cookie-remover">
      <script>
        (function() {{
          try {{
            var expCookie = "{NOME_COOKIE_AUTH}=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Lax";
            document.cookie = expCookie;
            try {{
              localStorage.removeItem("{NOME_COOKIE_AUTH}");
              sessionStorage.setItem("kr_logged_out", "1");
            }} catch(errLS) {{}}
            {reload_js}
          }} catch(e) {{
            {reload_js}
          }}
        }})();
      </script>
    </div>
    """
    try:
        st.html(script_html, unsafe_allow_javascript=True)
    except Exception as e:
        print(f"⚠️ Erro ao remover cookie: {e}")

def injetar_script_recuperacao_localstorage():
    """
    Executado na tela de login: se a URL não possui o parâmetro ?session=,
    mas o localStorage possui um token salvo dentro dos 30 min (e o usuário não efetuou logout voluntário),
    restaura a sessão adicionando o parâmetro na URL para autenticar de imediato.
    """
    script_html = f"""
    <div style="display:none;" id="kr-cookie-recovery">
      <script>
        (function() {{
          try {{
            if (sessionStorage.getItem("kr_logged_out") === "1") {{
              return;
            }}
            var urlParams = new URLSearchParams(window.location.search);
            if (!urlParams.get("session")) {{
              var saved = localStorage.getItem("{NOME_COOKIE_AUTH}");
              if (saved && saved.length > 20) {{
                window.location.href = window.location.origin + window.location.pathname + "?session=" + encodeURIComponent(saved);
              }}
            }}
          }} catch(e) {{}}
        }})();
      </script>
    </div>
    """
    try:
        st.html(script_html, unsafe_allow_javascript=True)
    except Exception:
        pass

def injetar_script_inatividade_30min():
    """
    Injeta um observador no cliente do navegador que monitora a inatividade do usuário:
    - Se o usuário ficar mais de 30 minutos sem nenhuma interação (clique, teclado, rolagem),
      o cookie e localStorage são removidos e a página é redirecionada para a URL limpa (sem query params).
    - Qualquer interação reinicia a contagem dos 30 minutos.
    """
    timeout_ms = TIMEOUT_INATIVIDADE_SEGUNDOS * 1000
    script_html = f"""
    <div style="display:none;" id="kr-cookie-watchdog">
      <script>
        (function() {{
          var timeoutMs = {timeout_ms};
          var timerId = null;

          function deslogarPorInatividade() {{
            try {{
              var expCookie = "{NOME_COOKIE_AUTH}=; max-age=0; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Lax";
              document.cookie = expCookie;
              try {{
                localStorage.removeItem("{NOME_COOKIE_AUTH}");
                sessionStorage.setItem("kr_logged_out", "1");
              }} catch(eLS) {{}}
              // Redireciona para o pathname puro limpando qualquer query param de sessão
              window.location.href = window.location.origin + window.location.pathname;
            }} catch(e) {{
              window.location.href = window.location.origin + window.location.pathname;
            }}
          }}

          function reiniciarContador() {{
            if (timerId) clearTimeout(timerId);
            timerId = setTimeout(deslogarPorInatividade, timeoutMs);
          }}

          reiniciarContador();

          var eventos = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'];
          eventos.forEach(function(evt) {{
            window.addEventListener(evt, reiniciarContador, {{ passive: true }});
          }});
        }})();
      </script>
    </div>
    """
    try:
        st.html(script_html, unsafe_allow_javascript=True)
    except Exception as e:
        print(f"⚠️ Erro ao injetar script de inatividade: {e}")

