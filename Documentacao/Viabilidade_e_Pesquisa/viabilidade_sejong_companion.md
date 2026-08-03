# 📊 Viabilidade: App Sejong Companion — CCCB

**Data:** 06 de maio de 2026  
**Contexto:** App companion para alunos do Sejong Hakdang / Centro Cultural Coreano no Brasil  
**Solicitante:** Professora de coreano do CCCB  
**Desenvolvedor:** Aluno da turma (dev solo, experiência com Python)

---

## 1. Resumo Executivo

> [!IMPORTANT]
> **Veredicto: VIÁVEL COM RESSALVAS** — O projeto é viável como ferramenta institucional gratuita para alunos do CCCB. Porém, há um ponto crítico: o conteúdo do livro 세종한국어 é protegido por copyright da KSIF (King Sejong Institute Foundation) e **não pode ser reproduzido em app sem autorização formal**. A recomendação é criar conteúdo **complementar e original** ao invés de copiar o workbook, e buscar aval institucional do CCCB junto à KSIF.

### Pontos-chave

| Aspecto | Status |
|:---|:---|
| Demanda real? | ✅ Alta — vagas do CCCB esgotam todo semestre |
| Apps existentes resolvem? | ❌ Não — nem o app oficial Sejong atende bem |
| Flet/Python é viável? | ✅ Sim, com limitações conhecidas |
| Copyright é problema? | ⚠️ Sim — precisa de estratégia de conteúdo |
| Dev solo consegue? | ✅ Sim, com escopo controlado e sem prazo |

---

## 2. Contexto Institucional

### 2.1 O que é o Sejong Hakdang

O **Instituto Rei Sejong (세종학당)** é uma rede global de ensino de coreano mantida pelo **Ministério da Cultura, Esportes e Turismo** da Coreia do Sul, via a **King Sejong Institute Foundation (KSIF)**. Há mais de 240 institutos em 80+ países.

- **Currículo padronizado** em 6 níveis (Iniciante 1-2, Intermediário 3-4, Avançado 5-6)
- **Metodologia comunicativa** com integração cultural
- **Material oficial:** Série "Sejong Korean" (세종한국어) — livros-texto + workbooks + áudios
- **Avaliações padronizadas** aplicadas 2x por ano globalmente

### 2.2 O CCCB no Brasil

O **Centro Cultural Coreano no Brasil** (São Paulo) opera como ponto de ensino vinculado ao Sejong Hakdang:

| Fato | Detalhe |
|:---|:---|
| Localização | São Paulo, SP |
| Cursos | Gratuitos (aluno paga apenas o material) |
| Vagas | Limitadas e **extremamente concorridas** |
| Inscrições | Semestrais (jan-fev e jul-ago) |
| Site | [brazil.korean-culture.org](http://brazil.korean-culture.org/) |
| Redes | [@kccbrazil](https://www.instagram.com/kccbrazil/) |

### 2.3 Por que o CCCB precisa de um app companion

1. **Material em coreano puro** — O workbook 1A é 100% em coreano, sem traduções. Alunos iniciantes precisam de apoio em português
2. **Áudios soltos** — A professora envia áudios pelo grupo de WhatsApp, sem organização ou exercícios vinculados
3. **Sem ferramenta de revisão** — Não existe forma estruturada de revisar fora da aula
4. **Apps existentes não servem** — Nem o oficial Sejong, nem Duolingo, nem outros atendem (detalhes abaixo)

---

## 3. Por que os Apps Existentes Não Servem

### 3.1 App Oficial do Sejong (손안의 세종학당)

O próprio app oficial da KSIF tem problemas documentados:

| Problema | Detalhe |
|:---|:---|
| **Bugs de áudio/mic** | Não funciona em vários modelos Samsung Galaxy |
| **UI quebrada** | Layout desconfigurado em iPads |
| **Login burocrático** | Sem login via Apple/Google, processo manual |
| **Barreira para iniciantes** | Diálogos complexos demais, precisa de dicionário constante |
| **IA limitada** | Conversação com IA só funciona em scripts pré-definidos |
| **Gramática rasa** | Níveis avançados não explicam gramática em detalhe |
| **Sem português** | Interface e explicações apenas em coreano e inglês |

> A KSIF lançou a versão 2.0 em março de 2026 com melhorias, mas os problemas fundamentais (idioma, UX, bugs) persistem.

### 3.2 Duolingo

| Problema | Impacto para alunos CCCB |
|:---|:---|
| **Sem explicação gramatical** | Alunos não entendem partículas (은/는 vs 이/가) |
| **Frases artificiais** | Não correspondem ao que aprendem na aula |
| **Honoríficos confusos** | Foca em 하십시오체 sem explicar contextos |
| **Currículo diferente** | Não segue a sequência do Sejong Korean |
| **Gamificação excessiva** | XP e streaks > aprendizado real |

### 3.3 LingoDeer / TTMIK / Lingory

| App | Problema Principal para alunos brasileiros |
|:---|:---|
| **LingoDeer** | ❌ Não disponível em português |
| **TTMIK** | ❌ Todo em inglês, usa romanização nos níveis iniciais |
| **Lingory** | ❌ Bugs técnicos frequentes, só vai até intermediário baixo |

### 3.4 A lacuna que o Sejong Companion preenche

```
Apps genéricos (Duolingo, etc.)        App oficial Sejong
  ↓ Conteúdo errado/raso                ↓ Bugs, sem PT, difícil
  ↓ Não segue currículo Sejong          ↓ Não complementa o workbook
  ↓ Sem foco em partículas              ↓ IA limitada a scripts

              ╔══════════════════════════════╗
              ║   SEJONG COMPANION (CCCB)    ║
              ║   ✅ Em português            ║
              ║   ✅ Segue currículo Sejong  ║
              ║   ✅ Complementa o workbook  ║
              ║   ✅ Áudios da professora    ║
              ║   ✅ Exercícios focados      ║
              ╚══════════════════════════════╝
```

---

## 4. Demanda de Mercado

### 4.1 Hallyu no Brasil (2025-2026)

| Indicador | Dado |
|:---|:---|
| Brasil no ranking K-pop global | **8º maior mercado** |
| Área de interesse líder no Brasil | **K-Film** (acima de K-Drama em outros países) |
| Tendência | Expansão para gastronomia, skincare, moda e idioma |
| Escolas de coreano | Crescimento visível em SP, Brasília, e capitais |
| Influenciadores | Comunidade coreano-brasileira ativa no Instagram/TikTok |

### 4.2 TOPIK no Brasil

- Coordenado pelo **CEC-SP** (Centro de Educação Coreana em São Paulo)
- Aplicado **3x ao ano** (abril, julho, outubro)
- Inscritos globais ultrapassaram **500.000 em 2025** (crescimento constante)
- Principal motivação: bolsas GKS, ingresso em universidades coreanas, carreira

### 4.3 Mercado global de apps de idiomas

| Métrica | Valor |
|:---|:---|
| Mercado 2024 | **USD 7,2 bilhões** |
| CAGR projetado | **25,1%** (até 2034) |
| Projeção 2034 | **USD 67 bilhões** |
| Coreano no Duolingo | Supera o chinês em interesse |

---

## 5. Viabilidade Técnica — Flet (Python)

### 5.1 Por que Flet faz sentido

| Vantagem | Detalhe |
|:---|:---|
| **Python puro** | Dev solo com experiência em Python pode produzir rápido |
| **Cross-platform** | Um código → Android + iOS + Web + Desktop |
| **Flutter por baixo** | UI nativa, animações suaves, 60fps |
| **150+ componentes** | Botões, listas, cards, navegação — tudo built-in |
| **Hot reload** | Desenvolvimento iterativo rápido |
| **Áudio** | `flet-audio` wraps Flutter audioplayers |

### 5.2 Limitações conhecidas

| Limitação | Impacto | Mitigação |
|:---|:---|:---|
| **Build iOS requer Mac** | Sem Mac = sem IPA | Usar PWA web como alternativa para iOS |
| **APK maior** | ~50-80MB (inclui Python + Flutter) | Aceitável para app educacional |
| **Pacotes com C/Rust** | Não funciona em mobile | App não precisa de numpy/opencv |
| **Apple Developer = USD 99/ano** | Custo para publicar na App Store | Distribuir via TestFlight ou PWA |

### 5.3 Estratégia de deploy recomendada

```
Prioridade 1: Android APK
  → flet build apk
  → Distribuir via WhatsApp/grupo da turma
  → Zero custo

Prioridade 2: PWA Web
  → flet build web
  → Hospedar gratuitamente (Vercel/GitHub Pages)
  → Funciona em iPhone sem App Store

Prioridade 3 (futuro): App Store / Play Store
  → Só se o CCCB quiser institucionalizar
  → Requer conta de desenvolvedor
```

---

## 6. ⚠️ Direitos Autorais — PONTO CRÍTICO

> [!CAUTION]
> **O conteúdo do livro 세종한국어 é protegido por copyright da KSIF.** Reproduzir o conteúdo do workbook em um app sem autorização é proibido, mesmo para fins educacionais sem lucro.

### 6.1 Política da KSIF

- Todo material (livros, áudios, software) é propriedade da **KSIF**
- **Proibido:** reprodução, cópia, modificação e criação de obras derivadas sem aprovação prévia
- Alguns materiais no Nuri Sejong Hakdang têm licença KOGL, mas geralmente **proíbem uso comercial e modificação**
- Contato para licenciamento: `online@ksif.or.kr` ou via [ksif.or.kr](https://www.ksif.or.kr)

### 6.2 Estratégia recomendada

| Abordagem | Risco | Recomendação |
|:---|:---|:---|
| ❌ Copiar conteúdo do workbook no app | **Alto** — violação de copyright | Não fazer |
| ⚠️ Criar exercícios inspirados no workbook | **Médio** — zona cinza | Possível se suficientemente original |
| ✅ Criar conteúdo complementar original | **Baixo** — obra própria | **Recomendado** |
| ✅ Usar apenas áudios fornecidos pela professora | **Baixo** — uso interno do curso | OK com aval da professora |
| ✅ Pedir autorização formal via CCCB → KSIF | **Nenhum** — legitimado | **Ideal, pedir à professora** |

### 6.3 O que o app PODE fazer sem problemas

- ✅ Ensinar Hangul (alfabeto é patrimônio público, não tem copyright)
- ✅ Criar vocabulário e exercícios originais que **acompanham** os temas do curso
- ✅ Usar áudios gravados pela/para a professora (com permissão dela)
- ✅ Criar explicações gramaticais originais em português
- ✅ Seguir a mesma **sequência temática** (apresentação → números → localização...) sem copiar texto

---

## 7. Análise SWOT — Contexto Institucional

### Forças
- 🟢 Público-alvo definido e cativo (alunos da turma)
- 🟢 Conteúdo validado pela professora (precisão garantida)
- 🟢 Respaldo institucional do CCCB + Sejong Hakdang
- 🟢 Zero concorrência no nicho (companion app para Sejong em PT-BR)
- 🟢 Sem pressão de prazo ou monetização
- 🟢 Dev tem acesso direto aos alunos para feedback

### Fraquezas
- 🟡 Dev solo = velocidade limitada
- 🟡 Restrição de copyright do material KSIF
- 🟡 Sem acesso a Mac para build iOS nativo
- 🟡 Conteúdo precisa ser criado do zero (não pode copiar workbook)

### Oportunidades
- 🔵 Se o CCCB adotar oficialmente, pode escalar para todas as turmas
- 🔵 KSIF pode se interessar em apoiar (app complementar em português para toda a América Latina)
- 🔵 Portfolio profissional forte para o desenvolvedor
- 🔵 Potencial de expansão para níveis 1B, 2A, 2B, 3A, 3B
- 🔵 Pode evoluir para ferramenta oficial do Sejong Hakdang no Brasil

### Ameaças
- 🔴 KSIF pode atualizar o app oficial e resolver as deficiências
- 🔴 Mudança de currículo pode invalidar conteúdo do app
- 🔴 Sem manutenção contínua, o app pode ficar desatualizado
- 🔴 Dependência de um dev solo — se parar, o projeto para

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|:---|:---|:---|:---|
| Copyright do material KSIF | Alta | Alto | Criar conteúdo original + pedir autorização via CCCB |
| Dev solo abandonar projeto | Média | Alto | Código open-source, documentado, outros alunos podem contribuir |
| Flet ter bug em mobile | Média | Médio | Testar cedo em celular real, ter PWA como fallback |
| Professora não validar conteúdo | Baixa | Alto | Envolver desde o início, mostrar protótipo da Unidade 1 |
| Alunos não usarem | Média | Médio | Fazer pesquisa com a turma antes, co-criar funcionalidades |
| Mudança de currículo Sejong | Baixa | Médio | Estrutura modular permite trocar conteúdo sem reescrever app |

---

## 9. Comparativo: Companion App vs. App Comercial

| Aspecto | App Comercial (Duolingo-like) | Companion App (Sejong CCCB) |
|:---|:---|:---|
| Público | Qualquer pessoa | Alunos do curso CCCB |
| Monetização | Freemium/assinatura | Gratuito |
| Conteúdo | Genérico | Alinhado ao currículo Sejong |
| Validação | Equipe interna | Professora nativa |
| Escopo | Amplo (do zero ao avançado) | Focado (níveis 1-3 do Sejong) |
| Equipe | 5-20+ pessoas | 1 dev + 1 professora |
| Prazo | 6-12 meses para MVP | Sem pressão, ritmo do dev |
| Risco financeiro | Alto | Zero |
| Impacto potencial | Grande se viralizar | Direto e imediato nos alunos |

---

## 10. Recomendações e Próximos Passos

### Ações imediatas (antes de codar)

1. **Conversar com a professora sobre copyright**
   - Perguntar se o CCCB pode intermediar com a KSIF
   - Definir o que pode ou não ser usado do material oficial
   - Obter permissão formal para usar os áudios dela no app

2. **Pesquisa rápida com a turma**
   - Quantos usam Android vs. iOS?
   - Quais as maiores dificuldades de estudo fora da aula?
   - Usam algum app atualmente? Qual?

3. **Definir escopo do MVP com a professora**
   - Hangul + Unidade 1 (conteúdo original complementar)
   - Validar que o formato proposto faz sentido pedagogicamente

### Decisões pendentes da conversa anterior

| Pergunta | Status |
|:---|:---|
| Nome do app | ⏳ Aguardando |
| Formato do workbook (PDF ou físico) | ⏳ Aguardando |
| Formato dos áudios (MP3, M4A) | ⏳ Aguardando |
| Offline ou online | ⏳ Aguardando |
| Acesso a Mac para iOS | ⏳ Aguardando |

---

## 11. Conclusão

> [!IMPORTANT]
> ### Veredicto: **VIÁVEL como companion app institucional**
> 
> **A favor:**
> 1. Demanda real e confirmada (alunos precisam de apoio fora da aula)
> 2. Nenhum app existente serve — nem o oficial da KSIF
> 3. Flet/Python é tecnicamente adequado para o escopo
> 4. Zero risco financeiro, público cativo, feedback direto
> 5. Potencial de crescimento se o CCCB adotar oficialmente
> 
> **Ressalva principal:**
> O conteúdo do workbook 세종한국어 **não pode ser copiado** sem autorização. O app deve criar conteúdo **original e complementar** que acompanhe os temas do curso sem reproduzir o material da KSIF.
> 
> **Recomendação:** Avançar com o desenvolvimento, priorizando conteúdo original (Hangul + vocabulário + gramática explicada em PT-BR), e em paralelo solicitar via CCCB a autorização da KSIF para uso do material oficial.

---

> [!NOTE]
> **Fontes:** KSIF (ksif.or.kr), Nuri Sejong Hakdang (iksi.or.kr), CCCB (korean-culture.org), Apple App Store reviews, Google Play reviews, Reddit r/Korean, 2025 Global Hallyu Trend Report (Ministério da Cultura da Coreia), Korea Herald, The Guardian, CEC-SP, e pesquisa de mercado EdTech 2024-2026.
