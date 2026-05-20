from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import AgentProfile
from apps.properties.models import Location, Property, PropertyPayment
from apps.properties.views import sync_payment_from_checkout_session


class PaymentInvoiceTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.buyer = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="secret",
        )
        self.agent_user = User.objects.create_user(
            username="agent",
            email="agent@example.com",
            password="secret",
        )
        self.other_user = User.objects.create_user(username="other", password="secret")
        self.agent = AgentProfile.objects.create(
            user=self.agent_user,
            phone="3001234567",
            agency_name="Inmobilike",
        )
        self.location = Location.objects.create(
            city="Medellin",
            neighborhood="Laureles",
            address="Calle 10 # 20-30",
        )
        self.property = Property.objects.create(
            title="Apartamento con vista",
            description="Apartamento de prueba",
            operation=Property.OP_RENT,
            price=Decimal("2500000.00"),
            is_active=True,
            location=self.location,
            agent=self.agent,
        )

    def create_payment(self, status=PropertyPayment.STATUS_PAID):
        return PropertyPayment.objects.create(
            property=self.property,
            user=self.buyer,
            amount=Decimal("2500000.00"),
            currency="cop",
            status=status,
            stripe_session_id=f"cs_test_{status}",
            stripe_payment_intent_id="pi_test_123",
            paid_at=timezone.now() if status == PropertyPayment.STATUS_PAID else None,
        )

    def test_paid_checkout_generates_invoice_metadata(self):
        payment = self.create_payment(status=PropertyPayment.STATUS_PENDING)
        checkout_session = SimpleNamespace(
            payment_intent="pi_test_paid",
            payment_status="paid",
            status="complete",
        )

        sync_payment_from_checkout_session(payment, checkout_session)
        payment.refresh_from_db()

        self.assertEqual(payment.status, PropertyPayment.STATUS_PAID)
        self.assertTrue(payment.invoice_number.startswith("FAC-"))
        self.assertIsNotNone(payment.invoice_issued_at)

    def test_buyer_can_download_payment_invoice_pdf(self):
        payment = self.create_payment()
        self.client.force_login(self.buyer)

        response = self.client.get(
            reverse("properties:payment_invoice_pdf", args=[payment.id])
        )
        payment.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))
        self.assertIn(payment.invoice_number, response["Content-Disposition"])

    def test_agent_can_download_payment_invoice_pdf(self):
        payment = self.create_payment()
        self.client.force_login(self.agent_user)

        response = self.client.get(
            reverse("properties:payment_invoice_pdf", args=[payment.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_other_user_cannot_download_payment_invoice_pdf(self):
        payment = self.create_payment()
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse("properties:payment_invoice_pdf", args=[payment.id])
        )

        self.assertEqual(response.status_code, 403)
