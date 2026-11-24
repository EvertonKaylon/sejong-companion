#!/usr/bin/env bash
# ==============================================================================
# Script de Instalação e Deploy Automático — Saebom Companion (새봄 컴패니언) na Oracle Cloud
# Compatível com Ubuntu 22.04 / 24.04 LTS (ARM64 Ampere ou AMD64)
# ==============================================================================

set -e

echo "======================================================================"
echo " 🇰🇷 INICIANDO DEPLOY DO SAEBOM COMPANION (새봄 컴패니언) NA ORACLE CLOUD (OCI)"
echo "======================================================================"

# 1. Atualizar repositórios e pacotes do sistema
echo "📦 1/5 Atualizando pacotes do sistema..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git curl ufw ca-certificates gnupg lsb-release

# 2. Configurar Firewall do Ubuntu na OCI (Liberar apenas Portas 80 e 443 no iptables nativo)
echo "🛡️ 2/5 Configurando regras de firewall local..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT || true
sudo netfilter-persistent save 2>/dev/null || true

# 3. Instalar Docker e Docker Compose Oficial
echo "🐳 3/5 Instalando Docker Engine e Docker Compose Plugin..."
if ! command -v docker &> /dev/null; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker "$USER"
fi

# 4. Clonar ou Atualizar o Repositório do Saebom Companion (새봄 컴패니언)
echo "📂 4/5 Obtendo o código-fonte mais recente..."
REPO_DIR="$HOME/saebom-companion"
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/EvertonKaylon/sejong-companion.git "$REPO_DIR"
    cd "$REPO_DIR"
    git checkout develop
else
    cd "$REPO_DIR"
    git pull origin develop
fi

# 5. Validar Configuração Obrigatória e Iniciar os Containers Docker
echo "🔐 5/5 Validando .env e iniciando serviços (Flet + Caddy)..."
if [ ! -f ".env" ]; then
    echo "❌ ERRO: Arquivo .env não encontrado em $REPO_DIR."
    echo "   Crie o arquivo .env com SAEBOM_ADMIN_PIN antes de subir os containers:"
    echo "   echo 'SAEBOM_ADMIN_PIN=defina_um_pin_forte' > .env"
    exit 1
fi

ADMIN_PIN_VALUE="$(grep -E '^[[:space:]]*SAEBOM_ADMIN_PIN=' .env | tail -n 1 | cut -d '=' -f 2- | tr -d '\r' | sed -E 's/^["'\'']|["'\'']$//g; s/^[[:space:]]+|[[:space:]]+$//g')"
if [ -z "$ADMIN_PIN_VALUE" ]; then
    echo "❌ ERRO: SAEBOM_ADMIN_PIN não está definido ou está vazio no arquivo .env."
    echo "   O Saebom Companion opera em modo fail-closed e exige SAEBOM_ADMIN_PIN configurado."
    exit 1
fi
unset ADMIN_PIN_VALUE

sudo docker compose up -d --build

echo ""
echo "======================================================================"
echo " ✅ SAEBOM COMPANION (새봄 컴패니언) ESTÁ ONLINE NA ORACLE CLOUD!"
echo "======================================================================"
echo " • Acesse pelo navegador: https://saebomcompanion.duckdns.org"
echo " • Painel do Professor:   https://saebomcompanion.duckdns.org/admin"
echo " • Status dos containers: sudo docker compose ps"
echo " • Logs em tempo real:   sudo docker compose logs -f"
echo "======================================================================"
