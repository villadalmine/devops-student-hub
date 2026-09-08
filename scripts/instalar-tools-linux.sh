#!/usr/bin/env bash
# ==============================================================================
# Script de Instalación Automatizada de Herramientas Cloud DevOps para Linux
# Compatible con: Ubuntu/Debian (apt), Fedora/RHEL (dnf), Arch Linux (pacman)
# ==============================================================================

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_header() {
    echo -e "\n${CYAN}======================================================================${NC}"
    echo -e "${YELLOW}   $1${NC}"
    echo -e "${CYAN}======================================================================${NC}\n"
}

print_success() { echo -e " ${GREEN}[OK]${NC} $1"; }
print_info()    { echo -e " ${CYAN}[i]${NC}  $1"; }
print_warn()    { echo -e " ${YELLOW}[!]${NC}  $1"; }
print_error()   { echo -e " ${RED}[X]${NC}  $1"; }

detect_pm() {
    if command -v apt-get &>/dev/null; then
        PM="apt"
    elif command -v dnf &>/dev/null; then
        PM="dnf"
    elif command -v pacman &>/dev/null; then
        PM="pacman"
    else
        print_error "No se detectó un gestor de paquetes soportado (apt, dnf, pacman)."
        exit 1
    fi
}

detect_pm
print_header "INSTALADOR CLOUD DEVOPS TOOLKIT PARA LINUX ($PM)"

CATEGORIA="ALL"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --base|-b)
            CATEGORIA="BASE"
            shift
            ;;
        --categoria|-c)
            CATEGORIA="${2^^}"
            shift 2
            ;;
        --all|-a)
            CATEGORIA="ALL"
            shift
            ;;
        --help|-h)
            echo "Uso: ./instalar-tools-linux.sh [OPCIONES]"
            echo ""
            echo "Opciones:"
            echo "  --base, -b            Instala únicamente el Software Base Esencial (12 herramientas)"
            echo "  --categoria, -c <CAT> Instala una categoría específica: BASE, TERM, TUI, EBPF, LANG, AI"
            echo "  --all, -a             Instala todo el ecosistema DevOps (por defecto)"
            echo "  --help, -h            Muestra esta ayuda"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

SUDO=""
if [ "$EUID" -ne 0 ]; then
    if command -v sudo &>/dev/null; then
        SUDO="sudo"
    else
        print_error "Este script requiere privilegios de superusuario o sudo."
        exit 1
    fi
fi

print_info "Actualizando repositorios del sistema..."
if [ "$PM" == "apt" ]; then
    $SUDO apt-get update -y
    $SUDO apt-get install -y curl wget unzip gnupg ca-certificates apt-transport-https lsb-release
elif [ "$PM" == "dnf" ]; then
    $SUDO dnf check-update || true
    $SUDO dnf install -y curl wget unzip gnupg
elif [ "$PM" == "pacman" ]; then
    $SUDO pacman -Sy --noconfirm curl wget unzip
fi

install_base() {
    print_header "INSTALANDO SOFTWARE BASE DEVOPS (CORE ESENCIAL)"

    print_info "Instalando Git y jq..."
    if [ "$PM" == "apt" ]; then
        $SUDO apt-get install -y git jq
    elif [ "$PM" == "dnf" ]; then
        $SUDO dnf install -y git jq
    elif [ "$PM" == "pacman" ]; then
        $SUDO pacman -S --noconfirm git jq
    fi

    if ! command -v gh &>/dev/null; then
        print_info "Instalando GitHub CLI (gh)..."
        if [ "$PM" == "apt" ]; then
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | $SUDO dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            $SUDO chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
            echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | $SUDO tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            $SUDO apt-get update -y && $SUDO apt-get install -y gh
        elif [ "$PM" == "dnf" ]; then
            $SUDO dnf install -y 'dnf-command(config-manager)'
            $SUDO dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
            $SUDO dnf install -y gh
        elif [ "$PM" == "pacman" ]; then
            $SUDO pacman -S --noconfirm github-cli
        fi
    fi

    if ! command -v docker &>/dev/null; then
        print_info "Instalando Docker Engine..."
        curl -fsSL https://get.docker.com | $SUDO sh
        $SUDO usermod -aG docker "$USER" || true
        print_success "Docker instalado. NOTA: Cierra sesión y vuelve a entrar para usar Docker sin sudo."
    fi

    if ! command -v terraform &>/dev/null; then
        print_info "Instalando HashiCorp Terraform..."
        if [ "$PM" == "apt" ]; then
            wget -O- https://apt.releases.hashicorp.com/gpg | $SUDO gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg --yes
            echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | $SUDO tee /etc/apt/sources.list.d/hashicorp.list
            $SUDO apt-get update -y && $SUDO apt-get install -y terraform
        elif [ "$PM" == "dnf" ]; then
            $SUDO dnf install -y dnf-plugins-core
            $SUDO dnf config-manager --add-repo https://rpm.releases.hashicorp.com/fedora/hashicorp.repo
            $SUDO dnf install -y terraform
        elif [ "$PM" == "pacman" ]; then
            $SUDO pacman -S --noconfirm terraform
        fi
    fi

    if ! command -v aws &>/dev/null; then
        print_info "Instalando AWS CLI v2..."
        ARCH=$(uname -m)
        if [ "$ARCH" == "x86_64" ]; then
            AWS_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
        else
            AWS_URL="https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip"
        fi
        curl "$AWS_URL" -o "awscliv2.zip"
        unzip -q awscliv2.zip
        $SUDO ./aws/install --update || true
        rm -rf aws awscliv2.zip
    fi

    if ! command -v az &>/dev/null; then
        print_info "Instalando Azure CLI..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | $SUDO bash || true
    fi

    if ! command -v kubectl &>/dev/null; then
        print_info "Instalando kubectl..."
        K_VER=$(curl -L -s https://dl.k8s.io/release/stable.txt)
        ARCH=$(uname -m)
        [ "$ARCH" == "x86_64" ] && K_ARCH="amd64" || K_ARCH="arm64"
        curl -LO "https://dl.k8s.io/release/${K_VER}/bin/linux/${K_ARCH}/kubectl"
        $SUDO install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
        rm -f kubectl
    fi

    if ! command -v helm &>/dev/null; then
        print_info "Instalando Helm..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi

    if ! command -v minikube &>/dev/null; then
        print_info "Instalando Minikube..."
        ARCH=$(uname -m)
        [ "$ARCH" == "x86_64" ] && M_ARCH="amd64" || M_ARCH="arm64"
        curl -LO "https://storage.googleapis.com/minikube/releases/latest/minikube-linux-${M_ARCH}"
        $SUDO install "minikube-linux-${M_ARCH}" /usr/local/bin/minikube
        rm -f "minikube-linux-${M_ARCH}"
    fi

    print_success "Categoría BASE instalada exitosamente."
}

install_term() {
    print_header "INSTALANDO TERMINALES Y EDITORES"

    if [ "$PM" == "apt" ]; then
        $SUDO apt-get install -y neovim vlc gajim || true
    elif [ "$PM" == "dnf" ]; then
        $SUDO dnf install -y neovim vlc gajim || true
    elif [ "$PM" == "pacman" ]; then
        $SUDO pacman -S --noconfirm neovim vlc gajim || true
    fi

    if ! command -v zed &>/dev/null; then
        print_info "Instalando Zed Editor..."
        curl -f https://zed.dev/install.sh | sh || true
    fi

    if ! command -v herdr &>/dev/null; then
        if command -v npm &>/dev/null; then
            print_info "Instalando Herdr Multiplexer via npm..."
            $SUDO npm install -g herdr || true
        fi
    fi

    print_success "Categoría TERM instalada exitosamente."
}

install_tui() {
    print_header "INSTALANDO HERRAMIENTAS TUI"

    if [ "$PM" == "apt" ]; then
        $SUDO apt-get install -y fzf || true
    elif [ "$PM" == "dnf" ]; then
        $SUDO dnf install -y fzf || true
    elif [ "$PM" == "pacman" ]; then
        $SUDO pacman -S --noconfirm fzf || true
    fi

    if ! command -v lazygit &>/dev/null; then
        print_info "Instalando Lazygit..."
        LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
        ARCH=$(uname -m)
        curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_${ARCH}.tar.gz"
        tar xf lazygit.tar.gz lazygit
        $SUDO install lazygit /usr/local/bin
        rm -f lazygit lazygit.tar.gz
    fi

    if ! command -v lazydocker &>/dev/null; then
        print_info "Instalando Lazydocker..."
        curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash || true
    fi

    if ! command -v k9s &>/dev/null; then
        print_info "Instalando k9s..."
        K9S_VERSION=$(curl -s "https://api.github.com/repos/derailed/k9s/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
        ARCH=$(uname -m)
        [ "$ARCH" == "x86_64" ] && K9S_ARCH="amd64" || K9S_ARCH="arm64"
        curl -Lo k9s.tar.gz "https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_${K9S_ARCH}.tar.gz"
        tar xf k9s.tar.gz k9s
        $SUDO install k9s /usr/local/bin
        rm -f k9s k9s.tar.gz
    fi

    print_success "Categoría TUI instalada exitosamente."
}

install_ebpf() {
    print_header "INSTALANDO CONTENEDORES Y EBPF (CILIUM & HUBBLE)"

    if ! command -v cilium &>/dev/null; then
        print_info "Instalando Cilium CLI..."
        CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
        ARCH=$(uname -m)
        [ "$ARCH" == "x86_64" ] && C_ARCH="amd64" || C_ARCH="arm64"
        curl -L --fail --remote-name-all "https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-${C_ARCH}.tar.gz"
        $SUDO tar xzvfC "cilium-linux-${C_ARCH}.tar.gz" /usr/local/bin
        rm -f "cilium-linux-${C_ARCH}.tar.gz"
    fi

    if ! command -v hubble &>/dev/null; then
        print_info "Instalando Hubble CLI..."
        HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/master/stable.txt)
        ARCH=$(uname -m)
        [ "$ARCH" == "x86_64" ] && H_ARCH="amd64" || H_ARCH="arm64"
        curl -L --fail --remote-name-all "https://github.com/cilium/hubble/releases/download/${HUBBLE_VERSION}/hubble-linux-${H_ARCH}.tar.gz"
        $SUDO tar xzvfC "hubble-linux-${H_ARCH}.tar.gz" /usr/local/bin
        rm -f "hubble-linux-${H_ARCH}.tar.gz"
    fi

    print_success "Categoría EBPF instalada exitosamente."
}

install_lang() {
    print_header "INSTALANDO LENGUAJES Y RUNTIMES (GO & PYTHON)"

    if [ "$PM" == "apt" ]; then
        $SUDO apt-get install -y golang-go python3 python3-pip python3-venv nodejs npm
    elif [ "$PM" == "dnf" ]; then
        $SUDO dnf install -y golang python3 python3-pip nodejs npm
    elif [ "$PM" == "pacman" ]; then
        $SUDO pacman -S --noconfirm go python python-pip nodejs npm
    fi

    print_success "Categoría LANG instalada exitosamente."
}

install_ai() {
    print_header "INSTALANDO SUITE DE AGENTES DE INTELIGENCIA ARTIFICIAL"

    if command -v npm &>/dev/null; then
        print_info "Instalando Claude Code CLI (@anthropic-ai/claude-code)..."
        $SUDO npm install -g @anthropic-ai/claude-code || true
    fi

    if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
        print_info "Instalando Shell-GPT (sgpt)..."
        pip install --user shell-gpt || pip3 install --user shell-gpt || true
    fi

    if ! command -v omp &>/dev/null; then
        print_info "Instalando OMP (Oh My Pi)..."
        curl -fsSL https://omp.sh | bash || true
    fi

    print_success "Categoría AI instalada exitosamente."
}

case "$CATEGORIA" in
    "BASE")
        install_base
        ;;
    "TERM")
        install_term
        ;;
    "TUI")
        install_tui
        ;;
    "EBPF")
        install_ebpf
        ;;
    "LANG")
        install_lang
        ;;
    "AI")
        install_ai
        ;;
    "ALL")
        install_base
        install_term
        install_tui
        install_ebpf
        install_lang
        install_ai
        ;;
esac

print_header "INSTALACIÓN FINALIZADA"
echo -e "${GREEN}Verifica tu instalación ejecutando:${NC}"
echo -e "  ${CYAN}./scripts/verificar-tools.sh${NC}\n"
