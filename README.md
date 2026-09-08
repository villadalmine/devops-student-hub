# 🚀 Cloud DevOps Workspace & Student Hub

> **Entorno Profesional DevOps Multiplataforma:** Automatización de software, diagnóstico y toolkit para **Windows**, **Linux** y **macOS**.

---

## 💡 ¿Qué es este Repositorio?

Este repositorio es una estación de trabajo completa pensada para estudiantes y profesionales de **Cloud DevOps e Infraestructura moderna**.

Está diseñado bajo tres pilares fundamentales:
1. **📦 Automatización de Software Multi-OS:** Provisiona y diagnostica en Windows (`winget` + PowerShell), Linux (`apt`/`dnf`/`pacman` + Bash) y macOS (`brew` + Bash) el conjunto de las **31 herramientas del curso** organizadas en 6 categorías modulares.
2. **🩺 Diagnóstico del Sistema en Vivo:** Herramientas de escaneo para validar que tus CLIs, variables de entorno `PATH` y binarios estén 100% listos antes de cada laboratorio.
3. **🌐 Student Hub Web Local:** Un panel de control visual en `http://localhost:8080` con visor interactivo de apuntes, manuales técnicos y reproductor local de clases en video (`HTTP Range 206`).

---

## ⚡ 1. Instalación Rápida por Sistema Operativo

Elige tu sistema operativo y ejecuta el instalador automatizado correspondiente:

### 🪟 Windows (PowerShell)
Abre **PowerShell como Administrador** en la carpeta del repositorio y ejecuta:

```powershell
# Opción A: Instalar solo el Core Esencial (12 herramientas base)
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloBase

# Opción B: Menú interactivo completo (las 31 herramientas)
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1

# Verificar instalación:
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```
*Guía detallada:* [`01-Guia-Completa-Instalacion-Windows.md`](01-Guia-Completa-Instalacion-Windows.md)

---

### 🐧 Linux (Ubuntu, Debian, Fedora, Arch)
Abre tu terminal en la carpeta del repositorio y ejecuta:

```bash
chmod +x ./scripts/instalar-tools-linux.sh ./scripts/verificar-tools.sh

# Opción A: Instalar Core Esencial (12 herramientas base)
./scripts/instalar-tools-linux.sh --base

# Opción B: Instalar todo el ecosistema (31 herramientas)
./scripts/instalar-tools-linux.sh --all

# Verificar instalación:
./scripts/verificar-tools.sh
```
*Guía detallada:* [`02-Guia-Instalacion-Linux.md`](02-Guia-Instalacion-Linux.md)

---

### 🍎 macOS (Apple Silicon M1/M2/M3/M4 & Intel)
Abre tu Terminal de macOS y ejecuta:

```bash
chmod +x ./scripts/instalar-tools-macos.sh ./scripts/verificar-tools.sh

# Opción A: Instalar Core Esencial con Homebrew
./scripts/instalar-tools-macos.sh --base

# Opción B: Instalar todo el ecosistema
./scripts/instalar-tools-macos.sh --all

# Verificar instalación:
./scripts/verificar-tools.sh
```
*Guía detallada:* [`03-Guia-Instalacion-MacOS.md`](03-Guia-Instalacion-MacOS.md)

---

## 🛠️ 2. El Toolkit de 31 Herramientas (6 Categorías)

| Categoría | Cantidad | Herramientas Incluidas |
| :--- | :---: | :--- |
| **⚙️ BASE (Core Esencial)** | 12 | Zoom, Git, GitHub CLI (`gh`), VS Code, Docker, Terraform, AWS CLI, Azure CLI, kubectl, Helm, Minikube, jq |
| **💻 TERM (Terminales & Editores)** | 6 | Gajim (XMPP), Ghostty Terminal, Zed Editor, Herdr Multiplexer, Neovim (`nvim`), VLC |
| **🖥️ TUI (Productividad de Consola)** | 5 | fzf, Lazygit, Yazi (File Manager), Lazydocker, k9s |
| **🌐 EBPF (Redes & Observabilidad)** | 3 | nerdctl (containerd), Cilium CLI, Hubble CLI |
| **🐍 LANG (Lenguajes & Runtimes)** | 2 | Go (Golang), Python 3 |
| **🤖 AI (Agentes Inteligentes)** | 3 | Claude Code CLI, Shell-GPT (`sgpt`), OMP (Oh My Pi) |

---

## 🌐 3. Iniciar el Student Hub Local

El repositorio cuenta con una interfaz web local para consultar comandos, documentación y reproducir videos:

### En Windows:
Haz doble clic sobre:
```text
▶ iniciar-mi-hub.bat
```
*(O ejecuta `python scripts\servidor_asistente.py`).*

### En Linux / macOS:
```bash
python3 scripts/servidor_asistente.py
```

Tu navegador se abrirá en **`http://localhost:8080`**.

---

## 📁 4. Estructura del Repositorio

```text
dist_alumnos/
├── 01-Guia-Completa-Instalacion-Windows.md # Manual paso a paso para Windows
├── 02-Guia-Instalacion-Linux.md           # Manual paso a paso para Linux
├── 03-Guia-Instalacion-MacOS.md           # Manual paso a paso para macOS
├── devops_hub.html                        # Portal web interactivo multi-OS
├── iniciar-mi-hub.bat                     # Lanzador en 1 clic para Windows
├── apuntes/                               # Tus notas y resúmenes personales
├── material/                              # Guías y documentación descargable
├── practicas/                             # Laboratorios prácticos del curso
├── videos/                                # Reproductor de videos MP4 locales
└── scripts/
    ├── instalar-tools-devops.ps1          # Instalador Windows (PowerShell/Winget)
    ├── instalar-tools-linux.sh            # Instalador Linux (apt/dnf/pacman)
    ├── instalar-tools-macos.sh            # Instalador macOS (Homebrew)
    ├── verificar-tools.ps1                # Diagnóstico en Windows
    ├── verificar-tools.sh                 # Diagnóstico en Linux / macOS
    └── servidor_asistente.py              # Servidor HTTP local y API diagnóstico
```
