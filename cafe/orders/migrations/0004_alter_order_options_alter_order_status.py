# Generated by Django 5.1.5 on 2025-01-23 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_remove_order_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-created'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('PENDING', 'В ожидании'), ('READY', 'Готово'), ('PAID', 'Оплачено')], db_index=True, default='PENDING', max_length=12, verbose_name='статус'),
        ),
    ]
