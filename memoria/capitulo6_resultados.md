# 6. Resultados

Todos los resultados de este capítulo se refieren al periodo de prueba, del 8 de julio al 31 de diciembre de 2025,
con el protocolo fijado antes de ejecutarlo y los modelos congelados. En la primera repetición tras las correcciones de
robustez, la serie, el clima, las predicciones y los contrastes salieron idénticos; solo cambió una cifra
descriptiva, los días secos, por un ajuste de redondeo. Después, la revisión detectó que faltaba el feriado del 2 de septiembre de 2022.
Se corrigió el calendario y se repitió el experimento. Todas las cifras de la memoria proceden de esa última
ejecución. Las alternativas se comparan sobre las mismas **4.244 horas**: de las 4.248 horas posteriores al margen,
se excluyeron 4 por faltantes, todas alrededor del corte de registro del 14 de octubre de 2025 (una por el objetivo y
tres porque alguna variable de conteo apuntaba a esa hora). En ese periodo se iniciaron de media **374,7 viajes por
hora**, una referencia útil para leer los errores.

## 6.1. Resultado general

La Tabla 6.1 resume las métricas de prueba y la Figura 6.1 muestra el criterio principal, el MAE.

**Tabla 6.1.** Métricas de prueba, en viajes por hora (4.244 horas).

| Método | Retraso | MAE | RMSE | Sesgo medio | MAE en horas pico |
|---|---|---|---|---|---|
| Ingenuo semanal | cualquiera | 104,36 | 177,15 | −2,77 | 191,35 |
| Mediana de calendario | cualquiera | 111,71 | 160,05 | −32,86 | 195,65 |
| Ridge | 1 h | 34,88 | 51,73 | −10,07 | 54,85 |
| *Boosting* | 1 h | **31,15** | **47,07** | −6,32 | **48,18** |
| Perceptrón | 1 h | 33,34 | 49,86 | −10,69 | 52,54 |
| Ridge | 24 h | 87,41 | 139,39 | −34,06 | 167,29 |
| *Boosting* | 24 h | **78,28** | **130,29** | −22,20 | **150,90** |
| Perceptrón | 24 h | 80,75 | 133,58 | −28,31 | 151,88 |
| Ridge | 168 h | 92,43 | 140,95 | −38,25 | 176,60 |
| *Boosting* | 168 h | **89,44** | 141,78 | −29,54 | 170,86 |
| Perceptrón | 168 h | 89,61 | **138,71** | −34,11 | **169,58** |

Nota: las dos referencias no dependen del retraso. El ingenuo semanal solo usa el conteo de hace 168 horas, que está
disponible en los tres escenarios, y la mediana de calendario no usa conteos recientes. Las horas pico son las 13:00
y de las 15:00 a las 19:00.

{{FIGURA:03_mae_por_metodo}}

La tabla muestra tres patrones. Primero, con el último conteo de hace una hora, los tres modelos ajustados cometen
entre 31 y 35 viajes de error medio por hora, entre el 8,3 % y el 9,3 % del nivel medio, frente a más de 100 de las
referencias. Segundo, el MAE de esos tres modelos se multiplica por 2,4 a 2,5 cuando el dato tiene un día de
antigüedad, y por 2,7 a 2,9 cuando tiene una semana. Tercero, la mediana de calendario, que no usa información
reciente, tiene el mayor MAE. Su sesgo medio de −33 viajes por hora indica que, en promedio, subestima. Una
explicación probable es que la demanda del segundo semestre de 2025 fue más alta que la típica del bloque con que se
calculó la mediana (enero de 2022 a junio de 2025).

## 6.2. Primera pregunta: el mejor método con datos frescos

Con una hora de retraso, el *boosting* obtiene el menor MAE (31,15), seguido del perceptrón (33,34) y de Ridge
(34,88). También tiene el menor RMSE, el menor sesgo de los modelos ajustados y el menor error en las horas pico. El
resultado coincide con la hipótesis 1, con una precisión: el orden entre los tres modelos ajustados es descriptivo,
porque los contrastes fijados de antemano solo comparan el *boosting* con el ingenuo semanal. Además, la distancia
entre ellos es pequeña: entre el mejor y el peor hay unos 4 viajes por hora, alrededor de un 1 % del nivel medio.

La Figura 6.2 muestra la primera semana completa de la prueba. Con el dato de hace una hora, el *boosting* sigue de
cerca la forma de cada día, incluidos los picos de la tarde. El miércoles 9 de julio, feriado por el Día de la
Independencia, sirve de ejemplo de la debilidad del ingenuo semanal: copia el miércoles anterior, que fue laborable,
y sobrestima buena parte del día, mientras que el *boosting*, que recibe el indicador de feriado, se mantiene cerca
de lo real.

{{FIGURA:04_semana_de_prueba}}

## 6.3. Segunda pregunta: el coste del retraso

La Tabla 6.2 resume cuánto aumenta el error de cada modelo al envejecer el último conteo. Hay que tener en cuenta que
cada escenario tiene su propia búsqueda de configuraciones, de modo que el aumento mide el coste del escenario
completo: menos información reciente y modelos reajustados a esa situación.

**Tabla 6.2.** Aumento del MAE respecto al escenario de 1 hora.

| Método | MAE con 1 h | Con 24 h | Aumento | Con 168 h | Aumento |
|---|---|---|---|---|---|
| Ridge | 34,88 | 87,41 | +150,62 % | 92,43 | +165,02 % |
| *Boosting* | 31,15 | 78,28 | +151,35 % | 89,44 | +187,16 % |
| Perceptrón | 33,34 | 80,75 | +142,22 % | 89,61 | +168,81 % |

El salto más grande ocurre entre una hora y un día; pasar de un día a una semana añade un aumento menor. Con 24
horas, el *boosting* tiene el menor MAE. Con 168 horas también queda primero (89,44), seguido del perceptrón
(89,61), con una diferencia descriptiva de 0,17 viajes por hora. El *boosting* comete menos error que el perceptrón
en el 52,1 % de las horas. Ridge queda tercero en MAE en los tres escenarios. Con 168 horas, el perceptrón obtiene
el menor RMSE (138,71) y el menor MAE en horas pico (169,58). El RMSE de Ridge (140,95) también queda por debajo
del del *boosting* (141,78).

La Tabla 6.3 recoge los tres contrastes de Diebold-Mariano fijados de antemano, uno por retraso.

**Tabla 6.3.** *Boosting* frente al ingenuo semanal: contraste de Diebold-Mariano con pérdida absoluta (varianza de
Newey-West con 24 rezagos; valores p corregidos por Holm; intervalo del 95 % de la diferencia de MAE calculado con
el mismo error estándar).

| Retraso | Diferencia de MAE (viajes/h) | Intervalo del 95 % | Diferencia relativa | Estadístico DM | Valor p corregido | Horas en que gana el *boosting* |
|---|---|---|---|---|---|---|
| 1 h | −73,21 | −84,75 a −61,67 | −70,15 % | −12,44 | 4,96 × 10⁻³⁵ | 77,62 % |
| 24 h | −26,07 | −35,98 a −16,17 | −24,99 % | −5,16 | 4,95 × 10⁻⁷ | 61,05 % |
| 168 h | −14,92 | −23,98 a −5,86 | −14,30 % | −3,23 | 1,25 × 10⁻³ | 53,91 % |

Las cuatro horas excluidas de la prueba se tratan en el contraste como huecos de la rejilla horaria: no aportan
ningún producto a las autocovarianzas, de modo que no se emparejan como contiguas horas que no lo son.

En los tres escenarios el *boosting* comete significativamente menos error que el ingenuo, incluso después de la
corrección por comparaciones múltiples. La ventaja relativa es del 70 % con datos de hace una hora, del 25 % con
datos de hace un día y del 14 % con datos de hace una semana. Esa disminución, que coincide con la hipótesis 2, es
una comparación descriptiva entre los tres contrastes: no se contrastó formalmente que las ventajas sean distintas
entre sí. Con una semana de retraso, el *boosting* gana en algo más de la mitad de las horas.

Las diferencias de pérdida de horas cercanas están muy correlacionadas (entre 0,84 y 0,86 con una hora de desfase)
y, en el escenario de 1 hora, también a 168 horas (0,49), por el ciclo semanal. Por eso se repitieron los contrastes
con más rezagos en la varianza de Newey-West (Tabla 6.4).
El estadístico cambia, pero las tres diferencias siguen siendo significativas con cualquiera de las cuatro opciones.

**Tabla 6.4.** Sensibilidad del contraste al número de rezagos de Newey-West (estadístico DM; entre paréntesis, valor
p corregido por Holm).

| Rezagos | 1 h | 24 h | 168 h |
|---|---|---|---|
| 24 (principal) | −12,44 (4,96 × 10⁻³⁵) | −5,16 (4,95 × 10⁻⁷) | −3,23 (1,25 × 10⁻³) |
| 48 | −10,94 (2,35 × 10⁻²⁷) | −4,67 (5,94 × 10⁻⁶) | −2,90 (3,78 × 10⁻³) |
| 168 | −10,62 (7,08 × 10⁻²⁶) | −4,53 (1,20 × 10⁻⁵) | −2,92 (3,49 × 10⁻³) |
| 336 | −9,04 (4,73 × 10⁻¹⁹) | −4,47 (1,56 × 10⁻⁵) | −3,11 (1,84 × 10⁻³) |

Incluso con 168 horas, los modelos ajustados superan al ingenuo semanal. Disponen de la misma información reciente
que él, el conteo de hace una semana, y además de la media de las 24 horas que terminan en ese conteo y del
calendario (feriados, perfil horario por tipo de día, mes). El experimento no aísla cuál de esas entradas explica la
ventaja. Los feriados son el 3,4 % de las horas de prueba y concentran el 8,3 %, el 17,9 % y el 29,6 % de la
ventaja total del *boosting* sobre el ingenuo con 1, 24 y 168 horas, respectivamente.

## 6.4. Dónde se concentran los errores

La Figura 6.3 muestra el error por hora del día con 24 horas de retraso. Todos los métodos siguen el mismo patrón:
error mínimo de madrugada, cuando casi no hay viajes, y máximo entre las 16:00 y las 18:00, cuando la demanda es mayor
y más variable. En las horas pico, el MAE del *boosting* pasa de 48,2 viajes con datos frescos a 150,9 con 24 horas
de retraso.

{{FIGURA:05_mae_por_hora}}

La Tabla 6.5 separa el error por tipo de día. Los sábados son el tipo de día con menor MAE para todos los métodos en
los tres retrasos. En feriados, el ingenuo semanal comete 211,7 viajes por hora de error, aproximadamente el doble
que en los domingos ordinarios (100,0), probablemente porque copia un día normal de la semana anterior. La mediana
de calendario, que trata los feriados como domingos, los pronostica mejor que el ingenuo, pero falla en los
laborables (126,4).

**Tabla 6.5.** MAE de prueba por tipo de día, en viajes por hora (2.924 horas laborables, 600 de sábado, 576 de
domingo y 144 de feriado).

| Método | Laborable 1 h | Laborable 24 h | Laborable 168 h | Sábado 24 h | Domingo 24 h | Feriado 24 h |
|---|---|---|---|---|---|---|
| Ingenuo semanal | 107,00 | 107,00 | 107,00 | 69,88 | 100,01 | 211,70 |
| Mediana de calendario | 126,37 | 126,37 | 126,37 | 68,62 | 80,00 | 120,41 |
| Ridge | 37,45 | 94,64 | 100,16 | 62,12 | 76,41 | 89,91 |
| *Boosting* | 32,97 | 82,60 | 96,73 | 57,97 | 78,58 | 74,17 |
| Perceptrón | 36,43 | 85,47 | 97,54 | 59,66 | 77,38 | 86,25 |

El sesgo medio de todos los métodos es negativo (Tabla 6.1), y el de los tres modelos ajustados crece con el
retraso: con una semana de antigüedad, el *boosting* subestima en promedio unos 30 viajes por hora. El periodo de
prueba incluye la primavera de 2025, con octubre como el mes de más viajes de toda la serie; una explicación
posible es que un modelo que solo conoce conteos de hace una semana llega tarde a ese crecimiento.

## 6.5. Tercera pregunta: el clima retrospectivo

La Figura 6.4 compara el *boosting* con y sin la temperatura y la precipitación de ERA5 de la hora pronosticada.

{{FIGURA:06_efecto_del_clima}}

Con datos de hace una hora, añadir el clima apenas cambia el error, que pasa de 31,15 a 30,21 viajes por hora
(−3,0 %). Con 24 horas pasa de 78,28 a 59,33 (−24,2 %), y con 168 horas, de 89,44 a 65,29 (−27,0 %). La Tabla
6.6 separa las horas con y sin lluvia.

**Tabla 6.6.** MAE del *boosting* con y sin clima, por tipo de hora (484 horas con lluvia y 3.760 secas).

| Retraso | Con lluvia: sin clima | Con lluvia: con clima | Secas: sin clima | Secas: con clima | Parte de la reducción total aportada por las horas secas |
|---|---|---|---|---|---|
| 1 h | 37,75 | 37,36 | 30,30 | 29,29 | 95,16 % |
| 24 h | 149,90 | 83,67 | 69,06 | 56,19 | 60,15 % |
| 168 h | 152,07 | 86,11 | 81,37 | 62,61 | 68,85 % |

Con 24 o 168 horas de retraso, la mejora por hora es mucho mayor en las horas de lluvia (unos 66 viajes menos
de error) que en las secas (13 a 19). Pero como las horas secas son muchas más, aportan la mayor parte de la
reducción total. Una explicación plausible es que, cuando el último conteo es de hace una hora, ya refleja las
condiciones del momento, incluida la lluvia, y cuando es de ayer el modelo no tiene forma de conocerlas; el clima
suple en parte esa falta.

Este resultado debe leerse con cuidado. ERA5 se publica después de la hora pronosticada, así que estas cifras miden
cuánto cambia el error al conocer el clima real de la hora objetivo, con la configuración elegida para el modelo sin
clima. No dicen lo que se lograría con un pronóstico meteorológico emitido antes de la hora, que tendría sus propios
errores; Wessel (2020) estudió precisamente el uso de pronósticos meteorológicos para predecir el uso de
bicicletas. Medir ese caso queda como trabajo futuro.

## 6.6. Coherencia entre validación y prueba

Los errores de prueba son parecidos a los de validación (Tabla 5.4). El *boosting* obtuvo 31,65, 72,54 y 86,96 en
validación, y 31,15, 78,28 y 89,44 en prueba. El orden entre los modelos ajustados se mantiene con 1 y 24 horas.
Con 168 horas, el perceptrón quedó primero en validación (86,31 frente a 86,96 del *boosting*) y segundo en prueba
(89,61 frente a 89,44). Entre las referencias, la mediana de calendario obtuvo un MAE menor en validación (105,43
frente a 106,63) y mayor en prueba (111,71 frente a 104,36), probablemente por el aumento de la demanda del segundo
semestre. La evaluación abarca un solo semestre de prueba y el orden podría variar en otros periodos.
