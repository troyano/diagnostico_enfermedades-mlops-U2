from datetime import UTC, datetime
from io import BytesIO
from typing import Any

from openpyxl import load_workbook

from diagnostico_ui.estados import ESTADOS
from diagnostico_ui.reporte import nombre_archivo, reporte_excel

GENERADO = datetime(2026, 11, 14, 23, 50, tzinfo=UTC)

DATOS: dict[str, Any] = {
    "total_predicciones": 2,
    "por_categoria": {"ENFERMEDAD AGUDA": 1, "ENFERMEDAD TERMINAL": 1},
    "ultimas_predicciones": [
        {"id": "C-0002", "fecha": "2026-11-14T23:49:07.306106Z",
         "nombre": "Rosa Delgado Peña", "estado": "ENFERMEDAD TERMINAL"},
        {"id": "C-0001", "fecha": "2026-11-14T23:40:00Z",
         "nombre": "Marta Ospina Cruz", "estado": "ENFERMEDAD AGUDA"},
    ],
    "fecha_ultima_prediccion": "2026-11-14T23:49:07.306106Z",
}  # fmt: skip


def test_nombre_de_archivo() -> None:
    assert nombre_archivo(GENERADO) == "reporte_estadisticas_20261114_2350.xlsx"


def test_excel_con_resumen_por_categoria_y_ultimas() -> None:
    libro = load_workbook(BytesIO(reporte_excel(DATOS, GENERADO)))
    assert libro.sheetnames == ["Resumen", "Ultimas 5"]

    resumen = libro["Resumen"]
    assert resumen["B3"].value == 2
    assert resumen["B4"].value == datetime(2026, 11, 14, 23, 49, 7)
    tabla = resumen.tables["PrediccionesPorCategoria"]
    assert tabla.ref == "A6:B11"
    conteos = {fila[0].value: fila[1].value for fila in resumen["A7:B11"]}
    assert conteos == {nombre: 0 for nombre in ESTADOS} | {
        "ENFERMEDAD AGUDA": 1, "ENFERMEDAD TERMINAL": 1,
    }  # fmt: skip

    ultimas = libro["Ultimas 5"]
    assert ultimas.tables["UltimasPredicciones"].ref == "A3:D5"
    assert [c.value for c in ultimas[3]] == ["Consulta", "Fecha (UTC)", "Paciente", "Estado"]
    assert [c.value for c in ultimas[4]][0::2] == ["C-0002", "Rosa Delgado Peña"]
    assert ultimas["B4"].number_format == "yyyy-mm-dd hh:mm"


def test_excel_sin_predicciones() -> None:
    vacio = {
        "total_predicciones": 0,
        "por_categoria": dict.fromkeys(ESTADOS, 0),
        "ultimas_predicciones": [],
        "fecha_ultima_prediccion": None,
    }
    libro = load_workbook(BytesIO(reporte_excel(vacio, GENERADO)))
    assert libro["Resumen"]["B4"].value == "Sin predicciones todavía"
    assert [f[1].value for f in libro["Resumen"]["A7:B11"]] == [0, 0, 0, 0, 0]
    assert not libro["Ultimas 5"].tables
    assert libro["Ultimas 5"]["A3"].value == "Aún no hay predicciones."
