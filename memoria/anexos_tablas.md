# Anexo D. Búsqueda completa de configuraciones

Todas las configuraciones probadas en validación (8 de enero a 30 de junio de 2025), con su error. La marcada con «sí» es la elegida en cada método y escenario (menor MAE). Generada por `src/tablas_memoria.py` a partir de `resultados/metricas_validacion.csv`.

| Método | Retraso | Configuración | MAE | RMSE | Sesgo | Elegida |
|---|---|---|---|---|---|---|
| Ingenuo semanal | 1 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 1 h | — | 105,43 | 149,39 | −19,39 | sí |
| Ridge | 1 h | α 0,1 | 37,18 | 56,37 | −10,74 |  |
| Ridge | 1 h | α 1 | 37,17 | 56,37 | −10,74 | sí |
| Ridge | 1 h | α 10 | 37,24 | 56,50 | −10,78 |  |
| Ridge | 1 h | α 100 | 39,89 | 61,21 | −11,99 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 15 | 33,66 | 51,66 | −6,08 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 31 | 32,19 | 49,25 | −5,43 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 63 | 31,65 | 48,36 | −5,17 | sí |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 15 | 32,59 | 49,44 | −5,43 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 31 | 32,11 | 49,13 | −4,78 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 63 | 32,06 | 48,93 | −5,40 |  |
| Perceptrón | 1 h | capas ocultas 64; α 0,0001 | 33,02 | 50,01 | −5,61 |  |
| Perceptrón | 1 h | capas ocultas 64; α 0,001 | 33,00 | 50,00 | −5,84 |  |
| Perceptrón | 1 h | capas ocultas 64 y 32; α 0,0001 | 33,00 | 50,42 | −9,43 |  |
| Perceptrón | 1 h | capas ocultas 64 y 32; α 0,001 | 32,80 | 50,09 | −7,53 | sí |
| Ingenuo semanal | 24 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 24 h | — | 105,43 | 149,39 | −19,39 | sí |
| Ridge | 24 h | α 0,1 | 85,98 | 129,49 | −34,99 |  |
| Ridge | 24 h | α 1 | 85,89 | 129,57 | −35,10 |  |
| Ridge | 24 h | α 10 | 85,39 | 130,71 | −35,87 | sí |
| Ridge | 24 h | α 100 | 86,88 | 140,01 | −37,31 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 15 | 72,54 | 118,66 | −16,10 | sí |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 31 | 73,08 | 119,57 | −12,55 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 63 | 73,60 | 119,76 | −12,86 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 15 | 72,95 | 119,19 | −14,26 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 31 | 74,66 | 122,49 | −10,83 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 63 | 75,32 | 123,53 | −10,95 |  |
| Perceptrón | 24 h | capas ocultas 64; α 0,0001 | 80,80 | 124,60 | −21,98 |  |
| Perceptrón | 24 h | capas ocultas 64; α 0,001 | 79,74 | 123,89 | −19,15 |  |
| Perceptrón | 24 h | capas ocultas 64 y 32; α 0,0001 | 79,22 | 123,71 | −25,00 |  |
| Perceptrón | 24 h | capas ocultas 64 y 32; α 0,001 | 78,77 | 123,15 | −23,44 | sí |
| Ingenuo semanal | 168 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 168 h | — | 105,43 | 149,39 | −19,39 | sí |
| Ridge | 168 h | α 0,1 | 92,99 | 136,63 | −39,26 | sí |
| Ridge | 168 h | α 1 | 93,00 | 136,79 | −39,48 |  |
| Ridge | 168 h | α 10 | 93,14 | 138,51 | −41,18 |  |
| Ridge | 168 h | α 100 | 95,85 | 149,55 | −44,99 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 15 | 86,96 | 131,65 | −28,57 | sí |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 31 | 87,96 | 132,85 | −27,23 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 63 | 88,41 | 134,85 | −27,14 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 15 | 88,97 | 134,86 | −28,76 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 31 | 89,20 | 135,78 | −25,75 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 63 | 91,53 | 139,58 | −26,85 |  |
| Perceptrón | 168 h | capas ocultas 64; α 0,0001 | 86,37 | 130,08 | −25,74 |  |
| Perceptrón | 168 h | capas ocultas 64; α 0,001 | 86,31 | 129,99 | −25,80 | sí |
| Perceptrón | 168 h | capas ocultas 64 y 32; α 0,0001 | 90,39 | 135,41 | −36,49 |  |
| Perceptrón | 168 h | capas ocultas 64 y 32; α 0,001 | 90,96 | 135,44 | −30,87 |  |

# Anexo E. Viajes y horas de cobertura dudosa por mes

Generada a partir de `resultados/cobertura_mensual.csv`.

| Mes | Viajes válidos | Horas dudosas | Mes | Viajes válidos | Horas dudosas |
|---|---|---|---|---|---|
| 2022-01 | 191.864 | 0 | 2024-01 | 270.456 | 0 |
| 2022-02 | 219.116 | 0 | 2024-02 | 254.124 | 0 |
| 2022-03 | 266.859 | 0 | 2024-03 | 287.933 | 0 |
| 2022-04 | 253.607 | 0 | 2024-04 | 255.332 | 0 |
| 2022-05 | 227.669 | 0 | 2024-05 | 242.116 | 20 |
| 2022-06 | 189.364 | 0 | 2024-06 | 219.072 | 0 |
| 2022-07 | 177.903 | 0 | 2024-07 | 215.252 | 0 |
| 2022-08 | 271.953 | 0 | 2024-08 | 220.693 | 0 |
| 2022-09 | 303.989 | 0 | 2024-09 | 313.900 | 0 |
| 2022-10 | 284.004 | 0 | 2024-10 | 335.031 | 0 |
| 2022-11 | 300.310 | 0 | 2024-11 | 322.066 | 0 |
| 2022-12 | 236.167 | 0 | 2024-12 | 298.914 | 0 |
| 2023-01 | 242.310 | 0 | 2025-01 | 301.245 | 0 |
| 2023-02 | 222.215 | 0 | 2025-02 | 260.339 | 0 |
| 2023-03 | 257.641 | 0 | 2025-03 | 288.796 | 0 |
| 2023-04 | 218.972 | 0 | 2025-04 | 297.754 | 0 |
| 2023-05 | 196.620 | 0 | 2025-05 | 230.404 | 0 |
| 2023-06 | 176.599 | 0 | 2025-06 | 150.753 | 0 |
| 2023-07 | 163.536 | 0 | 2025-07 | 177.440 | 0 |
| 2023-08 | 211.861 | 0 | 2025-08 | 227.801 | 0 |
| 2023-09 | 216.713 | 0 | 2025-09 | 289.100 | 0 |
| 2023-10 | 247.631 | 0 | 2025-10 | 344.319 | 1 |
| 2023-11 | 256.959 | 0 | 2025-11 | 308.388 | 0 |
| 2023-12 | 211.274 | 0 | 2025-12 | 279.835 | 0 |
