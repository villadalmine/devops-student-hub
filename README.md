# 🚀 Universal Student Hub & DevOps Workspace

> **Plataforma Educativa Universal & Panel de Control Local:** Un chasis de aprendizaje modular, interactivo y multiplataforma (**Windows**, **Linux**, **macOS**) que se adapta dinámicamente a cualquier curso y corre **100% en local** sin Docker ni dependencias externas.

---

## ⚡ 1. Inicio Rápido (En 1 Clic)

No necesitas configurar entornos complejos ni tener Docker instalado. Puedes iniciar el portal directamente:

### 🪟 En Windows (Sin requerir Python):
1. Descarga el ejecutable standalone:  
   👉 **[⬇️ Descargar student-hub.exe (Release v1.0.0)](https://github.com/villadalmine/devops-student-hub/releases/latest/download/student-hub.exe)**
2. Haz doble clic sobre **`student-hub.exe`** (o sobre **`iniciar-mi-hub.bat`**).
3. ¡Listo! Tu navegador se abrirá automáticamente en **`http://localhost:8081`**.

### 🐧 Linux / 🍎 macOS:
```bash
chmod +x ./iniciar-mi-hub.sh
./iniciar-mi-hub.sh
# O directamente con Python 3:
python3 scripts/servidor_asistente.py 8081
```

---

## 🖥️ 2. El Hub Dashboard: ¿Cómo Funciona?

El **Student Hub** centraliza toda tu experiencia de clase en una interfaz visual moderna (`http://localhost:8081`) dividida en módulos interactivos:

| Módulo | ¿Para qué sirve? |
| :--- | :--- |
| **🩺 Diagnóstico del Sistema** | Escanea en tiempo real qué herramientas tienes en tu `PATH`. Muestra tu % de preparación para el curso y te permite instalar lo que falte abriendo una terminal con 1 clic. |
| **⚡ Instalación & Software Multi-OS** | Selector interactivo de sistema operativo (Windows, Linux, macOS) con comandos automáticos para las 33 herramientas del curso sin tener que buscar documentación manual. |
| **🎒 Mis Aportes & Notas** | Tu espacio de trabajo personal. Redacta notas en Markdown y usa el botón **📥 Exportar Mis Aportes (.ZIP)** para empaquetar tus apuntes y compartirlos con el docente. |
| **🌐 Glosario & Labs en Navegador** | Directorio con simuladores de terminal web (iximiuz, Killercoda, SadServers) para practicar sin romper tu máquina, más chuletas listas para copiar al chat de clase. |
| **📚 Apuntes & Guías Oficiales** | Visualizador integrado de documentos Markdown y acceso offline al libro ilustrado de la CNCF: *"The Illustrated Children's Guide to Kubernetes"* (PDF 15 MB). |
| **🎥 Reproductor de Clases** | Streaming local inteligente (`HTTP Range 206`) para repasar grabaciones MP4 en tu disco con reproducción continua y sin saturar tu red. |
| **📡 Telemetría en Vivo** | Monitor en tiempo real de llamadas HTTP, eventos del servidor y estado del sistema. |

---

## 🧩 3. Arquitectura Genérica: Una Plataforma para Cualquier Curso

El **Student Hub** no está cableado de forma rígida a una única materia; es un **chasis educativo universal** diseñado con los siguientes principios:

```
┌─────────────────────────────────────────────────────────────────┐
│                      STUDENT HUB CHASSIS                        │
│          (Servidor Local + UI Reactiva + Diagnóstico)           │
└────────────────┬───────────────────────────────┬────────────────┘
                 │                               │
                 ▼                               ▼
       ┌──────────────────┐            ┌──────────────────┐
       │    curso.json    │            │   mis_apuntes/   │
       │ (Manifiesto del  │            │ (Notas y Labs    │
       │      Curso)      │            │  del Estudiante) │
       └──────────────────┘            └─────────┬────────┘
                 │                               │
                 ▼                               ▼
      Adapta la plataforma:           Exportación en 1 clic:
      - Título y Comisión             📥 aportes_alumno.zip
      - Categorías y Módulos          (Listo para compartir
      - Herramientas a chequear        y sumar al curso)
```

### 1️⃣ Manifiesto Declarativo (`curso.json`)
La plataforma lee al iniciar el archivo [`curso.json`](curso.json). Si mañana el curso es de **Kubernetes Avanzado**, **Python** o **Cloud AWS**, solo se actualiza ese JSON y la UI adapta títulos, insignias, horas y categorías automáticamente sin alterar el código de la aplicación.

### 2️⃣ Material Oficial Protegido vs. Plataforma Abierta
Los alumnos instalan y ejecutan libremente la plataforma en sus computadoras. El material privado de la cursada se mantiene protegido por el docente, quien puede ir desbloqueando y distribuyendo contenidos según el avance de las clases.

### 3️⃣ Ecosistema de Aportes Colaborativos
Los alumnos no son meros espectadores:
- Pueden crear sus propios laboratorios, scripts de apoyo y resúmenes.
- Al pulsar **Exportar Mis Aportes (.ZIP)**, el Hub genera un paquete con su metadata y archivos locales.
- El docente puede revisar estos aportes y, si aportan valor a la comunidad, incorporarlos al repositorio oficial del curso.

---

## 📁 4. Estructura del Repositorio

```text
dist_alumnos/
├── student-hub.exe            # Binario standalone para Windows (no requiere Python)
├── iniciar-mi-hub.bat         # Lanzador rápido Windows (detecta .exe o Python)
├── iniciar-mi-hub.sh          # Lanzador rápido Linux / macOS
├── curso.json                 # Manifiesto dinámico del curso actual
├── devops_hub.html            # Dashboard principal interactivo
├── glosario_recursos_devops.html # Visor de glosario y directorio de labs web
├── mis_apuntes/               # Carpeta personal de trabajo del estudiante
├── practicas/                 # Enunciados y laboratorios prácticos
├── material/                  # Guías PDF (incluye Guía Ilustrada de K8s CNCF)
├── videos/                    # Carpeta para colocar grabaciones locales MP4
└── scripts/
    ├── servidor_asistente.py  # Backend HTTP multihilo y API REST
    └── instalar-tools-*       # Automatizadores de software para cada OS
```

---

## 🤝 Soporte y Comunidad

Si tienes dudas sobre el entorno o sugerencias de herramientas para incorporar al Hub, abre un issue en el repositorio o compártelo en clase mediante la función de exportación de aportes.
