from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fpdf import FPDF
from PIL import Image

from app.config import settings
from app.schemas import LayoutPanel


class ComicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "ComicCraft", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


def _fit_image(image_path: Path, max_width: float, max_height: float) -> tuple[float, float]:
    with Image.open(image_path) as image:
        width, height = image.size

    ratio = min(max_width / width, max_height / height)
    return width * ratio, height * ratio


def _write_text(pdf: FPDF, label: str, value: str):
    if not value:
        return
    pdf.set_font("Helvetica", "B", 10)
    pdf.multi_cell(0, 6, label)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, value)
    pdf.ln(1)


def save_pdf(layout: list[LayoutPanel]) -> str:
    if not layout:
        raise ValueError("Cannot export an empty comic.")

    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        image_path = settings.static_dir / panel.image_url.lstrip("/")
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 9, f"Panel {panel.panel_number}: {panel.title}")
        pdf.ln(3)

        max_width = pdf.w - pdf.l_margin - pdf.r_margin
        max_height = 145
        width, height = _fit_image(image_path, max_width, max_height)
        x = (pdf.w - width) / 2
        pdf.image(str(image_path), x=x, y=pdf.get_y(), w=width, h=height)
        pdf.ln(height + 6)

        _write_text(pdf, "Scene", panel.scene_description)
        _write_text(pdf, "Caption", panel.caption)
        _write_text(pdf, "Narration", panel.narration)
        _write_text(pdf, "Dialogue", panel.dialogue)

    filename = f"comiccraft-{uuid4().hex}.pdf"
    output = settings.exports_dir / filename
    pdf.output(str(output))
    return str(output)
