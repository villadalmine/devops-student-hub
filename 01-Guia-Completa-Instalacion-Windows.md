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

| Herramienta | Versión Mínima / ID Winget | Propósito y Uso |
| :--- | :---: | :--- |
| **Zoom Workplace** | `Zoom.Zoom` (6.0+) | Plataforma para reuniones, demos y sesiones técnicas en vivo. |
| **Git for Windows** | `Git.Git` (2.40+) | Control de versiones distribuido y trabajo con ramas. |
| **Visual Studio Code** | `Microsoft.VisualStudioCode` | IDE principal para edición de código, Dockerfiles, YAML y HCL. |
| **Docker Desktop (+ WSL 2)** | `Docker.DockerDesktop` (4.25+) | Motor de contenerización Linux en Windows. |
| **HashiCorp Terraform** | `Hashicorp.Terraform` (1.5+) | Aprovisionamiento de Infraestructura como Código (IaC). |
| **AWS CLI (v2)** | `Amazon.AWSCLI` (2.15+) | Gestión, aprovisionamiento y autenticación con Amazon Web Services. |
| **Azure CLI (az)** | `Microsoft.AzureCLI` (2.50+) | Gestión, suscripciones y despliegue en Microsoft Azure Cloud. |
| **Kubernetes CLI (kubectl)** | `Kubernetes.kubectl` (1.28+) | Administración de clústeres y despliegue de manifiestos. |
| **Helm** | `Helm.Helm` (3.12+) | Gestor de paquetes y charts para Kubernetes. |
| **Minikube** | `Kubernetes.minikube` (1.32+) | Clúster local ligero de Kubernetes para pruebas y laboratorios. |
| **jq (JSON Processor)** | `jqlang.jq` (1.7+) | Procesamiento, parsing y filtrado de respuestas JSON en pipelines y CLIs. |
| **WSL 2 (Ubuntu)** | Kernel 5.10+ | Subsistema de Linux para Windows (backend de Docker). |

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

### 📦 [EBPF] Contenedores Alternativos, Redes, Seguridad & eBPF
* **`nerdctl` (containerd CLI):** Cliente CLI para `containerd` compatible con sintaxis de Docker, utilizado en entornos de producción y Kubernetes.
* **Cilium CLI (`cilium`):** CLI oficial de Cilium para redes Cloud Native, cifrado transparente y políticas de seguridad basadas en eBPF.
* **Hubble CLI (`hubble`):** CLI de Hubble para observabilidad profunda de red (L3/L4/L7) e inspección de tráfico en Kubernetes.
* **Trivy (`trivy`):** Escáner integral de vulnerabilidades (CVEs), secretos y malas prácticas de seguridad para imágenes Docker, clústeres de K8s y plantillas Terraform (IaC).

### 📦 [LANG] Lenguajes & Runtimes DevOps
* **Go (`go`):** Lenguaje de programación base del ecosistema Cloud Native (Docker, K8s, Terraform y Cilium).
* **Python (`python`):** Lenguaje estándar para scripting de automatización, testing de infraestructura y SDKs cloud (`boto3`, `azure-sdk`).
* **Rust (`rustc` / `cargo`):** Lenguaje de sistemas moderno para herramientas Cloud, CLIs de ultra-alta velocidad y controladores eBPF.

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
   * Gestiona las 32 herramientas (Obligatorias + todas las Optativas).
   * *Atajo directo:* `.\instalar-tools-devops.ps1 -Completo`
3. **[Opción 3] Selección Personalizada por Categorías o Números:**
   * Muestra las herramientas agrupadas por categoría con su estado `[YA INSTALADO]` vs `[PENDIENTE]`.
   * Puedes ingresar códigos de categoría (`BASE`, `AI`, `TUI`, `TERM`, `EBPF`, `LANG`), números (`1-12`, `13-18`, `19-23`, `24-27`) o combinaciones (`BASE, AI, 13`).

### 💡 Uso de la Terminal en Windows: ¿Por qué evitamos `curl.exe` y usamos PowerShell nativo?
> [!TIP]
> **PowerShell nativo vs. `curl.exe` en Windows:**  
> En Windows PowerShell 5.1 (la consola predeterminada de Windows), `curl` **no es el comando de Linux**, sino un alias interno de `Invoke-WebRequest`. Si intentas ejecutar comandos típicos de Linux como `curl -fsSL https://...` o `curl -Lo ...`, PowerShell arrojará un error de sintaxis (`A parameter cannot be found that matches parameter name 'fsSL'`).  
> Por esta razón:
> 1. **Nunca ejecutamos `curl.exe` ni sintaxis Unix de curl en las terminales o scripts de Windows.**
> 2. Utilizamos siempre los cmdlets nativos y confiables de PowerShell:
>    - `Invoke-WebRequest -Uri <URL> -OutFile <DESTINO> -UseBasicParsing` (alias nativo: `iwr`)
>    - `Invoke-RestMethod -Uri <URL>` (alias nativo: `irm`)
>    - `winget install <ID>` para descargas y actualizaciones gestionadas.

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

# Instalar toda la categoría de Redes, Seguridad y eBPF (incluyendo Trivy):
powershell -ExecutionPolicy Bypass -File .\instalar-tools-devops.ps1 -Categoria EBPF

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

---

## 🐳 5. Docker en Windows: Docker Desktop vs. Docker Engine Nativo en WSL 2

Para trabajar con contenedores en Windows dentro de tus proyectos y entornos Cloud DevOps dispones de **dos caminos de arquitectura**. Ambos son 100% válidos y compatibles:

1. **Opción A: Docker Desktop para Windows (con backend WSL 2)**
2. **Opción B: Docker Engine nativo corriendo directamente dentro de WSL 2 (Ubuntu)**

---

### ⚖️ Comparativa: ¿Por qué elegir una opción u otra?

| Criterio | Opción A: Docker Desktop | Opción B: Docker Engine en WSL 2 |
| :--- | :--- | :--- |
| **Licenciamiento Empresarial** | ⚠️ **De Pago** para empresas con >250 empleados o >$10M USD de facturación anual. Gratis solo para estudiantes, open source y empresas pequeñas. | 🟢 **100% Gratuito y Open Source** (Licencia Apache 2.0 / Moby). Sin restricciones comerciales ni de tamaño corporativo. |
| **Consumo de Memoria RAM** | ⚠️ **Alto (2 GB a 4.5 GB)** en reposo debido a las máquinas virtuales auxiliares (`docker-desktop` y `docker-desktop-data`) y la UI de Electron. | 🟢 **Bajo (300 MB a 600 MB)** en reposo. Se ejecuta como un servicio nativo de Linux dentro de tu distribución. |
| **Interfaz de Usuario** | 🖥️ **Interfaz Gráfica (GUI)** con panel de control, monitoreo visual de contenedores, extensiones y configuración con clics. | 💻 **Línea de Comandos (CLI)** pura. Se complementa con **Lazydocker** (TUI interactiva de terminal) y la extensión Docker de VS Code. |
| **Rendimiento de E/S de Disco** | Bueno, pero con capa de traducción entre Windows y la VM de Docker Desktop. | 🚀 **Rendimiento Linux Nativo** dentro del sistema de archivos de WSL 2 (`/home/...`). |
| **Integración con Kubernetes** | Incluye clúster Kubernetes local de un solo nodo activable con una casilla en Settings. | Utiliza **Minikube** o **k3d/kind** de forma ultraligera en WSL 2. |
| **Recomendado para...** | Principiantes que valoran paneles visuales o equipos sin restricciones de licencias de Docker Inc. | Desarrolladores DevOps profesionales, equipos corporativos que evitan costos de licencias y notebooks con 8 GB o 16 GB de RAM. |

---

### 🛠️ Configuración Paso a Paso: Opción A (Docker Desktop + WSL 2)

1. **Asegurar que WSL 2 esté instalado:**
   ```powershell
   wsl --install
   ```
2. **Instalar Docker Desktop mediante Winget:**
   ```powershell
   winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
   ```
3. **Reiniciar el equipo si Windows lo solicita.**
4. **Configuración en la interfaz de Docker Desktop:**
   * Abre Docker Desktop desde el Menú Inicio.
   * Dirígete a **Settings (icono de engranaje) ➔ General**.
   * Verifica que esté activada la casilla **"Use the WSL 2 based engine"**.
   * Ve a **Settings ➔ Resources ➔ WSL Integration**.
   * Activa tu distribución de Linux (ej. `Ubuntu`).
   * Haz clic en **Apply & Restart**.
5. **Verificar en PowerShell:**
   ```powershell
   docker --version
   docker run --rm hello-world
   ```

---

### 🛠️ Configuración Paso a Paso: Opción B (Docker Engine Nativo en WSL 2 - Sin Docker Desktop)

Si prefieres ahorrar memoria RAM o trabajas en una empresa con políticas estrictas de licencias, puedes instalar el motor nativo de Docker dentro de Ubuntu en WSL 2:

#### 1. Instalar o abrir Ubuntu en WSL 2
```powershell
# En PowerShell (si aún no tienes Ubuntu):
wsl --install -d Ubuntu

# Abrir la terminal de Ubuntu:
wsl -d Ubuntu
```

#### 2. Habilitar `systemd` dentro de WSL 2
Para que el demonio `dockerd` arranque automáticamente como servicio del sistema, ejecuta dentro de Ubuntu:
```bash
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true
EOF
```
Sal de Ubuntu (`exit`) y reinicia WSL desde PowerShell en Windows:
```powershell
wsl --shutdown
```

#### 3. Instalar Docker Engine oficial en Ubuntu
Vuelve a entrar a Ubuntu (`wsl -d Ubuntu`) y ejecuta el instalador oficial de Docker:
```bash
# Descargar e instalar Docker Engine oficial:
curl -fsSL https://get.docker.com | sudo sh

# Permitir a tu usuario ejecutar docker sin escribir 'sudo':
sudo usermod -aG docker $USER

# Iniciar o comprobar el servicio docker:
sudo systemctl enable --now docker
sudo systemctl status docker
```
Cierra la terminal de Ubuntu y vuelve a entrar para aplicar el nuevo grupo.

#### 4. Verificar la instalación
```bash
docker run --rm hello-world
```

#### 5. Gestión visual sin Docker Desktop
* **En Terminal (TUI):** Ejecuta `lazydocker` dentro de WSL 2 para ver contenedores, logs, CPU y memoria en una interfaz visual interactiva de alta velocidad.
* **En Visual Studio Code:** Abre VS Code en Windows, instala la extensión **"WSL"** (`ms-vscode-remote.remote-wsl`) y la extensión **"Docker"** (`ms-azuretools.vscode-docker`). Al abrir tu carpeta dentro de WSL 2 (`code .`), VS Code detectará Docker Engine de forma nativa e inmediata.

