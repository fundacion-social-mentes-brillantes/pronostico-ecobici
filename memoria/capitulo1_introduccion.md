# 1. Introducción

## 1.1. Motivación

Los sistemas públicos de bicicletas se han convertido en una pieza habitual del transporte urbano. Su operación
diaria depende de anticipar cuánta actividad habrá en las próximas horas: cuántas bicicletas saldrán, en qué
momentos del día se concentrará el uso y cuándo conviene programar tareas de redistribución. Por eso las revisiones
sobre aprendizaje automático en bicicletas compartidas recogen el pronóstico de la demanda entre sus aplicaciones
principales (Albuquerque et al., 2021; Jiang, 2022).

Al comparar modelos es fácil suponer, de forma implícita, que el último dato está siempre disponible: para
pronosticar la próxima hora se usaría el conteo de la hora que acaba de terminar. En la práctica no siempre es así. Los registros pueden consolidarse con horas o días de retraso, los sistemas de información pueden
fallar, y quien trabaja con datos abiertos los recibe en publicaciones periódicas. La pregunta que motiva este
trabajo es sencilla de formular y tiene consecuencias prácticas: **¿cuánto empeora cada técnica cuando el último
conteo disponible es antiguo, y cambia por ello la técnica que conviene usar?**

Una segunda motivación es metodológica. Algunos trabajos con el conjunto clásico de Washington evalúan los modelos
repartiendo las horas al azar entre entrenamiento y prueba (por ejemplo, Brajevic et al., 2026). Ese diseño permite
que el modelo aprenda de horas posteriores a las que luego pronostica, algo imposible en la operación real. La
evaluación cronológica, en la que el modelo solo conoce el pasado, es la forma correcta de responder a la pregunta
anterior (Tashman, 2000; Bergmeir y Benítez, 2012), y obliga a definir con precisión qué información existe en
cada momento.

## 1.2. Planteamiento del trabajo

El trabajo se sitúa en Ecobici, el sistema público de bicicletas de la Ciudad de Buenos Aires, que publica como
datos abiertos sus recorridos. A partir de los registros de 2022 a 2025 se construye una serie de viajes
iniciados por hora en toda la red, con casi 12 millones de recorridos depurados. Sobre esa serie se pronostica, al
comienzo de cada hora, cuántos viajes empezarán en esa hora.

Se comparan cinco alternativas de complejidad creciente: dos referencias simples (repetir lo ocurrido a la misma
hora de la semana anterior y la mediana histórica por hora y día de la semana), una regresión lineal regularizada
(Ridge), un modelo de árboles con *gradient boosting* y una red neuronal (perceptrón multicapa). Todas se evalúan en
tres escenarios de disponibilidad de datos, en los que el último conteo conocido tiene 1 hora, 24 horas o 168 horas
(una semana) de antigüedad. Como análisis secundario, se mide cuánto cambia el error del modelo de *boosting* si se
le añade el clima observado de la hora pronosticada.

El trabajo corresponde al tipo 3 de la titulación, **comparativa de soluciones**: no se construye una aplicación
nueva, sino que se comparan empíricamente técnicas existentes sobre un problema concreto, con datos reales y un
protocolo fijado antes de mirar los resultados. Se relaciona con las líneas de aprendizaje automático (los modelos
lineales y de árboles, la validación y el contraste de hipótesis) y de aprendizaje profundo (la red neuronal).

## 1.3. Aportación

La aportación del trabajo es triple:

1. **Una serie horaria depurada y documentada de Ecobici 2022-2025**, construida desde los registros originales con
   SQL. En el proceso se detectó una inconsistencia en los datos publicados: el archivo de 2024 incluye 321.015
   recorridos de menos de un minuto, frente a ninguno en 2022 y 2023 y 8 en 2025, que inflarían la demanda de ese
   año si no se filtraran.
2. **Una medición del coste del retraso**: para las mismas horas de prueba, cuánto aumenta el error de cada técnica
   al pasar de 1 a 24 y a 168 horas de antigüedad, y si cambia el orden entre ellas.
3. **Un protocolo de evaluación estrictamente cronológico y reproducible**: particiones con margen de siete días,
   modelos congelados en la prueba, horas evaluadas comunes a todas las alternativas, contraste de Diebold-Mariano
   con varianza robusta a la autocorrelación y corrección por comparaciones múltiples. Todo el código, los datos
   procesados y los resultados están disponibles en un repositorio público
   (https://github.com/fundacion-social-mentes-brillantes/pronostico-ecobici).

## 1.4. Estructura de la memoria

El capítulo 2 presenta el contexto de los sistemas de bicicletas compartidas, los conceptos de pronóstico y
disponibilidad de información, las técnicas comparadas y los estudios previos. El capítulo 3 formula los objetivos,
las preguntas de investigación y la metodología. El capítulo 4 describe los datos y su preparación. El capítulo 5
detalla el diseño concreto de la comparativa y su implementación. El capítulo 6 presenta los resultados, y el
capítulo 7 los discute y señala las limitaciones. El capítulo 8 recoge las conclusiones y las líneas de trabajo
futuro. Los anexos incluyen la declaración de uso de herramientas de inteligencia artificial, la guía para
reproducir los experimentos, tablas complementarias y un glosario de los términos técnicos.
