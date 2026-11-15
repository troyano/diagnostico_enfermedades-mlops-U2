# Flujo de ramas y contribución

## Ramas

```
rama de trabajo  ──PR──►  main
```

| Rama | Propósito | Regla |
|---|---|---|
| `main` | Versión entregable. Siempre arranca con Docker | Protegida: exige Pull Request, sin push directo y sin excepción para administradores |
| Rama de trabajo | Un requerimiento o cambio acotado | Se integra con un Pull Request a `main` y se borra al fusionar |

No se usan ramas `dev` ni `stage`.

## Nombres de ramas

En ASCII: sin tildes ni ñ, en minúsculas y con guiones. Por ejemplo `enfermedad-terminal`,
`reporte-estadisticas` o `anadir-github-actions`. El enunciado escribe `solución-inicial` y
`añadir-github-actions`; aquí se usan `solucion-inicial` y `anadir-github-actions` para evitar
problemas de codificación en la terminal, en las URL y en las herramientas de CI.

## Commits

Se usa [Conventional Commits](https://www.conventionalcommits.org/es/) en español: `feat`, `fix`,
`docs`, `refactor`, `test`, `chore`, con un alcance opcional (`feat(api): ...`). Cada requerimiento
va en al menos un commit propio, para que sus cambios se vean por separado.

## Antes de abrir un PR

```bash
make lint typecheck test
docker compose up --build -d   # api en :8000 y app en :8501 deben quedar healthy
docker compose down -v
```

Las pruebas de la API usan `fcntl`, que solo existe en Linux y macOS. En Windows, córrelas en WSL o
dentro de Docker.

## Pull Requests

1. Publicar la rama: `git push -u origin <rama>`.
2. Abrir el PR contra `main`, sin revisores, con un resumen de los cambios.
3. Esperar el pipeline de CI/CD: comenta "CI/CD en acción. Ejecutando tareas …" al empezar y
   "CI/CD terminado con éxito." si pasan las pruebas de los dos servicios (`Pruebas (api)` y
   `Pruebas (app)`). La protección de `main` exige que esas dos verificaciones pasen.
4. Fusionar con **Create a merge commit**. El merge vuelve a correr las pruebas y publica las
   imágenes en GitHub Packages.
