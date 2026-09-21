# Imagem base oficial Python 3.12 Slim (Suporte nativo Multi-Arch: linux/arm64 e linux/amd64)
FROM python:3.12-slim-bookworm

# Evitar prompts interativos do apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8554

# Instalar dependências de sistema mínimas necessárias para Flet e bibliotecas de rede
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    libmpv-dev \
    mpv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar requirements primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar todo o código-fonte da aplicação
COPY . .

# Criar usuário não-privilegiado saebomuser (Princípio do Menor Privilégio - OWASP A05 / MITRE T1068 & T1611)
RUN groupadd -g 10001 saebom && \
    useradd -u 10001 -g saebom -s /bin/sh -m saebomuser

# Criar e garantir permissões para os diretórios persistentes de dados e cache de áudio
RUN mkdir -p /app/data/cache/audio /app/data/sessions /app/data/telemetry /app/data/reports && \
    chown -R saebomuser:saebom /app

# Executar como usuário não-root
USER saebomuser

# Expor a porta web padrão do Flet
EXPOSE 8554

# Healthcheck simples para verificar se o Flet server está respondendo
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8554/ || exit 1

# Comando de inicialização em modo nuvem headless
CMD ["python", "main.py"]
