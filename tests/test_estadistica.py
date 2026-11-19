"""Casos de referencia para Diebold-Mariano y Holm."""
import numpy as np
import pytest

from src.estadistica import diebold_mariano, holm


def test_diebold_mariano_con_perdidas_iguales():
    perdidas = np.arange(100, dtype=float)
    resultado = diebold_mariano(perdidas, perdidas)
    assert resultado["estadistico_dm"] == pytest.approx(0)
    assert resultado["p"] == pytest.approx(1)


def test_diebold_mariano_con_un_rezago_bartlett():
    # Diferencias centradas -1, 1, -1, 1: gamma_0 = 1, gamma_1 = -3/4.
    resultado = diebold_mariano([2, 4, 2, 4], [2, 2, 2, 2], rezagos=1)
    assert resultado["estadistico_dm"] == pytest.approx(4)


def test_diebold_mariano_respeta_los_huecos_de_la_rejilla():
    # Con un hueco entre las posiciones 1 y 3, el par (1, 3) no es contiguo y no aporta autocovarianza de rezago 1.
    con_hueco = diebold_mariano([2, 4, 2, 4], [2, 2, 2, 2], rezagos=1, posiciones=[0, 1, 3, 4])
    seguido = diebold_mariano([2, 4, 2, 4], [2, 2, 2, 2], rezagos=1)
    assert con_hueco["estadistico_dm"] != pytest.approx(seguido["estadistico_dm"])
    with pytest.raises(ValueError):
        diebold_mariano([1, 2], [1, 1], posiciones=[1, 1])


def test_diebold_mariano_no_inventa_significacion_con_varianza_nula():
    resultado = diebold_mariano([3, 3, 3], [1, 1, 1])
    assert np.isnan(resultado["estadistico_dm"]) and np.isnan(resultado["p"])
    with pytest.raises(ValueError):
        diebold_mariano([1, np.inf], [1, 1])


def test_holm_respeta_orden_original_y_monotonia():
    np.testing.assert_allclose(holm([0.04, 0.01, 0.03]), [0.06, 0.03, 0.06])
    np.testing.assert_allclose(holm([0.8, 0.5, 0.01]), [1, 1, 0.03])
