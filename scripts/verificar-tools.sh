#!/usr/bin/env bash
# ==============================================================================
# Script de Diagnóstico y Verificación de Herramientas Cloud DevOps (POSIX)
# Compatible con: Linux, macOS y WSL
# ==============================================================================

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
BOLD='\033[1m'
NC='\033[0m'

TOTAL_TOOLS=0
INSTALLED_COUNT=0

check_tool() {
    local num="$1"
    local name="$2"
    local cmd="$3"
    local ver_arg="$4"
    local is_req="$5"

    TOTAL_TOOLS=$((TOTAL_TOOLS + 1))
    local ver=""
    if command -v "$cmd" &>/dev/null; then
        INSTALLED_COUNT=$((INSTALLED_COUNT + 1))
        if [ -n "$ver_arg" ]; then
            ver=$($cmd $ver_arg 2>&1 | head -n 1 | cut -c 1-35)
        else
            ver="Instalado"
        fi
        printf " ${GREEN}[OK]${NC}  %02d. %-24s ${GREEN}%-10s${NC} ${GRAY}(%s)${NC}\n" "$num" "$name" "INSTALADO" "$ver"
    else
        local badge="${GRAY}[OPTATIVO]${NC}"
        [ "$is_req" == "REQ" ] && badge="${RED}[FALTA OBLIGATORIO]${NC}"
        printf " ${RED}[--]${NC}  %02d. %-24s %b\n" "$num" "$name" "$badge"
    fi
}

echo -e "\n${CYAN}======================================================================${NC}"
echo -e "${BOLD}   DIAGNÓSTICO DEL TOOLKIT CLOUD DEVOPS (${OSTYPE})${NC}"
echo -e "${CYAN}======================================================================${NC}\n"

echo -e "${YELLOW}--- [BASE] SOFTWARE BASE DEVOPS (CORE ESENCIAL) ---${NC}"
check_tool 1  "Zoom Workplace"        "zoom"       ""                 "REQ"
check_tool 2  "Git"                   "git"        "--version"        "REQ"
check_tool 3  "GitHub CLI (gh)"       "gh"         "--version"        "REQ"
check_tool 4  "Visual Studio Code"    "code"       "--version"        "REQ"
check_tool 5  "Docker Engine/Desktop" "docker"     "--version"        "REQ"
check_tool 6  "HashiCorp Terraform"   "terraform"  "--version"        "REQ"
check_tool 7  "AWS CLI v2"            "aws"        "--version"        "REQ"
check_tool 8  "Azure CLI (az)"        "az"         "version"          "REQ"
check_tool 9  "Kubernetes CLI (kubectl)" "kubectl" "version --client" "REQ"
check_tool 10 "Helm"                  "helm"       "version --short"  "REQ"
check_tool 11 "Minikube"              "minikube"   "version --short"  "REQ"
check_tool 12 "jq (JSON Processor)"   "jq"         "--version"        "REQ"

echo -e "\n${YELLOW}--- [TERM] TERMINALES, COMUNICACIÓN & EDITORES ---${NC}"
check_tool 13 "Gajim (XMPP)"          "gajim"      "--version"        "OPT"
check_tool 14 "Ghostty Terminal"      "ghostty"    "--version"        "OPT"
check_tool 15 "Zed Editor"            "zed"        "--version"        "OPT"
check_tool 16 "Herdr Multiplexer"     "herdr"      "--version"        "OPT"
check_tool 17 "Neovim"                "nvim"       "--version"        "OPT"
check_tool 18 "VLC Media Player"      "vlc"        "--version"        "OPT"

echo -e "\n${YELLOW}--- [TUI] HERRAMIENTAS TUI Y PRODUCTIVIDAD ---${NC}"
check_tool 19 "fzf (Fuzzy Finder)"    "fzf"        "--version"        "OPT"
check_tool 20 "Lazygit"               "lazygit"    "--version"        "OPT"
check_tool 21 "Yazi (File Manager)"   "yazi"       "--version"        "OPT"
check_tool 22 "Lazydocker"            "lazydocker" "--version"        "OPT"
check_tool 23 "k9s (K8s Monitor)"     "k9s"        "version"          "OPT"

echo -e "\n${YELLOW}--- [EBPF] CONTENEDORES, REDES & EBPF ---${NC}"
check_tool 24 "nerdctl (containerd)"  "nerdctl"    "version"          "OPT"
check_tool 25 "Cilium CLI"            "cilium"     "version --client" "OPT"
check_tool 26 "Hubble CLI"            "hubble"     "version"          "OPT"
check_tool 27 "Trivy (Security)"      "trivy"      "--version"        "OPT"

echo -e "\n${YELLOW}--- [LANG] LENGUAJES & RUNTIMES ---${NC}"
check_tool 28 "Go (Golang)"           "go"         "version"          "OPT"
check_tool 29 "Python 3"              "python3"    "--version"        "OPT"
check_tool 30 "Rust (rustc/cargo)"    "rustc"      "--version"        "OPT"

echo -e "\n${YELLOW}--- [AI] AGENTES IA EN TERMINAL ---${NC}"
check_tool 31 "Claude Code CLI"       "claude"     "--version"        "OPT"
check_tool 32 "Shell-GPT (sgpt)"      "sgpt"       "--version"        "OPT"
check_tool 33 "OMP (Oh My Pi)"        "omp"        "--version"        "OPT"

echo -e "\n${CYAN}======================================================================${NC}"
PERCENT=$(( (INSTALLED_COUNT * 100) / TOTAL_TOOLS ))
echo -e " Resumen: ${BOLD}${INSTALLED_COUNT} / ${TOTAL_TOOLS}${NC} herramientas instaladas (${PERCENT}% completado)"
echo -e "${CYAN}======================================================================${NC}\n"
