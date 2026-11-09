import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Booking, PaymentAttempt, Service


class PaymentFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='payuser', password='strongpass123')
        self.service = Service.objects.create(
            name='Signature Cut',
            price='25.00',
            description='A polished style for any occasion.',
            image_url='https://example.com/service.jpg',
        )
        self.booking = Booking.objects.create(
            customer=self.user,
            full_name='Test Customer',
            phone='0712345678',
            service=self.service,
            appointment_date='2026-08-01',
            appointment_time='10:00:00',
            location='Nairobi',
            notes='Need a fresh trim.',
            payment_method=Booking.PAYMENT_CARD,
        )

    def test_pay_booking_starts_mpesa_prompt_but_remains_pending(self):
        self.client.force_login(self.user)
        with patch('core.views.start_mpesa_payment') as start_payment:
            start_payment.return_value = {
                'CheckoutRequestID': 'checkout-123',
                'MerchantRequestID': 'merchant-123',
            }
            response = self.client.post(
                reverse('pay_booking', args=[self.booking.pk]),
                {'phone_number': '0712345678'},
            )

        self.booking.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.booking.payment_status, Booking.PAYMENT_PENDING)
        self.assertEqual(self.booking.payment_method, Booking.PAYMENT_MPESA)
        start_payment.assert_called_once_with(
            phone_number='254712345678',
            amount=25,
            account_reference=f'BOOKING-{self.booking.pk}',
            description=f'Salon booking {self.booking.pk}',
        )
        attempt = PaymentAttempt.objects.get(booking=self.booking)
        self.assertEqual(attempt.status, PaymentAttempt.STATUS_PENDING)

    def test_mpesa_callback_marks_booking_paid_only_after_confirmation(self):
        attempt = PaymentAttempt.objects.create(
            booking=self.booking,
            checkout_request_id='checkout-123',
            phone_number='254712345678',
            amount=25,
        )
        response = self.client.post(
            reverse('mpesa_callback'),
            data=json.dumps({
                'Body': {
                    'stkCallback': {
                        'CheckoutRequestID': attempt.checkout_request_id,
                        'ResultCode': 0,
                        'ResultDesc': (
                            'The service request is processed successfully.'
                        ),
                        'CallbackMetadata': {
                            'Item': [
                                {'Name': 'Amount', 'Value': 25},
                                {
                                    'Name': 'MpesaReceiptNumber',
                                    'Value': 'ABC123XYZ',
                                },
                            ],
                        },
                    },
                },
            }),
            content_type='application/json',
        )

        self.booking.refresh_from_db()
        attempt.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.booking.payment_status, Booking.PAYMENT_PAID)
        self.assertEqual(attempt.status, PaymentAttempt.STATUS_PAID)
        self.assertEqual(attempt.receipt_number, 'ABC123XYZ')

    def test_payment_is_not_marked_paid_when_daraja_is_unconfigured(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('pay_booking', args=[self.booking.pk]),
            {'phone_number': '0712345678'},
        )

        self.booking.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.booking.payment_status, Booking.PAYMENT_PENDING)
        self.assertFalse(
            PaymentAttempt.objects.filter(booking=self.booking).exists()
        )
