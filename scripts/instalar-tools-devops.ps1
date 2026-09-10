<#
.SYNOPSIS
    Script de Instalacion Automatizada de Herramientas Cloud DevOps para Windows.
    Entorno y Toolkit de Automatizacion Cloud DevOps para Windows.

.DESCRIPTION
    Escanea el sistema previamente, marca visualmente que herramientas ya estan instaladas
    para evitar reinstalarlas y ofrece opciones de instalacion por categorias o seleccion:
      1) Solo Software Base DevOps (Core Esencial) (Zoom, Git, GitHub CLI (gh), VS Code, Docker, Terraform, AWS CLI, Azure CLI, Kubectl, Helm, Minikube, jq).
      2) Ecosistema Completo (Obligatorio + Todas las herramientas optativas).
      3) Seleccion Personalizada por Categorias o Numeros (ej: 'BASE', 'AI', 'TERM', 'TUI', 'EBPF', 'LANG', '1-33').

.PARAMETER SoloObligatorio
    Si se activa, gestiona UNICAMENTE el software oficial requerido por DevOps.

.PARAMETER Completo
    Si se activa, gestiona todo el ecosistema (Obligatorio + Optativos).

.PARAMETER Categoria
    Instala directamente una o mas categorias: BASE, TERM, TUI, EBPF, LANG, AI.

.PARAMETER AutoApprove
    Instala sin solicitar confirmacion interactiva.

.EXAMPLE
    # Menu interactivo inteligente:
    powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1

    # Instalar Software Base Obligatorio (AWS CLI + Azure CLI + K8s + jq):
    powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -SoloObligatorio
#>

[CmdletBinding()]
param (
    [Alias("SoloBase", "Base", "Core")]
    [switch]$SoloObligatorio = $false,
    [switch]$Completo = $false,
    [string]$Categoria = "",
    [switch]$AutoApprove = $true,       # Por defecto true: automático sin confirmaciones redundantes
    [switch]$Menu = $false,             # Solo abre menú si se pasa explícitamente -Menu
    [switch]$SkipExtensions = $false
)

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "   $Text" -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Success {
    param([string]$Text)
    Write-Host " [OK] $Text" -ForegroundColor Green
}

function Write-WarningMsg {
    param([string]$Text)
    Write-Host " [!]  $Text" -ForegroundColor Yellow
}

function Write-ErrorMsg {
    param([string]$Text)
    Write-Host " [X]  $Text" -ForegroundColor Red
}

function Write-Info {
    param([string]$Text)
    Write-Host " [i]  $Text" -ForegroundColor Cyan
}

# 1. VERIFICACION DE PRIVILEGIOS DE ADMINISTRADOR CON AUTO-ELEVACION TRANSPARENTE (UAC)
Write-Header "VERIFICACION DE PRIVILEGIOS DEL SISTEMA"

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-WarningMsg "Este instalador requiere permisos de Administrador para instalar software en Windows (winget)."
    Write-Host " [*] Elevando automáticamente a Administrador mediante Control de Cuentas de Usuario (UAC)..." -ForegroundColor Green
    Write-Host " [!] Por favor, haz clic en 'SÍ' en la ventana emergente de Windows para continuar." -ForegroundColor Yellow
    Write-Host ""

    # Reconstruir parametros para el proceso elevado
    $paramList = @()
    if ($SoloObligatorio) { 
        $paramList += "-SoloBase" 
    } elseif ($Completo) { 
        $paramList += "-Completo" 
    } elseif (-not [string]::IsNullOrWhiteSpace($Categoria)) { 
        $paramList += "-Categoria `"$Categoria`"" 
    }
    if ($AutoApprove) { $paramList += "-AutoApprove" }
    if ($SkipExtensions) { $paramList += "-SkipExtensions" }
    
    $scriptPath = $PSCommandPath
    if (-not $scriptPath) {
        $scriptPath = (Resolve-Path ".\instalar-tools-devops.ps1" -ErrorAction SilentlyContinue).Path
        if (-not $scriptPath) {
            $scriptPath = (Resolve-Path ".\scripts\instalar-tools-devops.ps1" -ErrorAction SilentlyContinue).Path
        }
    }
    
    if ($scriptPath -and (Test-Path $scriptPath)) {
        $fullArgs = "-NoExit -ExecutionPolicy Bypass -File `"$scriptPath`" " + ($paramList -join " ")
        try {
            Start-Process powershell.exe -Verb RunAs -ArgumentList $fullArgs
            Write-Success "Ventana de instalación de Administrador iniciada correctamente."
            Write-Host " [i] Continúa en la ventana de Administrador abierta." -ForegroundColor Cyan
            Exit 0
        } catch {
            Write-ErrorMsg "El diálogo UAC fue cancelado o no se concedieron permisos de Administrador."
            Write-WarningMsg "Para abrir una consola de Administrador directamente desde PowerShell, ejecuta:"
            Write-Host "   Start-Process powershell -Verb RunAs" -ForegroundColor Yellow
            Exit 1
        }
    } else {
        Write-ErrorMsg "No se pudo determinar la ruta del script para la auto-elevación."
        Write-WarningMsg "Por favor, haz clic derecho sobre PowerShell y selecciona 'Ejecutar como Administrador'."
        Exit 1
    }
}
Write-Success "Permisos de Administrador verificados correctamente."

# 2. VERIFICACION DE WINGET Y REFRESCO DE PATH
Write-Info "Comprobando Windows Package Manager (winget)..."
$wingetCmd = Get-Command "winget" -ErrorAction SilentlyContinue
if (-not $wingetCmd) {
    Write-ErrorMsg "No se encontro 'winget' en tu sistema."
    Write-WarningMsg "Instalalo desde Microsoft Store actualizando 'Instalador de aplicaciones' o desde:"
    Write-WarningMsg "https://github.com/microsoft/winget-cli/releases"
    Exit 1
}
$wingetVer = (& winget --version 2>&1 | Out-String).Trim()
Write-Success "winget detectado: Version $wingetVer"

# Refrescar PATH en memoria para detectar herramientas recien instaladas
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$wingetLinks = "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
if (Test-Path $wingetLinks) { $env:Path += ";$wingetLinks" }
$azurePath = "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin"
if (Test-Path $azurePath) { $env:Path += ";$azurePath" }
$zedPath = "$env:LOCALAPPDATA\Programs\Zed\bin"
if (Test-Path $zedPath) { $env:Path += ";$zedPath" }
$agyPath = "$env:LOCALAPPDATA\agy\bin"
if (Test-Path $agyPath) { $env:Path += ";$agyPath" }
$npmPath = "$env:APPDATA\npm"
if (Test-Path $npmPath) { $env:Path += ";$npmPath" }
$vlcPath = "C:\Program Files\VideoLAN\VLC"
if (Test-Path $vlcPath) { $env:Path += ";$vlcPath" }
$vlcPath86 = "C:\Program Files (x86)\VideoLAN\VLC"
if (Test-Path $vlcPath86) { $env:Path += ";$vlcPath86" }
$gajimPath = "C:\Program Files\Gajim\bin"
if (Test-Path $gajimPath) { $env:Path += ";$gajimPath" }
$gajimPath86 = "C:\Program Files (x86)\Gajim\bin"
if (Test-Path $gajimPath86) { $env:Path += ";$gajimPath86" }
$ciliumPath = "$env:LOCALAPPDATA\cilium\bin"
if (Test-Path $ciliumPath) { $env:Path += ";$ciliumPath" }
$nerdctlPath = "$env:LOCALAPPDATA\nerdctl\bin"
if (Test-Path $nerdctlPath) { $env:Path += ";$nerdctlPath" }
$ghosttyPath = "$env:LOCALAPPDATA\Programs\ghostty"
if (Test-Path $ghosttyPath) { $env:Path += ";$ghosttyPath" }
$goPath = "C:\Program Files\Go\bin"
if (Test-Path $goPath) { $env:Path += ";$goPath" }
$cargoPath = "$env:USERPROFILE\.cargo\bin"
if (Test-Path $cargoPath) { $env:Path += ";$cargoPath" }

# 3. CATALOGO COMPLETO DE HERRAMIENTAS CATEGORIZADAS (33 TOOLS)
$allTools = @(
    # --- [BASE] SOFTWARE BASE DEVOPS (CORE ESENCIAL) ---
    @{ IdNum=1;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Zoom Workplace"; Id="Zoom.Zoom"; Command="zoom"; VersionArg=""; Description="Videoconferencias y comunicacion de equipo"; InstallerType="winget"; Tipo="Obligatorio"; CustomCheck={ Test-Path "$env:APPDATA\Zoom\bin\Zoom.exe", "C:\Program Files\Zoom\bin\Zoom.exe", "$env:LOCALAPPDATA\Zoom\bin\Zoom.exe" } },
    @{ IdNum=2;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Git for Windows"; Id="Git.Git"; Command="git"; VersionArg="--version"; Description="Control de versiones distribuido"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=3;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="GitHub CLI (gh)"; Id="GitHub.cli"; Command="gh"; VersionArg="--version"; Description="CLI oficial de GitHub para autenticar cuenta (gh auth login) y sincronizar repositorios"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=4;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Visual Studio Code"; Id="Microsoft.VisualStudioCode"; Command="code"; VersionArg="--version"; Description="Editor principal de codigo e infraestructura"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=5;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Docker Desktop"; Id="Docker.DockerDesktop"; Command="docker"; VersionArg="--version"; Description="Motor de Contenerizacion Linux en Windows"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=6;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="HashiCorp Terraform"; Id="Hashicorp.Terraform"; Command="terraform"; VersionArg="--version"; Description="Infraestructura como Codigo - IaC"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=7;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="AWS CLI (v2)"; Id="Amazon.AWSCLI"; Command="aws"; VersionArg="--version"; Description="CLI oficial para Amazon Web Services"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=8;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Azure CLI (az)"; Id="Microsoft.AzureCLI"; Command="az"; VersionArg="version"; Description="CLI oficial para Microsoft Azure Cloud"; InstallerType="winget"; Tipo="Obligatorio"; CustomCheck={ (Get-Command "az" -ErrorAction SilentlyContinue) -or (Test-Path "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd") } },
    @{ IdNum=9;  Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Kubernetes CLI (kubectl)"; Id="Kubernetes.kubectl"; Command="kubectl"; VersionArg="version --client"; Description="CLI para orquestacion de K8s"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=10; Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Helm"; Id="Helm.Helm"; Command="helm"; VersionArg="version --short"; Description="Package manager para Kubernetes"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=11; Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="Minikube"; Id="Kubernetes.minikube"; Command="minikube"; VersionArg="version --short"; Description="Cluster local de Kubernetes"; InstallerType="winget"; Tipo="Obligatorio" },
    @{ IdNum=12; Categoria="BASE"; CatNombre="Software Base DevOps (Core Esencial)"; Name="jq (JSON Processor)"; Id="jqlang.jq"; Command="jq"; VersionArg="--version"; Description="Procesador y filtro de JSON para scripts DevOps"; InstallerType="winget"; Tipo="Obligatorio"; CustomCheck={ (Get-Command "jq" -ErrorAction SilentlyContinue) -or (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe") } },

    # --- [TERM] TERMINALES, COMUNICACION & EDITORES MODERNOS ---
    @{ IdNum=13; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="Gajim (Cliente XMPP)"; Id="Gajim.Gajim"; Command="gajim"; VersionArg="--version"; Description="Cliente XMPP moderno para mensajeria segura y cifrada"; InstallerType="winget"; Tipo="Optativo"; CustomCheck={ (Get-Command "gajim" -ErrorAction SilentlyContinue) -or (Test-Path "C:\Program Files\Gajim\bin\Gajim.exe", "C:\Program Files (x86)\Gajim\bin\Gajim.exe", "$env:LOCALAPPDATA\Programs\Gajim\bin\Gajim.exe") } },
    @{ IdNum=14; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="Ghostty Terminal"; Id="AmanThanvi.winghostty"; Command="ghostty"; VersionArg="--version"; Description="Terminal nativa acelerada por GPU"; InstallerType="winget"; Tipo="Optativo"; CustomCheck={ (Get-Command "ghostty" -ErrorAction SilentlyContinue) -or (Get-Command "ghostly" -ErrorAction SilentlyContinue) -or (Get-Command "winghostty" -ErrorAction SilentlyContinue) -or (Test-Path "$env:LOCALAPPDATA\Programs\ghostty\ghostty.exe", "$env:ProgramFiles\Ghostty\ghostty.exe") } },
    @{ IdNum=15; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="Zed Editor"; Id="ZedIndustries.Zed"; Command="zed"; VersionArg="--version"; Description="Editor ultra-rapido en Rust con soporte de IA"; InstallerType="winget"; Tipo="Optativo"; CustomCheck={ Test-Path "$env:LOCALAPPDATA\Programs\Zed\Zed.exe", "$env:LOCALAPPDATA\Programs\Zed\bin\zed.exe" } },
    @{ IdNum=16; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="Herdr (Multiplexer)"; Id="Herdr"; Command="herdr"; VersionArg="--version"; Description="Workspace Manager tematico para terminal"; InstallerType="herdr"; Tipo="Optativo" },
    @{ IdNum=17; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="Neovim (Modal Editor)"; Id="Neovim.Neovim"; Command="nvim"; VersionArg="--version"; Description="Editor modal extensible"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=18; Categoria="TERM"; CatNombre="Terminales y Editores Modernos"; Name="VLC Media Player"; Id="VideoLAN.VLC"; Command="vlc"; VersionArg="--version"; Description="Reproductor multimedia para streams de video"; InstallerType="winget"; Tipo="Optativo"; CustomCheck={ Test-Path "C:\Program Files\VideoLAN\VLC\vlc.exe", "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" } },

    # --- [TUI] HERRAMIENTAS TUI Y PRODUCTIVIDAD ---
    @{ IdNum=19; Categoria="TUI"; CatNombre="Herramientas TUI y Productividad"; Name="fzf (Fuzzy Finder)"; Id="junegunn.fzf"; Command="fzf"; VersionArg="--version"; Description="Buscador interactivo difuso para terminal"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=20; Categoria="TUI"; CatNombre="Herramientas TUI y Productividad"; Name="Lazygit (TUI Git)"; Id="JesseDuffield.lazygit"; Command="lazygit"; VersionArg="--version"; Description="Visor visual TUI para Git"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=21; Categoria="TUI"; CatNombre="Herramientas TUI y Productividad"; Name="Yazi (TUI Files)"; Id="sxyazi.yazi"; Command="yazi"; VersionArg="--version"; Description="Explorador de archivos TUI en Rust"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=22; Categoria="TUI"; CatNombre="Herramientas TUI y Productividad"; Name="Lazydocker (TUI Docker)"; Id="JesseDuffield.Lazydocker"; Command="lazydocker"; VersionArg="--version"; Description="Visor TUI para Docker"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=23; Categoria="TUI"; CatNombre="Herramientas TUI y Productividad"; Name="k9s (TUI Kubernetes)"; Id="Derailed.k9s"; Command="k9s"; VersionArg="version"; Description="Monitor interactivo para Kubernetes"; InstallerType="winget"; Tipo="Optativo" },

    # --- [EBPF] CONTENEDORES, REDES, SEGURIDAD & EBPF ---
    @{ IdNum=24; Categoria="EBPF"; CatNombre="Contenedores Alternativos, Redes, Seguridad y eBPF"; Name="nerdctl (containerd CLI)"; Id="containerd.nerdctl"; Command="nerdctl"; VersionArg="version"; Description="CLI compatible con Docker para containerd"; InstallerType="nerdctl"; Tipo="Optativo"; CustomCheck={ (Get-Command "nerdctl" -ErrorAction SilentlyContinue) -or (Get-Command "nerctl" -ErrorAction SilentlyContinue) } },
    @{ IdNum=25; Categoria="EBPF"; CatNombre="Contenedores Alternativos, Redes, Seguridad y eBPF"; Name="Cilium CLI (eBPF)"; Id="Cilium.CiliumCLI"; Command="cilium"; VersionArg="version --client"; Description="CLI oficial de Cilium para redes y eBPF en K8s"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=26; Categoria="EBPF"; CatNombre="Contenedores Alternativos, Redes, Seguridad y eBPF"; Name="Hubble CLI (eBPF)"; Id="Cilium.Hubble"; Command="hubble"; VersionArg="version"; Description="CLI de Hubble para observabilidad de red con eBPF"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=27; Categoria="EBPF"; CatNombre="Contenedores Alternativos, Redes, Seguridad y eBPF"; Name="Trivy (Vulnerability Scanner)"; Id="AquaSecurity.Trivy"; Command="trivy"; VersionArg="--version"; Description="Escaner de vulnerabilidades y seguridad para contenedores, K8s e IaC"; InstallerType="winget"; Tipo="Optativo" },

    # --- [LANG] LENGUAJES & RUNTIMES DEVOPS ---
    @{ IdNum=28; Categoria="LANG"; CatNombre="Lenguajes de Programacion y Runtimes"; Name="Go (Golang)"; Id="GoLang.Go"; Command="go"; VersionArg="version"; Description="Lenguaje Go para herramientas K8s, Docker y eBPF"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=29; Categoria="LANG"; CatNombre="Lenguajes de Programacion y Runtimes"; Name="Python 3.12"; Id="Python.Python.3.12"; Command="python"; VersionArg="--version"; Description="Lenguaje Python para scripting y automatizacion DevOps"; InstallerType="winget"; Tipo="Optativo" },
    @{ IdNum=30; Categoria="LANG"; CatNombre="Lenguajes de Programacion y Runtimes"; Name="Rust (Rustup / Cargo)"; Id="Rustlang.Rustup"; Command="rustc"; VersionArg="--version"; Description="Lenguaje de sistemas moderno para herramientas Cloud y CLI de alto rendimiento"; InstallerType="winget"; Tipo="Optativo" },

    # --- [AI] SUITE DE AGENTES DE INTELIGENCIA ARTIFICIAL ---
    @{ IdNum=31; Categoria="AI"; CatNombre="Suite de Agentes de Inteligencia Artificial"; Name="Claude Code CLI"; Id="@anthropic-ai/claude-code"; Command="claude"; VersionArg="--version"; Description="Agente autonomo de Anthropic en terminal"; InstallerType="npm"; Tipo="Optativo" },
    @{ IdNum=32; Categoria="AI"; CatNombre="Suite de Agentes de Inteligencia Artificial"; Name="OpenAI GPT CLI (Shell-GPT)"; Id="shell-gpt"; Command="sgpt"; VersionArg="--version"; Description="CLI para consultas a OpenAI"; InstallerType="pip"; Tipo="Optativo" },
    @{ IdNum=33; Categoria="AI"; CatNombre="Suite de Agentes de Inteligencia Artificial"; Name="OMP (Oh My Pi AI Agent)"; Id="OMP"; Command="omp"; VersionArg="--version"; Description="Agente de IA para terminal (omp.sh)"; InstallerType="omp"; Tipo="Optativo" }
)

# 4. ESCANEO PREVIO DEL SISTEMA (MARCAJE EN VIVO DE ESTADO)
foreach ($t in $allTools) {
    $isInst = $false
    $cmd = Get-Command $t.Command -ErrorAction SilentlyContinue
    if (-not $cmd -and $t.Command -eq "ghostty") {
        $cmd = (Get-Command "ghostly" -ErrorAction SilentlyContinue)
        if (-not $cmd) { $cmd = (Get-Command "winghostty" -ErrorAction SilentlyContinue) }
    }

    if ($cmd) {
        $isInst = $true
    } elseif ($t.CustomCheck -and (& $t.CustomCheck)) {
        $isInst = $true
    }
    $t["IsInstalled"] = $isInst

    if ($isInst) {
        try {
            if ($t.Command -eq "az") {
                $rawOut = (& az version 2>&1 | Out-String)
                if ($rawOut -match '"azure-cli":\s*"([^"]+)"') {
                    $t["VersionText"] = "v$($matches[1])"
                } else {
                    $t["VersionText"] = "Instalado"
                }
            } elseif ($t.Command -eq "jq" -and -not $cmd -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe")) {
                $rawOut = (& "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe" --version 2>&1 | Out-String).Trim()
                $t["VersionText"] = $rawOut
            } elseif ($t.Name -like "*VLC*" -and (Test-Path "C:\Program Files\VideoLAN\VLC\vlc.exe")) {
                $vlcVer = (Get-Item "C:\Program Files\VideoLAN\VLC\vlc.exe").VersionInfo.ProductVersion -replace ',', '.'
                $t["VersionText"] = "v$vlcVer"
            } elseif ($t.Name -like "*Gajim*" -and (Test-Path "C:\Program Files\Gajim\bin\Gajim.exe")) {
                $verRaw = (Get-Item "C:\Program Files\Gajim\bin\Gajim.exe").VersionInfo.ProductVersion
                $t["VersionText"] = "v$verRaw"
            } elseif ($t.VersionArg -and $cmd) {
                $rawOut = (& $cmd ($t.VersionArg -split ' ') 2>&1 | Out-String).Trim()
                $line = ($rawOut -split "`r?`n")[0]
                if ($line.Length -gt 32) { $line = $line.Substring(0, 29) + "..." }
                $t["VersionText"] = $line
            } else {
                $t["VersionText"] = "Instalado"
            }
        } catch {
            $t["VersionText"] = "Instalado"
        }
    } else {
        $t["VersionText"] = "No instalado"
    }
}

# 5. MENU DE SELECCION (OPCIONES 1, 2 O 3 / PARAMETROS)
$selectedTools = @()

if ($SoloObligatorio) {
    $selectedTools = $allTools | Where-Object { $_.Categoria -eq "BASE" }
    Write-Info "Modo directo: SOFTWARE BASE DEVOPS (CORE ESENCIAL)."
} elseif ($Completo) {
    $selectedTools = $allTools
    Write-Info "Modo directo: ECOSISTEMA COMPLETO (33 Herramientas)."
} elseif (-not [string]::IsNullOrWhiteSpace($Categoria)) {
    $catList = $Categoria.ToUpper() -split '[, ]+' | Where-Object { $_ -ne "" }
    $selectedTools = $allTools | Where-Object { $catList -contains $_.Categoria }
    Write-Info "Modo directo: CATEGORIAS ($($catList -join ', '))."
} else {
    Write-Header "SELECCION DE TIPO DE INSTALACION"
    Write-Host " [1] Solo Software Base DevOps (Core Esencial) [1-12]" -ForegroundColor Green
    Write-Host "     -> Zoom, Git, gh, VS Code, Docker, Terraform, AWS CLI, Azure CLI, Kubectl, Helm, Minikube, jq" -ForegroundColor Gray
    Write-Host ""
    Write-Host " [2] Ecosistema Completo (Instalar todas las 33 herramientas)" -ForegroundColor Cyan
    Write-Host "     -> Core + Terminales (Zed, WezTerm, Ghostty), TUIs, Redes eBPF, Lenguajes (Go, Rust), Suite IA" -ForegroundColor Gray
    Write-Host ""
    Write-Host " [3] Seleccion por Categorias o Numeros (Elige que bloques instalar)" -ForegroundColor Magenta
    Write-Host "     -> Categorias [C1] a [C6] o rango de numeros (ej: 'C4', 'C1, C4', '13-33')" -ForegroundColor Gray
    Write-Host ""
    Write-Host " [4] Ver Comandos de Todas las Herramientas (Cheat Sheet de verificacion y uso)" -ForegroundColor Yellow
    Write-Host "     -> Muestra la guia de comandos rapidos de cada una de las 33 herramientas" -ForegroundColor Gray
    Write-Host ""
    Write-Host " [5] Salir (Sin realizar cambios)" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Selecciona una opcion [1, 2, 3, 4 o 5] (Enter = Opcion 1 Base): " -ForegroundColor Yellow -NoNewline
    $modeChoice = Read-Host

    if ($modeChoice -eq "2") {
        $selectedTools = $allTools
        Write-Info "Has seleccionado: ECOSISTEMA COMPLETO."
    } elseif ($modeChoice -eq "3") {
        Write-Header "CATALOGO DE HERRAMIENTAS AGRUPADAS POR CATEGORIA"
        
        $categoriesInfo = @(
            @{ Num=1; Code="BASE"; Name="SOFTWARE BASE DEVOPS (CORE ESENCIAL)"; Color="Yellow"; Range="1 - 12" },
            @{ Num=2; Code="TERM"; Name="TERMINALES, COMUNICACION Y EDITORES"; Color="Green"; Range="13 - 18" },
            @{ Num=3; Code="TUI";  Name="HERRAMIENTAS TUI Y PRODUCTIVIDAD"; Color="Cyan"; Range="19 - 23" },
            @{ Num=4; Code="EBPF"; Name="CONTENEDORES, REDES, SEGURIDAD Y EBPF"; Color="Magenta"; Range="24 - 27" },
            @{ Num=5; Code="LANG"; Name="LENGUAJES Y RUNTIMES DEVOPS"; Color="White"; Range="28 - 30" },
            @{ Num=6; Code="AI";   Name="SUITE DE AGENTES DE IA (AIOPS)"; Color="DarkCyan"; Range="31 - 33" }
        )

        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host " RESUMEN DE CATEGORIAS DISPONIBLES (Puedes elegir por C1..C6 o Nombre):" -ForegroundColor Yellow
        foreach ($ci in $categoriesInfo) {
            $catTools = $allTools | Where-Object { $_.Categoria -eq $ci.Code }
            $instCount = ($catTools | Where-Object { $_.IsInstalled }).Count
            $totCount = $catTools.Count
            $catTag = "  [C$($ci.Num)]".PadRight(8)
            $codeTag = "[$($ci.Code)]".PadRight(8)
            $nameStr = "$($ci.Name) (Herramientas $($ci.Range))".PadRight(50)
            Write-Host "$catTag $codeTag $nameStr [$instCount/$totCount instaladas]" -ForegroundColor $ci.Color
        }
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host ""

        foreach ($cat in $categoriesInfo) {
            $catTools = $allTools | Where-Object { $_.Categoria -eq $cat.Code }
            $installedCount = ($catTools | Where-Object { $_.IsInstalled }).Count
            $totalCount = $catTools.Count
            
            Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
            Write-Host " [*] CATEGORIA [C$($cat.Num)] [$($cat.Code)]: $($cat.Name)  (Instaladas: $installedCount/$totalCount)" -ForegroundColor $cat.Color
            Write-Host "----------------------------------------------------------------------" -ForegroundColor DarkGray
            
            foreach ($t in $catTools) {
                $numPadded = "[$($t.IdNum)]".PadRight(5)
                $namePadded = $t.Name.PadRight(28)
                if ($t.IsInstalled) {
                    Write-Host "   $numPadded $namePadded [YA INSTALADO: $($t.VersionText)]" -ForegroundColor Green
                } else {
                    Write-Host "   $numPadded $namePadded [PENDIENTE]" -ForegroundColor Yellow
                }
            }
            Write-Host ""
        }

        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host " COMO SELECCIONAR:" -ForegroundColor Yellow
        Write-Host "  * Por Numero de Categoria : Ingresa 'C1', 'C2', 'C3', 'C4', 'C5', 'C6'" -ForegroundColor White
        Write-Host "  * Varias Categorias juntas: 'C1, C4' o 'BASE, EBPF, AI'" -ForegroundColor White
        Write-Host "  * Por Codigo de Categoria : 'BASE', 'TERM', 'TUI', 'EBPF', 'LANG', 'AI'" -ForegroundColor White
        Write-Host "  * Por Numeros de Tools    : '1-12', '13-18', '24, 25', '1-33'" -ForegroundColor White
        Write-Host "  * Combinado               : 'C4, 14, 20'" -ForegroundColor White
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host "Tu seleccion: " -ForegroundColor Yellow -NoNewline
        $customInput = Read-Host

        if ([string]::IsNullOrWhiteSpace($customInput)) {
            Write-WarningMsg "No seleccionaste nada. Se evaluara el Software Base Obligatorio por defecto."
            $selectedTools = $allTools | Where-Object { $_.Categoria -eq "BASE" }
        } else {
            $chosenTools = @()
            $tokens = $customInput.ToUpper() -split '[, ]+' | Where-Object { $_ -ne "" }
            
            foreach ($token in $tokens) {
                # 1. Si es seleccion por categoria C1..C6 o CAT1..CAT6
                if ($token -match '^C(?:AT)?([1-6])$') {
                    $cNum = [int]$matches[1]
                    $targetCat = $categoriesInfo | Where-Object { $_.Num -eq $cNum }
                    if ($targetCat) {
                        $chosenTools += ($allTools | Where-Object { $_.Categoria -eq $targetCat.Code })
                    }
                }
                # 2. Si es codigo de categoria directo (ej: BASE, AI, EBPF)
                elseif ($allTools | Where-Object { $_.Categoria -eq $token }) {
                    $chosenTools += ($allTools | Where-Object { $_.Categoria -eq $token })
                }
                # 3. Si es rango de numeros (ej: 10-15)
                elseif ($token -match '^(\d+)-(\d+)$') {
                    $start = [int]$matches[1]
                    $end = [int]$matches[2]
                    $chosenTools += ($allTools | Where-Object { $_.IdNum -ge $start -and $_.IdNum -le $end })
                }
                # 4. Si es numero individual (ej: 10)
                elseif ($token -match '^\d+$') {
                    $idNum = [int]$token
                    $chosenTools += ($allTools | Where-Object { $_.IdNum -eq $idNum })
                }
                # 5. Si pide 'ALL' o 'TODO'
                elseif ($token -in @("ALL", "TODO", "*")) {
                    $chosenTools += $allTools
                }
            }

            # Eliminar duplicados
            $selectedTools = $chosenTools | Select-Object -Unique
            
            if ($selectedTools.Count -eq 0) {
                Write-WarningMsg "Seleccion invalida. Se evaluara el Software Base Obligatorio por defecto."
                $selectedTools = $allTools | Where-Object { $_.Categoria -eq "BASE" }
            } else {
                Write-Success "Has seleccionado $($selectedTools.Count) herramientas para procesar."
            }
        }
    } elseif ($modeChoice -eq "4") {
        $curDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        if (-not $curDir) { $curDir = $PWD.Path }
        $cmdScript = Join-Path $curDir "mostrar-todos-comandos.ps1"
        if (-not (Test-Path $cmdScript)) {
            $cmdScript = Join-Path $curDir "scripts\mostrar-todos-comandos.ps1"
        }
        if (Test-Path $cmdScript) {
            & powershell -ExecutionPolicy Bypass -File $cmdScript
        } else {
            Write-WarningMsg "No se encontro el script de comandos en $cmdScript"
        }
        Write-Host "Presiona cualquier tecla para salir..." -ForegroundColor Gray
        [Console]::ReadKey($true) | Out-Null
        Exit 0
    } elseif ($modeChoice -eq "5") {
        Write-WarningMsg "Saliendo del instalador."
        Exit 0
    } else {
        $selectedTools = $allTools | Where-Object { $_.Categoria -eq "BASE" }
        Write-Info "Has seleccionado: SOFTWARE BASE DEVOPS (CORE ESENCIAL)."
    }
}

# 6. FILTRAR HERRAMIENTAS: OMITIR LAS QUE YA ESTAN INSTALADAS
$missingTools = @()
Write-Header "REVISION DE HERRAMIENTAS SELECCIONADAS"

foreach ($tool in $selectedTools) {
    $toolPadded = "[$($tool.Categoria)] $($tool.Name)".PadRight(35)
    if ($tool.IsInstalled) {
        Write-Host " [OMITIDO]    $toolPadded : YA INSTALADO ($($tool.VersionText))" -ForegroundColor Green
    } else {
        Write-Host " [A INSTALAR] $toolPadded : PENDIENTE" -ForegroundColor Yellow
        $missingTools += $tool
    }
}

# 7. INSTALACION EXCLUSIVA DE LAS HERRAMIENTAS FALTANTES
if ($missingTools.Count -eq 0) {
    Write-Header "TODO EN ORDEN EN ESTA SELECCION"
    Write-Success "Todas las herramientas de esta seleccion ya estan instaladas en tu equipo."
    
    # Comprobar si hay otras herramientas optativas del curso sin instalar
    $otherMissing = $allTools | Where-Object { -not $_.IsInstalled }
    if ($otherMissing.Count -gt 0) {
        Write-Host ""
        Write-Host " [i] Tienes $($otherMissing.Count) herramientas optativas del curso disponibles para instalar:" -ForegroundColor Cyan
        foreach ($om in $otherMissing) {
            Write-Host "     - [$($om.Categoria)] $($om.Name) ($($om.Id))" -ForegroundColor Yellow
        }
        Write-Host ""
        Write-Host " ¿Deseas instalar estas $($otherMissing.Count) herramientas optativas ahora? (S/n) [Enter = Sí]: " -ForegroundColor Yellow -NoNewline
        $respOpt = Read-Host
        if ([string]::IsNullOrWhiteSpace($respOpt) -or ($respOpt -match "^[sSyY]")) {
            $missingTools = $otherMissing
        }
    } else {
        Write-Info "Tienes el 100% de las 33 herramientas del curso instaladas en tu sistema."
    }
}

if ($missingTools.Count -gt 0) {
    Write-Header "INSTALACION DE HERRAMIENTAS PENDIENTES"
    Write-Host "Se instalaran $($missingTools.Count) herramientas que faltan en el sistema:" -ForegroundColor Yellow
    foreach ($m in $missingTools) {
        Write-Host "   - [$($m.Categoria)] $($m.Name) ($($m.Id))" -ForegroundColor Cyan
    }

    if (-not $AutoApprove) {
        Write-Host ""
        Write-Host "Deseas proceder con la instalacion de estas $($missingTools.Count) herramientas? (S/n) [Enter = Sí]: " -ForegroundColor Yellow -NoNewline
        $response = Read-Host
        if ($response -and ($response -notmatch "^[sSyY]")) {
            Write-WarningMsg "Instalacion cancelada por el usuario."
            Exit 0
        }
    }

    foreach ($tool in $missingTools) {
        Write-Header "Instalando: $($tool.Name)..."
        if ($tool.InstallerType -eq "herdr") {
            try {
                Invoke-Expression (Invoke-RestMethod -Uri "https://herdr.dev/install.ps1")
                Write-Success "Herdr instalado correctamente."
            } catch {
                Write-ErrorMsg "Error instalando Herdr: $_"
            }
        } elseif ($tool.InstallerType -eq "omp") {
            try {
                Invoke-Expression (Invoke-RestMethod -Uri "https://omp.sh/install.ps1")
                Write-Success "OMP instalado correctamente."
            } catch {
                Write-ErrorMsg "Error instalando OMP: $_"
            }
        } elseif ($tool.InstallerType -eq "nerdctl") {
            try {
                Write-Info "Descargando nerdctl release desde GitHub..."
                $nerdctlDir = "$env:LOCALAPPDATA\nerdctl\bin"
                if (-not (Test-Path $nerdctlDir)) { New-Item -ItemType Directory -Path $nerdctlDir -Force | Out-Null }
                $zipPath = "$env:TEMP\nerdctl.tar.gz"
                & winget install -e --id containerd.nerdctl --accept-source-agreements --accept-package-agreements --silent
                if ($LASTEXITCODE -ne 0) {
                    Write-Info "Descargando binario directo de nerdctl..."
                    $url = "https://github.com/containerd/nerdctl/releases/latest/download/nerdctl-windows-amd64.tar.gz"
                    Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
                    tar -xzf $zipPath -C $nerdctlDir
                    $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
                    if ($userPath -notlike "*$nerdctlDir*") {
                        [System.Environment]::SetEnvironmentVariable("Path", ($userPath + ";" + $nerdctlDir), "User")
                    }
                }
                Write-Success "nerdctl configurado correctamente."
            } catch {
                Write-ErrorMsg "Error instalando nerdctl: $_"
            }
        } elseif ($tool.InstallerType -eq "npm") {
            try {
                & npm install -g $tool.Id
                Write-Success "$($tool.Name) instalado correctamente."
            } catch {
                Write-ErrorMsg "Error instalando $($tool.Name): $_"
            }
        } elseif ($tool.InstallerType -eq "pip") {
            try {
                & pip install $tool.Id openai
                Write-Success "$($tool.Name) instalado correctamente."
            } catch {
                Write-ErrorMsg "Error instalando $($tool.Name): $_"
            }
        } else {
            try {
                & winget install -e --id $tool.Id --accept-source-agreements --accept-package-agreements --silent
                if ($LASTEXITCODE -eq 0) {
                    Write-Success "$($tool.Name) se instalo correctamente."
                } else {
                    Write-WarningMsg "$($tool.Name) finalizo con codigo $LASTEXITCODE."
                }
            } catch {
                Write-ErrorMsg "Error instalando $($tool.Name): $_"
            }
        }
    }
}

# 8. CONFIGURACION DE WSL 2 SI SE INSTALO DOCKER
$dockerMissing = $missingTools | Where-Object { $_.Command -eq "docker" }
if ($dockerMissing) {
    Write-Header "VERIFICACION DE WSL 2 (REQUERIDO POR DOCKER)"
    $wslCmd = Get-Command "wsl" -ErrorAction SilentlyContinue
    if ($wslCmd) {
        Write-Success "WSL esta habilitado en tu sistema."
    } else {
        Write-WarningMsg "Habilitando Windows Subsystem for Linux (WSL)..."
        wsl --install --no-distribution
    }
}

# 9. CONFIGURACION DE HERDR SI SE INSTALO
$herdrMissing = $missingTools | Where-Object { $_.Command -eq "herdr" }
if ($herdrMissing -or ($selectedTools | Where-Object { $_.Command -eq "herdr" -and $_.IsInstalled })) {
    $appDataHerdr = Join-Path $env:APPDATA "herdr"
    if (-not (Test-Path $appDataHerdr)) { New-Item -ItemType Directory -Path $appDataHerdr -Force | Out-Null }
    $localConfig = Join-Path (Split-Path -Parent $PSScriptRoot) "herdr\config.toml"
    $targetConfig = Join-Path $appDataHerdr "config.toml"
    if (Test-Path $localConfig) {
        Copy-Item -Path $localConfig -Destination $targetConfig -Force
        Write-Success "Configuracion de paneles de Herdr desplegada en: $targetConfig"
    }
}

# 10. EXTENSIONES DE VS CODE SI SE INSTALO CODE
$codeSelected = $selectedTools | Where-Object { $_.Command -eq "code" }
if ($codeSelected -and -not $SkipExtensions) {
    $codeCmd = Get-Command "code" -ErrorAction SilentlyContinue
    if ($codeCmd) {
        Write-Header "CONFIGURACION DE EXTENSIONES PARA VS CODE"
        $extensions = @(
            "ms-azuretools.vscode-docker",
            "HashiCorp.terraform",
            "ms-kubernetes-tools.vscode-kubernetes-tools",
            "redhat.vscode-yaml",
            "ms-vscode-remote.remote-wsl"
        )
        foreach ($ext in $extensions) {
            Write-Info "Instalando extension: $ext..."
            & code --install-extension $ext --force | Out-Null
            Write-Success "Extension $ext configurada."
        }
    }
}

# 11. VERIFICACION Y AUTENTICACION DE GITHUB CLI (gh)
$ghInstalled = $allTools | Where-Object { $_.Command -eq "gh" -and $_.IsInstalled }
$ghMissing = $missingTools | Where-Object { $_.Command -eq "gh" }
if ($ghInstalled -or $ghMissing) {
    Write-Header "AUTENTICACION CON GITHUB (gh auth status / login)"
    $ghCmd = Get-Command "gh" -ErrorAction SilentlyContinue
    if (-not $ghCmd -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\gh.exe")) {
        $ghCmd = "$env:LOCALAPPDATA\Microsoft\WinGet\Links\gh.exe"
    }
    if ($ghCmd) {
        $authOut = (& $ghCmd auth status 2>&1 | Out-String)
        if ($LASTEXITCODE -eq 0 -or $authOut -match "Logged in to github\.com account ([^\s]+)") {
            if ($authOut -match "Logged in to github\.com account ([^\s]+)") {
                Write-Success "GitHub CLI autenticado correctamente con la cuenta: @$($matches[1])"
            } else {
                Write-Success "GitHub CLI ya se encuentra autenticado con GitHub."
            }
        } else {
            Write-WarningMsg "GitHub CLI (gh) esta instalado pero todavia NO esta autenticado con tu cuenta de GitHub."
            Write-Host "   Para vincular tu cuenta con GitHub y clonar repositorios de tus proyectos, ejecuta:" -ForegroundColor Yellow
            Write-Host "   gh auth login" -ForegroundColor Cyan
            Write-Host "   -> Pasos recomendados: Selecciona 'GitHub.com' -> 'HTTPS' -> 'Y' -> 'Login with a web browser'" -ForegroundColor Gray
        }
    }
}

# 12. RESUMEN FINAL
Write-Header "RESUMEN FINAL"
Write-Success "Proceso de instalacion finalizado."
Write-Host ""
Write-Host "PASOS SIGUIENTES:" -ForegroundColor Yellow
Write-Host "1. Abre una nueva terminal de PowerShell para que se recarguen las variables de entorno (PATH)." -ForegroundColor White
Write-Host "2. Si aun no autenticaste GitHub, ejecuta: gh auth login" -ForegroundColor White
Write-Host "3. Para verificar el estado de todas las herramientas en cualquier momento, ejecuta:" -ForegroundColor White
Write-Host "   powershell -ExecutionPolicy Bypass -File .\verificar-tools.ps1" -ForegroundColor Cyan
Write-Host ""
