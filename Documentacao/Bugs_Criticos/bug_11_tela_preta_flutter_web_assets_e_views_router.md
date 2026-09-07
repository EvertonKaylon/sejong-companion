# BUG-11: Tela Preta no Flutter Web por Resolução Relativa de Imagens (`/`) e Esvaziamento de Views no Router

| Metadado | Detalhe |
| :--- | :--- |
| **ID do Bug** | `BUG-11` |
| **Severidade** | 🔴 Crítica (Bloqueador de Inicialização e Renderização Web) |
| **Componentes Afetados** | `Router` (`src/router.py`), `splash_view` (`src/views/splash_view.py`), `home_view` (`src/views/home_view.py`), `onboarding_view` (`src/views/onboarding_view.py`) |
| **Data de Resolução** | 2026-09-07 |
| **Branch** | `feature/branding` |
| **Testes Automatizados** | `tests/test_router.py`, `tests/test_views_rendering.py` (213 testes 100% aprovados) |

---

## 1. Descrição Sintomática

Ao executar o aplicativo no navegador via `python main.py --browser`, a janela do browser abria e permanecia em uma tela completamente preta (ou na cor de fundo `#02060F` do Canvas), sem renderizar o logotipo, os textos de boas-vindas ou transitar para a tela principal (`/home` ou `/onboarding`).

A anomalia manifestava-se especialmente após erros não tratados no handler de rotas do Flet (`on_route_change`), em que o processo servidor permanecia em execução em segundo plano, mas qualquer recarregamento subsequente (F5) resultava em tela vazia contínua.

---

## 2. Causa Raiz Técnica

A investigação e testes automatizados identificaram quatro fatores interligados:

### A. Resolução de Caminhos Relativos no Flutter Web StaticFiles
No Flet Web, o servidor FastAPI mapeia `assets_dir="assets"` na raiz `/`. Ao declarar controles de imagem com caminhos relativos sem barra inicial (ex: `src="branding/app_icon_512.png"`), o navegador tenta resolver o recurso em relação à rota ativa atual. Quando a rota é `/splash`, a requisição emitida é:
`http://127.0.0.1:8554/splash/branding/app_icon_512.png` -> **HTTP 404 Not Found**.
No motor CanvasKit do Flutter, falhas críticas de decodificação de imagem em componentes-raiz podem quebrar o pipeline de layout. Com o prefixo `/` (`src="/branding/app_icon_512.png"`), a requisição é direcionada a `http://127.0.0.1:8554/branding/app_icon_512.png` -> **HTTP 200 OK**.

### B. Esvaziamento Prematuro de `page.views` no Router
No arquivo `src/router.py`, o método `route_change` realizava `self.page.views.clear()` **antes** de chamar o construtor da view (`self.routes[base_route](self.page)`). Se o construtor disparasse qualquer exceção (como o erro de sintaxe `AttributeError: module 'flet' has no attribute 'ImageFit'`), a execução era interrompida antes do `views.append(view)`. Consequentemente, `self.page.views` ficava com 0 elementos. No Flutter Engine, uma lista vazia de views exibe a tela de canvas preta sem conteúdo.

### C. Bloqueio Indefinido no Bridge Async de `SharedPreferences`
Em `splash_view.py`, uma nova instância `sp = ft.SharedPreferences()` era criada dentro da task assíncrona `prewarm_and_redirect` e adicionada a `page.services`. Em Flet 0.85+, a chamada `await sp.get(...)` envia uma mensagem ao runtime client via `Session.invoke_method` com `timeout=None`. Se o controle não estivesse totalmente sincronizado no cliente Flutter, a Promise aguardava eternamente (`evt.wait()`), bloqueando o `await asyncio.sleep(1.2)` e impedindo que `page.router.navigate_to(next_route)` fosse executado.

### D. Formatação Incorreta de Opacidade Hex (`#AARRGGBB` vs `#RRGGBBAA`)
Concatenações de sufixo alfa em hexadecimais (ex: `f"{colors['primary']}12"`) produziam valores como `#8B4DFF12`. O Flutter Engine interpreta cores de 8 dígitos exclusivamente no formato nativo `#AARRGGBB` (onde os primeiros dois dígitos são o canal Alfa). Isso corrompia as cores primárias em tons esverdeados/cianuras imprevistos. A solução canônica do Flet é o uso de `ft.Colors.with_opacity(0.12, colors['primary'])`.

---

## 3. Soluções e Código: Antes vs. Depois

### A. Roteamento Defensivo contra Esvaziamento de Views (`src/router.py`)

#### Antes (Esvaziamento prematuro):
```python
# ❌ Se a construção da view falhar, page.views fica vazia -> Tela Preta
self.page.views.clear()

if base_route in self.routes:
    view = self.routes[base_route](self.page)
    self.page.views.append(view)
```

#### Depois (Transição atômica e fallback de emergência):
```python
# ✅ Constrói a view primeiro; só limpa se a instanciação tiver sucesso
target_builder = self.routes.get(base_route) or self.routes.get("/splash") or self.routes.get("/home")
view = None
if target_builder:
    try:
        view = target_builder(self.page)
    except Exception as ex:
        print(f"[Router] Erro ao construir view '{base_route}': {ex}")
        fallback_builder = self.routes.get("/home") or self.routes.get("/splash")
        if fallback_builder and fallback_builder != target_builder:
            try:
                view = fallback_builder(self.page)
            except Exception:
                pass

if view is not None:
    self.page.views.clear()
    self.page.views.append(view)
elif not self.page.views:
    # Fallback defensivo: garante que views nunca fique vazia
    self.page.views.append(
        ft.View(
            route=base_route,
            controls=[ft.ProgressRing(width=32, height=32)],
            bgcolor="#02060F",
        )
    )
```

---

### B. Caminhos Absolutos de Assets e Opacidade Canônica (`src/views/splash_view.py`)

#### Antes:
```python
# ❌ Caminho relativo causa 404 em rotas aninhadas e hex causa distorção cromática
ft.Image(
    src="branding/app_icon_512.png",
    fit=ft.BoxFit.CONTAIN,
)
bgcolor=f"{colors['primary']}12",
border=ft.Border.all(1.5, f"{colors['primary']}40"),
```

#### Depois:
```python
# ✅ Caminho absoluto com / e opacidade padronizada via ft.Colors.with_opacity
ft.Image(
    src="/branding/app_icon_512.png",
    fit=ft.BoxFit.CONTAIN,
)
bgcolor=ft.Colors.with_opacity(0.12, colors["primary"]),
border=ft.Border.all(1.5, ft.Colors.with_opacity(0.25, colors["primary"])),
```

---

### C. Timeout Estrito em Checagens de Persistência no Splash

#### Antes:
```python
# ❌ Chamada sem timeout pode suspender indefinidamente se o controle não responder
sp = ft.SharedPreferences()
saved_id = await sp.get("saebom_student_id")
```

#### Depois:
```python
# ✅ Uso prioritário de StudentIdentity e ProgressService com timeout defensivo de 0.8s
from ..services import StudentIdentity, ProgressService
existing_id = StudentIdentity.get_student_id(page)
ps = ProgressService(page)
saved_name = ps.get_student_name()

if existing_id and not existing_id.startswith("student_") and saved_name and saved_name != "Aluno Anônimo":
    page._sejong_student_id = existing_id
    page._sejong_student_name = saved_name
    next_route = "/home"
else:
    try:
        sp = ft.SharedPreferences()
        async def _safe_get(k: str):
            try:
                return await asyncio.wait_for(sp.get(k), timeout=0.8)
            except Exception:
                return None
        # Consulta segura com timeout
        saved_id = await _safe_get("saebom_student_id") or await _safe_get("sejong_student_id")
        ...
```

---

## 4. Regras Preventivas

1. **Caminhos de Assets Sempre Absolutos:** Imagens e ícones em `ft.Image(src=...)` DEVEM sempre começar com barra inicial (`/branding/...` ou `/icons/...`) para que o servidor estático web nunca tente resolvê-los relativamente ao segmento de rota atual.
2. **Nunca Limpar `page.views` Antes de Garantir a Próxima View:** Em arquiteturas de roteamento Flet/Flutter, a substituição da view deve ser atômica. Se a construção falhar, mantenha a view anterior ou apresente uma view de fallback.
3. **Timeouts Obrigatórios em Métodos de Serviços Flet:** Toda chamada assíncrona a serviços Flet (`SharedPreferences.get`, `invoke_method`, etc.) executada no fluxo principal de carregamento de view DEVE possuir `asyncio.wait_for(..., timeout=...)` para evitar que a interface fique congelada caso o runtime cliente não envie confirmação.
4. **Opacidade via `ft.Colors.with_opacity`:** Não concatenar números hexadecimais no final de strings de cor; usar sempre a função canônica `ft.Colors.with_opacity(opacity, color)`.
