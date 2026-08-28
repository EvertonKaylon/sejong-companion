# ✍️ Reconhecimento Tátil e Caligrafia Hangul (원고지)

**Status:** VIGENTE / ARQUITETURA IMPLEMENTADA  
**Data de Criação:** 2026-08-28  
**Componentes Relacionados:** `CalligraphyWidget` (`src/components/calligraphy_widget.py`), `jamo_utils` (`src/jamo_utils.py`), `assets/stroke_order/jamo_strokes.json`  
**Documentos Vinculados:** [[Motor_Adaptativo_e_Learning_Engine]] | [[Neuropedagogia_e_Gamificacao]] | [[didactic_neuroscience_korean_ptbr]] | [[CHANGELOG]]

---

## 1. Fundamentos da Escrita Hangul e o Princípio Composicional

Diferente de sistemas alfabéticos lineares (como o alfabeto latino) ou logográficos holísticos (como os Hanja chineses), o **Hangul (한글)** opera como um sistema **alfabético-silábico composicional**, criado pelo Rei Sejong em 1446 (*Hunminjeongeum*).

Cada bloco silábico visível é estruturado deterministicamente a partir de subunidades fonéticas (**자모 — Jamo**):

```
┌────────────────────────────────────────────────────────┐
│             ANATOMIA DO BLOCO SILÁBICO HANGUL          │
├────────────────────────────┬───────────────────────────┤
│ 1. 초성 (Choseong)        │ Consoante Inicial (19)    │
│ 2. 중성 (Jungseong)       │ Vogal Medial (21)         │
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

```
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

Na implementação digital do Sejong Companion:
1. **Camada de Fundo (Grid Layer)**: Renderiza as bordas da célula e as linhas pontilhadas da cruz central para orientar a proporção dos quadrantes.
2. **Camada de Modelo (Ghost Layer)**: Projeta o silabograma esperado com opacidade reduzida e indica com um círculo âmbar o ponto de partida do traço ativo.
3. **Camada de Interação (Canvas + GestureDetector)**: Captura as coordenadas do toque do estudante com interpolação contínua a ~60fps.

---

## 3. Neuropedagogia: Memória Motora e Feedback Tátil

Pesquisas em neurociência cognitiva da escrita (Sweller, Ullman) demonstram que o aprendizado de novos alfabetos é potencializado pela formação de **traços de memória procedurais e proprioceptivos** (*motor memory*).

* **Ordem de Traços (획순 - Stroke Order)**: Não é uma convenção meramente estética, mas o algoritmo neuromotor que garante a fluidez, proporção e legibilidade do Hangul (regras fundamentais: *de cima para baixo* e *da esquerda para a direita*).
* **Progressão Pedagógica em 3 Estágios**:
  1. *Fase 1: Tracing Guiado (따라쓰기)* — O modelo fantasma fica visível, com o ponto de início em destaque.
  2. *Fase 2: Prática com Dicas* — O aluno pode ocultar o modelo com o botão de visibilidade e consultar apenas quando tiver dúvida.
  3. *Fase 3: Escrita Livre* — Grade limpa onde o motor valida a escrita de memória.

---

## 4. Arquitetura de Validação: Path Matching vs. OCR

> [!IMPORTANT]
> Para o ensino de escrita em tempo real, **OCR estático (redes neurais baseadas em imagem final) é inadequado**, pois avalia apenas a forma resultante, ignorando se o aluno escreveu na ordem ou direção erradas.

O Sejong Companion utiliza um **Motor de Similaridade de Traços por Path Matching Direcional**:

```
                         PIPELINE DE VALIDAÇÃO DE TRAÇOS
                         
  Entrada do Aluno              Dados de Referência (JSON)
  [(x₀,y₀), (x₁,y₁)...]         [(rx₀,ry₀), (rx₁,ry₁)...]
          │                                │
          ▼                                ▼
  ┌────────────────────────────────────────────────────────┐
  │ 1. Proximidade dos Extremos (Start & End Points)       │
  │    • dist_start ≤ tolerance                            │
  │    • dist_end ≤ tolerance                              │
  ├────────────────────────────────────────────────────────┤
  │ 2. Coerência Direcional (Similaridade de Cosseno)      │
  │    • cos(θ) > -0.2 (rejeita traços no sentido oposto)  │
  ├────────────────────────────────────────────────────────┤
  │ 3. Distância Média Ponto-Segmento (Trajetória)         │
  │    • Projeção ortogonal euclidiana na polilinha        │
  ├────────────────────────────────────────────────────────┤
  │ 4. Score Ponderado & Feedback                          │
  │    • Score = 1.0 - (erro_combinado / tolerância)       │
  │    • Se válido: trava traço em azul (#004C97)          │
  │    • Se inválido: vibra/destaca modelo para correção   │
  └────────────────────────────────────────────────────────┘
```

---

## 5. Estrutura de Código e Componentes

| Arquivo | Responsabilidade |
| :--- | :--- |
| [`src/jamo_utils.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/jamo_utils.py) | Decomposição aritmética Unicode KS X 1001, classificação geométrica de blocos e cálculo de caixas delimitadoras de jamo. |
| [`assets/stroke_order/jamo_strokes.json`](file:///c:/Users/Pichau/Documents/sejong_companion/assets/stroke_order/jamo_strokes.json) | Base de vetores normalizados [0.0, 1.0] dos 40 Jamo básicos (adaptado de *hangeul-stroke-order*, CC BY-SA 4.0). |
| [`src/components/calligraphy_widget.py`](file:///c:/Users/Pichau/Documents/sejong_companion/src/components/calligraphy_widget.py) | Componente visual `CalligraphyWidget` Flet com grade, ghost layer, GestureDetector e feedback em tempo real. |
| [`tests/test_jamo_utils.py`](file:///c:/Users/Pichau/Documents/sejong_companion/tests/test_jamo_utils.py) | 16 testes automatizados validando decomposição, composição e integridade do dataset. |
| [`tests/test_calligraphy_widget.py`](file:///c:/Users/Pichau/Documents/sejong_companion/tests/test_calligraphy_widget.py) | 12 testes automatizados cobrindo similaridade, direcionalidade e ciclo de vida do widget. |
