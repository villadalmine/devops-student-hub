# 🍎 Guía Completa de Instalación de Herramientas Cloud DevOps para macOS

> **Arquitecturas Soportadas:** Apple Silicon (M1, M2, M3, M4) e Intel Mac  
> **Gestor Principal:** Homebrew (`brew`)  
> **Objetivo:** Configurar una estación de trabajo completa para Cloud DevOps con las 32 herramientas del curso.

---

## 🚀 Método Rápido y Automatizado (Recomendado)

Hemos creado un script que verifica e instala automáticamente todas las dependencias usando Homebrew:

```bash
# 1. Dar permisos de ejecución
chmod +x ./scripts/instalar-tools-macos.sh ./scripts/verificar-tools.sh

# 2. Opción A: Instalar SOLO el Software Base Obligatorio (12 herramientas)
./scripts/instalar-tools-macos.sh --base

# 3. Opción B: Instalar el Ecosistema Completo (Obligatorio + Optativos)
./scripts/instalar-tools-macos.sh --all

# 4. Opción C: Instalar por Categorías Específicas
./scripts/instalar-tools-macos.sh --categoria BASE
./scripts/instalar-tools-macos.sh --categoria TUI
./scripts/instalar-tools-macos.sh --categoria EBPF
./scripts/instalar-tools-macos.sh --categoria AI

# 5. Comprobar la instalación:
./scripts/verificar-tools.sh
```

---

## 📦 Instalación Manual por Categorías con Homebrew

Si prefieres ejecutar los comandos manualmente:

### 1. ⚙️ Categoría BASE (Core Esencial Obligatorio)

```bash
# Herramientas CLI
brew install git gh jq terraform awscli azure-cli kubectl helm minikube

# Aplicaciones de Escritorio (Casks)
brew install --cask zoom visual-studio-code docker
```

* **Nota para Docker Desktop en macOS:** Al abrirlo por primera vez, macOS solicitará permisos para crear el socket de Docker en `/var/run/docker.sock`.

---

### 2. 💻 Categoría TERM (Terminales y Editores Modernos)

```bash
brew install neovim
brew install --cask ghostty zed vlc gajim

# Herdr Multiplexer
npm install -g herdr
```

---

### 3. 🖥️ Categoría TUI (Herramientas TUI de Productividad)

```bash
# Buscador difuso y gestores TUI
brew install fzf lazygit yazi
brew install jesseduffield/lazydocker/lazydocker
brew install derailed/k9s/k9s
```

---

### 4. 🌐 Categoría EBPF (Redes y Observabilidad en K8s)

```bash
brew install cilium-cli hubble nerdctl trivy
```

---

### 5. 🐍 Categoría LANG (Lenguajes y Runtimes: Go, Python & Rust)

```bash
brew install go python@3.12 node rust
```

---

### 6. 🤖 Categoría AI (Agentes Inteligentes en Terminal)

```bash
# Claude Code CLI (Anthropic)
npm install -g @anthropic-ai/claude-code

# Shell-GPT (sgpt)
pip3 install --user shell-gpt

# OMP (Oh My Pi)
curl -fsSL https://omp.sh | bash
```

---

## 🔍 Verificación Final

Ejecuta el script de diagnóstico para verificar que todos los comandos estén en tu `PATH`:
```bash
./scripts/verificar-tools.sh
```
