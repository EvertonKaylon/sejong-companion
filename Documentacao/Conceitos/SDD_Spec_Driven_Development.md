# SDD — Spec-Driven Development (Desenvolvimento Guiado por Especificações)

**Conceito Relacionado:** [[Design_System_e_Tokens_Semanticos]] | [[Arquitetura_Flet_e_Flutter_Engine]] | [[Desenvolvimento_Multiplataforma_Python]]  
**Documentos Vinculados:** [[MANUAL_DE_IDENTIDADE_SAEBOM]] | [[DESIGN_SYSTEM_CHANGELOG]] | [[Plano_UIUX_Flet_Sejong_Companion]] | [[implementation_plan]]  
**Bugs Catalogados:** [[bug_05_w_ampa_simulador_neuromorfico_e_performance]] | [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]]  

---

## 1. 💡 Fundamentação Teórica do Spec-Driven Development

O **Spec-Driven Development (SDD)** é uma disciplina de engenharia de software na qual componentes, regras de negócio e contratos visuais derivam estritamente de **especificações formais declarativas** (*Single Source of Truth - SSOT*).

No ecossistema do **Saebom Companion (새봄 컴패니언)**, o SDD elimina a estilização *ad-hoc* (cores arbitrárias, constantes mágicas espalhadas, recriação de sombras em loops e desvios entre documentação e código), conectando diretamente o **Brand Book v3.1** (`MANUAL_DE_IDENTIDADE_SAEBOM.md` e `DESIGN.md`) à implementação em Python/Flet e aos contratos Pydantic em `src/models.py`.

```text
┌─────────────────────────────────────────────────────────────┐
│              ESPECIFICAÇÃO DE MARCA E DESIGN                │
│         (Brand Book v3.1 · Hierarquia 60/20/12/8)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ Contrato Unificado (SSOT)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FONTE ÚNICA DE VERDADE (SSOT)               │
│          `src/theme.py` -> (Tokens, Colors, Styles)         │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     Componentes de UI        │  │   Views & Quiz Engine     │
│  (HangulCard, QuizWidget)    │  │  (src/views/*, models.py) │
└──────────────────────────────┘  └───────────────────────────┘
```

---

## 2. 🧱 Os Três Pilares do SDD no Saebom Companion

### Pilar A: Tokenização Rigorosa (Zero Magic Values)
Nenhum arquivo de visualização (`src/views/*.py`) ou componente (`src/components/*.py`) deve inventar cores HEX soltas (muito menos tokens legados descontinuados como `"#004C97"` ou `"#0356C5"`) nem instanciar `ft.BoxShadow` repetidamente dentro de loops (`BUG-05`). Toda estilização consome a camada de tokens em `src/theme.py`:

```python
# ❌ VIOLAÇÃO DO SDD (Estilo Ad-hoc e cor legada descontinuada)
card = ft.Container(
    bgcolor="#FFFFFF",
    border_radius=15,
    padding=20,
    border=ft.Border.all(1, "#004C97"),
)

# ✅ CONFORMIDADE COM SDD (Consumo de Tokens Únicos Brand Book v3.1)
card = ft.Container(
    bgcolor=colors["card_bg"],
    border_radius=Styles.BORDER_RADIUS_MD,
    padding=16,
    border=ft.Border.all(1, colors["border"]),
    shadow=Styles.CARD_SHADOW,
)
```

### Pilar B: Mapeamento Semântico de Papéis (Brand Book v3.1 — 60/20/12/8)
As cores representam **intenções funcionais e hierarquia cognitiva** definidas no Brand Book v3.1:
- `Colors.NAVY` / `Colors.DARK_BG` (`#02060F`): **Território (60%)** — fundo escuro silencioso para estudo sem fadiga ocular.
- `Colors.CREAM` / `Colors.LIGHT_BG` (`#F7F4EC`) e `Colors.SLATE` (`#9EA2AE`): **Superfície Clara & Estrutura (20%)** — leitura quente, bordas sutis e textos secundários.
- `Colors.PRIMARY` / `Colors.VIOLET` (`#8B4DFF`): **Sistema (12%)** — navegação, progresso, estados ativos e botões estruturais.
- `Colors.SECONDARY` / `Colors.LILAC` (`#B28AFF`): **Apoio** — companheirismo e destaques complementares.
- `Colors.ACCENT` / `Colors.GOLD` (`#FFAB22`): **Sinal (8%)** — conquistas, notificações, avisos docentes e CTAs primários.
- `Colors.CORRECT` (`#188150`) & `Colors.INCORRECT` (`#C50337`): Feedback estrito de acerto (WCAG AA 4.89:1) e erro.

> [!NOTE]
> **Nota Histórica de Descontinuação (Rodadas 1–3):** Os valores da fase inicial pré-rebranding (`#0356C5`, `#004C97`, `#268EF6`, `#F5A623`, além da paridade CSS Next.js da etapa exploratória) foram descontinuados na Rodada 4 (Brand Book v3.1) e preservados apenas para registro histórico em `DESIGN_SYSTEM_CHANGELOG.md`.

### Pilar C: Contratos Fail-Closed em Dados (`QuizQuestion`) e Tokens Estruturais
Além do sistema visual em `src/theme.py`, o SDD estende-se à camada de domínio em `src/models.py`: todo tipo de exercício (`multiple_choice`, `order_words`, `drag_and_drop_sov`, `calligraphy`) possui validadores `@model_validator(mode="after")` com postura **fail-closed**, rejeitando metadados ausentes antes de chegarem à UI.

| Papel no Brand Book v3.1 | Token Python (`src/theme.py`) | Valor Hexadecimal |
| :--- | :--- | :--- |
| Território Noturno (60%) | `Colors.NAVY` / `Colors.DARK_BG` | `#02060F` |
| Superfície Clara (10%) | `Colors.CREAM` / `Colors.LIGHT_BG` | `#F7F4EC` |
| Estrutura / Legenda (10%) | `Colors.SLATE` | `#9EA2AE` |
| Sistema / Primária (12%) | `Colors.PRIMARY` (`Colors.VIOLET`) | `#8B4DFF` |
| Apoio / Secundária | `Colors.SECONDARY` (`Colors.LILAC`) | `#B28AFF` |
| Sinal / Acento (8%) | `Colors.ACCENT` (`Colors.GOLD`) | `#FFAB22` |
| Sucesso / Erro | `Colors.CORRECT` / `Colors.INCORRECT` | `#188150` / `#C50337` |

---

## 3. 🔬 Impacto do SDD na Resolução de Bugs

### Estudo de Caso 1: Alocação de Memória em Renderização
- **Causa**: A reinstanciação direta de objetos `ft.BoxShadow(...)` dentro de loops/renders elevava a pressão de alocação de memória.
- **Resolução via SDD**: Uso obrigatório das constantes estáticas `Styles.CARD_SHADOW`, `Styles.SHADOW_SM`, `Styles.SHADOW_LG` e `Styles.HOVER_SHADOW` (`#598B4DFF`) centralizadas em `src/theme.py`.
- **Relatório Completo**: Veja [[bug_05_w_ampa_simulador_neuromorfico_e_performance]].

### Estudo de Caso 2: Inversão de Cores no Quiz (`#AARRGGBB`)
- **Causa**: Concatenação de sufixo alfa ao final de strings hex (`f"{Colors.CORRECT}15"`) fazia o Flutter Engine interpretar os dois primeiros dígitos como canal Alpha (`#AARRGGBB`), invertendo vermelho e verde.
- **Resolução via SDD**: Uso estrito de `ft.Colors.with_opacity(opacity, color)` em componentes dinâmicos e formato `#AARRGGBB` (`#26188150`, `#26C50337`) em constantes estáticas.
- **Relatório Completo**: Veja [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]].

---

## 4. 📐 Modelo de Implementação da Camada de Tokens (`src/theme.py`)

```python
# src/theme.py — Estrutura Real de Tokens SDD (Resumo)

import flet as ft


class Tokens:
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32


class Styles:
    BORDER_RADIUS_SM = 9
    BORDER_RADIUS_MD = 12
    BORDER_RADIUS_LG = 18
    BORDER_RADIUS_PILL = 999

    CARD_SHADOW = [
        ft.BoxShadow(
            spread_radius=-2,
            blur_radius=10,
            color="#141A1A1A",
            offset=ft.Offset(0, 4),
        ),
        ft.BoxShadow(
            spread_radius=-2,
            blur_radius=4,
            color="#0A1A1A1A",
            offset=ft.Offset(0, 2),
        ),
    ]

    HOVER_SHADOW = ft.BoxShadow(
        spread_radius=-4,
        blur_radius=20,
        color="#598B4DFF",
        offset=ft.Offset(0, 8),
    )
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🏷️ Manual de Identidade Saebom: [[MANUAL_DE_IDENTIDADE_SAEBOM]]
- 🎨 Design System e Tokens: [[Design_System_e_Tokens_Semanticos]]
- ⚙️ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
