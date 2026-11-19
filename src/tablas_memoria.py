"""Tablas complementarias de la memoria, calculadas desde los resultados guardados (no reajusta ningún modelo).

Salida: resultados/tablas_memoria.json con
- error por tipo de día (separando domingos y feriados) y por retraso;
- porcentaje de horas en que el boosting comete menos error que el ingenuo y que el perceptrón;
- efecto del clima en horas secas y con lluvia, y qué parte de la reducción total aporta cada grupo;
- sensibilidad de Diebold-Mariano al número de rezagos de Newey-West (24, 48, 168 y 336);
- cifras descriptivas de la serie usadas en el capítulo 4 (días completos, convención explícita).
"""
import json

import numpy as np
import pandas as pd

if __package__:
    from . import config
    from .estadistica import diebold_mariano, holm
    from .variables import cargar_serie
else:
    import config
    from estadistica import diebold_mariano, holm
    from variables import cargar_serie


def redondear(x, dec=2):
    """Redondea floats y deja null (None) donde un valor no es finito, para que el JSON sea siempre válido."""
    if isinstance(x, dict):
        return {str(k): redondear(v, dec) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [redondear(v, dec) for v in x]
    if isinstance(x, (float, np.floating)):
        return round(float(x), dec) if np.isfinite(x) else None
    if isinstance(x, (np.integer,)):
        return int(x)
    return x


def errores_prueba(serie):
    p = pd.read_csv(config.RESULTADOS / "predicciones_prueba.csv", parse_dates=["hora"])
    extra = serie[["tipo_dia", "feriado", "dia_semana", "precipitacion"]].rename_axis("hora").reset_index()
    p = p.merge(extra, on="hora", how="left", validate="many_to_one")
    p["error_abs"] = (p["predicho"] - p["real"]).abs()
    p["grupo_dia"] = np.select(
        [p["feriado"].eq(1), p["dia_semana"].eq(6), p["dia_semana"].eq(5)],
        ["feriado", "domingo", "sabado"], default="laborable")
    return p


def main():
    serie = cargar_serie()
    p = errores_prueba(serie)
    salida = {}

    por_dia = p.groupby(["retraso", "grupo_dia", "metodo"])["error_abs"].mean()
    salida["mae_por_grupo_de_dia"] = {
        f"{d}h": {g: por_dia.loc[(d, g)].to_dict() for g in ("laborable", "sabado", "domingo", "feriado")}
        for d in config.RETRASOS}
    unicas = p.drop_duplicates("hora")
    salida["horas_por_grupo_de_dia"] = unicas["grupo_dia"].value_counts().to_dict()
    salida["media_real_prueba"] = unicas["real"].mean()

    tabla = p.pivot_table(index=["retraso", "hora"], columns="metodo", values="error_abs")
    salida["porcentaje_horas_boosting_mejor_que_ingenuo"] = {
        f"{d}h": 100 * (tabla.loc[d, "boosting"] < tabla.loc[d, "ingenuo_semanal"]).mean() for d in config.RETRASOS}
    salida["porcentaje_horas_boosting_mejor_que_mlp"] = {
        f"{d}h": 100 * (tabla.loc[d, "boosting"] < tabla.loc[d, "mlp"]).mean() for d in config.RETRASOS}

    clima = {}
    for d in config.RETRASOS:
        t = tabla.loc[d].join(unicas.set_index("hora")["precipitacion"])
        lluvia = t["precipitacion"].gt(0)
        reduccion = t["boosting"] - t["boosting_clima"]
        clima[f"{d}h"] = {
            "horas_lluvia": int(lluvia.sum()), "horas_secas": int((~lluvia).sum()),
            "mae_boosting_lluvia": t.loc[lluvia, "boosting"].mean(),
            "mae_boosting_clima_lluvia": t.loc[lluvia, "boosting_clima"].mean(),
            "mae_boosting_seco": t.loc[~lluvia, "boosting"].mean(),
            "mae_boosting_clima_seco": t.loc[~lluvia, "boosting_clima"].mean(),
            "reduccion_media_por_hora_lluvia": reduccion[lluvia].mean(),
            "reduccion_media_por_hora_seca": reduccion[~lluvia].mean(),
            "parte_de_la_reduccion_total_en_horas_secas_pct": 100 * reduccion[~lluvia].sum() / reduccion.sum(),
            "reduccion_relativa_total_pct": 100 * reduccion.sum() / t["boosting"].sum(),
        }
    salida["clima"] = clima

    # Autocorrelación de la diferencia de pérdidas (boosting menos ingenuo) y peso de los feriados en la ventaja.
    grupo_por_hora = unicas.set_index("hora")["grupo_dia"]
    salida["autocorrelacion_diferencia_de_perdidas"] = {}
    salida["parte_de_la_ventaja_en_feriados_pct"] = {}
    for d in config.RETRASOS:
        dif = (tabla.loc[d, "boosting"] - tabla.loc[d, "ingenuo_semanal"]).asfreq("h")
        salida["autocorrelacion_diferencia_de_perdidas"][f"{d}h"] = {
            f"rezago_{k}": dif.autocorr(k) for k in (1, 24, 168)}
        ventaja = tabla.loc[d, "ingenuo_semanal"] - tabla.loc[d, "boosting"]
        salida["parte_de_la_ventaja_en_feriados_pct"][f"{d}h"] = (
            100 * ventaja[grupo_por_hora.reindex(ventaja.index).eq("feriado")].sum() / ventaja.sum())
    salida["porcentaje_horas_feriado"] = 100 * unicas["grupo_dia"].eq("feriado").mean()

    horas = pd.DatetimeIndex(sorted(unicas["hora"]))
    posiciones = (horas - horas[0]) // pd.Timedelta(hours=1)
    sensibilidad = {}
    for rezagos in (24, 48, 168, 336):
        filas = []
        for d in config.RETRASOS:
            t = tabla.loc[d].loc[horas]
            filas.append(diebold_mariano(t["boosting"], t["ingenuo_semanal"], rezagos=rezagos, posiciones=posiciones))
        p_holm = holm([f["p"] for f in filas])
        sensibilidad[str(rezagos)] = {}
        for d, f, ph in zip(config.RETRASOS, filas, p_holm):
            # Intervalo del 95 % para la diferencia de MAE: diferencia ± 1,96 × error estándar de Newey-West.
            dm = f["estadistico_dm"]
            error_estandar = abs(f["diferencia_mae"] / dm) if np.isfinite(dm) and dm != 0 else np.nan
            sensibilidad[str(rezagos)][f"{d}h"] = {
                "estadistico_dm": f["estadistico_dm"], "p_holm": f"{ph:.2e}",
                "diferencia_mae": f["diferencia_mae"],
                "ic95": (None if not np.isfinite(error_estandar) else
                         [f["diferencia_mae"] - 1.96 * error_estandar, f["diferencia_mae"] + 1.96 * error_estandar])}
    salida["diebold_mariano_sensibilidad_rezagos"] = sensibilidad

    # Cifras descriptivas del capítulo 4: solo días con las 24 horas válidas, bloque 2022-2025.
    s = serie.copy()
    s["fecha"] = s.index.normalize()
    dias = s.groupby("fecha").agg(viajes=("viajes", "sum"), validas=("viajes", "count"),
                                  lluvia=("precipitacion", "sum"), feriado=("feriado", "max"),
                                  dia_semana=("dia_semana", "first"), tipo=("tipo_dia", "first"))
    # La precipitación viene en décimas de mm: se redondea la suma diaria para no arrastrar errores de coma flotante.
    dias["lluvia"] = dias["lluvia"].round(1)
    completos = dias[dias["validas"].eq(24)]
    grupo = np.select([completos["feriado"].eq(1), completos["dia_semana"].eq(6), completos["dia_semana"].eq(5)],
                      ["feriado", "domingo", "sabado"], default="laborable")
    salida["capitulo4"] = {
        "dias_completos": int(len(completos)),
        "media_diaria_por_grupo_dias_completos": completos.groupby(grupo)["viajes"].mean().to_dict(),
        "feriados_entre_semana_media": completos.loc[completos["feriado"].eq(1) & completos["dia_semana"].lt(5),
                                                     "viajes"].mean(),
        "laborables_secos_menos_1mm": {"dias": int(((grupo == "laborable") & (completos["lluvia"] < 1)).sum()),
                                       "media": completos.loc[(grupo == "laborable") & (completos["lluvia"] < 1),
                                                              "viajes"].mean()},
        "laborables_lluvia_10mm_o_mas": {"dias": int(((grupo == "laborable") & (completos["lluvia"] >= 10)).sum()),
                                         "media": completos.loc[(grupo == "laborable") & (completos["lluvia"] >= 10),
                                                                "viajes"].mean()},
        "horas_con_lluvia_periodo_completo": int(s["precipitacion"].gt(0).sum()),
    }
    ajuste = s.loc[config.ENTRENAMIENTO[0]:config.ENTRENAMIENTO[1]]
    perfil = ajuste.groupby(["tipo_dia", "hora"])["viajes"].mean()
    salida["capitulo4"]["perfil_2022_2024"] = {t: perfil.loc[t].round(1).to_dict() for t in
                                               ("laborable", "sabado", "domingo_o_feriado")}

    (config.RESULTADOS / "tablas_memoria.json").write_text(
        json.dumps(redondear(salida), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    escribir_anexos_de_tablas()
    return salida


def coma(x, dec=2):
    """Número con coma decimal, punto de miles y signo menos tipográfico, como en el resto de la memoria."""
    texto = f"{x:,.{dec}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".").replace("-", "−")


PARAMETROS = {"alpha": "α", "learning_rate": "tasa de aprendizaje", "max_leaf_nodes": "hojas máximas",
              "hidden_layer_sizes": "capas ocultas"}


def valor_parametro(x):
    if isinstance(x, list):
        return " y ".join(str(v) for v in x)
    return str(x).replace(".", ",")


NOMBRES = {"ingenuo_semanal": "Ingenuo semanal", "mediana_calendario": "Mediana de calendario", "ridge": "Ridge",
           "boosting": "*Boosting*", "mlp": "Perceptrón"}


def escribir_anexos_de_tablas():
    """Genera memoria/anexos_tablas.md con la búsqueda completa de configuraciones y la cobertura mensual."""
    v = pd.read_csv(config.RESULTADOS / "metricas_validacion.csv")
    lineas = ["# Anexo D. Búsqueda completa de configuraciones", "",
              "Todas las configuraciones probadas en validación (8 de enero a 30 de junio de 2025), con su error. "
              "La marcada con «sí» es la elegida en cada método y escenario (menor MAE). Generada por "
              "`src/tablas_memoria.py` a partir de `resultados/metricas_validacion.csv`.", "",
              "| Método | Retraso | Configuración | MAE | RMSE | Sesgo | Elegida |", "|---|---|---|---|---|---|---|"]
    for _, f in v.iterrows():
        parametros = json.loads(f["hiperparametros"])
        texto = "; ".join(f"{PARAMETROS[k]} {valor_parametro(x)}" for k, x in parametros.items()) or "—"
        lineas.append(f"| {NOMBRES[f['metodo']]} | {f['retraso']} h | {texto} | {coma(f['mae'])} | "
                      f"{coma(f['rmse'])} | {coma(f['sesgo'])} | {'sí' if f['elegido'] else ''} |")
    m = pd.read_csv(config.RESULTADOS / "cobertura_mensual.csv")
    lineas += ["", "# Anexo E. Viajes y horas de cobertura dudosa por mes", "",
               "Generada a partir de `resultados/cobertura_mensual.csv`.", "",
               "| Mes | Viajes válidos | Horas dudosas | Mes | Viajes válidos | Horas dudosas |", "|---|---|---|---|---|---|"]
    mitad = (len(m) + 1) // 2
    for i in range(mitad):
        a = m.iloc[i]
        celdas = [str(a["hora"]), coma(a["viajes"], 0), str(int(a["horas_dudosas"]))]
        if i + mitad < len(m):
            b = m.iloc[i + mitad]
            celdas += [str(b["hora"]), coma(b["viajes"], 0), str(int(b["horas_dudosas"]))]
        else:
            celdas += ["", "", ""]
        lineas.append("| " + " | ".join(celdas) + " |")
    ruta = config.RAIZ / "memoria" / "anexos_tablas.md"
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
    print("tablas_memoria.json listo")
