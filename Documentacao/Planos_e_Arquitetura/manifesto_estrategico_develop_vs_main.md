# 📜 Manifesto Estratégico & Análise Comparativa: `develop` vs `main`

**Tipo:** Registro Histórico de Decisão e Visão de Produto  
**Data:** 2026-08-19  
**Status:** CONSOLIDADO  
**Documentos Relacionados:** [[decisao_arquitetural_motor_adaptativo_local_vs_llm]] | [[Motor_Adaptativo_e_Learning_Engine]] | [[ROADMAP_MESTRE_COMPANION]] | [[CHANGELOG]]  

---

## 🧭 1. Veredito Executivo

> **"Se a `main` é o Sejong Companion funcional em produção, a `develop` é o Sejong Companion começando a virar um sistema adaptativo de aprendizagem."**

### Matriz Comparativa de Maturidade (`main` vs `develop`)

| Área | `main` | `develop` | Análise |
| :--- | :---: | :---: | :--- |
| **Produto** | 7/10 | **8.5/10** | Salto de um visualizador estático para um ambiente de estudo ativo |
| **Conteúdo** | 5/10 | **9/10** | De 1 unidade + placeholders para 11 unidades reais (`unit_intro` + `unit_01` a `unit_10`) |
| **Arquitetura** | 7/10 | **8/10** | Abordagem 100% data-driven com modelos Pydantic rigorosos |
| **Pedagogia** | 6/10 | **8.5/10** | Foco em estrutura sintática (SOV) e recuperação ativa em vez de mera tradução |
| **Personalização** | 2/10 | **8/10** | Rastreamento por nó de memória e fila adaptativa de revisão |
| **SRS / Memória** | 0/10 | **8/10** | Algoritmo de meia-vida temporal e repetição espaçada integrado |
| **Testes** | 7.5/10 | **9/10** | De 25 testes para **62 testes automatizados** com 100% de aprovação |
| **UX** | 8/10 | **8.5/10** | Feedback tátil elástico, tema escuro nativo, design responsivo |
| **Prontidão de Produção** | 5/10 | **7/10** | Alta estabilidade local, mas exigindo consolidação antes do deploy |
| **Potencial** | 9/10 | **9.5/10** | Transição para Propriedade Intelectual pedagógica própria |

---

## 🔬 2. Os 28 Pontos Fundamentais da Análise

### 1. Transformação de Conteúdo
A `develop` entrega o currículo completo do Sejong Hakdang 1A em 11 arquivos JSON estruturados (`unit_intro.json` e `unit_01.json` a `unit_10.json`), cobrindo números sino/nativos, localização, rotina, compras, classificadores, horários, clima, passado, desejos e propostas.

### 2. Paradigma Data-Driven
Transição de *"o código conhece cada aula"* para *"o código conhece o formato de uma aula"*. `DataService.get_unit(unit_id)` carrega dinamicamente qualquer unidade sem acoplamento.

### 3. Contratos Estritos no `models.py`
O Pydantic atua como barreira de integridade para `Unit`, `VocabItem`, `GrammarSection`, `CulturalNote`, `QuizQuestion`, `SovWordItem`, `SovSlotDefinition`, `MemoryNode`, `FlashcardItem` e `ReviewSessionState`.

### 4. SOV Semântico com Papéis Sintáticos
O Drag & Drop valida papéis funcionais (`SUBJECT`, `OBJECT`, `VERB`, `PREDICATE`, `PLACE`, `PARTICLE`) e slots com `accepted_roles`.

### 5. Ensino de Estrutura vs Tradução
A mecânica ensina a função estrutural das palavras na sentença coreana, essencial para falantes de Português (L1 SVO $\rightarrow$ L2 SOV).

### 6. Modelo de Memória Temporal (HLR)
Implementação da equação $R = 2^{-t/h}$, onde a meia-vida $h$ se expande com acertos rápidos e se contrai com erros.

### 7. Delimitação Metodológica (Bandeira Amarela)
⚠️ **Não confundir modelo heurístico com ciência estatística validada.** O algoritmo é uma heurística matemática calibrável e determinística, evitando "neurociência de PowerPoint".

### 8. Granularidade de Memória Dupla
Separação de memória agregada por unidade (`memory_unit_`) e memória atômica por item (`memory_item_`), permitindo precisão cirúrgica na revisão.

### 9. Active Recall Real (`/review`)
Fila de revisão dinâmica que seleciona automaticamente apenas itens cuja retenção estimada caiu abaixo de $75\%$.

### 10. Flashcards Derivados do Currículo
Os cartões são sintetizados dinamicamente a partir dos JSONs das unidades 01 a 10, sem duplicação de base de dados.

### 11. Distinção Obrigatória: `difficulty` $\ne$ `mastery`
Dificuldade é uma propriedade intrínseca do item gramatical; maestria é o histórico de domínio do aluno. Um item difícil pode estar com 95% de domínio e vice-versa.

### 12. Persistência Atômica em Disco
Gravação de sessões em `data/sessions/{uuid}.json` via escrita temporária e `os.replace()`, prevenindo corrupção de arquivos.

### 13. Sessão em Disco vs Persistência de Produção (Bandeira Vermelha)
🚨 O filesystem local em containers de nuvem (ex: Render sem disco persistente) é efêmero. A transição para PostgreSQL na fase Beta é mandatória para produção real.

### 14. Isolamento por Sessão vs Identidade de Usuário
O UUID atual isola abas de navegadores, mas não representa a conta persistente de um aluno entre dispositivos.

### 15. XP Não-Punitivo
O sistema adota `study_days` e `study_dates`, recompensando presença contínua sem zerar o progresso por faltas.

### 16. Separação de Métricas
- **XP** = Motivação
- **Mastery** = Domínio do conceito
- **Retention** = Memória temporal
- **Completion** = Progresso curricular

### 17. Ciclo de Aprendizagem Adaptativa
`Currículo ──► Prática ──► Recuperação Ativa ──► Memória ──► Retenção ──► Fila de Revisão`.

### 18. Desacoplamento da UI do Motor Pedagógico
Criação do módulo dedicado `LearningEngine` (`src/engine/`) para evitar o emaranhamento de lógica pedagógica com widgets Flet.

### 19. Foco em Validação Pedagógica
Equilíbrio entre adicionar novas features e medir se os alunos estão de fato retendo o conteúdo.

### 20. Telemetria e Evidência Pedagógica Anônima
Registro de eventos (`lesson_opened`, `quiz_completed`, `response_time_ms`, `error_count`) para calibrar as heurísticas de retenção com dados reais.

### 21. Evolução do Modelo
Dados reais de interação permitirão ajustar os multiplicadores de estabilidade matemática da meia-vida.

### 22. Segurança e Autorização
O identificador de sessão UUID de 12 caracteres é adequado para isolamento local, mas deve ser substituído por autenticação formal na fase de contas multi-usuário.

### 23. Rigor na Suíte de Testes
Avanço de 25 para **62 testes automatizados** testando regras de domínio, contratos semânticos e integridade de áudio.

### 24. Rumo aos Testes E2E
Necessidade futura de testes automatizados ponta-a-ponta cobrindo a jornada completa do aluno.

### 25. UX Pedagógica nas Telas de Fila Vazia
Quando não há itens abaixo de $75\%$, a interface deve incentivar o estudo preventivo e o aprendizado de novos módulos em vez de passar a impressão de "não preciso estudar".

### 26. Rastreamento por Conceito e Habilidade
Superar a nota média por unidade, mapeando conceitos atômicos (ex: números sino vs nativos).

### 27. O Grafo de Aprendizagem (Learning Graph)
Mapeamento de pré-requisitos: o erro em uma partícula frequentemente se origina na fonética de *받침*.

### 28. Filosofia Central: IA Simbólica / Cognitiva Local (Sem LLMs)
Decisão definitiva de construir um app mobile leve, 100% offline, rápido, privado, determinístico e de custo zero, sem dependência de APIs de IA Generativa.
