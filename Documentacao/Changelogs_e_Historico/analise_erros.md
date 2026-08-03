# 🔍 Catálogo de Erros — Sejong Companion

Análise completa do projeto. Flet instalado: **v0.85.3**. Todos os arquivos `.py` e `.json` foram revisados.

---

## Resumo Executivo

| Severidade | Quantidade | Impacto |
|:---:|:---:|:---|
| 🔴 Crítico | 3 | App não funciona / crash em tempo de execução |
| 🟠 Alto | 4 | Funcionalidade quebrada ou comportamento incorreto |
| 🟡 Médio | 4 | Problemas de qualidade / debt técnico |
| 🔵 Baixo | 3 | Boas práticas / otimização |
| **Total** | **14** | |

---

## 🔴 Erros Críticos (App quebra)

### C1 — `ft.app()` está deprecado desde Flet 0.80

> [!CAUTION]
> `ft.app()` foi deprecado na v0.80.0 e substituído por `ft.run()`. A chamada funciona por enquanto (wrapper de compatibilidade), mas emite um warning e pode ser removida a qualquer momento.

**Arquivo:** [main.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/main.py#L36)
```python
# ❌ Atual (deprecado)
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8554)

# ✅ Correto
ft.run(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8554)
```

---

### C2 — `page.snack_bar` não existe no Flet 0.85

> [!CAUTION]
> O atributo `page.snack_bar` foi removido. No Flet 0.85, `SnackBar` herda de `DialogControl` e deve ser exibido via `page.show_dialog()`. O código atual lança `AttributeError` quando o usuário tenta clicar numa unidade bloqueada ou no botão de áudio.

**Arquivos afetados:**

#### [home_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/home_view.py#L111-L116) (linhas 111-116)
```python
# ❌ Atual — AttributeError
page.snack_bar = ft.SnackBar(
    content=ft.Text("🔒 Complete as unidades anteriores..."),
    bgcolor=colors["secondary"]
)
page.snack_bar.open = True
page.update()

# ✅ Correto (Flet 0.85+)
snack = ft.SnackBar(
    content=ft.Text("🔒 Complete as unidades anteriores..."),
    bgcolor=colors["secondary"],
    open=True,
)
page.show_dialog(snack)
```

#### [vocab_card.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/vocab_card.py#L107-L113) (linhas 107-113)
```python
# ❌ Mesma API inexistente
page.snack_bar = ft.SnackBar(...)
page.snack_bar.open = True
page.update()
```

---

### C3 — `ft.Icons.DICTIONARY_ROUNDED` não existe

> [!CAUTION]
> Esse ícone não existe no Flet 0.85. Causa `AttributeError` ao abrir a view de lição, impedindo completamente a renderização da tela.

**Arquivo:** [lesson_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/lesson_view.py#L88) (linha 88)
```python
# ❌ Não existe
icon=ft.Icons.DICTIONARY_ROUNDED

# ✅ Alternativas válidas
icon=ft.Icons.BOOK_ROUNDED           # Livro genérico
icon=ft.Icons.TRANSLATE_ROUNDED      # Tradução
icon=ft.Icons.LOCAL_LIBRARY_ROUNDED  # Biblioteca
icon=ft.Icons.ABC_ROUNDED            # Letras
```

---

## 🟠 Erros de Alta Severidade (Comportamento incorreto)

### A1 — Checagem `page.theme_mode is None` nunca é `True`

**Arquivo:** [main.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/main.py#L12-L13) (linhas 12-13)

No Flet 0.85, `page.theme_mode` tem valor padrão `ThemeMode.SYSTEM`, nunca `None`. O bloco condicional **nunca executa**, e o tema fica como `SYSTEM` ao invés do `LIGHT` pretendido.

```python
# ❌ Atual — condição morta
if page.theme_mode is None:
    page.theme_mode = ft.ThemeMode.LIGHT

# ✅ Correto
page.theme_mode = ft.ThemeMode.LIGHT
```

---

### A2 — Typo no JSON: "안na" ao invés de "안나"

**Arquivo:** [unit_01.json](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/data/units/unit_01.json#L9) (linha 9)

O campo `example_kr` do vocabulário "안녕하세요" contém texto em script latino ("na") misturado com Hangul:

```json
// ❌ Atual — "na" em latim no meio do coreano
"example_kr": "안녕하세요? 저는 안na예요."

// ✅ Correto — todo em Hangul
"example_kr": "안녕하세요? 저는 안나예요."
```

---

### A3 — Lógica de progresso inconsistente (escala 0-1 vs 0-100)

**Arquivo:** [services.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/services.py#L62) (linha 62)

O código verifica `progress >= 1.0 or progress >= 100.0`, mas todo o resto do sistema usa escala **0.0 a 1.0**. A condição `>= 100.0` nunca será verdadeira com a escala atual, e se alguém passasse 100 acidentalmente, `>= 1.0` já capturaria. A condição `or` é redundante.

```python
# ❌ Atual — condição redundante
if progress >= 1.0 or progress >= 100.0:

# ✅ Correto — escala única
if progress >= 1.0:
```

---

### A4 — `import time` no handler de evento sem uso real

**Arquivo:** [vocab_card.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/vocab_card.py#L116) (linha 116)

`import time` aparece no meio do método `play_audio_animation` mas **nunca é usado** (não há `time.sleep()`). O import é código morto. Além disso, se fosse usado com `time.sleep()`, bloquearia a thread principal do Flet.

```python
# ❌ Import morto
import time  # Nunca usado

# ✅ Remover a linha
# (sem import desnecessário)
```

---

## 🟡 Erros de Média Severidade (Qualidade)

### M1 — `handle_unit_click` definida dentro do loop sem closure adequada

**Arquivo:** [home_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/home_view.py#L109) (linhas 106-122)

A função `handle_unit_click` é redefinida a cada iteração do loop `for unit in curriculum`. Embora `create_click_handler` crie uma closure corretamente para `u_id` e `unlocked`, a função `handle_unit_click` em si é redefinida desnecessariamente em cada iteração (mesmo padrão, diferentes referências).

O padrão funcional mais limpo seria inline direto no `create_click_handler`:

```python
# ✅ Mais limpo — tudo no closure
def create_click_handler(u_id=unit.id, unlocked=is_unlocked):
    def handler(e):
        if not unlocked:
            # mostrar snackbar...
            return
        if u_id == "unit_intro":
            page.router.navigate_to("/hangul", u_id)
        else:
            page.router.navigate_to("/lesson", u_id)
    return handler
```

---

### M2 — Atributo dinâmico `page.router` não tipado

**Arquivo:** [main.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/main.py#L22) (linha 22)

```python
page.router = router  # Monkey-patching sem type safety
```

Funciona em runtime, mas:
- Nenhuma IDE dará autocompleção para `page.router`
- Se alguém renomear o atributo, o erro só aparece em runtime
- Dificulta manutenção futura

**Sugestão:** Usar `page.data` (atributo oficial do Page para dados customizados) ou criar uma variável de módulo.

---

### M3 — `ProgressService._store` é um class-level mutable default

**Arquivo:** [services.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/services.py#L49) (linha 49)

```python
class ProgressService:
    _store: dict = {}  # Compartilhado entre TODAS as instâncias
```

Isso é intencional (singleton pattern), mas é uma armadilha conhecida em Python. Se o app for usado por múltiplos usuários simultâneos (web mode), **todos compartilham o mesmo progresso**. Para o Beta 0.1 (usuário único) funciona, mas é um risco real para produção.

---

### M4 — `callable` em minúsculo no type hint

**Arquivo:** [quiz_widget.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/quiz_widget.py#L5) (linha 5)

```python
# ❌ Atual — builtin function, não type hint
def __init__(self, question_data, is_dark: bool, on_next: callable, on_answer: callable):

# ✅ Correto — type hint do typing
from typing import Callable, Optional
def __init__(self, question_data, is_dark: bool, on_next: Callable, on_answer: Callable):
```

`callable` em minúsculo é a built-in function `callable()` (verifica se algo é chamável). O type hint correto é `Callable` do módulo `typing` ou `collections.abc`.

---

## 🔵 Erros de Baixa Severidade (Boas práticas)

### B1 — Falta de `__init__.py` nos pacotes

**Diretórios afetados:**
- `src/`
- `src/components/`
- `src/views/`

No Python 3.3+, isso funciona via "namespace packages" implícitos, por isso os imports funcionam. Porém, é uma boa prática incluir `__init__.py` para:
- Compatibilidade explícita com ferramentas (mypy, pytest, empacotadores)
- Deixar claro que são pacotes, não diretórios aleatórios

---

### B2 — `SnackBar.duration` recebe int mas espera milissegundos

**Arquivo:** [vocab_card.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/components/vocab_card.py#L110)

```python
duration=1500  # Funciona, mas considerar verificar a unidade (ms vs segundos)
```

O valor `1500` funciona corretamente (são milissegundos), mas como o `SnackBar` é mostrado da forma errada (via `page.snack_bar` inexistente — ver C2), esse detalhe é irrelevante até que o C2 seja corrigido.

---

### B3 — Sem tratamento de erro para `page.router` nas views

Todas as views acessam `page.router.navigate_to(...)` e `page.router.current_unit_id` sem nenhuma verificação de que `page.router` existe. Se alguma view for renderizada antes de `main()` configurar o router, haverá `AttributeError`.

**Arquivos afetados:** Todas as views ([splash_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/splash_view.py#L51), [home_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/home_view.py#L15), [hangul_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/hangul_view.py#L27), [lesson_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/lesson_view.py#L10), [quiz_view.py](file:///c:/Users/Pichau/Documents/app%20sejong%20companion/src/views/quiz_view.py#L11))

---

## 📋 Checklist de Correção (por prioridade)

| # | Severidade | Erro | Arquivo | Ação |
|:---:|:---:|:---|:---|:---|
| C1 | 🔴 | `ft.app()` deprecado | main.py:36 | Trocar por `ft.run()` |
| C2 | 🔴 | `page.snack_bar` inexistente | home_view, vocab_card | Usar `page.show_dialog()` |
| C3 | 🔴 | `DICTIONARY_ROUNDED` inexistente | lesson_view:88 | Usar `BOOK_ROUNDED` |
| A1 | 🟠 | `theme_mode is None` morto | main.py:12 | Setar direto |
| A2 | 🟠 | Typo "안na" | unit_01.json:9 | Corrigir para "안나" |
| A3 | 🟠 | Progresso redundante | services.py:62 | Simplificar condição |
| A4 | 🟠 | `import time` morto | vocab_card.py:116 | Remover |
| M1 | 🟡 | Closure no loop | home_view.py:109 | Refatorar |
| M2 | 🟡 | `page.router` monkey-patch | main.py:22 | Documentar ou usar `page.data` |
| M3 | 🟡 | Mutable class default | services.py:49 | OK para Beta, documentar |
| M4 | 🟡 | `callable` minúsculo | quiz_widget.py:5 | Usar `Callable` |
| B1 | 🔵 | Falta `__init__.py` | src/ | Criar arquivos |
| B2 | 🔵 | SnackBar duration | vocab_card.py:110 | Depende de C2 |
| B3 | 🔵 | Sem guard para router | Todas as views | Adicionar verificação |
