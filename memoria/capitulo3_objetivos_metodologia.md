# 3. Objetivos concretos y metodología de trabajo

## 3.1. Objetivo general

Medir de forma experimental cómo cambia el error de distintas técnicas de aprendizaje automático al pronosticar los viajes horarios de Ecobici Buenos Aires cuando los conteos más recientes llegan con retraso, e identificar cuál conviene en cada escenario. La comparación se refiere a los viajes iniciados en toda la red y a las condiciones, el periodo y las horas válidas del estudio.

## 3.2. Objetivos específicos

1. Construir y documentar, a partir de los registros públicos de 2022-2025, una serie de viajes iniciados por hora, acompañada de un informe de cobertura.
2. Implementar cinco alternativas de pronóstico mediante un mismo protocolo de evaluación temporal.
3. Evaluar las alternativas con retrasos de 1, 24 y 168 horas sobre un periodo de prueba reservado desde el inicio.
4. Analizar los errores por franja horaria, tipo de día y horas con precipitación, y estimar en un análisis secundario el aporte del clima observado.
5. Resumir qué alternativa conviene según la antigüedad de los conteos, dentro del sistema y el periodo evaluados.

## 3.3. Preguntas de investigación e hipótesis

**P1.** ¿Qué técnica obtiene el menor error absoluto medio cuando el último conteo tiene una hora de antigüedad? Se plantea como hipótesis que será el modelo de *boosting* de árboles. La hipótesis se valoró frente a las cuatro alternativas restantes sobre las mismas horas válidas, de forma descriptiva salvo frente al ingenuo semanal, que es el único contraste formal predefinido; no se presupone que la diferencia sea necesariamente relevante en términos prácticos.

**P2.** ¿Cuánto cambia el error absoluto medio de cada técnica con retrasos de 24 y 168 horas, y cambia la alternativa que conviene? Se plantea que la ventaja del *boosting* sobre las referencias simples se reducirá al aumentar la antigüedad de los conteos. Para responder se comparó cada método entre escenarios y también se examinó el orden de los métodos en cada uno. La mediana de calendario es una referencia particular porque no utiliza conteos recientes y sus predicciones no dependen del retraso simulado.

**P3.** Como pregunta secundaria, ¿cambia el error del *boosting* al añadir el clima observado de ERA5, también en las horas con precipitación? Se comparan las variantes con y sin temperatura y precipitación de la hora objetivo. No se establece una hipótesis direccional adicional. Puesto que el reanálisis se publica después de la hora pronosticada, la comparación mide el aporte de información retrospectiva y no el rendimiento con un pronóstico meteorológico disponible en tiempo real.

## 3.4. Metodología

### 3.4.1. Tipo de trabajo y fases

Se realizó una comparativa empírica de soluciones, correspondiente al tipo 3 del trabajo fin de máster. Las alternativas se aplicaron a un mismo problema y se evaluaron con criterios y periodos comunes. El propósito es medir diferencias observadas bajo restricciones de disponibilidad predefinidas, no demostrar una superioridad general de una familia de modelos.

El trabajo se organizó en cinco fases. Primero se obtuvieron y revisaron las fuentes públicas, se construyó la serie y se documentó su cobertura. Después se fijaron las variables, los escenarios, las particiones, los criterios de exclusión y las métricas. En la tercera fase se implementaron las referencias y los modelos. La cuarta comprendió la búsqueda de hiperparámetros en validación y la evaluación de la prueba reservada con el protocolo ya fijado (repetida después una vez, solo para comprobar la reproducibilidad, con resultados idénticos). Por último, se analizaron los errores, las diferencias entre escenarios y el contraste predefinido, con atención a las limitaciones de cobertura y de disponibilidad de información.

La evaluación sigue el orden temporal y recorre sucesivamente las horas objetivo, en consonancia con la evaluación de pronósticos fuera de muestra y con origen móvil (Tashman, 2000; Hyndman y Athanasopoulos, 2021). La elección de modelos se efectuó sin consultar los errores de la prueba. Los resultados se conservaron en forma de predicciones y métricas para permitir su revisión posterior.

### 3.4.2. Datos y definición del problema

Se utilizaron los recorridos públicos de Ecobici correspondientes a 2022-2025 (Gobierno de la Ciudad de Buenos Aires, s. f.). El objetivo $y_t$ fue el número de viajes iniciados en $[t,t+1)$, en hora local, para toda la red. Al comienzo de cada hora $t$ se pronosticó su total. La serie tuvo una observación por hora; las horas de cobertura dudosa se representaron como faltantes, mientras que el cero se conservó en las horas sin indicios de fallo y sin ningún inicio observado.

Se descartaron los recorridos de menos de 60 segundos para homogeneizar los años: 2024 contenía 321.015, frente a ninguno en 2022 y 2023 y ocho en 2025. Se marcaron como cobertura dudosa las rachas de cuatro o más horas sin viajes y las horas sin viajes entre las 7:00 y las 21:59 (21 horas en total); se descartó la regla de días con muy pocos viajes porque solo señalaba feriados y días de lluvia (véase el capítulo 4).

Se simularon tres escenarios $d\in\{1,24,168\}$. En cada uno, el conteo más reciente permitido al pronosticar $y_t$ fue $y_{t-d}$. Ninguna variable de conteo incorporó observaciones posteriores a ese límite. Aquí $d$ mide el desfase entre el inicio de la hora pronosticada y el inicio de la hora del último conteo permitido: con $d=1$, ese conteo es el de la hora que acaba de cerrarse, es decir, se supone que llega sin demora; con $d=24$ y $d=168$ se simulan datos más antiguos. Visto desde el último conteo conocido, el objetivo se encuentra a $d$ pasos horarios. Estas antigüedades son condiciones experimentales y no se atribuyen como latencias reales de publicación de la fuente.

Las variables de calendario fueron la hora del día, el día de la semana, el mes, un indicador de feriado y otro de día no laborable. Además, se definió el tipo de día como laborable, sábado o domingo o feriado: en esa categoría, que usan Ridge y el perceptrón, un feriado se agrupó con los domingos y un día no laborable con los laborables, conservando ambos su indicador específico. La mediana de calendario también trata los feriados como domingos, mientras que el *boosting* recibe el día de la semana real junto con los indicadores (Tabla 5.2). Las fechas efectivas de feriados y días no laborables se construyeron a partir de la Ley 27.399 de 2017 y de las normas de traslado aplicables a cada año, registrando las fuentes correspondientes.

Las tres variables de conteo fueron: el último conteo disponible, $y_{t-d}$; la media de las 24 horas desde $y_{t-d-23}$ hasta $y_{t-d}$; y el conteo de la misma hora de la semana anterior, $y_{t-168}$. Para la media se exigieron al menos 18 valores válidos y, si se alcanzaba ese mínimo, se promediaban los disponibles; en otro caso fue faltante. Cuando $d=168$, el último conteo y el de la semana anterior coinciden. Se conservaron ambas variables tal como están definidas para mantener el protocolo común.

### 3.4.3. Alternativas y búsqueda de configuraciones

Se compararon cinco alternativas. El **ingenuo semanal** predice $y_{t-168}$. La **mediana de calendario** utiliza la mediana del bloque de ajuste para cada combinación de hora y día de la semana, considerando los feriados como domingo. Estas dos referencias permiten valorar el desempeño de los métodos ajustados frente a reglas sencillas; la segunda no depende de conteos recientes.

La **regresión Ridge** utilizó indicadores de las 72 combinaciones de hora y tipo de día, 12 indicadores mensuales, los indicadores de feriado y día no laborable y las tres variables de conteo. Estas últimas se transformaron mediante $\log(1+x)$ y se estandarizaron con parámetros calculados solo en el bloque de ajuste. El objetivo también se transformó con $\log(1+y)$. Las predicciones se devolvieron a la escala original mediante $\exp(x)-1$ y se recortaron en cero. Se compararon valores de $\alpha$ de 0,1, 1, 10 y 100; este parámetro regula la penalización de los coeficientes (Hoerl y Kennard, 1970).

El **boosting de árboles por histogramas** empleó hora, día de la semana y mes como variables categóricas, los dos indicadores de calendario y las tres variables de conteo transformadas con $\log(1+x)$. El objetivo y la transformación inversa fueron los mismos que en Ridge. Para cada escenario se probaron tasas de aprendizaje de 0,05 y 0,1 combinadas con 15, 31 y 63 hojas máximas, con 300 iteraciones máximas y la semilla del proyecto. El procedimiento de *gradient boosting* combina sucesivamente modelos para reducir la pérdida (Friedman, 2001).

El **perceptrón multicapa** utilizó las mismas entradas y el mismo preprocesamiento que Ridge. Se compararon las arquitecturas de una capa oculta de 64 unidades y de dos capas de 64 y 32 unidades, combinadas con penalizaciones $\alpha$ de $10^{-4}$ y $10^{-3}$. El máximo fue de 300 iteraciones; se activó la parada temprana y se fijó la semilla. El objetivo transformado también se estandarizó con parámetros calculados en el bloque de ajuste. La parada interna del ajuste no reemplaza la validación cronológica externa.

Como análisis secundario se añadió **boosting con clima**: la misma familia y configuración seleccionada para *boosting* en cada escenario, con temperatura y precipitación de la hora objetivo como entradas adicionales. No se efectuó una búsqueda independiente de sus hiperparámetros. Las variables meteorológicas proceden del producto ERA5 accesible mediante Open-Meteo (Zippenfenig, 2023). Esta variante no forma parte de las cinco alternativas operativas principales, porque utiliza información retrospectiva.

La búsqueda de hiperparámetros se realizó por escenario y se eligió la configuración con menor MAE en validación. Las filas de ajuste sin objetivo o sin alguna de las variables necesarias se descartaron. Se utilizaron las mismas filas para *boosting* que para Ridge, aunque la implementación de árboles pueda admitir faltantes, para mantener comparable el ajuste. Las transformaciones se aprendieron exclusivamente en el bloque de ajuste correspondiente y se aplicaron después sin incorporar información de los periodos evaluados.

### 3.4.4. Particiones y evaluación cronológica

El ajuste utilizado para elegir configuraciones comprendió desde el 1 de enero de 2022 hasta el 31 de diciembre de 2024. La validación abarcó desde el 8 de enero hasta el 30 de junio de 2025. Los siete días anteriores a la primera predicción de validación constituyen el margen respecto al final del bloque de ajuste. La validación permitió elegir los hiperparámetros de cada escenario mediante el menor MAE, sin utilizar el periodo de prueba.

Una vez elegidas las configuraciones, se realizó el ajuste final con el periodo del 1 de enero de 2022 al 30 de junio de 2025. La mediana de calendario se recalculó con ese mismo bloque. La prueba comenzó el 8 de julio y terminó el 31 de diciembre de 2025, tras otro margen de siete días. Los modelos y las transformaciones quedaron congelados durante toda la prueba. Se recorrieron las horas en orden y se usaron como entradas los conteos reales que ya estaban permitidos por cada valor de $d$. Incorporar esas observaciones disponibles a las variables no constituye reentrenamiento.

Para comparar métodos y retrasos se utilizó una única intersección de horas de prueba: aquellas con objetivo válido y todas las variables de los tres escenarios válidas. De las 4.248 horas posteriores al margen se excluyeron cuatro por faltantes: una por el objetivo y tres por variables de conteo, todas alrededor del corte del 14 de octubre de 2025. La muestra común quedó en 4.244 horas. Así, una diferencia de error no se explica simplemente porque dos métodos se hayan evaluado en horas distintas. Los resultados representan esa muestra común, por lo que las exclusiones deben considerarse al interpretar su alcance.

### 3.4.5. Métricas, análisis y contraste

El criterio principal fue el error absoluto medio o MAE, expresado en viajes por hora. Se informaron también la raíz del error cuadrático medio o RMSE y el sesgo, definido como la media de predicho menos real. El primero da más peso a errores grandes; el segundo muestra la dirección media de las desviaciones, aunque puede ocultar compensaciones entre sobreestimaciones y subestimaciones (Hyndman y Koehler, 2006).

Para cada método y escenario se calcularon, además, el número de horas y los tiempos de ajuste y predicción medidos en el mismo equipo. Se comunicó el cambio de MAE de cada método con respecto a su propio resultado con $d=1$. Las horas pico fueron las seis horas del día con mayor media de viajes en días laborables del bloque 2022-2024, definidas antes de la prueba. Se calculó el MAE en esas horas y en las horas con precipitación mayor que cero. También se examinaron errores por hora y tipo de día, sin interpretar los resultados por subgrupos sin considerar su tamaño.

Se predefinieron tres contrastes de Diebold-Mariano: *boosting* frente al ingenuo semanal, uno por cada retraso, con pérdida absoluta en las horas comunes (Diebold y Mariano, 1995). La varianza de largo plazo se estimó mediante Newey-West con núcleo de Bartlett y 24 rezagos (Newey y West, 1987); se utilizó el estadístico normal asintótico. Los tres valores p se corrigieron mediante Holm (Holm, 1979). Se informó también la diferencia de MAE en viajes por hora y en porcentaje. Si los huecos o la dependencia impedían sostener el contraste, las diferencias se presentaban como descriptivas, sin atribuirles significación estadística.

El análisis del clima comparó *boosting* con y sin las dos variables retrospectivas por retraso y en horas con precipitación. La temperatura corresponde al comienzo del intervalo y la precipitación a lo acumulado durante él. Por ejemplo, para 10:00-11:00 se asociaron la temperatura de las 10:00 y la precipitación etiquetada por la API a las 11:00, que acumula la hora anterior. Se registraron las coordenadas de la celda fija, la consulta y la fecha de extracción. Una mejora, si se observaba, no se interpretaba como mejora alcanzable con previsiones meteorológicas reales.

## 3.5. Herramientas y reproducibilidad

Se utilizó Python para la preparación, el ajuste y la evaluación. pandas permitió manipular las series y scikit-learn proporcionó las implementaciones de Ridge, *boosting* por histogramas y perceptrón multicapa, así como las transformaciones necesarias (Pedregosa et al., 2011). DuckDB permitió cargar y agregar los recorridos mediante SQL (Raasveldt y Mühleisen, 2019). Se empleó matplotlib para representar los resultados, y el contraste de Diebold-Mariano se implementó directamente con NumPy conforme al protocolo.

El repositorio Git conserva los scripts y su evolución. Se fijó una semilla para los procedimientos que la admitan y se documentaron configuraciones, particiones y transformaciones. Los datos se descargaron mediante un script; se conservaron las consultas y la información necesaria para identificar las versiones obtenidas. Se guardaron las predicciones por hora, los hiperparámetros elegidos, las métricas, las exclusiones y los resultados de los contrastes. Esta trazabilidad permitió reconstruir las decisiones del análisis, aunque la reproducción exacta también depende de que las fuentes y el entorno permanezcan disponibles.

## 3.6. Datos y aspectos éticos y legales

Se emplearon únicamente datos públicos. Los recorridos de Ecobici se atribuyeron al Gobierno de la Ciudad de Buenos Aires conforme a la licencia CC BY 2.5 Argentina, indicando su depuración y agregación horaria. Los datos meteorológicos se atribuyeron a Open-Meteo y Copernicus conforme a CC BY 4.0. Las fechas de feriados y días no laborables procedieron de normativa pública y se documentaron los traslados aplicables.

Las columnas del usuario nunca se seleccionaron. La consulta se limitó al identificador del recorrido, las fechas y horas de salida y llegada y las estaciones, necesarios para contar inicios y controlar la calidad; el archivo publicado se descomprimió temporalmente y se borró al terminar, y el conjunto analítico contuvo solo conteos agregados por hora. No se realizaron encuestas ni se recabaron datos personales. La agregación no permite responder preguntas sobre personas individuales ni sobre trayectos entre estaciones.

## 3.7. Planificación de referencia

Como referencia para un trabajo de este tipo, la planificación se distribuye en cuatro meses. En este caso, asistentes de IA realizaron la ejecución en mucho menos tiempo (véase el Anexo A). Los controles de cobertura y el cierre del diseño preceden al ajuste; la prueba reservada se realiza después de elegir las configuraciones.

| Mes | Actividades | Entrega prevista |
|---|---|---|
| 1 | Estado del arte, revisión de cobertura, construcción de la serie, comprobación de los tres cortes de disponibilidad en una muestra de entrenamiento y formulación de objetivos. | Primera entrega. |
| 2 | Implementación de las cinco alternativas, validación y cierre de métricas y configuraciones. | Modelos y protocolo de validación preparados. |
| 3 | Prueba reservada, análisis de errores y diferencias entre escenarios, y análisis secundario del clima. | Segunda entrega. |
| 4 | Discusión, conclusiones, revisión de citas y formato, y preparación de la defensa. | Tercera entrega y predepósito. |
