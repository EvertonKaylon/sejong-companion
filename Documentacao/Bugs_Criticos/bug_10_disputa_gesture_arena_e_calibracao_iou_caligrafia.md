# BUG-10: Disputa de Gestos na Gesture Arena & Calibração Espacial de IoU no Wongoji Lab

| Metadado | Detalhe |
| :--- | :--- |
| **ID do Bug** | `BUG-10` |
| **Severidade** | 🔴 Crítica (Bloqueador de Interação e Usabilidade Tátil) |
| **Componentes Afetados** | `CalligraphyWidget` (`src/components/calligraphy_widget.py`), `hangul_view` (`src/views/hangul_view.py`), `theme.py` |
| **Data de Resolução** | 2026-08-29 |
| **Branch** | `feature/calligraphy-grid` |
| **Testes Automatizados** | `tests/test_calligraphy_widget.py` (161 testes 100% aprovados) |

---

## 1. Descrição Sintomática

Durante os testes de toque e desenho na grade de caligrafia coreana 원고지 (Wongoji) em dispositivos móveis e navegadores web, manifestaram-se três anomalias críticas:

1. **Salto de Rolagem (Scroll Jump) e Pincel Travado:** Ao tocar na grade para iniciar um traço, a tela dava um salto abrupto para o topo da página, a tinta demorava para aparecer e o traçado falhava ou entrava em um estado intermitente de congelamento ("entra e sai").
2. **Guia e Diagnóstico Corrompidos:** O modelo fantasma (ghost layer) gerado a partir do bitmap 48×48 apresentava aspecto altamente pixelado e borrado; além disso, após clicar em "Avaliar Sílaba", os traços pretos cobriam o mapa colorido de diagnóstico (verde/vermelho), impedindo a visualização dos acertos e desvios.
3. **Injustiça na Métrica de Similaridade (Teto Artificial de ~50% de IoU):** Mesmo quando o usuário desenhava o caractere (ex: `가`, `한`) de forma extremamente precisa sobre o modelo visual, a similaridade computada não ultrapassava 50%–53%, impossibilitando a obtenção da classificação "Excelente" ou o disparo do feedback de áudio em coreano.

---

## 2. Causa Raiz Técnica

A investigação aprofundada revelou múltiplos fatores concorrentes na camada de interface e no motor de visão matricial:

### A. A "Gesture Arena" do Flutter e a Destruição do Viewport Rolável
No Flutter (motor subjacente ao Flet), gestos de toque (`PointerDownEvent`, `PointerMoveEvent`) entram em uma competição conhecida como **Gesture Arena**. Quando um `GestureDetector` com `on_pan_start` / `on_pan_update` é filho de um `ft.Column` ou `ft.ListView` rolável (`scroll=AUTO`), ambos tentam reivindicar os gestos de arrasto vertical.
Para contornar isso, a implementação inicial tentava alterar dinamicamente o parâmetro `column.scroll = None` no evento Python `on_pan_start` / `on_pan_down`. No entanto, no Flet/Flutter:
- Mudar a propriedade `scroll` de um `Column` reconstrói a árvore de RenderObjects do Viewport;
- A reconstrução destrói o estado do `ScrollPosition`, resetando a rolagem para o offset `0.0` (topo da página);
- A alteração do estado disparava `page.update()` durante o frame de toque, entupindo o canal de mensagens e causando atraso severo no pincel.

### B. Discrepância Geométrica entre Modelo Visual e Bitmap de Referência
O modelo fantasma na tela utilizava um tamanho de fonte com proporção de `0.56 × grade`, enquanto a rotina de rasterização de referência do Pillow (`render_reference_bitmap`) utilizava `0.68 × bitmap`. Essa diferença de 21% na escala significava que o usuário estava copiando uma letra com tamanho diferente daquela usada como gabarito, limitando matematicamente o IoU máximo a cerca de 0.37–0.41 mesmo para uma cópia milimétrica.

### C. Inversão na Ordem de Camadas do Canvas (Z-Index)
No `Flet Canvas`, os elementos são renderizados na ordem da lista `canvas.shapes`. Os retângulos de diagnóstico (verde/vermelho) estavam sendo adicionados **antes** dos traços pretos do usuário (`all_strokes`). Dessa forma, a tinta preta opaca era pintada por cima dos pixels coloridos de acerto e excesso.

### D. Severidade Excessiva do IoU Binário Pixel a Pixel
Em uma matriz de 48×48 pixels, pequenas imprecisões motoras humanas de 1 a 2 pixels (ou ligeiras variações de kerning/anti-aliasing entre o motor de texto Skia do Flutter e a biblioteca Pillow) faziam com que os pixels 1 da referência e do traço não coincidissem perfeitamente na mesma célula exata $(r, c)$, derrubando drasticamente a intersecção sem que houvesse um erro estrutural na escrita.

---

## 3. Soluções e Código: Antes vs. Depois

### A. Modo de Escrita em Foco Modal (Isolamento da Gesture Arena)

Substituiu-se a manipulação frágil de `scroll` por um **Wongoji Focus Mode** (`ft.AlertDialog` sem ancestral rolável). Na página principal, a grade opera como uma **prévia passiva** que permite rolagem natural sem conflitos de gesto.

#### Código Antes (Manipulação no fluxo de toque):
```python
# ❌ Abordagem frágil: alterar scroll durante o gesto causa reset e lag
def on_pan_down(e):
    calligraphy_column.scroll = None
    page.update()  # Provocava salto para o topo e travamento
```

#### Código Depois (Separação entre Prévia e Modo Modal):
```python
# ✅ Abordagem robusta: Prévia passiva na aba + Modal com Canvas isolado
writing_dialog = ft.AlertDialog(
    modal=True,
    content=ft.Container(
        content=calligraphy_widget,
        width=300,
        height=480,
    ),
    actions=[
        ft.TextButton(
            "Fechar / Voltar",
            icon=ft.Icons.ARROW_BACK,
            on_click=close_writing_mode,
        )
    ],
    on_dismiss=lambda _: refresh_preview(),
)

# Na aba principal: apenas um gatilho de toque para abrir o modal
preview_card = ft.GestureDetector(
    content=ft.Container(content=preview_canvas, ...),
    on_tap=open_writing_mode,
)
```

---

### B. Tipografia Oficial Kyobo e Ghost Layer Vetorial Suave

Substituiu-se a projeção matricial pixelada por renderização vetorial tipográfica com a fonte de caligrafia oficial coreana `KyoboHandwriting2025lyb.otf`.

#### Código Antes (Matricial pixelado):
```python
# ❌ Projeção de blocos 48x48 ampliados com aspecto serrilhado
cell_sz = size / 48
for r in range(48):
    for c in range(48):
        if ref_bitmap[r][c]:
            shapes.append(cv.Rect(c * cell_sz, r * cell_sz, cell_sz, cell_sz, ...))
```

#### Código Depois (Texto Vetorial Nativo Suave):
```python
# ✅ Renderização vetorial fluida com Kyobo Handwriting
shapes.append(
    cv.Text(
        x=size / 2,
        y=size / 2,
        text=self.target_char,
        alignment=ft.Alignment.CENTER,
        style=ft.TextStyle(
            size=int(size * 0.68),
            font_family="Kyobo Handwriting",
            color="#33A8A29E" if not is_dark else "#3378716C",
            weight=ft.FontWeight.BOLD,
        ),
    )
)
```

---

### C. IoU Tolerante Espacialmente (`calculate_tolerant_iou`)

Implementou-se dilatação morfológica com raio de tolerância $\pm 1$ pixel em 48×48 para absorver a variabilidade natural da coordenação motora humana sem comprometer a detecção de erros de forma.

#### Código Antes (IoU Rígido):
```python
# ❌ IoU binário estrito: qualquer desvio de 1px zera a intersecção local
def calculate_iou(ref, drawn):
    intersection = sum(1 for r in range(48) for c in range(48) if ref[r][c] == 1 and drawn[r][c] == 1)
    union = sum(1 for r in range(48) for c in range(48) if ref[r][c] == 1 or drawn[r][c] == 1)
    return intersection / union if union > 0 else 0.0
```

#### Código Depois (IoU com Dilatação Morfológica de Tolerância):
```python
# ✅ Dilatação morfológica controlada para avaliação justa
def _dilate_bitmap(bitmap: list[list[int]], radius: int) -> list[list[int]]:
    if radius <= 0 or not bitmap:
        return bitmap
    rows, cols = len(bitmap), len(bitmap[0])
    expanded = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if bitmap[r][c]:
                for rr in range(max(0, r - radius), min(rows, r + radius + 1)):
                    for cc in range(max(0, c - radius), min(cols, c + radius + 1)):
                        expanded[rr][cc] = 1
    return expanded

def calculate_tolerant_iou(bitmap_ref, bitmap_drawn, tolerance_radius=1) -> float:
    return calculate_iou(
        _dilate_bitmap(bitmap_ref, tolerance_radius),
        _dilate_bitmap(bitmap_drawn, tolerance_radius),
    )
```

---

### D. Ordenação Correta das Camadas no Canvas (Z-Index)

```python
# ✅ Ordem de pintura garantida: Fundo -> Guia -> Traços -> Diagnóstico (Overlay)
shapes.extend(grid_shapes)          # 1. Grade e moldura 원고지
shapes.extend(guide_shapes)         # 2. Letra modelo fantasma
shapes.extend(user_stroke_shapes)   # 3. Traços de tinta do usuário
if self.show_overlay:
    shapes.extend(overlay_shapes)   # 4. Mapa de calor (Verde/Vermelho/Cinza) no topo
```

---

## 4. Regras Preventivas

1. **Nunca concorrer `GestureDetector` de desenho contínuo com viewports roláveis no mesmo contexto visual:** Sempre utilizar tela cheia, modal ou componente com foco exclusivo quando o gesto exigir captura contínua de alta precisão.
2. **Nunca alterar propriedades estruturais como `scroll` durante eventos de interação (`on_pan_start` / `on_pan_update`):** No Flutter, mudar o modo de rolagem recria o RenderObject e reseta a posição da tela.
3. **Manter fonte, tamanho de fonte e proporção de centralização idênticos entre guia visual e gabarito de avaliação:** Se a referência usa escala $0.68$, o componente de exibição deve usar rigorosamente a mesma proporção.
4. **Adotar Tolerância Espacial em algoritmos de Visão voltados para Caligrafia Humana:** Reconhecedores de escrita manual devem aplicar dilatação ou distância de Hausdorff para não penalizar variações milimétricas naturais do traço.
5. **Tipografia Segmentada:** Manter fontes de alta legibilidade (ex: `Pretendard`) para componentes estruturais de UI e restringir fontes manuscritas/caligráficas (ex: `Kyobo Handwriting`) para o laboratório de prática de escrita.
