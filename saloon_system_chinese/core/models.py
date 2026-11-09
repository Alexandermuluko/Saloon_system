from django.conf import settings
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Hairdresser(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    PAYMENT_CARD = 'Card'
    PAYMENT_CASH = 'Cash'
    PAYMENT_CRYPTO = 'Crypto'
    PAYMENT_MPESA = 'M-Pesa'
    PAYMENT_METHODS = [
        (PAYMENT_CARD, 'Card'),
        (PAYMENT_CASH, 'Cash'),
        (PAYMENT_CRYPTO, 'Crypto'),
        (PAYMENT_MPESA, 'M-Pesa'),
    ]

    PAYMENT_PENDING = 'Pending'
    PAYMENT_PAID = 'Paid'
    PAYMENT_FAILED = 'Failed'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
    ]

    STATUS_PENDING = 'Pending'
    STATUS_ASSIGNED = 'Assigned'
    STATUS_ON_THE_WAY = 'On the Way'
    STATUS_ARRIVED = 'Arrived'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_ON_THE_WAY, 'On the way'),
        (STATUS_ARRIVED, 'Arrived'),
        (STATUS_IN_PROGRESS, 'In progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    hairdresser = models.ForeignKey(
        Hairdresser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} - {self.service.name}'


class PaymentAttempt(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_PAID = 'Paid'
    STATUS_FAILED = 'Failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment_attempts',
    )
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    receipt_number = models.CharField(max_length=30, blank=True)
    result_description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.booking} - {self.status}'
