# Encargo 16 — Revisar la web y el PDF con el estilo «Ciudad de noche»

Quien encargó el estudio escogió entre tres direcciones la B, «Ciudad de noche». Claude la aplicó (aún sin subir):

- `web/estilos.css`: un solo tema oscuro (tokens nuevos), cabecera sólida, separación por tono y no por líneas
  (control segmentado y botones rellenos, descargas como bloques, pie en banda), portada con ilustración de fondo y
  velo, bandas de ilustración (`.banda`), alturas reservadas para los gráficos.
- `web/index.html`: ilustración de portada (`img/portada-*.webp`, `fetchpriority="high"`), tres bandas con carga
  diferida (`datos`, `lluvia`, `amanecer`), crédito de las ilustraciones (generadas con IA por Codex), `color-scheme`
  oscuro, imagen para compartir `compartir.jpg`; las tablas desplegables quedaron antes de los pies de figura.
- `memoria/construir_pdf.py` y `memoria/estilo_pdf.css`: portada del PDF nocturna con `memoria/portada.jpg` y texto
  alternativo; se quitó la función del gráfico de portada que ya no se usaba.
- `recursos/hacer_compartir.py`: genera `web/compartir.jpg` (1200×630, JPEG liviano).
- `DESIGN.md` actualizado.

Revisa leyendo el código (no puedes ejecutar Python) y señala solo errores reales, con archivo y línea:
1. Accesibilidad: contraste del texto sobre el fondo y sobre la ilustración (los velos), foco visible, imágenes
   decorativas bien marcadas (`aria-hidden`, `alt=""`), crédito de las ilustraciones.
2. Rendimiento: tamaños de imagen, `srcset`/`sizes`, precarga de la portada, carga diferida de las bandas.
3. Que no quede nada del tema claro anterior que choque (colores fijos en `web/app.js`, `estilos.css`, metadatos).
4. Que el PDF siga bien: portada, índice y marcadores (lee `memoria/memoria.html`).
5. Coherencia de `DESIGN.md` con lo construido.

Responde en español, breve, lista numerada. Si todo está bien, termina con la línea exacta: SIN ERRORES PENDIENTES.
