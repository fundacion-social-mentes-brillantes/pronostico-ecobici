# Encargo 17 — Confirmar los arreglos del estilo «Ciudad de noche»

En tu respuesta 16 (proceso_ia/16-respuesta-codex-revisar-estilo-noche.txt) señalaste 5 puntos. Arreglos:

1. Foco del botón activo: se quitó la regla que ponía el contorno en color papel; ahora todos los botones del control
   usan contorno de tinta clara (#EDE9E1) a 2 px por fuera, que contrasta con el fondo del control (#131A22).
2. Las bandas ya no usan `figcaption`: son `div.banda` con una frase (`p.banda__frase`, abajo a la izquierda) y el
   crédito (`span.banda__credito`), que ahora va arriba a la derecha, así que no se cruzan.
3. Reserva del gráfico principal: `min-height: clamp(320px, calc(0.3 * min(100vw - 3rem, 70rem)), 400px)`, igual a la
   fórmula de `app.js` (medido: 336 px a 1440 y 1200, 320 px a 900, 700 y 600, 300 px a 390; cero saltos al cargar).
4. Favicon con la paleta nocturna; se quitó de `app.js` el redibujo al cambiar el tema del sistema.
5. La interpolación dura 300 ms; `DESIGN.md` describe también las respuestas a la mano (botones y flecha).

Además, por una crítica visual: frases sobre las bandas ligadas a los datos, gráfico de resultados más alto y con
rótulos más separados, cabecera de una sola fila en celular (menú deslizable), títulos de sección fijos a la izquierda
en PC (`position: sticky`) y encabezados de la tabla sin partirse.

Revisa SOLO estos cambios (en `web/estilos.css`, `web/index.html`, `web/app.js`, `web/favicon.svg`, `DESIGN.md`) y que
no rompan nada: en especial, que las frases de las bandas sean exactas respecto de los datos y la memoria
(«Casi doce millones de viajes en cuatro años, contados hora por hora», «Un día laborable con 10 mm de lluvia o más
tiene, en promedio, un 35 % menos de viajes que uno seco», «Todo el estudio se puede leer, revisar y repetir»), y que
el menú deslizable y los títulos fijos no tapen contenido. No puedes ejecutar Python. Responde en español, breve. Si
todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
