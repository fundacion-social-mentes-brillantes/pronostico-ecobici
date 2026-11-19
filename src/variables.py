"""Construcción de variables sobre una rejilla de horas locales."""
import pandas as pd

if __package__:
    from . import config
else:
    import config


CONTEOS = ["ultimo_conteo", "media_24", "semana_anterior"]
TIPOS_DIA = ["laborable", "sabado", "domingo_o_feriado"]
CLIMA = ["temperatura", "precipitacion"]


def preparar_serie(serie, feriados, clima=None):
    """Conserva el instante en el índice y usa `hora` para la hora del día."""
    # El índice (instante) y la columna `hora` (hora del día, 0-23) deben tener nombres distintos:
    # si ambos se llamaran «hora», pandas no sabría por cuál agrupar.
    df = serie.set_index(pd.to_datetime(serie["hora"]).rename("instante")).drop(columns="hora").sort_index()
    df = df.asfreq("h")
    df.loc[df["cobertura_dudosa"].eq(True), "viajes"] = float("nan")
    indice = df.index
    df["hora"] = indice.hour
    df["dia_semana"] = indice.day_of_week
    df["mes"] = indice.month
    fechas = pd.to_datetime(feriados["fecha"])
    for tipo in ("feriado", "no_laborable"):
        df[tipo] = indice.normalize().isin(fechas[feriados["tipo"].eq(tipo)]).astype(int)

    df["tipo_dia"] = "laborable"
    df.loc[df["dia_semana"].eq(5), "tipo_dia"] = "sabado"
    df.loc[df["dia_semana"].eq(6), "tipo_dia"] = "domingo_o_feriado"
    df.loc[df["no_laborable"].eq(1), "tipo_dia"] = "laborable"
    df.loc[df["feriado"].eq(1), "tipo_dia"] = "domingo_o_feriado"
    if clima is not None:
        tiempo = clima.set_index(pd.to_datetime(clima["hora"]))
        df = df.join(tiempo[CLIMA], validate="one_to_one")
        if df[CLIMA].isna().any().any():
            raise ValueError("Hay horas de la serie sin clima")
    return df


def cargar_serie():
    """Lee los tres datos procesados del proyecto."""
    carpeta = config.DATOS_PROCESADOS
    return preparar_serie(
        pd.read_csv(carpeta / "serie_horaria.csv"),
        pd.read_csv(carpeta / "feriados.csv"),
        pd.read_csv(carpeta / "clima_horario.csv"),
    )


def variables_escenario(serie, retraso):
    """Usa la rejilla completa para que los desplazamientos sean horas reales."""
    if retraso not in config.RETRASOS:
        raise ValueError(f"Retraso fuera del protocolo: {retraso}")
    df = serie.copy()
    df["ultimo_conteo"] = df["viajes"].shift(retraso)
    df["media_24"] = df["ultimo_conteo"].rolling(24, min_periods=18).mean()
    # Con 168 horas de retraso, este predictor coincide con el último conteo.
    df["semana_anterior"] = df["viajes"].shift(168)
    return df
