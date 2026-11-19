"""Comprobaciones de disponibilidad de los conteos y ajuste del calendario."""
import numpy as np
import pandas as pd
import pytest

from src.config import RETRASOS
from src.modelos import MedianaCalendario
from src.variables import CONTEOS, preparar_serie, variables_escenario


@pytest.mark.parametrize("retraso", RETRASOS)
def test_conteos_no_usan_horas_posteriores_al_corte(retraso):
    serie = pd.DataFrame({"viajes": np.arange(400, dtype=float)},
                         index=pd.date_range("2025-01-01", periods=400, freq="h"))
    t = 220
    corte = t - retraso
    esperado = variables_escenario(serie, retraso)[CONTEOS].iloc[t]
    modificada = serie.copy()
    modificada.iloc[corte + 1:t + 1, 0] += 5000
    obtenido = variables_escenario(modificada, retraso)[CONTEOS].iloc[t]
    pd.testing.assert_series_equal(obtenido, esperado)
    assert obtenido["ultimo_conteo"] == corte
    assert obtenido["media_24"] == np.mean(np.arange(corte - 23, corte + 1))
    assert obtenido["semana_anterior"] == t - 168


def test_media_24_exige_al_menos_18_conteos():
    serie = pd.DataFrame({"viajes": np.arange(31, dtype=float)})
    serie.loc[6:11, "viajes"] = np.nan
    media = variables_escenario(serie, 1).loc[30, "media_24"]
    assert media == serie.loc[6:29, "viajes"].mean()
    serie.loc[12, "viajes"] = np.nan
    assert np.isnan(variables_escenario(serie, 1).loc[30, "media_24"])


def test_mediana_usa_solo_el_bloque_de_ajuste_y_agrupa_feriados_con_domingos():
    serie = pd.DataFrame({
        "hora": ["2024-12-25 09:00", "2024-12-29 09:00", "2025-01-05 09:00", "2025-01-06 09:00"],
        "viajes": [10, 30, 9999, 9999],
        "cobertura_dudosa": False,
    })
    feriados = pd.DataFrame({"fecha": ["2024-12-25", "2025-01-06"], "tipo": ["feriado", "feriado"]})
    datos = preparar_serie(serie, feriados)
    mediana = MedianaCalendario().ajustar(datos.loc[:"2024-12-31"])
    prueba = datos.loc[datos.index >= "2025-01-01"].dropna(subset=["viajes"])
    np.testing.assert_array_equal(mediana.predecir(prueba), [20, 20])
