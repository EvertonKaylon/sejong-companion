# Desenvolvimento Multiplataforma em Python

**Conceito Relacionado:** [[Arquitetura_Flet_e_Flutter_Engine]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[analise_stack_multiplataforma]] | [[implementation_plan]]  
**Bugs Catalogados:** [[bug_06_bind_windows_flet_server_ip]] | [[bug_11_tela_preta_flutter_web_assets_e_views_router]] | [[bug_12_deadlock_pipe_anonimo_windows_playwright_e2e]]  

---

## 1. 💻 O Paradigma Multiplataforma Unificado

O desenvolvimento moderno de aplicações educacionais exige presença contínua nos dispositivos utilizados pelos estudantes: navegadores Web/PWA de computadores, smartphones Android e aparelhos iOS, além de desktop local.

Em vez de manter projetos de código separados em linguagens distintas (Swift para iOS, Kotlin para Android e TypeScript/React para Web), o **Saebom Companion (새봄 컴패니언)** adota o ecossistema **Python + Flet**, no qual **uma única base de código em Python** gera as distribuições nativas.

```text
                      ┌─────────────────────────────────────────┐
                      │    BASE DE CÓDIGO ÚNICA EM PYTHON       │
                      │    (src/views, router.py, main.py)      │
                      └────────────────────┬────────────────────┘
                                           │
         ┌─────────────────────────────────┼─────────────────────────────────┐
         │                                 │                                 │
┌────────▼─────────────────┐   ┌───────────▼─────────────────┐   ┌───────────▼─────────────────┐
│     Web Application      │   │      Android Application    │   │       iOS Application       │
│  (Navegador / CanvasKit) │   │    (APK Nativo / Flutter)   │   │    (Bundle / App Store)      │
│  `ft.AppView.WEB_BROWSER`│   │    `flet build apk`         │   │    `flet build ipa`          │
└──────────────────────────┘   └─────────────────────────────┘   └─────────────────────────────┘
```

---

## 2. ⚙️ Desafios Específicos e Soluções Arquiteturais

### A. Resolução de Binds de Rede no SO Windows (`FLET_SERVER_IP`)
Durante o desenvolvimento local no Windows, o Flet gerencia um servidor HTTP interno e instrui a abertura automática do navegador padrão.

- **Comportamento do Windows Sockets**: Definir `FLET_SERVER_IP = "0.0.0.0"` instrui a abertura do navegador em `http://0.0.0.0:8554`. No Windows, `0.0.0.0` não é destino de loopback válido, resultando em `ERR_ADDRESS_INVALID` ou falhas no `getaddrinfo()`.
- **Solução Nativa**: Fixar o endereço de desenvolvimento local em `127.0.0.1` no [main.py](../../main.py) e reservar `0.0.0.0` apenas para execução em container em nuvem (quando a variável `PORT` está presente no ambiente).
- Veja o relatório completo em [[bug_06_bind_windows_flet_server_ip]].

### B. Otimização de Memória, Performance e Armazenamento Cross-Platform
O aplicativo foi projetado para operar com fluidez tanto em smartphones de entrada quanto em desktops modestos:

- **Tokens Estáticos de Renderização**: Reaproveitamento integral de constantes estáticas em `Styles` e `Tokens` de `src/theme.py` (`Styles.CARD_SHADOW`, `Styles.HOVER_SHADOW`), evitando recriação de objetos `ft.BoxShadow` em loops (`BUG-05`).
- **Isolamento de Armazenamento**: `assets/` (imagens de branding, fontes `Pretendard` e `Kyobo Handwriting 2025`, `silent.wav` e áudio pré-empacotado) permanece estritamente *read-only* no bundle multiplataforma; sessões, telemetria, relatórios, comunicados e cache dinâmico de áudio (`data/cache/audio/`) residem em `data/`.

---

## 3. 🛠️ Arquitetura do Roteador Global (`src/router.py`)

A navegação multiplataforma é gerenciada por um roteador atômico desacoplado de instâncias diretas de `ft.RouteChangeEvent`, preservando histórico real (`view_pop`), deep links Web e fallback de emergência contra tela preta (`BUG-11`):

```python
# src/router.py — Roteador Global Atômico (Resumo Arquitetural)

import flet as ft
from typing import Dict, Callable


class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, Callable[[ft.Page], ft.View]] = {}
        self.current_unit_id: str = "unit_intro"
        self._history: list[str] = []

        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def register_route(self, route_name: str, view_builder: Callable[[ft.Page], ft.View]):
        self.routes[route_name] = view_builder

    def render_route(self, route: str):
        base_route = (route or "/splash").split("?")[0]
        if base_route in ("", "/"):
            base_route = "/splash"

        target_builder = self.routes.get(base_route) or self.routes.get("/splash") or self.routes.get("/home")
        view = None
        if target_builder:
            try:
                view = target_builder(self.page)
            except Exception as ex:
                print(f"[Router] Erro ao construir view '{base_route}': {ex}")

        # Transição atômica: só limpa page.views após construir a nova view com sucesso
        if view is not None:
            self.page.views.clear()
            self.page.views.append(view)
        elif not self.page.views:
            # View de fallback de emergência em Midnight Navy (#02060F)
            self.page.views.append(ft.View(route=base_route, bgcolor="#02060F", controls=[]))

        try:
            self.page.update()
        except Exception:
            pass
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- ⚡ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
- ⚙️ Análise de Stack Multiplataforma: [[analise_stack_multiplataforma]]
- 🚨 Bug do Bind no Windows: [[bug_06_bind_windows_flet_server_ip]]
- 🚨 Tela Preta Web & Router: [[bug_11_tela_preta_flutter_web_assets_e_views_router]]
