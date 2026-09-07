# 📝 Apuntes: Clase 07 - Contenerización con Docker: Docker Engine, Dockerfiles y Multi-Stage Builds

> **Módulo:** M4: Contenedores con Docker  
> **Estado:** En Progreso / Completado  
> **Video Asociado:** `mis_videos/Clase_07.mp4`

---

## 🎯 1. Conceptos Clave Aprendidos

- [ ] Concepto 1: Imágenes vs Contenedores
- [ ] Concepto 2: Capas (Union File System)
- [ ] Concepto 3: Directivas Dockerfile (FROM, RUN, COPY, CMD)

### 💡 Analogía Útil:
> *Imagen como la receta de cocina grabada en piedra; Contenedor como el plato cocinado en ejecución.*

---

## 💻 2. Comandos y Terminal Practicados

```bash
# Comandos esenciales de esta clase:
docker build -t mi-app:v1 .
docker run -d -p 8080:80 --name web mi-app:v1
docker ps
docker logs -f web
docker exec -it web sh
```

---

## ❓ 3. Mis Dudas para el Profesor o Tutor IA

1. *Anota aquí cualquier pregunta que surja durante la clase o la práctica:*
   - 

---

## 🛠️ 4. Mi Laboratorio / Desafío Práctico de la Clase

- **Objetivo:** Reproducir el ejercicio visto en vivo.
- **Resultado:** 

---

## 🔗 5. Enlaces, Repositorios y Recursos Recomendados

- Repositorio oficial de la clase: [GitHub EducacionIT](https://github.com/ferraroluc)
- Documentación de consulta rápida:
