import pytest

from diagnostico_api.model import predecir
from diagnostico_api.schemas import EstadoSalud, Sintoma


def s(intensidad: int, dias: int, desc: str = "Síntoma") -> Sintoma:
    return Sintoma(descripcion=desc, intensidad=intensidad, duracion_dias=dias)


CASOS = [
    (36.5, [], EstadoSalud.NO_ENFERMO),
    (37.0, [s(2, 2), s(1, 2)], EstadoSalud.LEVE),
    (39.0, [s(8, 3), s(7, 3), s(6, 2), s(5, 2)], EstadoSalud.AGUDA),
    (36.8, [s(3, 45)], EstadoSalud.CRONICA),
    (37.0, [s(9, 15)], EstadoSalud.AGUDA),
    (38.0, [], EstadoSalud.LEVE),
    (38.5, [s(1, 1)], EstadoSalud.AGUDA),
    (37.0, [s(9, 30)], EstadoSalud.CRONICA),
    (37.5, [], EstadoSalud.LEVE),
    (37.0, [s(6, 29)], EstadoSalud.LEVE),
    # ENFERMEDAD TERMINAL: un mismo síntoma con intensidad >= 9 y >= 90 días
    (37.0, [s(9, 90)], EstadoSalud.TERMINAL),
    (39.5, [s(10, 365), s(3, 2)], EstadoSalud.TERMINAL),
    (37.0, [s(9, 89)], EstadoSalud.CRONICA),
    (37.0, [s(8, 120)], EstadoSalud.CRONICA),
    (37.0, [s(9, 5), s(2, 120)], EstadoSalud.CRONICA),
]


@pytest.mark.parametrize(("temp", "sintomas", "esperado"), CASOS)
def test_estados(temp: float, sintomas: list[Sintoma], esperado: EstadoSalud) -> None:
    assert predecir(temp, sintomas).estado == esperado


def test_resumen_y_regla() -> None:
    r = predecir(39.0, [s(8, 3), s(4, 10)])
    assert (r.resumen.cantidad_sintomas, r.resumen.intensidad_maxima) == (2, 8)
    assert r.resumen.duracion_maxima_dias == 10
    assert "Intensidad" in r.regla


def test_regla_sin_sintomas_con_fiebre() -> None:
    assert predecir(38.0, []).regla == "Temperatura elevada sin síntomas reportados"


def test_regla_terminal() -> None:
    r = predecir(37.2, [s(9, 120), s(6, 150)])
    assert r.estado == EstadoSalud.TERMINAL
    assert r.regla == "Un síntoma de intensidad 9 o más con 90 días o más de duración"


def test_las_cinco_categorias_se_alcanzan() -> None:
    assert {predecir(t, sx).estado for t, sx, _ in CASOS} == set(EstadoSalud)
