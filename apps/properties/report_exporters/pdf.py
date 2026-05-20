from io import BytesIO

from django.utils.translation import gettext as _

from .base import PropertyReportExporter


class PdfPropertyReportExporter(PropertyReportExporter):
    def export(self, filters=None) -> BytesIO:
        rows = self.build_rows(filters=filters)
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
        except ImportError:
            content = _("Listado de propiedades").encode("latin-1", errors="replace")
            buffer = BytesIO()
            buffer.write(b"%PDF-1.4\n")
            buffer.write(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
            buffer.write(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
            buffer.write(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n")
            stream = b"BT /F1 18 Tf 72 720 Td (" + content + b") Tj ET"
            buffer.write(b"4 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n")
            buffer.write(stream + b"\nendstream endobj\n")
            buffer.write(b"trailer << /Root 1 0 R >>\n%%EOF")
            buffer.seek(0)
            return buffer

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [Paragraph(_("Listado de propiedades"), styles["Title"]), Spacer(1, 12)]

        data = [["ID", _("Titulo"), _("Ciudad"), _("Barrio"), _("Precio")], *rows]
        table = Table(data, colWidths=[40, 200, 100, 120, 80])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)
        return buffer
