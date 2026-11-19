"""Descarga la temperatura y la precipitación horarias de Buenos Aires (Open-Meteo, ERA5) para 2021-2025.

Se baja desde diciembre de 2021 para tener la hora anterior al primer día. Guarda
datos/procesados/clima_horario.csv con la hora local de inicio de cada intervalo.

Alineación: en Open-Meteo la precipitación etiquetada a las 11:00 es la acumulada entre 10:00 y 11:00,
y la temperatura etiquetada a las 10:00 es la instantánea a esa hora. Para el intervalo [10:00, 11:00)
se usa la temperatura de las 10:00 y la precipitación etiquetada a las 11:00.
"""
import json
from datetime import datetime, timezone

import pandas as pd
import requests

if __package__:
    from .config import DATOS_PROCESADOS, LATITUD, LONGITUD, URL_CLIMA, ZONA_HORARIA
else:
    from config import DATOS_PROCESADOS, LATITUD, LONGITUD, URL_CLIMA, ZONA_HORARIA


def main():
    parametros = {
        "latitude": LATITUD,
        "longitude": LONGITUD,
        "start_date": "2021-12-25",
        "end_date": "2026-01-01",
        "hourly": "temperature_2m,precipitation",
        "timezone": ZONA_HORARIA,
        "models": "era5",
    }
    r = requests.get(URL_CLIMA, params=parametros, timeout=120)
    r.raise_for_status()
    datos = r.json()
    h = datos["hourly"]
    if datos.get("hourly_units", {}).get("precipitation") != "mm":
        raise ValueError("La precipitación no viene en mm")
    df = pd.DataFrame({"hora_etiqueta": pd.to_datetime(h["time"]),
                       "temperatura": h["temperature_2m"],
                       "precipitacion_etiqueta": h["precipitation"]})
    df = df.set_index("hora_etiqueta").sort_index()
    if not df.index.is_unique:
        raise ValueError("La API devolvió horas repetidas")
    esperada = pd.date_range(parametros["start_date"], pd.Timestamp(parametros["end_date"]) + pd.Timedelta(hours=23),
                             freq="h")
    if not df.index.equals(esperada):
        raise ValueError("La rejilla horaria del clima no cubre exactamente el rango pedido")
    if df[["temperatura", "precipitacion_etiqueta"]].isna().any().any():
        raise ValueError("Hay horas sin temperatura o sin precipitación")
    salida = pd.DataFrame(index=df.index)
    salida["temperatura"] = df["temperatura"]
    # Precipitación del intervalo [t, t+1) = valor etiquetado en t+1 (la API suma la hora anterior a la etiqueta).
    # Se desplaza por marca de tiempo, no por posición de fila.
    salida["precipitacion"] = df["precipitacion_etiqueta"].shift(-1, freq="h").reindex(salida.index)
    salida.index.name = "hora"
    salida = salida.loc["2021-12-25":"2025-12-31 23:00"]
    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    salida.to_csv(DATOS_PROCESADOS / "clima_horario.csv")
    meta = {
        "fuente": "Open-Meteo Historical Weather API (producto ERA5), datos CC BY 4.0",
        "consulta": URL_CLIMA + "?" + "&".join(f"{k}={v}" for k, v in parametros.items()),
        "latitud_celda": datos.get("latitude"),
        "longitud_celda": datos.get("longitude"),
        "elevacion": datos.get("elevation"),
        "fecha_extraccion_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "filas": int(len(salida)),
        "faltantes_temperatura": int(salida["temperatura"].isna().sum()),
        "faltantes_precipitacion": int(salida["precipitacion"].isna().sum()),
    }
    (DATOS_PROCESADOS / "clima_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                                                      encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
