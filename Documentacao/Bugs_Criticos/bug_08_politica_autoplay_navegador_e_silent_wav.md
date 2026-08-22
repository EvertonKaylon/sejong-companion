# BUG-08: Bloqueio de Autoplay em Navegadores Web (Issue Flet #3695) & Destravamento com `silent.wav`

- **Severidade**: 🔴 Crítica (Web / Mobile PWA)
- **Módulo**: `src/audio_service.py` / `assets/silent.wav`
- **Componente**: Player de Áudio Web (`flet_audio.Audio`)
- **Referência Externa**: [flet-dev/flet#3695](https://github.com/flet-dev/flet/issues/3695)

---

## 1. Descrição do Problema

Em ambiente Web (deploy na nuvem, PWA ou execução via `--browser`), o aplicativo ficava completamente mudo ou apresentava *timeouts* ao tentar reproduzir qualquer áudio, mesmo para arquivos já salvos em cache local (`assets/audio_cache/`).

---

## 2. Causa Raiz Técnica

O comportamento não era um bug do Flet nem lentidão da síntese TTS, mas uma restrição da **política de segurança de Autoplay dos navegadores modernos (Chrome, Edge, Safari)**:

1. **Assincronia do Flet**: Toda chamada a `play()` no Flet passa por um *round-trip* assíncrono entre servidor e cliente (mesmo para arquivos cacheados).
2. **Rejeição de Gesto pelo Navegador**: O navegador não reconhece a resposta assíncrona do servidor como um gesto direto do usuário (*user gesture*), bloqueando silenciosamente a reprodução de áudio sem disparar exceção no lado Python.
3. **Desktop Imune**: No desktop Windows, o `winsound` executa o arquivo `.wav` diretamente pelo subsistema nativo de áudio do sistema operacional, sem passar por navegadores, motivo pelo qual o erro nunca ocorria localmente no desktop.

---

## 3. Solução Aplicada (O Workaround Oficial Validado)

O workaround validado pela comunidade Flet e pelo mantenedor da issue #3695 consiste em:

1. O elemento `flet_audio.Audio` é montado na inicialização da página com `src="silent.wav"`, `autoplay=True` e `volume=0.0`.
2. Como o áudio inicial é **completamente silencioso e mudo (`volume=0.0`)**, os navegadores permitem o autoplay sem restrições.
3. Isso **destrava o elemento HTML de áudio específico para todo o restante da sessão**.
4. Nas chamadas subsequentes de reprodução de pronúncia coreana, o mesmo elemento é reutilizado apenas alterando o `src` e restaurando o volume para `1.0`, permitindo a reprodução fluida mesmo vindo de callbacks assíncronos.

### Localização Obrigatória do Arquivo:
- O arquivo deve estar salvo em: `assets/silent.wav` (na raiz da pasta `assets/`, não dentro de `audio_cache/`).
- Formato: WAV PCM 16-bit Mono 44.1kHz silencioso.

---

## 4. Como Evitar Regressões

- **Nunca destruir o player único** em mudanças de rota no modo Web; reutilizar sempre a instância `self.player` criada no `AudioService`.
- Garantir que o `assets/silent.wav` esteja incluído no versionamento Git e copiado no `Dockerfile` do deploy de produção.
