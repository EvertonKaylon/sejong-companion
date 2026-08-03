# BUG-07: Renderização de Tofu (Caixas Vazias) em Hangul por Fallback de Fonte

- **Severidade**: 🟠 Alta
- **Módulo**: `src/theme.py` / Font Engine
- **Componente**: Tipografia Bilíngue (Hangul + Latim)

---

## 1. Descrição do Problema

Ao tentar definir a fonte latina `Inter` como `font_family` padrão do aplicativo nas configurações globais do `ft.Theme()`, os textos contendo caracteres em alfabeto coreano (Hangul) passaram a ser exibidos como retângulos brancos vazios ("tofu" `□□□□`), impossibilitando a leitura do aplicativo educacional.

---

## 2. Causa Raiz Técnica

O motor Flutter (usado por baixo do Flet) renderiza textos em Canvas. Quando uma fonte primária é definida no `Theme(font_family="...")`:

1. **Ausência da Tabela CJK**: Fontes 100% latinas como `Inter` não contêm os glifos Unicode dos blocos Hangul (U+AC00 a U+D7A3).
2. **Sem Fallback Automático Multimídia**: No ambiente Web/CanvasKit, o Flutter não realiza busca automática por fontes do sistema para preencher glifos faltantes se a fonte padrão não cobrir a tabela de caracteres necessária.

---

## 3. Solução Aplicada

Adotamos a fonte unificada **Pretendard** (e **Noto Sans KR** como alternativa), que são especificamente projetadas para cobrir tanto o alfabeto latino quanto todo o bloco Unicode CJK (Korean Hangul) em uma única família de fontes.

### Código Antes (Causava Tofu no Coreano):
```python
# Definir Inter como fonte global quebrava o Hangul sem fallback
page.theme = ft.Theme(font_family="Inter")
```

### Código Depois (Suporte Total Bilíngue):
```python
# Registra PretendardVariable.ttf no mapa de fontes
page.fonts = {
    "Pretendard": "fonts/PretendardVariable.ttf",
    "Seollip-che": "fonts/establish_retrosans.ttf",
}

# Define Pretendard (CJK + Latim) como fonte primária global
page.theme = ft.Theme(
    font_family="Pretendard",
    color_scheme_seed=Colors.PRIMARY
)
```

---

## 4. Regra Preventiva

> [!CAUTION]
> Nunca defina uma fonte exclusivamente latina como `font_family` global do tema de um aplicativo bilíngue coreano. Utilize fontes unificadas como **Pretendard** ou **Noto Sans KR** como padrão global, aplicando fontes customizadas apenas via `font_family` explícito em `ft.Text(...)`.
