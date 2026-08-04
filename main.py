import os
from src import __version__


def load_local_env():
    """Load local development secrets without adding a dotenv dependency."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                if key and key not in os.environ:
                    os.environ[key] = value.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass


load_local_env()
# Rodando só em 127.0.0.1 (localhost) por padrão. Testei "0.0.0.0" e "*"
# aqui e os dois quebram em algum ponto no Windows:
#   - "0.0.0.0" faz o Flet tentar ABRIR o navegador em http://0.0.0.0:...,
#     que não é um endereço válido de destino -> ERR_ADDRESS_INVALID.
#   - "*" evita esse problema (Flet mostra 127.0.0.1 no navegador), mas o
#     Windows não aceita "*" como endereço de bind -> getaddrinfo failed.
# "127.0.0.1" não tem nenhum desses problemas: bind confiável + navegador
# abre certinho. A única perda é acesso pelo celular/rede local.
#
# Se algum dia precisar testar no celular (mesma rede Wi-Fi), troque a
# linha abaixo para "0.0.0.0" temporariamente. O navegador do PC pode não
# abrir sozinho nesse modo (aí você abre manualmente http://localhost:8554
# no PC), e no celular você digita o IP local do PC, ex: http://192.168.15.140:8554
os.environ["FLET_SERVER_IP"] = "0.0.0.0"

import flet as ft
import flet_audio
from src.theme import apply_app_theme
from src.router import Router
from src.views.splash_view import splash_view
from src.views.home_view import home_view
from src.views.hangul_view import hangul_view
from src.views.lesson_view import lesson_view
from src.views.quiz_view import quiz_view
from src.views.ui_test_view import ui_test_view

from src.services import FullscreenService

def main(page: ft.Page):
    # Definir o modo de tema padrão (Escuro - Midnight Blue)
    page.theme_mode = ft.ThemeMode.DARK
        
    # Aplicar o Design System (fontes e configurações de tema)
    apply_app_theme(page)

    # Configurações de layout responsivo mobile (384x715)
    page.padding = 0
    page.spacing = 0

    # Configurar responsividade mobile / PWA e viewport de tela cheia
    FullscreenService.setup_mobile_responsive_viewport(page)

    # Inicializar o Roteador Global
    router = Router(page)
    
    # Injetar o roteador no objeto page para acesso global nas views
    page.router = router

    # Registrar rotas do aplicativo
    router.register_route("/splash", splash_view)
    router.register_route("/home", home_view)
    router.register_route("/hangul", hangul_view)
    router.register_route("/lesson", lesson_view)
    router.register_route("/quiz", quiz_view)
    router.register_route("/ui_test", ui_test_view)

    # Inicializar o servico de audio global
    from src.audio_service import AudioService
    page.audio_service = AudioService(page)

    # Iniciar navegando para a tela de abertura
    router.navigate_to("/splash")

if __name__ == "__main__":
    print(f"Sejong Companion v{__version__}")
    # Executa no navegador web, em localhost (127.0.0.1)
    ft.run(main, view=ft.AppView.WEB_BROWSER, host="127.0.0.1", port=8554, assets_dir="assets")
