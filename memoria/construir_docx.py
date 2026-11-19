"""Arma la memoria en Word (.docx) a partir de los capítulos en Markdown.

Uso: .venv/Scripts/python memoria/construir_docx.py
Entrada: memoria/resumen.md, capitulo1..8_*.md, referencias.md y anexos.md, en ese orden.
Figuras: una línea {{FIGURA:nombre}} inserta resultados/figuras/<nombre>.png con su pie (ver PIES).
Salida: memoria/memoria.docx (el índice se actualiza al abrirlo en Word, o con Word instalado se actualiza solo).
"""
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RAIZ = Path(__file__).resolve().parent.parent
MEMORIA = RAIZ / "memoria"
FIGURAS = RAIZ / "resultados" / "figuras"
SALIDA = MEMORIA / "memoria.docx"

ORDEN = ["resumen.md", "capitulo1_introduccion.md", "capitulo2_estado_del_arte.md",
         "capitulo3_objetivos_metodologia.md", "capitulo4_datos.md", "capitulo5_implementacion.md",
         "capitulo6_resultados.md", "capitulo7_discusion.md", "capitulo8_conclusiones.md",
         "referencias.md", "anexos.md", "anexos_tablas.md", "glosario.md"]

TITULO = "Comparación de modelos para pronosticar viajes horarios de Ecobici Buenos Aires con datos retrasados"

PIES = {}  # se completa desde memoria/figuras.txt: nombre|pie


def cargar_pies():
    ruta = MEMORIA / "figuras.txt"
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "|" in linea:
                nombre, pie = linea.split("|", 1)
                PIES[nombre.strip()] = pie.strip()


def estilos(doc):
    for s in doc.sections:
        s.left_margin = s.right_margin = Cm(2.5)
        s.top_margin = s.bottom_margin = Cm(2.5)
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    for nivel, tam in ((1, 17), (2, 14), (3, 12)):
        h = doc.styles[f"Heading {nivel}"]
        h.font.name = "Calibri"
        h.font.size = Pt(tam)
        h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)


def enlace(par, url, texto):
    r_id = par.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                              is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F5FAD")
    rpr.append(color)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = texto
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    par._p.append(h)


TOKEN = re.compile(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\)|https?://[^\s)]+|\$[^$]+\$)")


def texto_latex(s):
    """Convierte LaTeX en línea sencillo a texto legible."""
    reemplazos = {r"\in": "∈", r"\{": "{", r"\}": "}", r"\hat y": "ŷ", r"\hat{y}": "ŷ", r"\sum": "Σ",
                  r"\sqrt": "√", r"\log": "log", r"\exp": "exp", r"\alpha": "α", r"\times": "×", r"\le": "≤",
                  r"\ge": "≥", r"\cdot": "·", r"\,": " ", r"\left": "", r"\right": "", r"\ldots": "…",
                  r"\dots": "…", r"\mathrm": "", r"\text": "", r"\neq": "≠", r"\approx": "≈"}
    for a, b in reemplazos.items():
        s = s.replace(a, b)
    s = re.sub(r"\^\{([^}]*)\}", r"^\1", s)
    s = re.sub(r"_\{([^}]*)\}", r"_\1", s)
    s = s.replace("{", "").replace("}", "")
    return s


def escribir(par, texto, negrita=False):
    for trozo in TOKEN.split(texto):
        if not trozo:
            continue
        if trozo.startswith("**") and trozo.endswith("**") and len(trozo) > 4:
            escribir(par, trozo[2:-2], negrita=True)
        elif trozo.startswith("*") and trozo.endswith("*") and len(trozo) > 2:
            run = par.add_run(trozo[1:-1])
            run.italic, run.bold = True, negrita
        elif trozo.startswith("`") and trozo.endswith("`"):
            run = par.add_run(trozo[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
            run.bold = negrita
        elif trozo.startswith("$") and trozo.endswith("$") and len(trozo) > 2:
            run = par.add_run(texto_latex(trozo[1:-1]))
            run.italic, run.bold = True, negrita
        elif trozo.startswith("[") and "](" in trozo:
            txt, url = re.match(r"\[([^\]]+)\]\(([^)]+)\)", trozo).groups()
            enlace(par, url, txt)
        elif trozo.startswith("http"):
            enlace(par, trozo, trozo)
        else:
            par.add_run(trozo).bold = negrita


def campo_indice(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    for tipo, texto in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None),
                        (None, None), ("end", None)):
        if tipo:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), tipo)
            run._r.append(f)
        elif texto:
            instr = OxmlElement("w:instrText")
            instr.set(qn("xml:space"), "preserve")
            instr.text = texto
            run._r.append(instr)
        else:
            t = OxmlElement("w:t")
            t.text = "Índice: ábralo en Word y pulse F9 para actualizarlo."
            run._r.append(t)


def numeros_de_pagina(seccion):
    pie = seccion.footer.paragraphs[0]
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = pie.add_run()
    for tipo, texto in (("begin", None), (None, "PAGE"), ("end", None)):
        if tipo:
            f = OxmlElement("w:fldChar")
            f.set(qn("w:fldCharType"), tipo)
            run._r.append(f)
        else:
            instr = OxmlElement("w:instrText")
            instr.text = texto
            run._r.append(instr)


def portada(doc):
    for _ in range(5):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(TITULO)
    r.bold, r.font.size = True, Pt(22)
    r.font.color.rgb = RGBColor(0x1F, 0x3A, 0x5F)
    for linea, tam in (("Comparativa de soluciones (tipo 3) · Aprendizaje automático y aprendizaje profundo", 12),
                       ("Memoria con la estructura de un Trabajo Fin de Máster en Inteligencia Artificial", 12),
                       ("", 12),
                       ("Realizada por Claude (Anthropic) y Codex (OpenAI) como prueba de capacidades,", 11),
                       ("por encargo de Sebastián, Fundación Social Mentes Brillantes", 11),
                       ("No es un trabajo presentado ante ninguna universidad (ver Anexo A)", 11),
                       ("", 12), ("Noviembre de 2026", 12)):
        q = doc.add_paragraph()
        q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        q.add_run(linea).font.size = Pt(tam)
    doc.add_page_break()
    h = doc.add_paragraph()
    h.add_run("Índice").bold = True
    campo_indice(doc)
    doc.add_page_break()


def figura(doc, nombre):
    ruta = FIGURAS / f"{nombre}.png"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta la figura {ruta}")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(ruta), width=Cm(15.5))
    pie = doc.add_paragraph()
    pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    escribir(pie, PIES.get(nombre, nombre))
    for run in pie.runs:
        run.font.size = Pt(9.5)


def volcar_md(doc, texto, primero):
    lineas = texto.split("\n")
    i, parrafo = 0, []

    def cerrar():
        nonlocal parrafo
        if parrafo:
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            escribir(p, " ".join(x.strip() for x in parrafo))
            parrafo = []

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
            while i < len(lineas) and not lineas[i].startswith("```"):
                p = doc.add_paragraph()
                r = p.add_run(lineas[i])
                r.font.name, r.font.size = "Consolas", Pt(9.5)
                p.paragraph_format.space_after = Pt(0)
                i += 1
            i += 1
            continue
        m = re.match(r"^(#{1,4}) (.*)", l)
        if m:
            cerrar()
            nivel = len(m.group(1))
            if nivel == 1 and not primero:
                doc.add_page_break()
            primero = False
            h = doc.add_heading(level=min(nivel, 3))
            escribir(h, m.group(2))
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
            ncol = max(len(f) for f in filas)
            t = doc.add_table(rows=len(filas), cols=ncol)
            t.style = "Table Grid"
            for r_i, fila in enumerate(filas):
                for c_i in range(ncol):
                    celda = t.cell(r_i, c_i)
                    celda.paragraphs[0].text = ""
                    escribir(celda.paragraphs[0], fila[c_i] if c_i < len(fila) else "", negrita=(r_i == 0))
                    for p in celda.paragraphs:
                        p.paragraph_format.line_spacing = 1.0
                        for run in p.runs:
                            run.font.size = Pt(9)
            doc.add_paragraph()
            continue
        m = re.match(r"^(\s*)([-*]|\d+\.) (.*)", l)
        if m:
            cerrar()
            texto_item = [m.group(3)]
            i += 1
            while i < len(lineas) and lineas[i].startswith("  ") and lineas[i].strip() and not re.match(
                    r"^\s*([-*]|\d+\.) ", lineas[i]):
                texto_item.append(lineas[i].strip())
                i += 1
            if m.group(2)[0].isdigit():
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1.0)
                p.paragraph_format.first_line_indent = Cm(-0.6)
                p.add_run(m.group(2) + " ")
            else:
                p = doc.add_paragraph(style="List Bullet")
                if m.group(1):
                    p.paragraph_format.left_indent = Cm(1.6)
            escribir(p, " ".join(texto_item))
            continue
        if l.startswith(">"):
            cerrar()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1)
            escribir(p, l.lstrip("> ").strip())
            i += 1
            continue
        parrafo.append(l)
        i += 1
    cerrar()
    return primero


def main():
    cargar_pies()
    doc = Document()
    estilos(doc)
    numeros_de_pagina(doc.sections[0])
    portada(doc)
    primero = True
    for nombre in ORDEN:
        ruta = MEMORIA / nombre
        if not ruta.exists():
            raise FileNotFoundError(ruta)
        primero = volcar_md(doc, ruta.read_text(encoding="utf-8"), primero)
    doc.save(SALIDA)
    print("ok", SALIDA)


if __name__ == "__main__":
    main()
