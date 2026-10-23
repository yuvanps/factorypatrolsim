#!/usr/bin/env python3
"""Benchmark report (PDF): algorithms, metrics, results and conclusions for one suite.

    presentation/.venv/bin/python presentation/scripts/build_report.py experiment_results/suites/<suite> \
        [docs/benchmark_report.pdf]

Needs reportlab (presentation/.venv: python3 -m venv --system-site-packages presentation/.venv &&
presentation/.venv/bin/pip install reportlab), matplotlib, scipy and graphviz (dot). Every number in
the report is read from the suite (aggregate.csv, runs.csv, per-run metrics_detail.json); the
interpretation text lives in report_text.py.
"""
import sys
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
from scipy import stats as sst

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_figures as rf  # noqa: E402
import report_text as rt     # noqa: E402

FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
for name, f in (('Serif', 'DejaVuSerif.ttf'), ('Serif-B', 'DejaVuSerif-Bold.ttf'), ('Serif-I', 'DejaVuSerif-Italic.ttf'),
                ('Serif-BI', 'DejaVuSerif-BoldItalic.ttf'), ('Sans', 'DejaVuSans.ttf'), ('Sans-B', 'DejaVuSans-Bold.ttf'),
                ('Sans-I', 'DejaVuSans-Oblique.ttf'), ('Mono', 'DejaVuSansMono.ttf')):
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / f)))
pdfmetrics.registerFontFamily('Serif', normal='Serif', bold='Serif-B', italic='Serif-I', boldItalic='Serif-BI')
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-B', italic='Sans-I', boldItalic='Sans-B')

INK, INK2, RULE, SHADE = colors.HexColor('#0b0b0b'), colors.HexColor('#52514e'), colors.HexColor('#c9c8c2'), \
    colors.HexColor('#f4f4f2')
ST = {
    'title': ParagraphStyle('title', fontName='Sans-B', fontSize=21, leading=26, textColor=INK, spaceAfter=10),
    'subtitle': ParagraphStyle('subtitle', fontName='Sans', fontSize=12, leading=16, textColor=INK2, spaceAfter=18),
    'h1': ParagraphStyle('h1', fontName='Sans-B', fontSize=14.5, leading=19, textColor=INK, spaceBefore=14, spaceAfter=7),
    'h2': ParagraphStyle('h2', fontName='Sans-B', fontSize=11.5, leading=15, textColor=INK, spaceBefore=10, spaceAfter=5),
    'h3': ParagraphStyle('h3', fontName='Sans-B', fontSize=10, leading=13, textColor=INK2, spaceBefore=7, spaceAfter=3),
    'body': ParagraphStyle('body', fontName='Serif', fontSize=9.6, leading=13.6, alignment=TA_JUSTIFY, spaceAfter=6,
                           textColor=INK),
    'bullet': ParagraphStyle('bullet', fontName='Serif', fontSize=9.6, leading=13.4, leftIndent=14, bulletIndent=4,
                             spaceAfter=2.5, textColor=INK),
    'caption': ParagraphStyle('caption', fontName='Sans', fontSize=8.2, leading=11, textColor=INK2, spaceBefore=3,
                              spaceAfter=10, alignment=TA_LEFT),
    'cell': ParagraphStyle('cell', fontName='Sans', fontSize=7.8, leading=9.8, textColor=INK),
    'cellb': ParagraphStyle('cellb', fontName='Sans-B', fontSize=7.8, leading=9.8, textColor=INK),
    'abstract': ParagraphStyle('abstract', fontName='Serif', fontSize=9.6, leading=13.8, alignment=TA_JUSTIFY,
                               leftIndent=18, rightIndent=18, textColor=INK),
    'eqnum': ParagraphStyle('eqnum', fontName='Serif', fontSize=9.6, alignment=TA_CENTER, textColor=INK2),
    'toc1': ParagraphStyle('toc1', fontName='Sans-B', fontSize=10, leading=15, leftIndent=0),
    'toc2': ParagraphStyle('toc2', fontName='Sans', fontSize=9.2, leading=13, leftIndent=16),
}
WIDTH = A4[0] - 4.2 * cm


class Doc(BaseDocTemplate):
    def __init__(self, path, **kw):
        super().__init__(str(path), pagesize=A4, leftMargin=2.1 * cm, rightMargin=2.1 * cm, topMargin=2.0 * cm,
                         bottomMargin=2.0 * cm, title='Benchmarking swarm coordination for factory drone patrol',
                         author='factory_patrol_sim', **kw)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id='f')
        self.addPageTemplates([PageTemplate('p', [frame], onPage=self._decor)])

    @staticmethod
    def _decor(canv, doc):
        if doc.page == 1:
            return
        canv.saveState()
        canv.setFont('Sans', 7.5)
        canv.setFillColor(INK2)
        canv.drawString(2.1 * cm, 1.2 * cm, 'Benchmarking swarm coordination for factory drone patrol')
        canv.drawRightString(A4[0] - 2.1 * cm, 1.2 * cm, str(doc.page))
        canv.setStrokeColor(RULE)
        canv.line(2.1 * cm, A4[1] - 1.5 * cm, A4[0] - 2.1 * cm, A4[1] - 1.5 * cm)
        canv.restoreState()

    def afterFlowable(self, f):
        if isinstance(f, Paragraph) and f.style.name in ('h1', 'h2'):
            level = 0 if f.style.name == 'h1' else 1
            key = f'h{id(f)}'
            self.canv.bookmarkPage(key)
            self.notify('TOCEntry', (level, f.getPlainText(), self.page, key))
            self.canv.addOutlineEntry(f.getPlainText(), key, level=level, closed=level > 0)


class Builder:
    def __init__(self, suite, build_dir):
        self.s = suite
        self.d = Path(build_dir)
        self.d.mkdir(parents=True, exist_ok=True)
        self.story = []
        self.eq_n = 0
        self.fig_n = 0
        self.tab_n = 0
        self.sec = [0, 0]

    # --- text -------------------------------------------------------------------------------------
    def h1(self, text):
        self.sec = [self.sec[0] + 1, 0]
        self.story.append(Paragraph(f'{self.sec[0]}  {text}', ST['h1']))

    def h2(self, text):
        self.sec[1] += 1
        self.story.append(Paragraph(f'{self.sec[0]}.{self.sec[1]}  {text}', ST['h2']))

    def h3(self, text):
        self.story.append(Paragraph(text, ST['h3']))

    def p(self, *texts):
        for t in texts:
            self.story.append(Paragraph(t, ST['body']))

    def bullets(self, items):
        for t in items:
            self.story.append(Paragraph(t, ST['bullet'], bulletText='•'))
        self.story.append(Spacer(1, 4))

    # --- equations, figures, tables -----------------------------------------------------------------
    def eq(self, tex, size=11.5):
        self.eq_n += 1
        path, w, h = rf.equation(tex, self.d / f'eq{self.eq_n:02d}.png', size)
        scale = min(1.0, (WIDTH - 1.6 * cm) / w)
        img = Image(str(path), width=w * scale, height=h * scale)
        t = Table([[img, Paragraph(f'({self.eq_n})', ST['eqnum'])]], colWidths=[WIDTH - 1.2 * cm, 1.2 * cm])
        t.setStyle(TableStyle([('ALIGN', (0, 0), (0, 0), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                               ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]))
        self.story.append(t)
        return self.eq_n

    def fig(self, path, caption, width=None):
        self.fig_n += 1
        from PIL import Image as PI
        w, h = PI.open(path).size
        width = width or WIDTH
        height = width * h / w
        if height > 19 * cm:
            height = 19 * cm
            width = height * w / h
        self.story.append(KeepTogether([Image(str(path), width=width, height=height),
                                        Paragraph(f'<b>Figure {self.fig_n}.</b> {caption}', ST['caption'])]))
        return self.fig_n

    def table(self, rows, caption, widths=None, header=True, zebra=True):
        self.tab_n += 1
        data = [[c if not isinstance(c, str) else Paragraph(c, ST['cellb' if header and i == 0 else 'cell'])
                 for c in r] for i, r in enumerate(rows)]
        t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        style = [('LINEABOVE', (0, 0), (-1, 0), 0.8, INK), ('LINEBELOW', (0, -1), (-1, -1), 0.8, INK),
                 ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                 ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5), ('LEFTPADDING', (0, 0), (-1, -1), 4),
                 ('RIGHTPADDING', (0, 0), (-1, -1), 4)]
        if header:
            style.append(('LINEBELOW', (0, 0), (-1, 0), 0.5, INK))
        if zebra:
            for i in range(1 + header, len(rows), 2):
                style.append(('BACKGROUND', (0, i), (-1, i), SHADE))
        t.setStyle(TableStyle(style))
        self.story.append(KeepTogether([Paragraph(f'<b>Table {self.tab_n}.</b> {caption}', ST['caption']), t,
                                        Spacer(1, 10)]))
        return self.tab_n

    # --- data helpers ---------------------------------------------------------------------------------
    def v(self, scen, algo, metric, d=1, ci=True):
        st = self.s.stat(scen, algo, metric)
        if not st:
            return '–'
        m, hw, n = st
        return f'{m:.{d}f} ± {hw:.{d}f}' if ci else f'{m:.{d}f}'

    def m(self, scen, algo, metric):
        st = self.s.stat(scen, algo, metric)
        return st[0] if st else None


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def tests(suite, scen, metric):
    """Kruskal-Wallis over the algorithms, then pairwise two-sided Mann-Whitney U with Holm
    correction and the rank-biserial correlation r (positive: the first algorithm has larger values)."""
    groups = {a: suite.values(scen, a, metric) for a in rf.ALGOS}
    groups = {a: g for a, g in groups.items() if len(g) >= 2}
    if len(groups) < 2 or len({x for g in groups.values() for x in g}) < 2:
        return None
    try:
        kw = sst.kruskal(*groups.values()).pvalue
    except ValueError:
        return None
    pairs, ps, rs = [], [], []
    names = list(groups)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = groups[names[i]], groups[names[j]]
            u = sst.mannwhitneyu(a, b, alternative='two-sided')
            pairs.append((names[i], names[j]))
            ps.append(u.pvalue)
            rs.append(2 * u.statistic / (len(a) * len(b)) - 1)
    return kw, list(zip(pairs, holm(ps), rs))


def build(suite_dir, out_pdf):
    suite = rf.Suite(suite_dir)
    B = Builder(suite, rf.ROOT / 'presentation' / 'report_build')
    rt.write(B, suite, tests)
    doc = Doc(out_pdf)
    toc = TableOfContents()
    toc.levelStyles = [ST['toc1'], ST['toc2']]
    story = rt.front_matter(B, suite, toc) + B.story
    doc.multiBuild(story)
    print('wrote', out_pdf)


if __name__ == '__main__':
    suite_dir = sys.argv[1]
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else rf.ROOT / 'docs' / 'benchmark_report.pdf'
    build(suite_dir, out.resolve())
