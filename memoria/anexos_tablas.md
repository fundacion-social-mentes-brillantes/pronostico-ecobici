# Anexo D. Búsqueda completa de configuraciones

Todas las configuraciones probadas en validación (8 de enero a 30 de junio de 2025), con su error. La marcada con «sí» es la elegida en cada método y escenario (menor MAE). Generada por `src/tablas_memoria.py` a partir de `resultados/metricas_validacion.csv`.

| Método | Retraso | Configuración | MAE | RMSE | Sesgo | Elegida |
|---|---|---|---|---|---|---|
| Ingenuo semanal | 1 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 1 h | — | 105,47 | 149,45 | −19,58 | sí |
| Ridge | 1 h | α 0,1 | 37,18 | 56,38 | −10,75 |  |
| Ridge | 1 h | α 1 | 37,18 | 56,38 | −10,75 | sí |
| Ridge | 1 h | α 10 | 37,24 | 56,50 | −10,79 |  |
| Ridge | 1 h | α 100 | 39,88 | 61,20 | −12,01 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 15 | 33,45 | 51,33 | −6,15 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 31 | 32,22 | 49,24 | −5,43 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,05; hojas máximas 63 | 31,81 | 48,45 | −5,12 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 15 | 31,96 | 48,50 | −4,82 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 31 | 31,68 | 48,42 | −5,11 |  |
| *Boosting* | 1 h | tasa de aprendizaje 0,1; hojas máximas 63 | 31,46 | 48,18 | −4,72 | sí |
| Perceptrón | 1 h | capas ocultas 64; α 0,0001 | 33,09 | 50,07 | −5,62 |  |
| Perceptrón | 1 h | capas ocultas 64; α 0,001 | 33,02 | 49,99 | −6,13 |  |
| Perceptrón | 1 h | capas ocultas 64 y 32; α 0,0001 | 32,83 | 50,22 | −7,84 |  |
| Perceptrón | 1 h | capas ocultas 64 y 32; α 0,001 | 32,72 | 50,01 | −7,14 | sí |
| Ingenuo semanal | 24 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 24 h | — | 105,47 | 149,45 | −19,58 | sí |
| Ridge | 24 h | α 0,1 | 86,03 | 129,51 | −35,02 |  |
| Ridge | 24 h | α 1 | 85,94 | 129,59 | −35,13 |  |
| Ridge | 24 h | α 10 | 85,44 | 130,71 | −35,92 | sí |
| Ridge | 24 h | α 100 | 86,92 | 140,01 | −37,39 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 15 | 72,16 | 118,36 | −15,17 | sí |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 31 | 72,91 | 119,09 | −13,73 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,05; hojas máximas 63 | 73,69 | 120,26 | −12,70 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 15 | 72,61 | 118,99 | −13,32 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 31 | 73,96 | 121,21 | −10,41 |  |
| *Boosting* | 24 h | tasa de aprendizaje 0,1; hojas máximas 63 | 76,69 | 125,68 | −11,63 |  |
| Perceptrón | 24 h | capas ocultas 64; α 0,0001 | 79,65 | 124,01 | −18,67 |  |
| Perceptrón | 24 h | capas ocultas 64; α 0,001 | 77,78 | 122,24 | −10,55 | sí |
| Perceptrón | 24 h | capas ocultas 64 y 32; α 0,0001 | 78,30 | 123,63 | −21,20 |  |
| Perceptrón | 24 h | capas ocultas 64 y 32; α 0,001 | 78,33 | 123,69 | −20,89 |  |
| Ingenuo semanal | 168 h | — | 106,63 | 182,96 | 7,53 | sí |
| Mediana de calendario | 168 h | — | 105,47 | 149,45 | −19,58 | sí |
| Ridge | 168 h | α 0,1 | 93,01 | 136,61 | −39,26 | sí |
| Ridge | 168 h | α 1 | 93,02 | 136,77 | −39,49 |  |
| Ridge | 168 h | α 10 | 93,16 | 138,49 | −41,20 |  |
| Ridge | 168 h | α 100 | 95,88 | 149,54 | −45,07 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 15 | 87,23 | 132,31 | −28,04 | sí |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 31 | 87,39 | 132,82 | −24,69 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,05; hojas máximas 63 | 88,37 | 134,97 | −26,71 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 15 | 88,62 | 134,05 | −28,87 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 31 | 89,64 | 136,55 | −27,55 |  |
| *Boosting* | 168 h | tasa de aprendizaje 0,1; hojas máximas 63 | 90,52 | 138,32 | −26,34 |  |
| Perceptrón | 168 h | capas ocultas 64; α 0,0001 | 88,96 | 133,09 | −29,42 |  |
| Perceptrón | 168 h | capas ocultas 64; α 0,001 | 86,81 | 130,62 | −26,83 | sí |
| Perceptrón | 168 h | capas ocultas 64 y 32; α 0,0001 | 90,58 | 135,63 | −35,94 |  |
| Perceptrón | 168 h | capas ocultas 64 y 32; α 0,001 | 90,55 | 134,84 | −29,95 |  |

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
