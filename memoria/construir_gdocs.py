"""Arma la memoria para Google Docs: un .docx con el diseño «Ciudad de noche» del PDF que, al subirlo a Google Drive
con conversión, queda como documento nativo de Google Docs (editable, con índice, títulos, tablas y figuras).

Uso: .venv/Scripts/python memoria/construir_gdocs.py
Salida: memoria/memoria_gdocs.docx (no se sube al repositorio). Usa los mismos capítulos, figuras (PNG) y pies que el
Word y el PDF. Las letras son Newsreader y Schibsted Grotesk, las mismas del PDF, que Google Docs trae porque son de
Google Fonts; en un Word que no las tenga instaladas se verán con otras, por eso el Word del repositorio sigue con
construir_docx.py. El índice va como campo: Word lo llena al actualizarlo y Google Docs lo convierte en su propio índice.
Contrato de diseño: DESIGN.md («PDF de la memoria»), adaptado a lo que Google Docs puede mostrar: una sola columna,
sin guiones de corte (por eso el texto va alineado a la izquierda y no justificado) y la portada como un bloque oscuro.
Las funciones de diseño (preparar, banda_noche, tabla, vestir_tabla, escribir) sirven también para otros documentos.
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from construir_docx import ORDEN, PIES, TITULO, TOKEN, cargar_pies  # noqa: E402
from construir_pdf import NORMALES, NUMERICO, SIMBOLOS, SUBTITULO, VOLADAS, argumento  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
MEMORIA = RAIZ / "memoria"
FIGURAS = RAIZ / "resultados" / "figuras"
SALIDA = MEMORIA / "memoria_gdocs.docx"

SERIF, SANS, MONO = "Newsreader", "Schibsted Grotesk", "Roboto Mono"
TINTA, TINTA_2, TINTA_3 = "1A1D21", "4F555D", "62686F"
LINEA, PAPEL_2, FRESCO = "D6D3CA", "F7F6F3", "0F6F63"
NOCHE, NOCHE_LINEA = "0B0F14", "2F3946"
CLARO, CLARO_2, CLARO_3 = "F6F2EA", "C9CED6", "B4BBC5"
EDADES = (("3DD6C0", "dato de 1 hora"), ("F5B54A", "de 1 día"), ("FF7A66", "de 1 semana"))
ANCHO = Cm(16.4)  # A4 (21 cm) menos 2,3 cm de margen a cada lado
PIE_DE_PAGINA = "Pronóstico de viajes de Ecobici con datos retrasados"
ALT_PORTADA = ("Ilustración: una calle arbolada de Buenos Aires de noche, con una estación de bicicletas públicas bajo "
               "las farolas y tres estelas de luz (verde aguamarina, ámbar y coral) que representan el pronóstico con el "
               "dato de 1 hora, 1 día y 1 semana")

# Orden de los hijos que exige el formato de Word (si no se respeta, Word dice que el archivo está dañado).
ORDEN_PPR = ["w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore", "w:framePr", "w:widowControl", "w:numPr",
             "w:suppressLineNumbers", "w:pBdr", "w:shd", "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
             "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi", "w:adjustRightInd",
             "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
             "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId",
             "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"]
ORDEN_RPR = ["w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs", "w:caps", "w:smallCaps", "w:strike", "w:dstrike",
             "w:outline", "w:shadow", "w:emboss", "w:imprint", "w:noProof", "w:snapToGrid", "w:vanish", "w:webHidden",
             "w:color", "w:spacing", "w:w", "w:kern", "w:position", "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect",
             "w:bdr", "w:shd", "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout",
             "w:specVanish", "w:oMath"]
ORDEN_TCPR = ["w:cnfStyle", "w:tcW", "w:gridSpan", "w:hMerge", "w:vMerge", "w:tcBorders", "w:shd", "w:noWrap",
              "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign", "w:hideMark"]
ORDEN_TBLPR = ["w:tblStyle", "w:tblpPr", "w:tblOverlap", "w:bidiVisual", "w:tblStyleRowBandSize",
               "w:tblStyleColBandSize", "w:tblW", "w:jc", "w:tblCellSpacing", "w:tblInd", "w:tblBorders", "w:shd",
               "w:tblLayout", "w:tblCellMar", "w:tblLook"]


# ---------------------------------------------------------------- Ayudas de formato

def poner(padre, nombre, orden, interno="", atributos=""):
    """Crea (o reemplaza) el hijo `nombre` de `padre` en el lugar que le toca según `orden`."""
    viejo = padre.find(qn(nombre))
    if viejo is not None:
        padre.remove(viejo)
    nuevo = parse_xml(f"<{nombre} {nsdecls('w')} {atributos}>{interno}</{nombre}>")
    padre.insert_element_before(nuevo, *orden[orden.index(nombre) + 1:])
    return nuevo


def fuente(elemento, nombre):
    """Pone la letra en los cuatro alfabetos y quita la letra del tema, que si no manda sobre la elegida."""
    rpr = elemento.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = poner(rpr, "w:rFonts", ORDEN_RPR)
    for atributo in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
        rfonts.attrib.pop(qn(f"w:{atributo}"), None)
    for atributo in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{atributo}"), nombre)


def letra(objeto, nombre=None, tam=None, color=None, negrita=None, cursiva=None):
    """Formato de letra de un run o de un estilo."""
    elemento = objeto.element if hasattr(objeto, "base_style") else objeto._r
    if nombre:
        fuente(elemento, nombre)
    if tam:
        objeto.font.size = Pt(tam)
    if color:
        objeto.font.color.rgb = RGBColor.from_string(color)
    if negrita is not None:
        objeto.font.bold = negrita
    if cursiva is not None:
        objeto.font.italic = cursiva
    return objeto


def parrafo(objeto, antes=None, despues=None, interlineado=None, izquierda=None, primera=None, derecha=None,
            alineacion=None, con_siguiente=None):
    """Formato de párrafo de un párrafo o de un estilo."""
    f = objeto.paragraph_format
    if antes is not None:
        f.space_before = Pt(antes)
    if despues is not None:
        f.space_after = Pt(despues)
    if interlineado is not None:
        f.line_spacing = interlineado
    if izquierda is not None:
        f.left_indent = Cm(izquierda)
    if derecha is not None:
        f.right_indent = Cm(derecha)
    if primera is not None:
        f.first_line_indent = Cm(primera)
    if alineacion is not None:
        f.alignment = alineacion
    if con_siguiente is not None:
        f.keep_with_next = con_siguiente
    return objeto


def ppr(objeto):
    return (objeto.element if hasattr(objeto, "base_style") else objeto._p).get_or_add_pPr()


def borde_parrafo(objeto, lado, color, grosor, espacio=4):
    """Línea en un lado del párrafo; `grosor` en octavos de punto (4 = 0,5 pt)."""
    pbdr = ppr(objeto).find(qn("w:pBdr"))
    previo = "" if pbdr is None else "".join(
        f'<w:{e.tag.split("}")[1]} w:val="single" w:sz="{e.get(qn("w:sz"))}" w:space="{e.get(qn("w:space"))}" '
        f'w:color="{e.get(qn("w:color"))}"/>' for e in pbdr if e.tag != qn(f"w:{lado}"))
    poner(ppr(objeto), "w:pBdr", ORDEN_PPR,
          previo + f'<w:{lado} w:val="single" w:sz="{grosor}" w:space="{espacio}" w:color="{color}"/>')


def fondo_parrafo(objeto, color):
    poner(ppr(objeto), "w:shd", ORDEN_PPR, atributos=f'w:val="clear" w:color="auto" w:fill="{color}"')


def estilo(doc, nombre, base="Normal"):
    try:
        return doc.styles[nombre]
    except KeyError:
        nuevo = doc.styles.add_style(nombre, WD_STYLE_TYPE.PARAGRAPH)
        nuevo.base_style = doc.styles[base]
        nuevo.quick_style = True
        return nuevo


# ---------------------------------------------------------------- Página y estilos

def preparar(doc, pie_de_pagina=PIE_DE_PAGINA, portada_sin_pie=True):
    """A4, márgenes, letras y estilos del diseño, y el pie con el número de página."""
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.left_margin = s.right_margin = Cm(2.3)
        s.top_margin, s.bottom_margin = Cm(2.2), Cm(2.4)
        s.header_distance = s.footer_distance = Cm(1.2)

    # Letra por defecto del documento (la plantilla trae la del tema, Calibri).
    defecto = doc.styles.element.find(qn("w:docDefaults")).find(qn("w:rPrDefault")).find(qn("w:rPr"))
    rfonts = defecto.find(qn("w:rFonts"))
    if rfonts is not None:
        for atributo in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            rfonts.attrib.pop(qn(f"w:{atributo}"), None)
        for atributo in ("ascii", "hAnsi", "eastAsia", "cs"):
            rfonts.set(qn(f"w:{atributo}"), SERIF)

    normal = doc.styles["Normal"]
    letra(normal, SERIF, 11.5, TINTA, False, False)
    parrafo(normal, 0, 7, 1.42, alineacion=WD_ALIGN_PARAGRAPH.LEFT)
    poner(normal.element.get_or_add_rPr(), "w:lang", ORDEN_RPR, atributos='w:val="es-CO" w:eastAsia="es-CO"')
    parrafo(letra(doc.styles["Title"], SERIF, 28, TINTA, False, False), 0, 10, 1.08)
    for nivel, (nombre, tam, color, negrita, antes, despues, inter) in enumerate((
            (SERIF, 26, TINTA, False, 18, 16, 1.1),
            (SERIF, 15, TINTA, True, 20, 6, 1.2),
            (SANS, 11, FRESCO, True, 14, 4, 1.25)), start=1):
        h = doc.styles[f"Heading {nivel}"]
        letra(h, nombre, tam, color, negrita, False)
        parrafo(h, antes, despues, inter, con_siguiente=True)
    for nombre in ("List Bullet", "List Bullet 2"):
        parrafo(doc.styles[nombre], despues=4)

    parrafo(letra(estilo(doc, "Tabla"), SANS, 9, TINTA), 0, 0, 1.2)
    parrafo(letra(estilo(doc, "Pie"), SANS, 9, TINTA_2), 4, 14, 1.35)
    parrafo(letra(estilo(doc, "Pie tabla"), SANS, 9, TINTA_2), 10, 5, 1.35, con_siguiente=True)
    parrafo(letra(estilo(doc, "Referencia"), SERIF, 10.5), 0, 5, 1.3, izquierda=0.8, primera=-0.8)
    codigo = parrafo(letra(estilo(doc, "Codigo"), MONO, 8.5, TINTA), 0, 0, 1.25, izquierda=0.25, derecha=0.25)
    fondo_parrafo(codigo, PAPEL_2)
    cita = parrafo(letra(estilo(doc, "Cita"), SERIF, 11, TINTA_2), 2, 8, 1.4, izquierda=0.5)
    borde_parrafo(cita, "left", FRESCO, 12, 8)

    if pie_de_pagina:
        s = doc.sections[0]
        s.different_first_page_header_footer = portada_sin_pie
        # Alineado a la derecha y sin tabulador: Google Docs no respeta la tabulación derecha del pie.
        p = s.footer.paragraphs[0]
        parrafo(p, alineacion=WD_ALIGN_PARAGRAPH.RIGHT)
        letra(p.add_run(pie_de_pagina + "   ·   "), SANS, 8, TINTA_3)
        campo(letra(p.add_run(), SANS, 8, TINTA, True), "PAGE")


def campo(run, instruccion, provisional=None):
    """Campo de Word (número de página, índice) dentro de un run."""
    for tipo, texto in (("begin", None), (None, instruccion), ("separate", None), (None, provisional),
                        ("end", None)):
        if tipo:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), tipo)
            run._r.append(f)
        elif texto is instruccion:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = f" {instruccion} "
            run._r.append(instr)
        elif texto:
            t = OxmlElement("w:t")
            t.set(qn("xml:space"), "preserve")
            t.text = texto
            run._r.append(t)
    return run


def salto_de_pagina(doc):
    p = doc.add_paragraph()
    parrafo(p, 0, 0, 1.0)
    p.add_run().add_break(WD_BREAK.PAGE)
    return p


# ---------------------------------------------------------------- Texto en línea

def piezas_mate(s, modo=""):
    """LaTeX en línea sencillo → lista de (texto, modo), con modo "", "sub" o "sup"."""
    piezas, i = [], 0
    while i < len(s):
        if s.startswith(r"\{", i) or s.startswith(r"\}", i):
            piezas.append((s[i + 1], modo))
            i += 2
        elif s.startswith(r"\hat", i):
            i += 4
            while s[i] == " ":
                i += 1
            base, i = argumento(s, i)
            piezas.append(({"y": "ŷ", "z": "ẑ"}.get(base, base + "̂"), modo))
        elif s.startswith(r"\sqrt", i):
            dentro, i = argumento(s, i + 5)
            piezas += [("√(", modo)] + piezas_mate(dentro, modo) + [(")", modo)]
        elif s[i] in "_^":
            nuevo = "sub" if s[i] == "_" else "sup"
            dentro, i = argumento(s, i + 1)
            piezas += piezas_mate(dentro, nuevo)
        elif s[i] == "\\":
            comando = re.match(r"\\[a-zA-Z]+|\\.", s[i:]).group(0)
            piezas.append((SIMBOLOS.get(comando, comando.lstrip("\\")), modo))
            i += len(comando)
        elif s[i] in "{}":
            i += 1
        else:
            piezas.append(("−" if s[i] == "-" else s[i], modo))
            i += 1
    unidas = []
    for texto, m in piezas:
        if unidas and unidas[-1][1] == m:
            unidas[-1] = (unidas[-1][0] + texto, m)
        else:
            unidas.append((texto, m))
    return unidas


def mate(par, s, negrita=False):
    """Fórmula: letras en cursiva (menos log y exp), subíndices y superíndices de verdad."""
    for texto, modo in piezas_mate(s):
        for trozo in re.findall(r"log|exp|[A-Za-zαŷẑ]̂?|[^A-Za-zαŷẑ]+", texto):
            r = par.add_run(trozo)
            r.bold = negrita
            r.italic = bool(re.fullmatch(r"[A-Za-zαŷẑ]̂?", trozo))
            r.font.subscript = modo == "sub" or None
            r.font.superscript = modo == "sup" or None


def enlace(par, url, texto, negrita=False):
    r_id = par.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if negrita:
        rpr.append(OxmlElement("w:b"))
    color = OxmlElement("w:color")
    color.set(qn("w:val"), FRESCO)
    rpr.append(color)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = re.sub(r"[*`]", "", texto)
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    par._p.append(h)


def escribir(par, texto, negrita=False, cursiva=False, codigo=10):
    """Markdown en línea (negrita, cursiva, código, fórmulas, enlaces, cifras voladas) → runs del párrafo."""
    for trozo in TOKEN.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**") and len(trozo) > 4:
            escribir(par, trozo[2:-2], True, cursiva, codigo)
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            escribir(par, trozo[1:-1], negrita, True, codigo)
        elif trozo.startswith("`") and trozo.endswith("`"):
            letra(par.add_run(trozo[1:-1]), MONO, codigo, negrita=negrita)
        elif trozo.startswith("$") and trozo.endswith("$") and len(trozo) > 2:
            mate(par, trozo[1:-1], negrita)
        elif trozo.startswith("[") and "](" in trozo:
            txt, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", trozo).groups()
            enlace(par, url, txt, negrita)
        elif trozo.startswith("http"):
            enlace(par, trozo, trozo, negrita)
        else:
            pos = 0
            for m in list(VOLADAS.finditer(trozo)) + [None]:
                fin = m.start() if m else len(trozo)
                if fin > pos:
                    r = par.add_run(trozo[pos:fin])
                    r.bold, r.italic = negrita or None, cursiva or None
                if m:
                    r = par.add_run(m.group(0).translate(NORMALES))
                    r.bold, r.italic, r.font.superscript = negrita or None, cursiva or None, True
                    pos = m.end()


# ---------------------------------------------------------------- Bloques

def celda(c, fondo=None, margenes=None, bordes=None, ancho=None, vertical=None):
    tcpr = c._tc.get_or_add_tcPr()
    if ancho is not None:
        c.width = ancho
    if bordes is not None:
        poner(tcpr, "w:tcBorders", ORDEN_TCPR, "".join(
            f'<w:{lado} w:val="nil"/>' if valor is None else
            f'<w:{lado} w:val="single" w:sz="{valor[1]}" w:space="0" w:color="{valor[0]}"/>'
            for lado, valor in bordes.items()))
    if fondo:
        poner(tcpr, "w:shd", ORDEN_TCPR, atributos=f'w:val="clear" w:color="auto" w:fill="{fondo}"')
    if margenes is not None:
        poner(tcpr, "w:tcMar", ORDEN_TCPR, "".join(
            f'<w:{lado} w:w="{int(valor * 567)}" w:type="dxa"/>'
            for lado, valor in zip(("top", "left", "bottom", "right"), margenes)))
    if vertical is not None:
        c.vertical_alignment = vertical


def tabla_base(t, margen_celdas=(0.06, 0.15)):
    """Tabla a todo el ancho, sin la cuadrícula de Word y con márgenes de celda finos."""
    tblpr = t._tbl.tblPr
    estilo_viejo = tblpr.find(qn("w:tblStyle"))
    if estilo_viejo is not None:
        tblpr.remove(estilo_viejo)
    poner(tblpr, "w:tblW", ORDEN_TBLPR, atributos='w:w="5000" w:type="pct"')
    poner(tblpr, "w:tblBorders", ORDEN_TBLPR, "".join(
        f'<w:{lado} w:val="nil"/>' for lado in ("top", "left", "bottom", "right", "insideH", "insideV")))
    poner(tblpr, "w:tblLayout", ORDEN_TBLPR, atributos='w:type="fixed"')
    v, h = (int(x * 567) for x in margen_celdas)
    poner(tblpr, "w:tblCellMar", ORDEN_TBLPR,
          f'<w:top w:w="{v}" w:type="dxa"/><w:left w:w="{h}" w:type="dxa"/>'
          f'<w:bottom w:w="{v}" w:type="dxa"/><w:right w:w="{h}" w:type="dxa"/>')


def fila_fija(fila, encabezado=False):
    trpr = fila._tr.get_or_add_trPr()
    trpr.append(OxmlElement("w:cantSplit"))
    if encabezado:
        trpr.append(OxmlElement("w:tblHeader"))


def texto_plano(s):
    return re.sub(r"\*\*|\*|`|\$|\[([^\]]+)\]\([^)]+\)", r"\1", s)


def anchos_de_columnas(t, tam=9):
    """Ancho de cada columna: nunca menos que su palabra más larga (para que ninguna se parta, como «Claud e»), y el
    espacio que sobra se reparte según lo que le falta a cada una para que su texto quepa en un renglón."""
    letra_cm = 0.2 * tam / 9  # ancho medio de una letra de Schibsted Grotesk, con algo de holgura
    total = ANCHO.cm
    minimos, deseos = [], []
    for c in range(len(t.columns)):
        textos = [texto_plano(f.cells[c].text) for f in t.rows]
        palabra = max((len(p) for s in textos for p in s.split()), default=1)
        largo = max([len(s) for s in textos[1:]] + [len(textos[0]) // 2])
        minimos.append(palabra * letra_cm + 0.4)
        deseos.append(max(largo * letra_cm + 0.4, minimos[-1]))
    if sum(deseos) <= total:
        anchos = [d * total / sum(deseos) for d in deseos]
    elif sum(minimos) >= total:
        anchos = [m * total / sum(minimos) for m in minimos]
    else:
        falta = [d - m for d, m in zip(deseos, minimos)]
        sobra = total - sum(minimos)
        anchos = [m + sobra * f / sum(falta) for m, f in zip(minimos, falta)]
    return [Cm(a) for a in anchos]


def vestir_tabla(doc, t, derecha=None, anchos=None, tam=9):
    """Diseño de tabla del PDF: línea fuerte bajo el encabezado, líneas finas entre filas y filas pares sombreadas."""
    tabla_base(t)
    if anchos is None:
        anchos = anchos_de_columnas(t, tam)
    for c, ancho in enumerate(anchos):
        t.columns[c].width = ancho
    for r, fila in enumerate(t.rows):
        fila_fija(fila, encabezado=(r == 0))
        for c, cel in enumerate(fila.cells):
            linea = (TINTA, 8) if r == 0 else (LINEA, 4)
            celda(cel, fondo=PAPEL_2 if r > 0 and r % 2 == 0 else None, ancho=anchos[c],
                  bordes={"top": None, "left": None, "right": None, "bottom": linea},
                  vertical=WD_CELL_VERTICAL_ALIGNMENT.BOTTOM if r == 0 else WD_CELL_VERTICAL_ALIGNMENT.TOP)
            for p in cel.paragraphs:
                p.style = doc.styles["Tabla"]
                if tam != 9:
                    for run in p.runs:
                        run.font.size = Pt(tam)
                if derecha and derecha[c]:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def separador(doc, alto=6):
    p = doc.add_paragraph()
    parrafo(p, 0, 0)
    p.paragraph_format.line_spacing = Pt(alto)
    return p


def tabla(doc, filas):
    ncol = max(len(f) for f in filas)
    filas = [f + [""] * (ncol - len(f)) for f in filas]
    cuerpo = filas[1:]
    derecha = [c > 0 and sum(bool(NUMERICO.match(f[c])) for f in cuerpo) >= max(1, len(cuerpo) * 0.6)
               for c in range(ncol)]
    tam = 8 if ncol >= 6 else 9
    t = doc.add_table(rows=len(filas), cols=ncol)
    for r, fila in enumerate(filas):
        for c, texto in enumerate(fila):
            escribir(t.cell(r, c).paragraphs[0], texto, negrita=(r == 0), codigo=tam - 0.5)
    vestir_tabla(doc, t, derecha, tam=tam)
    separador(doc, 8)
    return t


def imagen(par, ruta, ancho, alternativo):
    forma = par.add_run().add_picture(str(ruta), width=ancho)
    forma._inline.docPr.set("descr", alternativo)
    return forma


def figura(doc, nombre):
    ruta = FIGURAS / f"{nombre}.png"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta la figura {ruta}")
    p = doc.add_paragraph()
    parrafo(p, 10, 0, 1.0, alineacion=WD_ALIGN_PARAGRAPH.CENTER, con_siguiente=True)
    imagen(p, ruta, ANCHO, texto_plano(PIES.get(nombre, nombre)))
    escribir(doc.add_paragraph(style="Pie"), PIES.get(nombre, nombre), codigo=8.5)


def banda_noche(doc, tipo, titulo, subtitulo=None, imagen_ruta=None, alternativo="", edades=False, pie=(),
                alto_pie=None, tam_titulo=26):
    """Bloque oscuro como la portada del PDF y la web: imagen opcional, etiqueta, título, subtítulo y pie."""
    filas = (1 if imagen_ruta else 0) + 1 + (1 if pie else 0)
    t = doc.add_table(rows=filas, cols=1)
    tabla_base(t, (0, 0))
    t.columns[0].width = ANCHO
    # Bordes del mismo color del fondo: sin borde («nil»), Google Docs dibuja una raya gris entre las filas.
    sin_bordes = {lado: (NOCHE, 4) for lado in ("top", "left", "bottom", "right")}
    fila = 0
    if imagen_ruta:
        c = t.cell(0, 0)
        celda(c, NOCHE, (0, 0, 0, 0), sin_bordes, ANCHO)
        p = c.paragraphs[0]
        parrafo(p, 0, 0, 1.0, alineacion=WD_ALIGN_PARAGRAPH.CENTER)
        imagen(p, imagen_ruta, ANCHO, alternativo)
        fila = 1
    c = t.cell(fila, 0)
    celda(c, NOCHE, (0.9, 0.95, 0.5 if pie else 0.9, 0.95), sin_bordes, ANCHO)
    p = c.paragraphs[0]
    parrafo(p, 0, 12, 1.2)
    letra(p.add_run(tipo), SANS, 8.5, CLARO_3)
    p = c.add_paragraph()
    parrafo(p, 0, 10, 1.08)
    letra(p.add_run(titulo), SERIF, tam_titulo, CLARO)
    if subtitulo:
        p = c.add_paragraph()
        parrafo(p, 0, 12 if edades else 0, 1.35)
        letra(p.add_run(subtitulo), SERIF, 12.5, CLARO_2, cursiva=True)
    if edades:
        p = c.add_paragraph()
        parrafo(p, 0, 0, 1.2)
        for n, (color, texto) in enumerate(EDADES):
            letra(p.add_run(("     " if n else "") + "━━ "), SANS, 9, color, True)
            letra(p.add_run(texto), SANS, 9, CLARO_2)
    if pie:
        c = t.cell(fila + 1, 0)
        celda(c, NOCHE, (0.4, 0.95, 0.9, 0.95), sin_bordes, ANCHO, WD_CELL_VERTICAL_ALIGNMENT.BOTTOM)
        if alto_pie:
            t.rows[fila + 1].height = Cm(alto_pie)
            t.rows[fila + 1].height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST
        for n, linea in enumerate(pie):
            p = c.paragraphs[0] if n == 0 else c.add_paragraph()
            parrafo(p, 0, 3, 1.35)
            if n == 0:
                borde_parrafo(p, "top", NOCHE_LINEA, 4, 8)
            escribir(p, linea)
            for run in p.runs:
                letra(run, SANS, 8.5, CLARO_3)
            for h in p._p.findall(qn("w:hyperlink")):
                h.find(qn("w:r")).find(qn("w:rPr")).find(qn("w:color")).set(qn("w:val"), EDADES[0][0])
    return t


# ---------------------------------------------------------------- Memoria

def titulo(doc, nivel, texto):
    m = re.match(r"^((?:Anexo [A-Z])|(?:\d+(?:\.\d+)*))\.?\s+(.*)$", texto)
    numero, resto = (m.group(1), m.group(2)) if m else ("", texto)
    h = doc.add_paragraph(style=f"Heading {nivel}")
    if numero:
        r = h.add_run(numero + ("." if nivel == 1 else "") + " ")
        letra(r, color=FRESCO if nivel == 1 else TINTA_3, negrita=False if nivel == 2 else None)
    escribir(h, resto)
    return resto


def volcar(doc, texto, primero, seccion=None):
    lineas = texto.split("\n")
    i, acumulado = 0, []

    def cerrar():
        nonlocal acumulado
        if acumulado:
            contenido = " ".join(x.strip() for x in acumulado)
            if contenido.startswith("**Tabla"):
                p = doc.add_paragraph(style="Pie tabla")
            elif seccion == "Referencias":
                p = doc.add_paragraph(style="Referencia")
            else:
                p = doc.add_paragraph()
            escribir(p, contenido, codigo=9.5 if p.style.name == "Referencia" else 10)
            acumulado = []

    while i < len(lineas):
        l = lineas[i]
        if not l.strip() or l.strip() == "---":
            cerrar()
            i += 1
            continue
        m = re.match(r"^\{\{FIGURA:([\w\-]+)\}\}\s*$", l.strip())
        if m:
            cerrar()
            figura(doc, m.group(1))
            i += 1
            continue
        if l.startswith("```"):
            cerrar()
            i += 1
            bloque = []
            while i < len(lineas) and not lineas[i].startswith("```"):
                bloque.append(lineas[i])
                i += 1
            for n, linea in enumerate(bloque):
                p = doc.add_paragraph(linea, style="Codigo")
                if n == 0:
                    p.paragraph_format.space_before = Pt(4)
                if n == len(bloque) - 1:
                    p.paragraph_format.space_after = Pt(10)
            i += 1
            continue
        m = re.match(r"^(#{1,4}) (.*)", l)
        if m:
            cerrar()
            nivel = min(len(m.group(1)), 3)
            if nivel == 1 and not primero:
                salto_de_pagina(doc)
            primero = False
            resto = titulo(doc, nivel, m.group(2).strip())
            if nivel == 1:
                seccion = resto
            i += 1
            continue
        if l.startswith("|"):
            cerrar()
            filas = []
            while i < len(lineas) and lineas[i].startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in celdas):
                    filas.append(celdas)
                i += 1
            tabla(doc, filas)
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)", l)
        if m:
            cerrar()
            item = [m.group(3)]
            i += 1
            while i < len(lineas) and lineas[i].startswith("  ") and lineas[i].strip() and not re.match(
                    r"^\s*([-*]|\d+\.) ", lineas[i]):
                item.append(lineas[i].strip())
                i += 1
            if m.group(2)[0].isdigit():
                p = doc.add_paragraph()
                parrafo(p, 0, 4, izquierda=0.9, primera=-0.6)
                p.add_run(m.group(2) + " ")
            else:
                p = doc.add_paragraph(style="List Bullet 2" if m.group(1) else "List Bullet")
            escribir(p, " ".join(item))
            continue
        if l.startswith(">"):
            cerrar()
            escribir(doc.add_paragraph(style="Cita"), l.lstrip("> ").strip())
            i += 1
            continue
        acumulado.append(l)
        i += 1
    cerrar()
    return primero, seccion


def primer_renglon(doc):
    """Párrafo mínimo antes de una tabla que abre el documento (Google Docs, si no, pone uno de 11 pt en Arial)."""
    p = doc.add_paragraph()
    parrafo(p, 0, 0)
    p.paragraph_format.line_spacing = Pt(1)
    return p


def portada(doc):
    primer_renglon(doc)
    banda_noche(
        doc, "Memoria · Comparativa de soluciones · Aprendizaje automático", TITULO, SUBTITULO,
        MEMORIA / "portada.jpg", ALT_PORTADA, edades=True, alto_pie=7.0,
        pie=("Realizada por **Claude** (Anthropic) y **Codex** (OpenAI) como prueba de capacidades, por encargo de la "
             "Fundación Social Mentes Brillantes. Tiene la estructura de un Trabajo Fin de Máster en Inteligencia "
             "Artificial, pero no es un trabajo presentado ante ninguna universidad (ver Anexo A).",
             "Noviembre de 2026"))
    p = doc.add_paragraph()
    parrafo(p, 0, 16, 1.1)
    p.add_run().add_break(WD_BREAK.PAGE)
    letra(p.add_run("Índice"), SERIF, 26, TINTA)
    q = doc.add_paragraph()
    campo(q.add_run(), r'TOC \o "1-2" \h \z \u',
          "Índice: en Google Docs, clic en el índice y luego en «Actualizar»; en Word, clic derecho › Actualizar campos.")
    salto_de_pagina(doc)


def main():
    cargar_pies()
    doc = Document()
    preparar(doc)
    doc.core_properties.title = TITULO
    doc.core_properties.subject = SUBTITULO
    doc.core_properties.author = "Claude (Anthropic) y Codex (OpenAI)"
    doc.core_properties.language = "es-CO"
    portada(doc)
    primero, seccion = True, None
    for nombre in ORDEN:
        ruta = MEMORIA / nombre
        if not ruta.exists():
            raise FileNotFoundError(ruta)
        primero, seccion = volcar(doc, ruta.read_text(encoding="utf-8"), primero, seccion)
    doc.save(SALIDA)
    print("ok", SALIDA)


if __name__ == "__main__":
    main()
