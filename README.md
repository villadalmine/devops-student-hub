# 🎓 Cloud DevOps Student Hub & Learning OS

> **Curso:** Cloud DevOps: Automatización y Despliegue (EducaciónIT - DEVO07)  
> **Tu Segundo Cerebro Técnico:** Entorno offline-first con Tutor de IA local, apuntes, reproductor de clases y banco de autoevaluación.

---

## 🌟 ¿Qué es este Campus Personal?

Este repositorio es tu **Espacio de Aprendizaje Personal (Second Brain)** para las 12 clases del curso y para tu futura carrera como Ingeniero DevOps.

A diferencia de un simple repositorio de código, aquí cuentas con:
1. 🚀 **Instalador Automatizado de Herramientas:** Provisiona en minutos todo el software oficial de Alumni en Windows.
2. 🤖 **Tutor Personal de IA con RAG Local:** Un asistente inteligente conectado a tu base de datos SQLite FTS5 (`data/devops_knowledge.db`) que responde dudas citando tus propios apuntes, diapositivas y transcripciones.
3. 🎥 **Reproductor Local de Grabaciones:** Para ver tus clases locales (`.mp4`) o enlaces web sin depender de plataformas externas.
4. 📝 **12 Plantillas de Apuntes en Markdown:** Listas para estructurar conceptos clave, comandos practicados y dudas.
5. 🧩 **Simulador de Quizzes & Exámenes:** Banco interactivo de autoevaluación técnica con respuestas fundamentadas.

---

## 🚀 Guía de Inicio Rápido (En 3 Pasos)

### Paso 1: Instalar el Software Base Obligatorio
Abre PowerShell como **Administrador** en esta carpeta y ejecuta:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\instalar-tools-devops.ps1 -SoloObligatorio
```
Esto instalará las 12 herramientas obligatorias (`Zoom, Git, GitHub CLI, VS Code, Docker, Terraform, AWS CLI, Azure CLI, kubectl, Helm, Minikube, jq`).

> [!IMPORTANT]
> **Autenticación con GitHub (Obligatorio):**  
> Para poder sincronizar este repositorio en tu cuenta y clonar los ejercicios de clase, ejecuta:
> ```powershell
> gh auth login
> ```
> *(Selecciona: GitHub.com ➔ HTTPS ➔ Yes ➔ Login with a web browser).*

Para verificar que todo tu entorno esté al 100%, corre:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\verificar-tools.ps1
```

---

### Paso 2: Iniciar tu Campus Web en 1 Clic
Haz doble clic en el archivo:
```text
🚀 iniciar-mi-hub.bat
```
Se abrirá automáticamente tu navegador en **`http://localhost:8080`** con el portal web interactivo.

---

### Paso 3: Usar tu Tutor de IA y Tomar Apuntes
* **Para Estudiar:** En la pestaña **"Tutor IA & Chat"**, haz cualquier pregunta técnica. El asistente buscará en tus apuntes y materiales.
* **Para Practicar:** Cambia el modo a **"Simulador de Examen"** y pídele: *"Tomame un quiz de 3 preguntas de la Clase 1"*.
* **Para Tomar Notas:** Abre la carpeta `mis_apuntes/` y edita `Clase_01_Apuntes.md` con tus notas de cada clase.

---

## 📁 Estructura del Repositorio

```text
dist_alumnos/
├── 🚀 iniciar-mi-hub.bat             # 1 clic: Inicia el servidor local y abre el navegador
├── 🔄 actualizar-mi-base.bat         # 1 clic: Re-escanea apuntes y PDFs en tu base SQLite
├── 📄 course_hub.html                # Portal Web del Estudiante
│
├── 📂 mis_apuntes/                   # 📝 Tus notas Markdown clase por clase (Clase 01 a 12)
├── 📂 mis_videos/                    # 🎥 Tus videos locales (.mp4) o URLs en clases.json
├── 📂 material_clases/               # 📚 Diapositivas, PDFs y cheat sheets de referencia
├── 📂 examenes_y_practicas/          # 🧩 Quizzes de autoevaluación y desafíos prácticos
├── 📂 transcripciones/               # 🎙️ Subtítulos o transcripciones de audio/video
├── 📂 player/                        # 🎬 Reproductor local de videos
├── 📂 data/                          # 💾 Base de conocimiento SQLite FTS5 (devops_knowledge.db)
└── 📂 scripts/                       # 🛠️ Scripts de instalación, diagnóstico y RAG
```

---

## 🔄 ¿Cómo Actualizar tu Base de Conocimiento RAG?

Cada vez que agregues un PDF a `material_clases/`, tomes nuevos apuntes en `mis_apuntes/` o descargues una transcripción:
1. Haz doble clic en **`actualizar-mi-base.bat`** (o pulsa el botón **"Actualizar Base"** en la web).
2. En **2 segundos**, SQLite indexará todo el texto nuevo.
3. Tu Tutor IA ahora podrá responder citando esa nueva información.

---

## 🤖 Configuración del Motor de IA (Opcional)

El Asistente funciona **100% offline out-of-the-box** usando el motor de búsqueda semántica SQLite FTS5. Si deseas respuestas redactadas con razonamiento conversacional generativo:

* **Opción A: Google Gemini (Recomendado y Gratuito)**
  Obtén una clave gratuita en [Google AI Studio](https://aistudio.google.com/) y define la variable en tu sistema:
  ```powershell
  [System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "tu-clave-aqui", "User")
  ```

* **Opción B: Ollama Local (100% Privado y Offline)**
  Instala Ollama y descarga un modelo ligero:
  ```powershell
  ollama run qwen2.5
  ```
  El servidor asistente detectará automáticamente Ollama en `http://localhost:11434`.

---

## 🐙 Cómo Guardar tus Avances en tu Propio GitHub

Para respaldar tus notas, ejercicios y avances en tu perfil de GitHub:
```powershell
# 1. Guarda tus cambios
git add .
git commit -m "docs: apuntes y ejercicios de la clase"

# 2. Súbelos a tu repositorio personal
git push origin main
```

---

## 📅 Cronograma de las 12 Clases

| Clase | Módulo | Tema Principal |
| :---: | :--- | :--- |
| **Clase 01** | M1: Fundamentos | Introducción a DevOps, Cultura CALMS, Métricas DORA y Git |
| **Clase 02** | M1: Fundamentos | GitFlow, Trunk-Based Development, Pull Requests y Code Review |
| **Clase 03** | M2: Cloud AWS | Cloud Computing, Modelo de Responsabilidad, AWS IAM y Amazon S3 |
| **Clase 04** | M2: Cloud AWS | Cómputo EC2, Redes VPC, Subnets, Route Tables y Security Groups |
| **Clase 05** | M3: Terraform | Infraestructura como Código (IaC), Sintaxis HCL, Providers y Recursos |
| **Clase 06** | M3: Terraform | Terraform State, S3 Backend + DynamoDB locking y LocalStack |
| **Clase 07** | M4: Docker | Contenerización, Docker Engine, Dockerfiles y Multi-Stage Builds |
| **Clase 08** | M4: Docker | Docker Compose Multi-servicio, Redes, Volúmenes y Seguridad |
| **Clase 09** | M5: Kubernetes | Orquestación con K8s, Arquitectura, Pods, Deployments y Auto-healing |
| **Clase 10** | M5: Kubernetes | Services (ClusterIP, NodePort, LoadBalancer), Ingress, Secrets y Helm |
| **Clase 11** | M6: CI/CD | Pipelines automatizados con GitHub Actions y GitOps con Argo CD |
| **Clase 12** | M7: AWS Containers | Contenedores en AWS (ECS, Fargate, EKS), Monitoreo CloudWatch y Cierre |
