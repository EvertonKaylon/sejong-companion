# Plano de Pesquisa e Implementação — UI/UX Moderno para Apps Flet
### Acessibilidade · Fluidez · Design System · Elegância Profissional
**Aplicado ao Sejong Companion (Flet 0.85.3 + flet-audio + Typecast.ai)**

---

## Como usar este plano

Este documento é um roteiro técnico, não um manifesto teórico. Cada seção tem: (1) o conceito, (2) por que importa no seu caso específico (hardware limitado, app bilíngue PT-BR/한국어, propósito educacional), (3) snippet de código — do básico ao avançado — e (4) referências reais de projetos open-source para você ler o código-fonte deles diretamente.

A ordem das seções **é** a ordem de implementação recomendada. Pular direto para "Fase 5 (elegância visual)" sem ter os tokens da Fase 1 prontos é o erro mais comum que leva a inconsistência visual — e foi exatamente o tipo de acoplamento frágil que já te custou tempo de debugging no áudio (registro em `page.services`, corrida de montagem em `quiz_view.py`). Design system mal fundamentado gera o mesmo tipo de bug: sintomas espalhados, causa raiz centralizada.

---

## Sumário

1. [Diagnóstico e Objetivos](#1-diagnóstico-e-objetivos)
2. [Fundamentos: Design Tokens e Theming (Material 3)](#2-fundamentos-design-tokens-e-theming-material-3)
3. [Tipografia Bilíngue (PT-BR + 한국어)](#3-tipografia-bilíngue-pt-br--한국어)
4. [Acessibilidade (a11y) — Checklist e Implementação](#4-acessibilidade-a11y--checklist-e-implementação)
5. [Fluidez: Animações, Microinterações e Performance](#5-fluidez-animações-microinterações-e-performance)
6. [Arquitetura de Design System em Flet](#6-arquitetura-de-design-system-em-flet)
7. [Elegância Visual: Elevação, Glass, Gradientes, Grid](#7-elegância-visual-elevação-glass-gradientes-grid)
8. [Responsividade Multiplataforma](#8-responsividade-multiplataforma)
9. [Estudos de Caso — Bibliotecas Reais em Flet](#9-estudos-de-caso--bibliotecas-reais-em-flet)
10. [Roteiro de Implementação (Sprints)](#10-roteiro-de-implementação-sprints)
11. [Checklist Final de Qualidade](#11-checklist-final-de-qualidade)
12. [Referências](#12-referências)

---

## 1. Diagnóstico e Objetivos

**Contexto real do projeto:**
- Framework: Flet 0.85.3 (Material Design 3 + Cupertino nativo, arquitetura cliente-servidor Python↔Flutter)
- Hardware de desenvolvimento (atualizado): desktop com Intel Core i7-3770 (4 núcleos/8 threads, 3.4–3.9GHz), 8GB DDR3 1600MHz (single-channel, com plano de upgrade para 16GB), GeForce GT 730 4GB dedicada, SSD SATA 240GB. É um salto real em relação ao notebook Compaq Presario CQ42 (Pentium T4500) usado antes — CPU multi-thread e GPU dedicada mudam o que é "seguro" testar (blur, animações simultâneas), mesmo com RAM ainda limitada a 8GB. Isso não elimina a disciplina de performance deste plano, mas muda o ponto de referência: seu ambiente de dev deixa de ser o pior caso possível de usuário real (celulares antigos, Chromebooks, integrada sem GPU dedicada continuam existindo entre seus usuários), então vale testar tanto o modo "completo" quanto o modo `low_performance` — não assumir que o que roda bem na sua máquina roda bem para todo mundo.
- Domínio: app de aprendizado de coreano, conteúdo bilíngue, integração de áudio TTS (Typecast.ai)
- Você já iniciou um design system paralelo em Next.js + Tailwind v4 + shadcn/ui com tema violeta e tipografia coreana — isso vira uma vantagem: dá para tratar esse projeto Next.js como o **"livro de marca" (brand book)** e portar os tokens (cores, espaçamento, raio, tipografia) para o Flet, garantindo consistência entre os dois códigos.

**Objetivos deste plano:**
1. Estabelecer um design system tokenizado único, com uma "fonte de verdade" reaproveitável entre Flet e Next.js.
2. Elevar a acessibilidade a um nível que suporte leitores de tela, navegação por teclado e contraste adequado — crítico em um app *educacional*.
3. Aplicar fluidez (animações) com curva de aprendizado mínima e custo de performance controlado — testando tanto no seu desktop atual (i7-3770 + GT 730) quanto num cenário de hardware mais restrito, já que seus usuários reais não têm necessariamente a mesma máquina que você.
4. Alcançar um acabamento visual "profissional" sem depender de efeitos caros (blur pesado, glassmorphism excessivo) que penalizam seu hardware de teste.

---

## 2. Fundamentos: Design Tokens e Theming (Material 3)

### 2.1 O que são tokens e por que começar por eles

Um "design token" é qualquer valor de design (cor, espaçamento, raio, duração de animação, peso de fonte) que existe **uma vez só** no código e é referenciado em todo lugar. Sem isso, "deixar o app elegante" vira uma tarefa de encontrar e trocar valores espalhados manualmente — o mesmo padrão de dívida técnica que gerou o bug do `w_ampa` sem limite no seu simulador neuromórfico: um valor sem uma "fonte única de verdade" tende a divergir silenciosamente.

O Flet já usa nativamente o sistema de cores do **Material Design 3**: um `ColorScheme` com papéis semânticos (`primary`, `on_primary`, `secondary`, `surface`, `error`, etc.), não cores "cruas". Isso significa que, ao trocar sua cor de marca (violeta), todos os componentes nativos (botões, campos, diálogos) se realinham automaticamente — desde que você use os papéis semânticos e não hardcode `ft.Colors.PURPLE_500` em todo canto.

### 2.2 Estrutura de projeto recomendada

```
sejong_companion/
├── main.py
├── design/
│   ├── tokens.py          # cores, espaçamento, raio, durações — fonte única
│   ├── theme.py           # monta ft.Theme / ft.ColorScheme a partir dos tokens
│   └── typography.py      # TextTheme, registro de fontes
├── components/            # componentes reutilizáveis (ver Seção 6)
│   ├── glass_card.py
│   ├── quiz_option.py
│   └── audio_button.py
├── views/
│   ├── quiz_view.py
│   └── lesson_view.py
└── assets/
    └── fonts/
```

### 2.3 Snippet básico: tema com seed color (violeta) e modo claro/escuro

```python
# design/tokens.py
import flet as ft

class Tokens:
    # --- Cor de marca única (seed). Tudo deriva daqui. ---
    SEED = "#7C3AED"  # violeta — mesmo valor usado no projeto Next.js/shadcn

    # --- Espaçamento em escala de 8pt (ver Seção 7.4) ---
    SPACE_XS = 4
    SPACE_SM = 8
    SPACE_MD = 16
    SPACE_LG = 24
    SPACE_XL = 32

    # --- Raio de borda ---
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 20

    # --- Durações de animação (ver Seção 5) ---
    DUR_FAST = 150
    DUR_BASE = 250
    DUR_SLOW = 400
```

```python
# design/theme.py
import flet as ft
from design.tokens import Tokens

def build_light_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=Tokens.SEED,   # Flet gera o ColorScheme M3 completo a partir da seed
        font_family="Pretendard",
        use_material3=True,
    )

def build_dark_theme() -> ft.Theme:
    return ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=Tokens.SEED,
            on_primary=ft.Colors.WHITE,
            surface=ft.Colors.GREY_900,
            on_surface=ft.Colors.GREY_100,
            error=ft.Colors.RED_300,
        ),
        font_family="Pretendard",
    )

def apply_theme(page: ft.Page):
    page.theme = build_light_theme()
    page.dark_theme = build_dark_theme()
    page.theme_mode = ft.ThemeMode.SYSTEM  # respeita a preferência do SO do usuário
```

> **Nota técnica:** `color_scheme_seed` é a forma equivalente ao `ColorScheme.fromSeed()` do Flutter — gera automaticamente uma paleta harmônica de 20+ cores semânticas (containers, variantes, tons) a partir de uma única cor. Use isso antes de definir um `ColorScheme` manual completo; só migre para o manual quando precisar de controle fino (ex.: uma cor de erro específica de marca).

### 2.4 Snippet avançado: tokens compartilhados entre Flet e Next.js

Já que você mantém os dois projetos (Flet + Next.js/shadcn), a forma profissional de evitar divergência é um **arquivo único de tokens** em JSON, consumido pelos dois lados:

```json
// design-tokens.json (raiz compartilhada, versionada em ambos os repositórios)
{
  "color": { "seed": "#7C3AED", "error": "#EF4444" },
  "radius": { "sm": 8, "md": 12, "lg": 20 },
  "space":  { "xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32 },
  "duration": { "fast": 150, "base": 250, "slow": 400 }
}
```

```python
# design/tokens.py — carregado a partir do JSON compartilhado
import json
from pathlib import Path

_data = json.loads(Path(__file__).parent.joinpath("../../design-tokens.json").read_text())

SEED = _data["color"]["seed"]
RADIUS = _data["radius"]
SPACE = _data["space"]
DURATION = _data["duration"]
```

No lado Next.js, o mesmo arquivo alimenta as variáveis CSS/Tailwind (`--radius-md`, `--space-md`). Resultado: mudar a cor de marca em um único lugar propaga para os dois códigos sem retrabalho manual — o mesmo princípio de "fonte única de verdade" que você já aplica ao tratar hardware_config.py como fonte central de perfil de hardware no projeto neuromórfico.

---

## 3. Tipografia Bilíngue (PT-BR + 한국어)

### 3.1 Escolha de fonte: por que Pretendard

Para um app que mistura português e hangul, a escolha de fonte importa mais do que em apps monolíngues: fontes ocidentais comuns (Roboto, Inter) não têm glifos coreanos e caem para uma fonte de sistema qualquer quando renderizam hangul — quebrando a identidade visual exatamente no conteúdo que é o coração do app.

**Pretendard** é uma fonte neo-grotesca desenhada especificamente para isso: é construída a partir de Inter, Source Han Sans e M PLUS 1p, cobrindo alfabeto latino e hangul com métricas unificadas — sem exigir ajustes manuais posteriores de escala, espaçamento de letras ou correções ópticas entre os dois sistemas de escrita. Ela cobre latim e hangul com métricas consistentes — o que significa que um título em português e um título em coreano no mesmo peso/tamanho *parecem* parte do mesmo sistema visual, e não dois blocos de texto colados. Está disponível em 9 pesos e como fonte variável, sob licença SIL Open Font License (uso comercial livre).

### 3.2 Registro de fontes no Flet

```python
# design/typography.py
import flet as ft

FONT_URLS = {
    "Pretendard": "fonts/Pretendard-Regular.ttf",
    "Pretendard-Bold": "fonts/Pretendard-Bold.ttf",
    "Pretendard-SemiBold": "fonts/Pretendard-SemiBold.ttf",
}

def register_fonts(page: ft.Page):
    page.fonts = FONT_URLS
    page.theme = page.theme or ft.Theme()
    page.theme.font_family = "Pretendard"
```

> **Limitação real do Flet (validada na documentação atual):** apenas fontes estáticas são suportadas — um arquivo por combinação peso/estilo — porque suporte a fontes variáveis ainda está em desenvolvimento. Se você baixar a versão variável do Pretendard, precisa gerar instâncias estáticas por peso com `fonttools`:
> ```bash
> fonttools varLib.mutator Pretendard-Variable.ttf wght=600
> ```

### 3.3 Escala tipográfica e fallback

```python
# design/typography.py (continuação)
import flet as ft

def styled_text(value: str, style: ft.TextThemeStyle, weight: ft.FontWeight = None) -> ft.Text:
    return ft.Text(
        value,
        theme_style=style,
        weight=weight,
        font_family="Pretendard",
        # fallback: se um glifo não existir em Pretendard, tenta a fonte de sistema
        font_family_fallback=["Noto Sans KR", "Apple SD Gothic Neo", "sans-serif"],
    )

# Uso:
titulo = styled_text("안녕하세요 · Bem-vindo", ft.TextThemeStyle.HEADLINE_MEDIUM, ft.FontWeight.W_600)
corpo  = styled_text("Lição 3: Partículas 은/는", ft.TextThemeStyle.BODY_LARGE)
```

Usar `theme_style` (em vez de `size=` cru) amarra o texto à escala tipográfica do `Theme` — se depois você decidir aumentar todos os tamanhos de fonte 10% para acessibilidade (baixa visão), muda em um lugar só.

### 3.4 Alternativa/complemento: Noto Sans KR

Se precisar de um peso ou estilo que o Pretendard não cobrir, vale saber que a base dos glifos coreanos do Pretendard vem justamente do Noto Sans KR — ou seja, os dois combinam estruturalmente e podem ser usados como par (títulos em Pretendard, texto muito longo/denso em Noto Sans KR) sem parecerem dissonantes.

---

## 4. Acessibilidade (a11y) — Checklist e Implementação

### 4.1 Por que isso é inegociável em um app educacional

Acessibilidade cara demais para "adicionar depois" é um mito recorrente: [a comunidade Flutter já documentou que retrofitting custa 3-5x mais que projetar com acessibilidade desde o início](https://dev.to/kanta13jp1/flutter-accessibility-semantics-screen-readers-and-wcag-compliance-48j2). Num app de idiomas, isso é ainda mais crítico: parte real do seu público pode depender de leitor de tela para *ouvir* a pronúncia coreana e o texto, e o app já lida com áudio como cidadão de primeira classe.

### 4.2 O que o Flet já resolve de graça — e o que você precisa fazer manualmente

O Flet é construído sobre o Flutter, que tem base sólida de acessibilidade em Android, iOS, web e desktop. Mas isso não é automático para tudo:

| Controle | Comportamento nativo | O que você precisa fazer |
|---|---|---|
| `ft.Button`/`FilledButton` com texto | Gera semântica correta sozinho | Nada |
| `ft.IconButton`, `FloatingActionButton`, `PopupMenuButton` | **Sem label por padrão** | Definir `tooltip=` sempre |
| `ft.TextField`, `ft.Dropdown` | Sem rótulo para leitor de tela por padrão | Definir `label=` |
| `ft.Text` | Lê o próprio conteúdo | Usar `semantics_label` quando o texto visível difere do que deveria ser falado (ex.: emoji, símbolo) |
| Qualquer controle customizado feito de `Container`+`GestureDetector` | **Invisível para leitor de tela** | Envolver com `ft.Semantics` |

### 4.3 Snippet básico: tooltip, label, foco

```python
import flet as ft

def build_login_form():
    return ft.Column([
        ft.TextField(
            label="이메일 · E-mail",
            hint_text="Digite seu e-mail",
            autofocus=True,
        ),
        ft.TextField(
            label="비밀번호 · Senha",
            password=True,
            can_reveal_password=True,
        ),
        ft.Row([
            ft.IconButton(
                icon=ft.Icons.VOLUME_UP,
                tooltip="Ouvir pronúncia",   # essencial — sem isso, leitor de tela só fala "botão"
                on_click=lambda e: None,
            ),
            ft.FilledButton("Entrar", on_click=lambda e: None),
        ]),
    ])
```

### 4.4 Snippet intermediário: `Semantics` em componente customizado (cartão de quiz)

Componentes feitos "na unha" (Container + GestureDetector/InkWell) não geram semântica nenhuma por padrão — é preciso descrever explicitamente o papel e o estado:

```python
import flet as ft

def quiz_option_card(text_kr: str, text_pt: str, is_correct: bool | None, on_select):
    return ft.Semantics(
        tooltip="Toque duas vezes para selecionar esta opção",
        value="Selecionada" if is_correct is not None else None,
        on_tap=lambda e: on_select(),
        content=ft.Container(
            content=ft.Column([
                ft.Text(text_kr, theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.Text(text_pt, theme_style=ft.TextThemeStyle.BODY_SMALL),
            ]),
            padding=16,
            border_radius=12,
            ink=True,               # feedback visual de toque (ripple) — também ajuda usuários com baixa visão
            on_click=lambda e: on_select(),
        ),
    )
```

### 4.5 Depuração de acessibilidade

O Flet expõe um overlay de depuração nativo — use-o durante todo o desenvolvimento, não só no fim:

```python
page.show_semantics_debugger = True  # mostra a árvore de semântica sobreposta na UI
```

Em web, lembre o usuário (ou vá testando você mesmo) que leitores de tela precisam habilitar "Enable accessibility" no próprio navegador para o Flet construir a árvore semântica completa — isso é uma particularidade do Flutter Web, não um bug seu.

### 4.6 Checklist de contraste e alvo de toque

Mesmo sem uma ferramenta de auditoria automática no Flet, os números-alvo do WCAG/Material se aplicam da mesma forma:
- Contraste mínimo texto/fundo: **4.5:1** para texto normal, 3:1 para texto grande (≥18pt ou 14pt bold).
- Alvos de toque (botões, ícones): mínimo **48×48px** — importante no seu caso porque telas de quiz tendem a ter múltiplas opções pequenas lado a lado.
- Nunca comunique estado (certo/errado no quiz) **só** por cor — combine cor + ícone + texto (ex.: verde + ✓ + "Correto"), para daltônicos e para quem usa leitor de tela.
- Respeite `prefers-reduced-motion`: para usuários sensíveis a movimento, animações de entrada/saída devem poder ser reduzidas — no Flet isso significa checar `page.platform_brightness`/preferências do SO quando disponível, ou expor um toggle "reduzir animações" nas configurações do app (a forma mais confiável de garantir isso hoje).

---

## 5. Fluidez: Animações, Microinterações e Performance

### 5.1 O modelo mental: animação implícita

O Flet usa o modelo de **animações implícitas** do Flutter: você não anima manualmente frame a frame — você declara uma propriedade "animável" (`animate_opacity`, `animate_scale`, `animate_position`, `animate_offset`, `animate_rotation`) e, toda vez que o valor-alvo muda, o Flet interpola sozinho entre o valor antigo e o novo, ao longo de uma duração e curva definidas.

Isso é ótimo para seu caso: é barato de escrever e, quando bem configurado, barato de rodar — muito mais leve que orquestrar animações manuais com controllers, que é o modelo "explícito" (reservado para loops, gestos e coreografias complexas que você provavelmente não precisa no Sejong Companion).

### 5.2 Regra de ouro de curva × duração

Curva errada é a diferença entre "parece profissional" e "parece que travou": a curva padrão é linear (velocidade constante), o que sempre parece mecânico. Curvas como `EASE_OUT_CUBIC` aceleram no início e desaceleram suavemente no final — isso imita como objetos físicos se movem e é o que o olho humano lê como "fluido".

| Interação | Duração sugerida | Curva sugerida |
|---|---|---|
| Botão pressionado (feedback rápido) | 100–150ms | `EASE_OUT` |
| Troca de conteúdo (ex.: pergunta→próxima pergunta) | 200–300ms | `EASE_IN_OUT` |
| Feedback de acerto/erro no quiz | 300–500ms | `BOUNCE_OUT` (só no acerto — para erro prefira algo mais sóbrio, `EASE_OUT`, para não "comemorar" o erro) |
| Entrada de tela/modal | 250–350ms | `EASE_OUT_CUBIC` |

### 5.3 Snippet básico: feedback de toque

```python
import flet as ft

def bounce_button(text: str, on_click):
    btn = ft.Container(
        content=ft.Text(text, weight=ft.FontWeight.W_600),
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        border_radius=12,
        bgcolor=ft.Colors.PRIMARY,
        scale=1.0,
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        on_click=lambda e: on_click(e),
    )

    def press(e):
        btn.scale = 0.96
        btn.update()

    def release(e):
        btn.scale = 1.0
        btn.update()

    btn.on_long_press_start = press   # feedback tátil visual no toque
    btn.on_long_press_end = release
    return btn
```

### 5.4 Snippet intermediário: transição de conteúdo com `AnimatedSwitcher`

Para trocar a pergunta do quiz sem um "corte seco":

```python
import flet as ft

class QuizCard(ft.Column):
    def __init__(self):
        super().__init__()
        self.switcher = ft.AnimatedSwitcher(
            content=self._build_question("..."),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=250,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
        )
        self.controls = [self.switcher]

    def _build_question(self, text: str) -> ft.Control:
        return ft.Text(text, key=text, theme_style=ft.TextThemeStyle.HEADLINE_SMALL)

    def go_to_next_question(self, next_text: str):
        self.switcher.content = self._build_question(next_text)
        self.switcher.update()
```

### 5.5 Snippet avançado: feedback de acerto com escala + rotação combinadas

```python
import flet as ft

def feedback_icon(is_correct: bool) -> ft.Container:
    icon = ft.Icon(
        ft.Icons.CHECK_CIRCLE if is_correct else ft.Icons.CANCEL,
        color=ft.Colors.GREEN if is_correct else ft.Colors.ERROR,
        size=0,  # começa em 0 — "nasce" com a animação
    )
    container = ft.Container(
        content=icon,
        animate_rotation=ft.Animation(400, ft.AnimationCurve.BOUNCE_OUT) if is_correct else None,
    )

    async def reveal():
        icon.size = 48
        icon.rotate = 0.15 if is_correct else 0  # leve "giro" só no acerto
        container.update()

    return container, reveal
```

> **Cuidado de performance específico para o seu hardware:** desenvolvedores da comunidade Flet já relataram que alguns controles não têm mecanismo de *throttling* embutido — quando isso acontece em cenários muito interativos, o volume de dados indo e voltando pelo WebSocket congestiona a comunicação e trava a aplicação inteira, não só o componente em questão. Na prática: eventos de alta frequência (`on_change` de sliders, campos de texto com busca em tempo real) devem ser debounced manualmente no seu código Python antes de disparar `update()` — especialmente relevante com 8GB de RAM single-channel, mesmo num CPU multi-thread capaz como o i7-3770.

### 5.6 Hero animations (transição de elemento compartilhado)

Desde a versão 0.81, o Flet suporta transições visuais avançadas com animações Hero (elemento compartilhado entre telas) e transformações Matrix4 — útil para, por exemplo, o ícone de áudio "voar" da lista de lições para a tela de detalhe da lição, criando uma sensação de continuidade espacial em vez de troca abrupta de tela.

### 5.7 Performance: batching de atualizações

Cada `page.update()` envia uma mensagem via WebSocket com todas as mudanças desde a última chamada. Mensagens grandes demais sobrecarregam esse canal, então a prática recomendada é sempre agrupar mudanças e enviar em lote em vez de disparar uma atualização por item. Regra prática:

```python
# EVITAR — um update() por item, gera N mensagens
for item in lesson_items:
    page.controls.append(build_item(item))
    page.update()   # ❌ 1 round-trip por item

# PREFERIR — monta tudo, um único update()
new_controls = [build_item(item) for item in lesson_items]
page.controls.extend(new_controls)
page.update()   # ✅ 1 round-trip só
```

Para listas longas (histórico de lições, ranking, vocabulário), prefira `ft.GridView`/`ft.ListView` (que já viram lazy-rendering) em vez de montar uma `Column` gigante — isso muda "rolagem engasgada" para "rolagem fluida" mesmo em hardware modesto.

### 5.8 Um lembrete alinhado ao seu próprio histórico de debugging

O bug do WebSocket/`play()` sem gesto direto do usuário (flet-dev/flet#3695) que você já resolveu com autoplay mudo é, na essência, o mesmo tipo de problema que animações mal-sequenciadas causam: uma ação client-side que dispara **antes** do estado estar pronto no servidor. Ao encadear animações (ex.: tocar áudio *depois* que o card termina de entrar na tela), use o evento `on_animation_end` do controle em vez de `asyncio.sleep()` arbitrário — isso elimina uma classe inteira de corrida de estado, do mesmo jeito que você já resolveu a corrida de montagem em `quiz_view.py`.

---

## 6. Arquitetura de Design System em Flet

### 6.1 Componentização em camadas (Atomic Design adaptado)

```
tokens/       → cores, espaçamento, duração (Seção 2)
   ↓
atoms/        → Text estilizado, Button, Icon com tooltip padrão
   ↓
molecules/    → QuizOptionCard, AudioButton, ProgressChip
   ↓
organisms/    → QuizCard completo, LessonHeader, StatsPanel
   ↓
views/        → quiz_view.py, lesson_view.py (compõem organisms)
```

A regra prática: **nenhuma view deveria conter `bgcolor="#7C3AED"` cru** — se um valor de design aparece direto numa view, é sinal de que faltou promovê-lo a token ou componente.

### 6.2 Snippet: componente reutilizável herdando `ft.Container`

```python
# components/glass_card.py
import flet as ft
from design.tokens import Tokens

class GlassCard(ft.Container):
    """Cartão elevado padrão do design system — uma única definição,
    usado em quiz, lição e perfil."""

    def __init__(self, content: ft.Control, **kwargs):
        super().__init__(
            content=content,
            padding=Tokens.SPACE_MD,
            border_radius=Tokens.RADIUS_LG,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
            shadow=ft.BoxShadow(
                blur_radius=16,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
            animate=ft.Animation(Tokens.DUR_BASE, ft.AnimationCurve.EASE_OUT),
            **kwargs,
        )
```

Uso em qualquer view:

```python
from components.glass_card import GlassCard

page.add(GlassCard(content=ft.Text("Lição 3")))
```

Se amanhã você decidir que todos os cartões do app devem ter `border_radius=16` em vez de 20, muda em **um** arquivo (`tokens.py`), não em cada view.

### 6.3 Onde a arquitetura de estado entra

Um design system sem gerência de estado organizada tende a degradar em "componentes bonitos, lógica emaranhada". Duas rotas viáveis, dependendo de quanto boilerplate você quer aceitar:

- **Leve, sem dependências:** classes Python simples encapsulando estado + método `build()`, como você já está fazendo com `quiz_view.py`.
- **Estruturada:** o projeto comunitário **FletX** (inspirado em GetX do Flutter) propõe uma estrutura pronta com controllers/services/pages/components e primitivos reativos (`RxInt`, `RxStr`, decorador `@obx`) — vale a leitura do código-fonte mesmo que você não adote a lib inteira, só para roubar o padrão de separar `controllers/` (estado) de `components/` (visual).

```python
# padrão inspirado no FletX — dá para replicar sem instalar a lib
class QuizController:
    def __init__(self):
        self.current_index = 0
        self.score = 0
        self._listeners = []

    def on_change(self, fn):
        self._listeners.append(fn)

    def notify(self):
        for fn in self._listeners:
            fn(self)

    def answer(self, correct: bool):
        if correct:
            self.score += 1
        self.current_index += 1
        self.notify()
```

---

## 7. Elegância Visual: Elevação, Glass, Gradientes, Grid

### 7.1 O princípio central: restrição, não acúmulo

A diferença entre um app "bonito" e um app "com aparência de IA genérica" quase sempre é *quantidade* de efeitos, não qualidade de um efeito isolado. A prática de design mais confiável aqui é: **escolha um elemento de assinatura visual** (no seu caso, provavelmente o gradiente violeta + tipografia coreana em destaque) e deixe tudo ao redor discreto e disciplinado. Sombra, blur, gradiente e animação todos ligados ao mesmo tempo no mesmo componente é o padrão mais comum de UI que "parece gerada", exatamente o oposto de "elegante".

### 7.2 Elevação (sombras) — a forma barata de dar profundidade

```python
import flet as ft

def elevated_surface(content: ft.Control, level: int = 1) -> ft.Container:
    """level 1 = sutil (cards), level 2 = destaque (modais, FAB)"""
    blur = {1: 8, 2: 20}[level]
    opacity = {1: 0.08, 2: 0.18}[level]
    return ft.Container(
        content=content,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        shadow=ft.BoxShadow(
            blur_radius=blur,
            color=ft.Colors.with_opacity(opacity, ft.Colors.BLACK),
            offset=ft.Offset(0, blur / 4),
        ),
    )
```

Sombra é **muito** mais barata computacionalmente do que blur de fundo (`BackdropFilter`), então em hardware limitado, prefira elevação por sombra a glassmorphism sempre que o efeito visual desejado for "isso está por cima de algo".

### 7.3 Glassmorphism — use com moderação e sempre com plano B

O efeito de "vidro fosco" (fundo borrado + transparência + borda clara sutil) é feito no Flet via `blur=` no `Container`. É visualmente elegante, mas caro: cada superfície com blur exige que o motor de renderização reprocesse os pixels por trás dela a cada frame. Boas práticas confirmadas pela documentação e comunidade Flutter/Flet:
- Nunca empilhe dois `Container`s com blur um sobre o outro.
- Limite a área da região borrada — não aplique blur na tela inteira.
- Tenha uma variante "flat" (sem blur, só cor semi-transparente + borda) para dispositivos/modo de baixa performance.

```python
import flet as ft

def glass_panel(content: ft.Control, low_performance: bool = False) -> ft.Container:
    if low_performance:
        # fallback leve: mesma linguagem visual, sem custo de blur
        return ft.Container(
            content=content,
            bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.20, ft.Colors.WHITE)),
            border_radius=20,
            padding=20,
        )
    return ft.Container(
        content=content,
        blur=ft.Blur(sigma_x=18, sigma_y=18),
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
        border=ft.border.all(1, ft.Colors.with_opacity(0.20, ft.Colors.WHITE)),
        border_radius=20,
        padding=20,
    )
```

Com a GeForce GT 730 dedicada no seu desktop atual, você tem uma GPU real para acelerar composição/blur — isso é bem diferente do notebook antigo, onde a única opção segura era assumir o pior caso o tempo todo. O caminho pragmático agora é outro: **teste os dois modos de propósito**, não escolha um só por padrão.

- No seu desktop (i7-3770 + GT 730 + 8GB RAM), rode o modo completo (`low_performance=False`) e confirme que ele é realmente fluido — isso valida a experiência "de vitrine" do app.
- Simule o pior caso separadamente: rode a build web em um celular/notebook mais antigo (ou limite CPU/GPU artificialmente nas ferramentas de profiling do Chrome/Flutter DevTools) para validar o modo `low_performance=True`.
- No app, deixe a alternância como preferência do usuário (ou uma detecção simples de plataforma/dispositivo), em vez de fixar um dos dois modos no código — isso serve tanto quem tem um celular topo de linha quanto quem tem hardware mais modesto, sem você ter que escolher por eles.

### 7.4 Grid de espaçamento de 8pt

Uma escala de espaçamento consistente (múltiplos de 8: 4, 8, 16, 24, 32, 40...) é a técnica mais barata e mais eficaz para o app parecer "desenhado por alguém", em vez de "espaçado no olho". Isso já está embutido nos tokens da Seção 2 (`SPACE_XS`...`SPACE_XL`) — a disciplina real está em **nunca** escrever `padding=13` ou `padding=22` fora dessa escala.

### 7.5 Gradientes com intenção, não decoração

```python
import flet as ft

hero_gradient = ft.LinearGradient(
    begin=ft.alignment.top_left,
    end=ft.alignment.bottom_right,
    colors=["#7C3AED", "#4C1D95"],  # violeta → violeta escuro, mesma família de cor
)
```

Gradiente funciona melhor quando reforça hierarquia (destacar *um* elemento-chave, como o cabeçalho da lição atual) e pior quando aplicado "porque fica bonito" em todo card da tela — nesse caso ele compete visualmente consigo mesmo e cansa o olho.

---

## 8. Responsividade Multiplataforma

O Flet compila para desktop, web e mobile a partir do mesmo código — mas "rodar" nas três plataformas não é o mesmo que "ser usável" nas três. `ResponsiveRow` é a ferramenta nativa para isso: um grid virtual de colunas (padrão 12, à la Bootstrap) que se reorganiza por breakpoint nomeado.

```python
import flet as ft

def lesson_grid(lessons: list[ft.Control]) -> ft.ResponsiveRow:
    return ft.ResponsiveRow(
        controls=[
            ft.Container(lesson, col={"xs": 12, "sm": 6, "md": 4, "xl": 3})
            for lesson in lessons
        ],
    )
```

No exemplo acima: celular mostra 1 card por linha (`xs: 12` = ocupa as 12 colunas), tablet mostra 2 (`sm: 6`), desktop mostra 3 (`md: 4`) e telas largas mostram 4 (`xl: 3`).

Para lógica condicional mais fina (trocar navegação inferior por rail lateral em telas largas, por exemplo), escute o redimensionamento:

```python
def main(page: ft.Page):
    def on_resize(e):
        is_desktop = page.window.width and page.window.width >= 900
        nav.visible = not is_desktop
        rail.visible = is_desktop
        page.update()

    page.on_resize = on_resize
```

---

## 9. Estudos de Caso — Bibliotecas Reais em Flet

Como pedido: aqui estão projetos open-source reais para você ler o código-fonte, do mais simples ao mais arquiteturalmente ambicioso. Todos estão listados no repositório oficial **awesome-flet** (`github.com/flet-dev/awesome-flet`), que vale colocar nos favoritos como índice vivo.

### 9.1 `material_design_flet` — o mais simples: theming centralizado

```python
import flet as ft
import flet_material as fm

fm.Theme.set_theme(theme="teal")

def main(page: ft.Page):
    page.bgcolor = fm.Theme.bgcolor
    button = fm.Buttons(width=220, height=55, title="Give this repo a star!")
    page.add(button)

ft.app(target=main)
```
**O que estudar aqui:** o padrão de uma classe `Theme` estática configurada uma vez no topo do arquivo, com todos os componentes lendo dela — é a versão mais simples possível do que a Seção 2 deste plano formaliza.

### 9.2 `fletmint` — API de componente "sharp and modern"

```python
import flet as ft
from fletmint import *

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#22242a"
    page.add(
        TagsInput(max_width=300, max_tags=2),
        Stepper(initial_value=123, suffix="px"),
        TabSwitch(["Label", "Label", "Label"], on_switch=lambda v: print(v)),
    )

ft.app(target=main)
```
**O que estudar aqui:** cada componente (`TagsInput`, `Stepper`, `TabSwitch`) herda de `ft.Container` e expõe uma API própria e opinativa (não é um wrapper fino do Flet puro) — é o mesmo espírito do `GlassCard` da Seção 6.2, só que num catálogo mais amplo. Vale ler o repositório (`github.com/Bbalduzz/fletmint`) para ver como eles implementam `TextInput` com prefixo/sufixo de ícone, um padrão que serve direto para o seu botão de "ouvir pronúncia" com ícone embutido.

### 9.3 `FletX` — arquitetura de aplicação completa

```bash
pip install FletXr[dev] --pre
fletx new sejong_companion
cd sejong_companion
fletx run --web --watch
```
Estrutura gerada:
```
app/
├── controllers/   # estado e lógica de negócio
├── services/      # APIs, storage, utilitários
├── pages/         # telas
├── components/    # widgets reutilizáveis
└── routes.py      # todas as rotas em um só lugar
```
**O que estudar aqui:** separação estrita entre `controllers` (estado reativo — `RxInt`, `RxStr`, `RxList`) e `pages`/`components` (puramente visual). Mesmo sem adotar o framework inteiro, a convenção de pastas é diretamente aplicável ao Sejong Companion e resolve o mesmo problema que você já sente na prática: view e lógica de áudio/estado acopladas demais em um único arquivo.

### 9.4 Referências de bugs e discussões técnicas para acompanhar

Esses são threads reais no repositório oficial (`github.com/flet-dev/flet`) relevantes para decisões deste plano:
- **Issue #2972** — discussão da comunidade sobre como customizar/trocar o design system além do Material padrão (relevante para a Seção 2).
- **Discussion #6494** e **#6095** — feedback aprofundado de desenvolvedores sobre gargalos de performance e ausência de throttling em alguns controles (relevante para a Seção 5.5/5.7).
- **Issue #4521** — fontes customizadas não aplicadas corretamente em builds web com CanvasKit; teste sua fonte Pretendard especificamente em build web, não assuma que o comportamento do modo desktop se repete lá.

---

## 10. Roteiro de Implementação (Sprints)

Sequência pensada para não empilhar retrabalho — cada sprint depende do anterior.

| Sprint | Foco | Entregável concreto |
|---|---|---|
| **1** | Tokens + Theme | `design/tokens.py`, `design/theme.py`, `color_scheme_seed` aplicado, tema claro/escuro funcionando |
| **2** | Tipografia | Pretendard registrada e aplicada via `TextTheme`/`theme_style`, fallback para Noto Sans KR testado em web e desktop |
| **3** | Acessibilidade base | Todo `IconButton`/`FAB` com `tooltip`, todo `TextField` com `label`, `show_semantics_debugger` testado uma vez em cada view |
| **4** | Componentização | `GlassCard`, `QuizOptionCard`, `AudioButton` extraídos como componentes reais (Seção 6), zero cor/raio "cru" nas views |
| **5** | Fluidez | Animações implícitas nos componentes-chave (quiz, feedback, transição entre lições), com `on_animation_end` substituindo qualquer `sleep()` arbitrário |
| **6** | Elegância visual | Elevação padronizada (Seção 7.2), variante `low_performance` do glass panel testada tanto no seu desktop (i7-3770 + GT 730) quanto simulando hardware mais restrito |
| **7** | Responsividade | `ResponsiveRow` nas telas de lista (lições, vocabulário), `on_resize` para navegação adaptativa |
| **8** | Auditoria final | Checklist da Seção 11 rodado por completo, incluindo teste real com leitor de tela (NVDA/Orca) |

---

## 11. Checklist Final de Qualidade

**Acessibilidade**
- [ ] Todo elemento interativo tem rótulo audível (`tooltip`, `label` ou `semantics_label`)
- [ ] Contraste texto/fundo ≥ 4.5:1 em todas as combinações de tema (claro e escuro)
- [ ] Alvos de toque ≥ 48×48px
- [ ] Estado certo/errado do quiz comunicado por cor **+** ícone **+** texto
- [ ] Testado com `show_semantics_debugger=True` em pelo menos uma passada por view
- [ ] Testado com leitor de tela real (não só o debugger)

**Fluidez e performance**
- [ ] Nenhum `page.update()` dentro de loop sem necessidade
- [ ] Listas longas usam `ListView`/`GridView`, não `Column` crua
- [ ] Eventos de alta frequência (`on_change`) têm debounce manual
- [ ] Todas as animações testadas no hardware mais fraco disponível, não só no ambiente "rápido"
- [ ] Toda animação de conteúdo (áudio após transição, por exemplo) usa `on_animation_end`, não `sleep()`

**Design system**
- [ ] Nenhuma cor/raio/espaçamento "cru" fora de `tokens.py`
- [ ] Tokens de cor sincronizados com o projeto Next.js/shadcn (mesmo arquivo-fonte ou processo manual documentado)
- [ ] Componentes reutilizáveis vivem em `components/`, não duplicados entre views

**Elegância**
- [ ] Um elemento de assinatura visual claro (não três ou quatro competindo)
- [ ] Ambos os modos (`low_performance=True` e `False`) testados — um no seu desktop atual, outro simulando hardware mais restrito
- [ ] Tipografia hierarquizada via `theme_style`, nunca `size=` arbitrário

---

## 12. Referências

- Flet — Theming System: https://mintlify.wiki/flet-dev/flet/concepts/theming
- Flet — Animations Cookbook: https://flet.dev/docs/cookbook/animations/
- Flet — Accessibility Cookbook: https://flet.dev/docs/cookbook/accessibility/
- Flet — Semantics Control: https://docs.flet.dev/controls/semantics/
- Flet — Fonts Cookbook: https://flet.dev/docs/cookbook/fonts/
- Flet — Text Control (TextTheme/font_family_fallback): https://flet.dev/docs/controls/text/
- Flet — ResponsiveRow: https://docs.flet.dev/controls/responsiverow/
- Flet — Navigation and Routing: https://docs.flet.dev/cookbook/navigation-and-routing/
- Flet — Router (manage_views): https://flet.dev/docs/controls/router/
- Flet — Container (blur, shadow, gradient): https://flet.dev/docs/controls/container/
- Flet — Large Lists / batched updates: https://flet.dev/docs/cookbook/large-lists/
- Flet — Blog (versões 0.81–0.85, Hero/Matrix4, performance): https://flet.dev/blog/
- Flet GitHub — awesome-flet (índice de bibliotecas): https://github.com/flet-dev/awesome-flet
- Flet GitHub — fletmint: https://github.com/Bbalduzz/fletmint
- Flet GitHub — FletX: https://github.com/AllDotPy/FletX
- Flet GitHub — material_design_flet: https://github.com/LineIndent/material_design_flet
- Flet GitHub — Issue #2972 (customização de design system): https://github.com/flet-dev/flet/issues/2972
- Flet GitHub — Discussion #6494 (feedback de performance): https://github.com/flet-dev/flet/discussions/6494
- Flet GitHub — Issue #4521 (fontes customizadas + CanvasKit web): https://github.com/flet-dev/flet/issues/4521
- Pretendard — README oficial: https://github.com/orioncactus/pretendard
- Flutter Accessibility — Semantics, Screen Readers, WCAG: https://dev.to/kanta13jp1/flutter-accessibility-semantics-screen-readers-and-wcag-compliance-48j2
- Glassmorphism em Flutter (BackdropFilter, performance): https://vibe-studio.ai/insights/implementing-glassmorphism-effects-in-flutter-uis
