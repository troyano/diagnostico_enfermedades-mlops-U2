"""Reporte de estadísticas: archivo de texto exportado y punto final GET /estadisticas."""

import csv
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from diagnostico_api.config import Settings
from diagnostico_api.estadisticas import calcular_estadisticas
from diagnostico_api.main import create_app
from diagnostico_api.schemas import EstadoSalud, PrediccionReciente

CATEGORIAS = [e.value for e in EstadoSalud]


def sint(i: int, d: int) -> dict[str, Any]:
    return {"descripcion": "Síntoma", "intensidad": i, "duracion_dias": d}


def cuerpo(temperatura: float, sintomas: list[dict[str, Any]], nombre: str) -> dict[str, Any]:
    return {"nombre": nombre, "temperatura": temperatura, "sintomas": sintomas}


NO_ENFERMO = cuerpo(36.5, [], "Laura Martínez Gil")
LEVE = cuerpo(37.0, [sint(2, 2)], "Carlos Pérez Ríos")
AGUDA = cuerpo(39.0, [sint(8, 3)], "Marta Ospina Cruz")
CRONICA = cuerpo(36.8, [sint(3, 45)], "Jorge Salazar Mena")
TERMINAL = cuerpo(37.2, [sint(9, 120)], "Rosa Delgado Peña")


def test_estadisticas_vacias_antes_de_predecir(client: TestClient) -> None:
    r = client.get("/estadisticas")
    assert r.status_code == 200
    assert r.json() == {
        "total_predicciones": 0,
        "por_categoria": dict.fromkeys(CATEGORIAS, 0),
        "ultimas_predicciones": [],
        "fecha_ultima_prediccion": None,
    }


def test_ultima_prediccion_reflejada_en_estadisticas(client: TestClient) -> None:
    client.post("/predecir", json=LEVE)
    consulta = client.post("/predecir", json=TERMINAL).json()
    data = client.get("/estadisticas").json()
    ultima = data["ultimas_predicciones"][0]
    assert ultima == {
        "id": consulta["id"],
        "fecha": consulta["fecha"],
        "nombre": "Rosa Delgado Peña",
        "estado": "ENFERMEDAD TERMINAL",
    }
    assert data["fecha_ultima_prediccion"] == consulta["fecha"]


def test_conteo_por_categoria_y_solo_las_ultimas_cinco(client: TestClient) -> None:
    for c in (NO_ENFERMO, LEVE, AGUDA, AGUDA, CRONICA, TERMINAL, LEVE):
        assert client.post("/predecir", json=c).status_code == 200
    data = client.get("/estadisticas").json()
    assert data["total_predicciones"] == 7
    assert data["por_categoria"] == {
        "NO ENFERMO": 1,
        "ENFERMEDAD LEVE": 2,
        "ENFERMEDAD AGUDA": 2,
        "ENFERMEDAD CRÓNICA": 1,
        "ENFERMEDAD TERMINAL": 1,
    }
    ids = [p["id"] for p in data["ultimas_predicciones"]]
    assert ids == ["C-0007", "C-0006", "C-0005", "C-0004", "C-0003"]


def test_exporta_una_linea_de_texto_por_prediccion(client: TestClient, tmp_path: Path) -> None:
    client.post("/predecir", json=AGUDA)
    client.post("/predecir", json=TERMINAL)
    archivo = tmp_path / "predicciones.csv"
    lineas = archivo.read_text(encoding="utf-8").splitlines()
    assert lineas[0] == "id,fecha,nombre,estado"
    assert len(lineas) == 3
    with open(archivo, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    assert [f["estado"] for f in filas] == ["ENFERMEDAD AGUDA", "ENFERMEDAD TERMINAL"]


def test_estadisticas_sobreviven_a_otra_app(tmp_path: Path) -> None:
    TestClient(create_app(Settings(data_dir=tmp_path))).post("/predecir", json=CRONICA)
    data = TestClient(create_app(Settings(data_dir=tmp_path))).get("/estadisticas").json()
    assert data["total_predicciones"] == 1
    assert data["por_categoria"]["ENFERMEDAD CRÓNICA"] == 1


def test_calcular_estadisticas_orden_y_fecha() -> None:
    inicio = datetime(2026, 11, 14, 12, 0, tzinfo=UTC)
    estados = list(EstadoSalud) + [EstadoSalud.LEVE]
    predicciones = [
        PrediccionReciente(
            id=f"C-{i:04d}", fecha=inicio + timedelta(minutes=i), nombre="Ana Gómez", estado=e
        )
        for i, e in enumerate(estados, start=1)
    ]
    reporte = calcular_estadisticas(predicciones)
    assert reporte.total_predicciones == 6
    assert reporte.por_categoria[EstadoSalud.LEVE] == 2
    assert [p.id for p in reporte.ultimas_predicciones] == [
        "C-0006", "C-0005", "C-0004", "C-0003", "C-0002",
    ]  # fmt: skip
    assert reporte.fecha_ultima_prediccion == inicio + timedelta(minutes=6)
