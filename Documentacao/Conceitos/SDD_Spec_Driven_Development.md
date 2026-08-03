# SDD — Spec-Driven Development (Desenvolvimento Guiado por Especificações)

**Conceito Relacionado:** [[Design_System_e_Tokens_Semanticos]] | [[Arquitetura_Flet_e_Flutter_Engine]] | [[Desenvolvimento_Multiplataforma_Python]]  
**Documentos Vinculados:** [[Plano_UIUX_Flet_Sejong_Companion]] | [[implementation_plan]] | [[DESIGN_SYSTEM_CHANGELOG]]  
**Bugs Catalogados:** [[bug_05_w_ampa_simulador_neuromorfico_e_performance]] | [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]]  

---

## 1. 💡 Fundamentação Teórica do Spec-Driven Development

O **Spec-Driven Development (SDD)** é uma disciplina de engenharia de software na qual o desenvolvimento de componentes, lógica de negócios e contratos visuais é derivado estritamente de um conjunto de **especificações formais declarativas** (*Single Source of Truth - SSOT*).

No ecossistema do **Sejong Companion (세종학당 컴패니언)**, o SDD foi adotado para solucionar um dos maiores problemas de projetos de interface rica: o **estilo ad-hoc** (uso de cores arbitrárias, raios de borda desconexos e constantes mágicas espalhadas pelo código).

```
┌─────────────────────────────────────────────────────────────┐
│              ESPECIFICAÇÃO DE MARCA E DESIGN                │
│       (Brand Book Next.js + Tailwind v4 + shadcn/ui)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               │ Portabilidade Tokenizada (1:1)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 FONTE ÚNICA DE VERDADE (SSOT)               │
│          `src/theme.py` -> (Tokens, Colors, Styles)         │
└──────────────┬──────────────────────────────┬───────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────────┐  ┌───────────────────────────┐
│     Componentes de UI        │  │   Máquinas de Estado      │
│  (quiz_card, audio_button)   │  │   (quiz_view, home_view)  │
└──────────────────────────────┘  └───────────────────────────┘
```

---

## 2. 🧱 Os Três Pilares do SDD no Sejong Companion

### Pilar A: Tokenização Rigorosa (Zero Magic Values)
Nenhum arquivo de visualização (`src/views/*.py`) ou componente (`src/components/*.py`) tem permissão para definir cores HEX brutas (ex: `"#0356C5"` ou `ft.Colors.PURPLE_500`) ou espaçamentos arbitrários. Tudo deve ser consumido através da camada de abstração de tokens:

```python
# ❌ VIOLAÇÃO DO SDD (Estilo Ad-hoc, Frágil e Difícil de Manter)
card = ft.Container(
    bgcolor="#FFFFFF",
    border_radius=15,
    padding=20,
    border=ft.Border.all(1, "#E7E7E9")
)

# ✅ CONFORMIDADE COM SDD (Consumo de Tokens Únicos)
card = ft.Container(
    bgcolor=colors["card_bg"],
    border_radius=Styles.BORDER_RADIUS_MD,
    padding=Tokens.SPACE_MD,
    border=ft.Border.all(1, colors["border"])
)
```

### Pilar B: Mapeamento Semântico de Papéis (Role-Based Design)
As cores não representam apenas pigmentos; representam **intenções da interface**:
- `Colors.PRIMARY`: Estrutura institucional do Instituto Sejong (Azul Real `#0356C5`).
- `Colors.SECONDARY`: Elementos interativos de destaque e áudio TTS (Violeta `#7C3AED`).
- `Colors.ACCENT`: Dicas mnemônicas e cultura (Dourado `#F5A623`).
- `Colors.INCORRECT`: Feedback estrito de erro no quiz (Carmesim `#C50337`).

### Pilar C: Portabilidade Cross-Framework (Next.js ↔ Flet)
Como o projeto possui um livro de marca desenvolvido em **Next.js + Tailwind v4 + shadcn/ui**, as variáveis CSS de `app/globals.css` foram traduzidas em tabelas numéricas de equivalência no Python:

| Variável CSS (Next.js) | Token Python (`src/theme.py`) | Valor Hexadecimal |
| :--- | :--- | :--- |
| `--primary` | `Colors.PRIMARY` / `INFO_500` | `#0356C5` |
| `--secondary` | `Colors.SECONDARY` / `PRIMARY_500` | `#7C3AED` |
| `--accent` | `Colors.ACCENT` | `#F5A623` |
| `--destructive` | `Colors.INCORRECT` / `DESTRUCTIVE_500` | `#C50337` |
| `--bg-dark` | `Colors.DARK_BG` / `NEUTRAL_950` | `#02060E` |

---

## 3. 🔬 Impacto do SDD na Resolução de Bugs

### Estudo de Caso 1: Estouro de Memória no Simulador Neuromórfico
- **Causa**: O descumprimento do SDD no módulo de cronobiologia/simulador provocou a reinstanciação direta de objetos `ft.BoxShadow(blur_radius=10, ...)` em cada chamada de `update()`.
- **Resolução via SDD**: A especificação formal congelou a constante estática `Styles.CARD_SHADOW` e `Styles.HOVER_SHADOW`. A alocação foi reduzida a zero alocações secundárias por frame, estabilizando o uso de RAM no Intel Core i7-3770.
- **Relatório Completo**: Veja [[bug_05_w_ampa_simulador_neuromorfico_e_performance]].

### Estudo de Caso 2: Inversão de Cores no Quiz
- **Causa**: O uso de concatenação de strings fora da especificação do parser do Flutter Engine (`f"{Colors.CORRECT}15"`) fez o motor ler a opacidade no início (`#AARRGGBB`), trocando os canais vermelho e verde.
- **Resolução via SDD**: O contrato de cores foi corrigido especificando os tokens de transparência `#2619BD56` (Verde 15%) e `#26C50337` (Carmesim 15%).
- **Relatório Completo**: Veja [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]].

---

## 4. 📐 Modelo de Implementação da Camada de Tokens

```python
# src/theme.py — Estrutura de Arquitetura de Tokens SDD

import flet as ft

class Tokens:
    # Espaçamentos em escala modular de 8pt
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32

    # Durações Padrão de Animação (ms)
    DUR_FAST = 150
    DUR_BASE = 250
    DUR_SLOW = 400

class Styles:
    BORDER_RADIUS_SM = 9
    BORDER_RADIUS_MD = 12
    BORDER_RADIUS_LG = 18
    BORDER_RADIUS_PILL = 999

    CARD_SHADOW = [
        ft.BoxShadow(
            spread_radius=-2,
            blur_radius=10,
            color="rgba(26, 26, 26, 0.08)",
            offset=ft.Offset(0, 4),
        )
    ]
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🎨 Design System e Tokens: [[Design_System_e_Tokens_Semanticos]]
- ⚙️ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
- 📋 Plano de UI/UX: [[Plano_UIUX_Flet_Sejong_Companion]]
