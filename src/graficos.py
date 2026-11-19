"""Genera las seis figuras de la memoria a partir de los datos y resultados guardados.

Estilo (DESIGN.md): letra Schibsted Grotesk (recursos/fuentes), fondo blanco, sin marcos, rejilla horizontal suave
y una sola codificación de color, la edad del dato: 1 hora verde azulado, 1 día ámbar y 1 semana terracota. El
resto va en tonos de tinta y gris. Cada figura se guarda en PNG (para el Word) y en SVG (para el PDF), con un ancho
de 6,6 pulgadas, el de la caja de texto del PDF, para que las letras se impriman a su tamaño real.
"""
import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

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

TINTA, TINTA_2, TINTA_3 = "#1A1D21", "#4F555D", "#62686F"
LINEA, GRIS = "#D6D3CA", "#80858C"
EDAD = {1: "#0F6F63", 24: "#965806", 168: "#AE3B2F"}
NOMBRE_EDAD = {1: "Dato de 1 hora", 24: "Dato de 1 día", 168: "Dato de 1 semana"}
ETIQUETAS = {
    "ingenuo_semanal": "Ingenuo semanal",
    "mediana_calendario": "Mediana de calendario",
    "ridge": "Ridge",
    "boosting": "Boosting",
    "mlp": "Perceptrón multicapa",
    "boosting_clima": "Boosting + clima",
}
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
ANCHO = 6.6


def estilo():
    for ruta in sorted((config.RAIZ / "recursos" / "fuentes").glob("*.ttf")):
        font_manager.fontManager.addfont(str(ruta))
    plt.rcParams.update({
        "font.family": "Schibsted Grotesk", "font.size": 8.5,
        "axes.edgecolor": TINTA_3, "axes.linewidth": 0.8, "axes.labelcolor": TINTA_2, "axes.labelsize": 8.5,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.titlesize": 8.5, "axes.titleweight": 600, "axes.titlelocation": "left", "axes.titlepad": 8,
        "axes.titlecolor": TINTA_2,
        "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
        "grid.color": LINEA, "grid.linewidth": 0.7,
        "xtick.color": TINTA_3, "ytick.color": TINTA_3, "xtick.labelcolor": TINTA_2, "ytick.labelcolor": TINTA_2,
        "xtick.major.size": 3, "xtick.major.width": 0.8, "ytick.major.size": 0, "ytick.major.pad": 4,
        "legend.frameon": False, "legend.fontsize": 8, "legend.handlelength": 1.8, "legend.columnspacing": 1.4,
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "svg.fonttype": "path", "svg.hashsalt": "pronostico-ecobici", "lines.solid_capstyle": "round",
    })


def coma(v, dec=1):
    return f"{v:,.{dec}f}".replace(",", "_").replace(".", ",").replace("_", ".")


MILES = FuncFormatter(lambda v, _: coma(v, 0))


def guardar(fig, nombre):
    base = config.FIGURAS / nombre
    fig.savefig(base.with_suffix(".png"), dpi=220, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(base.with_suffix(".svg"), bbox_inches="tight", pad_inches=0.04, metadata={"Date": None})
    plt.close(fig)


def viajes_diarios(serie):
    fig, eje = plt.subplots(figsize=(ANCHO, 2.7))
    grupos = serie["viajes"].resample("D")
    completos = grupos.sum(min_count=24)
    dudosos = grupos.count().lt(24)
    subtotales = grupos.sum(min_count=1)
    tramos = [
        ("Entrenamiento", config.ENTRENAMIENTO[0], config.ENTRENAMIENTO[1], "#F2F1ED"),
        ("Validación", inicio_con_margen(config.VALIDACION), config.VALIDACION[1], "#E6E4DD"),
        ("Prueba", inicio_con_margen(config.PRUEBA), config.PRUEBA[1], "#D9D6CD"),
    ]
    for nombre, inicio, fin, color in tramos:
        a, b = pd.Timestamp(inicio), pd.Timestamp(fin) + pd.Timedelta(days=1)
        eje.axvspan(a, b, color=color, lw=0, zorder=0)
        eje.text(a + (b - a) / 2, 1.01, nombre, transform=eje.get_xaxis_transform(), ha="center", va="bottom",
                 fontsize=8, color=TINTA_2)
    eje.plot(completos.index, completos, color=TINTA, lw=0.6)
    eje.scatter(subtotales.index[dudosos], subtotales[dudosos].fillna(0), s=16, facecolors="white",
                edgecolors=TINTA, linewidths=0.9, zorder=3, label="Día con alguna hora de cobertura dudosa (subtotal)")
    eje.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    eje.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _: f"{MESES[mdates.num2date(v).month - 1]} {mdates.num2date(v).year}"))
    eje.set_xlim(pd.Timestamp("2022-01-01"), pd.Timestamp("2026-01-01"))
    eje.yaxis.set_major_formatter(MILES)
    eje.set_ylabel("viajes por día")
    eje.legend(loc="upper left", bbox_to_anchor=(0, -0.12), ncol=1)
    guardar(fig, "01_viajes_diarios")


def perfil_horario(serie):
    fig, eje = plt.subplots(figsize=(ANCHO, 2.6))
    ajuste = serie.loc[config.ENTRENAMIENTO[0]:config.ENTRENAMIENTO[1]]
    perfil = ajuste.groupby(["hora", "tipo_dia"])["viajes"].mean().unstack()
    eje.plot(perfil.index, perfil["laborable"], color=TINTA, lw=1.8, label="Laborable")
    eje.plot(perfil.index, perfil["sabado"], color=TINTA_2, lw=1.1, label="Sábado")
    eje.plot(perfil.index, perfil["domingo_o_feriado"], color=GRIS, lw=1.1, ls=(0, (3, 2)), label="Domingo o feriado")
    pico = perfil["laborable"].idxmax()
    eje.annotate(f"{coma(perfil['laborable'].max(), 0)} viajes a las {pico}:00", (pico, perfil["laborable"].max()),
                 xytext=(-8, 0), textcoords="offset points", ha="right", va="center", fontsize=8, color=TINTA)
    eje.set_xticks(range(0, 24, 2), [f"{h}:00" for h in range(0, 24, 2)])
    eje.set_xlim(0, 23)
    eje.set_ylim(0, None)
    eje.yaxis.set_major_formatter(MILES)
    eje.set_ylabel("viajes por hora")
    eje.set_xlabel("hora del día")
    eje.legend(loc="upper left")
    guardar(fig, "02_perfil_horario")


def barras_mae(metricas):
    fig, eje = plt.subplots(figsize=(ANCHO, 2.8))
    mae = metricas.pivot(index="metodo", columns="retraso", values="mae").loc[list(METODOS)]
    x = np.arange(len(mae))
    ancho = 0.26
    for i, d in enumerate(config.RETRASOS):
        barras = eje.bar(x + (i - 1) * ancho, mae[d], ancho * 0.92, color=EDAD[d], label=NOMBRE_EDAD[d])
        for b, v in zip(barras, mae[d]):
            eje.text(b.get_x() + b.get_width() / 2, v + 1.5, coma(v), ha="center", va="bottom", fontsize=6.6,
                     color=TINTA_2)
    nombres = {"ingenuo_semanal": "Ingenuo\nsemanal", "mediana_calendario": "Mediana de\ncalendario",
               "ridge": "Ridge", "boosting": "Boosting", "mlp": "Perceptrón\nmulticapa"}
    eje.set_xticks(x, [nombres[m] for m in mae.index])
    eje.tick_params(axis="x", length=0)
    eje.set_ylim(0, mae.to_numpy().max() * 1.12)
    eje.set_ylabel("MAE (viajes por hora)")
    eje.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=3)
    guardar(fig, "03_mae_por_metodo")


def dias_con_nombre(eje):
    eje.xaxis.set_major_locator(mdates.DayLocator())
    eje.xaxis.set_minor_locator(mdates.HourLocator(byhour=12))
    eje.xaxis.set_major_formatter(FuncFormatter(lambda v, _: ""))
    eje.xaxis.set_minor_formatter(FuncFormatter(
        lambda v, _: f"{DIAS[mdates.num2date(v).weekday()]} {mdates.num2date(v).day} {MESES[mdates.num2date(v).month - 1]}"))
    eje.tick_params(axis="x", which="minor", length=0, labelsize=8)


def semana_de_prueba(predicciones):
    fig, eje = plt.subplots(figsize=(ANCHO, 2.9))
    ingenuo = predicciones.loc[predicciones["metodo"].eq("ingenuo_semanal") & predicciones["retraso"].eq(1)]
    ingenuo = ingenuo.set_index("hora").sort_index()
    # Toma la primera ventana de siete días completos a partir de medianoche.
    for inicio in ingenuo.index[ingenuo.index.hour == 0]:
        horas = pd.date_range(inicio, periods=168, freq="h")
        if horas.isin(ingenuo.index).all():
            break
    else:
        # Si no hay una semana completa, se muestran las primeras 168 horas disponibles (con sus huecos).
        horas = pd.date_range(ingenuo.index[0], periods=168, freq="h")
    feriados = pd.read_csv(config.DATOS_PROCESADOS / "feriados.csv")
    for dia in pd.to_datetime(feriados.loc[feriados["tipo"].eq("feriado"), "fecha"]):
        if horas[0] <= dia <= horas[-1]:
            eje.axvspan(dia, dia + pd.Timedelta(days=1), color="#EFEDE7", lw=0, zorder=0)
            eje.text(dia + pd.Timedelta(hours=2), 0.97, "Feriado", transform=eje.get_xaxis_transform(),
                     va="top", fontsize=7.5, color=TINTA_3)
    semana = ingenuo.reindex(horas)  # las horas ausentes quedan vacías: la línea se corta en los huecos
    eje.plot(horas, semana["real"], label="Real", color=TINTA, lw=1.5)
    eje.plot(horas, semana["predicho"], label="Ingenuo semanal", color=GRIS, lw=0.9, ls=(0, (3, 2)))
    for d in config.RETRASOS:
        boosting = predicciones.loc[predicciones["metodo"].eq("boosting") & predicciones["retraso"].eq(d)]
        eje.plot(horas, boosting.set_index("hora")["predicho"].reindex(horas), color=EDAD[d], lw=0.95,
                 label=f"Boosting, {NOMBRE_EDAD[d].lower()}")
    dias_con_nombre(eje)
    eje.set_xlim(horas[0], horas[-1] + pd.Timedelta(hours=1))
    eje.set_ylim(0, None)
    eje.yaxis.set_major_formatter(MILES)
    eje.set_ylabel("viajes por hora")
    eje.legend(loc="upper left", bbox_to_anchor=(0, -0.1), ncol=3)
    guardar(fig, "04_semana_de_prueba")


def error_por_hora(predicciones):
    fig, eje = plt.subplots(figsize=(ANCHO, 2.8))
    datos = predicciones.loc[predicciones["retraso"].eq(24)]
    errores = datos.assign(hora_dia=datos["hora"].dt.hour, error=(datos["predicho"] - datos["real"]).abs())
    perfil = errores.groupby(["hora_dia", "metodo"])["error"].mean().unstack()
    trazos = {  # todo el gráfico es con el dato de 1 día: el boosting lleva su color de edad
        "boosting": dict(color=EDAD[24], lw=1.8),
        "boosting_clima": dict(color=EDAD[24], lw=1.1, ls=(0, (1, 1.6))),
        "mlp": dict(color=TINTA_2, lw=1.0),
        "ridge": dict(color=TINTA_3, lw=1.0, ls=(0, (5, 1.5))),
        "ingenuo_semanal": dict(color=GRIS, lw=1.0, ls=(0, (3, 2))),
        "mediana_calendario": dict(color=GRIS, lw=1.0, ls=(0, (1, 1.6))),
    }
    for nombre in (*METODOS, "boosting_clima"):
        eje.plot(perfil.index, perfil[nombre], label=ETIQUETAS[nombre], **trazos[nombre])
    eje.set_xticks(range(0, 24, 2), [f"{h}:00" for h in range(0, 24, 2)])
    eje.set_xlim(0, 23)
    eje.set_ylim(0, None)
    eje.set_ylabel("MAE (viajes por hora)")
    eje.set_xlabel("hora del día (dato de 1 día)")
    eje.legend(loc="upper left", ncol=2)
    guardar(fig, "05_mae_por_hora")


def efecto_clima(metricas):
    fig, eje = plt.subplots(figsize=(ANCHO, 1.95))
    mae = metricas.pivot(index="retraso", columns="metodo", values="mae")
    for k, d in enumerate(config.RETRASOS):
        y = len(config.RETRASOS) - 1 - k
        sin, con = mae.loc[d, "boosting"], mae.loc[d, "boosting_clima"]
        eje.plot([con, sin], [y, y], color=EDAD[d], lw=1.6, zorder=2)
        eje.scatter([sin], [y], s=42, facecolors="white", edgecolors=EDAD[d], linewidths=1.6, zorder=3)
        eje.scatter([con], [y], s=42, color=EDAD[d], zorder=3)
        if sin - con < 6:
            eje.annotate(f"{coma(sin)} → {coma(con)}", (sin, y), xytext=(8, 0), textcoords="offset points",
                         va="center", fontsize=8, color=TINTA_2)
        else:
            eje.annotate(coma(sin), (sin, y), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8,
                         color=TINTA_2)
            eje.annotate(coma(con), (con, y), xytext=(-8, 0), textcoords="offset points", va="center", ha="right",
                         fontsize=8, color=TINTA_2)
    eje.set_yticks(range(len(config.RETRASOS)), [NOMBRE_EDAD[d] for d in reversed(config.RETRASOS)])
    for etiqueta, d in zip(eje.get_yticklabels(), reversed(config.RETRASOS)):
        etiqueta.set_color(EDAD[d])
        etiqueta.set_fontweight(600)
    eje.grid(axis="y", visible=False)
    eje.grid(axis="x", visible=True)
    eje.set_xlim(0, 100)
    eje.set_ylim(-0.6, len(config.RETRASOS) - 0.4)
    eje.set_xlabel("MAE del boosting (viajes por hora)")
    eje.scatter([], [], s=36, facecolors="white", edgecolors=TINTA_2, linewidths=1.4, label="Sin clima")
    eje.scatter([], [], s=36, color=TINTA_2, label="Con clima observado (ERA5)")
    eje.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2)
    guardar(fig, "06_efecto_del_clima")


def generar_figuras():
    config.FIGURAS.mkdir(parents=True, exist_ok=True)
    estilo()
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
