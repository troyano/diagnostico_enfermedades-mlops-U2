# diagnostico_enfermedades-mlops-U2

Servicio de apoyo al médico que, a partir de los síntomas de un paciente, devuelve un estado de
salud simulado: **NO ENFERMO**, **ENFERMEDAD LEVE**, **ENFERMEDAD AGUDA**, **ENFERMEDAD CRÓNICA** o
**ENFERMEDAD TERMINAL**. No hay un modelo entrenado: una función con reglas simula las predicciones.

Proyecto de la Unidad 2 de MLOps (Maestría en Inteligencia Artificial Aplicada, ICESI, 2026-II).

## El problema

En medicina existe mucha información de los pacientes, pero para las enfermedades poco comunes,
llamadas huérfanas, los datos escasean. Se requiere un modelo que, dados los síntomas de un
paciente, prediga si es posible que sufra alguna enfermedad, tanto común (muchos datos) como
huérfana (pocos datos).

## Propósito

Pasar de la solución local del médico (Unidad 1: pipeline de MLOps e imagen de Docker) a un
proyecto controlado en GitHub:

1. **Control de versiones:** ramas, commits y Pull Requests para incorporar cada cambio.
2. **Nuevos requerimientos:** la categoría **ENFERMEDAD TERMINAL** (5 estados en total) y un reporte
   de estadísticas de las predicciones.
3. **CI/CD con GitHub Actions:** pruebas automáticas en cada Pull Request y, al integrar en `main`,
   nuevas pruebas y publicación de la imagen Docker en GitHub Packages.

La solución de partida es la entrega de la Unidad 1, en
[troyano/mlops-enfermedades](https://github.com/troyano/mlops-enfermedades). Su pipeline de MLOps
(`docs/brief.md`) se quedó en ese repositorio y no forma parte de este.

## Dónde está cada parte

| Parte | Dónde está |
|---|---|
| Función simulada con los 5 estados | [`api/src/diagnostico_api/model.py`](api/src/diagnostico_api/model.py), función `predecir()` |
| Dockerfiles | [`api/Dockerfile`](api/Dockerfile) (API) y [`app/Dockerfile`](app/Dockerfile) (interfaz) |
| Forma de recibir los datos del médico | Página web en Streamlit (puerto 8501) y punto final `POST /predecir` en FastAPI (puerto 8000) |
| Pruebas | `api/tests/` y `app/tests/` |
| Diseño de la interfaz | [`docs/interfaz.md`](docs/interfaz.md) |

## Estructura

| Ruta | Contenido |
|---|---|
| `api/` | Microservicio FastAPI (`diagnostico_api`), puerto 8000 |
| `app/` | Interfaz web Streamlit (`diagnostico_ui`), puerto 8501 |
| `docs/` | Diseño de la interfaz (`interfaz.md`, con prototipo) |
| `CONTRIBUTING.md` | Flujo de ramas y commits |
| `docker-compose.yml`, `Makefile`, `.env.example` | Entorno reproducible y atajos |

## Requisitos

Docker con Compose. Para desarrollo sin contenedores: [uv](https://docs.astral.sh/uv/).

En Windows, Docker Desktop necesita WSL 2. Si al abrirlo aparece "WSL not installed", ejecuta
`wsl --install --no-distribution` en PowerShell como administrador, reinicia el equipo y abre Docker
Desktop hasta que diga **Engine running**.

Los comandos de varias líneas de este README usan la sintaxis de bash (`\` para partir líneas y
comillas simples). En Windows, ejecútalos en Git Bash o WSL. Para probar la API sin `curl`, usa
Swagger en http://localhost:8000/docs.

## Ejecución con Docker Compose (recomendada)

```bash
docker compose up --build -d
```

- Interfaz para el médico: http://localhost:8501
- API y documentación Swagger: http://localhost:8000/docs
- Verificar la API: `curl http://localhost:8000/health`
- Detener: `docker compose down`

## Cada servicio por separado

### API

```bash
docker build -t diagnostico-api ./api
docker run --rm -p 8000:8000 -v consultas:/data diagnostico-api
```

### Interfaz

La interfaz necesita alcanzar la API. Con la API ya publicada en el puerto 8000 del equipo anfitrión:

```bash
docker build -t diagnostico-ui ./app
docker run --rm -p 8501:8501 -e API_URL=http://host.docker.internal:8000 \
  --add-host=host.docker.internal:host-gateway diagnostico-ui
```

## Cómo obtener una respuesta

### Desde el navegador

Abre http://localhost:8501, escribe el nombre del paciente, la temperatura y agrega los síntomas
(descripción, intensidad de 0 a 10 y días). También puedes usar Swagger en http://localhost:8000/docs.

### Con `curl`

`POST /predecir` recibe `nombre`, `temperatura` (35,0 a 42,0 °C) y una lista de `sintomas`
(`descripcion` de 2 a 80 caracteres, `intensidad` entera de 0 a 10, `duracion_dias` entera de 0 a 3650;
máximo 20 síntomas).

```bash
# NO ENFERMO
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Laura Martínez Gil","temperatura":36.5,"sintomas":[]}'

# ENFERMEDAD LEVE
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Carlos Pérez Ríos","temperatura":37.0,"sintomas":[
        {"descripcion":"Congestión nasal","intensidad":2,"duracion_dias":2},
        {"descripcion":"Estornudos","intensidad":1,"duracion_dias":2}]}'

# ENFERMEDAD AGUDA
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Marta Ospina Cruz","temperatura":39.0,"sintomas":[
        {"descripcion":"Dolor de cabeza","intensidad":8,"duracion_dias":3},
        {"descripcion":"Fiebre alta","intensidad":7,"duracion_dias":3}]}'

# ENFERMEDAD CRÓNICA
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Jorge Salazar Mena","temperatura":36.8,"sintomas":[
        {"descripcion":"Dolor articular","intensidad":3,"duracion_dias":45}]}'

# ENFERMEDAD TERMINAL
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Rosa Delgado Peña","temperatura":37.2,"sintomas":[
        {"descripcion":"Dolor óseo","intensidad":9,"duracion_dias":120},
        {"descripcion":"Pérdida de peso","intensidad":6,"duracion_dias":150}]}'
```

La respuesta incluye `id`, `fecha`, `estado`, `regla` (la regla aplicada), `resumen`,
`version_modelo` y un `aviso` didáctico.

La función `predecir()` usa la temperatura y, de la lista de síntomas, la cantidad, la intensidad
máxima, la duración máxima en días y si algún síntoma es a la vez muy intenso y prolongado. Reglas,
evaluadas en orden (la primera que se cumple):

1. **NO ENFERMO:** sin síntomas y temperatura menor a 37,5 °C.
2. **ENFERMEDAD TERMINAL:** un mismo síntoma tiene intensidad de 9 o más y dura 90 días o más.
3. **ENFERMEDAD CRÓNICA:** hay síntomas y alguno dura 30 días o más.
4. **ENFERMEDAD AGUDA:** hay síntomas y (intensidad máxima de 7 o más, o temperatura de 38,5 °C o más).
5. **ENFERMEDAD LEVE:** cualquier otro caso.

TERMINAL va antes que CRÓNICA porque es la más grave y, de lo contrario, CRÓNICA la atraparía
(todo síntoma de 90 días o más también supera los 30). Exigir que la intensidad y la duración sean
del **mismo** síntoma evita que un síntoma leve y prolongado, sumado a otro intenso y breve, se
clasifique como terminal: en ese caso el resultado es CRÓNICA. La versión de las reglas es
`simulado-0.2.0`.

| Temperatura | Síntomas (intensidad, días) | Estado |
|---|---|---|
| 37,0 | (9, 90) | ENFERMEDAD TERMINAL |
| 39,5 | (10, 365), (3, 2) | ENFERMEDAD TERMINAL |
| 37,0 | (9, 89) | ENFERMEDAD CRÓNICA |
| 37,0 | (8, 120) | ENFERMEDAD CRÓNICA |
| 37,0 | (9, 5), (2, 120) | ENFERMEDAD CRÓNICA |

Si los datos no son válidos, la API responde `422` con mensajes en español:

```bash
curl -s -X POST localhost:8000/predecir -H 'Content-Type: application/json' \
  -d '{"nombre":"Ana","temperatura":50,"sintomas":[]}'
# {"detail":[{"loc":["body","nombre"],"msg":"El nombre debe tener entre 5 y 120 caracteres.", ...},
#            {"loc":["body","temperatura"],"msg":"«temperatura» debe ser menor o igual a 42.0.", ...}]}
```

### Historial y persistencia

Cada consulta se guarda en `/data/consultas.json` dentro del contenedor de la API, y
`GET /consultas?limite=100` las devuelve, las más recientes primero.

La persistencia **requiere un volumen**: sin él, los datos se pierden al eliminar el contenedor.
Con Compose el volumen `consultas` ya está configurado. Con `docker run`:

```bash
docker run --rm -p 8000:8000 -v consultas:/data diagnostico-api
```

El historial contiene nombres de pacientes: usa solo datos ficticios en la demostración.

## Desarrollo

```bash
make lint        # ruff
make typecheck   # mypy estricto
make test        # pytest
```

## Variables de entorno

Ver `.env.example`.

## Flujo de trabajo

- `main` es la única rama permanente y está protegida: los cambios entran solo por Pull Request.
- Cada cambio se desarrolla en su propia rama de trabajo y se integra con un Pull Request a `main`.
  No se usan ramas `dev` ni `stage`.
- Los nombres de las ramas van **sin tildes ni ñ**, en minúsculas y con guiones (convención ASCII):
  por ejemplo `solucion-inicial`, `enfermedad-terminal` y `anadir-github-actions`, aunque el
  enunciado las escriba `solución-inicial` y `añadir-github-actions`. Así se evitan problemas de
  codificación en la terminal, en las URL y en las herramientas de CI.
- Los commits siguen [Conventional Commits](https://www.conventionalcommits.org/es/) en español.

Detalle en [CONTRIBUTING.md](CONTRIBUTING.md).

## Autores

Eduar Troyano Velasquez y Alexander Amador. Maestría en Inteligencia Artificial Aplicada, ICESI. Materia: Machine Learning Operations, MLOps, 2026-II.
