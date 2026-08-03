# Design System e Tokens Semânticos

**Conceito Relacionado:** [[SDD_Spec_Driven_Development]] | [[Tipografia_Bilingue_e_CJK]] | [[Neuropedagogia_e_Gamificacao]]  
**Documentos Vinculados:** [[Plano_UIUX_Flet_Sejong_Companion]] | [[DESIGN_SYSTEM_CHANGELOG]]  
**Bugs Catalogados:** [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]] | [[bug_05_w_ampa_simulador_neuromorfico_e_performance]]  

---

## 1. 🎨 Fundamentação Teórica do Design System

Um **Design System** é o conjunto consolidado de princípios visuais, guia de estilo, padrões de componentes e **Tokens Semânticos** que orientam o desenvolvimento de um produto digital.

No **Sejong Companion (세종학당 컴패니언)**, o sistema de design atua como a linguagem visual única entre a equipe pedagógica do Centro Cultural Coreano no Brasil (CCCB), o protótipo web em Next.js/Tailwind v4 e a aplicação nativa em Flet (Python).

---

## 2. 🌈 Arquitetura de Cores e Papéis Semânticos

A paleta de cores do Sejong Companion foi desenhada seguindo a especificação do **Material Design 3**, dividindo os pigmentos em **papéis funcionais e semânticos**:

```
                       ┌──────────────────────────────────────────────┐
                       │          PALETA SEMÂNTICA MESTRE             │
                       └──────────────────────┬───────────────────────┘
                                              │
         ┌──────────────────┬─────────────────┼──────────────────┬──────────────────┐
         │                  │                 │                  │                  │
┌────────▼─────────┐ ┌──────▼──────────┐ ┌────▼─────────────┐ ┌──▼──────────────┐ ┌─▼──────────────┐
│ Primary (#004C97)│ │Secondary(#268EF6)│ │ Accent (#F5A623)│ │Incorrect(#C50337)│ │Correct (#188150)│
│ Azul Oficial KSI │ │ Azul Claro (Ação)│ │ Dourado Cultural│ │ Carmesim Erro    │ │ Verde Sucesso   │
│ (Estrutura/Abas) │ │ (Mídia/TTS/Audio)│ │ (Dicas/Dancheong)│ │ (Estrito Quiz)   │ │ (Estrito Acerto)│
└──────────────────┘ └──────────────────┘ └─────────────────┘ └──────────────────┘ └─────────────────┘
```

### Tabela Completa de Papéis Semânticos de Cor

| Papel Semântico | Token Python | Hexadecimal | Papel Funcional na Interface |
| :--- | :--- | :--- | :--- |
| **Primary** | `Colors.PRIMARY` | `#004C97` | Azul oficial do 세종학당재단 (Pantone 2945 C, confirmado no CI/BI oficial em ksif.or.kr). Usado em cabeçalhos, abas, navegadores e estrutura oficial. **Não é mais `#0356C5`** — esse valor vinha de uma referência de mood board, não do CI real; ele agora vive só como acento do modo escuro (ver `Colors.PRIMARY_DARK_MODE`). |
| **Secondary** | `Colors.SECONDARY` | `#268EF6` | Variação tonal mais clara do mesmo azul oficial. Usado em botões de escuta TTS, anel de progresso e ações interativas de destaque. **O roxo/violeta (`#7C3AED`/`#7C4DFF`) saiu do sistema** — ver Rodada 3 do `DESIGN_SYSTEM_CHANGELOG.md`. |
| **Brand Crimson** | `Colors.BRAND_CRIMSON` | `#8A1538` | Carmesim oficial (Pantone 1955 C). Reservado à **identidade institucional** (splash, tela "sobre", certificados) — nunca à UI interativa comum, para não competir com o Carmesim de erro do quiz. |
| **Accent** | `Colors.ACCENT` | `#F5A623` | Dourado Nobre. Inspiração nas pinturas tradicionais Dancheong (단청) e no 황 (amarelo) do Obangsaek (오방색) — o esquema tradicional coreano de 5 cores, do qual o azul e o carmesim oficiais já cobrem 청 e 적. Usado em badges, dicas mnemônicas e destaque no dark mode. |
| **Incorrect** | `Colors.INCORRECT` | `#C50337` | Carmesim de Erro. Reservado exclusivamente para a alternativa errada no quiz e alertas, evitando poluição cognitiva. Deliberadamente diferente do Brand Crimson institucional (ver acima). |
| **Correct** | `Colors.CORRECT` | `#188150` | Verde Sucesso. Reservado para alternativas corretas e conclusão de lições. Ajustado de `#19BD56` para `#188150` — o tom antigo tinha só 3.95:1 de contraste sobre branco (abaixo do mínimo WCAG AA de 4.5:1); o novo tem 4.89:1. |
| **Dark Background** | `Colors.DARK_BG` | `#02060E` | Midnight Blue profundo (referência de paleta @rarostock). Fundo noturno que harmoniza com o Azul Oficial sem gerar contraste agressivo aos olhos. |
| **Light Background** | `Colors.LIGHT_BG` | `#F5F5F5` | ⚠️ pendência conhecida: este documento descreve um "Warm Off-White `#FAF9F6`" abaixo, mas `theme.py` usa `NEUTRAL_100` (`#F5F5F5`) — nunca foi implementado. Sinalizando para reconciliar (fora do escopo desta rodada). |
| **Light Background** | `Colors.LIGHT_BG` | `#FAF9F6` | Warm Off-White (papel natural). Evita o branco puro `#FFFFFF` estéril, simulando a textura visual de um livro didático. |

---

## 3. 🔬 A Regra Hexadecimal de Opacidade `#AARRGGBB` no Flutter

Uma das descobertas mais importantes no desenvolvimento do aplicativo envolve o parser interno de cores do **Flutter Engine** (utilizado pelo Flet):

### O Problema do Formato Hexadecimal de 8 Dígitos
Diferente do CSS tradicional (onde a opacidade é colocada no final `#RRGGBBAA`), o Flutter Engine interpreta os 8 dígitos Hexadecimais com a **opacidade Alpha nos dois primeiros dígitos**: **`#AARRGGBB`**.

$$\text{Valor Hexadecimal} = \underbrace{\text{AA}}_{\text{Alpha (Opacidade)}} \underbrace{\text{RR}}_{\text{Vermelho}} \underbrace{\text{GG}}_{\text{Verde}} \underbrace{\text{BB}}_{\text{Azul}}$$

### Tabela de Conversão de Opacidade para Hexadecimal (Alpha)
- **10% Opacidade**: $0.10 \times 255 = 25.5 \approx \mathbf{19}$ (Hexadecimal `19`)
- **15% Opacidade**: $0.15 \times 255 = 38.25 \approx \mathbf{26}$ (Hexadecimal `26`)
- **20% Opacidade**: $0.20 \times 255 = 51 \approx \mathbf{33}$ (Hexadecimal `33`)
- **50% Opacidade**: $0.50 \times 255 = 127.5 \approx \mathbf{80}$ (Hexadecimal `80`)

### Aplicação nos Cards de Quiz:
- **Fundo Verde Sucesso (15% opacidade)**: `#26188150` (`AA=26`, `RR=18`, `GG=81`, `BB=50`)
- **Fundo Carmesim Erro (15% opacidade)**: `#26C50337` (`AA=26`, `RR=C5`, `GG=03`, `BB=37`)
- **Fundo Azul Selecionado (10% opacidade)**: `#1A004C97` (`AA=1A`, `RR=00`, `GG=4C`, `BB=97`)

> **Histórico do Bug**: Escrever `f"{Colors.CORRECT}15"` gerava `#19BD5615` (com o tom antigo `#19BD56`). O Flutter lia `AA=19` (10% opacidade) e `RR=BD` (Vermelho=189), transformando o verde em vermelho castanho! Veja [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]]. **Atualização (Rodada 3/4)**: essa mesma inversão foi encontrada em outros 8 arquivos do projeto que ainda usavam `rgba(r, g, b, decimal)` como string — todos convertidos para `#AARRGGBB` nesta rodada.

---

## 4. 📐 Implementação dos Tokens e Temas (`src/theme.py`)

```python
# src/theme.py — Estrutura de Definição do Design System

import flet as ft

class Colors:
    # Escalas Primárias — ancoradas nas cores oficiais do 세종학당재단
    # (Pantone 2945 C / 1955 C, confirmadas em ksif.or.kr)
    PRIMARY = "#004C97"       # Azul Oficial (era "#0356C5", de mood board)
    PRIMARY_LIGHT = "#268EF6"
    PRIMARY_DARK = "#022549"

    SECONDARY = "#268EF6"     # Variação clara do azul — era "#7C3AED" (roxo, retirado)
    SECONDARY_LIGHT = "#7DB7F1"

    BRAND_CRIMSON = "#8A1538"  # Carmesim oficial — só identidade institucional
    ACCENT = "#F5A623"        # Dourado Cultural

    # Estados Semânticos
    CORRECT = "#188150"       # era "#19BD56" (contraste insuficiente: 3.95:1 < 4.5:1 WCAG AA)
    INCORRECT = "#C50337"

    # Fundo e Superfícies
    LIGHT_BG = "#F5F5F5"      # ver nota de pendência acima ("Warm Off-White" ainda não implementado
    DARK_BG = "#02060E"       # Midnight Blue
    DARK_SURFACE = "#091223"
    DARK_CARD_BG = "#091223"

def get_theme_colors(is_dark: bool):
    return {
        "bg": Colors.DARK_BG if is_dark else Colors.LIGHT_BG,
        "surface": Colors.DARK_SURFACE if is_dark else "#FFFFFF",
        "text": "#FAFAFA" if is_dark else "#1A1A1A",
        "text_sec": "#A19EA9" if is_dark else "#74717F",
        "border": "#1E293B" if is_dark else "#E2E8F0",
        "card_bg": Colors.DARK_CARD_BG if is_dark else "#FFFFFF",
        "primary": Colors.PRIMARY,
        "secondary": Colors.SECONDARY,
        "accent": Colors.ACCENT,
        "correct": Colors.CORRECT,
        "incorrect": Colors.INCORRECT,
    }
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 📐 Metodologia SDD: [[SDD_Spec_Driven_Development]]
- 🔤 Tipografia Bilíngue: [[Tipografia_Bilingue_e_CJK]]
- 🚨 Bug do Parser HEX: [[bug_03_inversao_hex_alpha_aarrggbb_flet_flutter]]
