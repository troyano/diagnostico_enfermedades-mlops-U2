"""Reporte de estadísticas descargable en Excel (.xlsx), con tablas de Excel reales."""

from datetime import UTC, datetime
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.worksheet import Worksheet

from diagnostico_ui.estados import ESTADOS

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
FORMATO_FECHA = "yyyy-mm-dd hh:mm"
ESTILO_TABLA = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)


def nombre_archivo(generado: datetime) -> str:
    return f"reporte_estadisticas_{generado:%Y%m%d_%H%M}.xlsx"


def _fecha(valor: Any) -> datetime | None:
    """ISO 8601 a fecha UTC sin zona (Excel no guarda zonas horarias)."""
    try:
        fecha = datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None
    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(UTC)
    return fecha.replace(tzinfo=None, microsecond=0)


def _tabla(hoja: Worksheet, nombre: str, encabezado: list[str], filas: list[list[Any]]) -> None:
    """Escribe encabezado y filas dejando una fila libre y las convierte en una tabla de Excel."""
    inicio = hoja.max_row + 2
    for i, fila in enumerate([encabezado, *filas]):
        for j, valor in enumerate(fila, start=1):
            hoja.cell(row=inicio + i, column=j, value=valor)
    fin = inicio + len(filas)
    ultima_col = chr(ord("A") + len(encabezado) - 1)
    tabla = Table(displayName=nombre, ref=f"A{inicio}:{ultima_col}{fin}")
    tabla.tableStyleInfo = ESTILO_TABLA
    hoja.add_table(tabla)


def reporte_excel(datos: dict[str, Any], generado: datetime | None = None) -> bytes:
    """Arma el libro con dos hojas: "Resumen" (conteo por categoría) y "Ultimas 5"."""
    generado = generado or datetime.now(UTC)
    conteos = datos.get("por_categoria") or {}
    ultima = _fecha(datos.get("fecha_ultima_prediccion"))
    libro = Workbook()

    resumen = libro.active
    assert resumen is not None
    resumen.title = "Resumen"
    resumen.append(["Reporte de estadísticas de predicciones"])
    resumen["A1"].font = Font(bold=True, size=14)
    resumen.append(["Generado (UTC)", generado.astimezone(UTC).replace(tzinfo=None, microsecond=0)])
    resumen.append(["Total de predicciones", datos.get("total_predicciones", 0)])
    resumen.append(["Última predicción (UTC)", ultima if ultima else "Sin predicciones todavía"])
    for celda in ("B2", "B4"):
        resumen[celda].number_format = FORMATO_FECHA
    _tabla(
        resumen,
        "PrediccionesPorCategoria",
        ["Categoría", "Predicciones"],
        [[nombre, int(conteos.get(nombre, 0))] for nombre in ESTADOS],
    )
    resumen.column_dimensions["A"].width = 30
    resumen.column_dimensions["B"].width = 22

    ultimas = libro.create_sheet("Ultimas 5")
    ultimas.append(["Últimas 5 predicciones (la más reciente primero)"])
    ultimas["A1"].font = Font(bold=True, size=14)
    recientes = datos.get("ultimas_predicciones") or []
    if recientes:
        filas = [
            [p.get("id"), _fecha(p.get("fecha")), p.get("nombre"), p.get("estado")]
            for p in recientes
        ]
        _tabla(
            ultimas, "UltimasPredicciones", ["Consulta", "Fecha (UTC)", "Paciente", "Estado"], filas
        )
        for (celda,) in ultimas.iter_rows(min_row=4, min_col=2, max_col=2):
            celda.number_format = FORMATO_FECHA
    else:
        ultimas["A3"] = "Aún no hay predicciones."
    for col, ancho in zip("ABCD", (12, 20, 32, 24), strict=True):
        ultimas.column_dimensions[col].width = ancho

    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()
