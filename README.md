# Sejong Companion 🇰🇷📱

O **Sejong Companion** é um projeto experimental de código aberto desenvolvido de forma independente como uma ferramenta de apoio complementar para os alunos de língua coreana do Centro Cultural Coreano no Brasil (CCCB).

Este aplicativo foi idealizado a partir de uma demanda pedagógica prática observada durante o primeiro semestre do curso, com o objetivo de fornecer aos estudantes um ambiente digital auxiliar para fixação de vocabulário, exercícios e acompanhamento prático fora do horário das aulas regulares.

---

## ⚖️ Aviso Legal e Direitos Autorais / Disclaimer

* **Caráter Educacional:** Este projeto possui caráter estritamente pedagógico, acadêmico e **sem fins lucrativos**. Ele foi desenvolvido por um aluno da instituição para fins de estudo de desenvolvimento de software e prática do idioma coreano.
* **Propriedade Intelectual:** Todos os direitos sobre os materiais didáticos originais, incluindo os livros *"Sejong Coreano 1A e 1B"*, seus respectivos *Workbooks*, áudios e marcas associadas, pertencem integralmente à **King Sejong Institute Foundation (KSIF)** e seus respectivos idealizadores.
* **Vínculo Institucional:** Este software **não possui vínculo oficial de desenvolvimento, homologação ou governança corporativa** por parte da diretoria do Centro Cultural Coreano no Brasil ou da KSIF, configurando-se exclusivamente como um projeto de portfólio estudantil de código aberto. 
* **Política de Dados:** Nenhuma informação pessoal ou confidencial de alunos, professores ou servidores institucionais é coletada, armazenada ou exposta por este repositório.

---

## 🛠️ Tecnologias Utilizadas

O ecossistema do projeto foi construído focando em boas práticas de arquitetura, conteinerização e segurança cibernética:

* **Backend:** Python (estruturado com rotinas automatizadas)
* **Infraestrutura & Deploy:** Docker & Docker Compose (para isolamento de ambiente)
* **Servidor Web / Proxy Reverso:** Caddy (configurado via `Caddyfile`)
* **Qualidade e Segurança:** Ambientes de testes automatizados (`tests/`) e relatórios periódicos de auditoria interna de código (`audit_report.md`).

---

## 📁 Estrutura Básica do Repositório

```text
.
├── .licenses/           # Licenças de dependências utilizadas
├── Documentacao/        # Manuais e documentações arquiteturais
├── assets/              # Elementos visuais e mídias da interface
├── data/                # Dicionários estruturados e dados de apoio locais
├── docs/ reference/     # Referências técnicas do projeto
├── scripts/             # Scripts utilitários de automação
├── src/                 # Código-fonte principal da aplicação (Python)
├── tests/               # Conjunto de testes de software
├── Caddyfile            # Configurações do servidor web Caddy
├── Dockerfile           # Manifesto de construção da imagem Docker
├── audit_report.md      # Relatório de auditoria de segurança cibernética
└── docker-compose.yml   # Orquestração local dos containers
```

---

## 🛡️ Práticas de Segurança Aplicadas

Por se tratar de um projeto mantido por um entusiasta da área de Segurança da Informação e jogador de CTF, o repositório segue diretrizes rigorosas para mitigar riscos:
1. **Segregação de Credenciais:** Nenhuma chave de API, token ou senha de produção é injetada diretamente nos arquivos fontes do repositório. Todas as configurações sensíveis utilizam variáveis de ambiente locais (`.env`).
2. **Auditoria de Código:** O arquivo `audit_report.md` documenta a conformidade de segurança da aplicação, mapeando superfícies de ataque locais de forma controlada.

---
Desenvolvido com 💙 por [Everton Kaylon](https://github.com/EvertonKaylon).
