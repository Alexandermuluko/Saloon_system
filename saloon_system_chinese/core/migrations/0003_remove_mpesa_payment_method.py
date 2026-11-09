from django.db import migrations, models


def convert_mpesa_to_cash(apps, schema_editor):
    Booking = apps.get_model('core', 'Booking')
    Booking.objects.filter(payment_method='M-Pesa').update(payment_method='Cash')


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0002_update_payment_methods'),
    ]

    operations = [
        migrations.RunPython(convert_mpesa_to_cash, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='booking',
            name='payment_method',
            field=models.CharField(
                choices=[
                    ('Card', 'Card'),
                    ('Cash', 'Cash'),
                    ('Crypto', 'Crypto'),
                ],
                max_length=20,
            ),
        ),
    ]
