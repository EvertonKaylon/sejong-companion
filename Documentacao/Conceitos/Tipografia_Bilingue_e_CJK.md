# Tipografia Bilíngue e Cobertura CJK (Hangul + Latim)

**Conceito Relacionado:** [[Design_System_e_Tokens_Semanticos]] | [[Neuropedagogia_e_Gamificacao]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[Plano_UIUX_Flet_Sejong_Companion]] | [[didactic_neuroscience_korean_ptbr]]  
**Bugs Catalogados:** [[bug_07_flutter_font_fallback_tofu_hangul]] | [[bug_02_sintaxe_flet_085_letter_spacing_e_button_args]]  

---

## 1. 🔤 O Desafio da Tipografia Bilíngue (PT-BR ↔ Coreano)

O desenvolvimento de um aplicativo de aprendizagem de idiomas para falantes de Português Brasileiro (PT-BR) estudarem Coreano (*Hangul*) apresenta desafios tipográficos únicos.

Enquanto o alfabeto latino é composto por caracteres lineares e espaçamento proporcional simples, o alfabeto coreano (*Hangul*) é um sistema **fonético-silábico organizado em blocos geométricos** (*Syllable Blocks*).

```
   [ Alfabeto Latino ]                        [ Hangul Coreano ]
   L-i-n-e-a-r (26 letras)                    Blocos Silábicos (11.172 combinações)
   Exemplo: "S-e-j-o-n-g"                     Exemplo: 세 (ㅅ+ㅔ) 종 (ㅈ+ㅗ+ㅇ)
   Faixa Unicode: U+0000 a U+00FF             Faixa CJK Hangul: U+AC00 a U+D7A3
```

---

## 2. 🏛️ Estratégia Dual de Fontes no Sejong Companion

Para equilibrar o desempenho do aplicativo, garantir a ausência de falhas visuais e preservar a identidade visual da marca, foi implementado um **padrão dual de fontes**:

```
                       ┌─────────────────────────────────────────────────────────────┐
                       │              ARQUITETURA TIPOGRÁFICA DUAL                   │
                       └──────────────┬──────────────────────────────┬───────────────┘
                                      │                              │
                                      ▼                              ▼
                       ┌──────────────────────────────┐ ┌──────────────────────────────┐
                       │  Pretendard (Fonte Global)   │ │ 설립체 / Seollip-che (Marca)  │
                       │ - `PretendardVariable.ttf`   │ │ - `establish Retrosans.ttf`  │
                       │ - Interface geral, lições    │ │ - Exclusivo para o Logotipo  │
                       │ - Zero glifos Tofu (□□□□)    │ │ - Estilo retrô-industrial    │
                       └──────────────────────────────┘ └──────────────────────────────┘
```

### A. Pretendard (`PretendardVariable.ttf`) — A Fonte Global da UI
O **Pretendard** é uma família de fontes moderna desenvolvida especificamente para resolver os problemas de alinhamento entre o alfabeto latino e os caracteres Hangul em interfaces de usuário na Coreia do Sul (utilizada por grandes apps como Toss).

- **Vantagem de Fonte Variável**: Contém uma única instância de arquivo (`PretendardVariable.ttf`) que suporta todas as espessuras (*Thin 100, Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, Black 900*) sem a necessidade de carregar múltiplos arquivos estáticos.
- **Encaixe Perfeito de Kerning**: O kerning e a altura X dos glifos latinos foram calibrados para alinhar perfeitamente com a baseline quadrada do Hangul.

### B. 설립체 / Seollip-che (`establish Retrosans.ttf`) — A Fonte Retrô do Logotipo
A fonte **설립체** (Seollip-che / *establish Retrosans*) inspirou-se em letreiros industriais de lojas coreanas das décadas de 1980 e 1990. Ela traz o conceito retrô-futurista com traços geométricos marcantes.

- **Uso Exclusivo**: Utilizada estritamente no wordmark `세종학당 컴패니언` na tela de abertura (`/splash`), no cabeçalho da aplicação e nos cartões de marca do laboratório UI/UX (`/ui_test`).

---

## 3. 🚨 A Regra do Fallback no Flutter Engine (Evitando Glifos Tofu)

No motor Flutter (utilizado pelo Flet), o componente `CanvasKit` renderiza todos os textos diretamente em um elemento HTML5 Canvas.

### A Causa do Glifo Tofu (`□□□□`)
Quando uma fonte estritamente latina (como `Inter` ou `Roboto`) é configurada no tema global da aplicação (`page.theme = ft.Theme(font_family="Inter")`):
1. O texto em português renderiza normalmente.
2. Ao encontrar caracteres Hangul (ex: `"안녕하세요"`), a engine verifica se a fonte `Inter` possui os glifos na faixa Unicode `U+AC00` a `U+D7A3`.
3. Como a fonte latina não possui esses glifos, e no ambiente Web o Flutter não faz busca automática no sistema operacional do usuário, a engine desenha retângulos brancos vazios (conhecidos como **Tofu** `□□□□`).

### A Solução Definitiva
Ao definir **Pretendard** como a fonte padrão global no [src/theme.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/theme.py), a aplicação garante que 100% dos textos do aplicativo (sejam em português, coreano ou símbolos) tenham renderização nativa imediata sem erros de tela.

Veja o relatório detalhado do bug em [[bug_07_flutter_font_fallback_tofu_hangul]].

---

## 4. 🛠️ Registro e Configuração de Fontes no Flet

```python
# src/theme.py — Registro de Fontes e Configuração de Tema

def apply_app_theme(page: ft.Page):
    page.title = "Sejong Companion"
    
    # 1. Registro de Arquivos Locais no Mapa da Página
    page.fonts = {
        "Pretendard": "fonts/PretendardVariable.ttf",
        "Seollip-che": "fonts/establish_retrosans.ttf",
        "establish Retrosans": "fonts/establish_retrosans.ttf",
        "Noto Sans KR": "https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap",
    }

    # 2. Definição do Pretendard como Fonte Global Unificada
    page.theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
    page.dark_theme = ft.Theme(
        font_family="Pretendard",
        color_scheme_seed=Colors.PRIMARY,
        visual_density=ft.VisualDensity.COMFORTABLE,
    )
```

```python
# Uso do Seollip-che no Logotipo Retrô (src/views/splash_view.py)
ft.Text(
    "세종학당 컴패니언",
    size=26,
    font_family="Seollip-che", # Override explícito para o logotipo
    weight=ft.FontWeight.W_900,
    color=Colors.PRIMARY,
    style=ft.TextStyle(letter_spacing=2)
)
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- 🎨 Design System e Tokens: [[Design_System_e_Tokens_Semanticos]]
- 🧠 Estudo Didático Neuropedagógico: [[didactic_neuroscience_korean_ptbr]]
- 🚨 Bug dos Glifos Tofu: [[bug_07_flutter_font_fallback_tofu_hangul]]
