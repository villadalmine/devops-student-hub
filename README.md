# 🚀 Cloud DevOps Workspace & Automation Hub

> **Entorno Profesional DevOps para Windows:** Instalador automatizado de herramientas con Winget, base de conocimiento RAG local y asistente de IA de arquitectura abierta y agnóstica.

---

## 💡 ¿Qué es este Repositorio?

Este repositorio es una estación de trabajo completa pensada para ingenieros, desarrolladores y estudiantes de **Cloud DevOps e Infraestructura moderna**. 

Está diseñado bajo dos principios fundamentales:
1. **📦 Automatización de Software sin Fricción:** Provisiona y diagnostica en Windows todo el conjunto de herramientas esenciales de la industria (Git, GitHub CLI, Docker, Kubernetes, Terraform, Cloud CLIs de AWS y Azure, etc.) mediante scripts de PowerShell y **Windows Package Manager (Winget)**.
2. **🧠 Espacio de Conocimiento Libre y Agnóstico (Second Brain + RAG):** **No está atado a ningún curso ni estructura rígida de clases**. Puedes crear libremente cualquier carpeta que necesites (`apuntes/`, `material/`, `practicas/`, `videos/`, `certificaciones/`, `docker/`, `kubernetes/`, etc.). El motor local indexa automáticamente tus notas Markdown, guías y PDFs en una base de datos **SQLite FTS5** y te brinda un **Tutor de IA interactivo** que responde citando tus propios documentos.

---

## ⚡ 1. Instalación y Diagnóstico del Software DevOps

Todo el proceso de instalación es automatizado, idempotente y utiliza herramientas oficiales de Microsoft y de los creadores de cada tecnología.

### Paso A: Instalar el Software Base (Core Esencial)
Abre **PowerShell como Administrador** en la raíz de este repositorio y ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloBase
```

Este comando instala el conjunto core recomendado:
* **Control de Versiones & Colaboración:** `Git for Windows`, `GitHub CLI (gh)`.
* **Editor & Entorno:** `Visual Studio Code`.
* **Contenedores & Virtualización:** `Docker Desktop` (con WSL2 backend).
* **Infraestructura como Código (IaC):** `HashiCorp Terraform`.
* **Nubes Públicas:** `AWS CLI (v2)`, `Azure CLI (az)`.
* **Orquestación de Contenedores:** `Kubernetes CLI (kubectl)`, `Helm`, `Minikube`.
* **Procesamiento de Datos:** `jq` (filtro de respuestas JSON para scripts y pipelines).

*(Si deseas un menú interactivo con herramientas optativas adicionales como Ansible, Vagrant, Packer, K9s o Trivy, ejecuta simplemente `.\scripts\instalar-tools-devops.ps1`).*

---

### Paso B: Autenticarte con GitHub CLI (gh)
Para vincular tu cuenta de GitHub, clonar repositorios y sincronizar tus cambios:

```powershell
gh auth login
```
> Elige: `GitHub.com` ➔ `HTTPS` ➔ `Yes` (autenticar Git credential helper) ➔ `Login with a web browser` e introduce el código de un solo uso que te muestra la terminal.

---

### Paso C: Verificar y Diagnosticar tu Entorno
Comprueba que todos los comandos, variables de entorno `PATH` y servicios estén 100% operativos:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```

---

## 🌐 2. Knowledge Hub & Asistente IA Local

El repositorio incluye un servidor web local y un panel de control con motor RAG (Retrieval-Augmented Generation).

### Iniciar el Hub en 1 Clic
Haz doble clic sobre:
```text
▶ iniciar-mi-hub.bat
```
*(O ejecuta `python scripts/servidor_asistente.py`).*  
Se abrirá automáticamente tu navegador en **`http://localhost:8080`**.

### Características del Hub:
* **💬 Tutor IA DevOps:** Un asistente pedagógico con 4 modos:
  * *Tutor DevOps:* Conceptos de arquitectura cloud, Twelve-Factor App, DORA metrics y GitOps.
  * *Laboratorio & Terminal:* Depuración de errores en consola, sintaxis de Dockerfiles, Terraform HCL y manifests de K8s.
  * *Certificaciones & Entrevistas:* Simulador de preguntas técnicas (AWS, CKA, Docker, Terraform).
  * *Documentación Local:* Preguntas que se responden consultando directamente tus notas locales.
* **📁 Explorador Dinámico:** Muestra y agrupa en tarjetas todas las carpetas y documentos que vayas agregando.
* **🔍 Buscador RAG SQLite FTS5:** Búsqueda a texto completo ultrarrápida sobre todos tus apuntes y PDFs.
* **🎬 Reproductor de Video Local:** Transmite de forma fluida (`HTTP Range 206`) cualquier video que coloques en la carpeta `videos/`.

---

## 📂 Organización de Carpetas (Flexible y Libre)

Puedes estructurar tus directorios como mejor se adapte a tu flujo de trabajo. Una estructura sugerida:

```text
├── apuntes/                 # Notas técnicas en Markdown (.md)
│   ├── 01_Fundamentos_DevOps_y_Git.md
│   └── README.md
├── material/                # Libros, diapositivas, PDFs oficiales y cheat sheets
│   └── README.md
├── practicas/               # Dockerfiles, docker-compose, scripts bash/powershell, Terraform HCL
│   └── README.md
├── videos/                  # Grabaciones de clases, talleres o tutoriales (.mp4, .mkv, .webm)
│   └── README.md
├── data/                    # Base de datos SQLite FTS5 (devops_knowledge.db)
├── scripts/                 # Scripts PowerShell de instalación y motor RAG en Python
│   ├── instalar-tools-devops.ps1
│   ├── verificar-tools.ps1
│   ├── crear_indice_rag.py
│   └── servidor_asistente.py
├── course_hub.html          # Panel Web interactivo
├── player/                  # Reproductor de video local
├── iniciar-mi-hub.bat       # Lanzador en 1 clic
└── actualizar-mi-base.bat   # Re-indexador en 1 clic
```

> **¿Quieres agregar una nueva carpeta?**  
> Simplemente crea carpetas como `certificaciones/`, `aws-solutions-architect/`, `docker-labs/`, guarda archivos `.md` o `.pdf` dentro, y haz clic en **"Actualizar Base"** (o ejecuta `actualizar-mi-base.bat`). El sistema la detectará e indexará automáticamente.

---

## 🔄 Cómo Actualizar la Base de Conocimiento

Cada vez que agregues nuevos apuntes o descargues un libro/PDF:
1. Haz doble clic en **`actualizar-mi-base.bat`** (o pulsa el botón **"Actualizar Base"** en la interfaz web).
2. El script `scripts/crear_indice_rag.py` escaneará recursivamente todas tus carpetas y actualizará el índice de búsqueda en segundos.

---

## 🤖 Proveedores de IA Soportados

El Asistente RAG funciona **100% offline out-of-the-box** recuperando citas textuales y correlacionando fuentes locales desde SQLite. Si deseas habilitar redacción y razonamiento conversacional con LLMs generativos:

* **Opción A: Google Gemini (Gratuito)**  
  Genera una clave gratuita en [Google AI Studio](https://aistudio.google.com/) y configúrala en PowerShell:
  ```powershell
  [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "tu-clave-aqui", "User")
  ```
* **Opción B: Ollama Local (100% Privado y Offline)**  
  Instala [Ollama](https://ollama.com/) y ejecuta tu modelo preferido (ej: `ollama run qwen2.5`). El servidor lo detectará automáticamente en el puerto 11434.

---

## 📄 Licencia

Código abierto bajo licencia MIT. ¡Siéntete libre de adaptarlo, bifurcarlo y utilizarlo para tu propio aprendizaje continuo!
