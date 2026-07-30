# Mapa de Dependencias del Motor

## Módulos Python (astronex/)
- `chart.py`: Lógica principal de cálculos de posiciones (natales, tránsitos, revoluciones). Contiene fórmulas matemáticas puras y orquestación.
- `nexdate.py`: Manejo riguroso del tiempo astronómico, día juliano y zonas horarias, integrando `tz_sup.py`.
- `pysw.py`: Wrapper para las llamadas en C a Swiss Ephemeris.
- `zodiac.py`, `directions.py`: Cálculos accesorios basados en las salidas de las efemérides.
- `database.py`: Acceso a la SQLite.

## Extensiones Compiladas
- `_pysw` (`.so` / `.pyd` / `.dylib`): Wrapper nativo de la librería de C de Swiss Ephemeris (`libswe.a` u objeto compartido). Todo el núcleo matemático reside aquí.

## Dependencias Externas
- `pytz`
- `cairo` / `pangocairo` (estrictamente para render, puede excluirse del cálculo matemático puro).
