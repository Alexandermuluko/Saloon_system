from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
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
    ]
