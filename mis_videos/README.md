# 🎥 Grabaciones de Clases y Videos

Esta carpeta te permite ver tus clases directamente dentro del reproductor web local (`http://localhost:8080/player/index.html`).

### 🚀 ¿Cómo agregar tus videos?

Tienes dos opciones muy sencillas:

#### Opción A: Archivos de Video Locales (.mp4 / .mkv / .webm)
Simplemente copia tus grabaciones a esta carpeta con los siguientes nombres recomendados:
- `Clase_01.mp4`
- `Clase_02.mp4`
- ... hasta `Clase_12.mp4`

El reproductor local detectará automáticamente los videos presentes y te permitirá reproducirlos fluidamente con barra de navegación, pausa y avance.

#### Opción B: Enlaces Externos (Zoom, YouTube, Google Drive o Alumni)
Abre el archivo `clases.json` que está en esta misma carpeta y pega la URL en el campo `"url_stream"`:
```json
{
  "clase": 1,
  "titulo": "Clase 01: Introducción a DevOps y Git",
  "archivo_local": "Clase_01.mp4",
  "url_stream": "https://us02web.zoom.us/rec/share/..."
}
```
