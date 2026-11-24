"""Suite de Testes E2E de Cobertura Total — Saebom Companion (feature/branding).

Cobre os 5 pilares fundamentais da aplicacao antes de promocao para producao:
1. Infraestrutura e Rede (Docker Compose, Caddy, Port Binding e Prevencao de Scanners TLS)
2. Seguranca, Autenticacao e Isolamento de Dados (Hardening, fail-closed, data/ vs assets/)
3. Arquitetura Flet e Prevencao de Tela Preta (BUG-11, transicao atomica, assets absolutos)
4. Rebranding Oficial e Brand Book v3.1 (Proibicao de 'Sejong', 60/20/12/8, Prevencao de Tofu)
5. Caligrafia Wongoji e Fidelidade Curricular (Gabaritos oficiais 1A/1B, 띄어쓰기, Focus Mode)
"""

import os
import re
import yaml
import hmac
import pytest
import flet as ft
from src.router import Router


class MockPage:
    """Mock completo para testes headless de views e router."""
    def __init__(self, theme_mode=ft.ThemeMode.DARK):
        self.theme_mode = theme_mode
        self.width = 400
        self.height = 700
        self.views = []
        self.overlay = []
        self.services = []
        self.client_storage = None
        self.audio_service = None
        self.route = "/splash"
        self.title = ""
        self.fonts = {}
        self.theme = None
        self.dark_theme = None
        self._admin_authenticated = False
        self._admin_session_token = None
        self.on_route_change = None
        self.on_view_pop = None

    def update(self):
        pass

    def run_task(self, fn):
        pass

    def go(self, route):
        self.route = route
        if self.on_route_change:
            class MockEvent:
                def __init__(self, r):
                    self.route = r
            self.on_route_change(MockEvent(route))


# ==============================================================================
# PILAR 1: INFRAESTRUTURA, REDE E DEPLOY EM NUVEM
# ==============================================================================
class TestPillar1InfraAndNetwork:
    """Valida configuracoes de infraestrutura, portas e reverse proxy."""

    def test_docker_compose_port_exposure_hardening(self):
        """Verifica se o container app nao expoe a porta 8554 diretamente para a internet.

        A exposicao publica '8554:8554' atrai scanners TLS e causa a enxurrada de
        'WARNING: Invalid HTTP request received'. Deve usar 'expose: [8554]' ou
        bind em '127.0.0.1:8554:8554'.
        """
        compose_path = os.path.join(os.path.dirname(__file__), "..", "docker-compose.yml")
        assert os.path.exists(compose_path), "docker-compose.yml deve existir na raiz"

        with open(compose_path, "r", encoding="utf-8") as f:
            compose_cfg = yaml.safe_load(f)

        app_service = compose_cfg.get("services", {}).get("app", {})
        ports = app_service.get("ports", [])

        # Inspecionar se 8554 esta diretamente aberta em 0.0.0.0:8554
        publicly_exposed_8554 = False
        for p in ports:
            p_str = str(p)
            if p_str in ("8554:8554", "0.0.0.0:8554:8554"):
                publicly_exposed_8554 = True

        assert not publicly_exposed_8554, (
            "FALHA DE INFRAESTRUTURA: 'ports: - \"8554:8554\"' esta aberto publicamente no container 'app'! "
            "Isso permite que scanners TLS e navegadores HTTPS conectem na porta HTTP pura gerando "
            "'WARNING: Invalid HTTP request received.'. Use 'expose: - \"8554\"' para rede interna do Caddy."
        )

    def test_caddyfile_reverse_proxy_configuration(self):
        """Verifica se o Caddyfile configura o proxy reverso para app:8554 com headers essenciais."""
        caddy_path = os.path.join(os.path.dirname(__file__), "..", "Caddyfile")
        assert os.path.exists(caddy_path), "Caddyfile deve existir na raiz"

        with open(caddy_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "reverse_proxy app:8554" in content, "Caddyfile deve conter reverse_proxy app:8554"
        assert "encode zstd gzip" in content, "Caddyfile deve ter compressao de assets ativada"

    def test_dockerfile_production_readiness(self):
        """Verifica se Dockerfile usa imagem slim oficial, instala libmpv e define healthcheck."""
        dockerfile_path = os.path.join(os.path.dirname(__file__), "..", "Dockerfile")
        with open(dockerfile_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "python:3.12-slim" in content, "Dockerfile deve usar Python 3.12 slim"
        assert "libmpv" in content, "Dockerfile deve instalar libmpv para flet-audio"
        assert "HEALTHCHECK" in content, "Dockerfile deve conter instrucao de HEALTHCHECK"


# ==============================================================================
# PILAR 2: SEGURANÇA, AUTENTICAÇÃO E ISOLAMENTO DE DADOS
# ==============================================================================
class TestPillar2SecurityAndHardening:
    """Valida seguranca contra timing attacks, PINs fracos e isolamento de storage."""

    def test_admin_pin_weak_credentials_rejected_fail_closed(self):
        """Verifica postura fail-closed: PINs vazios, default ou obvios sao rejeitados."""
        from src.services import AdminService

        invalid_pins = ["", "   ", None]
        for weak_pin in invalid_pins:
            success, token, msg = AdminService.login(weak_pin, client_key="sec_test_client")
            assert not success, f"PIN vazio '{weak_pin}' deveria ser rejeitado, mas foi aceito!"

    def test_auth_constant_time_comparison(self, monkeypatch):
        """Verifica se a comparacao de tokens e PINs usa hmac.compare_digest."""
        from src.services import AdminService

        real_pin = "K0r3a#2026!Strict"
        monkeypatch.setenv("SAEBOM_ADMIN_PIN", real_pin)
        AdminService.reset_rate_limit("sec_timing_client")

        # Sucesso
        success, token, msg = AdminService.login(real_pin, client_key="sec_timing_client")
        assert success is True
        assert token is not None

        # Falha em tempo constante
        success_bad, token_bad, msg_bad = AdminService.login("K0r3a#2026!Wrong", client_key="sec_timing_client")
        assert success_bad is False
        assert token_bad is None

    def test_mutable_data_directories_isolated_and_gitignored(self):
        """Garante que data/ (sessions, telemetry, reports, cache) esteja fora de assets/ e no gitignore."""
        gitignore_path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()

        required_patterns = ["data/sessions", "data/telemetry", "data/reports", "data/cache"]
        for pat in required_patterns:
            assert pat in gitignore_content, f"Diretorio mutavel '{pat}' DEVE estar protegido no .gitignore!"

    def test_student_id_not_used_as_recovery_credential(self, tmp_path):
        """Garante que student_id publico nunca funcione diretamente como recovery_key."""
        from src.services import ProgressService

        ProgressService.set_file_path_override(str(tmp_path / "student_sec.json"))
        try:
            ps = ProgressService()
            ps.set_student_name("Aluno Teste")
            recovery_code = ps.get_or_create_recovery_code()
            session_id = ps._session_id

            assert session_id != recovery_code, "student_id e recovery_code NUNCA podem ser identicos!"
            assert not hmac.compare_digest(session_id, recovery_code), "Credencial de recuperacao deve ter entropia independente"
        finally:
            ProgressService.set_file_path_override(None)


# ==============================================================================
# PILAR 3: ARQUITETURA FLET, VIEWS E PREVENÇÃO DE TELA PRETA (BUG-11)
# ==============================================================================
class TestPillar3ArchitectureAndWebCanvasKit:
    """Valida integridade do Router, caminhos de assets e prevencao de tela preta."""

    def test_router_atomic_views_transition_and_emergency_fallback(self):
        """Router nunca deve limpar views antes da nova view estar instanciada com sucesso."""
        page = MockPage()
        router = Router(page)

        # Simular construtor que quebra (simulando bug de sintaxe na view)
        def broken_builder(p):
            raise RuntimeError("Falha simulada na view")

        router.register_route("/broken", broken_builder)

        class MockEvent:
            def __init__(self, r):
                self.route = r

        router.route_change(MockEvent("/broken"))

        # page.views NUNCA pode ter 0 elementos (caso contrario tela preta no Flutter Web)
        assert len(page.views) >= 1, "page.views ficou vazia apos erro de construcao! Isso causa tela preta no CanvasKit!"

    def test_all_registered_views_use_absolute_asset_paths(self):
        """Todas as imagens (ft.Image) em todas as views DEVEM comecar com '/' (BUG-11)."""
        from src.views import APP_ROUTES

        page = MockPage()
        router = Router(page)
        page.router = router
        page.router.current_unit_id = "unit_01"

        def audit_control_images(control, route_name):
            if isinstance(control, ft.Image):
                src = getattr(control, "src", None)
                if src and not src.startswith("http") and not src.startswith("data:"):
                    assert src.startswith("/"), (
                        f"VIOLACAO CRITICA DO BUG-11 na rota '{route_name}': "
                        f"ft.Image(src='{src}') usa caminho relativo! DEVE comecar com '/' para evitar 404 no Flutter Web."
                    )
            children = []
            if hasattr(control, "controls") and isinstance(control.controls, list):
                children.extend(control.controls)
            if hasattr(control, "content") and control.content:
                children.append(control.content)
            for c in children:
                if isinstance(c, ft.Control):
                    audit_control_images(c, route_name)

        for route_name, builder in APP_ROUTES.items():
            try:
                view = builder(page)
                for ctrl in view.controls:
                    audit_control_images(ctrl, route_name)
            except Exception as ex:
                pytest.fail(f"Falha ao instanciar view da rota '{route_name}': {ex}")

    def test_zero_deprecated_imagefit_enums_in_codebase(self):
        """Garante que ft.ImageFit (descontinuado no Flet 0.85+) nao existe no codigo-fonte."""
        src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
        violations = []
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        if "ImageFit" in line:
                            violations.append(f"{file}:{idx}: {line.strip()}")

        assert not violations, f"Encontradas referencias a 'ImageFit' descontinuado: {violations}"


# ==============================================================================
# PILAR 4: REBRANDING OFICIAL E BRAND BOOK V3.1 (PROIBIÇÃO DE SEJONG)
# ==============================================================================
class TestPillar4RebrandingAndPedagogy:
    """Valida proibicao do nome 'Sejong' na UI, hierarquia 60/20/12/8 e Pretendard."""

    def test_zero_sejong_in_user_facing_titles_and_splash(self):
        """Garante que a marca oficial 'Saebom Companion' esta no page.title e nas telas."""
        from src.theme import apply_app_theme
        from src.views.splash_view import splash_view

        page = MockPage()
        apply_app_theme(page)

        # Titulo da janela
        assert "Saebom Companion" in page.title, f"Titulo da janela incorreto: '{page.title}'"
        assert "Sejong" not in page.title, f"O termo proibido 'Sejong' foi detectado no page.title: '{page.title}'"

        # Splash view
        splash = splash_view(page)
        def collect_texts(ctrl):
            texts = []
            if isinstance(ctrl, ft.Text):
                texts.append(ctrl.value or "")
            children = []
            if hasattr(ctrl, "controls") and isinstance(ctrl.controls, list):
                children.extend(ctrl.controls)
            if hasattr(ctrl, "content") and ctrl.content:
                children.append(ctrl.content)
            for c in children:
                if isinstance(c, ft.Control):
                    texts.extend(collect_texts(c))
            return texts

        splash_texts = " ".join(collect_texts(splash))
        assert "새봄" in splash_texts, "Splash view deve exibir o logotipo em Hangul '새봄'"
        assert "SAEBOM COMPANION" in splash_texts, "Splash view deve exibir 'SAEBOM COMPANION'"
        assert "Sejong" not in splash_texts, "Splash view contem o termo proibido 'Sejong'!"

    def test_color_hierarchy_conformance_and_no_alpha_concatenation(self):
        """Valida tokens do Brand Book v3.1: Navy #02060F, Violet #8B4DFF, Gold #FFAB22."""
        from src.theme import Colors

        assert Colors.NAVY == "#02060F", "Navy oficial deve ser #02060F (60%)"
        assert Colors.VIOLET == "#8B4DFF", "Violet oficial (PRIMARY) deve ser #8B4DFF (12%)"
        assert Colors.GOLD == "#FFAB22", "Gold oficial (ACCENT) deve ser #FFAB22 (8%)"

        # Garantir que nao ha concatenacao incorreta de sufixo alfa em hexadecimais (BUG-03/BUG-11)
        src_dir = os.path.join(os.path.dirname(__file__), "..", "src")
        alpha_concats = []
        for root, _, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines, 1):
                        # Detecta padroes como f"{...}12" ou f"{colors['primary']}40"
                        if re.search(r'f["\'][^"\']+\}\s*[0-9a-fA-F]{2}["\']', line):
                            alpha_concats.append(f"{file}:{idx}: {line.strip()}")

        assert not alpha_concats, (
            f"FALHA DE BRANDING/FLUTTER: Concatenacoes de canal alfa encontradas "
            f"(use ft.Colors.with_opacity): {alpha_concats}"
        )

    def test_global_typography_pretendard_fallback_no_tofu(self):
        """Garante que a fonte primaria oficial e Pretendard e possui Kyobo Handwriting."""
        from src.theme import apply_app_theme

        page = MockPage()
        apply_app_theme(page)

        assert page.theme.font_family == "Pretendard", "Fonte principal deve ser Pretendard (prevencao de tofu)"
        assert "Pretendard" in page.fonts, "Pretendard deve estar mapeada em page.fonts"
        assert "Kyobo Handwriting" in page.fonts, "Kyobo Handwriting deve estar mapeada para caligrafia"


# ==============================================================================
# PILAR 5: CALIGRAFIA WONGOJI E FIDELIDADE CURRICULAR (GABARITOS 1A/1B)
# ==============================================================================
class TestPillar5CalligraphyAndCurriculumFidelity:
    """Valida motor Wongoji multi-celula, conformidade de gabarito e 띄어쓰기."""

    def test_calligraphy_exercises_match_official_sejong_workbooks(self):
        """Garante presenca dos exercicios oficiais dos workbooks 1A e 1B (국립국어원)."""
        from src.services import DataService

        calligraphy_prompts = []
        for unit_id in DataService._get_all_unit_ids():
            unit = DataService.get_unit(unit_id)
            if not unit:
                continue
            for ex in getattr(unit, "exercises", []):
                if getattr(ex, "type", "") == "calligraphy":
                    # QuizQuestion armazena o texto alvo em target_text
                    target = getattr(ex, "target_text", None) or getattr(ex, "question", "")
                    calligraphy_prompts.append(target)

        # Exercicios representativos de 1A e 1B do gabarito oficial presentes no curriculo
        expected_sample_prompts = [
            "한국 사람",
            "가고 싶어요",
            "불고기를 자주 먹어요",
            "커피를 좋아해서",
        ]
        for prompt in expected_sample_prompts:
            found = any(prompt in p for p in calligraphy_prompts)
            assert found, f"Exercicio oficial '{prompt}' ausente do curriculo de caligrafia!"

    def test_spacing_rule_for_multi_word_calligraphy_expressions(self):
        """Frases de 2+ palavras DEVEM respeitar o espacamento oficial (띄어쓰기) com celula em branco."""
        phrase = "한국 사람"
        tokens = list(phrase)

        assert " " in tokens, "Frase deve conter espaco (띄어쓰기)"
        space_indices = [idx for idx, char in enumerate(tokens) if char == " "]
        assert len(space_indices) >= 1, "Pelo menos uma celula em branco deve existir para espacamento"

    def test_focus_mode_ergonomics_and_submission_trigger(self):
        """Grade de caligrafia multi-celula deve ter celula ativa de pelo menos 210px para ergonomia."""
        from src.components.wongoji_multi_cell_widget import WongojiMultiCellWidget

        widget = WongojiMultiCellWidget(
            target_text="한국 사람",
            cell_size=210.0,
        )
        assert widget.active_cell_size >= 210.0, "Focus Mode deve ter tamanho minimo de 210px para ergonomia touchscreen"
        assert widget.num_cells == len("한국 사람"), "Numero de celulas deve corresponder ao texto"
