<#
.SYNOPSIS
    Catalogo Completo de Comandos de Verificacion y Uso para las 33 Herramientas DevOps.
    Curso: Cloud DevOps Automatizacion y Despliegue (EducacionIT - DEVO07).
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\scripts\mostrar-todos-comandos.ps1
#>

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Write-CatHeader {
    param([string]$CatNum, [string]$Code, [string]$Name, [string]$Color)
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor DarkGray
    Write-Host " [*] CATEGORIA [$CatNum] [$Code]: $Name" -ForegroundColor $Color
    Write-Host "======================================================================" -ForegroundColor DarkGray
}

function Show-ToolCmd {
    param(
        [int]$Num,
        [string]$Name,
        [string]$VerifCmd,
        [string]$UsoCmd,
        [string]$Desc
    )
    $numStr = "[$Num]".PadRight(5)
    Write-Host " $numStr $Name" -ForegroundColor Yellow
    Write-Host "       Descripcion  : $Desc" -ForegroundColor DarkGray
    Write-Host "       Verificacion : $VerifCmd" -ForegroundColor Green
    Write-Host "       Comando tipo : $UsoCmd" -ForegroundColor Cyan
    Write-Host ""
}

Clear-Host
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   GUIA RAPIDA DE COMANDOS: ECOSISTEMA DEVOPS (33 HERRAMIENTAS)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan

Write-CatHeader "C1" "BASE" "SOFTWARE BASE OBLIGATORIO (CORE ESENCIAL)" "Yellow"
Show-ToolCmd 1  "Zoom Workplace"        "Test-Path `$env:APPDATA\Zoom\bin\Zoom.exe" "zoom" "Plataforma oficial de clases en vivo"
Show-ToolCmd 2  "Git for Windows"       "git --version" "git clone <repo> / git status / git log --oneline" "Control de versiones distribuido"
Show-ToolCmd 3  "GitHub CLI (gh)"       "gh --version" "gh auth login / gh repo create / gh pr list" "CLI oficial de GitHub y sincronizacion"
Show-ToolCmd 4  "Visual Studio Code"    "code --version" "code . / code --install-extension <ext>" "Editor principal de codigo e infraestructura"
Show-ToolCmd 5  "Docker Desktop"        "docker --version" "docker run -it alpine / docker ps / docker compose up" "Motor de contenedores Linux en Windows"
Show-ToolCmd 6  "HashiCorp Terraform"   "terraform --version" "terraform init / terraform plan / terraform apply" "Infraestructura como Codigo (IaC)"
Show-ToolCmd 7  "AWS CLI v2"            "aws --version" "aws configure / aws s3 ls / aws sts get-caller-identity" "CLI oficial para Amazon Web Services"
Show-ToolCmd 8  "Azure CLI (az)"        "az version" "az login / az account show / az group list" "CLI oficial para Microsoft Azure Cloud"
Show-ToolCmd 9  "Kubernetes (kubectl)"  "kubectl version --client" "kubectl get pods -A / kubectl apply -f deploy.yaml" "CLI para orquestacion y clusters K8s"
Show-ToolCmd 10 "Helm"                  "helm version --short" "helm repo add / helm install mi-app bitnami/nginx" "Package manager para Kubernetes"
Show-ToolCmd 11 "Minikube"              "minikube version --short" "minikube start --driver=docker / minikube dashboard" "Cluster local de Kubernetes"
Show-ToolCmd 12 "jq (JSON Processor)"   "jq --version" "cat config.json | jq .items[0] / az account show | jq" "Filtro y formateador JSON para pipelines"

Write-CatHeader "C2" "TERM" "TERMINALES, COMUNICACION Y EDITORES MODERNOS" "Green"
Show-ToolCmd 13 "Gajim (Cliente XMPP)"   "gajim --version" "gajim" "Mensajeria instantanea descentralizada y cifrada"
Show-ToolCmd 14 "Ghostty Terminal"      "ghostty --version" "ghostty" "Terminal nativa de alto rendimiento con GPU"
Show-ToolCmd 15 "Zed Editor"            "zed --version" "zed . / zed <archivo>" "Editor de codigo ultra-rapido escrito en Rust"
Show-ToolCmd 16 "Herdr (Multiplexer)"   "herdr --version" "herdr start / herdr list" "Multiplexor de terminal y workspace manager"
Show-ToolCmd 17 "Neovim"                "nvim --version" "nvim <archivo> / nvim ." "Editor modal extensible para terminal"
Show-ToolCmd 18 "VLC Media Player"      "vlc --version" "vlc <video.mp4> / vlc rtp://@..." "Reproductor para grabaciones y streaming"

Write-CatHeader "C3" "TUI" "HERRAMIENTAS TUI Y PRODUCTIVIDAD EN TERMINAL" "Cyan"
Show-ToolCmd 19 "fzf (Fuzzy Finder)"    "fzf --version" "Get-ChildItem -Recurse | fzf / git log | fzf" "Buscador difuso interactivo para consola"
Show-ToolCmd 20 "Lazygit"               "lazygit --version" "lazygit" "Interfaz visual TUI para gestionar repositorios Git"
Show-ToolCmd 21 "Yazi (TUI Files)"      "yazi --version" "yazi" "Explorador interactivo de archivos para terminal"
Show-ToolCmd 22 "Lazydocker"            "lazydocker --version" "lazydocker" "Dashboard TUI para contenedores, imagenes y volumenes"
Show-ToolCmd 23 "k9s (TUI Kubernetes)"  "k9s version" "k9s" "Consola interactiva visual para clusters Kubernetes"

Write-CatHeader "C4" "EBPF" "CONTENEDORES ALTERNATIVOS, REDES, SEGURIDAD Y EBPF" "Magenta"
Show-ToolCmd 24 "nerdctl (containerd)"  "nerdctl version" "nerdctl run -it --rm alpine / nerdctl ps" "CLI compatible con Docker para containerd"
Show-ToolCmd 25 "Cilium CLI (eBPF)"     "cilium version --client" "cilium status / cilium install / cilium connectivity test" "Plano de control y redes eBPF para Kubernetes"
Show-ToolCmd 26 "Hubble CLI (eBPF)"     "hubble version" "hubble observe / hubble status" "Observabilidad de trafico y flujos de red eBPF"
Show-ToolCmd 27 "Trivy Scanner"         "trivy --version" "trivy image nginx:alpine / trivy fs --scanners vuln ." "Escaner de vulnerabilidades y seguridad IaC"

Write-CatHeader "C5" "LANG" "LENGUAJES Y RUNTIMES DEVOPS" "White"
Show-ToolCmd 28 "Go (Golang)"           "go version" "go run main.go / go build / go test" "Lenguaje backend nativo del ecosistema Cloud Native"
Show-ToolCmd 29 "Python 3.12"           "python --version" "python script.py / python -m http.server 8000" "Scripting, automatizacion y testing DevOps"
Show-ToolCmd 30 "Rust (Rustup/Cargo)"   "rustc --version" "cargo new mi-tool / cargo build --release" "Lenguaje de sistemas para herramientas CLI ultra-rapidas"

Write-CatHeader "C6" "AI" "SUITE DE AGENTES DE INTELIGENCIA ARTIFICIAL (AIOPS)" "DarkCyan"
Show-ToolCmd 31 "Claude Code CLI"       "claude --version" "claude" "Agente autonomo de codificacion y terminal de Anthropic"
Show-ToolCmd 32 "Shell-GPT (sgpt)"      "sgpt --version" "sgpt --shell 'como filtrar procesos de docker con powershell'" "Consultas LLM directas en consola"
Show-ToolCmd 33 "OMP (Oh My Pi AI)"     "omp --version" "omp" "Agente de IA multiproposito para linea de comandos"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " [i] Para probar cualquier comando, copia y pegalo en tu terminal de PowerShell." -ForegroundColor Yellow
Write-Host ""
