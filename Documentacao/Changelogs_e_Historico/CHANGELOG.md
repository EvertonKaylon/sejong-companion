# Changelog — Sejong Companion

Todas as mudanças notáveis do projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## Ciclo de Vida do Projeto

```
Pré-Alpha → Alpha → Beta → RC → RTM → GA
               ▲
          ESTAMOS AQUI
          v0.3.0-alpha
```

| Fase | Versão Alvo | Critérios de Entrada |
|------|-------------|----------------------|
| **Alpha** (atual) | `0.3.0-alpha` | Todas as unidades do Sejong 1A integradas, HLR SRS, Lab Fonético, Drag & Drop SOV |
| **Beta** | `0.1.0-beta` | Todas as unidades do Livro 1A implementadas, persistência real, responsivo mobile, modo offline |
| **RC** | `1.0.0-rc.1` | Feature-complete, testes E2E, zero bugs críticos |
| **GA** | `1.0.0` | Pronto para distribuição pública |

---

## [0.3.0-alpha] — 2026-08-14

### Classificação: Alpha
> Milestone de Conteúdo & Inteligência de Memória: Currículo completo do Sejong Korean 1A (Unidades 01 a 10), Algoritmo HLR de Ebbinghaus, Laboratório Fonético Oclusivo e Mecânica Drag & Drop SOV.

### Added — Features
- **Currículo Sejong 1A Completo (10 Unidades)** — Criadas as unidades didáticas `unit_02.json` até `unit_10.json` com vocabulário, gramática formatada em Markdown, dicas lusófonas e exercícios interativos.
- **Política Estrita Zero Romanização** — Todo o conteúdo coreano padronizado exclusivamente em 한글, eliminando muletas de romanização.
- **Motor Matemático HLR SRS (Half-Life Regression de Ebbinghaus)** — Retenção calculada via $R = 2^{-t / h}$, com recálculo dinâmico de meia-vida no Active Recall com base em acurácia e tempo de resposta.
- **Orbes de Vitalidade SRS na Home** — Indicadores visuais nos cartões de unidade para memorização Alta ($\ge 75\%$), Média ($35\%-75\%$) e Baixa/Urgente ($< 35\%$).
- **Cadeia de Desbloqueio Progressivo de 10 Unidades** — Expansão do fluxo didático contínuo de `unit_intro` até `unit_10` com persistência atômica.
- **Laboratório Fonético Oclusivo** — Componente `oclusive_lab.py` na aba de Consoantes para as 4 tríades (ㄱ/ㅋ/ㄲ, ㄷ/ㅌ/ㄸ, ㅂ/ㅍ/ㅃ, ㅈ/ㅊ/ㅉ) com feedback visual por cor e pronúncia em áudio HD.
- **Mecânica Drag & Drop SOV com Rejeição Elástica** — Exercícios de sintaxe com `ft.Draggable` e `ft.DragTarget` em slots magnéticos de Sujeito (S), Objeto (O) e Verbo (V), com animação elástica de rejeição (*shake* + realce carmesim).
- **Padronização de Layout Dead-Center** — Componente `centered_content` garantindo alinhamento central absoluto em telas widescreen e ultra-wide.

### Added — Suíte de Testes
- **41 Testes Unitários (100% OK)** — Cobertura ampliada para carregamento dinâmico de 10 unidades (`test_data_service.py`), estabilidade/decaimento HLR, vitalidade e cadeia de desbloqueio (`test_progress_service.py`).

---

## [0.2.0-alpha] — 2026-08-11

### Classificação: Alpha
> Milestone de Arquitetura & Isolamento Multi-Sessão: Persistência atômica por sessão, neuro-dicas de cronobiologia e modo Fullscreen/PWA.

### Added — Features
- **Isolamento de Sessão Web / Multi-User** — Cada aba/conexão do navegador recebe um UUID próprio (`data/sessions/{uuid}.json`), evitando conflito de progresso entre usuários simultâneos.
- **Cronobiologia Adaptativa (Neuro-Tips)** — Card dinâmico na Home com recomendações de estudo personalizadas de acordo com o horário do dia (manhã, tarde, noite).
- **Serviço de Tela Cheia (FullscreenService)** — Suporte a alternância de tela cheia via Flet e injeção de viewport mobile/PWA para Web.
- **Tokens Semânticos de Papel Sintático** — Cores dedicadas para Sujeito (`#3B82F6`), Objeto (`#10B981`), Verbo (`#8B5CF6`) e Partícula (`#F59E0B`).

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
- **Persistência Real em Disco** — `ProgressService` com gravação atômica em `data/user_progress.json`, mantendo o progresso e desbloqueio curricular mesmo após reinicialização do app/servidor
- **Pedagogia Neuro-Linguística** — Anti-romanização, alerta "i fantasma" (epêntese lusófona), dicas mnemônicas, neuro-tips por vocabulário
- **Suíte TDD** — 25 testes unitários (audio, data, progress com persistência, router) com mocks Flet

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
- Perda de progresso ao reiniciar o app/servidor (migrado de memória pura para persistência atômica em disco)

### Known Issues
- Unidades 02 e 03 são placeholders (sem dados JSON didáticos completos)
- Layout não otimizado para telas ultra-estreitas (< 360px)
- Sem testes E2E automatizados de interface gráfica
- Tab "Diálogo" ausente na lesson_view
