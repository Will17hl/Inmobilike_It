from io import BytesIO

from django.utils.translation import gettext as _

from .base import PropertyReportExporter


class ExcelPropertyReportExporter(PropertyReportExporter):
    def export(self, filters=None) -> BytesIO:
        rows = self.build_rows(filters=filters)
        headers = ["ID", _("Titulo"), _("Ciudad"), _("Barrio"), _("Precio")]

        try:
            from openpyxl import Workbook
        except ImportError:
            buffer = BytesIO()
            lines = [",".join(headers)]
            lines.extend(",".join(str(value) for value in row) for row in rows)
            buffer.write("\n".join(lines).encode("utf-8"))
            buffer.seek(0)
            return buffer

        wb = Workbook()
        ws = wb.active
        ws.title = _("Propiedades")[:31]
        ws.append(headers)

        for row in rows:
            row[4] = float(row[4])
            ws.append(row)

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer
