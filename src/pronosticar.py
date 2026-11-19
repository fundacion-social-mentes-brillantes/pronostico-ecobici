"""Pronóstico de una hora cualquiera con los modelos del estudio, tal como quedaron congelados.

Uso:
    python src/pronosticar.py "2025-12-24 18:00"
    python src/pronosticar.py "2025-12-24 18:00" --retraso 1
    python src/pronosticar.py "2026-01-05 08:00"      (después del último dato publicado)

Dice cuántos viajes se iniciarían en Ecobici en esa hora (por ejemplo, de 18:00 a 18:59, hora de Buenos Aires) con
cada método y con el dato de hace 1 hora, 1 día y 1 semana. Si la hora tiene dato real, lo muestra al lado.

Los modelos se ajustan igual que en el experimento (src/experimento.py): con los datos de 2022 a junio de 2025 y los
hiperparámetros elegidos en validación (resultados/hiperparametros_elegidos.json). Por eso, en las horas de prueba
(desde el 8 de julio de 2025) da los mismos números que resultados/predicciones_prueba.csv, salvo diferencias de
redondeo de la computadora (menos de una billonésima de viaje); una prueba lo comprueba.
Un pronóstico solo es honesto si los modelos no vieron nada posterior a lo que se conocería en su escenario (la hora
menos el retraso); si no, el comando lo avisa. Después del último dato (31 de diciembre de 2025, 23:00) cada escenario
llega hasta donde alcanza su retraso: 1 hora, 1 día o 1 semana más allá. El análisis con clima (boosting_clima) no
está aquí, porque usa el clima observado de la hora que se pronostica, que no se conoce de antemano.
"""
import argparse
import json
import re
import sys

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

if __package__:
    from . import config
    from .experimento import ENTRADAS_CONTEO
    from .modelos import crear_modelo
    from .variables import CONTEOS, preparar_serie, variables_escenario
else:
    import config
    from experimento import ENTRADAS_CONTEO
    from modelos import crear_modelo
    from variables import CONTEOS, preparar_serie, variables_escenario


# Del mejor al peor según el error medio del estudio con el dato de 1 hora.
METODOS = ("boosting", "mlp", "ridge", "ingenuo_semanal", "mediana_calendario")
NOMBRES = {
    "boosting": "Boosting de árboles",
    "mlp": "Perceptrón multicapa",
    "ridge": "Regresión Ridge",
    "ingenuo_semanal": "Ingenuo semanal",
    "mediana_calendario": "Mediana de calendario",
}
# Conteos que necesita cada método para la hora pedida (la mediana solo usa el calendario).
REQUISITOS = {"boosting": CONTEOS, "mlp": CONTEOS, "ridge": CONTEOS, "ingenuo_semanal": ["semana_anterior"],
              "mediana_calendario": []}
FALTANTES = {"ultimo_conteo": "el último conteo", "media_24": "la media de las 24 horas anteriores",
             "semana_anterior": "el conteo de hace una semana"}
EDADES = {1: "1 hora", 24: "1 día", 168: "1 semana"}
DIAS = ("lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")
FIN_AJUSTE = pd.Timestamp(config.VALIDACION[1]) + pd.Timedelta(hours=23)  # última hora con que se ajustan los modelos
FORMATO = re.compile(r"^\s*(\d{4}-\d{2}-\d{2})[ T](\d{1,2})(?::(\d{2}))?\s*$")

_modelos = {}  # (retraso, hiperparámetros, huella de los datos de ajuste) → modelos ya ajustados


def fecha_larga(instante):
    return (f"{DIAS[instante.day_of_week]} {instante.day} de {MESES[instante.month - 1]} de {instante.year}, "
            f"{instante:%H:%M}")


def cantidad(x):
    return f"{round(x):,}".replace(",", ".")


def viajes(x):
    return f"{cantidad(x)} viaje" + ("" if round(x) == 1 else "s")


def leer_hora(texto):
    """«2025-12-24 18:00» (también «2025-12-24 18» o con T) → instante en hora local, sin zona horaria."""
    m = FORMATO.match(texto)
    if not m:
        raise ValueError(f'no entiendo la hora «{texto}»; escríbela con fecha y hora, así: "2025-12-24 18:00" '
                         "(hora de Buenos Aires)")
    return pd.Timestamp(f"{m.group(1)} {int(m.group(2)):02d}:{m.group(3) or '00'}")


def cargar_serie_hasta(instante):
    """Serie del proyecto (sin clima), con horas vacías añadidas al final si la hora pedida es posterior."""
    carpeta = config.DATOS_PROCESADOS
    serie = pd.read_csv(carpeta / "serie_horaria.csv")
    feriados = pd.read_csv(carpeta / "feriados.csv")
    inicio, ultima = pd.Timestamp(serie["hora"].min()), pd.Timestamp(serie["hora"].max())
    alcance = ultima + pd.Timedelta(hours=max(config.RETRASOS))
    if instante < inicio:
        raise ValueError(f"la serie empieza el {fecha_larga(inicio)}")
    if instante > alcance:
        raise ValueError(f"después del último dato publicado ({fecha_larga(ultima)}) solo se puede pronosticar "
                         f"hasta una semana más allá, es decir, hasta el {fecha_larga(alcance)}")
    if instante > ultima:
        horas = pd.date_range(ultima + pd.Timedelta(hours=1), instante, freq="h")
        extra = pd.DataFrame({"hora": horas.strftime("%Y-%m-%d %H:%M:%S"), "viajes": np.nan, "cobertura_dudosa": False})
        serie = pd.concat([serie, extra], ignore_index=True)
    return preparar_serie(serie, feriados), ultima, pd.to_datetime(feriados["fecha"]).max()


def modelos_congelados(df, retraso):
    """Ajuste final del experimento (experimento.ejecutar_escenario): 2022 a junio de 2025."""
    elegidos = json.loads((config.RESULTADOS / "hiperparametros_elegidos.json").read_text(encoding="utf-8"))
    elegidos = elegidos["por_retraso"][str(retraso)]
    completo = df.loc[config.ENTRENAMIENTO[0]:config.VALIDACION[1]]
    clave = (retraso, json.dumps(elegidos, sort_keys=True), int(pd.util.hash_pandas_object(completo).sum()))
    if clave not in _modelos:
        ajuste = completo.dropna(subset=ENTRADAS_CONTEO)
        modelos = {}
        with threadpool_limits(limits=1):
            for nombre in METODOS:
                parametros = {k: tuple(v) if isinstance(v, list) else v for k, v in elegidos[nombre].items()}
                datos = completo if nombre == "mediana_calendario" else ajuste
                modelos[nombre] = crear_modelo(nombre, **parametros).ajustar(datos)
        _modelos[clave] = modelos
    return _modelos[clave]


def pronosticar(instante, retrasos=tuple(config.RETRASOS)):
    """Pronóstico de cada método para la hora `instante`, con cada retraso. Devuelve un diccionario."""
    instante = pd.Timestamp(instante)
    if instante.tzinfo is not None:
        raise ValueError("escribe la hora local de Buenos Aires, sin zona horaria")
    if instante != instante.floor("h"):
        raise ValueError("la hora debe ser en punto (por ejemplo 18:00): cada pronóstico es de una hora completa")
    serie, ultima, ultimo_feriado = cargar_serie_hasta(instante)
    real = serie.at[instante, "viajes"]
    resultado = {
        "instante": instante,
        "real": None if pd.isna(real) else float(real),
        "ultimo_dato": ultima,
        "dentro_del_ajuste": instante <= FIN_AJUSTE,
        "sin_calendario_de_feriados": instante.year > ultimo_feriado.year,
        "escenarios": {},
    }
    for retraso in retrasos:
        df = variables_escenario(serie, retraso)
        fila = df.loc[[instante]]
        corte = instante - pd.Timedelta(hours=retraso)
        escenario = {"corte": corte, "ultimo_conteo": fila["ultimo_conteo"].iat[0], "pronosticos": {}, "sin_dato": {},
                     # Honesto: los modelos no vieron nada posterior a lo que se conocería en este escenario.
                     "honesto": corte >= FIN_AJUSTE}
        if corte > ultima:
            escenario["motivo"] = (f"ese conteo todavía no se conocería: con el dato de hace {EDADES[retraso]} se "
                                   f"puede pronosticar hasta el {fecha_larga(ultima + pd.Timedelta(hours=retraso))}")
        else:
            modelos = None
            for nombre in METODOS:
                faltan = [v for v in REQUISITOS[nombre] if pd.isna(fila[v].iat[0])]
                if faltan:
                    escenario["sin_dato"][nombre] = faltan
                    continue
                modelos = modelos or modelos_congelados(df, retraso)
                escenario["pronosticos"][nombre] = float(modelos[nombre].predecir(fila)[0])
        resultado["escenarios"][retraso] = escenario
    return resultado


def imprimir(r):
    print(f"\nViajes que se iniciarían en Ecobici el {fecha_larga(r['instante'])} "
          f"(de {r['instante']:%H:%M} a {r['instante']:%H}:59, hora de Buenos Aires)")
    if r["real"] is not None:
        print(f"Dato real: {viajes(r['real'])}")
    elif r["instante"] > r["ultimo_dato"]:
        print(f"Dato real: todavía no publicado (el último es del {fecha_larga(r['ultimo_dato'])})")
    else:
        print("Dato real: no disponible (el archivo publicado de esa hora está incompleto)")
    if r["dentro_del_ajuste"]:
        # Este aviso cubre todos los escenarios: por eso no se repite el aviso de cada uno.
        print("Ojo: esta hora está dentro de los datos con que se ajustaron los modelos (2022 a junio de 2025): el "
              "modelo ya la vio, así que ninguno de estos pronósticos es honesto.")
    if r["sin_calendario_de_feriados"]:
        print("Ojo: el calendario de feriados del proyecto llega hasta 2025; si ese día es feriado, el modelo no lo "
              "sabe y lo trata como un día común.")
    for retraso, e in r["escenarios"].items():
        if "motivo" in e:
            print(f"\nCon el dato de hace {EDADES[retraso]}: no se puede, {e['motivo']}.")
            continue
        conocido = "" if pd.isna(e["ultimo_conteo"]) else f": {viajes(e['ultimo_conteo'])}"
        print(f"\nCon el dato de hace {EDADES[retraso]} (lo último conocido sería el conteo de las "
              f"{e['corte']:%H:%M} del {e['corte'].day} de {MESES[e['corte'].month - 1]}{conocido})")
        if not e["honesto"] and not r["dentro_del_ajuste"]:
            print("  Ojo: los modelos se ajustaron con datos hasta el 30 de junio de 2025, que en este escenario "
                  "todavía no se conocerían; no es un pronóstico honesto.")
        for nombre in METODOS:
            if nombre in e["sin_dato"]:
                faltan = " ni ".join(FALTANTES[v] for v in e["sin_dato"][nombre])
                print(f"  {NOMBRES[nombre]:<24}  sin pronóstico: no hay {faltan}")
                continue
            valor = e["pronosticos"][nombre]
            linea = f"  {NOMBRES[nombre]:<24}{cantidad(valor):>7} {viajes(valor).split()[1]:<6}"
            if r["real"] is not None:
                diferencia = round(valor) - round(r["real"])
                linea += ("  (exacto)" if diferencia == 0 else
                          f"  (se pasa por {cantidad(diferencia)})" if diferencia > 0 else
                          f"  (se queda corto por {cantidad(-diferencia)})")
            print(linea)
    print()


def main(argumentos=None):
    for salida in (sys.stdout, sys.stderr):
        if hasattr(salida, "reconfigure"):
            salida.reconfigure(errors="replace")
    lector = argparse.ArgumentParser(
        description="Pronóstico de los viajes de Ecobici en una hora, con los modelos del estudio.")
    lector.add_argument("hora", help='fecha y hora en punto, hora de Buenos Aires; por ejemplo "2025-12-24 18:00"')
    lector.add_argument("--retraso", type=int, choices=config.RETRASOS, action="append",
                        help="antigüedad del último dato en horas (1, 24 o 168); por defecto, los tres")
    datos = lector.parse_args(argumentos)
    try:
        instante = leer_hora(datos.hora)
        print("Ajustando los modelos del estudio (tarda unos segundos)...", flush=True)
        resultado = pronosticar(instante, tuple(dict.fromkeys(datos.retraso or config.RETRASOS)))
    except ValueError as error:
        lector.error(str(error))
    imprimir(resultado)


if __name__ == "__main__":
    main()
