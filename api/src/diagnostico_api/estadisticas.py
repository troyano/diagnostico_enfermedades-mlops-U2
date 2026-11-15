"""Cálculo del reporte de estadísticas a partir de las predicciones exportadas."""

from collections.abc import Sequence

from diagnostico_api.schemas import Estadisticas, EstadoSalud, PrediccionReciente

ULTIMAS = 5


def calcular_estadisticas(
    predicciones: Sequence[PrediccionReciente], ultimas: int = ULTIMAS
) -> Estadisticas:
    """Recibe las predicciones en orden de llegada y arma el reporte.

    Sin predicciones, las 5 categorías aparecen en 0, la lista vacía y la fecha nula.
    """
    por_categoria = {estado: 0 for estado in EstadoSalud}
    for p in predicciones:
        por_categoria[p.estado] += 1
    recientes = list(reversed(predicciones))[:ultimas]
    return Estadisticas(
        total_predicciones=len(predicciones),
        por_categoria=por_categoria,
        ultimas_predicciones=recientes,
        fecha_ultima_prediccion=recientes[0].fecha if recientes else None,
    )
