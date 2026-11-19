# Resumen

Los sistemas públicos de bicicletas necesitan anticipar la demanda de las próximas horas, pero el último dato de
uso no siempre está disponible al momento de pronosticar. Este trabajo compara cinco técnicas para pronosticar los
viajes iniciados por hora en Ecobici, el sistema público de bicicletas de Buenos Aires, y mide cuánto empeora cada
una cuando el último conteo disponible tiene 1, 24 o 168 horas de antigüedad. A partir de los recorridos abiertos
de 2022 a 2025 se construyó con SQL una serie de 35.064 horas y 11.936.199 viajes depurados; en el proceso se detectó
que el archivo de 2024 incluye 321.015 recorridos de menos de un minuto, frente a ninguno en 2022 y 2023 y 8 en 2025.
Se compararon dos referencias simples (ingenuo semanal y mediana de calendario), regresión Ridge, *gradient
boosting* de árboles y un perceptrón multicapa, con particiones cronológicas, márgenes de siete días y modelos
congelados en un semestre de prueba de 4.244 horas. Con datos de hace una hora, el *boosting* obtuvo el menor error
de las cinco alternativas (31,2 viajes por hora, un 8,3 % del nivel medio). Con un día de retraso, el error de los
tres modelos ajustados se multiplicó por cerca de 2,5. La ventaja del *boosting* sobre la referencia ingenua fue del
70 % con datos de una hora, del 25 % con un día y del 14 % con una semana, significativa en los tres casos según la
prueba de Diebold-Mariano. El clima observado, que es información retrospectiva, apenas cambió el error con datos
frescos, pero lo redujo un 25-28 % con datos atrasados. En este caso, la frescura de los datos pesó más que la
elección entre modelos competentes.

**Palabras clave:** pronóstico de demanda, bicicletas compartidas, aprendizaje automático, disponibilidad de datos,
evaluación cronológica.

# Abstract

Bike-sharing systems need to anticipate demand for the coming hours, but the latest usage data are not always
available when the forecast is made. This work compares five techniques for forecasting the trips started per hour
in Ecobici, the public bike-sharing system of Buenos Aires, and measures how much each one degrades when the latest
available count is 1, 24 or 168 hours old. From the open trip records of 2022-2025, an hourly series of 35,064 hours
and 11,936,199 cleaned trips was built with SQL; the 2024 file was found to contain 321,015 trips shorter than one
minute, against none in 2022 and 2023 and 8 in 2025. Two simple baselines (seasonal naive and calendar median), Ridge
regression, gradient-boosted trees and a multilayer perceptron were compared with chronological splits, seven-day
gaps and models frozen over a 4,244-hour test semester. With one-hour-old data, gradient boosting achieved the
lowest error of the five alternatives (31.2 trips per hour, 8.3% of the mean level). With one day of delay, the error
of the three fitted models grew by a factor of about 2.5. The advantage of boosting over the naive baseline was 70%
with one-hour-old data, 25% with one day and 14% with one week, significant in all three cases according to the
Diebold-Mariano test. Observed weather, which is retrospective information, barely changed the error with fresh data
but cut it by 25-28% with delayed data. In this case, data freshness mattered more than the choice among competent
models.

**Keywords:** demand forecasting, bike sharing, machine learning, data availability, chronological evaluation.
