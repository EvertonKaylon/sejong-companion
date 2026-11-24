# Integração TTS (Typecast.ai) e Serviço de Áudio

**Conceito Relacionado:** [[Arquitetura_Flet_e_Flutter_Engine]] | [[Neuropedagogia_e_Gamificacao]] | [[SDD_Spec_Driven_Development]]  
**Documentos Vinculados:** [[didactic_neuroscience_korean_ptbr]] | [[Plano_UIUX_Flet_Sejong_Companion]]  
**Bugs Catalogados:** [[bug_01_flet_audio_corridas_e_page_services]] | [[bug_08_politica_autoplay_navegador_e_silent_wav]] | [[bug_09_vulnerabilidades_seguranca_e_hardening_autenticacao]]  

---

## 1. 🎙️ A Importância da Pronúncia Nativa (Typecast.ai)

O aprendizado da percepção auditiva no idioma coreano (*듣기*) é extremamente sensível a nuances fonéticas (como a tripartição oclusiva de consoantes simples, aspiradas e tensas).

Para garantir áudio cristalino com entonação humana natural, o **Saebom Companion (새봄 컴패니언)** utiliza vozes TTS geradas via **Typecast.ai** (`model="ssfm-v30"`), sintetizadas para o vocabulário e frases das lições baseadas nos livros didáticos oficiais *Sejong Korean 1A e 1B* (com fallback para Google Translate TTS quando aplicável em runtime Web).

---

## 2. ⚡ Arquitetura do Serviço Singleton (`AudioService`) & Isolamento `assets/` vs. `data/`

Em aplicações Flet 0.85+, instanciar players de áudio dentro de views temporárias causa vazamentos e exceções `Control not found` ao trocar de tela. Além disso, navegadores modernos bloqueiam `play()` disparado de forma assíncrona sem gesto síncrono direto (`BUG-08`), e ambientes containerizados exigem que `assets/` seja estritamente **read-only** (`BUG-09`).

Por isso, o projeto encapsula todo o ciclo de áudio no serviço global [`src/audio_service.py`](../../src/audio_service.py):

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                      SESSÃO GLOBAL DA PÁGINA (`page`)                   │
 │                        `page.audio_service`                             │
 └────────────────────────────────────┬────────────────────────────────────┘
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          │                                                       │
┌─────────▼──────────────────────────┐     ┌──────────────────────▼──────────────────────┐
│    Destravamento Autoplay (Web)    │     │     Armazenamento & Resolução de Áudio      │
│  `fa.Audio(src="silent.wav",       │     │ 1. Bundle estático (Read-Only):             │
│   autoplay=True, volume=0.0)`      │     │    `assets/audio_cache/{md5}.{ext}`         │
│  Mesmo player reusado na sessão    │     │ 2. Cache dinâmico (Mutável em Runtime):     │
└────────────────────────────────────┘     │    `data/cache/audio/{md5}.{ext}`           │
                                           │    (gravado via `.part` + `os.replace`)     │
                                           └─────────────────────────────────────────────┘
```

### Regras Arquiteturais Vigentes
1. **Player Singleton Permanente:** Criado uma única vez no startup (`main.py` → `page.audio_service`) usando `flet_audio.Audio`. Em navegadores Web/PWA, o player é inicializado com `src="silent.wav"` (`assets/silent.wav`, `volume=0.0`, `autoplay=True`) e nunca é destruído durante mudanças de rota.
2. **Isolamento `assets/` (Read-Only) vs. `data/cache/audio/` (Mutável):**
   - `assets/audio_cache/` contém apenas o pacote pré-aquecido empacotado no repositório/imagem Docker (`.mp3` para Web e `.wav` para Desktop Windows nativo). Nenhuma escrita em runtime ocorre em `assets/`.
   - `AudioService.get_cache_dir()` direciona toda gravação em runtime para **`data/cache/audio/`** (sobrescrevível via `SAEBOM_AUDIO_CACHE_DIR`, com fallback legado para `SEJONG_AUDIO_CACHE_DIR` ou `FLET_APP_STORAGE_CACHE`).
3. **Resolução Dual em Reprodução Web:** Arquivos presentes no bundle estático são reproduzidos via caminho relativo de asset (`audio_cache/{filename}`), enquanto novos áudios sintetizados em `data/cache/audio/` podem ser servidos diretamente como `bytes` ao `flet_audio.Audio.src`, garantindo funcionamento sem violar o caráter read-only de `assets/`.
4. **Chave de Cache Versionada & Gravação Atômica:** O nome do arquivo usa `md5("typecast-{fmt}-v2\0{text}")` e gravação atômica via arquivo temporário `.part` + `os.replace()`.

---

## 3. 🛠️ Fluxo de Execução Assíncrona (`src/audio_service.py`)

```python
# Resumo do pipeline em src/audio_service.py
async def _play_korean_async_inner(self, text: str):
    filename = self._cache_filename(text)
    local_file_path = os.path.join(self.cache_dir, filename)                  # data/cache/audio/
    bundled_path = os.path.join(self.get_bundled_assets_audio_dir(), filename) # assets/audio_cache/

    # Só sintetiza para data/cache/audio/ se ausente em ambos os repositórios
    if not (os.path.exists(local_file_path) or os.path.exists(bundled_path)):
        fetched = await asyncio.to_thread(self._synthesize_to_cache, text, local_file_path)
        if not fetched:
            self._show_audio_error(text)
            return

    if self._use_native_windows_player:
        target = local_file_path if os.path.exists(local_file_path) else bundled_path
        await self._play_native_file(target)  # winsound WAV
    else:
        await self._play_file(f"audio_cache/{filename}")  # asset ou bytes de cache_dir
```

---

## 4. 🚨 Bugs Críticos Relacionados

- **[[bug_01_flet_audio_corridas_e_page_services]]**: Migração do player por view para o serviço singleton global, eliminando `AssertionError: Control not found`.
- **[[bug_08_politica_autoplay_navegador_e_silent_wav]]**: Inclusão de `assets/silent.wav` e reutilização da mesma instância `fa.Audio` para destravar reprodução assíncrona no Chrome/Edge/Mobile PWA.
- **[[bug_09_vulnerabilidades_seguranca_e_hardening_autenticacao]]**: Transferência do cache mutável em runtime de `assets/audio_cache/` para `data/cache/audio/`, mantendo `assets/` 100% read-only.

---

## 📌 Links de Navegação Obsidian
- 🧠 Central Mestre de Conceitos: [[INDICE_CONCEITOS]]
- ⚡ Arquitetura Flet Engine: [[Arquitetura_Flet_e_Flutter_Engine]]
- 🧠 Estudo Didático Neuropedagógico: [[didactic_neuroscience_korean_ptbr]]
- 🚨 Bug do Serviço de Áudio: [[bug_01_flet_audio_corridas_e_page_services]]
- 🚨 Autoplay Web & silent.wav: [[bug_08_politica_autoplay_navegador_e_silent_wav]]
