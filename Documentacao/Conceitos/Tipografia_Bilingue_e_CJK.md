# Tipografia Bilíngue e Cobertura CJK (Hangul + Latim)

**Conceito Relacionado:** [[Design_System_e_Tokens_Semanticos]] | [[Neuropedagogia_e_Gamificacao]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[MANUAL_DE_IDENTIDADE_SAEBOM]] | [[DESIGN_SYSTEM_CHANGELOG]] | [[didactic_neuroscience_korean_ptbr]]  
**Bugs Catalogados:** [[bug_07_flutter_font_fallback_tofu_hangul]] | [[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]]  

---

## 1. 🔤 O Desafio da Tipografia Bilíngue (PT-BR ↔ Coreano)

O desenvolvimento de um aplicativo de aprendizagem de idiomas para falantes de Português Brasileiro (PT-BR) estudarem Coreano (*Hangul*) exige métricas tipográficas unificadas entre dois sistemas de escrita estruturalmente distintos.

Enquanto o alfabeto latino utiliza caracteres lineares proporcionais, o alfabeto coreano (*Hangul*) é um sistema **fonético-silábico organizado em blocos geométricos** (*Syllable Blocks*).

```text
   [ Alfabeto Latino ]                        [ Hangul Coreano ]
   L-i-n-e-a-r (26 letras)                    Blocos Silábicos (11.172 combinações)
   Exemplo: "S-a-e-b-o-m"                     Exemplo: 새 (ㅅ+ㅐ) 봄 (ㅂ+ㅗ+ㅁ)
   Faixa Unicode: U+0000 a U+00FF             Faixa CJK Hangul: U+AC00 a U+D7A3
```

---

## 2. 🏛️ Arquitetura Tipográfica Dual 100% Local no Saebom Companion (Brand Book v3.1)

Na **Rodada 4 (Brand Book v3.1)**, o **Saebom Companion (새봄 컴패니언)** consolidou uma estratégia dual **100% servida a partir de `assets/fonts/`** (sem dependências externas de CDN ou Google Fonts, garantindo compatibilidade offline, carregamento confiável no Flutter CanvasKit e conformidade com CSP estrita `font-src 'self' data:`):

```text
                       ┌─────────────────────────────────────────────────────────────┐
                       │         ARQUITETURA TIPOGRÁFICA DUAL 100% LOCAL             │
                       └──────────────┬──────────────────────────────┬───────────────┘
                                      │                              │
                                      ▼                              ▼
                       ┌──────────────────────────────┐ ┌──────────────────────────────┐
                       │  Pretendard (Interface UI)   │ │ Kyobo Handwriting 2025       │
                       │ - `Pretendard-Regular.otf`   │ │ - `KyoboHandwriting2025lyb`  │
                       │ - `Pretendard-Bold.otf`      │ │   (`.otf` / `.ttf`)          │
                       │ - Latim + Hangul sem Tofu    │ │ - Guias e avaliação Wongoji  │
                       └──────────────────────────────┘ └──────────────────────────────┘
```

### A. Pretendard (`assets/fonts/Pretendard-Regular.otf` e `Pretendard-Bold.otf`) — Fonte Global da UI
A família **Pretendard** foi projetada especificamente para alinhar métricas entre o alfabeto latino e os blocos silábicos Hangul:
- **Zero Glifos Tofu (`□□□□`):** Cobre integralmente caracteres latinos acentuados do Português e todo o bloco Hangul (`U+AC00`–`U+D7A3`).
- **Alinhamento de Baseline e Kerning:** Evita desalinhamentos verticais quando textos bilíngues (ex.: `"Nível 1A · 한국어 1A"`) dividem a mesma linha.
- **Múltiplos Pesos Locais:** O diretório `assets/fonts/` disponibiliza os 9 pesos estáticos em `.otf` (Thin a Black) além de `PretendardVariable.ttf`.

### B. Kyobo Handwriting 2025 (`assets/fonts/KyoboHandwriting2025lyb.otf`) — Caligrafia Coreana
A fonte manuscrita oficial **Kyobo Handwriting 2025** reproduz a proporção caligráfica natural de escrita manual coreana no **Wongoji Lab** (`CalligraphyWidget` e `WongojiMultiCellWidget`), sendo usada tanto no guia vetorial (`cv.Text`, escala `0.68`) quanto na rasterização de referência `48×48` do Pillow.

> [!NOTE]
> **Nota Histórica de Descontinuação (Rodadas 1–3):**
> - Nas Rodadas 1–3 anteriores ao Brand Book v3.1, o `src/theme.py` registrava URLs CSS externas do Google Fonts (`Noto Sans KR` e `Inter`) — ignoradas silenciosamente pelo Flutter Engine (que exige arquivos `.ttf`/`.otf` diretos) e bloqueadas por políticas restritivas de CSP. Essas URLs externas foram **removidas**; todas as fontes em runtime são locais em `assets/fonts/`.
> - A fonte local `establish_retrosans.ttf` (`Seollip-che`) segue armazenada em `assets/fonts/` apenas como recurso auxiliar de época; o logotipo e toda a identidade oficial do Brand Book v3.1 adotam **Pretendard** (`assets/branding/`).

---

## 3. 🚨 A Regra do Fallback no Flutter Engine (Evitando Glifos Tofu)

No motor Flutter (`CanvasKit` / `Skwasm`), os textos são rasterizados em Canvas sem fallback automático confiável para fontes do sistema operacional no ambiente Web:

1. **Causa do Glifo Tofu (`□□□□`):** Definir uma fonte exclusivamente latina (como `Inter` ou `Roboto`) como `font_family` padrão global faz com que caracteres na faixa Hangul (`U+AC00`–`U+D7A3`) sejam desenhados como retângulos vazios.
2. **Solução Definitiva:** Definir **`Pretendard`** (arquivo local `.otf` com cobertura Latim + CJK) como `font_family` padrão de `page.theme` e `page.dark_theme` em [`src/theme.py`](../../src/theme.py). Veja o diagnóstico completo em [[bug_07_flutter_font_fallback_tofu_hangul]].

---

## 4. 🛠️ Registro e Configuração de Fontes Locais no Flet (`src/theme.py`)

```python
# src/theme.py — Registro Local de Fontes (Sem Google Fonts CDN)

def apply_app_theme(page: ft.Page):
    from src import __version__

    page.title = f"Saebom Companion v{__version__}"
    page.fonts = {
        "Pretendard": "fonts/Pretendard-Regular.otf",
        "Pretendard-Bold": "fonts/Pretendard-Bold.otf",
        "Kyobo Handwriting": "fonts/KyoboHandwriting2025lyb.otf",
        "Seollip-che": "fonts/establish_retrosans.ttf",
        "establish Retrosans": "fonts/establish_retrosans.ttf",
    }

    page.theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,  # Violet #8B4DFF
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.dark_theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🏷️ Manual de Identidade Saebom: [[MANUAL_DE_IDENTIDADE_SAEBOM]]
- 🎨 Design System e Tokens: [[Design_System_e_Tokens_Semanticos]]
- ✍️ Caligrafia Hangul (Wongoji): [[Reconhecimento_Tatil_e_Caligrafia_Hangul]]
- 🚨 Bug dos Glifos Tofu: [[bug_07_flutter_font_fallback_tofu_hangul]]
