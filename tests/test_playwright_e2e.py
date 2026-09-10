"""Suite E2E com Playwright — Validação em Navegador Real (Chromium)

Cobre os 5 pilares fundamentais no ambiente web real com CanvasKit:
1. Infraestrutura & Servidor Flet Web (Startup, WebSocket, HTTP Headers & CanvasKit Loading)
2. Arquitetura & Prevenção de Tela Preta (BUG-11 Visual & Canvas Audit no /splash)
3. Navegação do Usuário e Roteamento Atômico (/splash -> /onboarding)
4. Segurança, Isolamento de Sessão e Auth no Browser (/admin)
5. Caligrafia Wongoji & Interatividade Touch no Canvas (/hangul)
"""

import os
import sys
import time
import socket
import subprocess
import pytest
from playwright.sync_api import sync_playwright
from PIL import Image


SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def find_free_port() -> int:
    """Encontra uma porta livre dinamicamente para evitar conflitos de porta."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def flet_server():
    """Sobe o servidor Flet Web em subprocesso isolado na porta alocada para os testes do Playwright."""
    port = find_free_port()
    base_url = f"http://127.0.0.1:{port}"
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    env = os.environ.copy()
    env["FLET_FORCE_WEB_SERVER"] = "true"
    env["PORT"] = str(port)
    env["FLET_SERVER_IP"] = "127.0.0.1"
    env["SAEBOM_ADMIN_PIN"] = "TestAdmin#2026"
    env["SEJONG_ADMIN_PIN"] = "TestAdmin#2026"

    proc = subprocess.Popen(
        [sys.executable, "main.py"],
        env=env,
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    start_time = time.time()
    started = False
    while time.time() - start_time < 20:
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            raise RuntimeError(
                f"Flet server process terminated early with code {proc.returncode}.\nSTDOUT: {stdout}\nSTDERR: {stderr}"
            )
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                started = True
                break
        except (OSError, ConnectionRefusedError):
            time.sleep(0.3)

    if not started:
        proc.terminate()
        proc.wait()
        raise TimeoutError(f"Servidor Flet não iniciou em 127.0.0.1:{port} dentro do prazo de 20s.")

    time.sleep(1.0)
    try:
        yield base_url
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


import hashlib


def file_hash(filepath: str) -> str:
    """Calcula o hash MD5 de um arquivo de screenshot."""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


class TestPlaywrightE2E:
    """Bateria de 5 testes E2E com Chromium real via Playwright com validação de unicidade visual."""

    def test_p1_infra_and_server_handshake(self, flet_server):
        """Teste 1 (Infra): Valida HTTP 200, WebSockets e título 'Saebom Companion' no Chromium real."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 384, "height": 715})
            page = context.new_page()

            ws_events = []
            page.on("websocket", lambda ws: ws_events.append(ws))

            # Acessar a raiz da aplicação
            response = page.goto(f"{flet_server}/", timeout=30000)
            assert response is not None, "Resposta HTTP não recebida do servidor Flet"
            assert response.status == 200, f"Status HTTP incorreto: {response.status}"

            # Aguardar o handshake do Flet atualizar o título da página
            page.wait_for_function("() => document.title.includes('Saebom')", timeout=20000)
            title = page.title()
            print(f"\n[Playwright] Título capturado no navegador: '{title}'")

            assert "Saebom Companion" in title, f"Título incorreto no navegador real: '{title}'"
            assert "Sejong" not in title, f"Termo proibido 'Sejong' no título do navegador: '{title}'"

            # Validar que a conexão WebSocket com o backend Python foi inicializada
            time.sleep(1.5)
            assert len(ws_events) > 0, "Nenhuma conexão WebSocket foi aberta pelo cliente Flutter/Flet"

            browser.close()

    def test_p2_architecture_and_black_screen_prevention(self, flet_server):
        """Teste 2 (Arquitetura/BUG-11): Valida renderização no /splash e ausência de tela preta."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 384, "height": 715})
            page = context.new_page()

            failed_requests = []
            page.on("requestfailed", lambda req: failed_requests.append(req.url))

            # Acessar a rota /splash em modo estático de auditoria visual (sem auto-redirect)
            page.goto(f"{flet_server}/splash?no_redirect=1", timeout=30000)

            # Aguardar renderização inicial do CanvasKit
            page.wait_for_function("() => document.title.includes('Saebom')", timeout=20000)
            time.sleep(3.0)

            # Capturar screenshot do navegador real
            screenshot_path = os.path.join(SCREENSHOT_DIR, "p2_splash_screen.png")
            screenshot_bytes = page.screenshot(path=screenshot_path)
            assert os.path.exists(screenshot_path), "Screenshot não foi gerado"
            print(f"\n[Playwright] Screenshot do /splash salvo em: {screenshot_path} ({len(screenshot_bytes)} bytes)")

            # Verificar se não houve 404 em assets críticos (BUG-11)
            for url in failed_requests:
                assert "app_icon" not in url, f"Asset crítico falhou no download: {url}"

            # Auditoria de luminância: verificar se a imagem não é tela preta vazia (BUG-11)
            img = Image.open(screenshot_path).convert("RGB")
            pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())
            # Pixels não-pretos (com alguma luminosidade visível)
            non_black = [px for px in pixels if sum(px) > 30]
            non_black_ratio = len(non_black) / len(pixels)

            print(f"[Playwright] Proporção de pixels renderizados não-pretos: {non_black_ratio:.2%}")
            assert non_black_ratio > 0.03, (
                f"TELA PRETA DETECTADA (BUG-11)! Proporção de conteúdo renderizado: {non_black_ratio:.2%}. "
                "O CanvasKit não desenhou os elementos da tela."
            )

            browser.close()

    def test_p3_user_navigation_and_console_integrity(self, flet_server):
        """Teste 3 (Roteamento & Ciclo de Vida): Valida rota direta /onboarding e zero erros JS."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 384, "height": 715})
            page = context.new_page()

            console_errors = []
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

            # Acessar rota /onboarding diretamente
            page.goto(f"{flet_server}/onboarding", timeout=30000)
            page.wait_for_function("() => document.title.includes('Saebom')", timeout=20000)
            time.sleep(2.5)

            screenshot_path = os.path.join(SCREENSHOT_DIR, "p3_onboarding_screen.png")
            page.screenshot(path=screenshot_path)
            assert os.path.exists(screenshot_path)
            print(f"\n[Playwright] Screenshot do /onboarding salvo em: {screenshot_path}")

            # Verificar ausência de erros graves de JavaScript ou WebAssembly no console
            critical_errors = [e for e in console_errors if "Uncaught" in e or "panic" in e or "TypeError" in e]
            assert not critical_errors, f"Erros críticos de JavaScript no console: {critical_errors}"

            # Garantir que a tela de onboarding não é idêntica à tela de splash
            p2_path = os.path.join(SCREENSHOT_DIR, "p2_splash_screen.png")
            if os.path.exists(p2_path):
                assert file_hash(screenshot_path) != file_hash(p2_path), "Tela de Onboarding está idêntica à Splash!"

            browser.close()

    def test_p4_admin_security_barrier(self, flet_server):
        """Teste 4 (Segurança): Valida barreira de login no /admin e ausência do PIN no DOM do cliente."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 384, "height": 715})
            page = context.new_page()

            page.goto(f"{flet_server}/admin", timeout=30000)
            page.wait_for_function("() => document.title.includes('Saebom')", timeout=20000)
            time.sleep(2.5)

            screenshot_path = os.path.join(SCREENSHOT_DIR, "p4_admin_login.png")
            page.screenshot(path=screenshot_path)
            assert os.path.exists(screenshot_path)
            print(f"\n[Playwright] Screenshot do /admin salvo em: {screenshot_path}")

            # O PIN real em texto claro NUNCA pode vazar no HTML/DOM do navegador
            html = page.content()
            assert "TestAdmin#2026" not in html, "Vazamento do PIN administrativo no HTML do cliente!"

            # Assegurar que a tela de login do admin é ÚNICA e não foi redirecionada para o onboarding
            p3_path = os.path.join(SCREENSHOT_DIR, "p3_onboarding_screen.png")
            if os.path.exists(p3_path):
                assert file_hash(screenshot_path) != file_hash(p3_path), (
                    "A rota /admin foi indevidamente redirecionada para o Onboarding!"
                )

            browser.close()

    def test_p5_wongoji_calligraphy_and_touch_interaction(self, flet_server):
        """Teste 5 (Caligrafia/Wongoji): Valida rota /hangul, alternância de aba e unicidade visual."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 384, "height": 715})
            page = context.new_page()

            page.goto(f"{flet_server}/hangul", timeout=30000)
            page.wait_for_function("() => document.title.includes('Saebom')", timeout=20000)
            time.sleep(2.5)

            # Screenshot inicial da rota /hangul (aba Vogais/Consoantes)
            screenshot_path = os.path.join(SCREENSHOT_DIR, "p5_hangul_view.png")
            page.screenshot(path=screenshot_path)
            assert os.path.exists(screenshot_path)
            print(f"\n[Playwright] Screenshot da aba Hangul salvo em: {screenshot_path}")

            # Garantir que a tela do Hangul não foi redirecionada para Onboarding ou Admin
            p3_path = os.path.join(SCREENSHOT_DIR, "p3_onboarding_screen.png")
            p4_path = os.path.join(SCREENSHOT_DIR, "p4_admin_login.png")
            if os.path.exists(p3_path):
                assert file_hash(screenshot_path) != file_hash(p3_path), "A rota /hangul foi redirecionada para Onboarding!"
            if os.path.exists(p4_path):
                assert file_hash(screenshot_path) != file_hash(p4_path), "A rota /hangul está idêntica ao Admin!"

            # Clicar na aba Caligrafia 원고지 (5ª aba na barra horizontal ~x=350, y=165)
            page.mouse.click(350, 165)
            time.sleep(1.5)

            # Capturar screenshot da grade de caligrafia 원고지
            post_draw_path = os.path.join(SCREENSHOT_DIR, "p5_hangul_drawn.png")
            page.screenshot(path=post_draw_path)
            assert os.path.exists(post_draw_path)
            print(f"[Playwright] Screenshot da grade Wongoji salvo em: {post_draw_path}")

            # Assegurar que a aba de caligrafia atualizou a tela
            assert file_hash(post_draw_path) != file_hash(screenshot_path), (
                "A aba de caligrafia não atualizou visualmente a tela do Hangul!"
            )

            # Auditoria de unicidade global: todas as 5 telas salvas DEVEM ter hashes MD5 distintos
            all_screenshots = [
                os.path.join(SCREENSHOT_DIR, "p2_splash_screen.png"),
                os.path.join(SCREENSHOT_DIR, "p3_onboarding_screen.png"),
                os.path.join(SCREENSHOT_DIR, "p4_admin_login.png"),
                os.path.join(SCREENSHOT_DIR, "p5_hangul_view.png"),
                os.path.join(SCREENSHOT_DIR, "p5_hangul_drawn.png"),
            ]
            existing_hashes = [file_hash(p) for p in all_screenshots if os.path.exists(p)]
            assert len(existing_hashes) == len(set(existing_hashes)), (
                f"Existem screenshots idênticas detectadas! Hashes encontrados: {existing_hashes}"
            )
            print(f"\n[Playwright] Auditoria de Unicidade Visual: {len(set(existing_hashes))}/5 telas únicas confirmadas!")

            browser.close()

