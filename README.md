# Saebom Companion (새봄 컴패니언) 🇰🇷📱

**Versão atual:** `v0.3.9-alpha`

O **Saebom Companion (새봄 컴패니언)** é um projeto experimental de código aberto desenvolvido de forma independente como uma ferramenta de apoio complementar para os alunos de língua coreana do Centro Cultural Coreano no Brasil (CCCB).

Este aplicativo foi idealizado a partir de uma demanda pedagógica prática observada durante o primeiro semestre do curso, seguindo a diretriz *"A tecnologia acompanha a pedagogia. Nunca compete com ela"* — oferecendo aos estudantes um ambiente digital auxiliar para fixação de vocabulário, caligrafia, exercícios e acompanhamento prático fora do horário das aulas regulares.

---

## ⚖️ Aviso Legal e Direitos Autorais / Disclaimer

* **Caráter Educacional:** Este projeto possui caráter estritamente pedagógico, acadêmico e **sem fins lucrativos**. Ele foi desenvolvido por um aluno da instituição para fins de estudo de desenvolvimento de software e prática do idioma coreano.
* **Propriedade Intelectual:** Todos os direitos sobre os materiais didáticos originais, incluindo os livros *"Sejong Coreano 1A e 1B"*, seus respectivos *Workbooks*, áudios e marcas associadas, pertencem integralmente à **King Sejong Institute Foundation (KSIF)** e seus respectivos idealizadores.
* **Vínculo Institucional:** Este software **não possui vínculo oficial de desenvolvimento, homologação ou governança corporativa** por parte da diretoria do Centro Cultural Coreano no Brasil ou da KSIF, configurando-se exclusivamente como um projeto de portfólio estudantil de código aberto.
* **Política de Dados:** Nenhuma informação pessoal ou confidencial de alunos, professores ou servidores institucionais é coletada, armazenada ou exposta por este repositório.

---

## 🛠️ Tecnologias Utilizadas

O ecossistema do projeto foi construído com foco em acessibilidade linguística, arquitetura resiliente, conteinerização e segurança cibernética:

* **Aplicação & Interface:** Python (`3.11` / `3.12`) + **Flet `0.85.3`** (Flutter Engine / CanvasKit Web & Desktop), validação de contratos com **Pydantic**, processamento de imagem/caligrafia com **Pillow** e tipografia local em **Pretendard** e **Kyobo Handwriting 2025**.
* **Áudio & Prática Interativa:** **flet-audio `0.85.3`** (com desbloqueio de autoplay via `silent.wav`), grade caligráfica *wongoji* (원고지), laboratório de oclusivas, fábrica de sílabas e revisão espaçada.
* **Infraestrutura & Deploy:** **Docker** (`Dockerfile` com usuário não-root `saebomuser` UID/GID `10001` e named volumes persistentes) & **Docker Compose** (`docker-compose.yml`).
* **Servidor Web / Proxy Reverso:** **Caddy 2** (`Caddyfile`) com redirecionamento HTTP `:80` → HTTPS, TLS automático via Let's Encrypt (`saebomcompanion.duckdns.org`), compressão `zstd`/`gzip` e cabeçalhos defensivos OWASP.
* **Qualidade, CI/CD e Segurança:** Pipeline **GitHub Actions** ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)), suíte automatizada com `pytest` (`tests/`), testes ponta a ponta em navegador real com **Playwright E2E** (Chromium) e registro histórico de auditoria arquivado em [`Documentacao/Changelogs_e_Historico/audit_report_historico.md`](Documentacao/Changelogs_e_Historico/audit_report_historico.md).

---

## 📁 Estrutura Básica do Repositório

```text
.
├── .github/workflows/     # Pipeline CI & Security Gates + E2E Playwright (ci.yml)
├── .licenses/             # Licenças de referências utilizadas
├── Documentacao/          # Manuais, bugs críticos, changelogs e auditoria histórica
│   └── Changelogs_e_Historico/
│       ├── CHANGELOG.md
│       └── audit_report_historico.md
├── assets/                # Branding v3.1, fontes locais, SVGs e áudio bundled
├── data/                  # Currículo (Hangul, 1A e 1B), unidades e dados locais
├── docs/reference/        # Referências técnicas do projeto
├── scripts/               # Scripts de auditoria curricular, áudio, branding e deploy OCI
├── src/                   # Código-fonte principal da aplicação (views, components, serviços)
├── tests/                 # Suíte de testes unitários, segurança e E2E Playwright (Chromium)
├── .dockerignore          # Exclusão de segredos, dados de runtime e artefatos da imagem
├── Caddyfile              # Proxy reverso Caddy 2 com TLS, CSP, HSTS e cabeçalhos defensivos
├── DESIGN.md              # Diretrizes de design e roadmap visual
├── Dockerfile             # Manifesto da imagem Docker non-root (saebomuser UID/GID 10001)
├── docker-compose.yml     # Orquestração de app + caddy com named volumes e PIN fail-closed
├── main.py                # Ponto de entrada da aplicação Flet
└── requirements.txt       # Dependências Python fixadas/mínimas do projeto
```

---

## 🛡️ Práticas de Segurança Aplicadas

Por se tratar de um projeto mantido com foco em Segurança da Informação e conformidade defensiva (OWASP Top 10 / MITRE ATT&CK), o repositório segue diretrizes rigorosas para mitigar riscos:

1. **Segregação de Credenciais (Fail-Closed):** Nenhuma chave de API, token ou senha de produção é injetada nos arquivos fonte. A autenticação administrativa exige `SAEBOM_ADMIN_PIN` via `.env` / variáveis de ambiente, utilizando comparação em tempo constante (`hmac.compare_digest`), bloqueio contra força bruta e validação *fail-closed* no `docker-compose.yml` e no backend.
2. **Isolamento de Containers & Proxy Defensivo:** O container da aplicação executa como usuário sem privilégios (`saebomuser`, UID/GID `10001`), com `no-new-privileges:true`, named volumes persistentes e exposição restrita atrás do Caddy 2 (redirecionamento `:80` → HTTPS com HSTS exclusivo em TLS e CSP calibrada para CanvasKit/Skwasm e WebSockets).
3. **Auditoria Contínua & Gates de CI:** O relatório histórico pré-hardening está arquivado em [`Documentacao/Changelogs_e_Historico/audit_report_historico.md`](Documentacao/Changelogs_e_Historico/audit_report_historico.md), enquanto o workflow [`.github/workflows/ci.yml`](.github/workflows/ci.yml) valida compilação, varredura de segredos, suíte `pytest` e testes reais em navegador com Playwright.

---
Desenvolvido com 💙 por [Everton Kaylon](https://github.com/EvertonKaylon).
