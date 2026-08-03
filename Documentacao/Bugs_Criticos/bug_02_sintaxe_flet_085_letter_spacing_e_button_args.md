# BUG-02: Quebra de Sintaxe no Flet 0.85+ (`letter_spacing` e `text=` em Buttons)

- **Severidade**: 🟠 Alta
- **Módulo**: `src/views/ui_test_view.py` / `src/views/home_view.py`
- **Componente**: `ft.Text` / `ft.ElevatedButton` / `ft.OutlinedButton`

---

## 1. Descrição do Problema

Durante a atualização e execução do aplicativo em Flet 0.85+, o console registrou erros fatais de inicialização de componentes:
```python
TypeError: Text.__init__() got an unexpected keyword argument 'letter_spacing'
TypeError: Button.__init__() got an unexpected keyword argument 'text'
```
As views falhavam em renderizar, interrompendo a navegação da aplicação.

---

## 2. Causa Raiz Técnica

O Flet 0.85 passou por uma refatoração em suas definições de API Python para alinhar os construtores de componentes aos padrões nativos do Flutter:

1. **`letter_spacing`**: A propriedade deixou de existir como parâmetro kwarg direto no construtor `ft.Text(...)` e passou a exigir a estrutura de classe de estilo `style=ft.TextStyle(...)`.
2. **`text=` em Botões**: Em botões como `ft.ElevatedButton` e `ft.OutlinedButton`, a propriedade `text=` foi descontinuada em favor do primeiro argumento posicional `("Texto")` ou da propriedade `content=ft.Text(...)`.

---

## 3. Solução Aplicada

### Código Antes (Quebrado no Flet 0.85+):
```python
# Text com letter_spacing direto (ERRADO)
ft.Text("세종학당", size=20, letter_spacing=2)

# ElevatedButton com argumento nomeado text= (ERRADO)
ft.ElevatedButton(text="Confirmar Resposta", icon=ft.Icons.CHECK)
```

### Código Depois (Corrigido):
```python
# Text utilizando ft.TextStyle (CORRETO)
ft.Text(
    "세종학당",
    size=20,
    style=ft.TextStyle(letter_spacing=2)
)

# ElevatedButton utilizando argumento posicional (CORRETO)
ft.ElevatedButton(
    "Confirmar Resposta",
    icon=ft.Icons.CHECK,
    bgcolor=colors["primary"]
)
```

---

## 4. Regra Preventiva

> [!TIP]
> Em atualizações do Flet, sempre utilize `style=ft.TextStyle(...)` para modificar tipografia de `ft.Text` e passe o texto de botões como primeiro parâmetro posicional `ft.ElevatedButton("Texto", ...)`.
