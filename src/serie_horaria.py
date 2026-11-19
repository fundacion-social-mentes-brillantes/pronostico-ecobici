"""Construye la serie de viajes iniciados por hora (Ecobici Buenos Aires, 2022-2025) con SQL (DuckDB).

Pasos:
1. Extrae el CSV de cada ZIP anual a datos/crudos/csv/ (con un límite de tamaño y un archivo temporal que solo se
   renombra cuando la extracción termina bien). Los CSV extraídos se borran al final; los ZIP se conservan.
2. De cada CSV, la consulta SQL selecciona SOLO cinco columnas: identificador del recorrido, fecha y hora de origen
   y de destino, y estaciones de origen y destino. Las columnas del usuario (identificador y género) nunca se
   seleccionan ni pasan al conjunto analítico. (El archivo completo sí se descomprime en disco mientras dura el
   proceso, porque así se publica, y se borra al terminar.)
3. Depura y cuenta cada motivo por separado: inicio inválido o fuera de 2022-2025, llegada ausente, llegada anterior
   a la salida, recorridos de menos de 60 segundos (según las marcas de salida y llegada), identificador ausente y
   recorridos repetidos. El filtro de 60 s iguala los años: en 2022 y 2023 el archivo publicado no trae ningún
   recorrido de menos de 60 s y en 2025 solo 8, mientras que el de 2024 trae 321.015 (el 9 %).
4. Agrega por hora local de inicio y completa todas las horas del periodo.
5. Marca la cobertura dudosa: rachas de 4 o más horas seguidas sin ningún viaje, y horas sin viajes entre las 7:00
   y las 21:59. Esas horas quedan como faltantes (vacías); los demás ceros se conservan. (Se probó también marcar
   los días con muy pocos viajes, pero todos los así marcados coincidieron con feriados o días de lluvia fuerte,
   por lo que la regla se descartó.)
Salidas: datos/procesados/serie_horaria.csv, resultados/calidad_datos.json y resultados/cobertura_mensual.csv.
"""
import json
import os
import uuid
import zipfile

import duckdb
import numpy as np
import pandas as pd

if __package__:
    from .config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, RESULTADOS
else:
    from config import ANIOS, DATOS_CRUDOS, DATOS_PROCESADOS, RESULTADOS

COLUMNAS = {
    "id": ["id_recorrido"],
    "inicio": ["fecha_origen_recorrido"],
    "fin": ["fecha_destino_recorrido"],
    "est_origen": ["id_estacion_origen"],
    "est_destino": ["id_estacion_destino"],
}
LIMITE_DESCOMPRIMIDO = 6 * 1024**3  # 6 GB por archivo: protege contra un ZIP anómalo
INICIO, FIN = "2022-01-01", "2026-01-01"


def extraer(anio):
    """Extrae el único CSV del ZIP del año. Devuelve la ruta del CSV."""
    destino = DATOS_CRUDOS / "csv"
    destino.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(DATOS_CRUDOS / f"recorridos-realizados-{anio}.zip") as z:
        csvs = [i for i in z.infolist() if i.filename.lower().endswith(".csv")]
        if len(csvs) != 1:
            raise ValueError(f"{anio}: se esperaba un único CSV en el ZIP y hay {len(csvs)}")
        miembro = csvs[0]
        if miembro.file_size > LIMITE_DESCOMPRIMIDO:
            raise ValueError(f"{anio}: el CSV ocupa {miembro.file_size:,} bytes, más que el límite")
        # Nombre propio de esta ejecución (el nombre interno del ZIP nunca se usa como ruta): proceso + marca
        # aleatoria, así ni dos ejecuciones simultáneas ni un número de proceso reutilizado pisan archivos ajenos,
        # y al final solo se borran los archivos que creó esta.
        marca = f"{os.getpid()}-{uuid.uuid4().hex[:12]}"
        ruta = destino / f"{anio}.{marca}.csv"
        temporal = destino / f"{anio}.csv.{marca}.parcial"
        if ruta.exists() or temporal.exists():
            raise FileExistsError(f"{anio}: el nombre temporal {marca} ya existe")
        creado = False  # solo se borra el temporal si lo creó esta llamada
        try:
            # Siempre se extrae de nuevo: zipfile comprueba el CRC al leer, así que el CSV queda verificado.
            with open(temporal, "xb") as sal:  # "x": falla si ya existiera
                creado = True
                with z.open(miembro) as fuente:
                    while bloque := fuente.read(16 * 1024 * 1024):
                        sal.write(bloque)
            temporal.replace(ruta)
        finally:
            if creado:
                temporal.unlink(missing_ok=True)
    return ruta


def mapa_columnas(con, ruta):
    """Busca por nombre las cinco columnas necesarias (los nombres cambian entre años)."""
    nombres = [d[0] for d in con.execute(
        "DESCRIBE SELECT * FROM read_csv(?, all_varchar=true)", [str(ruta)]).fetchall()]
    mapa = {}
    for clave, candidatos in COLUMNAS.items():
        coincidencias = [n for n in nombres if n.strip().lower() in candidatos]
        if not coincidencias:
            raise ValueError(f"{ruta.name}: falta la columna {clave}")
        mapa[clave] = coincidencias[0]
    return mapa, len(nombres)


def ident(nombre):
    """Identificador SQL entre comillas dobles, con escape (los nombres vienen de una lista cerrada)."""
    return '"' + nombre.replace('"', '""') + '"'


def depurar(con, ruta, anio):
    """Lee las cinco columnas de un CSV anual, cuenta cada motivo de descarte y deja la tabla limpio_<anio>
    (identificador y hora de salida de los recorridos válidos). Devuelve el diccionario de calidad del año."""
    m, n_columnas = mapa_columnas(con, ruta)
    con.execute(f"""
            CREATE OR REPLACE TEMP TABLE crudo AS
            SELECT {ident(m['id'])} AS id,
                   try_strptime({ident(m['inicio'])}, '%Y-%m-%d %H:%M:%S') AS inicio,
                   try_strptime({ident(m['fin'])}, '%Y-%m-%d %H:%M:%S') AS fin,
                   {ident(m['est_origen'])} AS est_origen,
                   {ident(m['est_destino'])} AS est_destino
            FROM read_csv(?, all_varchar=true)
        """, [str(ruta)])
    # Un solo recorrido de la tabla para todos los contadores de calidad.
    fila = con.execute(f"""
        SELECT count(*),
               count(*) FILTER (WHERE inicio IS NULL),
               count(*) FILTER (WHERE inicio < '{INICIO}' OR inicio >= '{FIN}'),
               count(*) FILTER (WHERE year(inicio) <> {int(anio)}),
               count(*) FILTER (WHERE fin IS NULL),
               count(*) FILTER (WHERE fin < inicio),
               count(*) FILTER (WHERE fin >= inicio AND epoch(fin) - epoch(inicio) < 60),
               count(*) FILTER (WHERE fin >= inicio AND epoch(fin) - epoch(inicio) < 60
                                AND est_origen = est_destino),
               count(*) FILTER (WHERE fin = inicio AND est_origen <> est_destino),
               count(*) FILTER (WHERE id IS NULL OR trim(id) = ''),
               min(inicio), max(inicio)
        FROM crudo""").fetchone()
    r = dict(zip([
        "filas", "inicio_invalido", "inicio_fuera_de_periodo", "inicio_fuera_del_anio_del_archivo",
        "llegada_ausente", "llegada_antes_de_salida", "menos_de_60_segundos",
        "menos_de_60_segundos_misma_estacion", "salida_y_llegada_iguales_entre_estaciones_distintas",
        "identificador_ausente", "inicio_minimo", "inicio_maximo"], fila))
    r["columnas_del_archivo"] = n_columnas
    r["inicio_minimo"], r["inicio_maximo"] = str(r["inicio_minimo"]), str(r["inicio_maximo"])
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE limpio_{int(anio)} AS
        SELECT id, inicio FROM crudo
        WHERE inicio IS NOT NULL AND inicio >= '{INICIO}' AND inicio < '{FIN}'
          AND fin IS NOT NULL AND fin >= inicio
          AND epoch(fin) - epoch(inicio) >= 60
          AND id IS NOT NULL AND trim(id) <> ''
    """)
    r["filas_tras_depurar"] = con.execute(f"SELECT count(*) FROM limpio_{int(anio)}").fetchone()[0]
    return r


def main():
    con = duckdb.connect()
    calidad = {"anios": {}}
    partes = []
    extraidos = []
    try:
        for anio in ANIOS:
            ruta = extraer(anio)
            extraidos.append(ruta)
            r = depurar(con, ruta, anio)
            calidad["anios"][str(anio)] = r
            partes.append(f"SELECT id, inicio FROM limpio_{int(anio)}")
            print(anio, r, flush=True)
        con.execute("CREATE TEMP TABLE todos AS " + " UNION ALL ".join(partes))
    finally:
        # Los CSV extraídos ocupan unos 3,2 GB: se borran siempre, también si algo falla (los ZIP se conservan).
        for ruta in extraidos:
            ruta.unlink(missing_ok=True)

    repetidos = con.execute("""
        SELECT count(*) FILTER (WHERE n > 1),
               coalesce(sum(n - 1) FILTER (WHERE n > 1), 0),
               count(*) FILTER (WHERE n > 1 AND inicios > 1)
        FROM (SELECT id, count(*) AS n, count(DISTINCT inicio) AS inicios FROM todos GROUP BY id)""").fetchone()
    calidad["identificadores_repetidos"] = int(repetidos[0])
    calidad["recorridos_repetidos_eliminados"] = int(repetidos[1])
    calidad["identificadores_repetidos_con_distinta_salida"] = int(repetidos[2])
    con.execute("CREATE TEMP TABLE unicos AS SELECT id, min(inicio) AS inicio FROM todos GROUP BY id")
    calidad["recorridos_validos"] = int(con.execute("SELECT count(*) FROM unicos").fetchone()[0])

    horas = con.execute("""
        SELECT date_trunc('hour', inicio) AS hora, count(*) AS viajes
        FROM unicos GROUP BY 1 ORDER BY 1""").df()
    indice = pd.date_range("2022-01-01 00:00", "2025-12-31 23:00", freq="h", name="hora")
    serie = horas.set_index("hora")["viajes"].reindex(indice, fill_value=0).astype(float).to_frame()

    # Rachas de 4 o más horas seguidas en cero (es una auditoría retrospectiva de la serie: para saber si un cero
    # inicia una racha hay que mirar las horas siguientes).
    cero = serie["viajes"].eq(0)
    grupo = (cero != cero.shift()).cumsum()
    largo = cero.groupby(grupo).transform("size")
    racha = cero & (largo >= 4)
    # Cero en horario diurno (7:00 a 21:59): en esa franja lo normal son decenas o cientos de viajes por hora.
    diurno = cero & (serie.index.hour >= 7) & (serie.index.hour <= 21)
    dudosa = racha | diurno
    serie["cobertura_dudosa"] = dudosa
    serie.loc[serie["cobertura_dudosa"], "viajes"] = np.nan

    calidad["horas_totales"] = int(len(serie))
    calidad["horas_dudosas"] = int(serie["cobertura_dudosa"].sum())
    calidad["dias_con_horas_dudosas"] = sorted({str(h.date()) for h in serie.index[dudosa]})
    calidad["horas_en_rachas_de_ceros"] = int(racha.sum())
    calidad["horas_diurnas_en_cero"] = [str(h) for h in serie.index[diurno & ~racha]]
    calidad["horas_en_cero_conservadas"] = int((serie["viajes"] == 0).sum())

    DATOS_PROCESADOS.mkdir(parents=True, exist_ok=True)
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    serie.to_csv(DATOS_PROCESADOS / "serie_horaria.csv")
    mensual = serie.groupby(serie.index.to_period("M")).agg(
        viajes=("viajes", "sum"), horas_dudosas=("cobertura_dudosa", "sum"))
    mensual.to_csv(RESULTADOS / "cobertura_mensual.csv")
    (RESULTADOS / "calidad_datos.json").write_text(json.dumps(calidad, ensure_ascii=False, indent=2, default=int),
                                                  encoding="utf-8")
    print(json.dumps({k: v for k, v in calidad.items() if k != "anios"}, ensure_ascii=False, indent=2, default=int))


if __name__ == "__main__":
    main()
