# DESIGN.md — Pronóstico Ecobici (web del proyecto y memoria en PDF)

## Producto (PRODUCT)
- Qué es: la presentación pública de un estudio con forma de TFM: cuánto empeora el pronóstico de viajes horarios de
  Ecobici Buenos Aires cuando el último dato llega con 1, 24 o 168 horas de retraso. Lo hicieron Claude y Codex como
  prueba de capacidades (no es un trabajo presentado ante ninguna universidad).
- Para quién: quien califica el trabajo (ingeniero, máster en IA) y cualquier curioso; se abre en PC y en celular
  (muchas veces desde WhatsApp).
- Modo: LEER (entender un estudio), con una presencia premium y cinematográfica; nada de plantilla de startup.
- Acción principal: entender el hallazgo en 30 segundos y poder bajar la memoria (PDF) o ir al código.
- Tono: claro, en español, sin jerga sin explicar; cifras exactas; honesto con las limitaciones.

## Dirección elegida: «Ciudad de noche»
Se presentaron tres direcciones con vista previa en PC y celular (A · Informe editorial claro, B · Ciudad de noche,
C · Ciclovía, afiche ámbar). Quien encargó el estudio escogió **B** el 19 nov 2026. Buenos Aires de noche: fondo tinta azul, la
ciudad iluminada por farolas cálidas y las tres edades del dato como estelas de luz (verde aguamarina, ámbar y coral).
La ilustración de portada amarra la imagen con la idea del estudio: las tres estelas son los tres pronósticos.

## Idea firma (del inventario del tema)
«La edad del dato»: un control con tres posiciones (1 hora · 1 día · 1 semana) que envejece el último conteo y
muestra, sobre una semana real de prueba, cómo la predicción se separa de lo real (el área entre las dos líneas es el
error) y cuánto sube el error. Se pueden recorrer las 26 semanas del semestre; la página arranca en la más parecida al
promedio (30 sep – 6 oct 2025, regla calculada en src/exportar_web.py). Al pasar por una hora dice qué conteo veía el
modelo («último dato que veía el modelo: mié 1 oct, 18:00»).
Inventario: 11.936.199 viajes; 35.064 horas; pico laborable 17:00 (949 viajes/h); hora récord 10/11/2025 18:00
(1.527); lluvia: −35 % de viajes en días de ≥10 mm; el hallazgo de 2024 (321.015 recorridos de menos de un minuto);
el feriado del 9 de julio en la semana de prueba; 21 horas de corte.

## Color (tokens en web/estilos.css; un solo tema, oscuro)
- `--papel` #0B0F14 (fondo, tinta azul), `--papel-2` #131A22 y `--papel-3` #1B2430 (superficies y estados),
  `--tinta` #EDE9E1 (texto, blanco cálido), `--tinta-2` #B4BBC5 (secundario), `--tinta-3` #8F99A6 (etiquetas).
- `--linea` #232B36 (rejilla de gráficos y tablas), `--gris` #6E7782 (referencias simples, solo líneas).
- Edades del dato, la única codificación de color: `--fresco` #3DD6C0 (1 hora), `--dia` #F5B54A (1 día), `--semana`
  #FF7A66 (1 semana). En los botones activos, el texto va en `--papel` sobre el color de la edad.
- Contraste AA o más en todo texto (medido: tinta-3 6,7:1 sobre el fondo; la más baja, 5,4:1 sobre papel-3).
- El PDF interior y sus figuras usan la versión clara para leer e imprimir (fresco #0F6F63, día #965806, semana
  #AE3B2F sobre blanco); la portada del PDF, el Léeme y la imagen para compartir usan la versión nocturna.

## Imágenes
- Cuatro ilustraciones generadas con IA por Codex a partir de indicaciones de Claude, en el mismo estilo pictórico
  (no son fotografías y se dice en la página): portada (calle arbolada de noche con estación de bicicletas y las tres
  estelas), banda antes de «Datos» (vista aérea nocturna con estaciones y recorridos de luz), banda antes de
  «Resultados» (noche de lluvia con la estación casi vacía) y banda antes de
  «Descargas» (amanecer en una estación). Sin logos ni marcas.
- En web/img, en WebP de 1672 y 960 px con `srcset`; la portada con `fetchpriority="high"`, las bandas con carga
  diferida. Velo de degradado solo funcional: oscurece donde va texto y funde las bandas con el fondo.

## Tipografía (OFL 1.1, alojadas en el repo: web/fuentes, recursos/fuentes)
- Títulos y texto de lectura: **Newsreader** (Production Type), variable con tamaño óptico. Titulares en peso 520-580
  con interletrado −0,02 em.
- Interfaz, etiquetas, tablas, cifras y figuras: **Schibsted Grotesk**, con cifras proporcionales: sus cifras
  tabulares ensanchan también el punto y la coma («3 .156 .182»), así que no se usan. Sin monoespaciada.
- Las dos están recortadas a los caracteres del español (recursos/preparar_fuentes.py).
- Escala web (px): 14 · 16 · 19 · 21 · 24 · 42 · 70 (el titular principal); las etiquetas de los gráficos van a 12.
  Ancho de lectura máximo unos 70 caracteres.

## Espacio, forma y retícula
- Unidad 8 px. Márgenes laterales 20-24 px en celular, retícula de 12 columnas con 1120 px máximo en PC.
- Separación por espacio y por tono, no por líneas: cabecera más oscura que el fondo, control segmentado y botones
  rellenos, descargas como bloques rellenos, pie en banda más oscura. Las líneas finas quedan solo en tablas y en la
  rejilla de los gráficos. Radios de 7-12 px en controles y bloques.
- Las cifras clave van dentro de frases, más grandes y en el color de su edad; nada de bloques «número grande +
  etiquetita».

## Componentes
- Cabecera con el nombre del estudio y enlaces: Hallazgo · Datos · Método · Resultados · Límites · Descargas; la
  sección visible se marca con un subrayado verde aguamarina.
- El control de edad del dato: tres botones segmentados con estado claro (aria-pressed), operable con teclado.
- Gráficos en SVG dibujados a mano con los datos exportados (sin librerías), con títulos y ejes legibles, globo
  accesible (Escape lo cierra) y tabla alternativa.
- Tablas de resultados con cifras alineadas a la derecha y la mejor de cada columna en negrita.

## Movimiento
- Mínimo y con propósito: al cambiar la edad del dato, la línea de predicción se interpola en 300 ms (ease-out) y el
  error se actualiza. Además, una sola entrada al cargar: los bloques de la portada aparecen en 500 ms, escalonados
  70 ms. Fuera de eso, solo respuestas a la mano: cambio de color de los botones (200 ms) y la flecha de cada descarga
  que se corre 2 px al pasar el cursor. `prefers-reduced-motion` desactiva todo.

## PDF de la memoria
- Portada a sangre en estilo nocturno, con la ilustración de la web, el título en blanco cálido y las tres edades.
- Interior claro para leer: índice; cuerpo en Newsreader a 10,5 pt; tablas en Schibsted Grotesk 8,2 pt con filas
  alternas muy suaves; figuras a todo el ancho de la caja con pie en Schibsted Grotesk; números de página y título
  corrido en el pie; márgenes 20 mm arriba, 22 mm a los lados y 24 mm abajo; A4. Ninguna tabla puede pasar del ancho
  de la caja: si pasara, Chrome encogería todas las páginas.
- Las figuras de matplotlib usan la paleta clara y Schibsted Grotesk (recursos/fuentes), fondo blanco.
