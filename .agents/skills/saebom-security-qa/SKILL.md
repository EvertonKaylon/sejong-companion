---
name: saebom-security-qa
description: >-
  Executa o pipeline completo de Security QA do Saebom Companion (새봄 컴패니언):
  linhagem de segurança Git, proteção Zero-PII, SAST AST, varredura de segredos,
  hardening Docker/Caddy/OCI, SAST/SCA externos (bandit, pip-audit, trivy), bateria
  pytest de segurança e DAST Playwright. Use antes de merges em develop/main, releases
  ou após alterações em autenticação, persistência, proxy ou containers.
---

# Security QA — Saebom Companion

## Quando Ativar
- Antes de promover qualquer branch para `develop` ou `main`
- Após alterações em `src/services.py` (`AdminService`, `ProgressService`, `TelemetryService`), `src/announcement_service.py`, `src/views/admin_view.py`, `Caddyfile`, `Dockerfile`, `docker-compose.yml` ou `scripts/setup_oci_server.sh`
- Durante auditorias OWASP Top 10 / MITRE ATT&CK ou ao invocar `/saebom-security-qa`

## Pipeline Completo em 6 Etapas

### Etapa 1 — Linhagem Git & Privacidade Zero-PII
Confirmar que a âncora histórica de hardening permanece ancestral do `HEAD` e que nenhum arquivo mutável ou com dados pessoais foi rastreado:
```powershell
git merge-base --is-ancestor security/hardening-v0.3.2 HEAD
git ls-files data/sessions/ data/telemetry/ data/reports/ data/cache/ *.jsonl .env*
```

### Etapa 2 — Auditoria Automatizada Local (`scripts/security_qa_audit.py`)
Executar o auditor unificado (exit code `0` = aprovado; `1` = falha crítica):
```powershell
.venv\Scripts\python.exe -m scripts.security_qa_audit
```
Verifica automaticamente:
1. `git_security_lineage` — `security/hardening-v0.3.2` ancestral de `HEAD`.
2. `zero_pii_tracked_files` — `0` arquivos rastreados em `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, `*.jsonl` ou `.env*`.
3. `secret_scan` — ausência de PINs comprometidos, `DEFAULT_PIN` ou tokens/chaves privadas no código e infraestrutura.
4. `python_sast_ast` — inspeção AST em `src/` e `main.py` para bloquear `eval()`, `exec()`, `pickle.load(s)`, `yaml.load()` sem `SafeLoader`, `subprocess.*(shell=True)` e escrita em `assets/` (*read-only*).
5. `crypto_and_infra_hardening` — uso de `hmac.compare_digest` (auth + recovery), `.dockerignore`, `USER saebomuser` no `Dockerfile`, `no-new-privileges:true` + `SAEBOM_ADMIN_PIN:?` + sem publicação de `8554` no `docker-compose.yml`, separação `:80` (sem HSTS) vs HTTPS (com HSTS + CSP completo) no `Caddyfile` e ausência da porta `8554` em `scripts/setup_oci_server.sh`.

### Etapa 3 — SAST, SCA e IaC Externos (CI e Ambiente Local)
Quando instalados localmente ou executados pelo job `security-qa` em `.github/workflows/ci.yml`:
```powershell
bandit -r src main.py -lll -ii
pip-audit -r requirements.txt
trivy config .   # opcional em ambiente com Trivy CLI
gitleaks detect --no-git -v  # opcional em ambiente com Gitleaks
```

### Etapa 4 — Bateria Dedicada de Testes de Segurança (`pytest`)
Executar a suíte obrigatória de segurança definida em `GEMINI.md` junto aos testes do pipeline:
```powershell
.venv\Scripts\python.exe -m pytest `
  tests/test_admin_auth_hardening.py `
  tests/test_student_identity_security.py `
  tests/test_telemetry_privacy_and_rotation.py `
  tests/test_infrastructure_security.py `
  tests/test_security_qa_pipeline.py -v
```

### Etapa 5 — DAST / Verificação em Browser Real (Playwright)
Validar que a barreira `/admin` não vaza o PIN no DOM, não redireciona indevidamente para `/onboarding` e que as rotas Web sobem sem erros críticos:
```powershell
.venv\Scripts\python.exe -m pytest tests/test_playwright_e2e.py -k test_p4_admin_security_barrier -v
```
*(Em validações de deploy atrás do Caddy, verificar também headers HTTP em `:80` vs `:443`, boot CanvasKit/WASM sem bloqueios de CSP no console e escrita com UID `10001` nos named volumes.)*

### Etapa 6 — Consolidação OWASP / MITRE ATT&CK
Classificar achados em **Bloqueadores (FAIL)** vs **Advisories (WARN)**, documentando eventuais regressões críticas em `Documentacao/Bugs_Criticos/` via `/saebom-docs-sync`.

---

## Topologia Recomendada com `/swarm`
Ao paralelizar a auditoria com `/swarm` (todos os agentes em `workspace: "inherit"`, somente leitura):
- **`sec-static`**: executa Etapas 1, 2 e 3 (`scripts.security_qa_audit`, `compileall`, `bandit`/`pip-audit`/`trivy`, revisão de diffs).
- **`sec-runtime`**: executa Etapas 4 e 5 (`pytest` de segurança + Playwright `test_p4_admin_security_barrier` / validação HTTP/Caddy).
- **`sec-verifier`**: cruza os achados de `sec-static` e `sec-runtime` contra `GEMINI.md` e OWASP Top 10 / MITRE ATT&CK antes de liberar o merge.

## Critérios Fail-Closed
1. **Bloqueio Imediato (`exit 1`):** quebra de linhagem `security/hardening-v0.3.2`, qualquer PII/sessão/`.env` rastreado no Git, segredo/PIN padrão no código, chamada AST insegura, ausência de `hmac.compare_digest`, exposição da porta `8554`, HSTS em HTTP `:80`, falha em qualquer teste de segurança ou vazamento do PIN no DOM.
2. **Advisories (`WARN`, não bloqueantes localmente):** ausência local de scanners opcionais (`bandit`, `pip-audit`, `trivy`, `gitleaks`) quando compensada pela execução no CI `.github/workflows/ci.yml`, ou CVEs upstream sem patch reportadas no relatório `pip-audit`.
