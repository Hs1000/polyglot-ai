"""
PDF export service.

Generates a clean, paginated PDF from document text using Arial Unicode so
every language the translation pipeline can produce renders correctly.
"""

import logging
import re
from pathlib import Path

from fpdf import FPDF

logger = logging.getLogger(__name__)

_FONT_CANDIDATES = [
    # Bundled (dev on macOS when copied from /Library/Fonts)
    Path(__file__).parent.parent.parent / "fonts" / "ArialUnicode.ttf",
    # Linux apt: fonts-dejavu-core
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),               # Arch / some distros
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    # macOS system (fallback when font not bundled)
    Path("/Library/Fonts/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
]

_FONT_PATH = next((str(p) for p in _FONT_CANDIDATES if p.exists()), None)
if _FONT_PATH is None:
    logger.warning("No Unicode font found — PDF export may fail. Install fonts-dejavu-core.")
_FONT_NAME = "MainFont"

_PAGE_W = 210   # A4 mm
_MARGIN = 18
_TEXT_W = _PAGE_W - 2 * _MARGIN


class _DocPDF(FPDF):
    """FPDF subclass with header/footer and the Unicode font pre-loaded."""

    def __init__(self, doc_title: str):
        super().__init__()
        self._doc_title = doc_title
        if _FONT_PATH is None:
            raise RuntimeError(
                "No Unicode font found. Install fonts-dejavu-core (Linux) "
                "or place ArialUnicode.ttf in backend/fonts/."
            )
        self.add_font(_FONT_NAME, fname=_FONT_PATH)
        self.set_auto_page_break(auto=True, margin=22)
        self.set_margins(_MARGIN, _MARGIN, _MARGIN)

    def header(self):
        self.set_font(_FONT_NAME, size=8)
        self.set_text_color(160, 160, 160)
        title = self._doc_title if len(self._doc_title) <= 80 else self._doc_title[:77] + "…"
        self.cell(0, 8, title, align="L")
        self.ln(0)
        self.set_draw_color(220, 220, 220)
        self.line(_MARGIN, self.get_y(), _PAGE_W - _MARGIN, self.get_y())
        self.ln(6)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-14)
        self.set_font(_FONT_NAME, size=8)
        self.set_text_color(160, 160, 160)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def generate_pdf(text: str, title: str, content_label: str = "Translated Text") -> bytes:
    """Return a PDF as bytes.

    Args:
        text:          Body text to render (translated or extracted).
        title:         Document filename — shown in the running header.
        content_label: Label shown above the body text.
    """
    pdf = _DocPDF(doc_title=title)
    pdf.add_page()

    # Document title (filename without extension)
    pdf.set_font(_FONT_NAME, size=20)
    display_title = re.sub(r'\.[^.]+$', '', title)
    pdf.multi_cell(_TEXT_W, 10, display_title, align="L")
    pdf.ln(1)

    # Content-type label
    pdf.set_font(_FONT_NAME, size=9)
    pdf.set_text_color(80, 120, 200)
    pdf.cell(0, 6, content_label.upper(), ln=True)
    pdf.set_text_color(0, 0, 0)

    # Divider
    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(_MARGIN, pdf.get_y(), _PAGE_W - _MARGIN, pdf.get_y())
    pdf.ln(7)

    # Body — split on newlines, treat blank lines as paragraph spacing
    pdf.set_font(_FONT_NAME, size=11)
    for para in text.split("\n"):
        para = para.strip()
        if not para:
            pdf.ln(4)
            continue
        pdf.multi_cell(_TEXT_W, 6, para, align="L")
        pdf.ln(1)

    return bytes(pdf.output())
