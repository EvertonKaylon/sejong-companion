# Plano de Implementação — Estabilização, Rebase e Reconciliação
## `feature/neuroscience-gap-closure` → `feature/branding`

---

## 1. Sumário Executivo & Metas de Confiabilidade

### 1.1 Objetivo do Plano
Este plano de implementação define o procedimento determinístico, auditável e seguro em nível de produção para reconciliar, rebasear e estabilizar o branch `feature/neuroscience-gap-closure` sobre a linha de base já validada de `feature/branding`. 

O objetivo principal é unificar as inovações sensoriais e neuropedagógicas (Fase 1 e Fase 2: efeito de partículas de ar, haptic feedback real, fábrica de sílabas, diorama espacial, fonética articulatória com silhuetas cinesiológicas e fusão atômica de estudantes em PascalCase) com os alicerces estruturais de segurança e design consolidados em `feature/branding` (Brand Book v3.1, arquitetura cromática 60/20/12/8, eliminação de strings "Sejong", caligrafia Wongoji multi-célula com Focus Mode de 210px+, autenticação fail-closed em tempo constante, isolamento de portas Docker e blindagem contra tela preta CanvasKit BUG-11).

### 1.2 Métricas de Sucesso e Alvos Quantitativos
A conclusão bem-sucedida deste plano exige o cumprimento estrito e simultâneo de todas as seguintes métricas:

| Métrica | Linha de Base Atual (`branding`) | Diagnóstico Atual (`neuroscience`) | Alvo Pós-Reconciliação | Tolerância de Regressão |
|---|---|---|---|---|
| **Suíte Global de Testes** | 229 testes PASS | Incompatível (divergente) | **≥ 261 testes PASS** | **0 falhas (zero tolerance)** |
| **Suíte E2E 5 Pilares (`test_e2e_full_coverage.py`)** | 16 / 16 PASS (100%) | 4 PASS / 12 FAIL (25%) | **16 / 16 PASS (100%)** | **0 falhas** |
| **Testes Sensoriais Fase 1 (`test_phase1_sensory_features.py`)** | Não presente | 5 / 5 PASS (100%) | **5 / 5 PASS (100%)** | **0 falhas** |
| **Testes Interativos Fase 2 (`test_phase2_interactive_features.py`)** | Não presente | 6 / 6 PASS (100%) | **6 / 6 PASS (100%)** | **0 falhas** |
| **Identidade de Aluno (`test_student_name_case_and_merge.py`)** | Não presente | 6 / 6 PASS (100%) | **6 / 6 PASS (100%)** | **0 falhas** |
| **Serviço Háptico (`test_haptic_service.py`)** | Não presente | 7 / 7 PASS (100%) | **7 / 7 PASS (100%)** | **0 falhas** |
| **Curriculo de Quiz e SOV (`test_quiz_widget.py`)** | Não presente | 8 / 8 PASS (100%) | **8 / 8 PASS (100%)** | **0 falhas** |
| **Concatenção Alfa Hexadecimal (`r'f".*\}\s*[0-9a-fA-F]{2}"'`)** | 0 ocorrências | 8 ocorrências | **0 ocorrências (100% `with_opacity`)** | **0 ocorrências** |
| **Caminhos Relativos de Assets (`mouth_shapes/`, `spatial/`)** | 0 ocorrências | 12 ocorrências | **0 ocorrências (100% absolutos `/...`)** | **0 ocorrências** |
| **Ocorrências de Marca "Sejong" na UI / page.title** | 0 ocorrências | 3 ocorrências | **0 ocorrências ("Saebom Companion")** | **0 ocorrências** |
| **Exposição de Portas Uvicorn (`docker-compose.yml`)** | `expose: - "8554"` | `ports: - "8554:8554"` | **`expose: - "8554"` (rede interna Caddy)** | **0 vazamentos** |

---

## 2. Topologia Git & Linha de Base de Ancestralidade

### 2.1 Grafo de Histórico e Ponto de Divergência
A auditoria estrutural do repositório confirma a seguinte árvore genealógica de commits:

```
                                    (Merge-Base: 2b11937)
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
         [Linha feature/branding]                    [Linha feature/neuroscience-gap-closure]
            30 commits à frente                             5 commits à frente
            - security/hardening-v0.3.2                     - Phase 1: Mecânicas sensoriais
            - feature/calligraphy-grid                      - Phase 2: Componentes interativos
            - Brand Book v3.1 (Navy/Violet/Gold)            - Identidade Aluno PascalCase & Merge
            - BUG-11 Web CanvasKit Hardening                - Haptic Service e Quiz SOV
            - Commit 614afba (Porta 8554, with_opacity)     HEAD: 0a248c299a5e507669c3d4480543468a0f29f997
            - Commit 921bfd2 (DESIGN.md master spec)
            HEAD: 921bfd2b75485dc22b5e3bb31b0397e22d9b38c5
```

### 2.2 Inventário de Commits
1. **Ponto de Fusão Comum (Merge-Base)**:
   - Commit: `2b11937b0361ace38654c1204e5d194c21566437`
   - Estado: Aplicação monolítica base com suporte inicial a Flet, 10 unidades 1A, pré-aquecimento básico de áudio e visual legado Sejong.
2. **Histórico `feature/branding` (HEAD `921bfd2`)**:
   - `921bfd2`: `chore(branding): preserve validated branding and test state` (Preservação de `DESIGN.md`).
   - `614afba`: `fix(infra,theme): fechar porta 8554 contra scanners, eliminar concatenacao alfa hex e implementar StudentIdentity`.
   - Commits anteriores englobam hardening do `AdminService`, motor Wongoji multi-célula de caligrafia, gabaritos oficiais 1A/1B (`한국 사람`, etc.) e arquitetura atômica do roteador.
3. **Histórico `feature/neuroscience-gap-closure` (HEAD `0a248c2`)**:
   - `0a248c2`: `feat(identity): cadastro de alunos case-insensitive com PascalCase e fusao automatica de progresso`.
   - Commits antecedentes implementaram `air_particle_effect.py`, `syllable_factory.py`, `spatial_stage.py`, `oclusive_lab.py`, `number_training.py` e os 32 testes de validação cognitiva.

---

## 3. Salvaguardas Pré-Rebase & Preparação do Ambiente

Antes de iniciar qualquer manipulação no grafo do Git, salvaguardas estritas devem ser aplicadas para garantir restauração instantânea em caso de divergência.

### 3.1 Criação do Branch de Backup Imutável
No terminal PowerShell ou Git Bash, execute:

```powershell
# 1. Garantir que estamos na raiz do repositório
cd c:\Users\Pichau\Documents\sejong_companion

# 2. Verificar integridade atual do branch neuroscience
git checkout feature/neuroscience-gap-closure
git status -s

# 3. Criar tag/branch de backup apontando exatamente para o commit 0a248c2
git branch -f backup/neuroscience-pre-rebase 0a248c2
git tag -f v0.3.0-neuroscience-pre-rebase 0a248c2

# 4. Criar branch de backup apontando para a base validada de branding 921bfd2
git branch -f backup/branding-pre-rebase 921bfd2
```

### 3.2 Isolamento de Metadados e Arquivos Voláteis
Verifique se `.git/info/exclude` está configurado para evitar poluição da árvore de trabalho durante a transição:

```
# Conteúdo obrigatório em .git/info/exclude:
.agents/
ORIGINAL_REQUEST.md
assets/audio_cache/
data/cache/
scratch/
```

Execute a validação:
```powershell
git status --ignored
# Deve listar .agents e caches como ignorados, sem arquivos untracked no git status principal
```

---

## 4. Instruções Passo a Passo de Rebase & Resolução de Conflitos

O rebase colocará os 5 commits de neurociência no topo da linha de base estabilizada `feature/branding`:
```powershell
git checkout feature/neuroscience-gap-closure
git rebase feature/branding
```
Durante o rebase, 8 arquivos centrais e 2 arquivos de configuração apresentarão conflitos ou necessitarão de reconciliação sintática manual. As instruções a seguir fornecem as especificações exatas de código para cada um.

---

### 4.1 Arquivo 1: `src/services.py`
**Problema**: Conflito entre a segurança fail-closed do `AdminService` + credencial independente de recuperação (`feature/branding`) e as funções de canonicalização PascalCase + fusão atômica de sessões (`feature/neuroscience-gap-closure`).

**Regras de Reconciliação**:
1. Manter no topo do arquivo todas as funções auxiliares de neurociência: `_capitalize_token`, `canonicalize_student_name`, `normalize_name_key` e `merge_session_data`.
2. Em `canonicalize_student_name`, atualizar o retorno padrão para `"Estudante Saebom"`. Tratar entradas vazias, `None`, `"estudante saebom"` e `"estudante sejong"` como retornando `"Estudante Saebom"`.
3. Em `ProgressService`:
   - Implementar `@classmethod def set_file_path_override(cls, path: Optional[str])` que redefine `_file_path_override` e limpa `_sessions`.
   - Adicionar geração de `recovery_code` com entropia independente de `_session_id` (`f"rec_{secrets.token_hex(8)}"`).
   - Implementar `get_or_create_recovery_code()`, `has_recovery_code()` e `verify_and_restore_student()`.
   - Integrar `resolve_or_create_student` para busca case-insensitive e consolidação atômica.
4. Em `AdminService`:
   - Implementar autenticação fail-closed em `login(pin, client_key="default") -> Tuple[bool, Optional[str], str]`:
     - Rejeitar `None`, string vazia ou apenas espaços em branco imediatamente.
     - Comparar contra `SAEBOM_ADMIN_PIN` (com fallback opcional para `SEJONG_ADMIN_PIN`) usando exclusivamente `hmac.compare_digest`.
     - Implementar limitação de taxa (rate limiting) com `_failed_attempts` e `_lockouts`.
     - Implementar `reset_rate_limit(client_key: str = "default")`.
   - Manter método legado `authenticate(pin: str) -> bool` delegando diretamente para `login(pin, client_key="legacy_auth")[0]`.
   - Em `get_all_students_summary`, manter a desduplicação de perfis baseada em `normalize_name_key`.

#### Implementação Canônica em `src/services.py`:
```python
# --- Top-Level Helpers em src/services.py ---
import hmac
import secrets
import time
from collections import defaultdict

def _capitalize_token(token: str) -> str:
    m = re.match(r"^(\W*)(.*?)(\W*)$", token)
    if not m:
        return token
    prefix, core, suffix = m.groups()
    if not core:
        return token
    if "-" in core:
        parts = core.split("-")
        core_formatted = "-".join(_capitalize_token(p) for p in parts)
    elif "'" in core:
        parts = core.split("'")
        core_formatted = "'".join(_capitalize_token(p) for p in parts)
    else:
        core_formatted = core.capitalize()
    return f"{prefix}{core_formatted}{suffix}"


def canonicalize_student_name(raw_name: str) -> str:
    """Formata o nome do aluno em PascalCase / Title Case, preservando Hangul e pontuações."""
    if not raw_name:
        return "Estudante Saebom"
    cleaned = unicodedata.normalize("NFKC", str(raw_name).strip())
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned or cleaned.lower() in ("estudante saebom", "estudante sejong"):
        return "Estudante Saebom"

    words = cleaned.split(" ")
    return " ".join(_capitalize_token(w) for w in words if w)


def normalize_name_key(name: str) -> str:
    if not name:
        return ""
    norm = unicodedata.normalize("NFKC", str(name).strip())
    norm = re.sub(r"\s+", " ", norm)
    return norm.casefold()


# --- ProgressService Security & Identity Reconciliado ---
class ProgressService:
    _file_path_override: Optional[str] = None
    _sessions: dict = {}
    DAILY_XP = 10
    MILESTONE_XP = 50

    @classmethod
    def set_file_path_override(cls, path: Optional[str]):
        """Define caminho de arquivo customizado para testes unitários isolados."""
        cls._file_path_override = path
        cls._sessions.clear()

    def get_or_create_recovery_code(self) -> str:
        """Gera ou recupera o código de recuperação com entropia criptográfica independente."""
        store = self._store
        if "recovery_code" not in store or not store["recovery_code"]:
            store["recovery_code"] = f"rec_{secrets.token_hex(8)}"
            ProgressService._save_to_disk(self._session_id, self._store)
        return store["recovery_code"]

    def has_recovery_code(self) -> bool:
        return bool(self._store.get("recovery_code"))

    @classmethod
    def verify_and_restore_student(cls, recovery_code: str, sessions_dir: Optional[str] = None) -> Optional[str]:
        if not recovery_code or not recovery_code.strip():
            return None
        code_clean = recovery_code.strip()
        directory = cls._get_storage_dir(sessions_dir)
        if not os.path.exists(directory):
            return None
        for filename in os.listdir(directory):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(directory, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    rec = data.get("recovery_code")
                    if rec and hmac.compare_digest(str(rec), code_clean):
                        return data.get("student_id") or filename[:-5]
            except Exception:
                continue
        return None

    def get_student_name(self) -> str:
        raw = self._store.get("student_name", "Estudante Saebom")
        return canonicalize_student_name(raw)


# --- AdminService Fail-Closed Reconciliado ---
class AdminService:
    DEFAULT_PIN: str = "saebom2026"
    _failed_attempts: Dict[str, int] = defaultdict(int)
    _lockouts: Dict[str, float] = {}

    @classmethod
    def reset_rate_limit(cls, client_key: str = "default"):
        cls._failed_attempts.pop(client_key, None)
        cls._lockouts.pop(client_key, None)

    @classmethod
    def login(cls, pin: Optional[str], client_key: str = "default") -> Tuple[bool, Optional[str], str]:
        now = time.time()
        if client_key in cls._lockouts:
            if now < cls._lockouts[client_key]:
                return False, None, "Muitas tentativas falhas. Acesso bloqueado temporariamente."
            else:
                cls.reset_rate_limit(client_key)

        if not pin or not str(pin).strip():
            return False, None, "PIN não pode ser vazio."

        pin_str = str(pin).strip()
        expected = os.environ.get("SAEBOM_ADMIN_PIN") or os.environ.get("SEJONG_ADMIN_PIN") or cls.DEFAULT_PIN

        if hmac.compare_digest(pin_str, expected):
            cls.reset_rate_limit(client_key)
            token = f"admin_tok_{secrets.token_hex(16)}"
            return True, token, "Autenticação autorizada."
        else:
            cls._failed_attempts[client_key] += 1
            if cls._failed_attempts[client_key] >= 5:
                cls._lockouts[client_key] = now + 300
            return False, None, "PIN incorreto."

    @classmethod
    def authenticate(cls, pin: str) -> bool:
        success, _, _ = cls.login(pin, client_key="legacy_auth")
        return success
```

---

### 4.2 Arquivo 2: `src/theme.py`
**Problema**: Coexistência da paleta oficial do Brand Book v3.1 (`NAVY`, `VIOLET`, `GOLD`, `Pretendard`, `Kyobo Handwriting`, título `"Saebom Companion"`) com os tokens sensoriais criados pela neurociência (`CONNECTOR_VOWEL`, `CONNECTOR_BATCHIM`, `OCLUSIVE_*`, `VITALITY_*`, `ROLE_*`).

**Regras de Reconciliação**:
1. Em `Colors`, adicionar:
   ```python
   # Brand Book v3.1 Hierarchy (60/20/12/8)
   NAVY = "#02060F"       # 60% Fundo Estrutural Dominante (Dark BG)
   VIOLET = "#8B4DFF"     # 12% Ações Primárias / Interação Principal
   GOLD = "#FFAB22"       # 8% Destaque / Conquistas / Acentos
   LILAC = "#C7B4FD"      # Apoio / Hover
   CREAM = "#FAF9F6"      # Fundo Claro / Warm Off-White
   SLATE = "#1E293B"      # Bordas e Superfícies Elevadas
   
   # Conectores Metálicos (Fase 2 Interativa)
   CONNECTOR_VOWEL = "#B87333"      # Cobre Metálico (Terminação Vogal)
   CONNECTOR_BATCHIM = "#C0C0C0"    # Prata Metálica (Terminação Batchim)
   
   # Fonética e Oclusivas
   OCLUSIVE_LAX = "#94A3B8"
   OCLUSIVE_ASPIRATED = "#38BDF8"
   OCLUSIVE_TENSE = "#EF4444"
   
   # Vitalidade SRS
   VITALITY_HIGH = "#10B981"
   VITALITY_MEDIUM = "#F59E0B"
   VITALITY_LOW = "#EF4444"
   VITALITY_NONE = "#74717F"
   ```
2. Em `Styles`:
   ```python
   CONNECTOR_VOWEL = Colors.CONNECTOR_VOWEL
   CONNECTOR_BATCHIM = Colors.CONNECTOR_BATCHIM
   ```
3. Em `apply_app_theme(page: ft.Page)`:
   - Definir `page.title = f"Saebom Companion v{__version__}"` (eliminando rigorosamente a palavra "Sejong").
   - Configurar `page.fonts` mapeando:
     - `"Pretendard": "fonts/Pretendard-Regular.otf"`
     - `"Kyobo Handwriting": "fonts/KyoboHandwriting2020pdy.ttf"`
     - Demais pesos de Pretendard e fontes de caligrafia.
   - Definir `page.theme = ft.Theme(font_family="Pretendard", color_scheme_seed=Colors.VIOLET)`.

---

### 4.3 Arquivo 3: `src/router.py`
**Problema**: `feature/neuroscience-gap-closure` executa `self.page.views.clear()` *antes* de instanciar a nova view, gerando `views == []` e crash de tela preta caso ocorra qualquer exceção no construtor.

**Regras de Reconciliação**:
Adotar a transição atômica de `feature/branding` com fallback de emergência:
```python
    def route_change(self, e: ft.RouteChangeEvent):
        route = e.route or "/splash"
        base_route = route.split("?")[0]
        
        # Gerenciamento de histórico
        if not self._history or self._history[-1] != base_route:
            if base_route in ("/splash", "/onboarding", "/home"):
                self._history = [base_route]
            else:
                self._history.append(base_route)

        new_view = None
        try:
            if base_route in self.routes:
                new_view = self.routes[base_route](self.page)
            elif "/splash" in self.routes:
                new_view = self.routes["/splash"](self.page)
            elif "/home" in self.routes:
                new_view = self.routes["/home"](self.page)
        except Exception as ex:
            # Fallback de emergência (previne tela preta no Flutter CanvasKit)
            new_view = ft.View(
                route=base_route,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.AMBER_400),
                                ft.Text(f"Erro ao carregar visualização: {ex}", size=14),
                                ft.ElevatedButton("Voltar ao Início", on_click=lambda _: self.page.go("/home")),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        expand=True,
                    )
                ]
            )

        if new_view:
            self.page.views.clear()
            self.page.views.append(new_view)

        try:
            self.page.update()
        except Exception:
            pass
```

---

### 4.4 Arquivo 4: `src/views/splash_view.py`
**Problema**: Exibe marca "세종학당" e "Centro Cultural Coreano no Brasil • 세종학당재단", além de invocar `asyncio.create_task(prewarm_and_redirect())` de forma desprotegida, travando testes unitários síncronos com `RuntimeError: no running event loop`.

**Regras de Reconciliação**:
1. Substituir textos pela identidade oficial Saebom:
   - Logotipo em Hangul: `"새봄"` (`size=36`, `font_family="Seollip-che"`).
   - Nome ocidental: `"SAEBOM COMPANION"` (`size=14`, `font_family="Pretendard"`).
   - Subtítulo de missão: `"Plataforma Neurocognitiva de Língua Coreana"`.
   - Garantir: **zero** ocorrências da palavra "Sejong" na árvore de controles.
2. Proteger a execução assíncrona contra ambientes síncronos/headless:
   ```python
   # Execução resiliente do prewarm
   if hasattr(page, "run_task") and callable(page.run_task):
       page.run_task(prewarm_and_redirect)
   else:
       try:
           loop = asyncio.get_running_loop()
           loop.create_task(prewarm_and_redirect())
       except RuntimeError:
           # Sem loop de eventos ativo em testes unitários síncronos (evita crash)
           pass
   ```

---

### 4.5 Arquivo 5: `src/views/home_view.py`
**Problema**: Concatenação direta de canais alfa em strings hexadecimais (`f"{tip_color}15"`, `f"{tip_color}30"`, `f"{vitality_color}35"`), que quebram no compilador web do Flutter e violam a suíte do Pilar 4.

**Regras de Reconciliação**:
1. Linha 161:
   ```python
   # De:
   bgcolor=f"{tip_color}15"
   # Para:
   bgcolor=ft.Colors.with_opacity(0.08, tip_color)
   ```
2. Linha 177:
   ```python
   # De:
   border=ft.Border.all(1, f"{tip_color}30")
   # Para:
   border=ft.Border.all(1, ft.Colors.with_opacity(0.19, tip_color))
   ```
3. Linha 419 (anel de vitalidade SRS):
   ```python
   # De:
   bgcolor=f"{vitality_color}35"
   # Para:
   bgcolor=ft.Colors.with_opacity(0.21, vitality_color)
   ```
4. Preservar os controles de anel de vitalidade SRS (`outer_ring` e `inner_core`) conectados a `retention_pct`.

---

### 4.6 Arquivo 6: `src/components/hangul_card.py`
**Problema**: Uso de caminho relativo `src=f"mouth_shapes/{mouth_id}.svg"`, causando erro 404 em rotas aninhadas do CanvasKit, e concatenação de cores (`f"{self.colors['primary']}20"`, `"#19188150"`).

**Regras de Reconciliação**:
1. Linha 82 — Garantir caminho absoluto com `/` na frente:
   ```python
   # De:
   src=f"mouth_shapes/{mouth_id}.svg"
   # Para:
   src=f"/mouth_shapes/{mouth_id}.svg"
   ```
2. Linha 23 — Fundo da camada de glow:
   ```python
   # De:
   bgcolor=f"{self.colors['primary']}20"
   # Para:
   bgcolor=ft.Colors.with_opacity(0.12, self.colors["primary"])
   ```
3. Linha 69 — Tag do tipo de caractere:
   ```python
   # De:
   bgcolor="#19188150"
   # Para:
   bgcolor=ft.Colors.with_opacity(0.10, self.colors["correct"])
   ```
4. Preservar a camada `self.glow_ring` e a integração com `page.haptic_service.tap_light()`.

---

### 4.7 Arquivo 7: `src/components/spatial_stage.py`
**Problema**: Todos os assets de diorama (`spatial/bag.svg`, `spatial/desk.svg`, etc.) usam caminhos relativos sem `/`, falhando no Flutter Web CanvasKit (BUG-11).

**Regras de Reconciliação**:
Na lista `self.challenges` (linhas 26-67), prefixar todos os `object_asset` e `base_asset` com `/`:
```python
        self.challenges = [
            {
                "id": "s1",
                "object_name": "가방",
                "object_asset": "/spatial/bag.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "위",
                "prompt_kr": "가방이 책상 위에 있어요.",
            },
            {
                "id": "s2",
                "object_name": "강아지",
                "object_asset": "/spatial/dog.svg",
                "base_name": "의자",
                "base_asset": "/spatial/chair.svg",
                "target_pos": "아래",
                "prompt_kr": "강아지가 의자 아래에 있어요.",
            },
            {
                "id": "s3",
                "object_name": "책",
                "object_asset": "/spatial/book.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "옆",
                "prompt_kr": "책이 책상 옆에 있어요.",
            },
            {
                "id": "s4",
                "object_name": "가방",
                "object_asset": "/spatial/bag.svg",
                "base_name": "의자",
                "base_asset": "/spatial/chair.svg",
                "target_pos": "뒤",
                "prompt_kr": "가방이 의자 뒤에 있어요.",
            },
            {
                "id": "s5",
                "object_name": "강아지",
                "object_asset": "/spatial/dog.svg",
                "base_name": "책상",
                "base_asset": "/spatial/desk.svg",
                "target_pos": "앞",
                "prompt_kr": "강아지가 책상 앞에 있어요.",
            },
        ]
```

---

### 4.8 Arquivo 8: `src/components/air_particle_effect.py`
**Problema**: Inicialização e animação de círculos usando strings hexadecimais com canal alfa concatenado (`f"{self.base_color}00"` e `f"{self.base_color}{hex_alpha}"`), violando a auditoria estática do Pilar 4.

**Regras de Reconciliação**:
1. Linha 57 (`_init_shapes`):
   ```python
   # De:
   paint=ft.Paint(
       color=f"{self.base_color}00",
       style=ft.PaintingStyle.FILL,
   )
   # Para:
   paint=ft.Paint(
       color=ft.Colors.with_opacity(0.0, self.base_color),
       style=ft.PaintingStyle.FILL,
   )
   ```
2. Linhas 95-107 (`emit`):
   ```python
   # De:
   progress = (step + 1) / steps
   alpha = int(255 * (1.0 - progress))
   hex_alpha = f"{alpha:02x}"
   ...
   circle.paint.color = f"{self.base_color}{hex_alpha}"
   
   # Para:
   progress = (step + 1) / steps
   opacity_val = max(0.0, min(1.0, 1.0 - progress))
   ...
   circle.paint.color = ft.Colors.with_opacity(opacity_val, self.base_color)
   ```

---

### 4.9 Arquivo 9: `docker-compose.yml`
**Problema**: Exposição pública de `ports: - "8554:8554"` abre o Uvicorn para o mundo exterior e provoca ruído de scans TLS inválidos.

**Regras de Reconciliação**:
Substituir a seção `ports` de `app` por `expose`:
```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: saebom-companion-app
    restart: always
    environment:
      - PORT=8554
      - SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:-}
      - TYPECAST_API_KEY=${TYPECAST_API_KEY:-}
    expose:
      - "8554"
    volumes:
      - ./assets/audio_cache:/app/assets/audio_cache
      - ./data/sessions:/app/data/sessions
      - ./data/telemetry:/app/data/telemetry
      - ./data/reports:/app/data/reports

  caddy:
    image: caddy:2-alpine
    container_name: saebom-companion-caddy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
    depends_on:
      - app
```

---

### 4.10 Arquivo 10: `.gitignore`
**Problema**: Falta a entrada `data/cache` na lista de diretórios mutáveis ignorados.

**Regras de Reconciliação**:
Certificar que a seção de dados do estudante contenha:
```gitignore
# Dados de progresso e cache do estudante (runtime)
data/user_progress.json
data/user_progress.json.tmp
data/sessions/
data/telemetry/
data/reports/
data/cache/
```

---

### 4.11 Arquivo 11: `tests/test_student_name_case_and_merge.py`
**Problema**: O teste unitário de canonicalização de nome espera `"Estudante Sejong"` quando a entrada é vazia ou nula, colidindo com o padrão `"Estudante Saebom"`.

**Regras de Reconciliação**:
Alinhar as asserções de nome padrão em `test_canonicalize_student_name_latin`:
```python
def test_canonicalize_student_name_latin():
    """Valida formatação de nomes em alfabeto latino para PascalCase."""
    assert canonicalize_student_name("everton kaylon") == "Everton Kaylon"
    assert canonicalize_student_name("EVERTON KAYLON") == "Everton Kaylon"
    assert canonicalize_student_name("eVeRtOn   kAyLoN") == "Everton Kaylon"
    assert canonicalize_student_name("   marianelly    seitz   arnold  ") == "Marianelly Seitz Arnold"
    assert canonicalize_student_name("carlos d'angelo") == "Carlos D'Angelo"
    assert canonicalize_student_name("ana-paula silva") == "Ana-Paula Silva"
    assert canonicalize_student_name("") == "Estudante Saebom"
    assert canonicalize_student_name(None) == "Estudante Saebom"
    assert canonicalize_student_name("estudante saebom") == "Estudante Saebom"
```

---

### 4.12 Arquivos Adicionais com Concatenação Alfa Hex (Higienização Completa)
Para garantir 100% de aprovação no teste `test_color_hierarchy_conformance_and_no_alpha_concatenation`, aplicar as correções identificadas pelo Explorer 4 nos demais componentes:

1. **`src/components/oclusive_lab.py`**:
   - Linha 126: Substituir `color=f"{border_color}35"` por `color=ft.Colors.with_opacity(0.21, border_color)`.
   - Linha 157: Substituir `color=f"{border_color}70"` por `color=ft.Colors.with_opacity(0.44, border_color)`.
   - Linha 168: Substituir `color=f"{border_color}35"` por `color=ft.Colors.with_opacity(0.21, border_color)`.
2. **`src/components/syllable_factory.py`**:
   - Linha 74: Substituir `color=f"{self.colors['primary']}30"` por `color=ft.Colors.with_opacity(0.19, self.colors["primary"])`.
3. **`src/components/vocab_card.py`**:
   - Linha 17: Substituir `bgcolor=f"{self.colors['primary']}25"` por `bgcolor=ft.Colors.with_opacity(0.15, self.colors["primary"])`.
   - Linha 126: Substituir `bgcolor="#14F5A623"` por `bgcolor=ft.Colors.with_opacity(0.08, self.colors["accent"])`.
   - Linha 128: Substituir `border=ft.Border.all(1, "#33F5A623")` por `border=ft.Border.all(1, ft.Colors.with_opacity(0.20, self.colors["accent"]))`.
4. **`src/views/admin_view.py`**:
   - Linha 359: Substituir `bgcolor=f"{color_hex}15"` por `bgcolor=ft.Colors.with_opacity(0.08, color_hex)`.

---

## 5. Protocolo de Verificação Pós-Reconciliação

Após aplicar as resoluções de conflito e concluir o rebase, o seguinte protocolo de testes em 4 etapas deve ser executado sequencialmente:

### 5.1 Etapa 1: Execução da Suíte E2E dos 5 Pilares (16 / 16 PASS)
Comando:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_e2e_full_coverage.py -v
```
Critério de Aceite:
- **Pilar 1 (Infra)**: 3/3 PASS (`test_docker_compose_port_exposure_hardening`, `test_caddyfile_reverse_proxy_configuration`, `test_dockerfile_production_readiness`).
- **Pilar 2 (Segurança)**: 4/4 PASS (`test_admin_pin_weak_credentials_rejected_fail_closed`, `test_auth_constant_time_comparison`, `test_mutable_data_directories_isolated_and_gitignored`, `test_student_id_not_used_as_recovery_credential`).
- **Pilar 3 (Arquitetura BUG-11)**: 3/3 PASS (`test_router_atomic_views_transition_and_emergency_fallback`, `test_all_registered_views_use_absolute_asset_paths`, `test_zero_deprecated_imagefit_enums_in_codebase`).
- **Pilar 4 (Branding v3.1)**: 3/3 PASS (`test_zero_sejong_in_user_facing_titles_and_splash`, `test_color_hierarchy_conformance_and_no_alpha_concatenation`, `test_global_typography_pretendard_fallback_no_tofu`).
- **Pilar 5 (Caligrafia 1A/1B)**: 3/3 PASS (`test_calligraphy_exercises_match_official_sejong_workbooks`, `test_spacing_rule_for_multi_word_calligraphy_expressions`, `test_focus_mode_ergonomics_and_submission_trigger`).
- **Total**: 16 passed, 0 failed.

---

### 5.2 Etapa 2: Execução das Suítes Especializadas de Neurociência (32 / 32 PASS)
Comando:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_phase1_sensory_features.py tests/test_phase2_interactive_features.py tests/test_student_name_case_and_merge.py tests/test_haptic_service.py tests/test_quiz_widget.py -v
```
Critério de Aceite:
- `test_phase1_sensory_features.py`: 5 passed.
- `test_phase2_interactive_features.py`: 6 passed.
- `test_student_name_case_and_merge.py`: 6 passed.
- `test_haptic_service.py`: 7 passed.
- `test_quiz_widget.py`: 8 passed (incluindo todos os 42 testes parametrizados de SOV e escolhas múltiplas).
- **Total**: 32 passed, 0 failed.

---

### 5.3 Etapa 3: Execução da Suíte Global Completa (≥ 261 PASS)
Comando:
```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```
Critério de Aceite:
- **Total**: ≥ 261 passed, 0 failed.
- Todos os testes de progresso, admin, flashcards, lições e visualizações mantêm compatibilidade total.

---

### 5.4 Etapa 4: Auditorias Estáticas via Regex
Executar varreduras estáticas para garantir que nenhum resíduo de concatenação alfa ou caminho relativo permaneça:

1. **Auditoria de Concatenação Alfa Hex**:
   ```powershell
   git grep -En 'f["\'][^"\']+\}\s*[0-9a-fA-F]{2}["\']' src/
   ```
   *Resultado Esperado*: Zero resultados (saída vazia).

2. **Auditoria de Caminhos Relativos de Assets**:
   ```powershell
   git grep -En '(src|asset)=f?"(mouth_shapes|spatial)/' src/
   ```
   *Resultado Esperado*: Zero resultados (todos os caminhos devem iniciar com `/`).

3. **Auditoria da Marca "Sejong" na Interface**:
   ```powershell
   git grep -in "sejong" src/views/splash_view.py
   ```
   *Resultado Esperado*: Zero resultados.

---

## 6. Protocolo de Rollback & Contingência de Emergência

Caso ocorra qualquer divergência insolúvel, quebra inesperada de testes legados ou travamento de rebase, o operador deve acionar imediatamente o protocolo de reversão garantido:

### 6.1 Abortar Rebase em Andamento
Se o rebase travar ou gerar conflitos inesperados:
```powershell
git rebase --abort
```

### 6.2 Restauração Instantânea a partir do Backup
Caso o rebase tenha sido concluído mas a suíte de testes falhe:
```powershell
# 1. Restaurar o branch feature/neuroscience-gap-closure para o estado pré-rebase
git checkout feature/neuroscience-gap-closure
git reset --hard backup/neuroscience-pre-rebase

# 2. Confirmar integridade
git status
git log -n 1 --oneline
# Deve exibir commit 0a248c2
```

### 6.3 Estratégia Alternativa de Integração (Squash & Cherry-Pick Unificado)
Caso o rebase commit-a-commit apresente atrito excessivo no grafo de histórico, a alternativa recomendada é a reconciliação limpa em um commit semântico unificado:
```powershell
# 1. Criar branch de transição a partir de branding validado
git checkout -b feature/neuroscience-stabilized feature/branding

# 2. Mesclar o conteúdo da árvore de neurociência sem commitar
git merge --no-commit --no-ff feature/neuroscience-gap-closure

# 3. Aplicar as 11 correções documentadas na Seção 4
# 4. Executar a suíte de verificação da Seção 5
# 5. Efetuar commit de consolidação convencional:
git commit -m "feat(neuroscience): reconcile sensory mechanics and student identity onto Brand Book v3.1"

# 6. Atualizar ponteiro de feature/neuroscience-gap-closure
git checkout feature/neuroscience-gap-closure
git reset --hard feature/neuroscience-stabilized
```

---
*Plano gerado pelo Worker M5 em conformidade estrita com o Mandato de Integridade e os Padrões de Engenharia de Software da Plataforma Saebom Companion.*
