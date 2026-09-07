# Diagnóstico del Entorno Local y Guía de Instalación de Software

> **Curso:** Cloud DevOps: Automatización y Despliegue  
> **Instructor:** rino@villadalmine.club  
> **Fecha de Actualización:** Septiembre de 2026  

---

## 1. Estado Actual de la Máquina Local (Diagnóstico)

Se realizó un escaneo automatizado sobre el entorno local Windows. A continuación se detalla el estado del software oficial y opcional:

| Herramienta | Categoría | Estado en el Sistema | Versión / Detalle |
| :--- | :---: | :---: | :--- |
| **Zoom Workplace** | `BASE` | **INSTALADO** | Detectado en sistema |
| **Git for Windows** | `BASE` | **INSTALADO** | `git version 2.54.0.windows.1` |
| **GitHub CLI (gh)** | `BASE` | **INSTALADO** | `gh version 2.98.0` *(Ejecutar `gh auth login`)* |
| **Visual Studio Code** | `BASE` | **INSTALADO** | `1.117.0` |
| **Docker Desktop** | `BASE` | **INSTALADO** | `Docker version 29.7.2` |
| **Docker Compose** | `BASE` | **INSTALADO** | `Docker Compose v5.4.0` |
| **HashiCorp Terraform** | `BASE` | **INSTALADO** | `Terraform v1.15.8` |
| **AWS CLI (v2)** | `BASE` | **INSTALADO** | `aws-cli/2.36.33` |
| **Azure CLI (az)** | `BASE` | **INSTALADO** | `Azure CLI v2.89.1` |
| **kubectl (Kubernetes CLI)** | `BASE` | **INSTALADO** | `Client Version: v1.36.1` |
| **Helm** | `BASE` | **INSTALADO** | `v4.2.4` |
| **Minikube** | `BASE` | **INSTALADO** | `v1.38.1` |
| **jq (JSON Processor)** | `BASE` | **INSTALADO** | `jq-1.8.2` |
| **Ghostty Terminal** | `TERM` | **INSTALADO** | Emulador acelerado por GPU |
| **Zed Editor** | `TERM` | **INSTALADO** | `Zed 1.17.2` |
| **Herdr Multiplexer** | `TERM` | **INSTALADO** | `herdr 0.8.2` |
| **VLC Media Player** | `TERM` | **INSTALADO** | `v3.0.23` |
| **Lazygit / Yazi / Lazydocker / k9s / fzf** | `TUI` | **INSTALADO** | TUIs de alto rendimiento |
| **Python** | `LANG` | **INSTALADO** | `Python 3.14.4` |
| **Go (Golang)** | `LANG` | **INSTALADO** | `go version go1.27.0` |
| **Suite Agentes IA (Claude, OMP, AGY)** | `AI` | **INSTALADO** | Claude Code, OMP, Antigravity |

---

## 2. Guía Rápida de Instalación Automatizada por Categorías

A través del script maestro `instalar-tools-devops.ps1`, cualquier equipo Windows puede provisionar todo el ecosistema de 28 herramientas organizadas en **6 categorías modulares**:

```powershell
# Ejecutar en PowerShell como Administrador:
cd "scripts"
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1
```

### Opciones Rápidas:
* **Solo Software Base Core:** `powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -SoloObligatorio`
* **Instalar Suite de IA:** `powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria AI`
* **Instalar Terminales y TUIs:** `powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria TERM,TUI`
* **Instalar Lenguajes y Redes eBPF:** `powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria LANG,EBPF`

---

## 3. Verificación Integral en 2 Segundos

Para comprobar el estado completo de tu equipo en cualquier momento:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```
