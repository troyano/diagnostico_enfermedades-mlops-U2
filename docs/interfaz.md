# Diseño de la interfaz

Boceto y decisiones de la interfaz para el médico (servicio `app/`, Streamlit). Prototipo interactivo navegable: [`mockup/interfaz.html`](mockup/interfaz.html) (abrir en el navegador; es solo un prototipo, no es la aplicación).

## Boceto

```
┌────────────────────────────────────────────────────────────────┐
│ ████ Apoyo a la decisión médica ████ │ ░░ Uso didáctico ░░░░░░ │
│ ████ MLOps · Unidad 2            ████ │ ░░ (aviso de reglas) ░░ │
├────────────────────────────────────────────────────────────────┤
│ [ 🩺 Consultas            ][ 📊 Estadísticas                 ] │  ← menú
├────────────────────────────────────────────────────────────────┤

Opción "Consultas"
┌───────────────────────────────────────┬────────────────────────┐
│ Nueva consulta                        │ Resultado              │
│ Nombre completo [________________]    │ ┌────────────────────┐ │
│ Temperatura (°C) [39,0]               │ │ ENFERMEDAD AGUDA   │ │
│ Síntomas (máx. 20)                    │ │ regla aplicada     │ │
│ ┌ Descripción │ Intensidad │ Días ┐   │ └────────────────────┘ │
│ Ejemplos: [No enfermo][Leve][Aguda]   │ Síntomas · Intensidad  │
│           [Crónica][Terminal]         │ Días · Temperatura     │
│ [Consultar]  [Limpiar formulario]     │                        │
├───────────────────────────────────────┴────────────────────────┤
│ Historial de consultas (más recientes primero)                 │
│ Fecha │ Paciente │ Estado │ Síntomas │ Temp. │ Regla aplicada   │
└────────────────────────────────────────────────────────────────┘

Opción "Estadísticas"
┌────────────────────────────────────────────────────────────────┐
│ Estadísticas                                                   │
│ [No enfermo 1][Leve 1][Aguda 2][Crónica 1][Terminal 1]         │
│ Total de predicciones: 6 · Última predicción: fecha (UTC)      │
│ Consulta │ Fecha │ Paciente │ Estado      (últimas 5)          │
│ [Descargar reporte en Excel]                                   │
├────────────────────────────────────────────────────────────────┤
│ Pie: institución, programa, materia e integrantes              │
└────────────────────────────────────────────────────────────────┘
```

## Decisiones

- **Entradas:** nombre completo, temperatura y una tabla de síntomas con descripción, intensidad (0 a 10) y días. Hasta 20 síntomas.
- **Valores derivados para la función:** cantidad de síntomas (filas), intensidad máxima y días máximos.
- **Validación:** el servicio valida con Pydantic y devuelve mensajes claros. La interfaz aplica los mismos límites antes de enviar y muestra los errores de la API.
- **Resultado:** estado con color propio, regla aplicada, versión del modelo y aviso didáctico.
- **Menú:** dos opciones, Consultas y Estadísticas, en un control segmentado a todo el ancho. Al cambiar de opción se conservan el nombre, la temperatura y los síntomas que se habían escrito.
- **Estadísticas:** cinco tarjetas con el total por categoría (con el color de cada estado), el total y la fecha de la última predicción, y una tabla con las últimas 5. Los datos vienen de `GET /estadisticas`, que lee el archivo de texto `predicciones.csv` exportado por la API. En pantallas angostas las tarjetas pasan a dos columnas. El botón **Descargar reporte en Excel** genera un `.xlsx` con las hojas `Resumen` y `Ultimas 5`, cada una con una tabla de Excel.
- **Historial:** cada consulta se guarda en un archivo JSON dentro de un volumen del contenedor de la API; la interfaz lo muestra en una tabla.
- **Estilos:** una sola hoja de estilos (`styles.css`) cargada desde un único punto, más el tema base de Streamlit en `.streamlit/config.toml`.
- **Paleta:** azul índigo `#5657EC`, lima `#E3EA55`, negro y blanco, con verde `#4DB87B`, naranja `#EB6B3F`, violeta `#8A5CF0` y rojo `#C8344D` para los estados. Tipografías Sora (títulos) y Figtree (texto).
- **Ejemplos:** cinco botones, uno por estado, en dos filas (3 y 2) para que las etiquetas no se corten en pantallas angostas.
- **Pie de página:** institución, facultad, programa, materia e integrantes del grupo.

## Colores por estado

| Estado | Color |
|---|---|
| NO ENFERMO | Verde |
| ENFERMEDAD LEVE | Lima |
| ENFERMEDAD AGUDA | Naranja |
| ENFERMEDAD CRÓNICA | Violeta |
| ENFERMEDAD TERMINAL | Rojo `#C8344D` (texto blanco, contraste 5,2:1) |

## Nota sobre datos personales

El nombre del paciente se almacena en el historial. En la demostración se usan solo nombres ficticios; un uso real requeriría consentimiento y cumplimiento de la Ley 1581 de 2012.
