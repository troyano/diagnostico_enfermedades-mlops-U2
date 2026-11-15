"""Persistencia de consultas en un archivo JSON (lista), con bloqueo y escritura atómica.

Cada predicción también se exporta como una línea de `predicciones.csv` (texto plano), que es
el archivo que se lee para el reporte de estadísticas.
"""

import csv
import fcntl
import json
import os
import threading
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from diagnostico_api.schemas import Consulta, PrediccionReciente

CAMPOS_EXPORTADOS = ("id", "fecha", "nombre", "estado")


class ConsultaStorage:
    """Guarda y lee consultas en `<directorio>/consultas.json` y exporta `predicciones.csv`."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory
        self._path = directory / "consultas.json"
        self._export_path = directory / "predicciones.csv"
        self._lock = threading.Lock()

    @property
    def path(self) -> Path:
        return self._path

    @property
    def export_path(self) -> Path:
        return self._export_path

    @contextmanager
    def _exclusive(self) -> Iterator[None]:
        self._dir.mkdir(parents=True, exist_ok=True)
        with self._lock, open(self._dir / ".consultas.lock", "w") as lock_file:
            fcntl.flock(lock_file, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock_file, fcntl.LOCK_UN)

    def _read(self) -> list[dict[str, Any]]:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return []
        return data if isinstance(data, list) else []

    def _write(self, items: list[dict[str, Any]]) -> None:
        tmp = self._path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, self._path)

    def add(self, build: Callable[[str], Consulta]) -> Consulta:
        """Asigna el siguiente id (C-0001...), construye la consulta y la guarda."""
        with self._exclusive():
            items = self._read()
            last = max((int(i["id"].split("-")[1]) for i in items), default=0)
            consulta = build(f"C-{last + 1:04d}")
            items.append(consulta.model_dump(mode="json"))
            self._write(items)
            self._exportar(consulta)
            return consulta

    def _exportar(self, consulta: Consulta) -> None:
        """Agrega una línea al archivo de texto del reporte (con encabezado si es nuevo)."""
        nuevo = not self._export_path.exists() or self._export_path.stat().st_size == 0
        fila = consulta.model_dump(mode="json", include=set(CAMPOS_EXPORTADOS))
        with open(self._export_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_EXPORTADOS)
            if nuevo:
                writer.writeheader()
            writer.writerow(fila)

    def predicciones(self) -> list[PrediccionReciente]:
        """Lee el archivo exportado; devuelve las predicciones en orden de llegada."""
        with self._exclusive():
            try:
                with open(self._export_path, newline="", encoding="utf-8") as f:
                    filas = list(csv.DictReader(f))
            except FileNotFoundError:
                return []
        return [PrediccionReciente.model_validate(fila) for fila in filas]

    def list(self, limit: int = 100) -> list[Consulta]:
        """Consultas más recientes primero."""
        with self._exclusive():
            items = self._read()
        return [Consulta.model_validate(i) for i in reversed(items)][:limit]
