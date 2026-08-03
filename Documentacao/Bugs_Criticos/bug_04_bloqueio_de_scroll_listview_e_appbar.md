# BUG-04: Bloqueio de Rolagem Vertical (`ft.ListView` dentro de `ft.View`)

- **Severidade**: 🟡 Média
- **Módulo**: `src/views/ui_test_view.py`
- **Componente**: `ft.View` / `ft.ListView`

---

## 1. Descrição do Problema

Na visualização do Laboratório UI/UX (`/ui_test`), a página ficava travada verticalmente: a tela exibia apenas o primeiro card e a primeira alternativa do simulador de quiz, sem responder aos gestos de rolagem do mouse ou touch para acessar os conteúdos inferiores.

---

## 2. Causa Raiz Técnica

O Flet exige que controles roláveis dentro de uma `ft.View` tenham sua expansão vertical explicitamente declarada (`expand=True`) ou que a própria `ft.View` assuma o controle de rolagem.

1. **Containers Aninhados sem Expand**: A view foi montada com `ft.View(controls=[app_bar, content_list])`, onde `content_list` era um `ft.ListView`. Sem `expand=True`, o `ListView` colapsou sua altura para o menor tamanho possível e não expandiu até o rodapé.
2. **AppBar dentro da Lista**: Colocar a `AppBar` dentro do array `controls` em vez da propriedade dedicada `appbar=app_bar` alterou o cálculo de layout do viewport.

---

## 3. Solução Aplicada

Alinhamos a estrutura de views ao padrão nativo do projeto (usado em `home_view.py` e `hangul_view.py`):

### Código Antes (Travado / Colapsado):
```python
content_list = ft.ListView(
    controls=[logo, card1, card2, quiz],
    padding=16
)

return ft.View(
    route="/ui_test",
    controls=[app_bar, content_list], # AppBar como controle comum
    bgcolor=colors["bg"]
)
```

### Código Depois (Rolagem Nativa Fluida):
```python
return ft.View(
    route="/ui_test",
    appbar=app_bar,                      # Propriedade nativa da AppBar
    controls=[logo, card1, card2, quiz], # Controles dispostos diretamente
    scroll=ft.ScrollMode.AUTO,           # Rolagem gerenciada pela View
    bgcolor=colors["bg"],
    padding=16
)
```

---

## 4. Regra Preventiva

> [!TIP]
> Em telas principais de visualização, utilize `scroll=ft.ScrollMode.AUTO` e `appbar=app_bar` diretamente na `ft.View`. Evite aninhar `ft.ListView` sem `expand=True` dentro de `controls`.
