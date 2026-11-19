"""Genera las seis figuras a partir de los datos y resultados guardados."""
import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

if __package__:
    from . import config
    from .experimento import inicio_con_margen
    from .modelos import METODOS
    from .variables import cargar_serie
else:
    import config
    from experimento import inicio_con_margen
    from modelos import METODOS
    from variables import cargar_serie


ETIQUETAS = {
    "ingenuo_semanal": "Ingenuo semanal",
    "mediana_calendario": "Mediana por calendario",
    "ridge": "Ridge",
    "boosting": "Boosting",
    "mlp": "MLP",
    "boosting_clima": "Boosting con clima",
}


def guardar(fig, eje, nombre):
    eje.set_axisbelow(True)
    eje.grid(axis="y", alpha=0.25)
    fig.savefig(config.FIGURAS / nombre, dpi=150, bbox_inches="tight")
    plt.close(fig)


def viajes_diarios(serie):
    fig, eje = plt.subplots(figsize=(13, 4.5))
    grupos = serie["viajes"].resample("D")
    completos = grupos.sum(min_count=24)
    dudosos = grupos.count().lt(24)
    subtotales = grupos.sum(min_count=1)
    eje.plot(completos.index, completos, color="#245269", linewidth=0.8, label="Total diario")
    eje.scatter(subtotales.index[dudosos], subtotales[dudosos].fillna(0), color="#a23323", s=20,
                zorder=3, label="Cobertura dudosa (subtotal observado)")
    particiones = [
        ("Ajuste inicial", config.ENTRENAMIENTO[0], config.ENTRENAMIENTO[1], "#c7dbe7"),
        ("Validación", inicio_con_margen(config.VALIDACION), config.VALIDACION[1], "#f1d59e"),
        ("Prueba", inicio_con_margen(config.PRUEBA), config.PRUEBA[1], "#b4ddd0"),
    ]
    for nombre, inicio, fin, color in particiones:
        eje.axvspan(pd.Timestamp(inicio), pd.Timestamp(fin) + pd.Timedelta(days=1),
                    color=color, alpha=0.45, label=nombre)
    eje.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    eje.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
    eje.tick_params(axis="x", labelrotation=35)
    eje.set(title="Viajes iniciados por día, 2022–2025", ylabel="Viajes")
    eje.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.2), frameon=False)
    guardar(fig, eje, "01_viajes_diarios.png")


def perfil_horario(serie):
    fig, eje = plt.subplots(figsize=(9, 4.5))
    ajuste = serie.loc[config.ENTRENAMIENTO[0]:config.ENTRENAMIENTO[1]]
    perfil = ajuste.groupby(["hora", "tipo_dia"])["viajes"].mean().unstack()
    for tipo, etiqueta in (("laborable", "Laborable"), ("sabado", "Sábado"),
                          ("domingo_o_feriado", "Domingo o feriado")):
        eje.plot(perfil.index, perfil[tipo], label=etiqueta, linewidth=2)
    eje.set(title="Perfil horario medio según el tipo de día, 2022–2024",
            xlabel="Hora local", ylabel="Viajes por hora", xticks=range(0, 24, 2))
    eje.legend()
    guardar(fig, eje, "02_perfil_horario.png")


def barras_mae(metricas):
    fig, eje = plt.subplots(figsize=(10, 4.5))
    mae = metricas.pivot(index="metodo", columns="retraso", values="mae").loc[list(METODOS)]
    x = np.arange(len(mae))
    ancho = 0.24
    for i, d in enumerate(config.RETRASOS):
        eje.bar(x + (i - 1) * ancho, mae[d], ancho, label=f"{d} h")
    eje.set_xticks(x, [ETIQUETAS[m] for m in mae.index])
    eje.set(title="Error de prueba por método y retraso", ylabel="MAE (viajes por hora)")
    eje.set_ylim(0, mae.to_numpy().max() * 1.22)
    eje.legend(title="Retraso", ncol=3, loc="upper center")
    guardar(fig, eje, "03_mae_por_metodo.png")


def semana_de_prueba(predicciones):
    fig, eje = plt.subplots(figsize=(13, 4.5))
    ingenuo = predicciones.loc[predicciones["metodo"].eq("ingenuo_semanal") & predicciones["retraso"].eq(1)]
    ingenuo = ingenuo.set_index("hora").sort_index()
    # Toma la primera ventana de siete días completos a partir de medianoche.
    for inicio in ingenuo.index[ingenuo.index.hour == 0]:
        horas = pd.date_range(inicio, periods=168, freq="h")
        if horas.isin(ingenuo.index).all():
            break
    else:
        # Si no hay una semana completa, se muestran las primeras 168 horas disponibles (con sus huecos).
        horas = ingenuo.index[:168]
        inicio = horas[0]
    semana = ingenuo.loc[horas]
    eje.plot(horas, semana["real"], label="Real", color="#222222", linewidth=2)
    eje.plot(horas, semana["predicho"], label="Ingenuo semanal", color="#777777", linestyle="--")
    for d in config.RETRASOS:
        boosting = predicciones.loc[predicciones["metodo"].eq("boosting") & predicciones["retraso"].eq(d)]
        eje.plot(horas, boosting.set_index("hora").loc[horas, "predicho"], label=f"Boosting, {d} h")
    eje.xaxis.set_major_locator(mdates.DayLocator())
    eje.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    eje.set(title=f"Demanda real y pronosticada del {inicio:%d/%m/%Y} al {horas[-1]:%d/%m/%Y}",
            xlabel="Fecha local", ylabel="Viajes por hora")
    eje.legend(ncol=5)
    guardar(fig, eje, "04_semana_de_prueba.png")


def error_por_hora(predicciones):
    fig, eje = plt.subplots(figsize=(9, 4.5))
    datos = predicciones.loc[predicciones["retraso"].eq(24)]
    errores = datos.assign(hora_dia=datos["hora"].dt.hour, error=(datos["predicho"] - datos["real"]).abs())
    perfil = errores.groupby(["hora_dia", "metodo"])["error"].mean().unstack()
    for nombre in (*METODOS, "boosting_clima"):
        eje.plot(perfil.index, perfil[nombre], label=ETIQUETAS[nombre])
    eje.set(title="Error de prueba por hora del día con 24 h de retraso", xlabel="Hora local",
            ylabel="MAE (viajes por hora)", xticks=range(0, 24, 2))
    eje.legend(ncol=2)
    guardar(fig, eje, "05_mae_por_hora.png")


def efecto_clima(metricas):
    fig, eje = plt.subplots(figsize=(8, 4.5))
    mae = metricas.pivot(index="retraso", columns="metodo", values="mae")
    x = np.arange(len(config.RETRASOS))
    for i, nombre in enumerate(("boosting", "boosting_clima")):
        eje.bar(x + (i - 0.5) * 0.36, mae.loc[config.RETRASOS, nombre], 0.36, label=ETIQUETAS[nombre])
    eje.set_xticks(x, [f"{d} h" for d in config.RETRASOS])
    eje.set(title="Error de prueba con clima retrospectivo de ERA5",
            xlabel="Retraso", ylabel="MAE (viajes por hora)")
    eje.legend()
    guardar(fig, eje, "06_efecto_del_clima.png")


def generar_figuras():
    config.FIGURAS.mkdir(parents=True, exist_ok=True)
    serie = cargar_serie()
    metricas = pd.read_csv(config.RESULTADOS / "metricas_prueba.csv")
    predicciones = pd.read_csv(config.RESULTADOS / "predicciones_prueba.csv", parse_dates=["hora"])
    viajes_diarios(serie)
    perfil_horario(serie)
    barras_mae(metricas)
    semana_de_prueba(predicciones)
    error_por_hora(predicciones)
    efecto_clima(metricas)


if __name__ == "__main__":
    generar_figuras()
