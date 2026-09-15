# 🚀 Universal Student Hub & DevOps Workspace

> **Plataforma Educativa Universal & Panel de Control Local:** Un chasis de aprendizaje modular, interactivo y multiplataforma (**Windows**, **Linux**, **macOS**) que se adapta dinámicamente a cualquier curso y corre **100% en local** sin Docker ni dependencias externas.

---

## ⚡ 1. Inicio Rápido (En 1 Clic)

No necesitas configurar entornos complejos ni tener Docker instalado. Elige tu método:

### 🪟 Opción A: Binario Standalone Windows (Solo .exe, todo empacado)

**Descarga solo el ejecutable** — incluye todos los archivos necesarios:

👉 **[⬇️ Descargar student-hub.exe](https://github.com/villadalmine/devops-student-hub/releases/latest)**

Luego:
```bash
# Haz doble clic en student-hub.exe
# O desde terminal:
./student-hub.exe

# Tu navegador se abrirá en http://localhost:8081
```

**Ventajas:** ✅ Un solo archivo, no necesitas Git ni Python  
**Desventajas:** ❌ Archivo más pesado (~50-100MB), requiere recompilar si hay cambios

---

### 📥 Opción B: Clonar/Descargar Repositorio (Recomendado para desarrollo)

El repositorio completo necesita todos los archivos. Elige **una** opción:

**Con Git (Recomendado):**
```bash
git clone https://github.com/villadalmine/devops-student-hub.git
cd devops-student-hub
./iniciar-mi-hub.ps1      # Windows
./iniciar-mi-hub.sh       # Linux/macOS
```

**O Descargar ZIP:**
👉 **[⬇️ Descargar ZIP](https://github.com/villadalmine/devops-student-hub/releases/latest)** (busca "Source code (.zip)")

Luego:
```bash
# Windows
./iniciar-mi-hub.ps1

# Linux/macOS
chmod +x ./iniciar-mi-hub.sh
./iniciar-mi-hub.sh
# O con Python directo:
python3 scripts/servidor_asistente.py 8081
```

**Ventajas:** ✅ Archivo más pequeño, cambios se reflejan inmediatamente  
**Desventajas:** ❌ Necesitas Python 3 y Git/ZIP

---

## 🔨 2. Recompilar el Binario (Si Hacés Cambios en el Código)

Cada vez que modifiques el código (servidor, HTMLs, etc.), necesitás generar un nuevo binario:

```bash
# 1. Instalar PyInstaller (una sola vez)
pip install pyinstaller

# 2. Compilar (empaca TODO dentro del .exe)
./build.ps1

# 3. El binario estará en: dist/student-hub.exe (~22 MB con todo incluido)
# 4. Copiar a la raíz y/o actualizar la release en GitHub
```

**Importante:** 
- El binario `student-hub.exe` incluye **todos los archivos** (HTMLs, JSONs, scripts, material)
- No necesita estar en el repositorio local; se genera en `dist/`
- Cada cambio en el código requiere recompilar

---

## 🖥️ 3. El Hub Dashboard: ¿Cómo Funciona?

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
| **🤖 Asistente IA (Bot)** | Bot de IA que corre con tu propia clave, tu PC o el CLI que ya tengas instalado — sin costo para la plataforma. Detalle completo en la [sección 6](#-6-asistente-ia--bot-multi-motor-con-tu-propia-clave). |

---

## 🧩 4. Arquitectura Genérica: Una Plataforma para Cualquier Curso

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

## 📁 5. Estructura del Repositorio

```text
dist_alumnos/
├── student-hub.exe            # Binario standalone para Windows (no requiere Python)
├── iniciar-mi-hub.bat         # Lanzador rápido Windows (detecta .exe o Python)
├── iniciar-mi-hub.sh          # Lanzador rápido Linux / macOS
├── curso.json                 # Manifiesto dinámico del curso actual
├── devops_hub.html            # Dashboard principal interactivo
├── glosario_recursos_devops.html # Visor de glosario y directorio de labs web
├── mis_apuntes/               # Carpeta personal de trabajo del estudiante
├── apuntes/                   # Apuntes base del curso (indexables por el Bot IA)
├── practicas/                 # Enunciados y laboratorios prácticos
├── mapa_estudio/              # Acá va el export del docente (mapa_estudio_devops.html) para el RAG local
├── material/                  # Guías PDF (incluye Guía Ilustrada de K8s CNCF)
├── videos/                    # Carpeta para colocar grabaciones locales MP4
└── scripts/
    ├── servidor_asistente.py  # Backend HTTP multihilo y API REST
    └── instalar-tools-*       # Automatizadores de software para cada OS
```

---

## 🤖 6. Asistente IA — Bot multi-motor con tu propia clave

La pestaña **🤖 Asistente IA** es un bot de estudio que corre **enteramente en tu equipo**: la plataforma no paga nada por tus consultas ni ve tu clave. Está inspirado en el diseño abierto de [study-cybercirujas](https://github.com/villadalmine/study-cybercirujas/blob/main/DEVELOPERS.md) — selección explícita de material en vez de RAG ciego, y "traé tu propia clave" en vez de un backend pago compartido.

### Elegí el motor de IA
| Motor | Cómo funciona | Costo |
| :--- | :--- | :--- |
| **🌐 OpenRouter** | Pegás tu clave (se guarda solo en `localStorage` de tu navegador, viaja directo a `openrouter.ai`, nunca pasa por este servidor). Catálogo de 18 modelos (4 gratis + 14 pagos), agrupados por precio. | $0 en los gratis; los pagos se cobran de verdad a tu clave — el bot te muestra una **estimación antes de preguntar** y el **gasto real acumulado** de la sesión. |
| **💻 Ollama local** | Botón "Detectar modelos instalados" lee los modelos que ya tenés descargados (`ollama list`) y los ofrece en un selector — nada de adivinar nombres. Corre 100% en tu PC. | $0, sin clave, sin internet. |
| **🤖 CLI instalada** | Usa el binario que ya instalaste desde la categoría 🤖 Agentes IA (`claude`, `gemini`, `omp` u `codex`) en modo no interactivo. | Según el plan que tengas contratado para esa CLI. |

Un indicador siempre visible arriba del botón "Preguntar" te muestra exactamente qué se va a enviar (*"Vas a preguntar con: 💻 Ollama local · qwen2.5:7b · 📎 con material: ..."*), y cada pregunta que mandás queda etiquetada en el chat con lo que realmente se usó — para que nunca haya dudas de si el material se está teniendo en cuenta.

### De dónde sale el material de contexto
- **Material local**: las guías de instalación y tus propios apuntes (`apuntes/`, `mis_apuntes/`, `practicas/`, `aportes/`).
- **📚 Mapa de Estudio del docente (RAG local)**: si tu docente te comparte un archivo `mapa_estudio_devops.html` (export curado de su base de conocimiento, sin exámenes ni guiones privados), colocalo en la carpeta `mapa_estudio/` y presioná **"Importar / Reindexar"**. Queda indexado en una base local con búsqueda de texto completo (FTS5) — podés buscar por tema y elegir qué fragmento cargar como material, todo offline.
- **🌐 Temario en vivo de study-cybercirujas**: elegí una certificación real (CKA, CKAD, AWS, Azure, LPI, NVIDIA AI y más) y un tema puntual del temario oficial — el contenido se trae al vuelo desde `study.cybercirujas.club` (proyecto abierto, no se guarda en tu equipo).

### Modos de pregunta (task harness)
Cuatro botones listos según lo que necesites: **📖 Explicámelo distinto**, **🧪 Dame un ejercicio**, **❓ Tomame una posta** (estilo examen de certificación) y **🎓 ¿Qué preguntaría el profe?** — cada uno arma un prompt especializado; vos podés editarlo antes de enviarlo.

**Todas las respuestas son generadas por IA y no están verificadas por el docente** — usalas como apoyo de estudio, no como fuente única.

---

## 🤝 Soporte y Comunidad

Si tienes dudas sobre el entorno o sugerencias de herramientas para incorporar al Hub, abre un issue en el repositorio o compártelo en clase mediante la función de exportación de aportes.


---

## Proyectos & Ejercicios (importar del docente)

Pestana nueva del hub. Sirve para traer a tu workspace los proyectos y ejercicios que publica
el docente, con todo el codigo adentro.

- **Importar por URL:** pegas el enlace de descarga que te pasa el docente
  (`http://IP-del-docente:8080/api/biblioteca/descargar?id=...`) y lo baja e instala solo.
- **Subir ZIP:** si te pasaron el `.zip` a mano, lo subis y listo.
- Cada unidad se guarda en `biblioteca/proyectos/<id>/` o `biblioteca/ejercicios/<id>/` (lo dice
  su ficha), con su `lab/` (el codigo que corres), sus dependencias reutilizadas y, si tiene,
  sus infografias.
- Abajo ves lo importado listado con sus tags, de que depende y si esta probado.

## Exportar comandos de instalacion

En la seccion de herramientas, el boton **Exportar comandos** te baja un archivo `.ps1` (Windows)
o `.sh` (Linux/Mac) con TODOS los comandos de instalacion segun tu sistema operativo, para
correrlos de una o revisarlos.

## Aviso de contenido generado con IA (transparencia)

Parte del material, el codigo y la documentacion de este workspace fueron **generados con
asistencia de inteligencia artificial y orquestados/revisados por una persona** antes de
publicarse. Se informa en cumplimiento del principio de transparencia del **Reglamento (UE)
2024/1689 (Reglamento de Inteligencia Artificial, "AI Act")**, en particular su articulo 50
sobre la divulgacion de contenidos generados o manipulados por sistemas de IA.

El contenido generado por IA puede contener errores: verifica los comandos antes de ejecutarlos.

## Independencia de la plataforma

Este es un proyecto **personal e independiente**. No esta asociado, respaldado ni afiliado a
ninguna institucion educativa. Cualquier referencia a un curso es solo el tema del material.
