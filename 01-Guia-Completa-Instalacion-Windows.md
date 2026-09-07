# Guía de Instalación del Entorno Cloud DevOps (Windows)

> **Estructura:** Software Base DevOps (Core Esencial) vs. Ecosistema de Herramientas Optativas por Categorías  

---

## 📌 Resumen de Requerimientos: Obligatorio (Mandatory) vs. Optativo

| Categoría | Descripción | Requerido para Cursar |
| :--- | :--- | :---: |
| 🔴 **Software Base DevOps (Core Esencial)** | Extraído del programa oficial de Cloud DevOps, nubes principales (AWS + Azure) y procesador JSON (`jq`). Necesario para laboratorios prácticos, desarrollo e infraestructura. | **SÍ (100% Obligatorio / Mandatory)** |
| 🟢 **Herramientas Optativas** | Terminales GPU, clientes XMPP/Jabber, visores TUI, lenguajes, redes eBPF, multiplexor Herdr y suite de IA. Mejoran la productividad y flujo de trabajo pero su instalación es a elección. | **NO (100% Optativo)** |

---

## 🔴 1. Software Base DevOps (Core Esencial)

Este es el stack tecnológico que cada usuario y docente **debe tener instalado obligatoriamente**:

| Herramienta | Versión Mínima / ID Winget | Módulos Oficiales | Propósito en el Programa |
| :--- | :---: | :---: | :--- |
| **Zoom Workplace** | `Zoom.Zoom` (6.0+) | Reuniones de equipo | Plataforma para reuniones, demos y sesiones técnicas en vivo. |
| **Git for Windows** | `Git.Git` (2.40+) | M1, M3, M6 | Control de versiones distribuido y trabajo con ramas. |
| **Visual Studio Code** | `Microsoft.VisualStudioCode` | M1 a M7 | IDE principal para edición de código, Dockerfiles, YAML y HCL. |
| **Docker Desktop (+ WSL 2)** | `Docker.DockerDesktop` (4.25+) | M4, M5, M6, M7 | Motor de contenerización Linux en Windows. |
| **HashiCorp Terraform** | `Hashicorp.Terraform` (1.5+) | M3 | Aprovisionamiento de Infraestructura como Código (IaC). |
| **AWS CLI (v2)** | `Amazon.AWSCLI` (2.15+) | M2, M3, M7 | Gestión, aprovisionamiento y autenticación con Amazon Web Services. |
| **Azure CLI (az)** | `Microsoft.AzureCLI` (2.50+) | M2, M3, M7 | Gestión, suscripciones y despliegue en Microsoft Azure Cloud. |
| **Kubernetes CLI (kubectl)** | `Kubernetes.kubectl` (1.28+) | M5, M6, M7 | Administración de clústeres y despliegue de manifiestos. |
| **Helm** | `Helm.Helm` (3.12+) | M5 | Gestor de paquetes y charts para Kubernetes. |
| **Minikube** | `Kubernetes.minikube` (1.32+) | M5 | Clúster local ligero de Kubernetes para pruebas y laboratorios. |
| **jq (JSON Processor)** | `jqlang.jq` (1.7+) | M1 a M7 | Procesamiento, parsing y filtrado de respuestas JSON en pipelines y CLIs. |
| **WSL 2 (Ubuntu)** | Kernel 5.10+ | M4, M5 | Subsistema de Linux para Windows (backend de Docker). |

---

## 🟢 2. Ecosistema de Herramientas Opcionales Organizadas por Categoría

Las herramientas opcionales están organizadas en **5 categorías temáticas** para facilitar su comprensión e instalación por bloques modulares:

### 📦 [TERM] Terminales, Comunicación XMPP & Editores Modernos
* **Gajim (`gajim`):** Cliente XMPP/Jabber moderno y ligero para Windows con soporte de cifrado extremo a extremo (OMEMO), salas de chat y envío de archivos.
* **Ghostty Terminal (`ghostty` / `ghostly`):** Emulador de terminal nativo acelerado por GPU, con renderizado ultra-rápido, tipografía con ligaduras y pestañas nativas.
* **Zed Editor (`zed`):** Editor moderno y veloz escrito en Rust con IA integrada.
* **Herdr (`herdr`):** Multiplexor de terminal (*tmux moderno*) con paneles preconfigurados por tema de tus proyectos (`Ctrl+1` a `Ctrl+7`).
* **Neovim (`nvim`):** Editor modal extensible de alto rendimiento para consola.
* **VLC Media Player (`vlc`):** Reproductor multimedia para transmisiones y grabaciones y tutoriales HLS `.m3u8` desde consola.

### 📦 [TUI] Herramientas TUI & Productividad
* **GitHub CLI (`gh`):** CLI oficial de GitHub con soporte para Pull Requests, visualización de GitHub Actions y extensión de Copilot.
* **Fuzzy Finder (`fzf`):** Búsqueda difusa interactiva en terminal para ramas Git, historial de comandos y contenedores.
* **Lazygit (`lazygit`):** Interfaz gráfica interactiva en terminal para operaciones de Git en 1 sola tecla.
* **Yazi (`yazi`):** Explorador de archivos TUI en Rust con previsualizaciones instantáneas.
* **Lazydocker (`lazydocker`):** Panel visual en terminal para monitorear contenedores Docker y métricas en vivo.
* **k9s (`k9s`):** Monitor interactivo para explorar clústeres de Kubernetes en tiempo real.

### 📦 [EBPF] Contenedores Alternativos, Redes & eBPF
* **`nerdctl` (containerd CLI):** Cliente CLI para `containerd` compatible con sintaxis de Docker, utilizado en entornos de producción y Kubernetes.
* **Cilium CLI (`cilium`):** CLI oficial de Cilium para redes Cloud Native, cifrado transparente y políticas de seguridad basadas en eBPF.
* **Hubble CLI (`hubble`):** CLI de Hubble para observabilidad profunda de red (L3/L4/L7) e inspección de tráfico en Kubernetes.

### 📦 [LANG] Lenguajes & Runtimes DevOps
* **Go (`go`):** Lenguaje de programación base del ecosistema Cloud Native (Docker, K8s, Terraform y Cilium).
* **Python (`python`):** Lenguaje estándar para scripting de automatización, testing de infraestructura y SDKs cloud (`boto3`, `azure-sdk`).

### 📦 [AI] Suite de Agentes de Inteligencia Artificial (AIOps)
* **Claude Code CLI (`claude`):** Agente autónomo de Anthropic para terminal con capacidades de refactorización y ejecución.
* **OpenAI GPT CLI (`sgpt`):** CLI para consultas directas a modelos de lenguaje GPT.
* **OMP (`omp` - omp.sh):** Agente agnóstico de IA para terminal que conecta modelos (Claude, OpenAI, Gemini, Ollama).
* **Antigravity CLI (`agy`):** CLI agéntico avanzado de Google DeepMind.

---

## ⚡ 3. Instalación Automatizada con `instalar-tools-devops.ps1`

El instalador (`instalar-tools-devops.ps1`) escanea tu sistema en tiempo real, detecta qué herramientas ya tienes instaladas para no descargarlas dos veces y ofrece 3 modos de ejecución:

```powershell
# Abrir PowerShell como Administrador:
cd "scripts"
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1
```

### Opciones del Menú:
1. **[Opción 1] Solo Software Base DevOps (Core Esencial):**
   * Instala las 12 herramientas oficiales obligatorias (Zoom, Git, **GitHub CLI (gh)**, VS Code, Docker, Terraform, **AWS CLI**, **Azure CLI**, Kubectl, Helm, Minikube, **jq**).
   * *Atajo directo:* `.\instalar-tools-devops.ps1 -SoloObligatorio`
2. **[Opción 2] Ecosistema Completo:**
   * Gestiona las 31 herramientas (Obligatorias + todas las Optativas).
   * *Atajo directo:* `.\instalar-tools-devops.ps1 -Completo`
3. **[Opción 3] Selección Personalizada por Categorías o Números:**
   * Muestra las herramientas agrupadas por categoría con su estado `[YA INSTALADO]` vs `[PENDIENTE]`.
   * Puedes ingresar códigos de categoría (`BASE`, `AI`, `TUI`, `TERM`, `EBPF`, `LANG`), números (`1-12`, `13-18`, `19-23`) o combinaciones (`BASE, AI, 13`).

### 🔐 Autenticación Obligatoria con GitHub CLI (`gh`):
Para clonar los repositorios privados y públicos de cada proyecto, sincronizar ramas y entregar laboratorios, es obligatorio autenticarse una sola vez en el sistema:
```powershell
# Iniciar sesión en GitHub desde PowerShell:
gh auth login
# 1. ¿Qué cuenta deseas conectar? -> GitHub.com
# 2. ¿Protocolo preferido para Git? -> HTTPS
# 3. ¿Autenticar Git con tus credenciales de GitHub? -> Yes (Y)
# 4. ¿Cómo deseas autenticar? -> Login with a web browser
# 5. Copia el código de 8 caracteres que aparece en terminal, pulsa Enter y pégalo en el navegador.
```
Para comprobar que estás autenticado en cualquier momento:
```powershell
gh auth status
```

### 🚀 Instalación Rápida por Línea de Comandos (Sin Menús):
```powershell
# Instalar todo el Software Base Obligatorio:
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -SoloObligatorio

# Instalar toda la categoría de Terminales, XMPP y Editores:
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria TERM

# Instalar toda la suite de IA:
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria AI
```

---

## 🔍 4. Verificación del Estado del Entorno

Para comprobar qué herramientas tienes instaladas y cuáles te faltan, ejecuta en cualquier momento:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```

El verificador escanea en 2 segundos el cumplimiento de los **Requisitos Base Obligatorios (Mandatory)** y el estado de las **Herramientas Optativas**.
