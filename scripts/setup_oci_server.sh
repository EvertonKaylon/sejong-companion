#!/usr/bin/env bash
# ==============================================================================
# Script de Instalação e Deploy Automático — Sejong Companion na Oracle Cloud
# Compatível com Ubuntu 22.04 / 24.04 LTS (ARM64 Ampere ou AMD64)
# ==============================================================================

set -e

echo "======================================================================"
echo " 🇰🇷 INICIANDO DEPLOY DO SEJONG COMPANION NA ORACLE CLOUD (OCI)"
echo "======================================================================"

# 1. Atualizar repositórios e pacotes do sistema
echo "📦 1/5 Atualizando pacotes do sistema..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y git curl ufw ca-certificates gnupg lsb-release

# 2. Configurar Firewall do Ubuntu na OCI (Liberar Portas 80 e 443 no iptables nativo da Oracle)
echo "🛡️ 2/5 Configurando regras de firewall local..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT || true
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8554 -j ACCEPT || true
sudo netfilter-persistent save 2>/dev/null || true

# 3. Instalar Docker e Docker Compose Oficial
echo "🐳 3/5 Instalando Docker Engine e Docker Compose Plugin..."
if ! command -v docker &> /dev/null; then
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
fi

# 4. Clonar ou Atualizar o Repositório do Sejong Companion
echo "📂 4/5 Obtendo o código-fonte mais recente..."
REPO_DIR="$HOME/sejong-companion"
if [ ! -d "$REPO_DIR" ]; then
    git clone https://github.com/EvertonKaylon/sejong-companion.git "$REPO_DIR"
    cd "$REPO_DIR"
    git checkout develop
else
    cd "$REPO_DIR"
    git pull origin develop
fi

# 5. Construir e Iniciar os Containers Docker
echo "🚀 5/5 Construindo imagem e iniciando serviços (Flet + Caddy)..."
sudo docker compose up -d --build

echo ""
echo "======================================================================"
echo " ✅ SEJONG COMPANION ESTÁ ONLINE NA ORACLE CLOUD!"
echo "======================================================================"
echo " • Acesse pelo navegador: http://$(curl -s ifconfig.me)"
echo " • Painel do Professor:   http://$(curl -s ifconfig.me)/admin"
echo " • Status dos containers: sudo docker compose ps"
echo " • Logs em tempo real:   sudo docker compose logs -f"
echo "======================================================================"
