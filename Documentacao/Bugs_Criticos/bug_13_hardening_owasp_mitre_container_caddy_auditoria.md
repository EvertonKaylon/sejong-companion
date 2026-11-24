# BUG-13: Hardening OWASP Top 10 & MITRE ATT&CK em Container, Proxy Caddy, Auditoria e Sanitização (e Lacunas Residuais v0.3.8)

| Metadado | Detalhe |
| :--- | :--- |
| **ID do Bug** | `BUG-13` |
| **Severidade** | 🔴 **Crítica (Segurança de Infraestrutura, Proxy & Auditoria)** |
| **Componentes Afetados** | `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `Caddyfile`, `AdminService` (`src/services.py`), `AnnouncementService` (`src/announcement_service.py`), `admin_view.py` (`src/views/admin_view.py`), `main.py`, `src/theme.py` |
| **Data de Registro / Commit Base** | 2026-09-21 (`d6289d5`) / Auditoria v0.3.8 (2026-11-23) |
| **Branch** | `security/mitre-owasp-hardening` |
| **Suíte de Testes** | `tests/test_infrastructure_security.py` (6/6 PASS); bateria de segurança (`19 passed in 1.31s`) + `test_p4_admin_security_barrier` (`1 passed`) |

---

## 1. Descrição Sintomática

A revisão de segurança voltada à conformidade com **OWASP Top 10 (2021/2025)** e **MITRE ATT&CK Enterprise** identificou exposições críticas na camada de containerização, proxy reverso, trilha de auditoria e entrada de dados do Mural da Professora (`d6289d5`):

1. **Build Docker sem `.dockerignore` e Execução como `root`:** A imagem incluía arquivos locais sensíveis (`.env`, `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, PDFs) no contexto de build (`COPY . .`) e executava o processo Python/Uvicorn como usuário `root`.
2. **Proxy Caddy sem Cabeçalhos Defensivos OWASP:** O `Caddyfile` encaminhava tráfego sem `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` nem supressão do banner `-Server`, mantendo ainda o domínio legado anterior.
3. **Ausência de Trilha de Auditoria de Autenticação:** Falhas de login, lockouts e sucessos em `AdminService.login()` não geravam eventos persistentes de auditoria de segurança (`security_audit`).
4. **Entrada Irrestrita no Mural Pedagógico:** `AnnouncementService.post_announcement()` aceitava strings sem teto de comprimento nem remoção de bytes nulos (`\x00`).
5. **Regressões/Conflitos Residuais em Runtime Pós-`d6289d5`:** Como `tests/test_infrastructure_security.py` executa apenas verificações estáticas de arquivo e unitárias em memória/diretório temporário (sem subir os containers nem o navegador atrás do Caddy), cinco conflitos reais de runtime permaneceram abertos após o commit.

---

## 2. Causa Raiz Técnica

* **Superfície de Container e Build (OWASP A01/A05 · MITRE T1552.001, T1005, T1068, T1611):** O `Dockerfile` copiava toda a árvore do diretório de trabalho sem arquivo `.dockerignore` e não declarava diretiva `USER` não-privilegiada; o `docker-compose.yml` não aplicava `security_opt: [no-new-privileges:true]` nem montava o volume de `data/announcements.json`.
* **Proxy Reverso sem Blindagem HTTP (OWASP A03/A05 · MITRE T1059.007, T1189, T1190, T1592):** O `Caddyfile` expunha o cabeçalho `Server` padrão e não impunha políticas de cabeçalhos de segurança no tráfego Web/WebSocket.
* **Cegueira de Monitoramento e Falta de Limites de Payload (OWASP A03/A04/A09 · MITRE T1070, T1110, T1499):** `AdminService.login()` atualizava apenas contadores voláteis em memória (`_failed_attempts`, `_lockouts`) sem persistir eventos `security_audit`, e `AnnouncementService.post_announcement()` não truncava nem sanitizava `\x00`.
* **Validação Apenas Estática na Suíte Automatizada:** A ausência de testes de integração reais com Docker Compose + Caddy + Playwright permitiu que regras estritas do `Caddyfile` (CSP/HSTS) e de UID `10001` no `Dockerfile` entrassem em conflito com o boot do Flutter Web e com permissões de bind mounts no host Linux.

---

## 3. Código Antes vs Depois (Commit `d6289d5`)

### A. Blindagem de Build (`.dockerignore` — Novo Arquivo de 51 Linhas)

#### ❌ Antes
* Arquivo `.dockerignore` inexistente na raiz do projeto; `COPY . .` incorporava potencialmente `.env*`, `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, `*.jsonl` e `*.pdf` na imagem.

#### ✅ Depois (`.dockerignore:1-51`)
```gitignore
# .dockerignore — Saebom Companion
# Prevenção de vazamento de segredos, dados mutáveis e artefatos de build na imagem Docker
# (OWASP A05: Security Misconfiguration / MITRE ATT&CK T1552.001 & T1005)

# Segredos e Variáveis de Ambiente Locais
.env
*.env
.env.*

# Controle de Versão
.git
.github

# Ambientes Virtuais e Dependências Locais
.venv
venv
ENV
env

# Caches do Python e Ferramental de Testes
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.coverage
htmlcov

# IDEs e Editores
.vscode
.idea
*.swp
*.swo

# Dados Mutáveis em Runtime e Privacidade do Aluno (Zero Data Leak)
data/sessions/
data/telemetry/
data/reports/
data/cache/
*.jsonl
*.tmp
*.tmp.*
*.bak
*.corrupt.*

# Documentos Volumosos e Artefatos Locais
*.pdf
WhatsApp*
scratch/
tests/screenshots/
gabarito*
```

### B. Execução Não-Privilegiada (`Dockerfile:28-37`)

#### ❌ Antes
```dockerfile
# Criar diretórios persistentes de dados e cache de áudio (processo rodava como root)
RUN mkdir -p /app/data/cache/audio /app/data/sessions /app/data/telemetry /app/data/reports
```

#### ✅ Depois (`Dockerfile:28-37`)
```dockerfile
# Criar usuário não-privilegiado saebomuser (Princípio do Menor Privilégio - OWASP A05 / MITRE T1068 & T1611)
RUN groupadd -g 10001 saebom && \
    useradd -u 10001 -g saebom -s /bin/sh -m saebomuser

# Criar e garantir permissões para os diretórios persistentes de dados e cache de áudio
RUN mkdir -p /app/data/cache/audio /app/data/sessions /app/data/telemetry /app/data/reports && \
    chown -R saebomuser:saebom /app

# Executar como usuário não-root
USER saebomuser
```

### C. Orquestração (`docker-compose.yml:6-30`)

#### ❌ Antes
```yaml
    container_name: sejong-companion-app
    restart: always
    environment:
      - PORT=8554
      - SEJONG_ADMIN_PIN=${SEJONG_ADMIN_PIN:?SEJONG_ADMIN_PIN environment variable is required}
      - TYPECAST_API_KEY=${TYPECAST_API_KEY:-}
...
  caddy:
    image: caddy:2-alpine
    container_name: sejong-companion-caddy
    restart: always
```

#### ✅ Depois (`docker-compose.yml:6-30`)
```yaml
    container_name: saebom-companion-app
    restart: always
    security_opt:
      - no-new-privileges:true
    environment:
      - PORT=8554
      - SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:-}
      - TYPECAST_API_KEY=${TYPECAST_API_KEY:-}
    expose:
      - "8554"
    volumes:
      - ./data/cache/audio:/app/data/cache/audio
      - ./data/sessions:/app/data/sessions
      - ./data/telemetry:/app/data/telemetry
      - ./data/reports:/app/data/reports
      - ./data/announcements.json:/app/data/announcements.json
...
  caddy:
    image: caddy:2-alpine
    container_name: saebom-companion-caddy
    restart: always
    security_opt:
      - no-new-privileges:true
```

### D. Cabeçalhos de Segurança no Proxy Reverso (`Caddyfile:1-38`)

#### ❌ Antes
```caddyfile
sejongcompanion.duckdns.org, :80 {
    reverse_proxy app:8554 {
        ...
    }
    encode zstd gzip
}
```

#### ✅ Depois (`Caddyfile:1-38`)
```caddyfile
saebomcompanion.duckdns.org, :80, :443 {
    reverse_proxy app:8554 {
        ...
    }
    encode zstd gzip
    header {
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=()"
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com; style-src 'self' 'unsafe-inline'; font-src 'self' data:; img-src 'self' data: https: blob:; connect-src 'self' ws: wss:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';"
        -Server
    }
}
```

### E. Trilha de Auditoria Zero-PII (`src/services.py:1399-1465`)

#### ❌ Antes (Sem persistência de auditoria em falhas, lockouts e logins)
```python
            count = len(attempts)
            if count >= cls.MAX_ATTEMPTS_TIER_2:
                cls._lockouts[client_key] = now + cls.LOCKOUT_DURATION_TIER_2
                return False, None, f"Acesso administrativo bloqueado por {int(cls.LOCKOUT_DURATION_TIER_2 // 60)} minutos."
            elif count >= cls.MAX_ATTEMPTS_TIER_1:
                cls._lockouts[client_key] = now + cls.LOCKOUT_DURATION_TIER_1
                return False, None, f"Muitas tentativas incorretas. Bloqueio temporário de {int(cls.LOCKOUT_DURATION_TIER_1)}s."
...
        cls.reset_rate_limit(client_key)
        token = secrets.token_urlsafe(32)
        cls._active_tokens[token] = now + cls.SESSION_DURATION_SECONDS
        return True, token, "Autenticado com sucesso."
```

#### ✅ Depois (`AdminService.login()` em `src/services.py:1399-1465`)
```python
            count = len(attempts)

            # Registro de auditoria estruturado (OWASP A09:2021 / MITRE ATT&CK T1070 & T1110)
            try:
                TelemetryService.record(
                    session_id=f"audit_{client_key}",
                    event=PedagogicalEvent(
                        event_type="security_audit",
                        unit_id="admin_auth_barrier",
                        item_id="login_failed",  # também registra "lockout_tier1", "lockout_tier2" e "login_success"
                        payload={"client_key": client_key, "action": "failed_attempt", "count": count},
                    ),
                )
            except Exception:
                pass
```

### F. Sanitização e Teto de Payload (`src/announcement_service.py:50-83`)

#### ❌ Antes
```python
clean_title = (title or "").strip()
clean_content = (content or "").strip()
...
"author": (author or "Professora").strip(),
```

#### ✅ Depois (`src/announcement_service.py:50-83`)
```python
MAX_TITLE_LENGTH: int = 120
MAX_CONTENT_LENGTH: int = 1000
MAX_AUTHOR_LENGTH: int = 50
...
clean_title = (title or "").strip().replace("\x00", "")[:cls.MAX_TITLE_LENGTH]
clean_content = (content or "").strip().replace("\x00", "")[:cls.MAX_CONTENT_LENGTH]
clean_author = (author or "Professora").strip().replace("\x00", "")[:cls.MAX_AUTHOR_LENGTH] or "Professora"
```

### G. Suíte Automatizada de Segurança de Infraestrutura (`tests/test_infrastructure_security.py:20-150`)

#### ❌ Antes
* Não existiam testes automatizados validando `.dockerignore`, `USER saebomuser` no `Dockerfile`, cabeçalhos OWASP no `Caddyfile`, `no-new-privileges:true` no `docker-compose.yml`, trilha `security_audit` ou truncamento/expurgo de `\x00` em `AnnouncementService`.

#### ✅ Depois (`tests/test_infrastructure_security.py:95-150`, trechos representativos dos 6 testes adicionados)
```python
def test_admin_auth_records_security_audit_events(monkeypatch, tmp_path):
    """Valida que falhas de autenticação e lockouts geram eventos de auditoria de segurança no TelemetryService."""
    monkeypatch.setattr(TelemetryService, "_get_telemetry_dir", lambda: str(tmp_path))
    monkeypatch.setenv("SAEBOM_ADMIN_PIN", "correct_pin_456")
    monkeypatch.delenv("SEJONG_ADMIN_PIN", raising=False)

    client_key = "test_audit_client_99"
    AdminService.reset_rate_limit(client_key)

    success, token, msg = AdminService.login("wrong_pin", client_key=client_key)
    assert success is False

    events = TelemetryService.get_events(session_id=f"audit_{client_key}")
    assert len(events) >= 1
    assert events[-1].event_type == "security_audit"
    assert events[-1].item_id == "login_failed"
    assert "wrong_pin" not in str(events[-1].payload)

def test_announcement_service_enforces_length_limits_and_null_byte_sanitization(tmp_path, monkeypatch):
    """Valida que o AnnouncementService trunca entradas longas e remove caracteres nulos sem sujar os dados reais."""
    temp_storage = tmp_path / "announcements.json"
    monkeypatch.setattr(AnnouncementService, "_get_data_path", lambda: str(temp_storage))

    ann = AnnouncementService.post_announcement(
        title="A" * 200,
        content="B" * 1500,
        author="Professora\x00Hacker",
    )
    assert len(ann["title"]) == AnnouncementService.MAX_TITLE_LENGTH
    assert len(ann["content"]) == AnnouncementService.MAX_CONTENT_LENGTH
    assert "\x00" not in ann["author"]
```

---

## 4. Lacunas e Regressões Residuais Abertas (Auditoria v0.3.8)

A auditoria de infraestrutura e código identificou **5 lacunas concretas** que permaneceram abertas após `d6289d5` e ainda precisam de correção antes do deploy em produção atrás do Caddy:

1. **CSP do `Caddyfile:33` bloqueia o boot do Flet/Flutter Web (CanvasKit / Skwasm):**
   * `main.py:124` não passa `no_cdn=True`; em runtime, `flet_web` injeta `flet.noCdn=false` e `flutter_bootstrap.js` carrega `canvaskit.js` e `canvaskit.wasm` de `https://www.gstatic.com/flutter-canvaskit/...`, além de criar worker `blob:` (`URL.createObjectURL(new Blob(...))`) no `skwasm`.
   * O cabeçalho `Content-Security-Policy` de `Caddyfile:33` **omite `https://www.gstatic.com`** em `script-src` e `connect-src`, **omite `worker-src 'self' blob:`** (herdando `default-src 'self'`), **omite `'wasm-unsafe-eval'`** e bloqueia fallback externo `https://fonts.gstatic.com` em `font-src 'self' data:` (enquanto `src/theme.py:287-288` ainda aponta para `fonts.googleapis.com`). Em produção real atrás do Caddy, o CanvasKit tende a falhar no boot.
2. **Bloco único `:80, :443` emitindo HSTS em HTTP plano (`Caddyfile:3,30`):**
   * `Caddyfile:3` agrupa `saebomcompanion.duckdns.org, :80, :443` no mesmo bloco, enviando `Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"` em respostas HTTP `:80` (violação da RFC 6797 §7.2), desabilitando o redirecionamento automático HTTP → HTTPS para o domínio DuckDNS e expondo `:443` sem política de certificado para acesso direto por IP.
3. **Conflito de permissões `USER saebomuser` (`Dockerfile:29-37`, UID `10001`) × Bind Mounts (`docker-compose.yml:18-22`):**
   * Embora `Dockerfile:33-34` execute `chown -R saebomuser:saebom /app` na imagem, os bind mounts em `docker-compose.yml:18-22` montam diretórios locais (`./data/cache/audio`, `./data/sessions`, `./data/telemetry`, `./data/reports`, que o Docker cria como `root:root 0755` após `git clone`) e o arquivo rastreado `./data/announcements.json` (pertencente ao UID do host, modo `0644`). Em host Linux/OCI, o processo com UID `10001` receberá `PermissionError` ao gravar sessões, auditoria/telemetria, relatórios, cache de áudio e comunicados (e `scripts/setup_oci_server.sh:22` também ainda abre a porta `8554` no `iptables` e não prepara permissões para `10001:10001`).
4. **Poluição de KPIs pedagógicos e colisão global de `client_key` na trilha `security_audit` (`src/services.py:1403-1464,1627-1635`; `src/views/admin_view.py:215`):**
   * `AdminService.login()` registra eventos `security_audit` via `TelemetryService.record(session_id=f"audit_{client_key}", ...)`, porém `AdminService.get_global_kpis()` (`src/services.py:1627,1635`) lê `TelemetryService.get_events()` sem filtrar `event_type != "security_audit"`, contaminando `total_telemetry_events`.
   * `src/views/admin_view.py:215` define `client_key = getattr(page, "_sejong_student_id", None) or "admin_client"`: acessos diretos via deep link `/admin` (sem onboarding prévio) compartilham o único balde `"admin_client"`, permitindo DoS de lockout global na conta da professora após 5 tentativas falhas de qualquer visitante.
5. **Relaxamento de startup fail-closed no Compose & escrita não-atômica em `AnnouncementService`:**
   * `docker-compose.yml:12` alterou `${SEJONG_ADMIN_PIN:?...}` para `SAEBOM_ADMIN_PIN=${SAEBOM_ADMIN_PIN:-}` (permite que o container suba sem PIN definido, embora `AdminService.login()` siga fail-closed).
   * `src/announcement_service.py:40-48` documenta persistência atômica na docstring, mas usa `open(path, "w")` direto (e uma substituição por `os.replace()` falharia com `EBUSY` sobre bind mount de arquivo único `./data/announcements.json`).

---

## 5. Regras Preventivas

1. **Testar CSP e Proxy em Runtime Real (ou `no_cdn=True`):** Toda alteração de `Content-Security-Policy` no `Caddyfile` deve ser validada com boot completo do Flet Web (`flutter_bootstrap.js` + `canvaskit`/`skwasm`) ou combinada com `no_cdn=True` e assets/fontes 100% locais.
2. **Separar Bloco `:80` (Redirect HTTPS) de `:443` (HSTS):** Nunca emitir cabeçalho `Strict-Transport-Security` em porta HTTP não criptografada (`:80`).
3. **Compatibilizar UID Não-Root com Persistência em Volume:** Ao adotar `USER saebomuser` (`10001:10001`), preferir volumes nomeados ou preparar/garantir ownership `10001:10001` no diretório `./data/` (evitando bind mounts de arquivo único como `./data/announcements.json`).
4. **Isolar Logs de Auditoria das Métricas Pedagógicas:** Eventos `event_type == "security_audit"` devem ser excluídos de KPIs pedagógicos (`get_global_kpis`) e o rate limiter de `/admin` deve usar chave isolada por sessão/IP real (`X-Real-IP` / `session_id`) em vez de fallback global compartilhado.
5. **Preservar Fail-Closed em Variáveis Críticas de Compose:** Sempre que viável em produção, manter checagem obrigatória (`:?`) para `SAEBOM_ADMIN_PIN` ou validar pré-requisito no script de provisionamento.
