"""El comando de pronóstico da lo mismo que el experimento y respeta lo que se conocería en cada momento."""
import pandas as pd
import pytest

from src import config
from src.pronosticar import METODOS, leer_hora, pronosticar

PREDICCIONES = pd.read_csv(config.RESULTADOS / "predicciones_prueba.csv", parse_dates=["hora"])
ULTIMO_DATO = pd.Timestamp("2025-12-31 23:00")


# El margen (una milmillonésima de viaje) cubre el redondeo distinto de cada computadora: en Windows la diferencia
# con lo guardado es de 10⁻¹³ viajes y en el Linux de GitHub, de 10⁻¹² viajes.
@pytest.mark.parametrize("posicion", [0, 2000, -1])
def test_en_las_horas_de_prueba_da_lo_mismo_que_el_experimento(posicion):
    hora = pd.Timestamp(PREDICCIONES["hora"].unique()[posicion])
    resultado = pronosticar(hora)
    esperadas = PREDICCIONES.loc[PREDICCIONES["hora"].eq(hora)]
    for retraso in config.RETRASOS:
        escenario = resultado["escenarios"][retraso]
        assert escenario["honesto"]
        for metodo in METODOS:
            fila = esperadas.loc[esperadas["metodo"].eq(metodo) & esperadas["retraso"].eq(retraso)]
            assert escenario["pronosticos"][metodo] == pytest.approx(fila["predicho"].iat[0], rel=0, abs=1e-9)
    assert resultado["real"] == esperadas["real"].iat[0]


@pytest.mark.parametrize("horas_despues, posibles", [
    (1, {1, 24, 168}), (2, {24, 168}), (24, {24, 168}), (25, {168}), (168, {168}),
])
def test_despues_del_ultimo_dato_cada_retraso_llega_solo_hasta_su_alcance(horas_despues, posibles):
    resultado = pronosticar(ULTIMO_DATO + pd.Timedelta(hours=horas_despues))
    assert resultado["real"] is None
    assert {d for d, e in resultado["escenarios"].items() if e["pronosticos"]} == posibles
    assert all("motivo" in e for d, e in resultado["escenarios"].items() if d not in posibles)


def test_no_pronostica_mas_alla_de_una_semana_ni_antes_de_la_serie():
    with pytest.raises(ValueError):
        pronosticar(ULTIMO_DATO + pd.Timedelta(hours=169))
    with pytest.raises(ValueError):
        pronosticar("2021-12-31 23:00")


def test_solo_es_honesto_si_los_modelos_no_vieron_nada_posterior_al_corte():
    # El 3 de julio de 2025 a las 00:00, el corte con 1 hora (2 de julio) es posterior al fin del ajuste (30 de
    # junio), pero el corte con una semana (26 de junio) no: el modelo ya vio horas que no se conocerían.
    resultado = pronosticar("2025-07-03 00:00")
    assert resultado["escenarios"][1]["honesto"] and resultado["escenarios"][24]["honesto"]
    assert not resultado["escenarios"][168]["honesto"]
    viejo = pronosticar("2024-05-10 12:00", (1,))
    assert viejo["dentro_del_ajuste"] and not viejo["escenarios"][1]["honesto"]


def test_cada_metodo_pronostica_si_tiene_sus_datos():
    # Al principio de la serie no hay conteo de hace una semana, pero la mediana solo usa el calendario.
    inicio = pronosticar("2022-01-03 10:00", (1,))["escenarios"][1]
    assert set(inicio["pronosticos"]) == {"mediana_calendario"}
    assert "semana_anterior" in inicio["sin_dato"]["ingenuo_semanal"]
    # Una hora con el conteo anterior faltante (archivo incompleto): solo el ingenuo y la mediana pueden pronosticar.
    hueco = pronosticar("2024-05-25 17:00", (1,))["escenarios"][1]
    assert set(hueco["pronosticos"]) == {"ingenuo_semanal", "mediana_calendario"}
    assert all("ultimo_conteo" in hueco["sin_dato"][m] for m in ("boosting", "mlp", "ridge"))
    # Con una semana de historia ya están los tres conteos en todos los escenarios.
    completo = pronosticar("2022-01-08 17:00")
    assert all(set(e["pronosticos"]) == set(METODOS) for e in completo["escenarios"].values())


def test_lee_solo_fechas_con_hora_y_sin_zona_horaria():
    assert leer_hora("2025-12-24 18:00") == pd.Timestamp("2025-12-24 18:00")
    assert leer_hora("2025-12-24T7") == pd.Timestamp("2025-12-24 07:00")
    for mal in ("2025-12", "2025-12-24", "2025-12-24 18:00-03:00", "24/12/2025 18:00", "2025-13-40 18:00"):
        with pytest.raises(ValueError):
            leer_hora(mal)
    with pytest.raises(ValueError):
        pronosticar("2025-12-24 18:30")
    with pytest.raises(ValueError):
        pronosticar(pd.Timestamp("2025-12-24 18:00", tz="America/Argentina/Buenos_Aires"))
