# BUG-03: Inversão de Cores no Parser HEX de 8 Dígitos (`#AARRGGBB` vs `#RRGGBBAA`)

- **Severidade**: 🟡 Média
- **Módulo**: `src/views/ui_test_view.py` / `src/theme.py`
- **Componente**: Container de Opções do Quiz (`bgcolor`)

---

## 1. Descrição do Problema

Ao testar a resposta do quiz no laboratório UI/UX, ao selecionar uma opção e confirmar:
- A alternativa correta (que deveria ser verde `#19BD56`) renderizou com fundo **vermelho/castanho**.
- A alternativa incorreta (que deveria ser carmesim `#C50337`) renderizou com fundo **verde**.
- Tentativas de usar `rgba(25, 189, 86, 0.15)` fizeram o fundo desaparecer completamente (ficou 100% transparente).

---

## 2. Causa Raiz Técnica

Existem duas causas técnicas combinadas neste comportamento do motor Flutter/Flet:

1. **Parser de Hexadecimal de 8 Dígitos (`#AARRGGBB`)**:
   O Flutter lê a opacidade/alpha nos **dois primeiros dígitos** (`#AARRGGBB`), e não nos dois últimos como em alguns pré-processadores CSS.
   Ao escrever `f"{Colors.CORRECT}15"` (`#19BD5615`):
   - `AA = 19` (Opacidade de 10%)
   - `RR = BD` (Vermelho = 189 -> Vermelho Castanho)
   - `GG = 56` (Verde = 86)
   - `BB = 15` (Azul = 21)
   Isso deslocou todos os bytes de cor, transformando o verde em vermelho.

2. **Parser de String `rgba()` no Flet Web Client**:
   A string `rgba(25, 189, 86, 0.15)` contendo valor decimal (`0.15`) falhou ao ser serializada pelo cliente web CanvasKit do Flutter, resultando no valor padrão fallback `0x00000000` (transparente).

---

## 3. Solução Aplicada

Calculamos o valor em hexadecimal exato para os dois primeiros dígitos de Alpha (`15% de 255 = 38 = 0x26`) e aplicamos a notação nativa de 8 dígitos **`#AARRGGBB`**:

### Código Antes (Invertido / Transparente):
```python
# Hexadecimal com transparência no final (INVERTIA AS CORES)
bg_color = f"{Colors.CORRECT}15"  # Virava #19BD5615 (Red = BD)

# String rgba com decimal (FICAVA TRANSPARENTE)
bg_color = "rgba(25, 189, 86, 0.15)"
```

### Código Depois (Correto em HEX Nativo):
```python
# Verde #19BD56 com 15% opacidade (#26 Alpha no início)
bg_correct = "#2619BD56"

# Carmesim #C50337 com 15% opacidade (#26 Alpha no início)
bg_incorrect = "#26C50337"

# Azul #0356C5 com 10% opacidade (#19 Alpha no início)
bg_selected = "#190356C5"
```

---

## 4. Regra Preventiva

> [!WARNING]
> Em Flet/Flutter, a transparência em Hexadecimal de 8 dígitos deve SEMPRE vir no início: `#AARRGGBB`.
> `0x26` = 15% opacidade, `0x33` = 20% opacidade, `0x80` = 50% opacidade.
