import argparse
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

# --- Deploy em nuvem (Render/HuggingFace) vs. execução local (Windows) ---
# A plataforma de deploy injeta a env var PORT antes de subir o processo;
# localmente ela nunca existe, então caímos no default 8554 lá embaixo. Uso
# essa distinção pra decidir host/FLET_SERVER_IP, porque nuvem e Windows
# local precisam de valores opostos e incompatíveis entre si:
#   - Nuvem: precisa bindar em "0.0.0.0" (todas as interfaces) pra ser
#     alcançável de fora do container.
#   - Local/Windows: "0.0.0.0" faz o Flet tentar abrir o navegador em
#     http://0.0.0.0:..., que não é um endereço válido de destino ->
#     ERR_ADDRESS_INVALID. "*" evita esse problema (Flet mostra 127.0.0.1
#     no navegador), mas o Windows não aceita "*" como endereço de bind ->
#     getaddrinfo failed. "127.0.0.1" é o único que não quebra nenhum dos
#     dois pontos -- a única perda é acesso via celular/rede local (troque
#     pra "0.0.0.0" manualmente aqui se precisar testar no celular).
_IS_CLOUD_DEPLOY = "PORT" in os.environ
_HOST = "0.0.0.0" if _IS_CLOUD_DEPLOY else "127.0.0.1"

# FLET_SERVER_IP sobrescreve o host= passado pra ft.app() internamente (ver
# flet/app.py:run_async, "env_host = os.getenv('FLET_SERVER_IP')") -- os
# dois precisam ficar sincronizados, ou um valor divergente aqui reabre o
# ERR_ADDRESS_INVALID mesmo com o host= "certo" na chamada de ft.app().
os.environ["FLET_SERVER_IP"] = _HOST

import flet as ft
import flet_audio
from src.theme import apply_app_theme
from src.router import Router
from src.views import APP_ROUTES

from src.services import FullscreenService

def main(page: ft.Page):
    # Definir o modo de tema padrão (Escuro - Midnight Blue)
    page.theme_mode = ft.ThemeMode.DARK
        
    # Aplicar o Design System (fontes e configurações de tema)
    apply_app_theme(page)

    # Configurações de layout responsivo mobile (384x715)
    page.padding = 0
    page.spacing = 0
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Configurar responsividade mobile / PWA e viewport de tela cheia
    FullscreenService.setup_mobile_responsive_viewport(page)

    # Inicializar o Roteador Global
    router = Router(page)
    
    # Injetar o roteador no objeto page para acesso global nas views
    page.router = router

    # Registrar rotas do aplicativo
    for route_name, view_builder in APP_ROUTES.items():
        router.register_route(route_name, view_builder)

    # Inicializar o servico de audio global
    from src.audio_service import AudioService
    page.audio_service = AudioService(page)

    # Iniciar navegando para a tela de abertura
    router.navigate_to("/splash")

if __name__ == "__main__":
    print(f"Sejong Companion v{__version__}")
    port = int(os.environ.get("PORT", 8554))

    parser = argparse.ArgumentParser(description="Sejong Companion")
    parser.add_argument(
        "--browser",
        action="store_true",
        help=(
            "Abre no navegador (AppView.WEB_BROWSER) em vez da janela desktop "
            "nativa (o padrão do ft.app() quando view= não é passado). Use "
            "isso pra testar responsividade mobile/PWA -- o viewport injetado "
            "por FullscreenService só faz sentido em contexto de página HTML "
            "de verdade, não na janela nativa (ver bugfix em src/services.py)."
        ),
    )
    args = parser.parse_args()

    if _IS_CLOUD_DEPLOY:
        # Deploy headless: sempre navegador -- não tem display pra abrir
        # janela nativa num container Linux (Render/HuggingFace).
        view = ft.AppView.WEB_BROWSER
    else:
        view = ft.AppView.WEB_BROWSER if args.browser else ft.AppView.FLET_APP

    # Usar ft.run (Flet >= 0.80) com fallback para ft.app
    app_runner = getattr(ft, "run", ft.app)
    app_runner(main, host=_HOST, port=port, assets_dir="assets", view=view)
