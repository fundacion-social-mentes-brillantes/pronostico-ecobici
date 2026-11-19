"""Modelos de pronóstico con los métodos ajustar(df) y predecir(df)."""
import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

if __package__:
    from . import config
    from .variables import CLIMA, CONTEOS, TIPOS_DIA
else:
    import config
    from variables import CLIMA, CONTEOS, TIPOS_DIA


METODOS = ("ingenuo_semanal", "mediana_calendario", "ridge", "boosting", "mlp")
INDICADORES = ["feriado", "no_laborable"]


class IngenuoSemanal:
    def ajustar(self, df):
        return self

    def predecir(self, df):
        return df["semana_anterior"].to_numpy()


class MedianaCalendario:
    @staticmethod
    def _grupos(df):
        dia = df["dia_semana"].mask(df["feriado"].eq(1), 6)
        return df.assign(dia_semana=dia)

    def ajustar(self, df):
        self.medianas = self._grupos(df).groupby(["hora", "dia_semana"])["viajes"].median()
        return self

    def predecir(self, df):
        grupos = self._grupos(df).set_index(["hora", "dia_semana"]).index
        return self.medianas.reindex(grupos).to_numpy()


class ModeloIndicadores:
    """Preprocesamiento compartido por Ridge y MLP."""

    def __init__(self, estimador, escalar_objetivo=False):
        self.estimador = estimador
        self.escalador_conteos = StandardScaler()
        self.escalador_objetivo = StandardScaler() if escalar_objetivo else None

    def _entradas(self, df, conteos):
        # El orden fijo conserva las 72 y las 12 columnas en cualquier partición.
        horarios = df["hora"].to_numpy()[:, None] == np.arange(24)
        tipos = df["tipo_dia"].to_numpy()[:, None] == TIPOS_DIA
        hora_tipo = (horarios[:, :, None] & tipos[:, None, :]).reshape(len(df), 72)
        meses = df["mes"].to_numpy()[:, None] == np.arange(1, 13)
        return np.column_stack((hora_tipo, meses, df[INDICADORES], conteos))

    def ajustar(self, df):
        conteos = self.escalador_conteos.fit_transform(np.log1p(df[CONTEOS]))
        objetivo = np.log1p(df["viajes"].to_numpy())
        if self.escalador_objetivo is not None:
            objetivo = self.escalador_objetivo.fit_transform(objetivo[:, None]).ravel()
        self.estimador.fit(self._entradas(df, conteos), objetivo)
        return self

    def predecir(self, df):
        conteos = self.escalador_conteos.transform(np.log1p(df[CONTEOS]))
        salida = self.estimador.predict(self._entradas(df, conteos))
        if self.escalador_objetivo is not None:
            salida = self.escalador_objetivo.inverse_transform(salida[:, None]).ravel()
        return np.expm1(salida).clip(min=0)


class Boosting:
    def __init__(self, con_clima=False, **parametros):
        self.calendario = ["hora", "dia_semana", "mes", *INDICADORES]
        self.clima = CLIMA if con_clima else []
        self.estimador = HistGradientBoostingRegressor(
            categorical_features=["hora", "dia_semana", "mes"],
            max_iter=300, early_stopping=False, random_state=config.SEMILLA, **parametros,
        )

    def _entradas(self, df):
        return df[self.calendario + self.clima].join(np.log1p(df[CONTEOS]))

    def ajustar(self, df):
        self.estimador.fit(self._entradas(df), np.log1p(df["viajes"]))
        return self

    def predecir(self, df):
        return np.expm1(self.estimador.predict(self._entradas(df))).clip(min=0)


def crear_modelo(nombre, **parametros):
    if nombre == "ingenuo_semanal":
        return IngenuoSemanal()
    if nombre == "mediana_calendario":
        return MedianaCalendario()
    if nombre == "ridge":
        return ModeloIndicadores(Ridge(**parametros))
    if nombre == "mlp":
        return ModeloIndicadores(MLPRegressor(
            max_iter=300, early_stopping=True, random_state=config.SEMILLA, **parametros,
        ), escalar_objetivo=True)
    if nombre in ("boosting", "boosting_clima"):
        return Boosting(con_clima=nombre == "boosting_clima", **parametros)
    raise ValueError(f"Modelo desconocido: {nombre}")
