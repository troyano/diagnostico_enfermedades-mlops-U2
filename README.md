# diagnostico_enfermedades-mlops-U2

Servicio de apoyo al médico que, a partir de los síntomas de un paciente, devuelve un estado de salud simulado. Proyecto de la Unidad 2 de MLOps (Maestría en Inteligencia Artificial Aplicada, ICESI, 2026-II).

## El problema

En medicina existe mucha información de los pacientes, pero para las enfermedades poco comunes, llamadas huérfanas, los datos escasean. Se requiere un modelo que, dados los síntomas de un paciente, prediga si es posible que sufra alguna enfermedad, tanto común (muchos datos) como huérfana (pocos datos).

## Propósito

Pasar de la solución local del médico (Unidad 1: pipeline de MLOps e imagen de Docker) a un proyecto controlado en GitHub:

1. **Control de versiones:** ramas, commits y Pull Requests para incorporar los cambios.
2. **Nuevos requerimientos:** la categoría `ENFERMEDAD TERMINAL` (5 estados en total) y un reporte de estadísticas de las predicciones.
3. **CI/CD con GitHub Actions:** pruebas automáticas en cada Pull Request y, al integrar en `main`, nuevas pruebas y publicación de la imagen Docker en GitHub Packages.

No hay un modelo entrenado: una función con reglas simula las predicciones.

## Estructura prevista del repositorio

| Ruta | Contenido |
|---|---|
| `api/` | Microservicio FastAPI con la función de predicción simulada |
| `app/` | Interfaz web en Streamlit |
| `docs/` | Documentación y diseño de la interfaz |
| `docker-compose.yml` | Ejecución conjunta de la API y la interfaz |
| `.github/workflows/` | Pipeline de CI/CD (GitHub Actions) |

## Flujo de trabajo

- `main` es la rama principal y estará protegida: los cambios entran solo mediante Pull Request.
- Cada cambio se desarrolla en su propia rama y se integra con un Pull Request.
- Los commits siguen [Conventional Commits](https://www.conventionalcommits.org/es/).

## Autores

Eduar Troyano Velasquez y Alexander Amador.
