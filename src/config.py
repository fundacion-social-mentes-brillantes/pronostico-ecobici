"""Configuración común del proyecto: rutas, fechas, escenarios y fuentes de datos."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS_CRUDOS = RAIZ / "datos" / "crudos"
DATOS_PROCESADOS = RAIZ / "datos" / "procesados"
RESULTADOS = RAIZ / "resultados"
FIGURAS = RESULTADOS / "figuras"

ZONA_HORARIA = "America/Argentina/Buenos_Aires"
ANIOS = [2022, 2023, 2024, 2025]

# Recorridos de Ecobici (Buenos Aires Data, licencia CC BY 2.5 AR).
URL_RECORRIDOS = (
    "https://cdn.buenosaires.gob.ar/datosabiertos/datasets/transporte-y-obras-publicas/"
    "bicicletas-publicas/recorridos-realizados-{anio}.zip"
)

# Clima: Open-Meteo, API de clima histórico, producto ERA5 (datos CC BY 4.0).
# Celda fija en el centro de Buenos Aires (Obelisco).
LATITUD, LONGITUD = -34.6037, -58.3816
URL_CLIMA = "https://archive-api.open-meteo.com/v1/archive"

# Particiones (fechas locales, inclusivas).
ENTRENAMIENTO = ("2022-01-01", "2024-12-31")
VALIDACION = ("2025-01-01", "2025-06-30")
PRUEBA = ("2025-07-01", "2025-12-31")
MARGEN_DIAS = 7  # margen entre el último dato usado para ajustar y la primera predicción evaluada

# Escenarios de antigüedad del último conteo disponible (horas).
RETRASOS = [1, 24, 168]

SEMILLA = 2026
