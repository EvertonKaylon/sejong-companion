# Sejong Companion — Regras do Projeto

## Identidade do Projeto
- **Nome:** Sejong Companion (세종학당 컴패니언)
- **Stack:** Python + Flet (Flutter Engine) — Web, Android, iOS, Desktop
- **Fase atual:** Alpha (`v0.3.2-alpha`)
- **Documentação oficial:** `Documentacao/` (estrutura Obsidian com wikilinks)

## Convenções de Código e Commits
- Usar **Conventional Commits** em português/inglês técnico: `tipo(escopo): descrição`
  - Tipos válidos: `feat`, `fix`, `refactor`, `docs`, `ci`, `test`, `chore`, `perf`, `security`
- Branch naming: `feature/*`, `fix/*`, `security/*`, `docs/*`
- Nunca commitar credenciais padrão ou segredos no código-fonte. Usar variáveis de ambiente com postura **fail-closed**.

## Segurança (Regras Invioláveis)
- Comparação de segredos (PINs, tokens, recovery keys) SEMPRE via `hmac.compare_digest`.
- Identificadores públicos (student_id) NUNCA devem servir como credencial de autorização.
- `assets/` é estritamente read-only. Dados mutáveis vão para `data/` (cache, sessions, telemetry, reports).
- O `.gitignore` DEVE proteger `data/sessions/`, `data/telemetry/`, `data/reports/`, `data/cache/`, `*.jsonl`.

## Documentação Oficial — Sincronização Obrigatória
Ao concluir qualquer alteração significativa (feature, bugfix, security, refactor), o agente DEVE atualizar:
1. **`Documentacao/Changelogs_e_Historico/CHANGELOG.md`** — Adicionar entrada de release com seções Added/Fixed/Security/Changed conforme [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).
2. **`Documentacao/Bugs_Criticos/INDICE_BUGS.md`** — Se um bug foi corrigido, adicionar a entrada na tabela com severidade, categoria e link.
3. **`Documentacao/Bugs_Criticos/bug_XX_*.md`** — Para bugs complexos, criar arquivo dedicado com: Diagnóstico, Causa Raiz, Código Antes/Depois, Regras Preventivas.
4. **`Documentacao/INDICE_DOCUMENTACAO.md`** — Atualizar o índice mestre se novos documentos foram criados.
5. **Nunca esperar o usuário perguntar "está documentado?"** — a documentação é parte integrante da entrega.

## Testes
- Toda alteração de código deve ser acompanhada de testes automatizados em `tests/`.
- Ao finalizar uma branch, executar `pytest tests/ -v` e confirmar 100% de aprovação antes de commitar documentação ou solicitar merge.
- O CI (`.github/workflows/ci.yml`) valida: compileall, secret scanning e pytest.
