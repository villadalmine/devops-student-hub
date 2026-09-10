# 🐧 Guía Completa de Instalación de Herramientas Cloud DevOps para Linux

> **Plataformas Soportadas:** Ubuntu, Debian, Linux Mint, Pop!_OS (vía `apt`) | Fedora, RHEL, Rocky (vía `dnf`) | Arch Linux, Manjaro (vía `pacman`) | WSL2  
> **Objetivo:** Disponer del entorno profesional completo para desarrollo, contenerización, infraestructura como código y automatización Cloud DevOps en entornos Linux.

---

## 🚀 Método Rápido y Automatizado

Hemos preparado un script inteligente que detecta tu distribución automáticamente e instala las 32 herramientas del curso clasificadas en 6 categorías:

```bash
# 1. Dar permisos de ejecución al script
chmod +x ./scripts/instalar-tools-linux.sh ./scripts/verificar-tools.sh

# 2. Opción A: Instalar SOLO el Software Base Obligatorio (12 herramientas esenciales)
./scripts/instalar-tools-linux.sh --base

# 3. Opción B: Instalar el Ecosistema Completo (Obligatorio + Optativos)
./scripts/instalar-tools-linux.sh --all

# 4. Opción C: Instalar por Categorías Específicas
./scripts/instalar-tools-linux.sh --categoria BASE
./scripts/instalar-tools-linux.sh --categoria TUI
./scripts/instalar-tools-linux.sh --categoria EBPF
./scripts/instalar-tools-linux.sh --categoria AI

# 5. Comprobar tu instalación con el verificador:
./scripts/verificar-tools.sh
```

---

## 📋 Catálogo de Herramientas y Comandos Manuales

Si prefieres instalar las herramientas de forma manual o selectiva, a continuación tienes los comandos para **Ubuntu/Debian**:

### 1. ⚙️ Categoría BASE (Core Esencial Obligatorio)

| Herramienta | Descripción | Comando en Ubuntu / Debian |
| :--- | :--- | :--- |
| **Git** | Control de versiones | `sudo apt install -y git` |
| **GitHub CLI (gh)** | CLI para sincronizar con GitHub | `sudo apt install -y gh` |
| **Visual Studio Code** | Editor principal de código | `sudo snap install --classic code` |
| **Docker Engine** | Motor de contenedores | `curl -fsSL https://get.docker.com \| sudo sh && sudo usermod -aG docker $USER` |
| **HashiCorp Terraform** | Infraestructura como Código | `sudo apt install -y terraform` *(añadiendo repo HashiCorp)* |
| **AWS CLI v2** | CLI para Amazon Web Services | Ver snippet abajo |
| **Azure CLI (az)** | CLI para Microsoft Azure | `curl -sL https://aka.ms/InstallAzureCLIDeb \| sudo bash` |
| **kubectl** | CLI para Kubernetes | `curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && sudo install -m 0755 kubectl /usr/local/bin/kubectl` |
| **Helm** | Gestor de paquetes de K8s | `curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 \| bash` |
| **Minikube** | Clúster local de K8s | `curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube` |
| **jq** | Procesador de JSON | `sudo apt install -y jq` |
| **Zoom** | Videoconferencias | `sudo snap install zoom-client` |

#### Instalación rápida de AWS CLI v2 en Linux:
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip
```

---

### 2. 💻 Categoría TERM (Terminales y Editores Modernos)

* **Neovim:** `sudo apt install -y neovim`
* **VLC Media Player:** `sudo apt install -y vlc`
* **Gajim (XMPP):** `sudo apt install -y gajim`
* **Zed Editor:** `curl -f https://zed.dev/install.sh | sh`
* **Herdr Multiplexer:** `sudo npm install -g herdr`

---

### 3. 🖥️ Categoría TUI (Herramientas TUI de Productividad)

* **fzf (Fuzzy Finder):** `sudo apt install -y fzf`
* **Lazygit (TUI Git):**
  ```bash
  LAZYGIT_VERSION=$(curl -s "https://api.github.com/repos/jesseduffield/lazygit/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
  curl -Lo lazygit.tar.gz "https://github.com/jesseduffield/lazygit/releases/latest/download/lazygit_${LAZYGIT_VERSION}_Linux_x86_64.tar.gz"
  tar xf lazygit.tar.gz lazygit
  sudo install lazygit /usr/local/bin
  rm -f lazygit lazygit.tar.gz
  ```
* **Lazydocker (TUI Docker):**
  ```bash
  curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash
  ```
* **k9s (Monitor K8s):**
  ```bash
  K9S_VERSION=$(curl -s "https://api.github.com/repos/derailed/k9s/releases/latest" | grep -Po '"tag_name": "v\K[^"]*')
  curl -Lo k9s.tar.gz "https://github.com/derailed/k9s/releases/latest/download/k9s_Linux_amd64.tar.gz"
  tar xf k9s.tar.gz k9s
  sudo install k9s /usr/local/bin
  rm -f k9s k9s.tar.gz
  ```

---

### 4. 🌐 Categoría EBPF (Redes y Observabilidad en K8s)

* **Cilium CLI:**
  ```bash
  CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
  curl -L --fail --remote-name-all "https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-amd64.tar.gz"
  sudo tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin
  rm cilium-linux-amd64.tar.gz
  ```
* **Hubble CLI:**
  ```bash
  HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/master/stable.txt)
  curl -L --fail --remote-name-all "https://github.com/cilium/hubble/releases/download/${HUBBLE_VERSION}/hubble-linux-amd64.tar.gz"
  sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin
  rm hubble-linux-amd64.tar.gz
  ```
* **Trivy (Aqua Security Scanner):**
  ```bash
  sudo apt-get install -y wget apt-transport-https gnupg lsb-release
  wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | gpg --dearmor | sudo tee /usr/share/keyrings/trivy.gpg > /dev/null
  echo "deb [signed-by=/usr/share/keyrings/trivy.gpg] https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/trivy.list
  sudo apt-get update -y && sudo apt-get install -y trivy
  ```

---

### 5. 🐍 Categoría LANG (Lenguajes y Runtimes: Go, Python & Rust)

```bash
# Instalación de Go, Python, Node.js y Rust vía apt:
sudo apt install -y golang-go python3 python3-pip python3-venv nodejs npm rustc cargo

# O bien instalar la última versión oficial de Rust con rustup:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
```

---

### 6. 🤖 Categoría AI (Agentes Inteligentes en Terminal)

* **Claude Code CLI:**
  ```bash
  sudo npm install -g @anthropic-ai/claude-code
  ```
* **Shell-GPT (sgpt):**
  ```bash
  pip install --user shell-gpt
  ```
* **OMP (Oh My Pi):**
  ```bash
  curl -fsSL https://omp.sh | bash
  ```

---

## 🔍 Diagnóstico Final

Ejecuta en cualquier momento para comprobar el estado de tus herramientas:
```bash
./scripts/verificar-tools.sh
```

---

## 🐧 Uso de Linux: Linux Nativo vs. WSL 2 en Windows

Si ejecutas tu entorno Linux a través de **WSL 2** (Windows Subsystem for Linux en Windows 10/11):
1. **Systemd Habilitado:** Para que Docker Engine, containerd y otros servicios arranquen automáticamente como en un servidor Linux real, asegúrate de configurar `/etc/wsl.conf` con:
   ```ini
   [boot]
   systemd=true
   ```
   Luego ejecuta `wsl --shutdown` desde Windows PowerShell y vuelve a abrir tu terminal Ubuntu.
2. **Rendimiento de Disco:** Almacena siempre tus proyectos y repositorios dentro del sistema de archivos nativo de Linux (ej. `~/proyectos` o `/home/usuario/clase`), **evitando** trabajar sobre montajes de Windows como `/mnt/c/Users/...`, ya que el rendimiento de I/O en ext4 nativo es hasta 10 veces más rápido.
3. **Docker Engine vs. Docker Desktop:** En WSL 2 puedes instalar Docker Engine puro (`sudo apt install docker-ce` o vía script oficial) de manera 100% gratuita y sin restricciones de licencias corporativas, consumiendo menos de 500 MB de RAM frente a los más de 2 GB de Docker Desktop.

