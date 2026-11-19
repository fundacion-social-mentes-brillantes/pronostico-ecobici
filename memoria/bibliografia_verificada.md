# Bibliografía verificada (APA 7)

Cada referencia se comprobó en Crossref, arXiv o la página oficial (19 nov 2026). En la memoria **solo** se citan
estas. Al lado va lo que cada una respalda; no atribuirles nada más.

## Bicicletas compartidas

- Albuquerque, V., Sales Dias, M., & Bacao, F. (2021). Machine learning approaches to bike-sharing systems: A
  systematic literature review. *ISPRS International Journal of Geo-Information, 10*(2), Artículo 62.
  https://doi.org/10.3390/ijgi10020062 — Revisión sistemática del aprendizaje automático en bicicletas compartidas;
  el pronóstico de demanda es una de sus aplicaciones; las redes neuronales aparecen en gran parte de los estudios
  desde 2016.
- Jiang, W. (2022). Bike sharing usage prediction with deep learning: A survey. *Neural Computing and Applications,
  34*(18), 15369–15385. https://doi.org/10.1007/s00521-022-07380-5 — Revisión de aprendizaje profundo para predecir
  el uso (estudios 2018-2021, sistemas con y sin estaciones); el uso depende de patrones temporales, del entorno y de
  la relación entre estaciones.
- Fanaee-T, H., & Gama, J. (2014). Event labeling combining ensemble detectors and background knowledge. *Progress in
  Artificial Intelligence, 2*(2–3), 113–127. https://doi.org/10.1007/s13748-013-0040-3 — Origen del conjunto de
  Capital Bikeshare (Washington) 2011-2012 del repositorio UCI.
- Brajevic, I., Tuba, E., & Tuba, M. (2026). Ensemble learning with systematic hyperparameter optimization for
  urban-bike-sharing demand prediction. *Sustainability, 18*(8), Artículo 3766. https://doi.org/10.3390/su18083766 —
  Datos horarios de Washington; diez repartos aleatorios 80/20; ensambles de árboles; RMSE 38,48 y R² 0,955; la hora
  del día y la temperatura son las variables más importantes.
- Torres, J., Jiménez-Meroño, E., & Soriguera, F. (2024). Forecasting the usage of bike-sharing systems through
  machine learning techniques to foster sustainable urban mobility. *Sustainability, 16*(16), Artículo 6910.
  https://doi.org/10.3390/su16166910 — Nueva York; bosque aleatorio, *gradient boosting* y red neuronal con precisión
  parecida; recomiendan el bosque aleatorio por su calibración más simple; insisten en que el error de predicción se
  traslada al reposicionamiento.
- Peláez-Rodríguez, C., Pérez-Aracil, J., Fister, D., Torres-López, R., & Salcedo-Sanz, S. (2024). Bike sharing and
  cable car demand forecasting using machine learning and deep learning multivariate time series approaches. *Expert
  Systems with Applications, 238*, Artículo 122264. https://doi.org/10.1016/j.eswa.2023.122264 — Compararon enfoques
  de aprendizaje automático y profundo para la demanda de bicicletas y de un teleférico (no atribuirles un orden
  entre familias).
- Wessel, J. (2020). Using weather forecasts to forecast whether bikes are used. *Transportation Research Part A:
  Policy and Practice, 138*, 537–559. https://doi.org/10.1016/j.tra.2020.06.006 — Estudia el uso de pronósticos
  meteorológicos para pronosticar el uso de bicicletas.
- Ohana, M. A. (2021). *Predicción de demanda del uso de las bicicletas públicas de CABA* [Tesis de maestría,
  Universidad Torcuato Di Tella]. Repositorio Digital UTDT. https://repositorio.utdt.edu/handle/20.500.13098/11241 —
  Ecobici 2018-2020; modelos econométricos de series de tiempo y de panel por estación; programación lineal entera
  para redistribuir.

## Pronóstico y evaluación

- Hyndman, R. J., & Athanasopoulos, G. (2021). *Forecasting: Principles and practice* (3.ª ed.). OTexts.
  https://otexts.com/fpp3/ — Métodos ingenuos y estacionales; evaluación con origen móvil; medidas de error.
- Hyndman, R. J., & Koehler, A. B. (2006). Another look at measures of forecast accuracy. *International Journal of
  Forecasting, 22*(4), 679–688. https://doi.org/10.1016/j.ijforecast.2006.03.001 — Medidas de error de pronóstico.
- Tashman, L. J. (2000). Out-of-sample tests of forecasting accuracy: An analysis and review. *International Journal
  of Forecasting, 16*(4), 437–450. https://doi.org/10.1016/S0169-2070(00)00065-0 — Evaluación fuera de muestra y
  origen móvil.
- Bergmeir, C., & Benítez, J. M. (2012). On the use of cross-validation for time series predictor evaluation.
  *Information Sciences, 191*, 192–213. https://doi.org/10.1016/j.ins.2011.12.028 — Validación cruzada frente a
  evaluación temporal en series de tiempo.
- Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic
  Statistics, 13*(3), 253–263. https://doi.org/10.1080/07350015.1995.10524599 — Prueba para comparar la precisión de
  dos pronósticos.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation
  consistent covariance matrix. *Econometrica, 55*(3), 703–708. https://doi.org/10.2307/1913610 — Varianza robusta a
  autocorrelación (núcleo de Bartlett).
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics,
  6*(2), 65–70. https://www.jstor.org/stable/4615733 — Corrección por comparaciones múltiples.
- Makridakis, S., Spiliotis, E., & Assimakopoulos, V. (2022). M5 accuracy competition: Results, findings, and
  conclusions. *International Journal of Forecasting, 38*(4), 1346–1364.
  https://doi.org/10.1016/j.ijforecast.2021.11.013 — Competencia M5 (ventas de Walmart): el ganador y la mayoría de
  los mejores métodos usaron LightGBM.

## Métodos

- Hoerl, A. E., & Kennard, R. W. (1970). Ridge regression: Biased estimation for nonorthogonal problems.
  *Technometrics, 12*(1), 55–67. https://doi.org/10.1080/00401706.1970.10488634
- Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324
- Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. *The Annals of Statistics,
  29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451
- Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986). Learning representations by back-propagating errors.
  *Nature, 323*(6088), 533–536. https://doi.org/10.1038/323533a0
- Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). *Why do tree-based models still outperform deep learning on
  tabular data?* [Prepublicación]. arXiv. https://doi.org/10.48550/arXiv.2207.08815 — Los árboles siguen siendo muy
  competitivos en datos tabulares.
- Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P.,
  Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011).
  Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.
  https://jmlr.org/papers/v12/pedregosa11a.html
- Raasveldt, M., & Mühleisen, H. (2019). DuckDB: An embeddable analytical database. En *Proceedings of the 2019
  International Conference on Management of Data* (pp. 1981–1984). ACM. https://doi.org/10.1145/3299869.3320212

## Datos

- Gobierno de la Ciudad de Buenos Aires. (s. f.). *Bicicletas públicas: Recorridos realizados 2022, 2023, 2024 y
  2025* [Conjunto de datos]. Buenos Aires Data. Recuperado el 19 de noviembre de 2026 de
  https://data.buenosaires.gob.ar/dataset/bicicletas-publicas — Licencia CC BY 2.5 Argentina.
- Zippenfenig, P. (2023). *Open-Meteo.com Weather API* [Software]. Zenodo. https://doi.org/10.5281/zenodo.7970649 —
  Datos CC BY 4.0; producto ERA5 de Copernicus.
- Ley 27.399 de 2017. Ley de establecimiento de feriados y fines de semana largos. 18 de octubre de 2017. Boletín
  Oficial de la República Argentina, 33732. https://www.argentina.gob.ar/normativa/nacional/ley-27399-281835/texto
- Decreto 1027 de 2024 [Poder Ejecutivo Nacional]. Días no laborables con fines turísticos para el año 2025. 20 de
  noviembre de 2024. Boletín Oficial de la República Argentina, 35551.
  https://www.argentina.gob.ar/normativa/nacional/norma-406417/texto — 2 de mayo, 15 de agosto y 21 de noviembre de
  2025 como días no laborables con fines turísticos.
- Resolución 139 de 2025 [Jefatura de Gabinete de Ministros]. Traslado del feriado nacional del 12 de octubre de 2025
  al 10 de octubre. 28 de agosto de 2025. Boletín Oficial de la República Argentina.
  https://www.argentina.gob.ar/normativa/nacional/norma-417061/texto

## Herramientas de IA usadas (Anexo A)

- Anthropic. (2026). *Claude Opus 5.5* [Modelo de lenguaje de gran tamaño]. https://www.anthropic.com/claude
- OpenAI. (2026). *Codex* (GPT-6.2 Sol y GPT-6.1 Terra) [Asistente de programación basado en modelos de lenguaje].
  https://openai.com/codex/
