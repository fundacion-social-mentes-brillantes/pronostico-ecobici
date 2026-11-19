"""Arma la memoria en PDF con diseño editorial, a partir de los mismos capítulos en Markdown que el Word.

Uso: .venv/Scripts/python memoria/construir_pdf.py
Necesita Microsoft Edge o Google Chrome. Hace dos pasadas: en la primera el navegador imprime el documento con
marcadores (uno por título) y de ahí sale la página de cada título; en la segunda esas páginas se escriben en el
índice. Las figuras son los SVG de resultados/figuras (vectoriales) y las letras, las de web/fuentes.
Contrato de diseño: DESIGN.md (sección «PDF de la memoria»).
Salidas: memoria/memoria.pdf y, como paso intermedio, memoria/memoria.html (no se sube al repositorio).
"""
import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pypdf
from pypdf.generic import NameObject, TextStringObject

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construir_docx import ORDEN, PIES, TITULO, TOKEN, cargar_pies  # noqa: E402  (mismo orden y pies que el Word)

RAIZ = Path(__file__).resolve().parent.parent
MEMORIA = RAIZ / "memoria"
SALIDA = MEMORIA / "memoria.pdf"
INTERMEDIO = MEMORIA / "memoria.html"
SUBTITULO = "Cuánto empeora el pronóstico cuando el último conteo tiene una hora, un día o una semana de antigüedad"
WEB = "https://fundacion-social-mentes-brillantes.github.io/pronostico-ecobici/"
REPOSITORIO = "https://github.com/fundacion-social-mentes-brillantes/pronostico-ecobici"

NAVEGADORES = [
    Path(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)")) / "Microsoft/Edge/Application/msedge.exe",
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Microsoft/Edge/Application/msedge.exe",
    Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe",
]


# ---------------------------------------------------------------- Texto en línea

SIMBOLOS = {r"\alpha": "α", r"\in": "∈", r"\sum": "∑", r"\log": "log", r"\exp": "exp", r"\times": "×",
            r"\le": "≤", r"\ge": "≥", r"\cdot": "·", r"\approx": "≈", r"\neq": "≠", r"\left": "", r"\right": "",
            r"\,": " "}


def argumento(s, i):
    """Devuelve (contenido, posición siguiente) del grupo {…} que empieza en s[i], o el carácter suelto."""
    if s[i] != "{":
        return s[i], i + 1
    nivel, j = 0, i
    while j < len(s):
        nivel += {"{": 1, "}": -1}.get(s[j], 0)
        if nivel == 0:
            return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def mate(s):
    """LaTeX en línea sencillo → HTML (variables en cursiva, subíndices, superíndices, raíz con vínculo)."""
    salida, i = [], 0
    while i < len(s):
        if s.startswith(r"\{", i) or s.startswith(r"\}", i):
            salida.append(s[i + 1])
            i += 2
        elif s.startswith(r"\hat", i):
            i += 4
            while s[i] == " ":
                i += 1
            letra, i = argumento(s, i)
            salida.append("ŷ" if letra == "y" else letra + "\u0302")
        elif s.startswith(r"\sqrt", i):
            dentro, i = argumento(s, i + 5)
            salida.append(f'√<span class="raiz">{mate(dentro)}</span>')
        elif s[i] in "_^":
            etiqueta = "sub" if s[i] == "_" else "sup"
            dentro, i = argumento(s, i + 1)
            salida.append(f"<{etiqueta}>{mate(dentro)}</{etiqueta}>")
        elif s[i] == "\\":
            comando = re.match(r"\\[a-zA-Z]+|\\.", s[i:]).group(0)
            salida.append(SIMBOLOS.get(comando, comando.lstrip("\\")))
            i += len(comando)
        elif s[i] in "{}":
            i += 1
        elif s[i] == "-":
            salida.append("−")
            i += 1
        elif s[i].isalpha():
            salida.append(f"<i>{s[i]}</i>")
            i += 1
        else:
            salida.append(html.escape(s[i]))
            i += 1
    return "".join(salida)


def url_partible(url):
    """URL con puntos de corte después de / . - _ para que no se salga del renglón."""
    return re.sub(r"([/.\-_?=&])", r"\1<wbr>", html.escape(url))


def en_linea(texto):
    partes = []
    for trozo in TOKEN.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**") and len(trozo) > 4:
            partes.append(f"<strong>{en_linea(trozo[2:-2])}</strong>")
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            partes.append(f"<em>{en_linea(trozo[1:-1])}</em>")
        elif trozo.startswith("`") and trozo.endswith("`"):
            partes.append(f"<code>{html.escape(trozo[1:-1])}</code>")
        elif trozo.startswith("$") and trozo.endswith("$") and len(trozo) > 2:
            partes.append(f'<span class="mate">{mate(trozo[1:-1])}</span>')
        elif trozo.startswith("[") and "](" in trozo:
            txt, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", trozo).groups()
            partes.append(f'<a href="{html.escape(url)}">{en_linea(txt)}</a>')
        elif trozo.startswith("http"):
            partes.append(f'<a class="url" href="{html.escape(trozo)}">{url_partible(trozo)}</a>')
        else:
            partes.append(VOLADAS.sub(exponente, html.escape(trozo, quote=False)))
    return "".join(partes)


# Exponentes escritos con cifras voladas («10⁻³⁵»): se pasan a <sup> con cifras normales, para que todas salgan en la
# misma letra (ninguna de las dos letras del proyecto trae el «menos» volado).
VOLADAS = re.compile("[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+")
NORMALES = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789−")


def exponente(m):
    return f'<sup class="exp">{m.group(0).translate(NORMALES)}</sup>'



# ---------------------------------------------------------------- Bloques

NUMERICO = re.compile(r"^[−\-+]?[\d.,\s]+(\s?%|\s?h|\s?s)?$|^[≈<>~]?\s?[\d.,]+")


def tabla(filas):
    ncol = max(len(f) for f in filas)
    filas = [f + [""] * (ncol - len(f)) for f in filas]
    cuerpo = filas[1:]
    derecha = [c > 0 and sum(bool(NUMERICO.match(f[c])) for f in cuerpo) >= max(1, len(cuerpo) * 0.6)
               for c in range(ncol)]
    salida = ['<div class="tabla"><table>', "<thead><tr>"]
    salida += [f'<th{" class=n" if derecha[c] else ""}>{en_linea(t)}</th>' for c, t in enumerate(filas[0])]
    salida.append("</tr></thead><tbody>")
    for f in cuerpo:
        salida.append("<tr>" + "".join(f'<td{" class=n" if derecha[c] else ""}>{en_linea(t)}</td>'
                                       for c, t in enumerate(f)) + "</tr>")
    salida.append("</tbody></table></div>")
    return "".join(salida)


def figura(nombre):
    svg = RAIZ / "resultados" / "figuras" / f"{nombre}.svg"
    if not svg.exists():
        raise FileNotFoundError(f"Falta la figura {svg} (corre src/graficos.py)")
    alternativo = html.escape(re.sub(r"[*`]", "", PIES.get(nombre, nombre)), quote=True)
    return (f'<figure><img src="../resultados/figuras/{nombre}.svg" alt="{alternativo}">'
            f"<figcaption>{en_linea(PIES.get(nombre, nombre))}</figcaption></figure>")


def titulo(nivel, texto, ident):
    m = re.match(r"^((?:Anexo [A-Z])|(?:\d+(?:\.\d+)*))\.?\s+(.*)$", texto)
    numero, resto = (m.group(1), m.group(2)) if m else ("", texto)
    if nivel == 1 and numero:
        # El número grande va fuera del título; dentro queda «1. » casi invisible, para que el marcador del PDF diga
        # «1. Introducción» y no «1Introducción».
        clase = " anexo" if numero.startswith("Anexo") else ""
        return (f'<div class="num-capitulo{clase}" aria-hidden="true">{html.escape(numero)}</div>'
                f'<h1 id="{ident}"><span class="oculto">{html.escape(numero)}. </span>{en_linea(resto)}</h1>',
                numero, resto)
    num = f'<span class="num">{html.escape(numero)}</span>' if numero else ""
    return f'<h{nivel} id="{ident}">{num} {en_linea(resto)}</h{nivel}>', numero, resto


def volcar(texto, titulos, contador):
    """Markdown de un archivo → HTML. Anota en `titulos` cada título (nivel, id, número, texto)."""
    lineas = texto.split("\n")
    salida, parrafo, lista = [], [], None
    seccion = None

    def cerrar_parrafo():
        nonlocal parrafo
        if parrafo:
            contenido = " ".join(x.strip() for x in parrafo)
            clase = ""
            if contenido.startswith("**Tabla"):
                clase = ' class="pie-tabla"'
            elif seccion == "Referencias":
                clase = ' class="ref"'
            salida.append(f"<p{clase}>{en_linea(contenido)}</p>")
            parrafo = []

    def cerrar_lista():
        nonlocal lista
        if lista:
            salida.append(f"</{lista}>")
            lista = None

    i = 0
    while i < len(lineas):
        l = lineas[i]
        if not l.strip() or l.strip() == "---":
            cerrar_parrafo()
            if not (i + 1 < len(lineas) and re.match(r"^\s*([-*]|\d+\.) ", lineas[i + 1])):
                cerrar_lista()
            i += 1
            continue
        m = re.match(r"^\{\{FIGURA:([\w\-]+)\}\}\s*$", l.strip())
        if m:
            cerrar_parrafo(); cerrar_lista()
            salida.append(figura(m.group(1)))
            i += 1
            continue
        if l.startswith("```"):
            cerrar_parrafo(); cerrar_lista()
            i += 1
            codigo = []
            while i < len(lineas) and not lineas[i].startswith("```"):
                codigo.append(lineas[i])
                i += 1
            salida.append(f"<pre><code>{html.escape(chr(10).join(codigo))}</code></pre>")
            i += 1
            continue
        m = re.match(r"^(#{1,4}) (.*)", l)
        if m:
            cerrar_parrafo(); cerrar_lista()
            nivel = min(len(m.group(1)), 3)
            contador[0] += 1
            ident = f"t{contador[0]}"
            bloque, numero, resto = titulo(nivel, m.group(2).strip(), ident)
            if nivel == 1:
                seccion = resto
                if salida or titulos:
                    salida.append("</section>")
                clase = "capitulo" + ("" if numero else " sin-numero")
                salida.append(f'<section class="{clase}">')
            titulos.append({"nivel": nivel, "id": ident, "numero": numero, "texto": resto})
            salida.append(bloque)
            i += 1
            continue
        if l.startswith("|"):
            cerrar_parrafo(); cerrar_lista()
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            salida.append(tabla(filas))
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)", l)
        if m:
            cerrar_parrafo()
            tipo = "ol" if m.group(2)[0].isdigit() else "ul"
            if lista != tipo:
                cerrar_lista()
                salida.append(f"<{tipo}>")
                lista = tipo
            item = [m.group(3)]
            i += 1
            while i < len(lineas) and lineas[i].startswith("  ") and lineas[i].strip() and not re.match(
                    r"^\s*([-*]|\d+\.) ", lineas[i]):
                item.append(lineas[i].strip())
                i += 1
            valor = f' value="{m.group(2)[:-1]}"' if tipo == "ol" else ""
            salida.append(f"<li{valor}>{en_linea(' '.join(item))}</li>")
            continue
        cerrar_lista()
        parrafo.append(l)
        i += 1
    cerrar_parrafo(); cerrar_lista()
    return "\n".join(salida)


# ---------------------------------------------------------------- Portada

def portada():
    return f"""
<section class="portada">
  <div class="portada-imagen"><img src="portada.jpg" alt="Ilustración: una calle arbolada de Buenos
    Aires de noche, con una estación de bicicletas públicas bajo las farolas y tres estelas de luz (verde aguamarina,
    ámbar y coral) que representan el pronóstico con el dato de 1 hora, 1 día y 1 semana"></div>
  <div class="portada-contenido">
    <p class="portada-tipo">Memoria · Comparativa de soluciones · Aprendizaje automático</p>
    <div class="portada-texto">
      <h1 class="portada-titulo">{html.escape(TITULO)}</h1>
      <p class="portada-sub">{html.escape(SUBTITULO)}</p>
      <p class="portada-edades"><span class="m m-1"></span>dato de 1 hora <span class="m m-24"></span>de 1 día
        <span class="m m-168"></span>de 1 semana</p>
    </div>
    <div class="portada-pie">
      <p>Realizada por <strong>Claude</strong> (Anthropic) y <strong>Codex</strong> (OpenAI) como prueba de
        capacidades, por encargo de la Fundación Social Mentes Brillantes.</p>
      <p>Con la estructura de un Trabajo Fin de Máster en Inteligencia Artificial (comparativa de soluciones). No es un
        trabajo presentado ante ninguna universidad (ver Anexo A). Ilustración de portada generada con IA (Codex).</p>
      <p class="portada-fecha">Noviembre de 2026 · <a href="{WEB}">{url_partible(WEB.removeprefix("https://"))}</a></p>
    </div>
  </div>
</section>"""


def indice(titulos, paginas):
    filas = []
    for t in titulos:
        if t["nivel"] > 2:
            continue
        pagina = paginas.get(t["id"], "")
        num = f'<span class="num">{html.escape(t["numero"])}</span>' if t["numero"] else ""
        filas.append(f'<li class="n{t["nivel"]}"><a href="#{t["id"]}">{num}<span class="txt">{en_linea(t["texto"])}'
                     f'</span><span class="relleno"></span><span class="pag">{pagina}</span></a></li>')
    return f'<section class="indice"><h1 id="indice">Índice</h1><ol>{"".join(filas)}</ol></section>'


def documento(cuerpo, titulos, paginas):
    # Las letras van incrustadas: un archivo local no puede cargar fuentes de otra carpeta (regla CORS del navegador).
    estilos = re.sub(r'url\("FUENTE:([^"]+)"\)', lambda m: 'url("data:font/woff2;base64,' + base64.b64encode(
        (RAIZ / "web" / "fuentes" / m.group(1)).read_bytes()).decode() + '")',
        (MEMORIA / "estilo_pdf.css").read_text(encoding="utf-8"))
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>{html.escape(TITULO)}</title>
<style>{estilos}</style>
</head><body>
{portada()}
{indice(titulos, paginas)}
{cuerpo}
</section>
</body></html>"""


# ---------------------------------------------------------------- Impresión

def navegador():
    for ruta in NAVEGADORES:
        if ruta.exists():
            return ruta
    for nombre in ("msedge", "chrome", "chromium", "google-chrome"):
        if shutil.which(nombre):
            return Path(shutil.which(nombre))
    raise FileNotFoundError("Hace falta Microsoft Edge o Google Chrome para imprimir el PDF")


def imprimir(html_texto, destino):
    INTERMEDIO.write_text(html_texto, encoding="utf-8")
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run([str(navegador()), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        "--generate-pdf-document-outline", "--run-all-compositor-stages-before-draw",
                        "--virtual-time-budget=15000", f"--user-data-dir={perfil}",
                        f"--print-to-pdf={destino}", INTERMEDIO.resolve().as_uri()],
                       check=True, capture_output=True, timeout=300)
    if not Path(destino).exists():
        raise RuntimeError("El navegador no produjo el PDF")


def normal(s):
    """Texto de comparación: sin etiquetas, sin signos ni espacios, en minúsculas."""
    return re.sub(r"\W+", "", re.sub(r"<[^>]+>", "", s)).lower()


def titulo_de_marcador(t):
    texto = re.sub(r"[*`]", "", t["texto"])
    if not t["numero"]:
        return texto
    return f"{t['numero']}. {texto}" if t["nivel"] == 1 else f"{t['numero']} {texto}"


def corregir_marcadores(escritor, titulos):
    """Chrome junta las palabras donde un título cambia de renglón («parapronosticar»); se reescriben los
    marcadores con el texto exacto de cada título."""
    correctos = {normal(TITULO): TITULO, normal("Índice"): "Índice"}
    correctos.update({normal(titulo_de_marcador(t)): titulo_de_marcador(t) for t in titulos})
    raiz = escritor.root_object
    if "/Outlines" not in raiz:
        return 0
    cambiados, pendientes = 0, [raiz["/Outlines"].get_object().get("/First")]
    while pendientes:
        nodo = pendientes.pop()
        if nodo is None:
            continue
        nodo = nodo.get_object()
        clave = normal(str(nodo.get("/Title", "")))
        if clave in correctos and str(nodo["/Title"]) != correctos[clave]:
            nodo[NameObject("/Title")] = TextStringObject(correctos[clave])
            cambiados += 1
        pendientes += [nodo.get("/First"), nodo.get("/Next")]
    return cambiados


def paginas_de_titulos(pdf, titulos):
    """Página de cada título, leída de los marcadores en el mismo orden en que aparecen en el documento."""
    lector = pypdf.PdfReader(pdf)
    marcas = []

    def recorrer(nodos):
        for nodo in nodos:
            if isinstance(nodo, list):
                recorrer(nodo)
            else:
                marcas.append((nodo.title, lector.get_destination_page_number(nodo) + 1))
    recorrer(lector.outline)
    marcas = [m for m in marcas if normal(m[0]) not in ("índice", "indice")]
    if len(marcas) < len(titulos):
        raise RuntimeError(f"El PDF tiene {len(marcas)} marcadores y la memoria {len(titulos)} títulos")
    paginas, k = {}, 0
    for t in titulos:
        buscado = normal((t["numero"] or "") + t["texto"].replace("*", ""))
        while k < len(marcas) and normal(marcas[k][0]) != buscado:
            k += 1
        if k == len(marcas):
            raise RuntimeError(f"No encontré el marcador del título «{t['texto']}»")
        paginas[t["id"]] = marcas[k][1]
        k += 1
    return paginas, len(lector.pages)


def main():
    cargar_pies()
    titulos, contador, partes = [], [0], []
    for nombre in ORDEN:
        partes.append(volcar((MEMORIA / nombre).read_text(encoding="utf-8"), titulos, contador))
    cuerpo = "\n".join(partes)
    with tempfile.TemporaryDirectory() as tmp:
        borrador = Path(tmp) / "borrador.pdf"
        paginas = {t["id"]: "00" for t in titulos}
        for vuelta in range(3):
            imprimir(documento(cuerpo, titulos, paginas), borrador)
            nuevas, total = paginas_de_titulos(borrador, titulos)
            if nuevas == paginas:
                break
            paginas = nuevas
        else:
            raise RuntimeError("Las páginas del índice no se estabilizaron")
        escritor = pypdf.PdfWriter(clone_from=str(borrador))
        corregir_marcadores(escritor, titulos)
        escritor.add_metadata({"/Title": TITULO, "/Author": "Claude (Anthropic) y Codex (OpenAI)",
                               "/Subject": SUBTITULO, "/Keywords": "pronóstico de demanda, bicicletas compartidas, "
                               "aprendizaje automático, Ecobici, datos retrasados"})
        with open(SALIDA, "wb") as f:
            escritor.write(f)
    print(f"{SALIDA.relative_to(RAIZ)}: {total} páginas, {SALIDA.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
