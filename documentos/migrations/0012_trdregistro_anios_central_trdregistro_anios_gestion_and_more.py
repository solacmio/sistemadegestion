# Generated by Django 5.1.6 on 2025-04-15 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0011_alter_documento_hash_sha256'),
    ]

    operations = [
        migrations.AddField(
            model_name='trdregistro',
            name='anios_central',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trdregistro',
            name='anios_gestion',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trdregistro',
            name='disposicion_final',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='documento',
            name='sesion',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Sección'),
        ),
        migrations.AlterField(
            model_name='documento',
            name='subsesion',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Subsección'),
        ),
    ]
