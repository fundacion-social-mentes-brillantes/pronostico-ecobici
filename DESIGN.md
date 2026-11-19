# DESIGN.md — Pronóstico Ecobici (web del proyecto y memoria en PDF)

## Producto (PRODUCT)
- Qué es: la presentación pública de un estudio con forma de TFM: cuánto empeora el pronóstico de viajes horarios de
  Ecobici Buenos Aires cuando el último dato llega con 1, 24 o 168 horas de retraso. Lo hicieron Claude y Codex como
  prueba de capacidades (no es un trabajo presentado ante ninguna universidad).
- Para quién: quien califica el trabajo (ingeniero, máster en IA) y cualquier curioso; se abre en PC y en celular
  (muchas veces desde WhatsApp).
- Modo: LEER (entender un estudio). Precisión y sobriedad; nada de plantilla de startup.
- Acción principal: entender el hallazgo en 30 segundos y poder bajar la memoria (PDF) o ir al código.
- Tono: claro, en español, sin jerga sin explicar; cifras exactas; honesto con las limitaciones.

## Idea firma (del inventario del tema)
«La edad del dato»: un control con tres posiciones (1 hora · 1 día · 1 semana) que envejece el último conteo y
muestra, sobre una semana real de prueba, cómo la predicción se separa de lo real (el área entre las dos líneas es el
error) y cuánto sube el error. Se pueden recorrer las 26 semanas del semestre; la página arranca en la más parecida al
promedio (30 sep – 6 oct 2025, regla calculada en src/exportar_web.py). Al pasar por una hora dice qué conteo veía el
modelo («último dato visto: mié 1 oct, 18:00»).
Inventario para el resto de la página: 11.936.199 viajes; 35.064 horas; pico laborable 17:00-18:00 (949 viajes/h);
hora récord 10/11/2025 18:00 (1.527); lluvia: −35 % de viajes en días de ≥10 mm; el hallazgo de 2024 (321.015
recorridos de menos de un minuto); el feriado del 9 de julio en la semana de prueba; 21 horas de corte.

## Color (tokens; el acento se usa poco)
- `--papel` #F4F3EF (fondo hueso de poco color, no crema), `--papel-2` #EAE8E2 (bloques), `--tinta` #1A1D21 (texto),
  `--tinta-2` #4F555D (secundario), `--tinta-3` #62686F (etiquetas pequeñas)
- `--linea` #D6D3CA (bordes finos)
- `--real` = `--tinta` (serie real, línea gruesa)
- `--fresco` #0F6F63 (dato de 1 h, verde azulado) · `--dia` #965806 (dato de 24 h, ámbar tostado) · `--semana`
  #AE3B2F (dato de 168 h, terracota). Esta escala «fresco → viejo» es la única codificación de color de la página y
  de las figuras.
- Métodos en los gráficos de resultados: tinta (el mejor), tinta-2 y gris #80858C (referencias simples, solo líneas).
- Modo oscuro: `--papel` #121518, `--papel-2` #1B1F23, `--tinta` #ECEAE4, `--tinta-2` #AEB4BB, `--linea` #2C3238; los
  tres colores de edad se aclaran un paso (#46B5A4, #E0A04B, #E5806F).
- Contraste mínimo AA en todo texto.

## Tipografía (OFL 1.1, alojadas en el repo: web/fuentes, recursos/fuentes)
- Títulos y texto de lectura: **Newsreader** (Production Type), variable con tamaño óptico: a 72 px se vuelve una
  letra de titular fina y a 19 px una de lectura cómoda. Titulares en peso 560-600 con interletrado −0,02 em.
- Interfaz, etiquetas, tablas, cifras y figuras: **Schibsted Grotesk**, con cifras proporcionales: sus cifras
  tabulares ensanchan también el punto y la coma («3 .156 .182»), así que no se usan. Sin monoespaciada.
- Las dos están recortadas a los caracteres del español (recursos/preparar_fuentes.py).
- Escala web (px): 14 · 16 · 19 · 21 · 24 · 42 · 70 (el titular principal); las etiquetas de los gráficos van a 12. Ancho
  de lectura máximo unos 70 caracteres.

## Espacio, forma y retícula
- Unidad 8 px. Márgenes laterales 24 px en celular, retícula de 12 columnas con 1120 px máximo en PC.
- Bordes finos de 1 px; radios pequeños (4 px). Sin sombras grandes, sin degradados, sin tarjetas con icono.
- Las cifras clave van dentro de frases, más grandes y en el color de su edad; nada de bloques «número grande +
  etiquetita».

## Componentes
- Encabezado sobrio con el nombre del estudio y enlaces: Hallazgo · Datos · Método · Resultados · Límites · Descargas.
- El control de edad del dato: tres botones segmentados con estado claro (aria-pressed), operable con teclado.
- Gráficos en SVG dibujados a mano con los datos exportados (sin librerías pesadas), con títulos y ejes legibles,
  tooltips accesibles y tabla alternativa.
- Tablas de resultados con cifras alineadas a la derecha y la mejor de cada columna en negrita.
- Notas al margen (en PC) / bloques de nota (en celular) para «cómo leer esto».

## Movimiento
- Mínimo y con propósito: al cambiar la edad del dato, la línea de predicción se interpola en 300 ms (ease-out) y el
  error se actualiza. Además, una sola entrada al cargar: los tres bloques de la portada aparecen en 500 ms,
  escalonados 70 ms. Nada más se anima. `prefers-reduced-motion` desactiva las dos cosas.

## PDF de la memoria
- Mismo sistema: portada con el titular en Newsreader y el gráfico de la semana típica; índice; cuerpo en
  Newsreader a 10,5 pt; tablas en Schibsted Grotesk 8,5 pt con filas alternas muy suaves; figuras a todo el ancho
  de la caja con pie en Schibsted Grotesk 8,5 pt; números de página y título corrido en el pie; márgenes 20 mm arriba, 22 mm a los lados y 24 mm abajo; A4. Ninguna tabla puede pasar del
  ancho de la caja: si pasara, Chrome encogería todas las páginas.
- Las figuras de matplotlib usan la misma paleta y Schibsted Grotesk (recursos/fuentes), fondo blanco.
