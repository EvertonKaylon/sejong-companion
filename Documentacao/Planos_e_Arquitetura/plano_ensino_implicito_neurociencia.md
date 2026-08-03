# 📋 Plano de Implementação: Ensino Implícito de Coreano via Neurociência (Sem Avisos por Escrito)

**Data:** 24 de julho de 2026  
**Foco:** Refatoração de UX/UI e schemas JSON para aprendizado implícito sem disclaimers textuais  
**Documentos Vinculados:** [[didactic_neuroscience_korean_ptbr]] | [[Plano_UIUX_Flet_Sejong_Companion]] | [[implementation_plan]]  

---

## 1. Visão Geral do Plano

Reestruturação didática do **Sejong Companion** com base nos manuais *Sejong Korean 1A (Textbook e Workbook)* para falantes de Português Brasileiro (PT-BR). O plano remove todos os avisos/banners explicativos por escrito dentro do app, substituindo-os por interações sensoriais implícitas (áudio-visual gating, física de blocos magnéticos para SOV, e encaixes morfofonéticos).

> [!IMPORTANT]
> **Substituição de Banners Textuais por Interações Sensoriais Implícitas**:
> Os banners explicativos como `"anti_romanization_notice"` (*"🚫 Por que NÃO usamos romanização?..."*) e caixas de texto `"neuro_tip"` serão removidos das visões do app. Toda a carga neuropedagógica passa a ser entregue via feedback tátil, restrições físicas de drag-and-drop e pareamento sonoro imediato.

> [!NOTE]
> Para detalhes completos dos estudos acadêmicos e preprints do arXiv (como `arXiv:1606.01256` - Settles & Meeder), consulte o documento mestre [[didactic_neuroscience_korean_ptbr]].

---

## 2. Mudanças Propostas por Componente

### 2.1 Camada de Dados (Data Schemas & JSON Units)

#### 📄 `data/units/unit_intro.json`
- Remover o bloco `anti_romanization_notice` com texto explicativo.
- Adicionar propriedades sensoriais para cada fonema em `vowels` e `consonants`: `audio_wave_profile`, `mouth_shape_id`, `contrast_pair_id`.

#### 📄 `data/units/unit_01.json`
- Eliminar campos de texto `"neuro_tip"` que exibiam explicações explícitas sobre partículas.
- Adicionar propriedades de encaixe estrutural:
  - `snap_anchor`: `"square"` (para palavras com 받침 / consoante final) ou `"round"` (para palavras terminadas em vogal).
  - `magnetic_slot_role`: `"SUBJECT"`, `"OBJECT"`, `"VERB"`, `"PARTICLE"`.

---

### 2.2 Camada de Interface (UX/UI Components & Views)

#### 🖥️ `src/views/hangul_view.py`
- Remover qualquer renderizador do `anti_romanization_notice`.
- Implementar componente de **Áudio-Visual Gating**:
  - Toque no caractere Hangul ativa animação de pulso radial de onda sonora pareada com áudio nativo HD.
  - Adicionar botão de alternância imediata de Par Mínimo (ex: ㄱ vs ㅋ vs ㄲ) sem rótulos textuais de instrução.

#### 🖥️ `src/views/lesson_view.py`
- Refatorar o fluxo de montagem de frases com **Physics Gating (Drag & Drop Magnético)**:
  - Blocos de palavras com bordas coloridas semânticas (Sujeito: Azul `#3B82F6`, Objeto: Verde `#10B981`, Verbo: Violeta `#8B5CF6`).
  - Os slots aceitam apenas a sequência **SOV**. Se o usuário tentar arrastar o verbo para a posição central (SVO), o bloco sofre mola de repulsão física.

#### 🖥️ `src/views/quiz_view.py`
- Manter o feedback tátil e neuromórfico não-punitivo (verde sutil `#2619BD56` para acerto e carmesim sutil `#26C50337` isolado na alternativa errada).
- Zerar mensagens pop-up de desculpas ou avisos ao errar, mantendo o fluxo rápido de tentativa.

---

## 3. Plano de Verificação

### 🧪 Testes Automatizados
- Executar a suíte de testes de integridade dos dados e da UI via pytest:
  ```powershell
  python -m pytest tests/
  ```

### 👁️ Validação Manual
- Testar a navegação na `hangul_view.py` e verificar a ausência total de avisos por escrito.
- Validar a reprodução fluida do áudio nativo ao tocar nos blocos de Hangul.
- Verificar se as aulas de introdução ao Hangul e Unidade 01 progridem de forma limpa, sensorial e intuitiva.

---

## 📌 Links de Navegação Obsidian
- Ir para a central de documentação: [[INDICE_DOCUMENTACAO]]
- Ir para o estudo mestre neuropedagógico: [[didactic_neuroscience_korean_ptbr]]
- Ir para o plano de UI/UX: [[Plano_UIUX_Flet_Sejong_Companion]]
