# 🚀 Fundamentos de DevOps: Cultura CALMS, Métricas DORA y Control de Versiones con Git

## 1. ¿Qué es DevOps?
DevOps es un conjunto de prácticas, herramientas y una filosofía cultural que automatiza e integra los procesos entre los equipos de desarrollo de software (Dev) y los equipos de operaciones de TI (Ops). Su objetivo principal es acortar el ciclo de vida del desarrollo y proporcionar entregas continuas con alta calidad de software.

### 🌟 El Marco Cultural CALMS
- **C (Culture):** Fomentar la colaboración, empatía, eliminación de silos y responsabilidad compartida.
- **A (Automation):** Automatizar procesos repetitivos (pruebas, integración continua, aprovisionamiento de infraestructura).
- **L (Lean):** Reducir desperdicios, trabajar en lotes pequeños (small batches) y optimizar el flujo de valor.
- **M (Measurement):** Medir todo mediante telemetría, observabilidad y métricas de negocio y entrega.
- **S (Sharing):** Compartir conocimientos, lecciones aprendidas ante incidentes (post-mortems sin culpa) y mejores prácticas.

### 📊 Las 4 Métricas Clave DORA (DevOps Research and Assessment)
1. **Deployment Frequency (DF):** Frecuencia con la que la organización despliega código a producción con éxito.
2. **Lead Time for Changes (LTTC):** Tiempo que transcurre desde que se realiza un commit hasta que ese cambio está operativo en producción.
3. **Change Failure Rate (CFR):** Porcentaje de despliegues a producción que derivan en fallas inmediatas o requieren remediación (rollback / hotfix).
4. **Mean Time to Recovery (MTTR):** Tiempo medio necesario para restablecer el servicio cuando ocurre un incidente en producción.

---

## 2. Flujo Esencial con Git y GitHub CLI (`gh`)

```bash
# Inicializar repositorio local
git init

# Comprobar estado de archivos
git status

# Añadir cambios al área de preparación (staging)
git add .

# Confirmar cambios con mensaje descriptivo (Conventional Commits)
git commit -m "feat: configuracion inicial del proyecto"

# Ver historial de cambios lineal y conciso
git log --oneline --graph --decorate

# Autenticar GitHub CLI de forma segura con el navegador
gh auth login

# Comprobar estado de autenticación en GitHub
gh auth status
```
