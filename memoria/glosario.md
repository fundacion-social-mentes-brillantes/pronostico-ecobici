# Anexo F. Glosario

**Autocorrelación.** Medida de cuánto se parece una serie a sí misma desplazada en el tiempo. Vale 1 si la serie se
repite exactamente y 0 si no hay relación.

**Boosting (gradient boosting).** Técnica que construye muchos árboles de decisión pequeños, uno detrás de otro;
cada árbol nuevo intenta corregir los errores que dejaron los anteriores (Friedman, 2001). La versión «por
histogramas» agrupa los valores de cada variable en intervalos para acelerar el ajuste.

**Cobertura dudosa.** Hora en la que el registro de viajes probablemente falló (un corte del servicio o del sistema
de registro). En este trabajo, esas horas se tratan como desconocidas y no como cero.

**Diebold-Mariano (prueba de).** Contraste estadístico que compara la precisión de dos pronósticos sobre las mismas
horas, a partir de la diferencia entre sus errores (Diebold y Mariano, 1995). Responde a la pregunta de si la
diferencia observada podría deberse al azar.

**ERA5.** Reanálisis meteorológico de Copernicus: una reconstrucción del clima pasado, hora por hora, hecha después
de los hechos con observaciones y modelos. Por eso no estaba disponible en el momento de pronosticar.

**Escenario de retraso (d).** Antigüedad del último conteo de viajes que el modelo puede usar al pronosticar: 1, 24 o
168 horas.

**Evaluación cronológica (origen móvil).** Forma de evaluar pronósticos en la que el modelo solo conoce el pasado de
cada hora que pronostica, como ocurriría en la realidad (Tashman, 2000; Hyndman y Athanasopoulos, 2021). Se opone al
reparto aleatorio de las horas entre entrenamiento y prueba.

**Holm (corrección de).** Ajuste de los valores p cuando se hacen varios contrastes a la vez, para no encontrar
diferencias «significativas» por pura casualidad (Holm, 1979).

**Hiperparámetro.** Ajuste de un modelo que no se aprende de los datos sino que se elige antes, como la penalización
de Ridge o el número de hojas de los árboles. Aquí se eligieron con el periodo de validación.

**Ingenuo semanal.** Pronóstico de referencia que repite el valor de la misma hora de la semana anterior.

**MAE (error absoluto medio).** Promedio de las diferencias, sin signo, entre lo pronosticado y lo real. Aquí se mide
en viajes por hora y es el criterio principal.

**Mediana de calendario.** Pronóstico de referencia que usa el valor típico (la mediana) de cada combinación de hora y
día de la semana en el historial; los feriados cuentan como domingo.

**Newey-West (varianza de).** Forma de calcular la incertidumbre de un promedio cuando los datos de horas cercanas
están relacionados entre sí (Newey y West, 1987). Se usa dentro de la prueba de Diebold-Mariano.

**Perceptrón multicapa.** Red neuronal sencilla: varias capas de unidades que combinan las variables de entrada y les
aplican transformaciones no lineales; se ajusta con retropropagación (Rumelhart et al., 1986).

**Ridge (regresión).** Regresión lineal con una penalización que impide coeficientes demasiado grandes; es útil cuando
hay variables parecidas entre sí (Hoerl y Kennard, 1970).

**RMSE (raíz del error cuadrático medio).** Medida de error que castiga más los errores grandes que el MAE.

**Sesgo.** Promedio de lo pronosticado menos lo real. Si es negativo, el método se queda corto en promedio.

**Validación y prueba.** Dos periodos reservados: la validación sirve para elegir las configuraciones; la prueba, al
final, para medir el resultado con datos que no intervinieron en ninguna decisión.
