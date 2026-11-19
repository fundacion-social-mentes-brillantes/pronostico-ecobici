# Encargo para Codex: código de modelos, experimentos y pruebas del proyecto «pronostico-ecobici»

Responde en español. Guarda todos los archivos en UTF-8. Trabajas sin internet, en esta carpeta.
Usa el Python del proyecto: `.venv/Scripts/python.exe` (ya tiene pandas, numpy, scikit-learn, statsmodels,
matplotlib, duckdb, pyarrow y pytest). No instales nada. La solución más simple que funcione: no agregues lo que no
se pide. Código claro y comentado en español, porque lo va a leer y calificar alguien que lo revisa a fondo.

## Contexto

Comparativa (trabajo tipo 3 de un máster de IA): pronosticar cuántos viajes de Ecobici Buenos Aires se **inician**
en cada hora en toda la red, y medir cómo cambia el error de cada técnica cuando el último conteo disponible tiene
1, 24 o 168 horas de antigüedad. Lee `src/config.py`. Ya existen (no los cambies):

- `datos/procesados/serie_horaria.csv`: columnas `hora` (inicio de la hora, local), `viajes` (vacío = cobertura
  dudosa, se trata como faltante), `cobertura_dudosa` (bool). 2022-01-01 00:00 a 2025-12-31 23:00.
- `datos/procesados/clima_horario.csv`: `hora`, `temperatura` (°C, instantánea al inicio de la hora),
  `precipitacion` (mm acumulados en [hora, hora+1)). Fuente ERA5 (se publica después: es información retrospectiva).
- `datos/procesados/feriados.csv`: `fecha`, `tipo` (`feriado` | `no_laborable`), `nombre`.

## Definición exacta del problema (no la cambies)

- Al inicio de cada hora *t* se pronostica *y_t* = viajes iniciados en [t, t+1).
- Escenario de retraso *d* ∈ {1, 24, 168}: el conteo más reciente permitido es *y_{t−d}* (la hora que empezó en
  t−d). Ningún dato posterior a t−d puede entrar en una variable de conteo.
- Variables de calendario (siempre conocidas): `hora` (0-23), `dia_semana` (0-6), `mes` (1-12), `feriado` (0/1),
  `no_laborable` (0/1), `tipo_dia` = laborable | sabado | domingo_o_feriado (feriado cuenta como domingo; no
  laborable cuenta como laborable pero con su indicador).
- Variables de conteo por escenario: `ultimo_conteo` = y_{t−d}; `media_24` = media de y_{t−d−23} … y_{t−d}
  (24 horas que terminan en el último conteo; si falta alguna, la media de las disponibles si hay al menos 18, si
  no, faltante); `semana_anterior` = y_{t−168}. (Con d = 168, `ultimo_conteo` y `semana_anterior` coinciden: está
  bien, déjalo así y coméntalo.)

## Las cinco alternativas

1. **ingenuo_semanal**: ŷ_t = y_{t−168}.
2. **mediana_calendario**: mediana de y en el bloque de ajuste, por (`hora`, `dia_semana`), donde los feriados se
   tratan como domingo (dia_semana = 6). No usa conteos recientes.
3. **ridge**: `Ridge` de scikit-learn sobre: variables indicadoras de `hora`×`tipo_dia` (72), de `mes` (12),
   `feriado`, `no_laborable`, y las tres variables de conteo transformadas con log1p y estandarizadas
   (`StandardScaler` ajustado solo con el bloque de ajuste). Objetivo: log1p(y); predicción: expm1, recortada en 0.
4. **boosting**: `HistGradientBoostingRegressor` con `hora`, `dia_semana`, `mes` (como categóricas), `feriado`,
   `no_laborable` y las tres de conteo en log1p. Objetivo log1p(y), predicción expm1 recortada en 0.
5. **mlp**: `MLPRegressor` con las mismas entradas que ridge (mismo preprocesamiento), objetivo log1p(y) estandarizado
   o no (elige lo más simple que converja), `early_stopping=True`, `random_state=config.SEMILLA`.

Análisis secundario (clima): **boosting_clima** = boosting + `temperatura` y `precipitacion` de la hora objetivo.

## Protocolo de evaluación (no lo cambies)

- Ajuste para validación: 2022-01-01 a 2024-12-31. Validación: 2025-01-08 a 2025-06-30 (margen de 7 días).
- Búsqueda pequeña de hiperparámetros, por escenario, eligiendo el menor MAE de validación:
  ridge `alpha` ∈ {0.1, 1, 10, 100}; boosting `learning_rate` ∈ {0.05, 0.1} × `max_leaf_nodes` ∈ {15, 31, 63},
  `max_iter=300`, `random_state=SEMILLA`; mlp `hidden_layer_sizes` ∈ {(64,), (64, 32)} × `alpha` ∈ {1e-4, 1e-3},
  `max_iter=300`. boosting_clima usa la mejor configuración de boosting del mismo escenario.
- Ajuste final: 2022-01-01 a 2025-06-30 (ajuste + validación), con la configuración elegida. La mediana de
  calendario también se recalcula con ese bloque.
- Prueba: 2025-07-08 a 2025-12-31 (margen de 7 días). Modelos congelados. Las variables de conteo de la prueba usan
  los valores reales que ya estarían disponibles según *d* (eso no es reentrenar).
- Filas de ajuste: se descartan las que tengan el objetivo o alguna variable faltante (para boosting puedes dejar
  faltantes en las variables, pero usa las mismas filas que ridge para que sea comparable; elige y documenta).
- **Horas evaluadas**: las mismas para todos los métodos y escenarios: horas de prueba con objetivo válido y con
  todas las variables de los tres escenarios válidas. Guarda cuántas horas se excluyen y por qué
  (`resultados/horas_excluidas.json`).

## Métricas y contraste

- Por método y escenario (y para boosting_clima): MAE (principal, viajes por hora), RMSE, sesgo (media de
  predicho − real), MAE en las **horas pico** (las 6 horas del día con mayor media de viajes en días laborables del
  bloque 2022-2024), MAE en horas con precipitación > 0, número de horas, tiempo de ajuste y de predicción
  (segundos, `time.perf_counter`). Cambio de MAE de cada método respecto a su propio escenario d = 1.
- Diebold-Mariano, solo tres contrastes predefinidos: boosting frente a ingenuo_semanal, uno por *d*, con pérdida
  absoluta sobre las horas evaluadas. Varianza de largo plazo de Newey-West (núcleo de Bartlett) con 24 rezagos;
  estadístico normal asintótico; corrección de Holm sobre los tres valores p. Reporta también la diferencia de MAE
  (viajes/hora y %). Implementa la prueba tú mismo con numpy (son pocas líneas) y explícala en comentarios.

## Figuras (PNG, 150 ppp, texto en español, en `resultados/figuras/`)

1. Viajes diarios 2022-2025, marcando los días de cobertura dudosa y las particiones.
2. Perfil horario medio: laborable vs sábado vs domingo/feriado (bloque 2022-2024).
3. MAE de prueba por método y retraso (barras agrupadas).
4. Una semana de prueba (elige una semana sin huecos): real vs boosting con d = 1, 24, 168 y el ingenuo semanal.
5. MAE por hora del día de cada método con d = 24.
6. Efecto del clima: MAE de boosting vs boosting_clima por retraso.

## Archivos a crear

- `src/variables.py` (construcción de variables por escenario), `src/modelos.py` (las cinco alternativas con una
  interfaz común `ajustar(df)` / `predecir(df)`), `src/estadistica.py` (métricas y Diebold-Mariano),
  `src/experimento.py` (protocolo completo; guarda `resultados/metricas_validacion.csv`,
  `resultados/hiperparametros_elegidos.json`, `resultados/metricas_prueba.csv`, `resultados/diebold_mariano.csv`,
  `resultados/predicciones_prueba.csv`), `src/graficos.py`, y `src/ejecutar_todo.py` que corre experimento y
  gráficos en orden.
- `tests/test_variables.py`: con una serie sintética, comprobar que para cada *d* ninguna variable de conteo usa
  datos posteriores a t−d (por ejemplo, poniendo valores distintos en t−d+1 … t y verificando que no cambian las
  variables), que `ultimo_conteo` = y_{t−d}, que `media_24` termina en t−d y que la mediana de calendario solo usa el
  bloque de ajuste. `tests/test_estadistica.py`: Diebold-Mariano da estadístico ~0 con pérdidas iguales y Holm
  ordena bien.

## Cómo comprobar antes de terminar

1. `.venv/Scripts/python.exe -m pytest -q` sin fallos.
2. `.venv/Scripts/python.exe src/ejecutar_todo.py` termina sin errores (no debería tardar más de unos minutos).
3. Al final, responde con: la tabla de `metricas_prueba.csv` (MAE por método y retraso), el resultado de
   Diebold-Mariano, las horas excluidas, las configuraciones elegidas y el tiempo total. Asume lo razonable y sigue;
   al final di qué no pudiste hacer o comprobar.
