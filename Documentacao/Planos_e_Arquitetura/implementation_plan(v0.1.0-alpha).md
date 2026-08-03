# Plano de Implementação: Sejong Companion — v0.1.0-alpha (Fundação)

Este documento detalha o plano de implementação original da versão **`0.1.0-alpha`** do aplicativo **Sejong Companion**. Esta versão serviu como protótipo interativo para validar a experiência de uso, o design system e a viabilidade técnica de navegação e componentes no framework **Flet**.

> [!NOTE]
> Este documento é um registro histórico. O que era informalmente chamado de "Beta 0.1" corresponde, pela nomenclatura [SemVer](https://semver.org/lang/pt-BR/) adotada no projeto, à versão **`0.1.0-alpha`** — fase Alpha (software funcional mas incompleto, testado internamente). Consulte o [CHANGELOG.md](file:///c:/Users/Pichau/Documents/sejong_companion/CHANGELOG.md) para o histórico completo de versões.

## User Review Required

> [!IMPORTANT]
> **Decisões de Design e Escopo para a v0.1.0-alpha:**
> - **Cores e Identidade:** Paleta baseada no Sejong Hakdang, evoluída para o Design System portado de Next.js/shadcn/ui (Azul Real `#0356C5`, Vibrant Violet `#7C4DFF`, Dourado Sejong `#F5A623`) com suporte a tema claro e escuro.
> - **Fontes:** Fonte do Google Fonts `Noto Sans KR` (global, cobre Hangul + Latin) + `Inter` registrada para uso pontual.
> - **Dados do Protótipo:** Dados simulados locais para a **Unidade de Introdução (Hangul)** e a **Unidade 01 (Apresentação)**.
> - **Armazenamento de Progresso:** Progresso salvo em memória via `ProgressService` (dicionário simples — persistência real planejada para `0.2.0-alpha`).

## Open Questions

> [!NOTE]
> Não existem impedimentos críticos imediatos. O áudio foi integrado via **Typecast.ai** (primário) + **Google TTS** (fallback), com cache local atômico em disco.

---

## Proposed Changes

Abaixo está a estrutura modular implementada na v0.1.0-alpha:

```
sejong_companion/
├── requirements.txt                # flet==0.85.3, pydantic, requests, flet-audio
├── main.py                         # Entry point + versão impressa no terminal
├── .env                            # API key Typecast (local, gitignored)
├── CHANGELOG.md                    # Histórico de versões (SemVer)
├── data/
│   ├── curriculum.json             # Grade curricular (4 unidades)
│   └── units/
│       ├── unit_intro.json         # Hangul: vogais, consoantes, sílabas, batchim, quiz
│       └── unit_01.json            # Unidade 1: vocabulário, gramática, cultura, quiz
├── src/
│   ├── __init__.py                 # __version__ = "0.1.0-alpha"
│   ├── theme.py                    # Design System completo (escalas, sombras, tipografia)
│   ├── router.py                   # SPA router com tratativa de erros
│   ├── models.py                   # Schemas Pydantic (15 modelos)
│   ├── services.py                 # DataService + ProgressService (memória)
│   ├── audio_service.py            # TTS (Typecast→Google) + flet-audio/winsound
│   ├── components/
│   │   ├── hangul_card.py          # Card interativo flip + hover + áudio
│   │   ├── vocab_card.py           # Card de vocabulário + badges + neuro-tips
│   │   └── quiz_widget.py          # Quiz unificado (multiple_choice + order_words)
│   └── views/
│       ├── splash_view.py          # Splash animado + redirect assíncrono seguro
│       ├── home_view.py            # Dashboard + progresso + cronobiologia
│       ├── hangul_view.py          # Módulo Hangul (4 abas)
│       ├── lesson_view.py          # Fichas de estudo (Vocabulário/Gramática/Cultura)
│       └── quiz_view.py            # Motor de quiz + tela de resultados
├── tests/
│   ├── test_audio_service.py       # 9 testes
│   ├── test_data_service.py        # 3 testes
│   ├── test_progress_service.py    # 4 testes
│   └── test_router.py             # 4 testes (20 total)
└── DESIGN_SYSTEM_CHANGELOG.md      # Registro das decisões de design
```

---

### [Ambiente & Dependências]

#### [NEW] [requirements.txt](file:///c:/Users/Pichau/Documents/sejong_companion/requirements.txt)
- Declaração dos pacotes: `flet==0.85.3`, `pydantic>=2.0.0`, `requests>=2.34.2`, `flet-audio==0.85.3`.

---

### [Dados e Modelos]

#### [NEW] [curriculum.json](file:///c:/Users/Pichau/Documents/sejong_companion/data/curriculum.json)
- Lista de 4 unidades do curso com títulos, descrições e status de bloqueio.

#### [NEW] [unit_intro.json](file:///c:/Users/Pichau/Documents/sejong_companion/data/units/unit_intro.json)
- Dados estruturados sobre vogais, consoantes (planas, aspiradas, tensas), sílabas, guia de 받침 e quiz — sem romanização.

#### [NEW] [unit_01.json](file:///c:/Users/Pichau/Documents/sejong_companion/data/units/unit_01.json)
- Vocabulário com categorias e neuro-tips, gramática com dicas para lusófonos, notas culturais e quiz (multiple_choice + order_words).

#### [NEW] [models.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/models.py)
- 15 classes Pydantic para validação e tipagem dos dados (curriculum, hangul, vocab, grammar, quiz).

---

### [Lógica de Negócio e Serviços]

#### [NEW] [services.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/services.py)
- `DataService`: Carregador de dados dos JSONs via Pydantic.
- `ProgressService`: Gerenciador de progresso em memória com desbloqueio progressivo.

#### [NEW] [audio_service.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/audio_service.py)
- TTS offline-first com Typecast.ai (primário) + Google TTS (fallback).
- Cache atômico em disco, reprodução via flet-audio (web) ou winsound (desktop).
- Autoplay unlock para navegadores, validação de arquivo, timeout com tratativa graceful.

---

### [Design System & Interface]

#### [NEW] [theme.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/theme.py)
- Escalas de cor portadas de design system Next.js/shadcn/ui (50→950).
- Primária: Azul Real Sejong (`#0356C5`), Secundária: Vibrant Violet (`#7C4DFF`), Accent: Dourado (`#F5A623`).
- Sombras, border radius, tipografia (Noto Sans KR + Inter). Tema claro/escuro.

#### [NEW] [router.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/router.py)
- SPA router com registro de rotas, estado de unidade, fallback e tratativa de erros em `update()`/`go()`/`view_pop()`.

---

### [Componentes de UI Reutilizáveis]

#### [NEW] [hangul_card.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/hangul_card.py)
- Card com animação de flip (frente: caractere / verso: detalhes fonéticos + mnemônica). Hover com escala e brilho. Áudio TTS ao virar.

#### [NEW] [vocab_card.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/vocab_card.py)
- Card de vocabulário com badge de categoria, exemplos contextuais, neuro-tips e botão de áudio TTS.

#### [NEW] [quiz_widget.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/quiz_widget.py)
- Quiz unificado: multiple_choice (A/B/C/D com feedback visual) + order_words (chips interativos para treino SOV). Explicação pedagógica após resposta.

---

### [Telas (Views)]

#### [NEW] [splash_view.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/splash_view.py)
- Animação de entrada com logotipo 세종. Redirect assíncrono seguro com try-except.

#### [NEW] [home_view.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/home_view.py)
- Dashboard com grade curricular, anel de progresso, painel de cronobiologia adaptativo e toggle de tema instantâneo.

#### [NEW] [hangul_view.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/hangul_view.py)
- 4 abas: Vogais, Consoantes (planas + aspiradas + tensas), 받침 (guia + alerta "i fantasma"), Sílabas. Banners anti-romanização e escrita manual.

#### [NEW] [lesson_view.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/lesson_view.py)
- Abas de Vocabulário, Gramática e Cultura. Dicas para lusófonos (🇧🇷).

#### [NEW] [quiz_view.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/views/quiz_view.py)
- Motor de quiz com barra de progresso, tela de resultados (anel de %, placar, mensagens motivacionais) e botão "Refazer Desafio".

#### [NEW] [main.py](file:///c:/Users/Pichau/Documents/sejong_companion/main.py)
- Entry point que inicializa o app Flet, carrega fontes, registra rotas, inicializa AudioService e imprime a versão no terminal.

---

## Verification Plan

### Testes Automatizados (TDD)
```bash
python -m unittest discover -s tests -p "test_*.py"
# Resultado: 20 testes, 0 falhas ✅
```

### Testes Manuais de Execução
1. **Instalação das dependências:** `python -m pip install -r requirements.txt`
2. **Execução no Navegador:** `python main.py` → abre em `http://127.0.0.1:8554`
3. **Validação de Fluxos:**
   - Splash Screen redireciona para Home sem erros de sessão.
   - Módulo Hangul: flip dos cards revela detalhes fonéticos e dispara áudio TTS.
   - Quiz da Unidade 01: cálculo de acertos, order_words SOV, tela de resultados.
   - Toggle claro/escuro aplica instantaneamente sem necessidade de trocar de tela.
   - Interação com áudio não causa loop de reinício nem timeout fatal.
