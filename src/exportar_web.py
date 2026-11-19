"""Exporta a web/datos.js las cifras que muestra la página del proyecto, leídas de los resultados guardados.

No ajusta ni vuelve a evaluar ningún modelo: solo lee resultados/ y datos/procesados/ y escribe un archivo
JavaScript (`window.DATOS = {...}`) que la página carga sin servidor. Así cada número de la web sale del código.
Uso: python src/exportar_web.py   (también lo corre src/ejecutar_todo.py al final). Sin fecha de
generación, para que dos ejecuciones iguales den el mismo archivo byte a byte.
"""
import csv
import json

import numpy as np
import pandas as pd

if __package__:
    from . import config
else:
    import config

METODO_SEMANA = "boosting"  # el mejor método en los tres retrasos
METODOS = ["ingenuo_semanal", "mediana_calendario", "ridge", "boosting", "mlp"]
DESTINO = config.RAIZ / "web" / "datos.js"


def r1(x):
    return None if x is None or not np.isfinite(x) else round(float(x), 1)


def leer_json(nombre):
    return json.loads((config.RESULTADOS / nombre).read_text(encoding="utf-8"))


def entero(x):
    return None if pd.isna(x) else int(round(float(x)))


def semanas():
    """Las semanas del semestre de prueba (martes a lunes, desde el primer día con margen), hora por hora: lo real y
    lo que predijo el boosting con cada edad del dato. Las horas excluidas de la prueba quedan en null.
    La semana «típica» es la que minimiza la suma de las diferencias relativas entre su MAE y el MAE del semestre
    completo en los tres retrasos: es la que la página muestra primero."""
    p = pd.read_csv(config.RESULTADOS / "predicciones_prueba.csv", parse_dates=["hora"])
    p = p[p["metodo"] == METODO_SEMANA]
    # El calendario sale del protocolo (no de las horas evaluadas): del primer día de prueba tras el margen al último.
    inicio = pd.Timestamp(config.PRUEBA[0]) + pd.Timedelta(days=config.MARGEN_DIAS)
    fin = pd.Timestamp(config.PRUEBA[1]) + pd.Timedelta(hours=23)
    total = {d: (g["predicho"] - g["real"]).abs().mean() for d, g in p.groupby("retraso")}
    lista, exactos = [], []
    while inicio <= fin:
        horas = pd.date_range(inicio, periods=168, freq="h")
        horas = horas[horas <= fin]
        semana = {"inicio": inicio.strftime("%Y-%m-%d"), "real": None, "pred": {}, "mae": {}}
        mae = {}
        for d in config.RETRASOS:
            t = p[p["retraso"] == d].set_index("hora").reindex(horas)
            semana["real"] = [entero(v) for v in t["real"]]
            semana["pred"][str(d)] = [entero(v) for v in t["predicho"]]
            mae[d] = (t["predicho"] - t["real"]).abs().mean()  # NaN si la semana no tiene horas evaluadas
            semana["mae"][str(d)] = r1(mae[d])
        semana["horas_validas"] = int(sum(v is not None for v in semana["real"]))
        lista.append(semana)
        exactos.append(mae)
        inicio += pd.Timedelta(days=7)
    # Con los MAE sin redondear, para que el redondeo no cambie la semana elegida ni convierta un aumento en empate.
    completas = [i for i, s in enumerate(lista) if s["horas_validas"] >= 160]
    tipica = min(completas, key=lambda i: sum(abs(exactos[i][d] - total[d]) / total[d] for d in config.RETRASOS))
    con_datos = [m for m in exactos if all(np.isfinite(m[d]) for d in config.RETRASOS)]
    crece = int(sum(bool(m[1] < m[24] < m[168]) for m in con_datos))
    feriados = pd.read_csv(config.DATOS_PROCESADOS / "feriados.csv")
    feriados = feriados[(feriados["tipo"] == "feriado") & (feriados["fecha"] >= lista[0]["inicio"])]
    return {"metodo": METODO_SEMANA, "lista": lista, "tipica": tipica, "error_crece_en": crece,
            "semanas_con_datos": len(con_datos),
            "feriados": dict(zip(feriados["fecha"], feriados["nombre"]))}


def metricas():
    m = pd.read_csv(config.RESULTADOS / "metricas_prueba.csv")
    salida = {}
    for d in config.RETRASOS:
        fila = m[m["retraso"] == d].set_index("metodo")
        salida[str(d)] = {met: {"mae": r1(fila.loc[met, "mae"]), "rmse": r1(fila.loc[met, "rmse"]),
                                "mae_pico": r1(fila.loc[met, "mae_pico"])}
                          for met in [*METODOS, "boosting_clima"]}
    return salida


def contrastes():
    with open(config.RESULTADOS / "diebold_mariano.csv", encoding="utf-8") as f:
        return {fila["retraso"]: {"ventaja_pct": r1(-float(fila["diferencia_mae_pct"])),
                                  "diferencia": r1(-float(fila["diferencia_mae"])),
                                  "p_holm": float(f"{float(fila['p_holm']):.2g}")}
                for fila in csv.DictReader(f)}


def cifras():
    calidad = leer_json("calidad_datos.json")
    tablas = leer_json("tablas_memoria.json")
    serie = pd.read_csv(config.DATOS_PROCESADOS / "serie_horaria.csv", index_col=0, parse_dates=True)
    record = serie["viajes"].idxmax()
    c4 = tablas["capitulo4"]
    perfil = c4["perfil_2022_2024"]
    laborable = {int(h): v for h, v in perfil["laborable"].items()}
    pico = max(laborable, key=laborable.get)
    return {
        "viajes": calidad["recorridos_validos"],
        "horas": calidad["horas_totales"],
        "horas_dudosas": calidad["horas_dudosas"],
        "cortos_2024": calidad["anios"]["2024"]["menos_de_60_segundos"],
        "cortos_otros": {a: calidad["anios"][a]["menos_de_60_segundos"] for a in ("2022", "2023", "2025")},
        "sin_llegada_2024": calidad["anios"]["2024"]["llegada_ausente"],
        "media_real_prueba": tablas["media_real_prueba"],
        "horas_prueba": int(sum(tablas["horas_por_grupo_de_dia"].values())),
        "record": {"hora": record.strftime("%Y-%m-%d %H:%M"), "viajes": int(serie["viajes"].max())},
        "pico_laborable": {"hora": pico, "viajes": r1(laborable[pico])},
        "lluvia": {"dias_secos": c4["laborables_secos_menos_1mm"]["dias"],
                   "media_seca": r1(c4["laborables_secos_menos_1mm"]["media"]),
                   "dias_lluvia": c4["laborables_lluvia_10mm_o_mas"]["dias"],
                   "media_lluvia": r1(c4["laborables_lluvia_10mm_o_mas"]["media"])},
        "media_diaria": {k: r1(v) for k, v in c4["media_diaria_por_grupo_dias_completos"].items()},
        "perfil": {t: [r1(perfil[t][str(h)] if str(h) in perfil[t] else perfil[t][h]) for h in range(24)]
                   for t in ("laborable", "sabado", "domingo_o_feriado")},
        "clima": {d: {"reduccion_pct": tablas["clima"][f"{d}h"]["reduccion_relativa_total_pct"]}
                  for d in map(str, config.RETRASOS)},
        "mejor_que_ingenuo_pct": {d.rstrip("h"): v for d, v in
                                  tablas["porcentaje_horas_boosting_mejor_que_ingenuo"].items()},
    }


def particiones():
    return {"entrenamiento": list(config.ENTRENAMIENTO), "validacion": list(config.VALIDACION),
            "prueba": list(config.PRUEBA), "margen_dias": config.MARGEN_DIAS}


def main():
    datos = {
        "retrasos": config.RETRASOS,
        "semanas": semanas(),
        "metricas": metricas(),
        "contrastes": contrastes(),
        "cifras": cifras(),
        "particiones": particiones(),
    }
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("// Generado por src/exportar_web.py a partir de resultados/. No editar a mano.\n"
                       f"window.DATOS = {texto};\n", encoding="utf-8")
    print(f"{DESTINO.relative_to(config.RAIZ)}: {DESTINO.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
