# Encargo para Codex: redactar los capítulos 2 y 3 de la memoria

Responde en español. Guarda en UTF-8. Trabajas sin internet, en esta carpeta. Escribe SOLO estos dos archivos:
`memoria/capitulo2_estado_del_arte.md` y `memoria/capitulo3_objetivos_metodologia.md`. No toques nada más.

## Qué es

La memoria de un trabajo fin de máster (Máster Universitario en Inteligencia Artificial, UNIR; tipo 3,
«comparativa de soluciones»; líneas aprendizaje automático y aprendizaje profundo). Tema:
**«Comparación de modelos para pronosticar viajes horarios de Ecobici Buenos Aires con datos retrasados»**.
Lee primero, para el contenido exacto: `memoria/solicitud_del_tema.md` (la propuesta aprobada en lo esencial),
`encargo-codex-modelos.md` (el diseño experimental exacto) y `memoria/bibliografia_verificada.md`.

## Reglas de escritura (importantes)

- Español académico neutro (la universidad es española), en impersonal («se propone», «se evalúa»). Frases claras y
  no muy largas. Nada de relleno, nada de frases de IA genéricas («en la era actual», «cabe destacar», «en
  resumen», «juega un papel crucial»). Explica cada concepto técnico de forma que alguien que no es experto lo
  entienda, sin perder rigor.
- **Solo puedes citar las referencias de `memoria/bibliografia_verificada.md`, y solo para lo que allí dice que
  respaldan.** Formato APA 7 en el texto: (Autor, año), (Autor y Autor, año), (Autor et al., año). No inventes
  datos, cifras ni resultados de otros trabajos. No copies frases de las fuentes: parafrasea.
- No adelantes resultados de este trabajo (todavía no existen). Donde haga falta, describe lo que se medirá.
- Markdown: títulos `## 2.1 ...`, `### 2.1.1 ...`. Ecuaciones sencillas en texto o LaTeX en línea con `$...$`.
  Puedes incluir hasta 2 tablas en cada capítulo (por ejemplo, una tabla resumen de estudios previos).
- Sin lista de referencias al final (va aparte).

## Capítulo 2. Contexto y estado del arte (entre 5.500 y 6.500 palabras)

Estructura sugerida (ajústala si mejora):
- 2.1 Los sistemas de bicicletas compartidas y el problema de la demanda (qué son, por qué se pronostica la
  demanda: redistribución, operación; Ecobici Buenos Aires en pocas líneas, sin cifras que no estén en las fuentes).
- 2.2 Conceptos de pronóstico: serie de tiempo, horizonte, información disponible al momento de pronosticar,
  estacionalidad diaria y semanal, métodos de referencia ingenuos; **por qué la disponibilidad de los datos
  importa** (un retraso de *d* horas equivale, visto desde el último dato conocido, a pronosticar *d* pasos adelante).
- 2.3 Técnicas: regresión lineal y Ridge; árboles, bosques aleatorios y *gradient boosting* (y su versión por
  histogramas); redes neuronales y perceptrón multicapa (retropropagación); en cada una: idea, ventajas, límites.
- 2.4 Estudios previos de pronóstico de demanda de bicicletas compartidas (Albuquerque et al., Jiang, Fanaee-T y
  Gama, Brajevic et al., Torres et al., Peláez-Rodríguez et al., Wessel, Ohana) y evidencia general sobre árboles
  frente a redes en datos tabulares (Grinsztajn et al.; M5). Una tabla resumen.
- 2.5 Cómo evaluar y comparar pronósticos: MAE, RMSE, sesgo; evaluación fuera de muestra y origen móvil frente a
  repartos aleatorios (Tashman; Bergmeir y Benítez; Hyndman y Athanasopoulos); prueba de Diebold-Mariano con
  varianza de Newey-West y corrección de Holm.
- 2.6 Conclusiones del estado del arte: el hueco que cubre este trabajo (medir el efecto de la antigüedad de los
  conteos sobre el error y la elección del modelo, con evaluación cronológica estricta, en un sistema
  latinoamericano con datos 2022-2025). Sin exagerar: es una brecha concreta, no «nadie lo ha hecho nunca».

## Capítulo 3. Objetivos concretos y metodología de trabajo (entre 2.500 y 3.200 palabras)

- 3.1 Objetivo general y 3.2 objetivos específicos (los de la solicitud).
- 3.3 Preguntas de investigación e hipótesis (P1-P3 de la solicitud).
- 3.4 Metodología: tipo de trabajo (comparativa empírica), fases (datos, diseño, implementación, experimentación,
  análisis), definición formal del problema (t, d, y_t), escenarios, alternativas, particiones con margen de siete
  días, búsqueda de hiperparámetros en validación, prueba única con modelos congelados, horas evaluadas comunes,
  métricas y contraste. Exactamente como en `encargo-codex-modelos.md`; si algo no está definido allí, no lo inventes.
- 3.5 Herramientas (Python, pandas, scikit-learn, DuckDB para el SQL, statsmodels si aplica, matplotlib; repositorio
  Git) y reproducibilidad (semilla, scripts, datos que se descargan con un script).
- 3.6 Datos y aspectos éticos y legales: solo datos públicos; licencias (CC BY 2.5 AR, CC BY 4.0); las columnas del
  usuario nunca se leen; solo conteos agregados; no se recaban datos personales.
- 3.7 Planificación (4 meses) en una tabla.

Al terminar, responde con el número de palabras de cada capítulo y la lista de citas que usaste. Asume lo razonable
y sigue; al final di qué no pudiste hacer.
