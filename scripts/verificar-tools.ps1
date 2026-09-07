<#
.SYNOPSIS
    Script de Verificacion de Herramientas Cloud DevOps para Windows.
    Distingue entre Software Base DevOps (Core Esencial) y Herramientas Optativas.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\verificar-tools.ps1
#>

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTICO DE HERRAMIENTAS CLOUD DEVOPS (WINDOWS)" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Refrescar PATH en memoria
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

# 1. SOFTWARE BASE DEVOPS (CORE ESENCIAL)
Write-Host " [1] SOFTWARE BASE OBLIGATORIO (MANDATORY):" -ForegroundColor Yellow
$coreTools = @(
    @{ Name="Zoom Workplace"; Cmd="zoom"; Args=""; CustomCheck={ Test-Path "$env:APPDATA\Zoom\bin\Zoom.exe", "C:\Program Files\Zoom\bin\Zoom.exe", "$env:LOCALAPPDATA\Zoom\bin\Zoom.exe" } },
    @{ Name="Git for Windows"; Cmd="git"; Args="--version" },
    @{ Name="GitHub CLI (gh)"; Cmd="gh"; Args="--version" },
    @{ Name="Visual Studio Code"; Cmd="code"; Args="--version" },
    @{ Name="Docker Desktop"; Cmd="docker"; Args="--version" },
    @{ Name="Docker Compose"; Cmd="docker"; Args="compose version" },
    @{ Name="HashiCorp Terraform"; Cmd="terraform"; Args="--version" },
    @{ Name="AWS CLI v2"; Cmd="aws"; Args="--version" },
    @{ Name="Azure CLI (az)"; Cmd="az"; Args="version"; CustomCheck={ (Get-Command "az" -ErrorAction SilentlyContinue) -or (Test-Path "C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd") } },
    @{ Name="Kubernetes CLI (kubectl)"; Cmd="kubectl"; Args="version --client" },
    @{ Name="Helm"; Cmd="helm"; Args="version --short" },
    @{ Name="Minikube"; Cmd="minikube"; Args="version --short" },
    @{ Name="jq (JSON Processor)"; Cmd="jq"; Args="--version"; CustomCheck={ (Get-Command "jq" -ErrorAction SilentlyContinue) -or (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe") } }
)

$coreInstalled = 0
foreach ($t in $coreTools) {
    $isInstalled = $false
    $cmd = Get-Command $t.Cmd -ErrorAction SilentlyContinue
    if ($cmd) {
        $isInstalled = $true
    } elseif ($t.CustomCheck -and (& $t.CustomCheck)) {
        $isInstalled = $true
    }

    $padded = $t.Name.PadRight(32)
    if ($isInstalled) {
        try {
            if ($t.Cmd -eq "az") {
                $rawOut = (& az version 2>&1 | Out-String)
                if ($rawOut -match '"azure-cli":\s*"([^"]+)"') {
                    $line = "Azure CLI v$($matches[1])"
                } else {
                    $line = "Instalado"
                }
            } elseif ($t.Cmd -eq "gh" -and $cmd) {
                $rawOut = (& $cmd --version 2>&1 | Out-String).Trim()
                $ver = ($rawOut -split "`r?`n")[0]
                $authCheck = (& $cmd auth status 2>&1 | Out-String)
                if ($authCheck -match "Logged in to github\.com account ([^\s]+)") {
                    $line = "$ver (GitHub: @$($matches[1]))"
                } else {
                    $line = "$ver (Sin autenticar -> gh auth login)"
                }
            } elseif ($t.Cmd -eq "jq" -and -not $cmd -and (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe")) {
                $rawOut = (& "$env:LOCALAPPDATA\Microsoft\WinGet\Links\jq.exe" --version 2>&1 | Out-String).Trim()
                $line = ($rawOut -split "`r?`n")[0]
            } elseif ($t.Args -and $cmd) {
                $rawOut = (& $cmd ($t.Args -split ' ') 2>&1 | Out-String).Trim()
                $line = ($rawOut -split "`r?`n")[0]
                if ($line.Length -gt 38) { $line = $line.Substring(0, 35) + "..." }
            } else {
                $line = "Instalado"
            }
            Write-Host "   [OK] $padded : $line" -ForegroundColor Green
            $coreInstalled++
        } catch {
            Write-Host "   [OK] $padded : Detectado" -ForegroundColor Green
            $coreInstalled++
        }
    } else {
        Write-Host "   [X]  $padded : NO INSTALADO (Requerido)" -ForegroundColor Red
    }
}
Write-Host "   -> Estado Base Obligatorio: $coreInstalled de $($coreTools.Count) instaladas." -ForegroundColor Cyan
Write-Host ""

# 2. HERRAMIENTAS OPTATIVAS (PRODUCTIVIDAD, TERMINALES, COMUNICACION, LENGUAJES, TUIS, IA & EBPF)
Write-Host " [2] HERRAMIENTAS OPTATIVAS (PRODUCTIVIDAD, TERMINALES, COMUNICACION, LENGUAJES, TUIS, IA & EBPF):" -ForegroundColor Yellow
$optTools = @(
    @{ Name="Gajim (Cliente XMPP/Jabber)"; Cmd="gajim"; Args="--version"; CustomCheck={ (Get-Command "gajim" -ErrorAction SilentlyContinue) -or (Test-Path "C:\Program Files\Gajim\bin\Gajim.exe", "C:\Program Files (x86)\Gajim\bin\Gajim.exe", "$env:LOCALAPPDATA\Programs\Gajim\bin\Gajim.exe") } },
    @{ Name="Ghostty Terminal"; Cmd="ghostty"; Args="--version"; CustomCheck={ (Get-Command "ghostty" -ErrorAction SilentlyContinue) -or (Get-Command "ghostly" -ErrorAction SilentlyContinue) -or (Get-Command "winghostty" -ErrorAction SilentlyContinue) -or (Test-Path "$env:LOCALAPPDATA\Programs\ghostty\ghostty.exe", "$env:ProgramFiles\Ghostty\ghostty.exe") } },
    @{ Name="Go (Golang)"; Cmd="go"; Args="version" },
    @{ Name="Python"; Cmd="python"; Args="--version" },
    @{ Name="fzf (Fuzzy Finder)"; Cmd="fzf"; Args="--version" },
    @{ Name="nerdctl (containerd CLI)"; Cmd="nerdctl"; Args="version"; CustomCheck={ (Get-Command "nerdctl" -ErrorAction SilentlyContinue) -or (Get-Command "nerctl" -ErrorAction SilentlyContinue) } },
    @{ Name="Cilium CLI (eBPF K8s)"; Cmd="cilium"; Args="version --client" },
    @{ Name="Hubble CLI (eBPF Observability)"; Cmd="hubble"; Args="version" },
    @{ Name="Zed Editor"; Cmd="zed"; Args="--version" },
    @{ Name="Herdr (Multiplexer)"; Cmd="herdr"; Args="--version" },
    @{ Name="VLC Media Player"; Cmd="vlc"; Args="--version"; CustomCheck={ Test-Path "C:\Program Files\VideoLAN\VLC\vlc.exe", "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" } },
    @{ Name="Lazygit (TUI Git)"; Cmd="lazygit"; Args="--version" },
    @{ Name="Yazi (TUI Files)"; Cmd="yazi"; Args="--version" },
    @{ Name="Neovim (Modal Editor)"; Cmd="nvim"; Args="--version" },
    @{ Name="Lazydocker (TUI Docker)"; Cmd="lazydocker"; Args="--version" },
    @{ Name="k9s (TUI Kubernetes)"; Cmd="k9s"; Args="version" },
    @{ Name="Claude Code CLI"; Cmd="claude"; Args="--version" },
    @{ Name="Antigravity CLI"; Cmd="agy"; Args="--version" },
    @{ Name="OpenAI GPT CLI (sgpt)"; Cmd="sgpt"; Args="--version" },
    @{ Name="OMP (Oh My Pi AI Agent)"; Cmd="omp"; Args="--version" },
    @{ Name="Node.js"; Cmd="node"; Args="--version" }
)

$optInstalled = 0
foreach ($t in $optTools) {
    $isInstalled = $false
    $cmd = Get-Command $t.Cmd -ErrorAction SilentlyContinue
    if (-not $cmd -and $t.Cmd -eq "ghostty") {
        $cmd = (Get-Command "ghostly" -ErrorAction SilentlyContinue)
        if (-not $cmd) { $cmd = (Get-Command "winghostty" -ErrorAction SilentlyContinue) }
    }

    if ($cmd) {
        $isInstalled = $true
    } elseif ($t.CustomCheck -and (& $t.CustomCheck)) {
        $isInstalled = $true
    }

    $padded = $t.Name.PadRight(32)
    if ($isInstalled) {
        try {
            if ($t.Name -like "*VLC*" -and (Test-Path "C:\Program Files\VideoLAN\VLC\vlc.exe")) {
                $verRaw = (Get-Item "C:\Program Files\VideoLAN\VLC\vlc.exe").VersionInfo.ProductVersion -replace ',', '.'
                $line = "VLC media player $verRaw"
            } elseif ($t.Name -like "*Gajim*" -and (Test-Path "C:\Program Files\Gajim\bin\Gajim.exe")) {
                $verRaw = (Get-Item "C:\Program Files\Gajim\bin\Gajim.exe").VersionInfo.ProductVersion
                $line = "Gajim XMPP v$verRaw"
            } elseif ($t.Args -and $cmd) {
                $rawOut = (& $cmd ($t.Args -split ' ') 2>&1 | Out-String).Trim()
                $line = ($rawOut -split "`r?`n")[0]
                if ($line.Length -gt 38) { $line = $line.Substring(0, 35) + "..." }
            } else {
                $line = "Instalado"
            }
            Write-Host "   [OK] $padded : $line" -ForegroundColor Green
            $optInstalled++
        } catch {
            Write-Host "   [OK] $padded : Detectado" -ForegroundColor Green
            $optInstalled++
        }
    } else {
        Write-Host "   [ -] $padded : No instalado (Opcional)" -ForegroundColor DarkGray
    }
}
Write-Host "   -> Estado Optativo: $optInstalled de $($optTools.Count) instaladas." -ForegroundColor DarkCyan
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan

if ($coreInstalled -lt $coreTools.Count) {
    Write-Host " Para instalar las herramientas OBLIGATORIAS faltantes, ejecuta como Admin:" -ForegroundColor Yellow
    Write-Host "   powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -SoloObligatorio" -ForegroundColor White
} else {
    Write-Host " Excelente: Tu equipo cuenta con todo el software obligatorio para el entorno DevOps." -ForegroundColor Green
}

$ghCmd = Get-Command "gh" -ErrorAction SilentlyContinue
if ($ghCmd) {
    $authCheck = (& $ghCmd auth status 2>&1 | Out-String)
    if ($authCheck -notmatch "Logged in to github\.com account") {
        Write-Host ""
        Write-Host " [!] ATENCION - AUTENTICACION DE GITHUB PENDIENTE:" -ForegroundColor Yellow
        Write-Host "     Tienes GitHub CLI instalado, pero aun no iniciaste sesion." -ForegroundColor White
        Write-Host "     Para vincular tu cuenta con GitHub y clonar repositorios de tus proyectos, ejecuta:" -ForegroundColor White
        Write-Host "     gh auth login" -ForegroundColor Cyan
        Write-Host "     (Recomendado: GitHub.com -> HTTPS -> Yes -> Login with a web browser)" -ForegroundColor Gray
    }
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""
