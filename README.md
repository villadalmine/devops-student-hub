# 🚀 Cloud DevOps Workspace & Student Hub

> **Entorno Profesional DevOps Multiplataforma:** Automatización de software, diagnóstico en vivo, labs interactivos y toolkit para **Windows**, **Linux** y **macOS**.

---

## 💡 ¿Qué es este Repositorio?

Este repositorio es una estación de trabajo completa pensada para estudiantes y profesionales de **Cloud DevOps, SRE e Infraestructura moderna**.

Está diseñado bajo cuatro pilares fundamentales:
1. **📦 Automatización de Software Multi-OS:** Provisiona y diagnostica en Windows (`winget` + PowerShell), Linux (`apt`/`dnf`/`pacman` + Bash) y macOS (`brew` + Bash) el conjunto de las **33 herramientas del curso** organizadas en 6 categorías modulares (`[C1]` a `[C6]`).
2. **🩺 Diagnóstico del Sistema en Vivo:** Herramientas de escaneo local en tiempo real para validar qué CLIs, variables de entorno `PATH` y binarios están 100% listos antes de cada laboratorio.
3. **🌐 Student Hub Web Local (Puerto 8081):** Panel de control visual en `http://localhost:8081/devops_hub.html` con visor interactivo de apuntes, instaladores de 1 clic, streaming de video local sin conexión (`HTTP Range 206`) y telemetría del sistema.
4. **📚 Glosario Técnico & Directorio de Labs Interactivos:** Aplicación web dedicada (`glosario_recursos_devops.html`) con buscador reactivo, simuladores de terminal en el navegador (iximiuz Labs, Killercoda, SadServers), fanzines visuales de arquitectura, el célebre libro ilustrado **"The Illustrated Children's Guide to Kubernetes" (CNCF)** en PDF local (15 MB) y 17 definiciones de clase listas para copiar al chat.

---

## ⚡ 1. Instalación Rápida por Sistema Operativo

Elige tu sistema operativo y ejecuta el instalador automatizado correspondiente:

### 🪟 Windows (PowerShell)
Abre **PowerShell** en la carpeta del repositorio y ejecuta:

```powershell
# Opción A: Instalar solo el Core Esencial (12 herramientas base)
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloBase

# Opción B: Menú interactivo completo (las 33 herramientas en 6 categorías)
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1

# Opción C: Ver la chuleta completa de comandos y verificación
powershell -ExecutionPolicy Bypass -File .\scripts\mostrar-todos-comandos.ps1

# Verificar instalación:
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```
*Guía detallada:* [`01-Guia-Completa-Instalacion-Windows.md`](01-Guia-Completa-Instalacion-Windows.md)

---

### 🐧 Linux (Ubuntu, Debian, Fedora, Arch)
Abre tu terminal en la carpeta del repositorio y ejecuta:

```bash
chmod +x ./scripts/*.sh ./iniciar-mi-hub.sh

# Opción A: Instalar Core Esencial (12 herramientas base)
./scripts/instalar-tools-linux.sh --base

# Opción B: Instalar todo el ecosistema (33 herramientas)
./scripts/instalar-tools-linux.sh --all

# Verificar instalación:
./scripts/verificar-tools.sh
```
*Guía detallada:* [`02-Guia-Instalacion-Linux.md`](02-Guia-Instalacion-Linux.md)

---

### 🍎 macOS (Apple Silicon M1/M2/M3/M4 & Intel)
Abre tu Terminal de macOS y ejecuta:

```bash
chmod +x ./scripts/*.sh ./iniciar-mi-hub.sh

# Opción A: Instalar Core Esencial con Homebrew
./scripts/instalar-tools-macos.sh --base

# Opción B: Instalar todo el ecosistema
./scripts/instalar-tools-macos.sh --all

# Verificar instalación:
./scripts/verificar-tools.sh
```
*Guía detallada:* [`03-Guia-Instalacion-MacOS.md`](03-Guia-Instalacion-MacOS.md)

---

## 🛠️ 2. El Toolkit de 33 Herramientas (6 Categorías)

| Categoría | Cantidad | Herramientas Incluidas |
| :--- | :---: | :--- |
| **[C1] ⚙️ BASE (Core Esencial)** | 12 | Zoom Workplace, Git, GitHub CLI (`gh`), VS Code, Docker, Terraform, AWS CLI v2, Azure CLI (`az`), kubectl, Helm, Minikube, jq |
| **[C2] 💻 TERM (Terminales & Editores)** | 6 | Gajim (XMPP), Ghostty Terminal, Zed Editor, Herdr Multiplexer, Neovim (`nvim`), VLC |
| **[C3] 🖥️ TUI (Productividad de Consola)** | 5 | fzf, Lazygit, Yazi (File Manager), Lazydocker, k9s |
| **[C4] 🛡️ EBPF & Seguridad** | 4 | nerdctl (containerd), Cilium CLI, Hubble CLI, Trivy (CVE Scanner) |
| **[C5] 🦀 LANG (Lenguajes & Runtimes)** | 3 | Go (Golang), Python 3.12, Rust (Cargo) |
| **[C6] 🤖 AI (Suite Agentes IA)** | 3 | Claude Code CLI, Shell-GPT (`sgpt`), OMP (Oh My Pi) |

---

## 🌐 3. Iniciar el Student Hub Local (Puerto 8081)

El portal puede iniciarse de dos formas: **como binario nativo compilado** (`student-hub.exe`, **sin requerir Python en tu PC**) o mediante el script Python estándar:

### En Windows:
Puedes descargarlo directamente como ejecutable sin necesidad de instalar Python:
👉 **[⬇️ Descargar student-hub.exe (Release v1.0.0)](https://github.com/villadalmine/devops-student-hub/releases/latest/download/student-hub.exe)**

O si ya clonaste/descargaste la carpeta, haz doble clic sobre:
```text
▶ iniciar-mi-hub.bat
```
*O ejecuta directamente el binario nativo:*
```text
▶ student-hub.exe
```
*(Si no tienes Python instalado, `student-hub.exe` o `iniciar-mi-hub.bat` arrancarán el entorno de inmediato).*

### En Linux / macOS:
```bash
./iniciar-mi-hub.sh
# O manualmente:
python3 scripts/servidor_asistente.py 8081
```

Tu navegador se abrirá automáticamente en: **`http://localhost:8081/devops_hub.html`**.

### 🌟 Pestañas del Student Hub:
1. **⚡ Instalación & Software DevOps:** Selector multi-OS (Windows, Linux, macOS) con comandos adaptados, botón de instalación rápida y apertura de terminal interactiva.
2. **📚 Guías de Instalación & Apuntes:** Manuales completos para cada OS y acceso directo al libro oficial **The Illustrated Children's Guide to Kubernetes** (PDF offline de 15 MB).
3. **🌐 Glosario & Labs Interactivos:** Buscador reactivo, simuladores de terminal en el navegador y 17 conceptos clave con botones **📋 Copiar para Chat** para Zoom/Discord.
4. **🎥 Videos Locales:** Catálogo y reproductor integrado de clases con soporte de streaming `HTTP Range 206`.
5. **🩺 Diagnóstico del Sistema:** Escaneo en tiempo real de las 33 herramientas en tu `%PATH%` con barra de cobertura porcentual y botón para instalar herramientas faltantes.
6. **🎒 Mis Aportes & Notas:** Editor personal de notas (`mis_apuntes/`) y botón **"📥 Exportar Mis Aportes (.ZIP)"** en 1-clic para descargar tu trabajo y compartirlo con el docente.
7. **📡 Logs & Telemetría:** Monitor de eventos en vivo, llamadas a la API y estado del servidor.

---

## 📖 4. Glosario DevOps, Labs Interactivos & Material de Lectura

Puedes abrir directamente el portal de recursos y glosario en:
👉 **[`glosario_recursos_devops.html`](glosario_recursos_devops.html)** *(o en `http://localhost:8081/glosario_recursos_devops.html` con el servidor activo)*.

### 🧪 Plataformas de Laboratorios en Navegador (Sin Instalar Nada):
- **iximiuz Labs (Ivan Velichko):** Playgrounds interactivos de bajo nivel para experimentar con Namespaces, cgroups, runc, containerd y networking.
- **Killercoda:** Escenarios interactivos guiados en Linux y Kubernetes directamente en la web.
- **SadServers:** Escenarios de troubleshooting realista bajo presión para diagnosticar problemas de servidores.
- **Play with Docker & Play with Kubernetes:** Clusters reales en el navegador para practicar comandos sin consumir memoria local.
- **Linux Kernel Teaching Labs:** Laboratorios académicos sobre llamadas al sistema (`syscalls`), memoria virtual y módulos del kernel.
- **Containerlab:** Orquestación declarativa de topologías de red en contenedores.

### 🐳 Lectura Destacada:
- **[The Illustrated Children's Guide to Kubernetes (CNCF)](material/The-Illustrated-Childrens-Guide-to-Kubernetes.pdf):** Cuento oficial ilustrado de Phippy la Jirafa y el Capitán Kube explicando Pods, ReplicaSets, Services, Deployments e Ingress de forma intuitiva. Descargado localmente en `material/The-Illustrated-Childrens-Guide-to-Kubernetes.pdf` (15 MB) y disponible online en [CNCF](https://www.cncf.io/wp-content/uploads/2020/08/The-Illustrated-Childrens-Guide-to-Kubernetes.pdf).

---

## 📁 5. Estructura del Repositorio

```text
dist_alumnos/
├── 01-Guia-Completa-Instalacion-Windows.md # Manual paso a paso para Windows
├── 02-Guia-Instalacion-Linux.md           # Manual paso a paso para Linux
├── 03-Guia-Instalacion-MacOS.md           # Manual paso a paso para macOS
├── devops_hub.html                        # Portal web interactivo multi-OS (puerto 8081)
├── glosario_recursos_devops.html          # Web App: Glosario, Labs y Recursos interactivos
├── iniciar-mi-hub.bat                     # Lanzador en 1 clic para Windows (.bat)
├── iniciar-mi-hub.ps1                     # Lanzador en PowerShell para Windows (.ps1)
├── iniciar-mi-hub.sh                      # Lanzador Bash para Linux y macOS (.sh)
├── README.md                              # Esta documentación completa
├── apuntes/                               # Tus notas y resúmenes personales
├── material/                              # Guías y documentación descargable
│   ├── README.md                          # Catálogo de material técnico
│   └── The-Illustrated-Childrens-Guide-to-Kubernetes.pdf # Libro ilustrado K8s (15 MB offline)
├── practicas/                             # Laboratorios prácticos del curso
├── videos/                                # Reproductor de videos MP4 locales
│   └── README.md                          # Instrucciones de streaming de video
└── scripts/
    ├── instalar-tools-devops.ps1          # Instalador Windows (PowerShell/Winget) con categorías [C1]-[C6]
    ├── instalar-tools-linux.sh            # Instalador Linux (apt/dnf/pacman)
    ├── instalar-tools-macos.sh            # Instalador macOS (Homebrew)
    ├── mostrar-todos-comandos.ps1         # Cheat sheet interactivo de las 33 herramientas
    ├── verificar-tools.ps1                # Diagnóstico local en Windows
    ├── verificar-tools.sh                 # Diagnóstico local en Linux / macOS
    └── servidor_asistente.py              # Servidor HTTP local multi-hilo, no-cache y API diagnóstico
```

---

## 🤝 Contribuciones y Soporte

Este entorno está optimizado para los cursos de **Cloud DevOps: Automatización y Despliegue**. Si encuentras algún inconveniente con un paquete o dependencias de tu sistema operativo, consulta la guía de instalación correspondiente o abre un issue en el repositorio.

