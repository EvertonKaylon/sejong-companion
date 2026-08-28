---
name: sejong-docs-sync
description: >-
  Sincroniza a documentação oficial do Sejong Companion após a conclusão de uma
  branch ou release. Use quando finalizar commits de feature, fix, security ou
  refactor para garantir que CHANGELOG, INDICE_BUGS, INDICE_DOCUMENTACAO e
  arquivos de bug dedicados estejam atualizados antes do commit final.
---

# Sincronização de Documentação Oficial — Sejong Companion

## Quando Ativar
- Após o último commit técnico de uma branch (feature, fix, security, refactor)
- Antes de solicitar merge ou review ao usuário

## Procedimento

### 1. Identificar o tipo de mudança
- Feature nova? → Seções `Added` no CHANGELOG
- Bugfix? → Seções `Fixed` + possível arquivo `bug_XX_*.md`
- Security? → Seções `Fixed`/`Security` + arquivo `bug_XX_*.md` obrigatório
- Refactor? → Seções `Changed` no CHANGELOG

### 2. Atualizar o CHANGELOG
- Abrir `Documentacao/Changelogs_e_Historico/CHANGELOG.md`
- Adicionar nova seção `## [versão] — YYYY-MM-DD` acima da release anterior
- Incluir classificação, milestone summary, e itens detalhados por categoria
- Atualizar a contagem de testes automatizados

### 3. Atualizar o Catálogo de Bugs (se aplicável)
- Determinar o próximo ID sequencial (`BUG-XX`) consultando `INDICE_BUGS.md`
- Criar `Documentacao/Bugs_Criticos/bug_XX_descricao_curta.md` com:
  - Tabela de metadados (ID, severidade, componentes, data, branch, testes)
  - Seção 1: Descrição Sintomática
  - Seção 2: Causa Raiz Técnica
  - Seção 3: Código Antes vs Depois
  - Seção 4: Regras Preventivas
- Adicionar linha na tabela de `INDICE_BUGS.md`

### 4. Atualizar o Índice Central
- Abrir `Documentacao/INDICE_DOCUMENTACAO.md`
- Adicionar links para novos documentos criados nas seções apropriadas

### 5. Commit de Documentação
- Stage apenas os arquivos de `Documentacao/`
- Commit com prefixo `docs(escopo): descrição`
- Verificar working tree limpa

### 6. Verificação Final
- Confirmar que `git status` mostra `nothing to commit, working tree clean`
- Confirmar que todos os links nos arquivos `.md` apontam para caminhos existentes
