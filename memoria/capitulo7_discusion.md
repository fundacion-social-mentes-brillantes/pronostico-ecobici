# 7. Discusión

## 7.1. La frescura del dato pesó más que el modelo

El resultado más claro del trabajo no es qué modelo gana, sino cuánto importó tener el dato reciente. Con el conteo
de hace una hora, la diferencia entre el mejor y el peor de los modelos ajustados fue de unos 4 viajes por hora
(31,2 frente a 34,9), alrededor de un 10 % del error. En cambio, para un mismo modelo, pasar de una hora a un día de
retraso multiplicó el error por dos y medio (el *boosting* pasó de 31,2 a 78,2). En este sistema y este periodo,
elegir entre modelos competentes movió el error en torno a un 10 %, mientras que perder la hora más reciente lo
empeoró en un 150 %.

Una explicación plausible está en la propia serie. Su autocorrelación con un desfase de una hora es de 0,93 (sección
4.4.3): la hora anterior se parece mucho a la actual, y es probable que en ella se reflejen el nivel de uso de esos
días y condiciones del momento como la lluvia. Con 24 horas de retraso esa información deja de estar disponible y los
modelos se apoyan en el calendario y en el nivel de días anteriores. El experimento muestra el efecto conjunto, pero
no aísla qué parte corresponde a cada uno de esos factores.

Para quien opera un sistema de este tipo, el resultado sugiere que tener los conteos al día importa más que elegir
entre modelos competentes. No se evaluó cuánto costaría conseguir datos más frescos ni si compensaría. El análisis
secundario sugiere, además, que la información meteorológica podría recuperar parte de lo que se pierde con datos
atrasados, algo que habría que comprobar con pronósticos reales.

## 7.2. Por qué los modelos superan al ingenuo incluso con una semana de retraso

Con 168 horas, el ingenuo semanal y los modelos ajustados disponen del mismo conteo reciente, y aun así el *boosting*
reduce el error un 14 %, con una diferencia significativa. Los modelos reciben además el calendario y la media de las
24 horas que terminan en ese conteo. El calendario parece ser una fuente importante de la ventaja: el ingenuo trata
un feriado como el día normal de la semana anterior, y por eso su error en los feriados (211,7 viajes por hora)
duplica el de los domingos ordinarios (100,0); los feriados son solo el 3,4 % de las horas de prueba, pero concentran
el 29 % de la ventaja del *boosting* con 168 horas. Probablemente influye también que los modelos combinan el último
dato con el patrón típico de esa hora y ese tipo de día, mientras que el ingenuo lo copia tal cual, aunque sea una
hora atípica.

La mediana de calendario muestra el extremo opuesto: se apoya solo en el patrón histórico y nada en el dato reciente.
Su sesgo medio de −33 viajes por hora apunta al problema: el nivel de uso cambia de un año a otro (2023 tuvo un 10 %
menos de viajes que 2022, y 2024 un 23 % más que 2023), y una mediana calculada con tres años y medio (enero de 2022 a
junio de 2025) probablemente no recoge esos cambios de nivel, aunque el experimento no aísla esa causa. Las dos referencias fallan por razones opuestas; los modelos
ajustados combinan ambas fuentes de información.

## 7.3. Comparación con la literatura

Los resultados son coherentes con la bibliografía consultada. Torres et al. (2024) encontraron en Nueva York que el
bosque aleatorio, el *gradient boosting* y una red neuronal alcanzan precisiones parecidas, y aquí ocurrió algo
similar: el *boosting* y el perceptrón quedaron a un viaje por hora con 24 horas de retraso y a 0,19 con 168. También
coinciden con Grinsztajn et al. (2022), según quienes los modelos de árboles siguen siendo muy competitivos en datos
tabulares: el *boosting* obtuvo el menor MAE con 1 y 24 horas y quedó a 0,19 del perceptrón con 168, con un ajuste
más rápido que el de la red.

Las cifras absolutas no son comparables con las de los estudios que usan el conjunto de Washington. Brajevic et al.
(2026), por ejemplo, reportan un coeficiente de determinación de 0,955 con repartos aleatorios de las horas y
destacan la hora del día y la temperatura entre sus variables más importantes. Un reparto aleatorio deja que el
modelo vea horas posteriores a las que pronostica, como se discutió en el capítulo 2, y su diseño de variables es
distinto del de este trabajo. Lo que sí muestran los escenarios de 24 y 168 horas es cuánto puede crecer el error
cuando la información no está al día, algo que una evaluación con repartos aleatorios no permite ver.

Respecto al clima, Wessel (2020) estudió el uso de pronósticos meteorológicos para predecir el uso de bicicletas.
Este trabajo no usó pronósticos sino el clima observado, de modo que su resultado describe cuánto cambia el error al
conocer el clima real de la hora pronosticada. Lo que aportaría un pronóstico meteorológico real, con sus errores, no
se midió.

## 7.4. Limitaciones

El trabajo tiene límites que conviene tener presentes al interpretar sus resultados:

1. **Un solo periodo de prueba.** Se evaluó un semestre (julio a diciembre de 2025). La coherencia con la
   validación ayuda, pero otro periodo, por ejemplo uno con un cambio de tarifas o de flota, podría dar cifras
   distintas.
2. **Retrasos simulados.** Los tres escenarios son condiciones experimentales; no se midió cuándo recibe realmente
   el operador sus conteos.
3. **El coste del retraso incluye el reajuste.** Cada escenario tiene su propia búsqueda de configuraciones, así que
   el aumento del error mide el escenario completo y no solo la antigüedad del dato. Además, con 168 horas,
   `ultimo_conteo` y `semana_anterior` son la misma columna; en Ridge eso cambia la penalización efectiva de esa
   señal y en el perceptrón le da dos pesos.
4. **Pronóstico agregado.** Se pronostican los viajes de toda la red. Las decisiones de redistribución se toman por
   estación y requerirían además datos de llegadas e inventario.
5. **Clima retrospectivo.** El efecto del clima se midió con observaciones publicadas después de la hora pronosticada,
   y con la configuración elegida para el modelo sin clima.
6. **Contrastes limitados.** Solo se contrastó el *boosting* frente al ingenuo. El orden entre los modelos ajustados y
   la disminución de la ventaja con el retraso son descriptivos.
7. **Parada temprana aleatoria del perceptrón.** El control interno de scikit-learn separa al azar el 10 % de las filas
   de ajuste, de modo que puede mezclar horas cercanas entre entrenamiento y control. Habría sido preferible un tramo
   final cronológico. No se cambió después de ver la prueba para no contaminarla.
8. **Una sola semilla para el perceptrón.** El resultado de una red depende de su inicialización. No se repitió con
   varias semillas, de modo que la mínima diferencia con el *boosting* con 168 horas podría invertirse.
9. **Búsqueda de configuraciones pequeña.** Se probaron entre 4 y 6 configuraciones por modelo. Una búsqueda más
   amplia podría mejorar algo cada modelo; por el tamaño relativo de los efectos, es poco probable que cambie la
   conclusión principal, pero no se comprobó.
10. **Reglas de calidad decididas con la serie completa.** Las reglas de cobertura se fijaron antes de entrenar y sin
    mirar errores, pero mirando la serie completa, incluido el periodo de prueba. La regla de las rachas de ceros,
    además, mira horas posteriores; en la prueba no tuvo efecto (sección 4.3).
11. **Familias no exploradas.** No se probaron modelos de secuencias ni modelos que usen la relación entre estaciones,
    que la literatura reciente explora (Jiang, 2022).
12. **Calidad de los datos publicados.** La inconsistencia de los recorridos cortos de 2024 se resolvió con una regla
    razonable, pero se desconoce el filtro exacto que aplica el publicador en los demás años, y no se midió cuánto
    cambiarían la serie y la comparación con otro umbral.
