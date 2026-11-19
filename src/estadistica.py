"""Métricas en viajes por hora y contrastes de precisión predictiva."""
from math import erfc, sqrt

import numpy as np


def calcular_metricas(df, predicho, horas_pico):
    error = predicho - df["viajes"].to_numpy()
    absoluto = np.abs(error)
    pico = df["hora"].isin(horas_pico).to_numpy()
    lluvia = df["precipitacion"].gt(0).to_numpy()
    return {
        "mae": absoluto.mean(),
        "rmse": np.sqrt(np.mean(error**2)),
        "sesgo": error.mean(),
        "mae_pico": absoluto[pico].mean() if pico.any() else np.nan,
        "mae_lluvia": absoluto[lluvia].mean() if lluvia.any() else np.nan,
        "n_horas": len(df),
    }


def diebold_mariano(perdida_a, perdida_b, rezagos=24, posiciones=None):
    """Contraste bilateral sobre pérdida A menos B, en orden cronológico."""
    a, b = np.asarray(perdida_a, dtype=float), np.asarray(perdida_b, dtype=float)
    if a.ndim != 1 or a.shape != b.shape or not len(a):
        raise ValueError("Se requieren dos vectores no vacíos de pérdidas emparejadas")
    if not (np.isfinite(a).all() and np.isfinite(b).all()):
        raise ValueError("Las pérdidas deben ser finitas")
    diferencial = a - b
    media = diferencial.mean()
    centrado = diferencial - media
    n = len(centrado)
    if posiciones is not None:
        # Mantiene los huecos de la rejilla horaria. Un par que toca una hora
        # excluida no contribuye al producto de diferencias centradas.
        posiciones = np.asarray(posiciones, dtype=int)
        if posiciones.shape != a.shape or posiciones[0] < 0 or np.any(np.diff(posiciones) <= 0):
            raise ValueError("Las posiciones deben ser no negativas, crecientes y sin repetir")
        rejilla = np.zeros(posiciones[-1] + 1)
        rejilla[posiciones] = centrado
        centrado = rejilla

    # Newey-West: autocovarianzas con divisor común n y ponderación Bartlett.
    # Bajo igualdad predictiva, la media dividida por su error estándar es
    # asintóticamente normal. erfc da la de dos colas sin restar de 1.
    varianza = centrado @ centrado / n
    for k in range(1, min(rezagos + 1, len(centrado))):
        covarianza = centrado[k:] @ centrado[:-k] / n
        varianza += 2 * (1 - k / (rezagos + 1)) * covarianza
    if varianza > 0:
        estadistico = media / sqrt(varianza / n)
        p = erfc(abs(estadistico) / sqrt(2))
    elif media == 0:
        estadistico, p = 0.0, 1.0
    else:
        # Varianza nula o negativa con media distinta de cero: el contraste no es calculable.
        estadistico, p = np.nan, np.nan
    referencia = b.mean()
    return {
        "estadistico_dm": estadistico,
        "p": p,
        "diferencia_mae": media,
        "diferencia_mae_pct": 100 * media / referencia if referencia else np.nan,
    }


def holm(valores_p):
    """Ajusta los valores p y los devuelve en el orden de entrada."""
    p = np.asarray(valores_p, dtype=float)
    orden = np.argsort(p)
    escalados = p[orden] * np.arange(len(p), 0, -1)
    ajustados = np.empty_like(p)
    ajustados[orden] = np.minimum(1, np.maximum.accumulate(escalados))
    return ajustados
