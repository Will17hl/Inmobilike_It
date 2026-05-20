from .report_exporters import ExcelPropertyReportExporter, PdfPropertyReportExporter


def generate_properties_pdf(filters=None):
    return PdfPropertyReportExporter().export(filters=filters)


def generate_properties_excel(filters=None):
    return ExcelPropertyReportExporter().export(filters=filters)
