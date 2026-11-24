# Design System e Tokens Semânticos

**Conceito Relacionado:** [[SDD_Spec_Driven_Development]] | [[Tipografia_Bilingue_e_CJK]] | [[Neuropedagogia_e_Gamificacao]]  
**Documentos Vinculados:** [[MANUAL_DE_IDENTIDADE_SAEBOM]] | [[DESIGN_SYSTEM_CHANGELOG]] | [[Plano_UIUX_Flet_Sejong_Companion]]  
**Bugs Catalogados:** [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]] | [[bug_05_w_ampa_simulador_neuromorfico_e_performance]]  

---

## 1. 🎨 Fundamentação Teórica do Design System

Um **Design System** é o conjunto consolidado de princípios visuais, guia de estilo, padrões de componentes e **Tokens Semânticos** que orientam o desenvolvimento de um produto digital.

No **Saebom Companion (새봄 컴패니언)**, a identidade cromática e semântica segue estritamente o **Brand Book v3.1** (proporção **60 / 20 / 12 / 8**), traduzido diretamente para a fonte única de verdade em [`src/theme.py`](../../src/theme.py).

> **Regra de Ouro Cromática (Brand Book v3.1):** *"Navy é território. Violet é sistema. Gold é sinal."*

---

## 2. 🌈 Arquitetura de Cores e Papéis Semânticos (Brand Book v3.1)

```text
                       ┌───────────────────────────────────────────────────────┐
                       │         HIERARQUIA CROMÁTICA 60 / 20 / 12 / 8         │
                       └───────────────────────────┬───────────────────────────┘
                                                   │
         ┌─────────────────┬──────────────────┬────┴─────────────┬─────────────────┐
         │                 │                  │                  │                 │
┌────────▼────────┐ ┌──────▼──────────┐ ┌─────▼──────────┐ ┌─────▼─────────┐ ┌─────▼──────────┐
│ Navy (#02060F)  │ │Cream/Slate (20%)│ │Violet (#8B4DFF)│ │Gold (#FFAB22) │ │Lilac (#B28AFF) │
│ Território 60%  │ │#F7F4EC / #9EA2AE│ │Sistema 12%     │ │Sinal 8%       │ │Apoio / Suave   │
│ Fundo Noturno   │ │Leitura/Estrutura│ │PRIMARY/Nav/Abas│ │ACCENT/CTAs    │ │SECONDARY       │
└─────────────────┘ └─────────────────┘ └────────────────┘ └───────────────┘ └────────────────┘
```

### Tabela Completa de Papéis Semânticos Vigentes (`src/theme.py`)

| Papel Semântico | Token Python | Hexadecimal | Proporção / Papel Funcional na Interface |
| :--- | :--- | :--- | :--- |
| **Midnight Navy** | `Colors.NAVY` / `Colors.DARK_BG` | `#02060F` | **60% — Território:** Fundo escuro silencioso para estudo focado sem fadiga ocular. |
| **Cream** | `Colors.CREAM` / `Colors.LIGHT_BG` | `#F7F4EC` | **10% — Superfície Clara:** Papel editorial de leitura quente no modo claro. |
| **Slate** | `Colors.SLATE` / `*_TEXT_SECONDARY` | `#9EA2AE` | **10% — Estrutura:** Textos secundários, legendas discretas e divisores sutis. |
| **Violet (Primary)** | `Colors.VIOLET` / `Colors.PRIMARY` | `#8B4DFF` | **12% — Sistema:** Navegação, progresso, estados ativos e botões estruturais. |
| **Lilac (Secondary)** | `Colors.LILAC` / `Colors.SECONDARY` | `#B28AFF` | **Apoio:** Presença suave, companheirismo e destaques complementares. |
| **Gold (Accent)** | `Colors.GOLD` / `Colors.ACCENT` | `#FFAB22` | **8% — Sinal:** Conquistas, medalhas, notificações, avisos docentes e CTAs primários. |
| **Correct** | `Colors.CORRECT` | `#188150` | **Acerto WCAG AA (4.89:1):** Alternativas corretas e conclusão de lições. |
| **Incorrect** | `Colors.INCORRECT` | `#C50337` | **Erro (`DESTRUCTIVE_500`):** Alternativa incorreta no quiz e alertas críticos. |

### Tokens Especializados (Neurociência & Sintaxe)
- **Papéis Sintáticos SOV:** `ROLE_SUBJECT` (`#3B82F6`), `ROLE_OBJECT` (`#10B981`), `ROLE_VERB`/`ROLE_PREDICATE` (`#8B5CF6`), `ROLE_PARTICLE` (`#F59E0B`).
- **Vitalidade SRS:** `VITALITY_HIGH` (`#10B981`), `VITALITY_MEDIUM` (`#F59E0B`), `VITALITY_LOW` (`#EF4444`), `VITALITY_NONE` (`#74717F`).
- **Tripartição Oclusiva:** `OCLUSIVE_LAX` (`#94A3B8`), `OCLUSIVE_ASPIRATED` (`#38BDF8`), `OCLUSIVE_TENSE` (`#EF4444`).
- **Conectores Metálicos:** `CONNECTOR_VOWEL` (`#B87333` cobre), `CONNECTOR_BATCHIM` (`#C0C0C0` prata).

> [!NOTE]
> **Nota Histórica de Descontinuação (Rodadas 1–3):** Os tokens legados `#004C97` (antigo Azul Sejong), `#0356C5` (Azul Real), `#268EF6`, `#8A1538`, `#F5A623` e fundos `#F5F5F5`/`#FAF9F6` foram formalmente **descontinuados** na Rodada 4 (Brand Book v3.1) e não devem ser reutilizados em código ou documentação vigente.

---

## 3. 🔬 Opacidade no Flutter Engine (`ft.Colors.with_opacity` e `#AARRGGBB`)

No **Flutter Engine**, cores hexadecimais de 8 dígitos colocam o **canal Alpha nos dois primeiros dígitos (`#AARRGGBB`)**, ao contrário do CSS tradicional (`#RRGGBBAA`).

$$\text{Valor Hexadecimal} = \underbrace{\text{AA}}_{\text{Alpha (Opacidade)}} \underbrace{\text{RR}}_{\text{Vermelho}} \underbrace{\text{GG}}_{\text{Verde}} \underbrace{\text{BB}}_{\text{Azul}}$$

### Regra Canônica de Código
- **Em views e componentes dinâmicos:** **NUNCA** concatenar sufixo hex ao final de uma string (ex.: `f"{colors['primary']}12"` inverte canais ou corrompe a cor). Utilizar **sempre** `ft.Colors.with_opacity(opacity, color)`.
- **Em constantes estáticas de `Styles` (`src/theme.py`):** Literais de 8 dígitos devem obedecer estritamente ao formato `#AARRGGBB`, como:
  - `Styles.HOVER_SHADOW`: `#598B4DFF` (35% de opacidade sobre Violet `#8B4DFF`)
  - `Styles.CARD_SHADOW`: `#141A1A1A` e `#0A1A1A1A`
  - Referência rápida `#AARRGGBB`: `10%` → `1A`, `15%` → `26`, `20%` → `33`, `35%` → `59`, `50%` → `80` (ex.: `#26188150` para verde 15%, `#26C50337` para carmesim 15%).

Veja o histórico técnico em [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]].

---

## 4. 📐 Implementação dos Tokens e Temas (`src/theme.py`)

```python
# src/theme.py — Paleta Oficial Brand Book v3.1

class Colors:
    # Cores Mestras Saebom (60/20/12/8)
    NAVY = "#02060F"     # Midnight Navy — Território (60%)
    VIOLET = "#8B4DFF"   # Violet — Sistema (12%)
    GOLD = "#FFAB22"     # Gold — Sinal (8%)
    LILAC = "#B28AFF"    # Lilac — Apoio
    CREAM = "#F7F4EC"    # Cream — Superfície Clara (10%)
    SLATE = "#9EA2AE"    # Slate — Estrutura e Linhas (10%)

    # Papéis Semânticos Oficiais
    PRIMARY = VIOLET
    SECONDARY = LILAC
    ACCENT = GOLD

    # Tema Claro (Cream & Slate) e Tema Escuro (Midnight Navy)
    LIGHT_BG = CREAM
    DARK_BG = NAVY
    CORRECT = "#188150"
    INCORRECT = "#C50337"


def get_theme_colors(is_dark: bool):
    return {
        "bg": Colors.DARK_BG if is_dark else Colors.LIGHT_BG,
        "surface": "#091122" if is_dark else "#FFFFFF",
        "text": "#FAFAFA" if is_dark else Colors.NAVY,
        "text_sec": Colors.SLATE,
        "border": "#1E293B" if is_dark else "#E7E7E9",
        "card_bg": "#0B172E" if is_dark else "#FFFFFF",
        "primary": Colors.PRIMARY,
        "secondary": Colors.SECONDARY,
        "accent": Colors.ACCENT,
        "correct": Colors.CORRECT,
        "incorrect": Colors.INCORRECT,
        "navy": Colors.NAVY,
        "violet": Colors.VIOLET,
        "gold": Colors.GOLD,
        "lilac": Colors.LILAC,
        "cream": Colors.CREAM,
        "slate": Colors.SLATE,
    }
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🏷️ Manual de Identidade Saebom: [[MANUAL_DE_IDENTIDADE_SAEBOM]]
- 📐 Metodologia SDD: [[SDD_Spec_Driven_Development]]
- 🔤 Tipografia Bilíngue: [[Tipografia_Bilingue_e_CJK]]
- 🚨 Bug do Parser HEX: [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]]
