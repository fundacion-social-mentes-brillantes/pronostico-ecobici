# 8. Conclusiones y trabajo futuro

## 8.1. Conclusiones

El objetivo general era medir cómo cambia el error de distintas técnicas de aprendizaje automático al pronosticar
los viajes horarios de Ecobici Buenos Aires cuando los conteos más recientes llegan con retraso, e identificar cuál
conviene en cada escenario. Los cinco objetivos específicos se cumplieron:

1. Se construyó una serie horaria de 35.064 horas con 11.936.199 recorridos depurados de 2022 a 2025, con un informe
   de cobertura y un recuento por motivo de depuración. En el proceso se detectó una inconsistencia de los datos
   publicados: el archivo de 2024 incluye 321.015 recorridos de menos de un minuto, frente a ninguno en 2022 y 2023 y
   8 en 2025, y se igualaron los años con un mismo umbral.
2. Se implementaron las cinco alternativas con un protocolo común, verificado con pruebas automáticas que comprueban,
   entre otras cosas, que ninguna variable de conteo tome valores posteriores al corte de su escenario (la marca de
   cobertura, que es retrospectiva, se discute en la sección 4.3).
3. Se evaluaron en los tres escenarios sobre 4.244 horas de prueba reservadas desde el inicio.
4. Se analizaron los errores por franja horaria, tipo de día y lluvia, y se estimó el efecto del clima observado.
5. Se obtuvo una pauta clara, dentro del sistema y el periodo evaluados, sobre qué conviene según la antigüedad de
   los datos.

Las respuestas a las preguntas de investigación son:

- **P1.** Con el último conteo de hace una hora, el *boosting* de árboles obtuvo el menor error (31,2 viajes por
  hora, un 8,3 % del nivel medio), seguido muy de cerca por el perceptrón (33,2) y por Ridge (34,9). Este orden es
  descriptivo.
- **P2.** El retraso fue el factor dominante. Con un día de antigüedad, el error de los tres modelos ajustados se
  multiplicó por entre 2,4 y 2,5, y con una semana, por entre 2,7 y 2,9. En cada escenario el *boosting* cometió
  significativamente menos error que la referencia ingenua, con una ventaja del 70 %, el 25 % y el 14 %; esa
  disminución entre escenarios es descriptiva. Con un día de retraso el *boosting* tuvo el menor error; con una
  semana quedó a 0,19 viajes por hora del perceptrón.
- **P3.** El clima observado casi no cambió el error con el dato fresco (−4,7 %) y lo redujo mucho con datos
  antiguos (−25 % con 24 horas y −28 % con 168). Con 24 y 168 horas, la mejora por hora fue mucho mayor en las horas
  de lluvia, aunque, por ser más numerosas, las horas secas aportaron la mayor parte de la reducción total. Como el clima usado es
  retrospectivo, estas cifras no equivalen a lo que aportaría un pronóstico meteorológico.

En el sistema, el periodo y las alternativas evaluadas, la frescura de los datos importó bastante más que la
elección entre modelos competentes. Con el dato reciente, un modelo de *boosting* dio un error de alrededor del 8 %
del nivel medio; sin él, el error se multiplicó, y el análisis secundario sugiere estudiar fuentes de información
disponibles en tiempo real, como el pronóstico del tiempo, para compensarlo.

## 8.2. Trabajo futuro

- **Pronósticos meteorológicos reales.** Repetir el análisis secundario con pronósticos emitidos antes de la hora
  objetivo, en lugar del clima observado, para medir el aporte real del clima con datos atrasados.
- **Aislar el efecto de cada entrada.** Comparar variantes que retiren por separado el último conteo, la media de
  24 horas y el calendario, y fijar la configuración entre escenarios para separar la antigüedad del dato del
  reajuste.
- **Más contrastes y más semillas.** Contrastar formalmente las diferencias entre modelos ajustados y entre
  escenarios, y repetir el perceptrón con varias semillas y una parada temprana cronológica.
- **Nivel de estación.** Llevar la comparación a estaciones o barrios, donde se toman las decisiones de
  redistribución, añadiendo llegadas e inventario.
- **Más periodos y otras ciudades.** Evaluar con origen móvil en varios semestres y repetir el protocolo con otros
  sistemas que publican sus recorridos.
- **Reentrenamiento periódico.** Comparar los modelos congelados con versiones que se reentrenan cada semana.
