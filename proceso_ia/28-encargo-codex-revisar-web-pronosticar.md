# Encargo 28 — Revisar el enlace al comando de pronóstico en la página web

La página ya mostraba el pronóstico del modelo hora por hora (el gráfico «La edad del dato»: al pasar el cursor o el
dedo por una hora sale el conteo real, el pronóstico, el error y el último dato que veía el modelo). Para que se sepa
que ahora se le puede pedir cualquier hora, Claude agregó (aún sin subir):

- `web/index.html`, sección `#descargas`: un quinto elemento `li.descargas__ancha` con el enlace
  `https://github.com/fundacion-social-mentes-brillantes/pronostico-ecobici#pronosticar-una-hora` (la sección
  «## Pronosticar una hora» del README), título «Pídele al modelo cualquier hora» y su detalle. El título de la
  sección pasó de «Para leerlo completo» a «Para leerlo y probarlo».
- `web/estilos.css`: `.descargas__ancha { grid-column: 1 / -1; }` dentro de `@media (min-width: 47.5rem)`, para que el
  quinto elemento ocupe las dos columnas y no quede huérfano.

Con Python pasan las 32 pruebas; el revisor de diseño (lint e inspector a 1440, 768 y 390 px) da 0 fallas; las 7
advertencias son las mismas que antes del cambio.

Revisa leyendo los archivos (no puedes ejecutar nada): que el enlace apunte al ancla correcta del README, que el texto
sea exacto respecto de lo que hace `src/pronosticar.py`, y que no se rompa nada de accesibilidad ni del diseño de la
lista. Responde en español, breve. Si todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
