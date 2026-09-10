#!/usr/bin/env bash
# ==============================================================================
# Script de Instalación Automatizada de Herramientas Cloud DevOps para macOS
# Compatible con: Apple Silicon (M1/M2/M3/M4) e Intel Mac via Homebrew
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

print_header "INSTALADOR CLOUD DEVOPS TOOLKIT PARA MACOS (HOMEBREW)"

# 1. Comprobar e instalar Homebrew si falta
if ! command -v brew &>/dev/null; then
    print_warn "Homebrew no fue detectado en tu sistema macOS."
    print_info "Instalando Homebrew automáticamente..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Configurar brew en PATH para Apple Silicon (/opt/homebrew) o Intel (/usr/local)
    if [ -f "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -f "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

print_success "Homebrew detectado: $(brew --version | head -n 1)"

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
            echo "Uso: ./instalar-tools-macos.sh [OPCIONES]"
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

# ------------------------------------------------------------------------------
# CATEGORÍA: BASE (Core Esencial)
# ------------------------------------------------------------------------------
install_base() {
    print_header "INSTALANDO SOFTWARE BASE DEVOPS EN MACOS"

    print_info "Instalando herramientas base con brew..."
    brew install git gh jq terraform awscli azure-cli kubectl helm minikube

    print_info "Instalando aplicaciones GUI con brew cask..."
    brew install --cask zoom visual-studio-code docker || true

    print_success "Categoría BASE instalada exitosamente."
}

# ------------------------------------------------------------------------------
# CATEGORÍA: TERM (Terminales y Editores)
# ------------------------------------------------------------------------------
install_term() {
    print_header "INSTALANDO TERMINALES Y EDITORES EN MACOS"

    brew install neovim
    brew install --cask ghostty zed vlc gajim || true

    # Herdr Multiplexer
    if command -v npm &>/dev/null; then
        print_info "Instalando Herdr Multiplexer..."
        npm install -g herdr || true
    fi

    print_success "Categoría TERM instalada exitosamente."
}

# ------------------------------------------------------------------------------
# CATEGORÍA: TUI (Herramientas TUI)
# ------------------------------------------------------------------------------
install_tui() {
    print_header "INSTALANDO HERRAMIENTAS TUI EN MACOS"

    brew install fzf lazygit yazi jesseduffield/lazydocker/lazydocker derailed/k9s/k9s

    print_success "Categoría TUI instalada exitosamente."
}

# ------------------------------------------------------------------------------
# CATEGORÍA: EBPF (Redes y Contenedores)
# ------------------------------------------------------------------------------
install_ebpf() {
    print_header "INSTALANDO HERRAMIENTAS EBPF Y REDES EN MACOS"

    brew install cilium-cli hubble nerdctl trivy || true

    print_success "Categoría EBPF instalada exitosamente."
}

# ------------------------------------------------------------------------------
# CATEGORÍA: LANG (Go, Python & Rust)
# ------------------------------------------------------------------------------
install_lang() {
    print_header "INSTALANDO LENGUAJES Y RUNTIMES EN MACOS (GO, PYTHON & RUST)"

    brew install go python@3.12 node rust

    print_success "Categoría LANG instalada exitosamente."
}

# ------------------------------------------------------------------------------
# CATEGORÍA: AI (Agentes IA en Terminal)
# ------------------------------------------------------------------------------
install_ai() {
    print_header "INSTALANDO SUITE DE AGENTES IA EN MACOS"

    if command -v npm &>/dev/null; then
        print_info "Instalando Claude Code CLI (@anthropic-ai/claude-code)..."
        npm install -g @anthropic-ai/claude-code || true
    fi

    if command -v pip3 &>/dev/null; then
        print_info "Instalando Shell-GPT (sgpt)..."
        pip3 install --user shell-gpt || true
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

print_header "INSTALACIÓN FINALIZADA EN MACOS"
echo -e "${GREEN}Verifica tu instalación ejecutando:${NC}"
echo -e "  ${CYAN}./scripts/verificar-tools.sh${NC}\n"
