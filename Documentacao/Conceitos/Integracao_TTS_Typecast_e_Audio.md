# Integração TTS (Typecast.ai) e Serviço de Áudio

**Conceito Relacionado:** [[Arquitetura_Flet_e_Flutter_Engine]] | [[Neuropedagogia_e_Gamificacao]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[didactic_neuroscience_korean_ptbr]] | [[Plano_UIUX_Flet_Sejong_Companion]]  
**Bugs Catalogados:** [[bug_01_flet_audio_corridas_e_page_services]]  

---

## 1. 🎙️ A Importância da Pronúncia Nativa (Typecast.ai)

O aprendizado da percepção auditiva no idioma coreano (*듣기*) é extremamente sensível a nuances fonéticas (como a tripartição oclusiva de consoantes simples, aspiradas e tensas).

Para garantir áudio cristalino com entonação humana natural, o **Sejong Companion (세종학당 컴패니언)** utiliza vozes TTS geradas via **Typecast.ai**, gravadas e sintetizadas especificamente para o vocabulário das lições do *Sejong Korean 1A*.

---

## 2. ⚡ A Arquitetura do Serviço Singleton (`AudioService`)

Em aplicações Flet 0.85+, gerenciar instâncias de áudio diretamente em views temporárias gera vazamentos de memória e exceções de corrida (*race conditions*) caso o usuário mude de tela enquanto o áudio está tocando.

Para resolver esse problema, o projeto implementa o padrão **Singleton Service** encapsulado em [src/audio_service.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/audio_service.py).

```
 ┌──────────────────────────────────────────────────────────────────┐
 │                     SESSÃO DA PÁGINA (page)                      │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
                                  │ Instanciação Única no Launch
                                  ▼
 ┌──────────────────────────────────────────────────────────────────┐
 │                    `page.audio_service`                          │
 │                (Instância de `AudioService`)                     │
 └────────────────────────────────┬─────────────────────────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          │                                               │
┌─────────▼───────────────────────┐             ┌─────────▼───────────────────────┐
│     `page.overlay.append()`     │             │       `current_audio.pause()`   │
│ (Controle retido na sessão raiz)│             │ (Cancela áudio ativo anterior)  │
└─────────────────────────────────┘             └─────────────────────────────────┘
```

---

## 3. 🛠️ Código Completo do Serviço (`src/audio_service.py`)

```python
# src/audio_service.py — Serviço de Áudio Robustecido

import flet as ft
import os

class AudioService:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_audio: ft.Audio = None

    def play_tts(self, audio_path: str):
        """
        Reproduz um arquivo de áudio de forma segura, pausando qualquer
        reprodução anterior e garantindo que o controle permaneça vivo no overlay.
        """
        # 1. Cancelar reprodução ativa anterior
        if self.current_audio:
            try:
                self.current_audio.pause()
            except Exception:
                pass

        # 2. Verificar existência do arquivo local em assets/audio
        full_path = os.path.join(os.path.dirname(__file__), "..", audio_path)
        if not os.path.exists(full_path):
            print(f"[AudioService] Aviso: Arquivo de áudio não encontrado: {audio_path}")

        # 3. Instanciar e anexar ao overlay da página
        self.current_audio = ft.Audio(
            src=audio_path,
            autoplay=True,
            on_state_changed=self._on_state_changed
        )
        
        # Garante vínculo com a sessão raiz sem duplicação
        if self.current_audio not in self.page.overlay:
            self.page.overlay.append(self.current_audio)
            
        self.page.update()

    def _on_state_changed(self, e):
        # Evento nativo disparado ao concluir a reprodução
        pass
```

---

## 4. 🚨 Análise do Bug Resolvido ([[bug_01_flet_audio_corridas_e_page_services]])

- **Sintoma**: Ao clicar rapidamente entre exercícios ou ao sair da view do quiz enquanto um áudio estava sendo baixado/tocado, o app travava com a mensagem `AssertionError: Control not found`.
- **Causa Raiz**: O player `ft.Audio` era instanciado dentro da view local (`quiz_view.py`). Ao trocar de rota, a view era descartada pelo Garbage Collector enquanto a thread do Flutter continuava tentando ler o player destruído.
- **Solução Nativa**: O registro no `page.overlay` garantiu que o controle pertença à janela mãe do Flet, sobrevivendo a trocas de rotas sem exceções.

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- ⚡ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
- 🧠 Estudo Didático Neuropedagógico: [[didactic_neuroscience_korean_ptbr]]
- 🚨 Bug do Serviço de Áudio: [[bug_01_flet_audio_corridas_e_page_services]]
