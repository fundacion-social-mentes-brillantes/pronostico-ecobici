"""Ajusta, selecciona y evalúa los modelos con particiones cronológicas fijas."""
import json
from itertools import product
from time import perf_counter

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

if __package__:
    from . import config
    from .estadistica import calcular_metricas, diebold_mariano, holm
    from .modelos import METODOS, crear_modelo
    from .variables import CONTEOS, cargar_serie, variables_escenario
else:
    import config
    from estadistica import calcular_metricas, diebold_mariano, holm
    from modelos import METODOS, crear_modelo
    from variables import CONTEOS, cargar_serie, variables_escenario


ENTRADAS_CONTEO = ["viajes", *CONTEOS]
REJILLAS = {
    "ingenuo_semanal": [{}],
    "mediana_calendario": [{}],
    "ridge": [{"alpha": alpha} for alpha in (0.1, 1, 10, 100)],
    "boosting": [
        {"learning_rate": tasa, "max_leaf_nodes": hojas}
        for tasa, hojas in product((0.05, 0.1), (15, 31, 63))
    ],
    "mlp": [
        {"hidden_layer_sizes": capas, "alpha": alpha}
        for capas, alpha in product(((64,), (64, 32)), (1e-4, 1e-3))
    ],
}


def inicio_con_margen(particion):
    return (pd.Timestamp(particion[0]) + pd.Timedelta(days=config.MARGEN_DIAS)).date().isoformat()


def guardar_json(nombre, datos):
    ruta = config.RESULTADOS / nombre
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def seleccionar_horas_prueba(serie, escenarios):
    prueba = serie.loc[inicio_con_margen(config.PRUEBA):config.PRUEBA[1]]
    objetivo_faltante = prueba["viajes"].isna()
    faltantes = pd.DataFrame(index=prueba.index)
    for retraso, df in escenarios.items():
        for variable in CONTEOS:
            faltantes[f"{variable}_d{retraso}"] = df.loc[prueba.index, variable].isna()
    conteos_faltantes = faltantes.any(axis=1)
    excluida = objetivo_faltante | conteos_faltantes
    guardar_json("horas_excluidas.json", {
        "horas_prueba_antes_de_excluir": len(prueba),
        "horas_evaluadas": int((~excluida).sum()),
        "horas_excluidas": int(excluida.sum()),
        "horas_excluidas_por_margen": config.MARGEN_DIAS * 24,
        "solo_objetivo_faltante": int((objetivo_faltante & ~conteos_faltantes).sum()),
        "solo_variables_de_conteo_faltantes": int((~objetivo_faltante & conteos_faltantes).sum()),
        "objetivo_y_variables_de_conteo_faltantes": int((objetivo_faltante & conteos_faltantes).sum()),
        "por_motivo_no_excluyente": {
            "objetivo_faltante": int(objetivo_faltante.sum()),
            **{motivo: int(total) for motivo, total in faltantes.sum().items()},
        },
    })
    return prueba.loc[~excluida]


def evaluar(nombre, parametros, ajuste, ajuste_completo, evaluacion, horas_pico):
    # La mediana usa todos los objetivos observados del bloque. Ridge, MLP y
    # ambos boosting usan las mismas filas con objetivo y conteos completos.
    # Si faltara clima, boosting_clima admite esos NaN de forma nativa.
    datos_ajuste = ajuste_completo if nombre == "mediana_calendario" else ajuste
    modelo = crear_modelo(nombre, **parametros)
    inicio = perf_counter()
    modelo.ajustar(datos_ajuste)
    tiempo_ajuste = perf_counter() - inicio
    inicio = perf_counter()
    predicho = modelo.predecir(evaluacion)
    tiempo_prediccion = perf_counter() - inicio
    if not np.isfinite(predicho).all():
        raise ValueError(f"Predicciones no finitas para {nombre}")
    metricas = calcular_metricas(evaluacion, predicho, horas_pico)
    return predicho, {
        **metricas, "tiempo_ajuste_s": tiempo_ajuste, "tiempo_prediccion_s": tiempo_prediccion,
    }


def ejecutar_escenario(df, retraso, horas_prueba, horas_pico):
    ajuste_completo = df.loc[config.ENTRENAMIENTO[0]:config.ENTRENAMIENTO[1]]
    ajuste = ajuste_completo.dropna(subset=ENTRADAS_CONTEO)
    validacion = df.loc[inicio_con_margen(config.VALIDACION):config.VALIDACION[1]]
    validacion = validacion.dropna(subset=ENTRADAS_CONTEO)
    filas_validacion, elegidos = [], {}
    for nombre, candidatos in REJILLAS.items():
        filas = []
        for parametros in candidatos:
            _, indicadores = evaluar(nombre, parametros, ajuste, ajuste_completo, validacion, horas_pico)
            filas.append({"metodo": nombre, "retraso": retraso, "hiperparametros": parametros, **indicadores})
        mejor = min(filas, key=lambda fila: fila["mae"])
        elegidos[nombre] = mejor["hiperparametros"]
        for fila in filas:
            fila["elegido"] = fila is mejor
            fila["hiperparametros"] = json.dumps(fila["hiperparametros"])
        filas_validacion.extend(filas)

    # El clima de la hora objetivo procede de ERA5 y se conoce retrospectivamente.
    elegidos["boosting_clima"] = elegidos["boosting"].copy()
    ajuste_final_completo = df.loc[config.ENTRENAMIENTO[0]:config.VALIDACION[1]]
    ajuste_final = ajuste_final_completo.dropna(subset=ENTRADAS_CONTEO)
    prueba = df.loc[horas_prueba]
    filas_prueba, predicciones = [], []
    for nombre, parametros in elegidos.items():
        predicho, indicadores = evaluar(nombre, parametros, ajuste_final, ajuste_final_completo, prueba, horas_pico)
        filas_prueba.append({"metodo": nombre, "retraso": retraso, **indicadores})
        predicciones.append(pd.DataFrame({
            "hora": prueba.index, "metodo": nombre, "retraso": retraso,
            "real": prueba["viajes"].to_numpy(), "predicho": predicho,
        }))
    return filas_validacion, elegidos, filas_prueba, predicciones


def guardar_contrastes(predicciones, horas_prueba):
    filas = []
    posiciones = (horas_prueba - horas_prueba[0]) // pd.Timedelta(hours=1)
    for retraso in config.RETRASOS:
        escenario = predicciones.loc[predicciones["retraso"].eq(retraso)]
        errores = escenario.assign(abs_error=(escenario["predicho"] - escenario["real"]).abs())
        perdidas = errores.pivot(index="hora", columns="metodo", values="abs_error").loc[horas_prueba]
        dm = diebold_mariano(perdidas["boosting"], perdidas["ingenuo_semanal"], posiciones=posiciones)
        filas.append({"retraso": retraso, "n_horas": len(perdidas), **dm})
    tabla = pd.DataFrame(filas)
    tabla["p_holm"] = holm(tabla["p"])
    tabla.to_csv(config.RESULTADOS / "diebold_mariano.csv", index=False)


def ejecutar_experimento():
    config.RESULTADOS.mkdir(parents=True, exist_ok=True)
    serie = cargar_serie()
    escenarios = {d: variables_escenario(serie, d) for d in config.RETRASOS}
    prueba = seleccionar_horas_prueba(serie, escenarios)
    entrenamiento = serie.loc[config.ENTRENAMIENTO[0]:config.ENTRENAMIENTO[1]]
    horas_pico = (entrenamiento.loc[entrenamiento["tipo_dia"].eq("laborable")]
                  .groupby("hora")["viajes"].mean().nlargest(6).index.tolist())
    filas_validacion, filas_prueba, predicciones, elegidos = [], [], [], {}
    # Limita OpenMP y BLAS para evitar sobrecoste de paralelismo en ajustes pequeños.
    with threadpool_limits(limits=1):
        for retraso, df in escenarios.items():
            print(f"Validación y prueba con {retraso} h de retraso", flush=True)
            validacion, elegidos[retraso], prueba_d, predicciones_d = ejecutar_escenario(
                df, retraso, prueba.index, horas_pico,
            )
            filas_validacion.extend(validacion)
            filas_prueba.extend(prueba_d)
            predicciones.extend(predicciones_d)

    tabla_prueba = pd.DataFrame(filas_prueba)
    referencia = tabla_prueba.loc[tabla_prueba["retraso"].eq(1)].set_index("metodo")["mae"]
    mae_d1 = tabla_prueba["metodo"].map(referencia)
    tabla_prueba["cambio_mae_vs_d1"] = tabla_prueba["mae"] - mae_d1
    tabla_prueba["cambio_mae_vs_d1_pct"] = 100 * tabla_prueba["cambio_mae_vs_d1"] / mae_d1.replace(0, np.nan)
    pd.DataFrame(filas_validacion).to_csv(config.RESULTADOS / "metricas_validacion.csv", index=False)
    guardar_json("hiperparametros_elegidos.json", {"horas_pico": horas_pico, "por_retraso": elegidos})
    tabla_prueba.to_csv(config.RESULTADOS / "metricas_prueba.csv", index=False)
    tabla_predicciones = pd.concat(predicciones, ignore_index=True)
    tabla_predicciones.to_csv(config.RESULTADOS / "predicciones_prueba.csv", index=False)
    guardar_contrastes(tabla_predicciones, prueba.index)


if __name__ == "__main__":
    ejecutar_experimento()
