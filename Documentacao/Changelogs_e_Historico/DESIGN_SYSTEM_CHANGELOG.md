# Design System aplicado ao Sejong Companion

O `design-system.zip` é um projeto Next.js + Tailwind v4 + shadcn/ui (web/React).
O Sejong Companion é um app Python feito com **Flet**. Não dá pra copiar os
arquivos `.tsx`/`.css` direto — eles não rodam nesse stack. O que foi feito foi
**portar os tokens de design** (cores, tipografia, radius, sombras) para
`src/theme.py`, que já era a única fonte de verdade de estilo do app: todo
componente e view lê `get_theme_colors()` e `Styles`, então a mudança se
propaga sozinha pelo app inteiro.

## Abordagem final (depois de duas rodadas)

- **Primária** → azul `#0356C5` ("Azul Real Sejong", token `info` do design
  system) — usada na estrutura do app: cabeçalhos, abas, ícones, avatares,
  bordas.
- **Secondary** → roxo `#7C4DFF` (Vibrant Violet, a cor primária original do
  design system) — usada como destaque pontual: CTAs, badges, anel de
  progresso, botões de áudio.
- **Accent** → dourado `#F5A623` do Sejong, mantido do início ao fim (dicas,
  destaques, lâmpadas de mnemônica).
- **Correto / Incorreto** → tokens `success` (`#19BD56`) e `destructive`
  (`#C50337`) do design system.
- **Neutros (fundo, texto, bordas, superfícies)** → escala neutra completa do
  design system, clara e escura.

Essa não foi a primeira tentativa — a Rodada 1 (mais abaixo) usava o roxo
como primária. Depois de ver o app rodando, isso não ficou bom (detalhes na
seção "Rodada 2").

## O que mudou em `src/theme.py`

- Todas as escalas de cor (primary/neutral/destructive/info/success/warning,
  50→950) foram portadas de `app/globals.css`.
- `Styles.BORDER_RADIUS_SM/MD/LG` passaram de `8/16/24` para `9/12/18`,
  batendo com a escala do design system (base `0.75rem`, ~9px botões, 12px
  cards, 18px para cards/chips em destaque). Adicionei também
  `BORDER_RADIUS_PILL` para badges totalmente arredondados, se quiser usar.
- `Styles.CARD_SHADOW` e `HOVER_SHADOW` foram reescritas a partir de
  `--shadow-md` e `--shadow-primary` do design system (o hover agora é um
  brilho roxo, no lugar do azul antigo). Adicionei também `SHADOW_SM` e
  `SHADOW_LG` como opções extras disponíveis.
- `get_theme_colors()` ganhou duas chaves novas: `"info"` e `"warning"`,
  disponíveis para uso futuro (ex: estados de aviso que hoje usam cores
  soltas).

## Tipografia — decisão deliberada

O design system pareia **Inter** (texto latino) com **Noto Sans KR**
(coreano). Registrei a fonte **Inter** em `page.fonts`, mas **não** troquei a
fonte padrão do app para ela. Motivo: o Flet roda sobre Flutter, que — ao
contrário de um navegador — não faz fallback automático de glifo por
caractere. Se "Inter" virasse a fonte global e algum texto em Hangul não
tivesse um `font_family` explícito de override, o caractere coreano correria
risco de renderizar como um retângulo vazio ("tofu"). Como isso é literalmente
um app de coreano, preferi manter "Noto Sans KR" como fonte padrão (ela já
cobre bem latim + hangul) e deixar "Inter" disponível para quem quiser aplicá-
la manualmente em textos 100% latinos depois.

## Outros arquivos tocados (cores hardcoded fora do theme.py)

Alguns componentes tinham cores em `rgba(...)`/hex escritas à mão (não liam de
`Colors`), então precisaram de ajuste manual para acompanhar a nova paleta:

- `src/components/hangul_card.py` — tag de "aspirada/tensa" (verde).
- `src/components/quiz_widget.py` — feedback de certo/errado, chip de palavra
  selecionada.
- `src/views/hangul_view.py` — banners de aviso (anti-romanização, alerta de
  escrita, "i fantasma").
- `src/views/home_view.py` — as 4 cores rotativas da dica por horário do dia
  (manhã/tarde/noite/madrugada), agora usando warning/info/primary/primary-
  escuro do design system; e o tom neutro do card de unidade bloqueada.

`src/components/vocab_card.py` e `src/views/lesson_view.py` já usavam o
dourado do Sejong em `rgba(245, 166, 35, ...)` — como o accent foi mantido,
esses dois arquivos não precisaram de nenhuma mudança.

## Bônus: bug pré-existente corrigido

Sem relação com o design system: `src/components/quiz_widget.py` usava
`min_height=` num `Container`, argumento que não existe mais na versão atual
do Flet instalada (`flet>=0.25.0` no `requirements.txt` é uma faixa bem
aberta, e a API mudou desde então) — isso quebrava o app na inicialização.
Troquei por uma abordagem sem altura mínima fixa (o padding já dá presença
suficiente à caixa vazia, e ela cresce livremente conforme os chips de
palavra são adicionados).

## O que testei

- Todos os arquivos `.py` do projeto compilam (`py_compile`).
- `theme.py` importa e `get_theme_colors()`/`Styles` resolvem corretamente em
  claro e escuro.
- `HangulCard`, `VocabCard` e `QuizWidget` (multiple_choice e order_words)
  instanciam sem erro em ambos os temas, com dados de exemplo.
- Todas as 5 views importam sem erro.

O que eu **não** consegui testar aqui: renderização visual real no navegador
(esse ambiente não tem como abrir um Flet app web). Vale rodar
`python main.py` localmente e dar uma conferida visual antes de considerar
finalizado.

---

## Rodada 2 — ajustes depois de ver o app rodando

Depois de rodar o app de verdade, dois problemas apareceram:

### 1. Roxo como cor primária não ficou bom

Rodando o app, o roxo dominando cabeçalhos/abas/ícones ficou pesado contra o
fundo escuro, e criava uma inconsistência visual clara: o botão "Praticar com
Exercícios" (que usa `colors["secondary"]`, na época azul) aparecia sozinho
em azul no meio de uma tela inteira roxa — parecia bug, não decisão de
design.

**Correção:** inverti os papéis semânticos em `theme.py`.
- `PRIMARY` voltou a ser o azul (`#0356C5`, "Azul Real Sejong") — estrutura:
  cabeçalhos, abas, ícones, avatares, bordas.
- `SECONDARY` passou a ser o roxo do design system (`#7C4DFF`) — aparece de
  forma deliberada nos CTAs (como o botão de quiz), badges, anel de
  progresso e botões de áudio, como um destaque pontual.
- `ACCENT` continua o dourado do Sejong, sem mudança.
- `HOVER_SHADOW` (o brilho usado em cards/botões pressionados) voltou a ser
  azul, acompanhando a nova cor primária.

Nenhum outro arquivo precisou de edição nessa rodada — como tudo lê de
`colors["primary"]`/`colors["secondary"]`, a troca se propagou sozinha. O
único `rgba(124, 77, 255, ...)` hardcoded que sobrou (chip de palavra no
quiz, em `quiz_widget.py`) passou a representar a nova cor secundária
automaticamente — e isso é bom, é exatamente mais roxo "à mostra" de forma
pontual/limpa, sem virar a cor de fundo de tudo.

### 2. Toggle de tema claro/escuro não era instantâneo

**Causa raiz:** `toggle_theme()` em `home_view.py` trocava `page.theme_mode`
e depois chamava `page.router.navigate_to("/home")` — só que já estávamos em
`/home`. Navegar para a mesma rota é tratado como no-op pelo roteador do
Flet (não dispara `on_route_change`), então a view não era reconstruída. Só
quando o usuário entrava numa lição (rota diferente) e voltava é que a
`home_view` era reconstruída do zero com o tema correto — daí a sensação de
"preciso trocar de tela pra aplicar".

**Correção:** `toggle_theme()` agora reconstrói a view atual diretamente
(`page.views.clear()` + `page.views.append(home_view(page))` +
`page.update()`), sem depender do sistema de rotas. Testei isso simulando o
clique do botão fora do navegador: o `bgcolor` da view mudou de `#F5F5F5`
(claro) para `#141316` (escuro) na hora, com uma única view na pilha (sem
duplicar).

Esse toggle só existe em `home_view.py` (é o único lugar com o ícone de
sol/lua) — as outras views herdam o tema correto normalmente ao serem
construídas via navegação normal, que já funcionava.

