# Desenvolvimento Multiplataforma em Python

**Conceito Relacionado:** [[Arquitetura_Flet_e_Flutter_Engine]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[analise_stack_multiplataforma]] | [[implementation_plan]]  
**Bugs Catalogados:** [[bug_06_bind_windows_flet_server_ip]]  

---

## 1. 💻 O Paradigma Multiplataforma Unificado

O desenvolvimento moderno de aplicações educacionais exige presença contínua nos dispositivos utilizados pelos estudantes: navegadores web de computadores, smartphones Android e aparelhos iOS.

Em vez de manter três projetos de código separados em linguagens distintas (Swift/Objective-C para iOS, Kotlin/Java para Android e TypeScript/React para Web), o **Sejong Companion (세종학당 컴패니언)** adota o ecossistema **Python + Flet**, no qual **uma única base de código em Python** gera as três distribuições nativas.

```
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

- **Comportamento do Windows Sockets**: Definir `FLET_SERVER_IP = "0.0.0.0"` instrui a abertura do navegador no endereço `http://0.0.0.0:8554`. No sistema operacional Windows, o endereço `0.0.0.0` não é um destino de loopback válido, resultando no erro `ERR_ADDRESS_INVALID`. Tentativas com wildcard `*` falham no `getaddrinfo()`.
- **Solução Nativa**: Fixar o endereço de desenvolvimento em `127.0.0.1` no [main.py](file:///c:/Users/Pichau/Documents/sejong_companion/main.py) garante inicialização confiável e rápida. Para testes no dispositivo móvel na mesma rede Wi-Fi, o endereço pode ser chaveado com acesso via IP da máquina.
- Veja o relatório completo em [[bug_06_bind_windows_flet_server_ip]].

### B. Otimização para Hardware de Desenvolvimento e Dispositivos de Entrada
O aplicativo foi projetado para rodar com fluidez tanto em smartphones de entrada quanto em máquinas desktop de desenvolvimento modestas (como o hardware de desenvolvimento atual: Intel Core i7-3770 / 8GB RAM DDR3 / GPU dedicada GT 730).

- **Estratégia de Performance**: Substituição de efeitos pesados de pós-processamento de GPU (como blurs pesados de `BackdropFilter`) por sombras estáticas tokenizadas (`Styles.CARD_SHADOW`) e bordas suaves.

---

## 3. 🛠️ Arquitetura do Roteador Global (`src/router.py`)

A navegação multiplataforma é gerenciada por um roteador personalizado desacoplado da plataforma:

```python
# src/router.py — Roteador Global Desacoplado

import flet as ft
from typing import Dict, Callable

class Router:
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, Callable[[ft.Page], ft.View]] = {}
        self.current_unit_id: str = "unit_intro"
        
        # Eventos nativos do histórico da janela / botão voltar do Android
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop

    def register_route(self, route_name: str, view_builder: Callable[[ft.Page], ft.View]):
        self.routes[route_name] = view_builder

    def route_change(self, e: ft.RouteChangeEvent):
        self.page.views.clear()
        base_route = e.route.split("?")[0]
        
        if base_route in self.routes:
            self.page.views.append(self.routes[base_route](self.page))
        self.page.update()

    def navigate_to(self, route_name: str, unit_id: str = None):
        if unit_id:
            self.current_unit_id = unit_id
        self.page.go(route_name)
```

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- ⚡ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
- ⚙️ Análise de Stack Multiplataforma: [[analise_stack_multiplataforma]]
- 🚨 Bug do Bind no Windows: [[bug_06_bind_windows_flet_server_ip]]
