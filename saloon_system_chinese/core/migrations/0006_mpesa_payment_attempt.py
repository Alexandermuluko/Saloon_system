from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_booking_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('Card', 'Card'),
                    ('Cash', 'Cash'),
                    ('Crypto', 'Crypto'),
                    ('M-Pesa', 'M-Pesa'),
                ],
                max_length=20,
            ),
        ),
        migrations.CreateModel(
            name='PaymentAttempt',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'checkout_request_id',
                    models.CharField(max_length=100, unique=True),
                ),
                (
                    'merchant_request_id',
                    models.CharField(blank=True, max_length=100),
                ),
                ('phone_number', models.CharField(max_length=15)),
                ('amount', models.PositiveIntegerField()),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('Pending', 'Pending'),
                            ('Paid', 'Paid'),
                            ('Failed', 'Failed'),
                        ],
                        default='Pending',
                        max_length=20,
                    ),
                ),
                (
                    'receipt_number',
                    models.CharField(blank=True, max_length=30),
                ),
                (
                    'result_description',
                    models.CharField(blank=True, max_length=255),
                ),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                (
                    'booking',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='payment_attempts',
                        to='core.booking',
                    ),
                ),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
