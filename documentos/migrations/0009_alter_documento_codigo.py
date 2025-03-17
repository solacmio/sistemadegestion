# Generated by Django 5.1.6 on 2025-02-14 19:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0008_trdregistro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documento',
            name='codigo',
            field=models.CharField(max_length=50, validators=[django.core.validators.RegexValidator(message='El código sólo puede contener números y puntos (por ejemplo, 100.02.01).', regex='^[0-9\\.]+$')]),
        ),
    ]
