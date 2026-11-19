"""Construye el calendario de feriados y días no laborables nacionales de Argentina, 2022-2025.

Base: librería `holidays` (categoría pública de Argentina), corregida con lo efectivo de cada año:
- Jueves Santo es día no laborable (Ley 27.399), no feriado.
- 2025: el 12 de octubre (domingo) se trasladó al viernes 10 de octubre (Resolución 139/2025).
- 2025: el 2 de mayo, el 15 de agosto y el 21 de noviembre fueron días no laborables con fines turísticos
  (Decreto 1027/2024), no feriados.
Salida: datos/procesados/feriados.csv con columnas fecha, tipo (feriado | no_laborable), nombre.
"""
import holidays
import pandas as pd

if __package__:
    from .config import ANIOS, DATOS_PROCESADOS
else:
    from config import ANIOS, DATOS_PROCESADOS

CORRECCIONES = {
    # fecha: (tipo, nombre) ; tipo None = quitar
    "2025-10-12": (None, None),
    "2025-10-10": ("feriado", "Día del Respeto a la Diversidad Cultural (trasladado, Res. 139/2025)"),
    "2025-05-02": ("no_laborable", "Día no laborable con fines turísticos (Decreto 1027/2024)"),
    "2025-08-15": ("no_laborable", "Día no laborable con fines turísticos (Decreto 1027/2024)"),
    "2025-11-21": ("no_laborable", "Día no laborable con fines turísticos (Decreto 1027/2024)"),
}


def construir():
    filas = {}
    for anio in ANIOS:
        for fecha, nombre in holidays.AR(years=anio, language="es").items():
            tipo = "no_laborable" if "Jueves Santo" in nombre else "feriado"
            filas[str(fecha)] = (tipo, nombre)
    for fecha, (tipo, nombre) in CORRECCIONES.items():
        if tipo is None:
            filas.pop(fecha, None)
        else:
            filas[fecha] = (tipo, nombre)
    df = pd.DataFrame([(f, t, n) for f, (t, n) in sorted(filas.items())], columns=["fecha", "tipo", "nombre"])
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


if __name__ == "__main__":
    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    df = construir()
    df.to_csv(DATOS_PROCESADOS / "feriados.csv", index=False)
    print(df.groupby([df.fecha.dt.year, "tipo"]).size().unstack(fill_value=0))
