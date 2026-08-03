# BUG-01: Corrida de Montagem de Áudio (`flet-audio`) & Vazamento em `page.services`

- **Severidade**: 🔴 Crítica
- **Módulo**: `src/audio_service.py` / `src/views/quiz_view.py`
- **Componente**: Player de Áudio TTS (Typecast.ai)

---

## 1. Descrição do Problema

Ao navegar entre as lições do quiz ou alternar rapidamente de telas enquanto um áudio estava sendo reproduzido (ou carregado), o aplicativo apresentava travamentos, exceções no console do Flet referentes a controles destruídos e interrupção inesperada do áudio. Adicionalmente, instâncias do `Audio` continuavam registradas em `page.services`, acumulando vazamento de memória.

---

## 2. Causa Raiz Técnica

O Flet 0.85+ exige que controles de serviço não-visuais (como `flet_audio.Audio`) permaneçam anexados a um container ativo ou registrados na página principal (`page.overlay` / `page.services`). 

1. **Corrida de Montagem**: Quando a view do quiz era desmontada ao clicar em "Voltar", o controle `Audio` pertencente à view era destruído pelo garbage collector antes que a chamada assíncrona de `play()` terminasse, gerando `AssertionError` ou `Control not found`.
2. **Vazamento em `page.services`**: Registrar novos players a cada clique em `page.services.append(audio)` sem um mecanismo centralizado de descarte fazia a lista de serviços crescer indefinidamente a cada exercício.

---

## 3. Solução Aplicada

Foi criado um **Serviço Global de Áudio Singleton** ([audio_service.py](file:///c:/Users/Pichau/Documents/sejong_companion/src/audio_service.py)) injetado diretamente no objeto `page.audio_service` durante a inicialização no [main.py](file:///c:/Users/Pichau/Documents/sejong_companion/main.py).

### Código Antes (Incorreto / Descentralizado):
```python
# quiz_view.py — Instanciando áudio direto na view (ERRADO)
def play_sound(url):
    audio = ft.Audio(src=url, autoplay=True)
    page.services.append(audio) # Acumulava lixo a cada clique
    page.update()
```

### Código Depois (Correto / Serviço Centralizado):
```python
# src/audio_service.py — Serviço reutilizável central (CORRETO)
class AudioService:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_audio = None

    def play_tts(self, audio_path: str):
        if self.current_audio:
            try:
                self.current_audio.pause()
            except Exception:
                pass
        
        # Reutiliza ou instancia no overlay seguro da página
        self.current_audio = ft.Audio(src=audio_path, autoplay=True)
        if self.current_audio not in self.page.overlay:
            self.page.overlay.append(self.current_audio)
        self.page.update()
```

---

## 4. Regra Preventiva

> [!IMPORTANT]
> Nunca instancie `ft.Audio()` diretamente dentro do método de construção de uma `View` individual. Sempre utilize a instância global `page.audio_service.play_tts(...)` para garantir gerenciamento centralizado de ciclo de vida.
