# ✍️ Reconhecimento Tátil e Caligrafia Hangul (원고지)

**Status:** VIGENTE / ARQUITETURA IMPLEMENTADA  
**Data de Atualização:** 2026-11-24  
**Componentes Relacionados:** `CalligraphyWidget` (`src/components/calligraphy_widget.py`), `WongojiMultiCellWidget` (`src/components/wongoji_multi_cell_widget.py`), `jamo_utils` (`src/jamo_utils.py`), `assets/stroke_order/jamo_strokes.json`  
**Documentos Vinculados:** [[Motor_Adaptativo_e_Learning_Engine]] | [[Neuropedagogia_e_Gamificacao]] | [[Tipografia_Bilingue_e_CJK]] | [[bug_10_disputa_gesture_arena_e_calibracao_iou_caligrafia]] | [[CHANGELOG]]

---

## 1. Fundamentos da Escrita Hangul e o Princípio Composicional

Diferente de sistemas alfabéticos lineares (como o alfabeto latino) ou logográficos holísticos (como os Hanja chineses), o **Hangul (한글)** opera como um sistema **alfabético-silábico composicional**, criado pelo Rei Sejong em 1446 (*Hunminjeongeum*).

Cada bloco silábico visível é estruturado deterministicamente a partir de subunidades fonéticas (**자모 — Jamo**):

```text
┌────────────────────────────────────────────────────────┐
│             ANATOMIA DO BLOCO SILÁBICO HANGUL          │
├────────────────────────────┬───────────────────────────┤
│ 1. 초성 (Choseong)         │ Consoante Inicial (19)    │
│ 2. 중성 (Jungseong)        │ Vogal Medial (21)         │
│ 3. 종성 (Jongseong/Batchim)│ Consoante Final (27 + ∅)  │
└────────────────────────────┴───────────────────────────┘
Total combinatório: 19 × 21 × 28 = 11.172 sílabas (Unicode U+AC00 a U+D7A3)
```

### Classificação Geométrica dos Blocos (6 Tipos)

Dependendo da orientação da vogal (vertical, horizontal ou composta) e da presença de *batchim*, o bloco assume um dos 6 layouts espaciais:

| Tipo de Bloco | Estrutura | Exemplo | Orientação da Vogal |
| :--- | :---: | :---: | :--- |
| `CV_VERTICAL` | Consoante + Vogal | **가**, **나** | Vertical (ㅏ, ㅐ, ㅑ, ㅓ, ㅔ, ㅕ, ㅣ) |
| `CV_HORIZONTAL` | Consoante / Vogal | **고**, **누** | Horizontal (ㅗ, ㅛ, ㅜ, ㅠ, ㅡ) |
| `CV_COMPOUND` | Consoante + Vogal Dupla | **과**, **의** | Composta (ㅘ, ㅙ, ㅚ, ㅝ, ㅞ, ㅟ, ㅢ) |
| `CVC_VERTICAL` | C + V / Batchim | **한**, **달** | Vertical com Consoante Final |
| `CVC_HORIZONTAL` | C / V / Batchim | **글**, **문** | Horizontal com Consoante Final |
| `CVC_COMPOUND` | C + V / Batchim | **광**, **읽** | Composta com Consoante Final |

---

## 2. A Grade Tradicional 원고지 (Wongoji)

**원고지 (原稿紙)** é o papel de manuscrito tradicional coreano composto por células quadradas perfeitas (proporção 1:1), onde cada caractere, espaço ou pontuação ocupa exatamente uma célula.

```text
┌───────────────┬───────────────┐
│       │       │       │       │
│ - - - ┼ - - - │ - - - ┼ - - - │  ← Linhas guia internas (Cruz Central)
│       │       │       │       │
├───────────────┼───────────────┤
│       │       │       │       │
│ - - - ┼ - - - │ - - - ┼ - - - │
│       │       │       │       │
└───────────────┴───────────────┘
```

Na implementação digital do **Saebom Companion (새봄 컴패니언)** (paleta **Brand Book v3.1** — Midnight Navy `#02060F`, Cream `#F7F4EC`, Slate `#9EA2AE`, tinta primária em Violet `#8B4DFF` e destaques em Gold `#FFAB22`):
1. **Camada de Fundo (Grid Layer)**: Renderiza as bordas da célula e as linhas pontilhadas da cruz central para orientar a proporção dos quadrantes.
2. **Camada de Modelo (Ghost Layer)**: Projeta o silabograma guia na fonte oficial **Kyobo Handwriting 2025** (`KyoboHandwriting2025lyb.otf`) com escala `0.68` idêntica à matriz de avaliação.
3. **Camada de Interação e Diagnóstico (`Z-Index` Superior)**: Captura coordenadas via `GestureDetector`, projeta a tinta do usuário e renderiza o overlay de diagnóstico no topo dos traços.

---

## 3. Neuropedagogia: Memória Motora e Progressão Pedagógica

Pesquisas em neurociência cognitiva da escrita (Sweller, Ullman) demonstram que o aprendizado de novos alfabetos é potencializado pela formação de **traços de memória procedurais e proprioceptivos** (*motor memory*).

* **Ordem de Traços (획순 - Stroke Order)**: Catálogo de 51 jamo (19 consoantes, 21 vogais, 11 compostos) em `assets/stroke_order/jamo_strokes.json` seguindo regras canônicas (*de cima para baixo* e *da esquerda para a direita*).
* **Progressão Pedagógica**:
  1. *Tracing Guiado (따라쓰기)* — Modelo fantasma visível na grade com fonte manuscrita **Kyobo Handwriting 2025**.
  2. *Prática com Dicas Ocultáveis* — O aluno pode ocultar o guia e consultar o diagnóstico visual pós-escrita.
  3. *Escrita Livre em Palavras e Frases (`WongojiMultiCellWidget`)* — Fita de visão geral + célula de foco ativo de `210×210px`, respeitando a regra de espaçamento coreano (*띄어쓰기* com células `␣` excluídas do cálculo IoU) e acionamento exclusivo da avaliação pelo botão **"✅ Terminei"** nos 23 exercícios caligráficos dos Workbooks 1A e 1B.

---

## 4. Evolução: Do Path Matching ao Wongoji Lab (Visão Tipográfica & IoU Tolerante)

Nas primeiras iterações (`v0.3.3-alpha`), o componente utilizou validação direcional de traços por *Path Matching* (destacando traços aceitos na cor primária vigente — hoje **Violet `#8B4DFF`**, após a descontinuação histórica do antigo azul `#004C97`).

A partir de `v0.3.4`–`v0.3.5-alpha`, o **Wongoji Lab** evoluiu para avaliação visual morfológica de escrita livre de alta fidelidade:

```text
                      PIPELINE DE VISÃO TIPOGRÁFICA (WONGOJI LAB)

   Letra Alvo (ex: "새", "봄", "가")           Traços Livres do Usuário
          │                                              │
          ▼                                              ▼
   ┌─────────────────────────────┐                ┌─────────────────────────────┐
   │ Rasterização Kyobo 2025     │                │ Rasterização de Traços      │
   │ (Matriz 48×48, escala 0.68) │                │ (Espessura Proporcional)    │
   └──────────────┬──────────────┘                └──────────────┬──────────────┘
                  │                                              │
                  ▼                                              ▼
            Bitmap Referência                              Bitmap Usuário
                  │                                              │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 1. Dilatação Morfológica de Tolerância       │
                  │    (Absorve microdesvios motores de ±1px)    │
                  ├──────────────────────────────────────────────┤
                  │ 2. Cálculo do Índice IoU Tolerante           │
                  │    IoU = Area(Intersecção) / Area(União)     │
                  ├──────────────────────────────────────────────┤
                  │ 3. Diagnóstico Visual em 3 Canais (Canvas)   │
                  │    🟢 Verde: Acertos (Sobreposição precisa)  │
                  │    🔴 Vermelho: Excessos (Fora do glifo)     │
                  │    ⚪ Cinza: Omissões (Faltou cobrir)        │
                  └──────────────────────────────────────────────┘
```

### Isolamento da Gesture Arena (Focus Mode Modal — `BUG-10`)
Para evitar que gestos verticais do pincel concorram com o scroll da página no Flutter (`BUG-10`), a grade na aba Caligrafia opera como **prévia passiva**, e o desenho interativo ocorre dentro de um modal ampliado (`ft.AlertDialog`) sem ancestrais roláveis (nunca alterando `Column.scroll = None` dinamicamente durante gestos). Enquanto a UI global utiliza **Pretendard**, toda a caligrafia e avaliação utilizam **Kyobo Handwriting 2025**.

---

## 5. Estrutura de Código e Componentes

| Arquivo | Responsabilidade |
| :--- | :--- |
| [`src/jamo_utils.py`](../../src/jamo_utils.py) | Decomposição aritmética Unicode KS X 1001, classificação geométrica de blocos e carregamento do catálogo de 획순 (51 jamo). |
| [`src/components/calligraphy_widget.py`](../../src/components/calligraphy_widget.py) | `CalligraphyWidget`: grade 원고지, ghost layer vetorial Kyobo 2025 (escala `0.68`), motor IoU tolerante `48×48`, telemetria viva e overlay diagnóstico no topo da tinta. |
| [`src/components/wongoji_multi_cell_widget.py`](../../src/components/wongoji_multi_cell_widget.py) | `WongojiMultiCellWidget`: fita de visão geral + célula ativa `210×210px` para palavras/frases no Quiz Engine com *띄어쓰기* (`␣`) e submissão via `"✅ Terminei"`. |
| [`assets/fonts/KyoboHandwriting2025lyb.otf`](../../assets/fonts/KyoboHandwriting2025lyb.otf) | Fonte oficial de caligrafia coreana usada como modelo de referência e rasterização no Wongoji Lab. |
| [`tests/test_jamo_utils.py`](../../tests/test_jamo_utils.py) | 24 testes de decomposição, composição, catálogo de stroke order (51 jamo) e projeção espacial na célula. |
| [`tests/test_calligraphy_widget.py`](../../tests/test_calligraphy_widget.py) | 18 testes cobrindo IoU tolerante, overlay diagnóstico, tipografia Kyobo e ciclo de vida do widget. |
| [`tests/test_quiz_calligraphy.py`](../../tests/test_quiz_calligraphy.py) | 13 testes cobrindo contrato fail-closed de `QuizQuestion`, multi-célula e fluxo de submissão no quiz. |
