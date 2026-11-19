/* La edad del dato: gráficos e interacción.
   Datos: window.DATOS (web/datos.js), generado por src/exportar_web.py a partir de resultados/.
   Sin librerías: cada gráfico es SVG dibujado a mano y se vuelve a dibujar si cambia el ancho. */
(() => {
  "use strict";
  const D = window.DATOS;
  if (!D) return;

  const NS = "http://www.w3.org/2000/svg";
  const EDAD = {
    1: { corta: "1 hora", larga: "hace 1 hora", color: "--fresco", suave: "--fresco-suave" },
    24: { corta: "1 día", larga: "hace 1 día", color: "--dia", suave: "--dia-suave" },
    168: { corta: "1 semana", larga: "hace 1 semana", color: "--semana", suave: "--semana-suave" },
  };
  const RETRASOS = [1, 24, 168];
  const DIAS = ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"];
  const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];
  const movimientoReducido = window.matchMedia("(prefers-reduced-motion: reduce)");

  /* ---------- Utilidades ---------- */

  // Punto de miles, coma decimal y signo menos tipográfico, como en la memoria.
  function num(x, dec = 0) {
    if (x === null || x === undefined || !Number.isFinite(x)) return "—";
    const [ent, frac] = Math.abs(x).toFixed(dec).split(".");
    const conMiles = ent.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    const signo = x < 0 && Number(Math.abs(x).toFixed(dec)) !== 0 ? "−" : "";
    return signo + conMiles + (frac ? "," + frac : "");
  }

  function valor(ruta) {
    return ruta.split(".").reduce((o, k) => (o === null || o === undefined ? undefined : o[k]), D);
  }

  function nodo(nombre, atributos = {}, padre = null) {
    const e = document.createElementNS(NS, nombre);
    for (const [k, v] of Object.entries(atributos)) {
      if (v !== undefined && v !== null) e.setAttribute(k, v);
    }
    if (padre) padre.appendChild(e);
    return e;
  }

  function texto(padre, x, y, contenido, atributos = {}) {
    const t = nodo("text", { x, y, ...atributos }, padre);
    t.textContent = contenido;
    return t;
  }

  function color(variable) {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
  }

  // Fechas en UTC para que el horario de verano del visitante no mueva las horas de Buenos Aires.
  function instante(inicioISO, horas) {
    const [a, m, d] = inicioISO.split("-").map(Number);
    return new Date(Date.UTC(a, m - 1, d) + horas * 3600e3);
  }
  const diaCorto = (f) => `${DIAS[f.getUTCDay()]} ${f.getUTCDate()}`;
  const diaConMes = (f) => `${DIAS[f.getUTCDay()]} ${f.getUTCDate()} ${MESES[f.getUTCMonth()]}`;
  const hora = (f) => `${String(f.getUTCHours()).padStart(2, "0")}:00`;
  const isoDia = (f) => f.toISOString().slice(0, 10);

  // Tope del eje vertical y paso de la rejilla: como mucho cinco divisiones, con números redondos.
  function escalaVertical(maximo) {
    for (const paso of [20, 25, 50, 100, 200, 250, 500]) {
      if (Math.ceil(maximo / paso) <= 5) return { tope: Math.ceil(maximo / paso) * paso, paso };
    }
    return { tope: Math.ceil(maximo / 500) * 500, paso: 500 };
  }

  function trazo(valores, x, y) {
    let d = "";
    let abierto = false;
    valores.forEach((v, i) => {
      if (v === null) { abierto = false; return; }
      d += `${abierto ? "L" : "M"}${x(i).toFixed(1)} ${y(v).toFixed(1)}`;
      abierto = true;
    });
    return d;
  }

  // Polígonos entre la serie real y la predicha, por tramos donde existen las dos: el área es el error.
  function areaEntre(real, pred, x, y) {
    let d = "";
    let tramo = [];
    const cerrar = () => {
      if (tramo.length > 1) {
        d += "M" + tramo.map((i) => `${x(i).toFixed(1)} ${y(pred[i]).toFixed(1)}`).join("L");
        d += "L" + tramo.slice().reverse().map((i) => `${x(i).toFixed(1)} ${y(real[i]).toFixed(1)}`).join("L") + "Z";
      }
      tramo = [];
    };
    real.forEach((r, i) => {
      if (r === null || pred[i] === null) cerrar();
      else tramo.push(i);
    });
    cerrar();
    return d;
  }

  // Separa rótulos que quedarían encimados (posiciones verticales, distancia mínima).
  function separar(posiciones, minimo, arriba, abajo) {
    const orden = posiciones.map((y, i) => ({ y, i })).sort((a, b) => a.y - b.y);
    for (let vuelta = 0; vuelta < 30; vuelta++) {
      let movido = false;
      for (let k = 1; k < orden.length; k++) {
        const falta = minimo - (orden[k].y - orden[k - 1].y);
        if (falta > 0) {
          orden[k - 1].y -= falta / 2;
          orden[k].y += falta / 2;
          movido = true;
        }
      }
      if (orden.length) {
        const exceso = orden[orden.length - 1].y - abajo;
        if (exceso > 0) orden.forEach((o) => { o.y -= exceso; });
        const falta = arriba - orden[0].y;
        if (falta > 0) orden.forEach((o) => { o.y += falta; });
      }
      if (!movido) break;
    }
    const salida = [];
    orden.forEach((o) => { salida[o.i] = o.y; });
    return salida;
  }

  // Vuelve a dibujar un gráfico cuando cambia el ancho de su contenedor.
  function alCambiarAncho(contenedor, dibujar) {
    let ultimo = 0;
    let pendiente = false;
    const observar = new ResizeObserver(() => {
      if (pendiente) return;
      pendiente = true;
      requestAnimationFrame(() => {
        pendiente = false;
        const ancho = Math.round(contenedor.clientWidth);
        if (ancho && ancho !== ultimo) { ultimo = ancho; dibujar(ancho); }
      });
    });
    observar.observe(contenedor);
  }

  function svgNuevo(contenedor, ancho, alto) {
    contenedor.querySelector(":scope > svg")?.remove();
    const svg = nodo("svg", { viewBox: `0 0 ${ancho} ${alto}`, width: ancho, height: alto, "aria-hidden": "true", focusable: "false" });
    contenedor.prepend(svg);
    return svg;
  }

  /* ---------- Cifras del texto ---------- */

  document.querySelectorAll("[data-cifra]").forEach((elemento) => {
    const v = valor(elemento.dataset.cifra);
    if (typeof v === "number") elemento.textContent = num(v, Number(elemento.dataset.dec || 0));
  });

  /* ---------- La edad del dato (gráfico principal) ---------- */

  const S = D.semanas;
  const figura = document.getElementById("edad");
  const lienzo = document.getElementById("grafico-edad");
  const lectura = document.getElementById("lectura");
  const botonesEdad = figura.querySelectorAll(".segmentos button");
  const antes = document.getElementById("semana-antes");
  const despues = document.getElementById("semana-despues");
  const etiquetaSemana = document.getElementById("semana-etiqueta");
  const detalles = document.getElementById("tabla-semana");

  const estado = { retraso: 1, semana: S.tipica, mostrada: null, cursor: null, animacion: null };
  let G = null;

  const globo = document.createElement("div");
  globo.className = "globo";
  globo.setAttribute("aria-hidden", "true");
  lienzo.appendChild(globo);

  const voz = document.createElement("p");
  voz.className = "solo-lector";
  voz.setAttribute("aria-live", "polite");
  lienzo.after(voz);

  const semanaActual = () => S.lista[estado.semana];

  function dibujarEdad(ancho) {
    ancho = ancho || Math.round(lienzo.clientWidth);
    if (!ancho) return;
    const semana = semanaActual();
    const angosto = ancho < 560;
    const dm = {
      w: ancho,
      h: angosto ? 300 : Math.round(Math.min(400, Math.max(320, ancho * 0.3))),
      izq: angosto ? 40 : 46, der: 6, arr: 30, aba: 30, angosto,
    };
    const n = 168;
    const todos = [semana.real, ...RETRASOS.map((d) => semana.pred[d])].flat().filter((v) => v !== null);
    const { tope, paso } = escalaVertical(Math.max(...todos, 1));
    const x = (i) => dm.izq + (i / (n - 1)) * (dm.w - dm.izq - dm.der);
    const y = (v) => dm.arr + (1 - v / tope) * (dm.h - dm.arr - dm.aba);
    const svg = svgNuevo(lienzo, dm.w, dm.h);

    const fondo = nodo("g", {}, svg);
    for (let dia = 0; dia < 7; dia++) {
      const i = dia * 24;
      if (i >= semana.real.length) break;
      const nombre = S.feriados[isoDia(instante(semana.inicio, i))];
      if (!nombre) continue;
      const x0 = x(Math.max(0, i - 0.5));
      const x1 = x(Math.min(n - 1, i + 23.5));
      nodo("rect", { class: "banda-feriado", x: x0, y: dm.arr, width: x1 - x0, height: dm.h - dm.arr - dm.aba }, fondo);
      texto(fondo, x0 + 6, dm.arr + 15, "Feriado", { class: "rotulo" });
    }

    const rejilla = nodo("g", { class: "rejilla" }, svg);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let v = 0; v <= tope; v += paso) {
      nodo("line", { x1: dm.izq, x2: dm.w - dm.der, y1: y(v), y2: y(v) }, rejilla);
      texto(eje, dm.izq - 8, y(v) + 4, num(v), { "text-anchor": "end" });
    }
    texto(eje, 0, 12, "viajes por hora", { class: "fuerte" });
    for (let dia = 0; dia < 7; dia++) {
      const i = dia * 24;
      if (i > 0 && i < n) nodo("line", { class: "dia", x1: x(i - 0.5), x2: x(i - 0.5), y1: dm.arr, y2: dm.h - dm.aba }, rejilla);
      if (i < semana.real.length) {
        const f = instante(semana.inicio, i);
        texto(eje, x(Math.min(i + 11.5, n - 1)), dm.h - 9, dm.angosto ? diaCorto(f) : diaConMes(f), { "text-anchor": "middle" });
      }
    }

    if (semana.real.length < n) {
      texto(svg, x((semana.real.length + n) / 2), dm.arr + (dm.h - dm.arr - dm.aba) / 2, "Fin del periodo de prueba",
        { class: "rotulo", "text-anchor": "middle" });
    }
    lienzo.setAttribute("aria-label", `Viajes reales y pronosticados, hora por hora, semana del ${rangoSemana(semana)} de 2025. ` +
      "Los valores están en la tabla que se abre debajo del gráfico.");
    const areaError = nodo("path", { class: "area-error" }, svg);
    nodo("path", { class: "linea-real", d: trazo(semana.real, x, y) }, svg);
    const lineaPred = nodo("path", { class: "linea-pred" }, svg);
    const cursor = nodo("g", { class: "cursor", visibility: "hidden" }, svg);
    const guia = nodo("line", { y1: dm.arr, y2: dm.h - dm.aba }, cursor);
    const puntoReal = nodo("circle", { r: 3.5, class: "punto-real" }, cursor);
    const puntoPred = nodo("circle", { r: 4.5, class: "punto-pred" }, cursor);

    G = { svg, x, y, dm, n, areaError, lineaPred, cursor, guia, puntoReal, puntoPred };
    pintarPrediccion(estado.mostrada || semana.pred[estado.retraso]);
  }

  function pintarPrediccion(pred) {
    estado.mostrada = pred;
    if (!G) return;
    G.lineaPred.setAttribute("d", trazo(pred, G.x, G.y));
    G.areaError.setAttribute("d", areaEntre(semanaActual().real, pred, G.x, G.y));
    if (estado.cursor !== null) mostrarCursor(estado.cursor, false);
  }

  function animarHacia(destino) {
    if (estado.animacion) cancelAnimationFrame(estado.animacion);
    const origen = estado.mostrada;
    if (movimientoReducido.matches || !origen || origen.length !== destino.length) {
      pintarPrediccion(destino);
      return;
    }
    const inicio = performance.now();
    const duracion = 320;
    const paso = (ahora) => {
      const t = Math.min(1, (ahora - inicio) / duracion);
      const e = 1 - Math.pow(1 - t, 3);
      if (t < 1 && !movimientoReducido.matches) {
        pintarPrediccion(destino.map((v, i) => (v === null || origen[i] === null ? v : origen[i] + (v - origen[i]) * e)));
        estado.animacion = requestAnimationFrame(paso);
      } else {
        estado.animacion = null;
        pintarPrediccion(destino);
      }
    };
    estado.animacion = requestAnimationFrame(paso);
  }

  function mostrarCursor(i, anunciar) {
    if (!G) return;
    const semana = semanaActual();
    i = Math.max(0, Math.min(semana.real.length - 1, i));
    estado.cursor = i;
    const real = semana.real[i];
    const pred = semana.pred[estado.retraso][i];
    const predDibujada = estado.mostrada[i];
    const cx = G.x(i);
    G.cursor.setAttribute("visibility", "visible");
    G.guia.setAttribute("x1", cx);
    G.guia.setAttribute("x2", cx);
    for (const [punto, v] of [[G.puntoReal, real], [G.puntoPred, predDibujada]]) {
      punto.setAttribute("visibility", v === null ? "hidden" : "visible");
      if (v !== null) { punto.setAttribute("cx", cx); punto.setAttribute("cy", G.y(v)); }
    }
    const f = instante(semana.inicio, i);
    const visto = instante(semana.inicio, i - estado.retraso);
    const cuando = `${diaConMes(f)} · ${hora(f)}`;
    const ultimo = `${diaConMes(visto)}, ${hora(visto)}`;
    if (real === null) {
      globo.innerHTML = `<div><b>${cuando}</b></div><div class="visto">Hora fuera de la comparación: su conteo, o uno que el modelo necesitaba, quedó marcado como dudoso.</div>`;
    } else {
      globo.innerHTML =
        `<div><b>${cuando}</b></div>` +
        `<div class="fila"><span>Viajes reales</span><b>${num(real)}</b></div>` +
        `<div class="fila pred"><span>Pronóstico</span><b>${num(pred)}</b></div>` +
        `<div class="fila"><span>Error</span><span>${num(Math.abs(pred - real))}</span></div>` +
        `<div class="visto">Último dato que veía el modelo: <b>${ultimo}</b></div>`;
    }
    const anchoGlobo = globo.offsetWidth;
    let izquierda = cx + 14;
    if (izquierda + anchoGlobo > G.dm.w) izquierda = cx - 14 - anchoGlobo;
    globo.style.left = `${Math.max(0, izquierda)}px`;
    globo.style.top = `${G.dm.arr}px`;
    globo.dataset.visible = "true";
    if (anunciar) {
      voz.textContent = real === null
        ? `${cuando}: hora fuera de la comparación.`
        : `${cuando}: ${num(real)} viajes reales, pronóstico ${num(pred)}. Último dato visto: ${ultimo}.`;
    }
  }

  function ocultarCursor() {
    estado.cursor = null;
    if (G) G.cursor.setAttribute("visibility", "hidden");
    globo.dataset.visible = "false";
  }

  function indiceDesde(evento) {
    const caja = G.svg.getBoundingClientRect();
    const px = (evento.clientX - caja.left) * (G.dm.w / caja.width);
    return Math.round(((px - G.dm.izq) / (G.dm.w - G.dm.izq - G.dm.der)) * (G.n - 1));
  }

  function alPuntero(e) {
    if (!G) return;
    const i = indiceDesde(e);
    if (i > semanaActual().real.length - 1) { ocultarCursor(); return; }
    mostrarCursor(Math.max(0, i), false);
  }
  lienzo.addEventListener("pointermove", alPuntero);
  lienzo.addEventListener("pointerdown", alPuntero);
  // Escape cierra el globo aunque el foco no esté en el gráfico (WCAG 1.4.13).
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && globo.dataset.visible === "true") ocultarCursor();
  });
  lienzo.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") ocultarCursor(); });
  lienzo.addEventListener("blur", ocultarCursor);
  lienzo.addEventListener("keydown", (e) => {
    const semana = semanaActual();
    let i = estado.cursor ?? 7;
    const flechas = { ArrowLeft: -1, ArrowRight: 1 };
    if (e.key in flechas) i += flechas[e.key] * (e.shiftKey ? 24 : 1);
    else if (e.key === "Home") i = 0;
    else if (e.key === "End") i = semana.real.length - 1;
    else if (e.key === "Escape") { ocultarCursor(); return; }
    else return;
    e.preventDefault();
    mostrarCursor(i, true);
  });

  function actualizarLectura() {
    const d = estado.retraso;
    const mae = D.metricas[d].boosting.mae;
    const parte = (100 * mae) / D.cifras.media_real_prueba;
    lectura.innerHTML =
      `Con el último dato de ${EDAD[d].larga}, el mejor modelo se equivoca en promedio ` +
      `<span class="cifra-edad">${num(mae)} viajes por hora</span> en el semestre de prueba: el ${num(parte)}&nbsp;% ` +
      `de lo que se mueve en una hora promedio. En la semana del gráfico, ${num(semanaActual().mae[d])}.`;
  }

  function rangoSemana(semana) {
    const a = instante(semana.inicio, 0);
    const b = instante(semana.inicio, semana.real.length - 1);
    return a.getUTCMonth() === b.getUTCMonth()
      ? `${a.getUTCDate()} al ${b.getUTCDate()} ${MESES[b.getUTCMonth()]}`
      : `${a.getUTCDate()} ${MESES[a.getUTCMonth()]} al ${b.getUTCDate()} ${MESES[b.getUTCMonth()]}`;
  }

  function rangoCorto(semana) {
    const a = instante(semana.inicio, 0);
    const b = instante(semana.inicio, semana.real.length - 1);
    return a.getUTCMonth() === b.getUTCMonth()
      ? `${a.getUTCDate()}–${b.getUTCDate()} ${MESES[b.getUTCMonth()]}`
      : `${a.getUTCDate()} ${MESES[a.getUTCMonth()]} – ${b.getUTCDate()} ${MESES[b.getUTCMonth()]}`;
  }

  function actualizarSemana() {
    const semana = semanaActual();
    let extra = "";
    if (estado.semana === S.tipica) extra = " · típica";
    if (semana.real.length < 168) extra = ` · ${Math.round(semana.real.length / 24)} días`;
    etiquetaSemana.innerHTML = `<b>${rangoCorto(semana)}</b>${extra}`;
    etiquetaSemana.setAttribute("aria-label", `Semana del ${rangoSemana(semana)}${estado.semana === S.tipica ? ", la más parecida al promedio" : ""}`);
    antes.disabled = estado.semana === 0;
    despues.disabled = estado.semana === S.lista.length - 1;
  }

  function construirTablaSemana() {
    const caja = detalles.querySelector(".tabla-desplazable");
    const semana = semanaActual();
    const d = estado.retraso;
    const tabla = document.createElement("table");
    tabla.className = "tabla";
    tabla.innerHTML =
      `<caption>Semana del ${rangoSemana(semana)} de 2025, dato de ${EDAD[d].larga}.</caption>` +
      "<thead><tr><th scope=\"col\">Hora</th><th scope=\"col\">Reales</th><th scope=\"col\">Pronóstico</th><th scope=\"col\">Error</th></tr></thead>";
    const cuerpo = document.createElement("tbody");
    semana.real.forEach((real, i) => {
      const pred = semana.pred[d][i];
      const fila = document.createElement("tr");
      const f = instante(semana.inicio, i);
      const celdas = [`${diaConMes(f)} ${hora(f)}`, num(real), num(pred), real === null || pred === null ? "—" : num(Math.abs(pred - real))];
      celdas.forEach((contenido, k) => {
        const celda = document.createElement(k === 0 ? "th" : "td");
        if (k === 0) celda.scope = "row";
        celda.textContent = contenido;
        fila.appendChild(celda);
      });
      cuerpo.appendChild(fila);
    });
    tabla.appendChild(cuerpo);
    caja.replaceChildren(tabla);
  }
  detalles.addEventListener("toggle", () => { if (detalles.open) construirTablaSemana(); });

  function cambiarRetraso(d) {
    if (d === estado.retraso) return;
    estado.retraso = d;
    figura.dataset.retraso = String(d);
    botonesEdad.forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.retraso) === d)));
    animarHacia(semanaActual().pred[d]);
    actualizarLectura();
    if (detalles.open) construirTablaSemana();
  }
  botonesEdad.forEach((b) => b.addEventListener("click", () => cambiarRetraso(Number(b.dataset.retraso))));

  function cambiarSemana(k) {
    const nueva = Math.max(0, Math.min(S.lista.length - 1, k));
    if (nueva === estado.semana) return;
    estado.semana = nueva;
    estado.mostrada = null;
    if (estado.animacion) cancelAnimationFrame(estado.animacion);
    ocultarCursor();
    dibujarEdad();
    actualizarLectura();
    actualizarSemana();
    if (detalles.open) construirTablaSemana();
    tira.marcar();
  }
  antes.addEventListener("click", () => cambiarSemana(estado.semana - 1));
  despues.addEventListener("click", () => cambiarSemana(estado.semana + 1));

  /* ---------- Qué ve el modelo ---------- */

  function dibujarVista(ancho) {
    const caja = document.getElementById("grafico-vista");
    const angosto = ancho < 520;
    const izq = angosto ? 74 : 96;
    const der = 12;
    const fila = 40;
    const arr = 28;
    const alto = arr + fila * 3 + 34;
    const svg = svgNuevo(caja, ancho, alto);
    const x = (h) => izq + ((h + 170) / 170) * (ancho - izq - der);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let dia = 7; dia >= 0; dia--) {
      const xx = x(-dia * 24);
      nodo("line", { class: "guia", x1: xx, x2: xx, y1: arr - 6, y2: arr + fila * 3 - 6 }, svg);
      if (!angosto || dia % 2 === 1 || dia === 0) {
        texto(eje, xx, arr + fila * 3 + 14, dia === 0 ? "ahora" : `−${dia} d`, { "text-anchor": dia === 0 ? "end" : "middle" });
      }
    }
    texto(eje, x(0), 12, "hora a pronosticar", { "text-anchor": "end", class: "fuerte" });
    RETRASOS.forEach((d, k) => {
      const yy = arr + k * fila + 8;
      const c = color(EDAD[d].color);
      nodo("line", { x1: x(-170), x2: x(0), y1: yy, y2: yy, stroke: color("--linea"), "stroke-width": 1 }, svg);
      nodo("rect", { x: x(-d), y: yy - 7, width: x(0) - x(-d), height: 14, fill: color(EDAD[d].suave) }, svg);
      if (d > 1 && x(0) - x(-d) > 90) {
        texto(svg, x(0) - 8, yy + 4, "sin datos todavía", { class: "rotulo", "text-anchor": "end" });
      }
      nodo("circle", { cx: x(-d), cy: yy, r: 5, fill: c }, svg);
      nodo("circle", { cx: x(0), cy: yy, r: 4.5, fill: color("--papel"), stroke: color("--tinta"), "stroke-width": 1.5 }, svg);
      texto(svg, 0, yy + 4, EDAD[d].corta, { class: "rotulo-serie", fill: c, style: `fill:${c}` });
    });
    texto(eje, izq, alto - 2, "● último conteo que ve el modelo", { fill: color("--tinta-2") });
  }

  /* ---------- Perfil diario ---------- */

  function dibujarPerfil(ancho) {
    const caja = document.getElementById("grafico-perfil");
    const angosto = ancho < 520;
    const dm = { w: ancho, h: angosto ? 250 : 280, izq: 40, der: 8, arr: 26, aba: 50 };
    const svg = svgNuevo(caja, dm.w, dm.h);
    const p = D.cifras.perfil;
    const { tope, paso } = escalaVertical(Math.max(...p.laborable));
    const x = (h) => dm.izq + (h / 23) * (dm.w - dm.izq - dm.der);
    const y = (v) => dm.arr + (1 - v / tope) * (dm.h - dm.arr - dm.aba);
    const rejilla = nodo("g", { class: "rejilla" }, svg);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let v = 0; v <= tope; v += paso) {
      nodo("line", { x1: dm.izq, x2: dm.w - dm.der, y1: y(v), y2: y(v) }, rejilla);
      texto(eje, dm.izq - 8, y(v) + 4, num(v), { "text-anchor": "end" });
    }
    texto(eje, 0, 12, "viajes por hora", { class: "fuerte" });
    for (const h of [0, 6, 12, 18, 23]) texto(eje, x(h), dm.h - dm.aba + 18, `${h}:00`, { "text-anchor": h === 0 ? "start" : h === 23 ? "end" : "middle" });
    nodo("path", { class: "serie-referencia", d: trazo(p.domingo_o_feriado, x, y) }, svg);
    nodo("path", { class: "serie-secundaria", d: trazo(p.sabado, x, y) }, svg);
    nodo("path", { class: "serie-principal", d: trazo(p.laborable, x, y) }, svg);
    const pico = D.cifras.pico_laborable;
    const maximo = (serie) => { const v = Math.max(...serie); return `${num(v)} a las ${serie.indexOf(v)}:00`; };
    caja.setAttribute("aria-label", `Viajes promedio por hora del día, 2022 a 2024. Laborable: subida a las 8:00 ` +
      `(${num(p.laborable[8])}) y máximo de ${num(pico.viajes)} a las ${pico.hora}:00. Sábado: máximo de ${maximo(p.sabado)}. ` +
      `Domingo o feriado: máximo de ${maximo(p.domingo_o_feriado)}.`);
    texto(svg, x(pico.hora) - 10, y(pico.viajes) + 4, `${num(pico.viajes)} viajes a las ${pico.hora}:00`, { class: "rotulo-serie", "text-anchor": "end" });
    leyendaLineas(svg, dm.izq, dm.h - 6, [
      ["serie-principal", "Laborable"], ["serie-secundaria", "Sábado"], ["serie-referencia", angosto ? "Dom. o feriado" : "Domingo o feriado"]]);
  }

  // Leyenda de líneas en una fila: muestra de 20 px y texto.
  function leyendaLineas(svg, x0, y, items) {
    let x = x0;
    items.forEach(([clase, nombre]) => {
      nodo("path", { class: clase, d: `M${x} ${y - 4}h20` }, svg);
      const t = texto(svg, x + 26, y, nombre, { class: "rotulo" });
      x += 26 + t.getComputedTextLength() + 18;
    });
  }

  /* ---------- Tramos del protocolo ---------- */

  function dibujarTramos(ancho) {
    const caja = document.getElementById("grafico-tramos");
    const angosto = ancho < 520;
    const alto = 126;
    const svg = svgNuevo(caja, ancho, alto);
    const t = (iso) => { const [a, m, d] = iso.split("-").map(Number); return Date.UTC(a, m - 1, d); };
    const a0 = t("2022-01-01");
    const a1 = t("2026-01-01");
    const x = (iso) => 1 + ((t(iso) - a0) / (a1 - a0)) * (ancho - 2);
    const P = D.particiones;
    const masDias = (iso, dias) => new Date(t(iso) + dias * 864e5).toISOString().slice(0, 10);
    // Cada tramo: desde su inicio (más el margen, salvo el primero) hasta el día siguiente a su último día.
    const tramos = [
      { de: P.entrenamiento[0], a: masDias(P.entrenamiento[1], 1), nombre: "Entrenamiento", fecha: "2022 a 2024", tono: "--tinta-3" },
      { de: masDias(P.validacion[0], P.margen_dias), a: masDias(P.validacion[1], 1), nombre: "Validación", fecha: "ene a jun 2025", tono: "--tinta-2" },
      { de: masDias(P.prueba[0], P.margen_dias), a: masDias(P.prueba[1], 1), nombre: "Prueba", fecha: "jul a dic 2025", tono: "--tinta" },
    ];
    const eje = nodo("g", { class: "eje" }, svg);
    const finAjuste = x(masDias(P.validacion[1], 1));
    texto(eje, 1, 12, angosto ? "Ajuste final: 2022 a junio de 2025" : "Ajuste final de los modelos elegidos: enero de 2022 a junio de 2025", { class: "fuerte" });
    nodo("path", { d: `M1.5 28V22.5H${finAjuste - 0.5}V28`, fill: "none", stroke: color("--tinta-3"), "stroke-width": 1 }, svg);
    const yB = 36;
    tramos.forEach((tr) => {
      nodo("rect", { x: x(tr.de), y: yB, width: Math.max(2, x(tr.a) - x(tr.de) - 1), height: 14, fill: color(tr.tono), rx: 2 }, svg);
    });
    // Rótulos: entrenamiento a la izquierda; validación y prueba, alineados a su final y en filas distintas.
    const rotulos = [
      { tr: tramos[0], xx: x(tramos[0].de), ancla: "start", fila: 0 },
      { tr: tramos[1], xx: x(tramos[1].a) - 1, ancla: "end", fila: 0 },
      { tr: tramos[2], xx: x(tramos[2].a) - 1, ancla: "end", fila: 1 },
    ];
    rotulos.forEach(({ tr, xx, ancla, fila }) => {
      const y0 = yB + 32 + fila * 36;
      if (fila) nodo("line", { x1: xx - 0.5, x2: xx - 0.5, y1: yB + 16, y2: y0 - 12, stroke: color("--linea") }, svg);
      texto(svg, xx, y0, tr.nombre, { class: "rotulo-serie", "text-anchor": ancla });
      texto(eje, xx, y0 + 15, tr.fecha, { "text-anchor": ancla });
    });
  }

  /* ---------- Resultados: error según la edad del dato ---------- */

  const NOMBRES = {
    boosting: { largo: "Boosting", corto: "Boosting", clase: "serie-principal" },
    mlp: { largo: "Perceptrón", corto: "Perceptrón", clase: "serie-secundaria" },
    ridge: { largo: "Ridge", corto: "Ridge", clase: "serie-secundaria" },
    ingenuo_semanal: { largo: "Ingenuo semanal", corto: "Ingenuo", clase: "serie-referencia" },
    mediana_calendario: { largo: "Mediana de calendario", corto: "Mediana", clase: "serie-referencia" },
    boosting_clima: { largo: "Boosting + clima", corto: "+ clima", clase: "serie-clima" },
  };

  function dibujarPendiente(ancho) {
    const caja = document.getElementById("grafico-pendiente");
    const angosto = ancho < 520;
    const dm = { w: ancho, h: angosto ? 280 : 320, izq: 40, der: angosto ? 118 : 178, arr: 26, aba: 34 };
    const svg = svgNuevo(caja, dm.w, dm.h);
    const metodos = Object.keys(NOMBRES);
    const maximo = Math.max(...metodos.flatMap((m) => RETRASOS.map((d) => D.metricas[d][m].mae)));
    const { tope, paso } = escalaVertical(maximo);
    const x = (k) => dm.izq + 14 + (k / 2) * (dm.w - dm.izq - dm.der - 28);
    const y = (v) => dm.arr + (1 - v / tope) * (dm.h - dm.arr - dm.aba);
    const rejilla = nodo("g", { class: "rejilla" }, svg);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let v = 0; v <= tope; v += paso) {
      nodo("line", { x1: dm.izq, x2: dm.w - dm.der + 8, y1: y(v), y2: y(v) }, rejilla);
      texto(eje, dm.izq - 8, y(v) + 4, num(v), { "text-anchor": "end" });
    }
    texto(eje, 0, 12, "error medio (viajes por hora)", { class: "fuerte" });
    RETRASOS.forEach((d, k) => {
      const c = color(EDAD[d].color);
      nodo("circle", { cx: x(k) - (angosto ? 26 : 30), cy: dm.h - 13, r: 4, fill: c }, svg);
      texto(eje, x(k) - (angosto ? 19 : 22), dm.h - 9, EDAD[d].corta, { class: "fuerte" });
    });
    caja.setAttribute("aria-label", "Error medio de cada método con el dato de 1 hora, 1 día y 1 semana: " +
      metodos.map((m) => `${NOMBRES[m].largo}, ${RETRASOS.map((d) => num(D.metricas[d][m].mae, 1)).join(", ")}`).join("; ") + ".");
    const finales = [];
    metodos.slice().reverse().forEach((m) => {
      const valores = RETRASOS.map((d) => D.metricas[d][m].mae);
      nodo("path", { class: NOMBRES[m].clase, d: trazo(valores, x, y) }, svg);
      if (m === "boosting" || m === "boosting_clima") {
        valores.forEach((v, k) => nodo("circle", { cx: x(k), cy: y(v), r: m === "boosting" ? 3.5 : 2.5, fill: color("--tinta") }, svg));
      }
      finales.push({ m, v: valores[2] });
    });
    const yEtiquetas = separar(finales.map((f) => y(f.v)), 15, dm.arr, dm.h - dm.aba);
    finales.forEach((f, k) => {
      const yy = yEtiquetas[k];
      const fuerte = f.m === "boosting";
      if (Math.abs(yy - y(f.v)) > 3) {
        nodo("path", { d: `M${x(2) + 4} ${y(f.v)}L${x(2) + 12} ${yy}`, stroke: color("--linea"), fill: "none" }, svg);
      }
      texto(svg, x(2) + 16, yy + 4, `${angosto ? NOMBRES[f.m].corto : NOMBRES[f.m].largo} ${num(f.v, 1)}`,
        { class: `rotulo-serie${fuerte ? "" : " suave"}` });
    });
  }

  /* ---------- Las 26 semanas ---------- */

  const tira = { marcar: () => {} };

  function dibujarSemanas(ancho) {
    const caja = document.getElementById("grafico-semanas");
    const angosto = ancho < 520;
    const dm = { w: ancho, h: angosto ? 230 : 250, izq: 40, der: 6, arr: 26, aba: 30 };
    const svg = svgNuevo(caja, dm.w, dm.h);
    const n = S.lista.length;
    const maximo = Math.max(...S.lista.flatMap((s) => RETRASOS.map((d) => s.mae[d])).filter((v) => v !== null));
    const { tope, paso } = escalaVertical(maximo);
    const banda = (dm.w - dm.izq - dm.der) / n;
    const x = (k) => dm.izq + banda * (k + 0.5);
    const y = (v) => dm.arr + (1 - v / tope) * (dm.h - dm.arr - dm.aba);
    const rejilla = nodo("g", { class: "rejilla" }, svg);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let v = 0; v <= tope; v += paso) {
      nodo("line", { x1: dm.izq, x2: dm.w - dm.der, y1: y(v), y2: y(v) }, rejilla);
      texto(eje, dm.izq - 8, y(v) + 4, num(v), { "text-anchor": "end" });
    }
    texto(eje, 0, 12, "error medio de la semana", { class: "fuerte" });
    let mesAnterior = -1;
    S.lista.forEach((s, k) => {
      const f = instante(s.inicio, 0);
      if (f.getUTCMonth() !== mesAnterior) {
        mesAnterior = f.getUTCMonth();
        texto(eje, x(k) - banda / 2, dm.h - 9, MESES[mesAnterior], { "text-anchor": "start" });
      }
    });
    const marca = nodo("rect", { y: dm.arr - 6, height: dm.h - dm.arr - dm.aba + 6, width: banda, fill: color("--papel-2"), rx: 2 }, svg);
    marca.parentNode.insertBefore(marca, rejilla);
    const r = angosto ? 2.75 : 3.5;
    S.lista.forEach((s, k) => {
      const valores = RETRASOS.map((d) => s.mae[d]);
      if (valores.some((v) => v === null)) return;  // semana sin horas evaluadas: no hay nada que dibujar
      const columna = nodo("rect", { class: "columna-semana", x: dm.izq + banda * k, y: dm.arr - 6, width: banda, height: dm.h - dm.arr - dm.aba + 6 }, svg);
      const g = nodo("g", { class: "puntos-semana" }, svg);
      nodo("line", { x1: x(k), x2: x(k), y1: y(Math.min(...valores)), y2: y(Math.max(...valores)), stroke: color("--linea"), "stroke-width": 1.5 }, g);
      RETRASOS.forEach((d) => nodo("circle", { class: "punto-semana", cx: x(k), cy: y(s.mae[d]), r, fill: color(EDAD[d].color) }, g));
      const titulo = nodo("title", {}, columna);
      titulo.textContent = `Semana del ${rangoSemana(s)}: ${RETRASOS.map((d) => `${EDAD[d].corta} ${num(s.mae[d])}`).join(" · ")}`;
      columna.addEventListener("click", () => {
        cambiarSemana(k);
        figura.scrollIntoView({ behavior: movimientoReducido.matches ? "auto" : "smooth", block: "start" });
      });
    });
    tira.marcar = () => { marca.setAttribute("x", dm.izq + banda * estado.semana); };
    tira.marcar();
    caja.setAttribute("aria-label", `Error del boosting en cada una de las ${n} semanas de prueba con el dato de 1 hora, ` +
      `1 día y 1 semana. En ${S.error_crece_en} de ${S.semanas_con_datos} semanas el error crece con la edad del dato. ` +
      "Los valores están en la tabla que se abre debajo.");
  }

  const detallesSemanas = document.getElementById("tabla-semanas");
  function construirTablaSemanas() {
    const tabla = document.createElement("table");
    tabla.className = "tabla";
    tabla.innerHTML = "<caption>Error medio del boosting en cada semana de prueba, en viajes por hora.</caption>" +
      "<thead><tr><th scope=\"col\">Semana</th><th scope=\"col\">1 hora</th><th scope=\"col\">1 día</th>" +
      "<th scope=\"col\">1 semana</th><th scope=\"col\"><span class=\"solo-lector\">Acción</span></th></tr></thead>";
    const cuerpo = document.createElement("tbody");
    S.lista.forEach((s, k) => {
      const fila = document.createElement("tr");
      const cabeza = document.createElement("th");
      cabeza.scope = "row";
      cabeza.textContent = rangoSemana(s);
      fila.appendChild(cabeza);
      RETRASOS.forEach((d) => {
        const celda = document.createElement("td");
        celda.textContent = num(s.mae[d], 1);
        fila.appendChild(celda);
      });
      const accion = document.createElement("td");
      const boton = document.createElement("button");
      boton.type = "button";
      boton.className = "boton-texto";
      boton.textContent = "Ver arriba";
      boton.setAttribute("aria-label", `Ver la semana del ${rangoSemana(s)} en el gráfico principal`);
      boton.addEventListener("click", () => {
        cambiarSemana(k);
        figura.scrollIntoView({ behavior: movimientoReducido.matches ? "auto" : "smooth", block: "start" });
        lienzo.focus({ preventScroll: true });
      });
      accion.appendChild(boton);
      fila.appendChild(accion);
      cuerpo.appendChild(fila);
    });
    tabla.appendChild(cuerpo);
    detallesSemanas.querySelector(".tabla-desplazable").replaceChildren(tabla);
  }
  detallesSemanas.addEventListener("toggle", () => {
    if (detallesSemanas.open && !detallesSemanas.querySelector("table")) construirTablaSemanas();
  });

  /* ---------- Clima ---------- */

  function dibujarClima(ancho) {
    const caja = document.getElementById("grafico-clima");
    const angosto = ancho < 520;
    const dm = { w: ancho, izq: angosto ? 72 : 92, der: 16, arr: 30, fila: 40 };
    const alto = dm.arr + dm.fila * 3 + 26;
    const svg = svgNuevo(caja, dm.w, alto);
    const maximo = Math.max(...RETRASOS.map((d) => D.metricas[d].boosting.mae));
    const { tope, paso } = escalaVertical(maximo);
    const x = (v) => dm.izq + (v / tope) * (dm.w - dm.izq - dm.der);
    const rejilla = nodo("g", { class: "rejilla" }, svg);
    const eje = nodo("g", { class: "eje" }, svg);
    for (let v = 0; v <= tope; v += paso) {
      nodo("line", { x1: x(v), x2: x(v), y1: dm.arr - 8, y2: dm.arr + dm.fila * 3 - 8 }, rejilla);
      texto(eje, x(v), dm.arr + dm.fila * 3 + 8, num(v), { "text-anchor": "middle" });
    }
    texto(eje, 0, 12, "error medio del boosting (viajes por hora)", { class: "fuerte" });
    RETRASOS.forEach((d, k) => {
      const yy = dm.arr + k * dm.fila + 8;
      const c = color(EDAD[d].color);
      const sin = D.metricas[d].boosting.mae;
      const con = D.metricas[d].boosting_clima.mae;
      texto(svg, 0, yy + 4, EDAD[d].corta, { class: "rotulo-serie", style: `fill:${c}` });
      nodo("line", { x1: x(con), x2: x(sin), y1: yy, y2: yy, stroke: c, "stroke-width": 2 }, svg);
      nodo("circle", { cx: x(sin), cy: yy, r: 5, fill: color("--papel"), stroke: c, "stroke-width": 2 }, svg);
      nodo("circle", { cx: x(con), cy: yy, r: 5, fill: c }, svg);
      // Si los dos puntos casi se tocan, un solo rótulo a la derecha; si no, cada valor junto a su punto.
      const juntos = x(sin) - x(con) < 16;
      texto(svg, x(sin) + 10, yy + 4, juntos ? `${num(sin, 1)} → ${num(con, 1)}` : num(sin, 1), { class: "rotulo-valor" });
      if (!juntos) texto(svg, x(con) - 10, yy + 4, num(con, 1), { class: "rotulo-valor", "text-anchor": "end" });
    });
    caja.setAttribute("aria-label", "Error del boosting sin clima y con clima observado: " +
      RETRASOS.map((d) => `dato de ${EDAD[d].corta}, ${num(D.metricas[d].boosting.mae, 1)} y ${num(D.metricas[d].boosting_clima.mae, 1)}`).join("; ") + ".");
    const leyenda = nodo("g", { class: "eje" }, svg);
    nodo("circle", { cx: dm.w - 196, cy: 8, r: 4, fill: color("--papel"), stroke: color("--tinta-2"), "stroke-width": 1.5 }, leyenda);
    texto(leyenda, dm.w - 188, 12, "sin clima", {});
    nodo("circle", { cx: dm.w - 120, cy: 8, r: 4, fill: color("--tinta-2") }, leyenda);
    texto(leyenda, dm.w - 112, 12, "con clima", {});
    if (angosto) leyenda.setAttribute("transform", `translate(0 ${alto - 4 - 12 + 4}) translate(${-(dm.w - 196) + dm.izq} 0)`);
  }

  /* ---------- Navegación: sección visible ---------- */

  const enlaces = new Map([...document.querySelectorAll(".secciones a")].map((a) => [a.hash.slice(1), a]));
  const visibles = new Set();
  const observador = new IntersectionObserver((entradas) => {
    entradas.forEach((e) => (e.isIntersecting ? visibles.add(e.target.id) : visibles.delete(e.target.id)));
    const primera = [...enlaces.keys()].find((id) => visibles.has(id));
    enlaces.forEach((a, id) => a.setAttribute("aria-current", String(id === primera)));
  }, { rootMargin: "-30% 0px -60% 0px" });
  enlaces.forEach((_, id) => { const s = document.getElementById(id); if (s) observador.observe(s); });

  /* ---------- Arranque ---------- */

  actualizarLectura();
  actualizarSemana();
  alCambiarAncho(lienzo, (a) => { dibujarEdad(a); if (estado.cursor !== null) mostrarCursor(estado.cursor, false); });
  alCambiarAncho(document.getElementById("grafico-vista"), dibujarVista);
  alCambiarAncho(document.getElementById("grafico-perfil"), dibujarPerfil);
  alCambiarAncho(document.getElementById("grafico-tramos"), dibujarTramos);
  alCambiarAncho(document.getElementById("grafico-pendiente"), dibujarPendiente);
  alCambiarAncho(document.getElementById("grafico-semanas"), dibujarSemanas);
  alCambiarAncho(document.getElementById("grafico-clima"), dibujarClima);

  // Si cambia el modo claro u oscuro, se redibujan los gráficos que usan colores calculados.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    for (const [id, f] of [["grafico-vista", dibujarVista], ["grafico-tramos", dibujarTramos], ["grafico-pendiente", dibujarPendiente],
      ["grafico-semanas", dibujarSemanas], ["grafico-clima", dibujarClima]]) {
      const c = document.getElementById(id);
      if (c.clientWidth) f(Math.round(c.clientWidth));
    }
  });
})();
