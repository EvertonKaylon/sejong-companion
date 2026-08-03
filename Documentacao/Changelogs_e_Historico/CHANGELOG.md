# Changelog — Sejong Companion

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## Ciclo de Vida do Projeto

```
Pré-Alpha → Alpha → Beta → RC → RTM → GA
               ▲
          ESTAMOS AQUI
          v0.1.0-alpha
```

| Fase | Versão Alvo | Critérios de Entrada |
|------|-------------|----------------------|
| **Alpha** (atual) | `0.1.0-alpha` | Features core funcionais, testes internos, software incompleto |
| **Beta** | `0.1.0-beta` | Todas as unidades do Livro 1A implementadas, persistência real, responsivo mobile |
| **RC** | `1.0.0-rc.1` | Feature-complete, testes E2E, zero bugs críticos |
| **GA** | `1.0.0` | Pronto para distribuição pública |

---

## [0.1.0-alpha] — 2026-07-23

### Classificação: Alpha
> Software funcional com features core implementadas, testado internamente.
> Incompleto: faltam unidades curriculares, persistência real, responsividade mobile.

### Added — Features
- **Serviço de Áudio TTS Offline-First** — Typecast.ai (primário) + Google TTS (fallback), cache atômico em disco, autoplay unlock para navegadores
- **Design System Completo** — Escalas de cor (50→950) portadas de Next.js/shadcn/ui, tema claro/escuro com toggle instantâneo
- **Módulo Hangul (Unit Intro)** — 4 abas (Vogais, Consoantes, 받침, Sílabas), HangulCard com flip + hover + áudio
- **Módulo de Lições (Unit 01)** — Vocabulário, Gramática, Notas Culturais com VocabCard interativo
- **Motor de Quiz Unificado** — Multiple choice + order_words (SOV), tela de resultados com placar
- **Dashboard Home** — Grade curricular, progresso geral, painel de cronobiologia adaptativo
- **Router SPA** — Navegação por builder functions, fallback, estado de unidade
- **Persistência em Memória** — ProgressService com desbloqueio progressivo (unit_intro → unit_01)
- **Pedagogia Neuro-Linguística** — Anti-romanização, alerta "i fantasma" (epêntese lusófona), dicas mnemônicas, neuro-tips por vocabulário
- **Suíte TDD** — 20 testes unitários (audio, data, progress, router) com mocks Flet

### Added — Infra
- `requirements.txt` — flet==0.85.3, pydantic>=2.0.0, requests>=2.34.2, flet-audio==0.85.3
- `.env` — API key Typecast (gitignored)
- `.gitignore`
- `DESIGN_SYSTEM_CHANGELOG.md` — Registro de decisões de portabilidade visual

### Fixed — Bugs Resolvidos
- `Unknown control: Audio` + loop de reinício desktop (player movido para atributo do AudioService)
- `RuntimeError: Session closed` em callbacks assíncronos (try-except em splash e router)
- `OSError [10048]` port bind (documentação + instruções de taskkill)
- `Container must be added to page first` no Quiz (flag view_mounted)
- `Tab.__init__() unexpected keyword 'text'` (corrigido para `label=`)
- `Button.__init__() unexpected keyword 'text'` (corrigido para `content=`)
- `ERR_ADDRESS_INVALID` ao iniciar navegador (host 127.0.0.1 + FLET_SERVER_IP 0.0.0.0)
- Toggle claro/escuro sem efeito instantâneo (reconstrução in-place da view)
- Autoplay bloqueado pelo Chrome/Edge (silent.wav mudo no init)
- `min_height=` removido do Flet 0.85 (substituído por padding)

### Known Issues
- Persistência em memória — progresso se perde ao reiniciar
- Unidades 02 e 03 são placeholders (sem dados JSON)
- Layout não otimizado para telas < 360px
- Sem testes E2E de interface
- Tab "Diálogo" ausente na lesson_view
