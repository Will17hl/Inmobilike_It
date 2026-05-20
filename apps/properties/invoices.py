from decimal import Decimal, InvalidOperation
from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from django.utils.translation import gettext as _


def format_currency(value, currency):
    try:
        amount = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, TypeError, ValueError):
        return f"{value} {currency.upper()}"

    if amount == amount.to_integral():
        formatted = f"{int(amount):,}".replace(",", ".")
    else:
        integer_part, decimal_part = f"{amount:,.2f}".split(".")
        formatted = f"{integer_part.replace(',', '.')},{decimal_part}"
    return f"${formatted} {currency.upper()}"


def user_display_name(user):
    if not user:
        return _("Sin usuario asociado")
    return user.get_full_name() or user.username


def user_email(user):
    if not user:
        return _("Sin email")
    return user.email or _("Sin email")


class PaymentInvoicePdf:
    def __init__(self, payment):
        self.payment = payment

    def export(self):
        self.payment.ensure_invoice()
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError:
            return self._fallback_pdf()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.7 * inch,
            leftMargin=0.7 * inch,
            topMargin=0.65 * inch,
            bottomMargin=0.65 * inch,
        )
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="Muted",
                parent=styles["Normal"],
                textColor=colors.HexColor("#6b7280"),
                fontSize=9,
                leading=12,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Section",
                parent=styles["Heading2"],
                fontSize=12,
                leading=15,
                spaceBefore=12,
                spaceAfter=6,
            )
        )

        payment = self.payment
        property_obj = payment.property
        agent_user = property_obj.agent.user if property_obj.agent else None
        issued_at = payment.invoice_issued_at or payment.paid_at or timezone.now()

        elements = [
            Paragraph(_("Factura de pago"), styles["Title"]),
            Paragraph("Inmobilike It", styles["Heading2"]),
            Paragraph(_("Documento generado automaticamente por la plataforma."), styles["Muted"]),
            Spacer(1, 18),
        ]

        summary_data = [
            [_("Factura"), payment.invoice_number],
            [_("Fecha emision"), timezone.localtime(issued_at).strftime("%d/%m/%Y %H:%M")],
            [_("Estado"), payment.get_status_display()],
            [_("Referencia Stripe"), payment.stripe_session_id],
        ]
        elements.append(self._table(summary_data, [130, 360], colors, Table, TableStyle))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(_("Cliente"), styles["Section"]))
        elements.append(
            self._table(
                [
                    [_("Nombre"), user_display_name(payment.user)],
                    [_("Email"), user_email(payment.user)],
                ],
                [130, 360],
                colors,
                Table,
                TableStyle,
            )
        )

        elements.append(Paragraph(_("Propiedad"), styles["Section"]))
        elements.append(
            self._table(
                [
                    [_("Titulo"), property_obj.title],
                    [_("Operacion"), property_obj.get_operation_display()],
                    [_("Ciudad"), property_obj.location.city],
                    [_("Barrio"), property_obj.location.neighborhood],
                    [_("Direccion"), property_obj.location.address],
                    [_("Asesor"), user_display_name(agent_user)],
                ],
                [130, 360],
                colors,
                Table,
                TableStyle,
            )
        )

        elements.append(Paragraph(_("Detalle del cobro"), styles["Section"]))
        detail_table = Table(
            [
                [_("Concepto"), _("Cantidad"), _("Valor")],
                [
                    _("Pago de propiedad en Inmobilike It"),
                    "1",
                    format_currency(payment.amount, payment.currency),
                ],
                ["", _("Total"), format_currency(payment.amount, payment.currency)],
            ],
            colWidths=[280, 80, 130],
        )
        detail_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                    ("BACKGROUND", (1, -1), (-1, -1), colors.HexColor("#fff7ed")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTNAME", (1, -1), (-1, -1), "Helvetica-Bold"),
                    ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                    ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor("#9ca3af")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )
        elements.append(detail_table)

        if payment.stripe_payment_intent_id:
            elements.append(Spacer(1, 12))
            elements.append(
                Paragraph(
                    _("ID de intento de pago: %(payment_intent)s")
                    % {"payment_intent": escape(payment.stripe_payment_intent_id)},
                    styles["Muted"],
                )
            )

        doc.build(elements)
        buffer.seek(0)
        return buffer

    def _table(self, rows, col_widths, colors, table_cls, table_style_cls):
        table = table_cls(rows, colWidths=col_widths)
        table.setStyle(
            table_style_cls(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f9fafb")),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d1d5db")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return table

    def _fallback_pdf(self):
        payment = self.payment
        lines = [
            "Factura de pago",
            f"Inmobilike It - {payment.invoice_number}",
            f"Total: {format_currency(payment.amount, payment.currency)}",
            f"Propiedad: {payment.property.title}",
        ]
        content = " | ".join(lines).encode("latin-1", errors="replace")
        buffer = BytesIO()
        buffer.write(b"%PDF-1.4\n")
        buffer.write(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
        buffer.write(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
        buffer.write(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n")
        stream = b"BT /F1 12 Tf 72 720 Td (" + content + b") Tj ET"
        buffer.write(b"4 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n")
        buffer.write(stream + b"\nendstream endobj\n")
        buffer.write(b"trailer << /Root 1 0 R >>\n%%EOF")
        buffer.seek(0)
        return buffer
