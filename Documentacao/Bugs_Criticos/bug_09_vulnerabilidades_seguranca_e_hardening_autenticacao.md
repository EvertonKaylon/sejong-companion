# BUG-09: Vulnerabilidades Críticas de Autenticação Administrativa e Hardening de Sessão

| Metadado | Detalhe |
| :--- | :--- |
| **ID do Bug** | `BUG-09` |
| **Severidade** | 🔴 **Crítica (P0/P1)** — Bloqueador de Release Pública |
| **Componentes Afetados** | `AdminService`, `ProgressService`, `AudioService`, `OnboardingView`, `docker-compose.yml`, `.gitignore` |
| **Data da Resolução** | 2026-08-28 |
| **Branch de Correção** | `security/hardening-v0.3.2` |
| **Suíte de Testes** | `tests/test_admin_service.py`, `tests/test_admin_auth_hardening.py`, `tests/test_student_identity_security.py`, `tests/test_telemetry_privacy_and_rotation.py` |

---

## 1. Descrição Sintomática e Riscos de Segurança Identificados

Durante a auditoria de segurança pré-merge da `main`, foram identificadas 4 superfícies críticas de vulnerabilidade:

1. **Credencial Administrativa Padrão Conhecida (P0)**:
   O `AdminService` definia `DEFAULT_PIN = "sejong2026"` e aceitava esse valor como fallback caso a variável de ambiente `SEJONG_ADMIN_PIN` não estivesse configurada. Além disso, `docker-compose.yml` utilizava a sintaxe `${SEJONG_ADMIN_PIN:-sejong2026}`, permitindo que qualquer instância exposta publicamente tivesse seu painel administrativo acessível por força de credencial padrão.
2. **Ausência de Rate Limiting e Vulnerabilidade a Timing Attacks (P1)**:
   A rota `/admin` não limitava tentativas incorretas de login, permitindo ataques de força bruta ilimitados. A comparação do PIN utilizava o operador padrão `==`, suscetível a ataques de temporização (timing attacks).
3. **Student ID Atuando Simultaneamente como Identificador e Credencial de Recuperação (P1)**:
   Na tela de Onboarding, informar apenas o `student_id` público permitia carregar e assumir o perfil de qualquer estudante sem necessidade de segredo ou senha de autorização.
4. **Cache Mutável Misturado à Árvore de Assets Estáticos (P1)**:
   O `AudioService` gravava arquivos de áudio sintetizados em runtime dentro de `assets/audio_cache/`. Em ambientes de container e no Flet 0.86+, a pasta `assets/` deve ser estritamente *read-only*. Além disso, dados mutáveis em `data/` não possuíam regras estritas no `.gitignore` nem limites de retenção de telemetria.

---

## 2. Causa Raiz Técnica

* **Modelo de Confiança Inseguro**: O sistema tratava identificadores públicos (`student_id`) como tokens de autorização de takeover de conta.
* **Fail-Open na Configuração**: O fallback do PIN adotava a postura *fail-open* em vez de *fail-closed*. Sem a variável de ambiente, o sistema abria o acesso em vez de rejeitar.
* **Falta de Isolamento de Armazenamento**: A separação entre assets estáticos do bundle (fontes, imagens) e dados mutáveis de cache/banco em runtime não estava formalmente isolada na raiz da aplicação.

---

## 3. Arquitetura da Solução Aplicada

```
                                  PIPELINE DE SEGURANÇA E HARDENING
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ 1. ADMIN SERVICE (Fail-Closed & Rate-Limited)                                                          │
│    • SEJONG_ADMIN_PIN obrigatório (sem DEFAULT_PIN)                                                    │
│    • Lockout progressivo: 5 falhas → 30s | 10 falhas → 5 min                                          │
│    • hmac.compare_digest para mitigação total de timing attacks                                       │
│    • Tokens de sessão efêmeros (secrets.token_urlsafe) com expiração em 1 hora                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. IDENTIDADE DO ALUNO (Zero Credential em ID Público)                                                 │
│    • student_id (identificador público) ≠ recovery_secret (chave privada XXXX-XXXX-XXXX)             │
│    • Armazenamento no disco exclusivo do hash salted SHA-256 (recovery_salt + recovery_hash)          │
│    • Restauração em novo dispositivo exige: Student ID + Chave de Recuperação                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. ISOLAMENTO DE CACHE E PRIVACIDADE DE DADOS                                                          │
│    • assets/ → 100% estático (read-only bundle)                                                       │
│    • Cache de áudio mutável → data/cache/audio/ (ou FLET_APP_STORAGE_CACHE)                            │
│    • TelemetryService com rotação automática (MAX_EVENTS_PER_FILE = 5000)                             │
│    • .gitignore protegendo data/sessions/, data/telemetry/, data/reports/, data/cache/, *.jsonl        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. CI AUTOMATIZADO (GitHub Actions)                                                                    │
│    • .github/workflows/ci.yml com compilação, scan de segredos e suíte de 106 testes automatizados    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Código Antes vs Depois

### A. Autenticação Administrativa (`src/services.py`)

#### ❌ Antes (Inseguro - Fallback Padrão Conhecido)
```python
class AdminService:
    DEFAULT_PIN: str = "sejong2026"

    @classmethod
    def authenticate(cls, pin: str) -> bool:
        if not pin:
            return False
        expected = os.environ.get("SEJONG_ADMIN_PIN", cls.DEFAULT_PIN).strip()
        return pin.strip() == expected
```

#### ✅ Depois (Seguro - Fail-Closed, Rate Limit e Timing Safe)
```python
class AdminService:
    _failed_attempts: Dict[str, List[float]] = {}
    _lockouts: Dict[str, float] = {}
    _active_tokens: Dict[str, float] = {}

    MAX_ATTEMPTS_TIER_1: int = 5
    LOCKOUT_DURATION_TIER_1: float = 30.0
    MAX_ATTEMPTS_TIER_2: int = 10
    LOCKOUT_DURATION_TIER_2: float = 300.0
    SESSION_DURATION_SECONDS: float = 3600.0

    @classmethod
    def get_configured_pin(cls) -> Optional[str]:
        pin = os.environ.get("SEJONG_ADMIN_PIN")
        return pin.strip() if pin else None

    @classmethod
    def login(cls, pin: str, client_key: str = "default") -> Tuple[bool, Optional[str], str]:
        remaining = cls.get_lockout_remaining(client_key)
        if remaining > 0:
            return False, None, f"Muitas tentativas. Bloqueio ativo por mais {int(remaining) + 1}s."

        expected = cls.get_configured_pin()
        if not expected:
            return False, None, "Autenticação administrativa desabilitada (SEJONG_ADMIN_PIN não configurado)."

        if not hmac.compare_digest(str(pin).strip(), expected):
            # Registra tentativa falha e dispara lockout se atingir o limiar
            ...
            return False, None, "PIN incorreto."

        cls.reset_rate_limit(client_key)
        token = secrets.token_urlsafe(32)
        cls._active_tokens[token] = time.time() + cls.SESSION_DURATION_SECONDS
        return True, token, "Autenticado com sucesso."
```

### B. Recuperação de Estudante (`src/services.py`)

#### ❌ Antes (Inseguro - ID público recuperava a conta)
```python
# Qualquer um que soubesse "student_a1b2c3d4e5f6" carregava os dados
page._sejong_student_id = code
ps = ProgressService(page)
existing_name = ps.get_student_name()
```

#### ✅ Depois (Seguro - Hash Salted e Chave Privada)
```python
@classmethod
def verify_and_restore_student(cls, student_id_or_name: str, recovery_code: str) -> Tuple[bool, ...]:
    # Localiza a sessão pelo ID ou Nome
    ...
    salt = target_data.get("recovery_salt")
    expected_hash = target_data.get("recovery_hash")
    if not salt or not expected_hash:
        return False, None, None, "Perfil sem chave de recuperação registrada."

    computed_hash = cls._hash_recovery_code(salt, recovery_code)
    if not hmac.compare_digest(computed_hash, expected_hash):
        return False, None, None, "Chave de recuperação incorreta."

    return True, s_id, s_name, "Restaurado com sucesso!"
```

---

## 5. Regras Preventivas para o Desenvolvimento Futuro

1. **Nunca Utilizar Credenciais Padrão no Código**: Qualquer segredo de sistema deve ser injetado exclusivamente via variável de ambiente. Se a variável não existir, a aplicação deve falhar de forma fechada (*fail-closed*).
2. **Sempre Comparar Segredos em Tempo Constante**: Usar `hmac.compare_digest()` para todas as verificações de tokens, PINs e senhas.
3. **Desacoplar Identificador de Autorização**: O identificador de um recurso (ID público) nunca deve ser a chave que autoriza sua modificação ou recuperação.
4. **Isolar Diretórios Mutáveis**: Manter a árvore `assets/` estritamente estática e destinar arquivos gerados em runtime para `data/cache/`, `data/sessions/` e `data/telemetry/`.
