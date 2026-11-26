"""
Gera artigo.tex (LaTeX, modelo SBC) e artigo.docx (Word, modelo SBC) a partir
de UMA ÚNICA fonte de conteúdo (conteudo.py) e dos números de resultados/resumo.json.

    python gerar_artigo.py

Dica para o grupo: depois de gerados, vocês podem editar diretamente o .tex
(Overleaf) ou o .docx (Word) -- este script é só o ponto de partida.
"""
import json
import os
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

from referencias import REFS
import conteudo as C

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, ".."))
TEMPLATE_DOCX = os.path.join(AQUI, "modelo-tcc-sbc.docx")

# ============================================================== utilidades
def br(x, casas=2):
    """Número no formato brasileiro: 1.234,56"""
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def numerar(blocos):
    num, cont = {}, {"sec": 0, "sub": 0, "fig": 0, "tab": 0, "eq": 0}
    for b in blocos:
        t = b[0]
        if t == "sec":
            cont["sec"] += 1; cont["sub"] = 0
            if len(b) > 2 and b[2]:
                num[b[2]] = str(cont["sec"])
        elif t == "sub":
            cont["sub"] += 1
            if len(b) > 2 and b[2]:
                num[b[2]] = f"{cont['sec']}.{cont['sub']}"
        elif t == "fig":
            cont["fig"] += 1; num[b[1]] = str(cont["fig"])
        elif t == "tab":
            cont["tab"] += 1; num[b[1]] = str(cont["tab"])
        elif t == "eq":
            cont["eq"] += 1; num[b[3]] = str(cont["eq"])
    return num


def preencher(s, valores):
    return re.sub(r"<<(\w+)>>", lambda m: str(valores[m.group(1)]), s)


# ------------------------------------------------- conversão TeX -> Unicode
SUB = str.maketrans("0123456789+-=()aeoxijklmnprstuv",
                    "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₒₓᵢⱼₖₗₘₙₚᵣₛₜᵤᵥ")
SUP = str.maketrans("0123456789+-=()nmaxi", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿᵐᵃˣⁱ")
TEX_SIMB = [(r"\preceq", "⪯"), (r"\prec", "≺"), (r"\in", "∈"), (r"\le", "≤"),
            (r"\ge", "≥"), (r"\times", "×"), (r"\cdot", "·"), (r"\sum", "∑"),
            (r"\lambda", "λ"), (r"\alpha", "α"), (r"\Omega", "Ω"), (r"\ldots", "…"),
            (r"\forall", "∀"), (r"\exists", "∃"), (r"\neq", "≠"), (r"\to", "→"),
            (r"\{", "{"), (r"\}", "}"), (r"\,", " "), (r"\;", " "), (r"\quad", "  "),
            (r"\max", "max"), (r"\min", "min"), (r"\mid", "|"), (r"\infty", "∞"),
            (r"\approx", "≈"), (r"\pm", "±"), (r"\iff", "⇔"), (r"\mathcal{X}", "𝒳"), (r"\mathbf{x}", "x"),
            (r"\mathbf{y}", "y"), (r"\mathbf{F}", "F"), (r"\left", ""), (r"\right", ""),
            (r"\big", ""), (r"\Big", ""), (r"\%", "%"), ("{,}", ",")]


def tex2uni(s):
    s = re.sub(r"\\bar\{(\w)\}", lambda m: m.group(1) + "\u0304", s)
    for a, b in sorted(TEX_SIMB, key=lambda t: -len(t[0])):
        s = s.replace(a, b)
    s = re.sub(r"\\text\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\mathrm\{([^}]*)\}", r"\1", s)
    s = re.sub(r"_\{([^}]*)\}", lambda m: m.group(1).translate(SUB)
               if all(c in "0123456789+-=()aeoxijklmnprstuv" for c in m.group(1))
               else "_" + m.group(1), s)
    # índice sem caractere Unicode subscrito (ex.: c_F) fica como "_F" e vira
    # subscrito de verdade em _math_runs
    s = re.sub(r"_(\w)", lambda m: m.group(1).translate(SUB)
               if m.group(1) in "0123456789aeoxijklmnprstuv" else "_" + m.group(1), s)
    s = re.sub(r"\^\{([^}]*)\}", lambda m: m.group(1).translate(SUP)
               if all(c in "0123456789+-=()nmaxi" for c in m.group(1))
               else "^" + m.group(1), s)
    s = re.sub(r"\^(\w)", lambda m: m.group(1).translate(SUP), s)
    return s.replace("{", "").replace("}", "") if "\\" not in s else s


# ------------------------------------------------- citações
def cit_p(chaves, tex):
    if tex:
        return r"\citep{" + ",".join(chaves) + "}"
    return "[" + "; ".join(f"{REFS[k][0]} {REFS[k][1]}" for k in chaves) + "]"


def cit_t(chave, tex):
    if tex:
        return r"\citet{" + chave + "}"
    return f"{REFS[chave][0]} [{REFS[chave][1]}]"


def citacoes(s, tex):
    s = re.sub(r"\[(@[\w]+(?:;\s*@[\w]+)*)\]",
               lambda m: cit_p([c.strip()[1:] for c in m.group(1).split(";")], tex), s)
    s = re.sub(r"(?<![\w\\{])@([a-z]+\d{4})", lambda m: cit_t(m.group(1), tex), s)
    return s


# ============================================================== LaTeX
def esc_tex(s):
    return (s.replace("%", r"\%").replace("&", r"\&").replace("#", r"\#")
             .replace("_", r"\_"))


def inline_tex(s, num):
    s = s.replace("{real}", r"R\$~")
    partes = re.split(r"(\$[^$]+\$)", s)
    out = []
    for p in partes:
        if p.startswith("$") and p.endswith("$") and len(p) > 1:
            out.append(p)
        else:
            p = esc_tex(p)
            p = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", p)
            p = re.sub(r"<(https?://[^>]+)>", r"\\url{\1}", p)
            out.append(p)
    s = "".join(out)
    s = citacoes(s, tex=True)
    s = re.sub(r"\{ref:([\w:\-]+)\}", r"\\ref{\1}", s)
    return s


PREAMBULO = r"""% =====================================================================
% ARTIGO -- Tema 38: Evolução multiobjetivo: custo e tempo de entrega
% Formato SBC (coluna única, A4, Times 12pt) -- baseado no modelo-tcc-sbc.tex
% Compile: pdflatex artigo.tex (2x). No Overleaf: envie este .tex + pasta figuras/.
% Trechos entre [colchetes] devem ser preenchidos pelo grupo.
% =====================================================================
\documentclass[a4paper,12pt]{article}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[brazilian]{babel}
\usepackage{times}
\usepackage[a4paper,top=3.5cm,left=3cm,right=3cm,bottom=2.5cm]{geometry}
\usepackage{graphicx}
\usepackage{url}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{titlesec}
\usepackage[bf,sf,footnotesize,indent]{caption}
% Citações no estilo SBC/ementa: [Autor Ano] e Autor [Ano]
\usepackage[authoryear,square]{natbib}
\setcitestyle{aysep={},yysep={;}}
\setlength{\bibsep}{6pt}
\setlength{\bibhang}{0.5cm}

% Regra da disciplina: 1º parágrafo da seção SEM recuo; demais com 1,27 cm.
% (por isso o pacote indentfirst do modelo original foi retirado)
\setlength{\parindent}{1.27cm}
\setlength{\parskip}{6pt}
\flushbottom

\titleformat{\section}{\fontsize{13}{15}\bfseries}{\thesection.}{1em}{}
\titleformat{\subsection}{\fontsize{12}{14}\bfseries}{\thesubsection.}{1em}{}
\titleformat{\subsubsection}{\fontsize{12}{14}\bfseries\itshape}{\thesubsubsection.}{1em}{}
\titlespacing*{\section}{0pt}{12pt}{6pt}
\titlespacing*{\subsection}{0pt}{10pt}{4pt}

\renewcommand{\captionfont}{\sffamily\footnotesize\bfseries}
\setlength{\captionmargin}{0.8cm}
\captionsetup{labelsep=period}

\newenvironment{resumo}{%
  \list{}{\advance\topsep by6pt\relax
    \leftmargin=0.8cm
    \labelwidth=0pt
    \listparindent=0pt
    \itemindent\listparindent
    \rightmargin\leftmargin}\item[\hskip\labelsep\bfseries\itshape Resumo.]\itshape}%
  {\endlist}

\renewenvironment{abstract}{%
  \list{}{\advance\topsep by6pt\relax
    \leftmargin=0.8cm
    \labelwidth=0pt
    \listparindent=0pt
    \itemindent\listparindent
    \rightmargin\leftmargin}\item[\hskip\labelsep\bfseries\itshape Abstract.]\itshape}%
  {\endlist}

\begin{document}
\pagestyle{empty}
"""


def gerar_tex(blocos, num, valores):
    L = [PREAMBULO]
    A = C.CABECALHO
    L.append(r"""\begin{center}
  {\fontsize{16}{20}\selectfont\bfseries %s}\\[4pt]
  {\fontsize{14}{18}\selectfont\bfseries %s}\\[12pt]
  {\normalsize\bfseries %s}\\[6pt]
  {\footnotesize\itshape %s}\\[4pt]
  {\normalsize
    %s\\{}
    \footnotesize\texttt{%s}
  }
\end{center}
\vspace{12pt}
""" % (A["titulo"], A["title"], A["autores_tex"], A["orientacao"],
       A["afiliacao"], A.get("emails_tex", A["emails"])))
    L.append("\\begin{resumo}\n" + inline_tex(preencher(C.RESUMO, valores), num)
             + "\n\\end{resumo}\n\\noindent\\textbf{Palavras-chave:} "
             + C.PALAVRAS + "\n\n\\vspace{6pt}\n\n\\begin{abstract}\n"
             + inline_tex(preencher(C.ABSTRACT, valores), num)
             + "\n\\end{abstract}\n\\noindent\\textbf{Keywords:} " + C.KEYWORDS
             + "\n\n\\vspace{18pt}\n")
    primeiro = False
    for b in blocos:
        t = b[0]
        if t in ("sec", "sub", "secnn"):
            cmd = {"sec": "section", "sub": "subsection", "secnn": "section*"}[t]
            lab = f"\\label{{{b[2]}}}" if len(b) > 2 and b[2] else ""
            L.append(f"\n\\{cmd}{{{b[1]}}}{lab}\n")
            primeiro = True
        elif t in ("p", "p+"):
            txt = inline_tex(preencher(b[1], valores), num)
            if t == "p+":
                L[-1] = L[-1].rstrip("\n") + " " + txt + "\n\n"
                continue
            L.append(("\\noindent " if primeiro else "") + txt + "\n\n")
            primeiro = False
        elif t == "eq":
            L.append("\\begin{equation}\n" + b[1] + f"\n\\label{{{b[3]}}}\n\\end{{equation}}\n")
        elif t == "fig":
            _, lab, arq, leg, larg = b
            L.append("\\begin{figure}[!htb]\n  \\centering\n"
                     f"  \\includegraphics[width={larg}\\linewidth]{{figuras/{arq}.pdf}}\n"
                     f"  \\caption{{{inline_tex(preencher(leg, valores), num)}}}\n"
                     f"  \\label{{{lab}}}\n\\end{{figure}}\n")
        elif t == "tab":
            _, lab, leg, spec, cab, linhas = b
            linhas = [[inline_tex(preencher(c, valores), num) for c in l] for l in linhas]
            corpo = " \\\\\n    ".join(" & ".join(l) for l in linhas)
            L.append("\\begin{table}[!htb]\n  \\centering\n"
                     f"  \\caption{{{inline_tex(preencher(leg, valores), num)}}}\n"
                     f"  \\label{{{lab}}}\n  \\small\n  \\begin{{tabular}}{{{spec}}}\n"
                     "    \\toprule\n    "
                     + " & ".join(inline_tex(c, num) for c in cab) + " \\\\\n    \\midrule\n    "
                     + corpo + " \\\\\n    \\bottomrule\n  \\end{tabular}\n\\end{table}\n")
    # referências
    L.append("\n\\begin{thebibliography}{99}\n")
    for k in sorted(REFS, key=lambda k: REFS[k][2].lower()):
        curta, ano, txt = REFS[k]
        curta_tex = curta.replace(" et al.", " et~al.")
        L.append(f"\\bibitem[{curta_tex}({ano})]{{{k}}}\n{inline_tex(txt, num)}\n")
    L.append("\\end{thebibliography}\n\n\\end{document}\n")
    return "".join(L)


# ============================================================== Word (docx)
FONTE = "Times New Roman"


def _fonte(run, nome=FONTE, tam=12, b=None, i=None, mono=False):
    run.font.name = nome
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), nome)
    run.font.size = Pt(tam)
    if b is not None: run.bold = b
    if i is not None: run.italic = i


def _math_runs(par, s, tam=12, italico=True, negrito=None):
    """Escreve matemática já convertida para Unicode; "_X" vira X subscrito."""
    for k, parte in enumerate(re.split(r"_(\w)", s)):
        if not parte:
            continue
        r = par.add_run(parte)
        _fonte(r, tam=tam, i=italico, b=negrito)
        if k % 2:
            r.font.subscript = True


def inline_docx(par, s, num, tam=12, italico_base=False, negrito_base=False):
    """Escreve texto com *itálico*, $math$, citações e referências."""
    s = s.replace("{real}/", "R\ue000/")
    s = s.replace("{real}", "R\ue000\u00a0")
    s = citacoes(s, tex=False)
    s = re.sub(r"\{ref:([\w:\-]+)\}", lambda m: num[m.group(1)], s)
    s = re.sub(r"<(https?://[^>]+)>", r"\1", s)
    s = s.replace("---", "—").replace("--", "–").replace("~", "\u00a0")
    tokens = re.split(r"(\$[^$]+\$|\*[^*]+\*)", s)
    for tk in tokens:
        if not tk:
            continue
        if "\ue000" in tk and not tk.startswith("$"):
            tk = tk.replace("\ue000", "$")
            r = par.add_run(tk.strip("*") if tk.startswith("*") and tk.endswith("*") else tk)
            _fonte(r, tam=tam, i=italico_base ^ (tk.startswith("*") and tk.endswith("*")),
                   b=negrito_base)
            continue
        if tk.startswith("$") and tk.endswith("$") and len(tk) > 1:
            _math_runs(par, tex2uni(tk[1:-1]), tam=tam, negrito=negrito_base)
        elif tk.startswith("*") and tk.endswith("*") and len(tk) > 1:
            r = par.add_run(tk[1:-1])
            _fonte(r, tam=tam, i=not italico_base, b=negrito_base)
        else:
            r = par.add_run(tk)
            _fonte(r, tam=tam, i=italico_base, b=negrito_base)


def _par(doc, alinh="both", antes=0, depois=6, recuo1=None, esq=None, dir_=None,
         keep=False, linha=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.alignment = {"both": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER,
                    "left": WD_ALIGN_PARAGRAPH.LEFT}[alinh]
    pf.space_before, pf.space_after = Pt(antes), Pt(depois)
    if recuo1 is not None: pf.first_line_indent = recuo1
    if esq is not None: pf.left_indent = esq
    if dir_ is not None: pf.right_indent = dir_
    if keep: pf.keep_with_next = True
    pf.line_spacing = linha if linha else 1.0
    return p


def gerar_docx(blocos, num, valores, saida):
    doc = Document(TEMPLATE_DOCX)
    corpo = doc.element.body
    for el in list(corpo):
        if el.tag != qn("w:sectPr"):
            corpo.remove(el)
    A = C.CABECALHO
    p = _par(doc, "center", depois=3); r = p.add_run(A["titulo"]); _fonte(r, tam=16, b=True)
    p = _par(doc, "center", depois=10); r = p.add_run(A["title"]); _fonte(r, tam=14, b=True)
    p = _par(doc, "center", depois=4); r = p.add_run(A["autores_docx"]); _fonte(r, tam=12, b=True)
    p = _par(doc, "center", depois=4); r = p.add_run(A["orientacao"].replace("--", "–")); _fonte(r, tam=10, i=True)
    p = _par(doc, "center", depois=1); r = p.add_run(A["afiliacao_docx"]); _fonte(r, tam=12)
    p = _par(doc, "center", depois=14); r = p.add_run(A["emails"]); _fonte(r, "Courier New", 10)

    for rot, txt, pal_rot, pal in (("Resumo.", C.RESUMO, "Palavras-chave: ", C.PALAVRAS),
                                   ("Abstract.", C.ABSTRACT, "Keywords: ", C.KEYWORDS)):
        p = _par(doc, "both", antes=6, depois=3, esq=Cm(0.8), dir_=Cm(0.8))
        r = p.add_run(rot + " "); _fonte(r, b=True, i=True)
        inline_docx(p, preencher(txt, valores), num, italico_base=True)
        p = _par(doc, "left", depois=10)
        r = p.add_run(pal_rot); _fonte(r, b=True)
        r = p.add_run(pal); _fonte(r)

    primeiro = False
    for b in blocos:
        t = b[0]
        if t in ("sec", "secnn"):
            rot = (num.get(b[2], "") + ". " if t == "sec" and len(b) > 2 and b[2] else "")
            if t == "sec" and not rot:
                rot = ""
            p = _par(doc, "left", antes=12, depois=6, keep=True)
            r = p.add_run(rot + b[1]); _fonte(r, tam=13, b=True)
            primeiro = True
        elif t == "sub":
            p = _par(doc, "left", antes=10, depois=4, keep=True)
            r = p.add_run(num[b[2]] + ". " + b[1]); _fonte(r, tam=12, b=True)
            primeiro = True
        elif t == "p+":
            p.add_run(" ")
            inline_docx(p, preencher(b[1], valores), num)
        elif t == "p":
            # regra SBC: 6 pt de espaço ANTES de cada parágrafo
            p = _par(doc, "both", antes=6, depois=0, recuo1=Cm(0) if primeiro else Cm(1.27))
            inline_docx(p, preencher(b[1], valores), num)
            primeiro = False
        elif t == "eq":
            p = _par(doc, "center", antes=6, depois=0)
            _math_runs(p, b[2], italico=False)
            r = p.add_run(f"\t({num[b[3]]})"); _fonte(r)
            # tabulação à direita para o número da equação
            pPr = p._p.get_or_add_pPr()
            tabs = OxmlElement("w:tabs"); tab = OxmlElement("w:tab")
            tab.set(qn("w:val"), "right"); tab.set(qn("w:pos"), "8504")
            tabs.append(tab); pPr.append(tabs)
        elif t == "fig":
            _, lab, arq, leg, larg = b
            p = _par(doc, "center", antes=6, depois=2, keep=True)
            p.add_run().add_picture(os.path.join(RAIZ, "figuras", arq + ".png"),
                                    width=Cm(15.0 * larg))
            p = _par(doc, "center", depois=10, esq=Cm(0.8), dir_=Cm(0.8))
            r = p.add_run(f"Figura {num[lab]}. "); _fonte(r, "Arial", 10, b=True)
            pp = doc.add_paragraph()  # temporário para reaproveitar inline_docx
            inline_docx(pp, preencher(leg, valores), num, tam=10, negrito_base=True)
            for rr in pp.runs:
                _fonte(rr, "Arial", 10, b=True, i=rr.italic)
                p._p.append(rr._r)
            pp._p.getparent().remove(pp._p)
        elif t == "tab":
            _, lab, leg, spec, cab, linhas = b
            p = _par(doc, "center", antes=6, depois=4, keep=True, esq=Cm(0.8), dir_=Cm(0.8))
            r = p.add_run(f"Tabela {num[lab]}. "); _fonte(r, "Arial", 10, b=True)
            pp = doc.add_paragraph()
            inline_docx(pp, preencher(leg, valores), num, tam=10, negrito_base=True)
            for rr in pp.runs:
                _fonte(rr, "Arial", 10, b=True, i=rr.italic)
                p._p.append(rr._r)
            pp._p.getparent().remove(pp._p)
            alinh = [c for c in spec if c in "lcr"]
            tb = doc.add_table(rows=1 + len(linhas), cols=len(cab))
            tb.alignment = 1
            for j, c in enumerate(cab):
                cel = tb.rows[0].cells[j]; cp = cel.paragraphs[0]
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                inline_docx(cp, c, num, tam=10, negrito_base=True)
            for i, l in enumerate(linhas, 1):
                for j, c in enumerate(l):
                    cp = tb.rows[i].cells[j].paragraphs[0]
                    cp.alignment = {"l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER,
                                    "r": WD_ALIGN_PARAGRAPH.RIGHT}[alinh[j]]
                    inline_docx(cp, preencher(c, valores), num, tam=10)
            # bordas finas estilo "booktabs": topo, abaixo do cabeçalho e base
            tblPr = tb._tbl.tblPr
            bord = OxmlElement("w:tblBorders")
            for lado, sz in (("top", "8"), ("bottom", "8")):
                e = OxmlElement(f"w:{lado}"); e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), sz); e.set(qn("w:color"), "000000"); bord.append(e)
            tblPr.append(bord)
            for cel in tb.rows[0].cells:
                tcPr = cel._tc.get_or_add_tcPr(); tb_ = OxmlElement("w:tcBorders")
                e = OxmlElement("w:bottom"); e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), "4"); e.set(qn("w:color"), "000000")
                tb_.append(e); tcPr.append(tb_)
            for row in tb.rows:
                for cel in row.cells:
                    for cp in cel.paragraphs:
                        cp.paragraph_format.space_before = Pt(1)
                        cp.paragraph_format.space_after = Pt(1)
            _par(doc, depois=2)
    # referências
    p = _par(doc, "left", antes=12, depois=6, keep=True)
    r = p.add_run("Referências"); _fonte(r, tam=13, b=True)
    for k in sorted(REFS, key=lambda k: REFS[k][2].lower()):
        p = _par(doc, "both", antes=6, depois=0, esq=Cm(0.5), recuo1=Cm(-0.5))
        inline_docx(p, REFS[k][2], num)
    doc.core_properties.title = A["titulo"]
    doc.core_properties.author = A["autores_docx"].replace("¹", "")
    doc.save(saida)


# ============================================================== main
def main():
    with open(os.path.join(RAIZ, "resultados", "resumo.json"), encoding="utf-8") as f:
        R = json.load(f)
    valores = C.valores_de(R, br)
    blocos = C.BLOCOS
    num = numerar(blocos)
    tex = gerar_tex(blocos, num, valores)
    with open(os.path.join(RAIZ, "artigo.tex"), "w", encoding="utf-8", newline="\n") as f:
        f.write(tex)
    gerar_docx(blocos, num, valores, os.path.join(RAIZ, "artigo.docx"))
    print("Gerados: artigo.tex e artigo.docx")


if __name__ == "__main__":
    main()
