# 🔍 Análise do Estado Atual — Sejong Companion v0.2.0-alpha

**Data:** 2026-08-11 | **Versão:** `0.2.0-alpha` | **Comparação com:** análise de 03/08 (v0.1.0-alpha)

---

## 🟢 Saúde do Código

| Indicador | Status |
|---|---|
| Testes unitários | ✅ **28/28 OK** (0 falhas, +8 novos) |
| Git funcional | ✅ **26 commits** com histórico completo |
| Versão SemVer | ✅ `__version__ = "0.2.0-alpha"` |
| App inicia | ✅ `main.py` executa, registra 6 rotas |
| Deploy cloud | ✅ Preparado para Render/HuggingFace (`ft.app`, `PORT` env) |

---

## 📈 Evolução: v0.1.0-alpha → v0.2.0-alpha

### Timeline de Desenvolvimento

**Sprint 1** (03-04/ago) — 23 commits em ~14h:
```
03/08 20:50  Initial commit v0.1.0-alpha
03/08 21:15  Release v0.2.0-alpha (neuroscience + SOV physics gating)
03/08 21:32  Batchim interativo com áudio
03/08 21:43  PWA responsive viewport + fullscreen toggle
03/08 22:10  Remove fullscreen button (iterated out)
03/08 22:17  Otimização mobile 384x715
03/08 22:32  Prep deploy cloud (Render/HuggingFace)
03/08 23:05  ft.app para deploy headless Linux
04/08 09:39  Fix Typecast key + layout áudio vocab
04/08 09:44  Security: API key via dotenv
04/08 09:52  Syllables blocks interativos com áudio
04/08 10:04  Gramática com cards rich Markdown
04/08 10:09  Ocultar UI Test Lab da Home
04/08 10:20  Quiz mobile-responsive refactor
04/08 10:31  Order_words estilo Duolingo
04/08 10:38  Remover spoilers de resposta coreana
04/08 10:42  Tela "Em Construção" para unidades futuras
04/08 10:55  Ganada + Números coreanos (1-10) na tab Sílabas
04/08 11:02  Anti-romanização rigorosa nos blocos Ganada
```

**Sprint 2** (11/ago) — 3 commits em ~30min:
```
11/08 20:52  Persistência atômica em disco (JSON)
11/08 21:06  Cadeia de desbloqueio data-driven + hardening de testes
11/08 21:12  Isolamento por sessão com UUID (multi-user web)
```

---

## 🆕 Features Novas (v0.2.0-alpha)

### 1. 💾 Persistência Real em Disco
**O maior avanço arquitetural.** O `ProgressService` foi completamente refatorado:

| Aspecto | v0.1.0-alpha | v0.2.0-alpha |
|---|---|---|
| **Storage** | Dicionário em memória (perdia ao reiniciar) | **JSON atômico em disco** (`data/sessions/*.json`) |
| **Multi-user** | Singleton compartilhado (todos veem o mesmo progresso) | **Isolamento por sessão UUID** (cada aba = progresso independente) |
| **Escrita** | Direta | **Atômica** (`.tmp` → `os.replace()`) — anticorrupção |
| **Desbloqueio** | Hardcoded com `if/elif` | **Data-driven** via `_UNLOCK_CHAIN` dict |
| **Reset** | Não existia | ✅ `reset_progress()` + `get_all_progress()` |
| **Testes** | 4 testes básicos | **10 testes** (isolamento, persistência, reset, cópia defensiva) |

### 2. 📱 Responsividade Mobile + PWA
- Layout otimizado para viewport **384×715** (Chrome Android)
- `page.padding = 0`, `page.spacing = 0`
- Meta viewport injetado via JS: `viewport-fit=cover`, `user-scalable=no`
- `apple-mobile-web-app-capable=yes` + `theme-color=#02060E`
- `FullscreenService` com toggle desktop + JS fallback web

### 3. ☁️ Deploy Cloud-Ready
- `ft.run()` → `ft.app()` (headless Linux, sem janela desktop)
- `PORT` via env var (Render/HuggingFace)
- `host="0.0.0.0"` para bind em container
- `gTTS` e `python-dotenv` adicionados ao requirements

### 4. 🎨 Cores Sintáticas SOV (Physics Gating)
Novas cores semânticas no Design System para papéis gramaticais:
- `ROLE_SUBJECT` → Azul (`#3B82F6`) — Sujeito
- `ROLE_OBJECT` → Verde Esmeralda (`#10B981`) — Objeto
- `ROLE_VERB` / `ROLE_PREDICATE` → Violeta (`#8B5CF6`)
- `ROLE_PARTICLE` → Âmbar (`#F59E0B`) — Partículas

### 5. 🔤 Conteúdo Hangul Expandido
- **Ganada sequence** (가나다라마바사아자차카타파하) na tab Sílabas
- **Números coreanos 1-10** com blocos interativos + áudio TTS
- Todos os syllable blocks são **botões clicáveis com áudio**
- Exemplos auditivos interativos no **guia de 받침**
- Anti-romanização rigorosa enforced nos blocos Ganada

### 6. 🎯 Quiz Mobile-Responsive
- Refactoring completo para layouts flexíveis (wrap, overflow)
- Chips `order_words` estilo **Duolingo** (tap-to-toggle, sem ícone X)
- Spoilers de resposta coreana removidos dos prompts
- Tela **"Em Construção" 🚧** para quizzes de unidades futuras

### 7. 📖 Gramática Rich Cards
- Seções de gramática reformatadas com **cards Markdown**
- Badges de regra interativos
- Exemplos com **botão de áudio TTS** integrado

### 8. 🔒 Segurança
- API key Typecast removida do código → carregada via `python-dotenv`
- `.env` no `.gitignore`

---

## 📊 Métricas Comparativas

| Métrica | v0.1.0-alpha (03/08) | v0.2.0-alpha (11/08) | Δ |
|---|---|---|---|
| **Commits git** | 0 (vazio) | **26** | +26 |
| **Testes unitários** | 20 | **28** | **+40%** |
| **Arquivos `.py` código** | 13 | 13 | = |
| **Linhas de código (views)** | ~1.015 | ~2.023 | **+99%** |
| **`services.py`** | 2.753 bytes | **9.848 bytes** | **+257%** |
| **`quiz_widget.py`** | 16.613 bytes | **17.424 bytes** | +5% |
| **`hangul_view.py`** | 13.337 bytes | **23.440 bytes** | **+76%** |
| **`lesson_view.py`** | 7.982 bytes | **13.388 bytes** | **+68%** |
| **`quiz_view.py`** | 9.292 bytes | **14.858 bytes** | **+60%** |
| **Dependências** | 4 | **6** (+gTTS, python-dotenv) | +2 |

---

## ✅ Problemas Anteriores Resolvidos

| Problema (03/08) | Status |
|---|---|
| ⚠️ Pasta duplicada `Documentacao/` vs `Documentação/` | ✅ **Resolvido** — apenas `Documentacao/` existe |
| ⚠️ `.git/` vazio | ✅ **Resolvido** — 26 commits com histórico limpo |
| ⚠️ 7+ arquivos soltos na raiz | ✅ **Resolvido** — raiz contém apenas 4 arquivos (`main.py`, `requirements.txt`, `.env`, `.gitignore`) |
| ⚠️ Fontes redundantes na raiz | ✅ **Resolvido** — removidas |
| ⚠️ Persistência em memória | ✅ **Resolvido** — JSON atômico em disco com isolamento por sessão |

---

## 🟡 Pontos de Atenção Restantes

1. **Unidades 02 e 03** — ainda são placeholders sem JSON de dados
2. **SRS (Repetição Espaçada)** — não implementado
3. **Tab Diálogos** — ausente na lesson_view
4. **Testes E2E** — sem automação de interface
5. **Versão** — o código está em `0.2.0-alpha` mas o `CHANGELOG.md` ainda documenta só a `0.1.0-alpha`
6. **`ft.app` vs `ft.run`** — `main.py` usa `ft.app` (modo headless para cloud), o que no Windows pode abrir diferente do `ft.run` com `WEB_BROWSER`

---

## 🎯 Resumo Executivo

O projeto deu um **salto significativo** em 8 dias com 26 commits em 2 sprints concentrados:

| Área | Progresso |
|---|---|
| 🏗️ Arquitetura | **Persistência real** com isolamento multi-user — a limitação #1 da v0.1.0-alpha foi resolvida |
| 📱 Mobile | Layout otimizado 384×715, viewport PWA, fullscreen service |
| ☁️ Infra | Deploy cloud-ready (Render/HuggingFace), `ft.app` headless, PORT via env |
| 🎨 Design | Cores sintáticas SOV, gramática rich cards, quiz Duolingo-style |
| 📝 Conteúdo | Ganada, números 1-10, batchim interativo, sílabas com áudio |
| 🔒 Segurança | API key via dotenv, .gitignore robusto |
| 🧹 Organização | Raiz limpa, git funcional, pastas consolidadas |
| ✅ Qualidade | 28 testes (+40%), 0 falhas |

O próximo passo natural é **atualizar o `CHANGELOG.md`** para documentar tudo que entrou na `0.2.0-alpha`, e depois planejar a `0.3.0-alpha` (Unidade 02, SRS, Diálogos).
