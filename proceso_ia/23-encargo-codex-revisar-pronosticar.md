# Encargo 23 — Revisar el comando que pronostica una hora cualquiera

Al ver el trabajo terminado, quien lo revisaba preguntó por el «predict». El estudio ya predecía (cada modelo tiene
`predecir` en `src/modelos.py` y las 4.244 horas de prueba están en `resultados/predicciones_prueba.csv`), pero no
había una forma directa de pedirle al modelo el pronóstico de una hora concreta. Claude agregó (aún sin subir):

- `src/pronosticar.py`: `python src/pronosticar.py "2025-12-24 18:00" [--retraso 1|24|168]`. Ajusta los cinco
  métodos como el ajuste final de `src/experimento.py` (2022 a junio de 2025, hiperparámetros de
  `resultados/hiperparametros_elegidos.json`, `threadpool_limits(1)`), arma las variables con `variables_escenario` y
  pronostica la hora pedida con cada retraso. Si la hora es posterior al último dato (31/12/2025 23:00), agrega
  horas vacías a la serie y cada escenario llega solo hasta donde alcanza su retraso. Avisa si la hora estaba dentro
  de los datos de ajuste y si cae fuera del calendario de feriados (que llega hasta 2025). No incluye
  `boosting_clima`, porque usa el clima observado de la hora objetivo.
- `tests/test_pronosticar.py`: 11 pruebas. En tres horas de prueba (primera, la 2001 y la última) da los mismos
  números que `predicciones_prueba.csv` para los 5 métodos y los 3 retrasos (con Python sí pasan: 31 de 31); después
  del último dato, cada retraso alcanza exactamente 1, 24 y 168 horas; avisos y rechazos.
- `memoria/construir_gdocs.py` (ya subido en 7e61ab6): versión de la memoria para Google Docs. Si quieres, revísalo
  también, pero lo principal es lo anterior.

Revisa leyendo el código (no puedes ejecutar Python) y señala solo errores reales, con archivo y línea:
1. Fuga de información: que ningún pronóstico use conteos posteriores al corte `hora − retraso`, ni siquiera al
   extender la serie después del último dato (fíjate en `media_24`, `semana_anterior` y el calendario).
2. Que el ajuste sea de verdad el mismo del experimento (datos, filas descartadas, hiperparámetros, mediana con el
   bloque completo), y que la caché `_modelos` no pueda dar modelos equivocados.
3. Casos límite: horas con cobertura dudosa, horas al inicio de la serie, cambio de año, fechas mal escritas.
4. Que los mensajes al usuario sean correctos (alcance de cada retraso, avisos).

Responde en español, breve, lista numerada. Si todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.

(Nota: en el encargo original iba el nombre de pila de quien hizo la pregunta; aquí se cambió por «quien lo revisaba» para no publicar datos personales.)
